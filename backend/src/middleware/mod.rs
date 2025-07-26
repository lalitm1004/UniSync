use jsonwebtoken::{Algorithm, DecodingKey, Validation, decode, errors::ErrorKind};
use poem_openapi::{ApiResponse, SecurityScheme, auth::Bearer, payload::Json};

use crate::{CONFIG, api::ErrorResponse, models::Claims};

#[allow(dead_code)]
#[derive(SecurityScheme)]
#[oai(
    ty = "bearer",
    key_name = "EXTENSION_ACCESS_KEY",
    key_in = "header",
    checker = "extension_access_checker"
)]
pub struct ExtensionAuth(String);

#[derive(ApiResponse)]
enum ExtensionAuthErrorResponse {
    #[oai(status = 401)]
    Unauthorized(Json<ErrorResponse>),
}

async fn extension_access_checker(
    _req: &poem::Request,
    bearer: Bearer,
) -> Result<String, poem::Error> {
    let header_data = bearer.token;

    if header_data == CONFIG.extension_access_key {
        Ok(header_data)
    } else {
        Err(
            ExtensionAuthErrorResponse::Unauthorized(Json(ErrorResponse {
                code: "UNAUTHORIZED".to_string(),
                message: None,
                details: None,
            }))
            .into(),
        )
    }
}

#[allow(dead_code)]
#[derive(SecurityScheme)]
#[oai(
    ty = "bearer",
    key_name = "JWT",
    key_in = "header",
    checker = "jwt_checker"
)]
pub struct JwtAuth(pub Claims);

#[derive(ApiResponse)]
enum JwtErrorResponse {
    #[oai(status = 401)]
    Unauthorized(Json<ErrorResponse>),

    #[oai(status = 400)]
    BadRequest(Json<ErrorResponse>),
}

async fn jwt_checker(_req: &poem::Request, bearer: Bearer) -> Result<Claims, poem::Error> {
    let mut validation = Validation::new(Algorithm::HS256);
    validation.validate_exp = true;
    validation.set_audience(&["authenticated"]);

    let token_data = decode::<Claims>(
        &bearer.token,
        &DecodingKey::from_secret(CONFIG.jwt_secret.as_bytes()),
        &validation,
    )
    .map_err(|e| match e.kind() {
        ErrorKind::ExpiredSignature => JwtErrorResponse::Unauthorized(Json(ErrorResponse {
            code: "JWT_EXPIRED".to_string(),
            message: Some("Token has expired".to_string()),
            details: None,
        })),

        ErrorKind::InvalidSignature => JwtErrorResponse::Unauthorized(Json(ErrorResponse {
            code: "JWT_INVALID".to_string(),
            message: Some("Invalid token signature".to_string()),
            details: None,
        })),

        _ => JwtErrorResponse::BadRequest(Json(ErrorResponse {
            code: "JWT_MALFORMED".to_string(),
            message: Some("Invalid token format".to_string()),
            details: Some(e.to_string()),
        })),
    })?;

    Ok(token_data.claims)
}
