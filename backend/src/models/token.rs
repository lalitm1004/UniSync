use std::{collections::HashMap, fmt};

use chrono::{Duration, NaiveDateTime, Utc};
use poem_openapi::Object;
use serde::Deserialize;
use sqlx::{Executor, Postgres, prelude::FromRow};
use uuid::Uuid;

use crate::CONFIG;

#[derive(FromRow, Object)]
pub struct GoogleToken {
    pub user_id: Uuid,
    pub access_token: String,
    pub refresh_token: String,
    pub expires_at: NaiveDateTime,
    pub created_at: NaiveDateTime,
}

#[derive(Debug, Deserialize)]
struct GoogleRefreshResponse {
    access_token: String,
    expires_in: Option<i64>,
    refresh_token: Option<String>,
}

impl GoogleToken {
    const GOOGLE_TOKEN_URL: &'static str = "https://oauth2.googleapis.com/token";

    async fn query_for_token<'e, E>(executor: E, user_id: Uuid) -> Result<Option<Self>, sqlx::Error>
    where
        E: Executor<'e, Database = Postgres> + Copy,
    {
        sqlx::query_as!(
            GoogleToken,
            r#"
                SELECT *
                FROM googletoken
                WHERE user_id = $1
                LIMIT 1
            "#,
            user_id
        )
        .fetch_optional(executor)
        .await
    }

    fn needs_refresh(&self) -> bool {
        Utc::now().naive_utc() >= self.expires_at
    }

    pub async fn get_valid_access_token<'e, E>(
        executor: E,
        user_id: Uuid,
    ) -> Result<Self, GoogleTokenError>
    where
        E: Executor<'e, Database = Postgres> + Copy,
    {
        let token = Self::query_for_token(executor, user_id).await?;
        match token {
            Some(token) => {
                if token.needs_refresh() {
                    Self::refresh_token(executor, &token).await
                } else {
                    Ok(token)
                }
            }
            None => Err(GoogleTokenError::NoTokenFound),
        }
    }

    pub async fn refresh_token<'e, E>(executor: E, token: &Self) -> Result<Self, GoogleTokenError>
    where
        E: Executor<'e, Database = Postgres> + Copy,
    {
        let http_client = reqwest::Client::new();

        let mut params = HashMap::new();
        params.insert("client_id".to_string(), CONFIG.google_client_id.clone());
        params.insert(
            "client_secret".to_string(),
            CONFIG.google_client_secret.clone(),
        );
        params.insert("refresh_token".to_string(), token.refresh_token.clone());
        params.insert("grant_type".to_string(), "refresh_token".to_string());

        let response = http_client
            .post(Self::GOOGLE_TOKEN_URL)
            .header("Content-Type", "application/x-www-form-urlencoded")
            .form(&params)
            .send()
            .await?;

        if !response.status().is_success() {
            let error_text = response
                .text()
                .await
                .unwrap_or_else(|_| "Unknown error".to_string());
            return Err(GoogleTokenError::RefreshFailed(error_text));
        }

        let refresh_response: GoogleRefreshResponse = response.json().await?;

        let now = Utc::now().naive_utc();

        let expires_at = refresh_response
            .expires_in
            .map(|expires_in| now + Duration::seconds(expires_in))
            .unwrap_or_else(|| now + Duration::minutes(60));

        let new_refresh_token = refresh_response
            .refresh_token
            .clone()
            .unwrap_or_else(|| token.refresh_token.clone());

        let updated_token = sqlx::query_as!(
            GoogleToken,
            r#"
                UPDATE googletoken
                SET access_token = $1, refresh_token = $2, expires_at = $3
                WHERE user_id = $4
                RETURNING user_id, access_token, refresh_token, created_at, expires_at
            "#,
            refresh_response.access_token,
            new_refresh_token,
            expires_at,
            token.user_id
        )
        .fetch_one(executor)
        .await?;

        Ok(updated_token)
    }
}

#[derive(Debug)]
pub enum GoogleTokenError {
    DatabaseError(sqlx::Error),
    HttpError(reqwest::Error),
    NoTokenFound,
    RefreshFailed(String),
}

impl fmt::Display for GoogleTokenError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            GoogleTokenError::DatabaseError(e) => write!(f, "Database error: {}", e),
            GoogleTokenError::HttpError(e) => write!(f, "HTTP error: {}", e),
            GoogleTokenError::NoTokenFound => write!(f, "No Google token found in database"),
            GoogleTokenError::RefreshFailed(msg) => write!(f, "Token refresh failed: {}", msg),
        }
    }
}

impl std::error::Error for GoogleTokenError {}

impl From<sqlx::Error> for GoogleTokenError {
    fn from(err: sqlx::Error) -> Self {
        GoogleTokenError::DatabaseError(err)
    }
}

impl From<reqwest::Error> for GoogleTokenError {
    fn from(err: reqwest::Error) -> Self {
        GoogleTokenError::HttpError(err)
    }
}
