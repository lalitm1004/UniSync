use nanoid::nanoid;
use std::{collections::HashMap, sync::Arc};
use tokio::{
    sync::RwLock,
    time::{self, Duration, Instant},
};

use crate::models::course::Course;

pub struct TaggedCourses {
    courses: Vec<Course>,
    created_at: Instant,
}

#[derive(Clone)]
pub struct ScheduleCacheManager {
    schedule_cache: Arc<RwLock<HashMap<String, TaggedCourses>>>,
    max_cache_size: usize,
}

impl ScheduleCacheManager {
    pub fn new(cleanup_after_secs: u64, max_cache_size: usize) -> Self {
        let manager = Self {
            schedule_cache: Arc::new(RwLock::new(HashMap::new())),
            max_cache_size,
        };

        let cleanup_after = Duration::from_secs(cleanup_after_secs);
        let schedule_cleanup_clone = manager.schedule_cache.clone();
        tokio::spawn(async move {
            let mut interval = time::interval(Duration::from_secs(30));
            loop {
                interval.tick().await;
                let now = Instant::now();

                let mut schedules = schedule_cleanup_clone.write().await;
                schedules.retain(|_, tagged| now.duration_since(tagged.created_at) < cleanup_after);
            }
        });

        manager
    }

    pub async fn set_courses(&self, courses: Vec<Course>) -> Result<String, CacheError> {
        let mut cache = self.schedule_cache.write().await;

        if cache.len() >= self.max_cache_size {
            return Err(CacheError::CacheFull);
        }

        let id = nanoid!();

        let tagged_courses = TaggedCourses {
            courses,
            created_at: Instant::now(),
        };
        cache.insert(id.clone(), tagged_courses);

        Ok(id)
    }

    pub async fn get_courses(&self, id: &str) -> Option<Vec<Course>> {
        let cache = self.schedule_cache.read().await;
        cache.get(id).map(|tagged| tagged.courses.clone())
    }
}

#[derive(Debug)]
pub enum CacheError {
    CacheFull,
}

impl std::error::Error for CacheError {}

impl std::fmt::Display for CacheError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            &CacheError::CacheFull => {
                write!(f, "The cache is temporarily full")
            }
        }
    }
}
