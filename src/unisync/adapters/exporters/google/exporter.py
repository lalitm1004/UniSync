"""Google Calendar exporter and OAuth integration."""

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
    """Export courses to Google Calendar.

    Converts courses into events, writes them to a review file, and uploads
    them to a dedicated calendar after confirmation.

    Attributes:
        SCOPES: OAuth scopes requested for the calendar API.
        CALENDAR_SUMMARY: Name of the target calendar.
    """

    SCOPES: Final[list[str]] = ["https://www.googleapis.com/auth/calendar"]
    CALENDAR_SUMMARY: Final[str] = "UniSync v4"

    def export_courses(self, course_list: list[Course]) -> None:
        """Convert courses to events, await review, then upload to Google Calendar.

        Args:
            course_list: The courses to export.
        """
        google_calendar_events = GoogleCalendarEvent.from_course_list(course_list)

        GoogleCalendarExporter.write_to_json(google_calendar_events)
        input("Press enter when done editing file...")
        google_calendar_events = GoogleCalendarExporter.read_from_file()

        self._sync_to_calendar(google_calendar_events)

    @staticmethod
    def write_to_json(events: list[GoogleCalendarEvent]) -> None:
        """Serialize events to the review file as JSON.

        Args:
            events: The events to write.
        """
        REVIEW_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)

        events_data = [e.model_dump() for e in events]

        with open(REVIEW_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(events_data, f, indent=4, ensure_ascii=False)

    @staticmethod
    def read_from_file() -> list[GoogleCalendarEvent]:
        """Read and validate events from the review file.

        Returns:
            The parsed events.

        Raises:
            FileNotFoundError: If the review file does not exist.
            ValueError: If the file does not contain a JSON list.
        """
        if not REVIEW_FILE_PATH.exists():
            raise FileNotFoundError

        with open(REVIEW_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError

        data = cast(list[Any], data)
        return [GoogleCalendarEvent.model_validate(item) for item in data]

    def _sync_to_calendar(self, events: list[GoogleCalendarEvent]) -> None:
        """Upload events to the target Google Calendar.

        Args:
            events: The events to upload.
        """
        service = self._initialize_service()
        calendar_id = self._get_calendar_id(service)

        for event in tqdm(events, desc="Uploading events"):
            service.events().insert(
                calendarId=calendar_id, body=event.model_dump(mode="json")
            ).execute()

    def _initialize_service(self) -> Any:
        """Build an authenticated Google Calendar service.

        Returns:
            The calendar service resource.
        """
        credentials = self._get_credentials()
        return build("calendar", "v3", credentials=credentials)

    def _get_credentials(self) -> Credentials:
        """Load cached credentials or run the OAuth flow to obtain new ones.

        Returns:
            Valid OAuth credentials.
        """
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
        """Create the target calendar and return its ID.

        Args:
            service: The calendar service resource.

        Returns:
            The ID of the created calendar.

        Raises:
            RuntimeError: If the calendar could not be created.
        """
        calendar = {"summary": self.CALENDAR_SUMMARY, "timeZone": APP_CONFIG.TIMEZONE}

        try:
            created_calendar = service.calendars().insert(body=calendar).execute()
            calendar_id = created_calendar["id"]

            return cast(str, calendar_id)
        except HttpError as e:
            raise RuntimeError(f"Failed to create calendar: {str(e)}")
