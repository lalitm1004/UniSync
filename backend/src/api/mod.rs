mod cache;
pub use cache::CacheApi;

use poem_openapi::{Object, Tags};

#[derive(Tags)]
enum ApiTags {
    Cache,
}

#[derive(Object)]
pub struct ErrorResponse {
    pub code: String,

    #[oai(skip_serializing_if = "Option::is_none")]
    pub message: Option<String>,

    #[oai(skip_serializing_if = "Option::is_none")]
    pub details: Option<String>,
}
