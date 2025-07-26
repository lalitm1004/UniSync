use poem::{Result, web::Data};
use poem_openapi::{ApiResponse, Object, OpenApi, param::Path, payload::Json};
use serde::Deserialize;

use super::{ApiTags, ErrorResponse};
use crate::{
    AppState, middleware::ExtensionAuth, models::course::Course, schedule_cache::CacheError,
};

#[derive(Deserialize, Object)]
struct InsertToCacheRequest {
    courses: Vec<Course>,
}

#[derive(Object)]
struct RefferalCode {
    id: String,
}

#[derive(ApiResponse)]
enum InsertToCacheResponse {
    #[oai(status = 201)]
    Inserted(Json<RefferalCode>),

    #[oai(status = 503)]
    CacheFull(Json<ErrorResponse>),
}

#[derive(ApiResponse)]
enum GetCacheResponse {
    #[oai(status = 200)]
    Found(Json<Vec<Course>>),

    #[oai(status = 404)]
    NotFound(Json<ErrorResponse>),
}

pub struct CacheApi;
#[OpenApi(tag = "ApiTags::Cache")]
impl CacheApi {
    #[oai(path = "/schedule-cache", method = "post")]
    async fn insert_to_cache(
        &self,
        data: Json<InsertToCacheRequest>,
        state: Data<&AppState>,
        _extension_auth: ExtensionAuth,
    ) -> Result<InsertToCacheResponse> {
        let schedule_cache_manager = state.schedule_cache_manager.clone();

        match schedule_cache_manager
            .set_courses(data.courses.clone())
            .await
        {
            Ok(id) => Ok(InsertToCacheResponse::Inserted(Json(RefferalCode { id }))),
            Err(CacheError::CacheFull) => {
                Ok(InsertToCacheResponse::CacheFull(Json(ErrorResponse {
                    code: "CACHE_FULL".to_string(),
                    message: Some(
                        "The server is processing existing requests. Try again in a few minutes"
                            .to_string(),
                    ),
                    details: None,
                })))
            }
        }
    }

    #[oai(path = "/schedule-cache/:id", method = "get")]
    async fn retrieve_from_cache(
        &self,
        state: Data<&AppState>,
        id: Path<String>,
        _extension_auth: ExtensionAuth,
    ) -> Result<GetCacheResponse> {
        let schedule_cache_manager = state.schedule_cache_manager.clone();

        match schedule_cache_manager.get_courses(&id.0).await {
            Some(courses) => Ok(GetCacheResponse::Found(Json(courses))),
            None => Ok(GetCacheResponse::NotFound(Json(ErrorResponse {
                code: "NOT_FOUND".to_string(),
                message: Some("No cached schedule found for the provided ID".to_string()),
                details: None,
            }))),
        }
    }
}
