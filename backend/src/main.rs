use poem::{EndpointExt, Route, Server, listener::TcpListener, middleware::Cors};
use poem_openapi::OpenApiService;
use std::process::ExitCode;

use unisync_backend::{AppState, CacheApi};

#[tokio::main]
async fn main() -> ExitCode {
    println!("Initializing app state...");
    let app_state = match AppState::new().await {
        Ok(state) => state,
        Err(e) => {
            eprintln!("Error initializing AppState: {}", e);
            return ExitCode::FAILURE;
        }
    };
    println!("Successfully intiialized app state");

    let api_service =
        OpenApiService::new(CacheApi, "unisync-backend", "1.0").server("http://localhost:3000");
    let ui = api_service.swagger_ui();

    let app = Route::new()
        .nest("/", api_service)
        .nest("/docs", ui)
        .data(app_state)
        .with(Cors::new());

    let _ = Server::new(TcpListener::bind("127.0.0.1:3000"))
        .run(app)
        .await;

    ExitCode::FAILURE
}
