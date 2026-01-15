import json
from pathlib import Path
from typing import cast, Final, List
from tqdm import tqdm

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import AppConfig, GoogleOAuthConfig
from models.course import Course
from models.calendar_event import CalendarEvent

APP_CONFIG = AppConfig.from_toml()


class CalendarSynchronizer:
    SCOPES: Final[List[str]] = ["https://www.googleapis.com/auth/calendar"]
    CALENDAR_SUMMARY: Final[str] = "UniSync v3"

    CACHE_DATA_PATH: Final[Path] = Path("data/cache")
    TOKEN_PATH: Final[Path] = CACHE_DATA_PATH / "client_token.json"
    CALENDAR_DETAILS_PATH: Final[Path] = CACHE_DATA_PATH / "calendar_details.json"

    def __init__(self) -> None:
        self.CACHE_DATA_PATH.mkdir(parents=True, exist_ok=True)
        self._service = self._initalize_service()

    def _initalize_service(self):
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

    def _get_calendar_id(
        self, calendar_details_path: Path = CALENDAR_DETAILS_PATH
    ) -> str:
        calendar = {"summary": self.CALENDAR_SUMMARY, "timeZone": APP_CONFIG.TIMEZONE}

        try:
            created_calendar = self._service.calendars().insert(body=calendar).execute()
            calendar_id = created_calendar["id"]

            with open(calendar_details_path, "w") as f:
                json.dump({"calendar_id": calendar_id}, f)

            return calendar_id
        except HttpError as e:
            raise RuntimeError(f"Failed to create calendar: {str(e)}")

    def synchronize(self, course_list: List[Course]) -> None:
        event_list = CalendarEvent.from_course_list(course_list)

        calendar_id = self._get_calendar_id()

        for event in tqdm(event_list, desc="Creating calendar events"):
            try:
                self._service.events().insert(
                    calendarId=calendar_id, body=event.model_dump(mode="json")
                ).execute()
            except HttpError as e:
                print(f"Failed to create event: {str(e)}")
                print(f"Event: {event}")


def test() -> None:
    from utils import get_sample_course_list

    sample_courses = get_sample_course_list()

    cs = CalendarSynchronizer()
    cs.synchronize(sample_courses)


if __name__ == "__main__":
    test()
