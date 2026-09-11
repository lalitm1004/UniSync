import json
from pathlib import Path
from typing import Any, Final, cast

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from tqdm import tqdm

from unisync.adapters.exporters.google.models import GoogleCalendarEvent
from unisync.config import AppConfig, GoogleOAuthConfig
from unisync.models.course import Course
from unisync.ports import CourseExporter


REVIEW_FILE_PATH: Final[Path] = Path("./data/export/google/review.json")
TOKEN_PATH: Final[Path] = Path("./data/export/google/client_token.json")

APP_CONFIG: Final[AppConfig] = AppConfig.from_toml()


class GoogleCalendarExporter(CourseExporter):
    SCOPES: Final[list[str]] = ["https://www.googleapis.com/auth/calendar"]
    CALENDAR_SUMMARY: Final[str] = "UniSync v4"

    def export_courses(self, course_list: list[Course]) -> None:
        google_calendar_events = GoogleCalendarEvent.from_course_list(course_list)

        GoogleCalendarExporter.write_to_json(google_calendar_events)
        input("Press enter when done editing file...")
        google_calendar_events = GoogleCalendarExporter.read_from_file()

        self._sync_to_calendar(google_calendar_events)

    @staticmethod
    def write_to_json(events: list[GoogleCalendarEvent]) -> None:
        REVIEW_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)

        events_data = [e.model_dump() for e in events]

        with open(REVIEW_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(events_data, f, indent=4, ensure_ascii=False)

    @staticmethod
    def read_from_file() -> list[GoogleCalendarEvent]:
        if not REVIEW_FILE_PATH.exists():
            raise FileNotFoundError

        with open(REVIEW_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError

        data = cast(list[Any], data)
        return [GoogleCalendarEvent.model_validate(item) for item in data]

    def _sync_to_calendar(self, events: list[GoogleCalendarEvent]) -> None:
        service = self._initialize_service()
        calendar_id = self._get_calendar_id(service)

        for event in tqdm(events, desc="Uploading events"):
            service.events().insert(
                calendarId=calendar_id, body=event.model_dump(mode="json")
            ).execute()

    def _initialize_service(self) -> Any:
        credentials = self._get_credentials()
        return build("calendar", "v3", credentials=credentials)

    def _get_credentials(self) -> Credentials:
        credentials = None

        if TOKEN_PATH.exists():
            credentials = Credentials.from_authorized_user_file(TOKEN_PATH, self.SCOPES)

        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                if TOKEN_PATH.exists():
                    TOKEN_PATH.unlink()

                oauth_config = GoogleOAuthConfig.from_env()
                flow = InstalledAppFlow.from_client_config(
                    oauth_config.to_client_config(),
                    self.SCOPES,
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

            TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(TOKEN_PATH, "w") as token:
                token.write(credentials.to_json())

        return cast(Credentials, credentials)

    def _get_calendar_id(self, service: Any) -> str:
        calendar = {"summary": self.CALENDAR_SUMMARY, "timeZone": APP_CONFIG.TIMEZONE}

        try:
            created_calendar = service.calendars().insert(body=calendar).execute()
            calendar_id = created_calendar["id"]

            return cast(str, calendar_id)
        except HttpError as e:
            raise RuntimeError(f"Failed to create calendar: {str(e)}")
