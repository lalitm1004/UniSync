from pathlib import Path
from typing import cast, Final, List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
# from googleapiclient.errors import HttpError

from config import GoogleOAuthConfig


class CalendarSynchronizer:
    SCOPES: Final[List[str]] = ["https://www.googleapis.com/auth/calendar"]
    CALENDAR_SUMMARY: Final[str] = "UniSync v3"

    TOKEN_PATH: Final[Path] = Path("data/cache/client_token.json")

    def __init__(self) -> None:
        self._service: Resource = self._initalize_service()

    def _initalize_service(self) -> Resource:
        try:
            credentials = self._get_credentials()
            service = build("calendar", "v3", credentials=credentials)
            return service
        except Exception as e:
            raise RuntimeError("Failed to initialize calendar service:", e)

    def _get_credentials(
        self, token_path: Path = TOKEN_PATH, scopes: List[str] = SCOPES
    ) -> Credentials:
        credentials = None

        if token_path.exists():
            credentials = Credentials.from_authorized_user_file(token_path, scopes)

        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                if token_path.exists():
                    token_path.unlink()

                oauth_config = GoogleOAuthConfig.from_env()
                flow = InstalledAppFlow.from_client_config(
                    oauth_config.to_client_config(),
                    scopes,
                    redirect_uri="http://localhost",
                )

                flow.oauth2session.fetch_token_kwargs = {
                    "client_secret": oauth_config.client_secret,
                }

                credentials = flow.run_local_server(
                    port=0,
                    access_type="offline",
                    prompt="consent",
                    include_granted_scopes="true",
                )

            token_path.parent.mkdir(parents=True, exist_ok=True)
            with open(token_path, "w") as token:
                token.write(credentials.to_json())

        return cast(Credentials, credentials)


def test() -> None:
    _ = CalendarSynchronizer()


if __name__ == "__main__":
    test()
