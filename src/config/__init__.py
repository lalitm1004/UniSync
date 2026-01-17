from config.app_config import AppConfig
from config.erp_credentials_config import ERPCredentials
from config.google_oauth_config import GoogleOAuthConfig

APP_CONFIG = AppConfig.from_toml()
ERP_CREDENTIALS = ERPCredentials.from_env()
GOOGLE_OAUTH_CONFIG = GoogleOAuthConfig.from_env()

__all__ = ["APP_CONFIG", "ERP_CREDENTIALS", "GOOGLE_OAUTH_CONFIG"]
