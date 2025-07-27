use poem::{Result, error::InternalServerError, web::Data};
use poem_openapi::{ApiResponse, Object, OpenApi, payload::Json};
use serde::Deserialize;

use super::{ApiTags, ErrorResponse};
use crate::{AppState, middleware::JwtAuth, models::GoogleToken};

#[derive(Deserialize, Object)]
struct StoreTokenRequest {
    access_token: String,
    refresh_token: String,
}

#[derive(ApiResponse)]
enum StoreTokenResponse {
    #[oai(status = 201)]
    Inserted,

    #[oai(status = 400)]
    BadRequest(Json<ErrorResponse>),
}

#[derive(ApiResponse)]
enum GetTokenResponse {
    #[oai(status = 201)]
    Get(Json<GoogleToken>),

    #[oai(status = 400)]
    BadRequest(Json<ErrorResponse>),
}

pub struct TokenApi;
#[OpenApi(tag = "ApiTags::Token")]
impl TokenApi {
    #[oai(path = "/token", method = "post")]
    async fn store_token(
        &self,
        data: Json<StoreTokenRequest>,
        state: Data<&AppState>,
        jwt_auth: JwtAuth,
    ) -> Result<StoreTokenResponse> {
        let claims = jwt_auth.0;

        let user_id = match uuid::Uuid::parse_str(&claims.user_id) {
            Ok(id) => id,
            Err(_) => {
                return Ok(StoreTokenResponse::BadRequest(Json(ErrorResponse {
                    code: "INVALID_USER_ID".to_string(),
                    message: None,
                    details: None,
                })));
            }
        };

        let now = chrono::Utc::now().naive_utc();
        let expires_at = now + chrono::Duration::seconds(3600);

        sqlx::query!(
            r#"
                INSERT INTO googletoken
                    (user_id, access_token, refresh_token, created_at, expires_at)
                VALUES
                    ($1, $2, $3, $4, $5)
                ON CONFLICT(user_id) DO UPDATE SET
                    access_token = excluded.access_token,
                    refresh_token = excluded.refresh_token,
                    created_at = excluded.created_at,
                    expires_at = excluded.expires_at
            "#,
            user_id,
            data.access_token,
            data.refresh_token,
            now,
            expires_at,
        )
        .execute(&*state.db)
        .await
        .map_err(InternalServerError)?;

        Ok(StoreTokenResponse::Inserted)
    }

    #[oai(path = "/token", method = "get")]
    async fn get_token(
        &self,
        state: Data<&AppState>,
        jwt_auth: JwtAuth,
    ) -> Result<GetTokenResponse> {
        let claims = jwt_auth.0;

        let user_id = match uuid::Uuid::parse_str(&claims.user_id) {
            Ok(id) => id,
            Err(_) => {
                return Ok(GetTokenResponse::BadRequest(Json(ErrorResponse {
                    code: "INVALID_USER_ID".to_string(),
                    message: None,
                    details: None,
                })));
            }
        };

        match GoogleToken::get_valid_access_token(&*state.db, user_id).await {
            Ok(token) => Ok(GetTokenResponse::Get(Json(token))),
            Err(err) => Ok(GetTokenResponse::BadRequest(Json(ErrorResponse {
                code: err.to_string(),
                message: None,
                details: None,
            }))),
        }
    }
}
