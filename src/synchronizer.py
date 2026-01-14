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
    CALENDAR_SUMMARY: Final[str] = "UniSync v3 TEST"

    TOKEN_PATH: Final[Path] = Path("data/cache/client_token.json")

    def __init__(self) -> None:
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

    def _get_calendar_id(self) -> str:
        calendar = {"summary": self.CALENDAR_SUMMARY, "timeZone": APP_CONFIG.TIMEZONE}

        try:
            created_calendar = self._service.calendars().insert(body=calendar).execute()
            calendar_id = created_calendar["id"]

            return calendar_id
        except HttpError as e:
            raise RuntimeError(f"Failed to create calendar: {str(e)}")

    def synchronize(self, course_list: List[Course]) -> None:
        event_list = CalendarEvent.from_course_list(course_list)

        calendar_id = self._get_calendar_id()

        for event in tqdm(event_list):
            try:
                self._service.events().insert(
                    calendarId=calendar_id, body=event.model_dump(mode="json")
                ).execute()
            except HttpError as e:
                print(f"Failed to create event: {str(e)}")
                print(f"Event: {event}")


def test() -> None:
    from datetime import date, time
    from models.course import CourseBatch, ComponentType, Timing, Day
    from typing import cast

    sample_course = [
        Course(
            course_code="CSD366",
            course_title="Reinforcement Learning",
            is_enrolled=True,
            batches=[
                CourseBatch(
                    event_color=5,
                    component=(ComponentType.L, 1),
                    start_date=date(2026, 1, 12),
                    end_date=date(2026, 4, 28),
                    timings=[
                        Timing(
                            start_time=cast(time, "08:00"),
                            end_time=cast(time, "08:55"),
                            days=[Day.MONDAY, Day.WEDNESDAY],
                            venue="D217",
                        ),
                        Timing(
                            start_time=cast(time, "12:00"),
                            end_time=cast(time, "13:55"),
                            days=[Day.FRIDAY],
                            venue="D217",
                        ),
                    ],
                ),
                CourseBatch(
                    event_color=3,
                    component=(ComponentType.P, 2),
                    start_date=date(2026, 1, 12),
                    end_date=date(2026, 4, 28),
                    timings=[
                        Timing(
                            start_time=cast(time, "12:10"),
                            end_time=cast(time, "14:05"),
                            days=[Day.TUESDAY],
                            venue="C317",
                        ),
                    ],
                ),
            ],
        ).generate_course_shorthand()
    ]

    cs = CalendarSynchronizer()
    cs.synchronize(sample_course)


if __name__ == "__main__":
    test()
