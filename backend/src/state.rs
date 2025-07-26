use sqlx::{PgPool, postgres::PgPoolOptions};
use std::sync::Arc;

use crate::{CONFIG, ScheduleCacheManager};

#[derive(Clone)]
pub struct AppState {
    pub db: Arc<PgPool>,
    pub schedule_cache_manager: Arc<ScheduleCacheManager>,
}

impl AppState {
    pub async fn new() -> Result<Self, String> {
        let db = Arc::new(
            PgPoolOptions::new()
                .max_connections(5)
                .connect(&CONFIG.database_url)
                .await
                .map_err(|e| format!("Database connection failed: {}", e))?,
        );

        let schedule_cache_manager = Arc::new(ScheduleCacheManager::new(
            CONFIG.schedule_cleanup_after,
            CONFIG.schedule_cache_max_size,
        ));

        Ok(AppState {
            db,
            schedule_cache_manager,
        })
    }
}
