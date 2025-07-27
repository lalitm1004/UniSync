use once_cell::sync::Lazy;

macro_rules! env_var {
    ($key:literal) => {
        std::env::var($key).expect(concat!($key, " is not set"))
    };

    ($key:literal, $type:ty) => {
        std::env::var($key)
            .expect(concat!($key, " is not set"))
            .parse::<$type>()
            .expect(concat!($key, " must be a valid ", stringify!($type)))
    };
}

pub struct Config {
    pub jwt_secret: String,
    pub database_url: String,
    pub extension_access_key: String,
    pub schedule_cleanup_after: u64,
    pub schedule_cache_max_size: usize,
    pub google_client_id: String,
    pub google_client_secret: String,
}

pub static CONFIG: Lazy<Config> = Lazy::new(|| {
    dotenvy::dotenv().ok();

    Config {
        jwt_secret: env_var!("JWT_SECRET"),
        database_url: env_var!("DATABASE_URL"),
        extension_access_key: env_var!("EXTENSION_ACCESS_KEY"),
        schedule_cleanup_after: env_var!("SCHEDULE_CLEANUP_AFTER", u64),
        schedule_cache_max_size: env_var!("SCHEDULE_CACHE_MAX_SIZE", usize),
        google_client_id: env_var!("GOOGLE_CLIENT_ID"),
        google_client_secret: env_var!("GOOGLE_CLIENT_SECRET"),
    }
});
