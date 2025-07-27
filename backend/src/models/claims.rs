use poem_openapi::Object;
use serde::{Deserialize, Serialize};

#[derive(Debug, Deserialize, Serialize, Clone, Object)]
pub struct Claims {
    #[serde(rename = "sub")]
    pub user_id: String,
    pub email: String,
}
