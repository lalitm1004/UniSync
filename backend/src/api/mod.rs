mod cache;
pub use cache::CacheApi;

mod token;
pub use token::TokenApi;

use poem_openapi::{Object, Tags};

#[derive(Tags)]
enum ApiTags {
    Cache,
    Token,
}

#[derive(Object)]
pub struct ErrorResponse {
    pub code: String,

    #[oai(skip_serializing_if = "Option::is_none")]
    pub message: Option<String>,

    #[oai(skip_serializing_if = "Option::is_none")]
    pub details: Option<String>,
}
