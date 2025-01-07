import os
import datetime
import pytz
import json
from dataclasses import dataclass
from dotenv import load_dotenv
from pathlib import Path
from typing import Dict, List, Tuple

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from parser import ScheduleEntry
from utilities import progress_bar


@dataclass
class GoogleOAuthConfig:
    client_id: str
    client_secret: str

    @classmethod
    def from_env(cls) -> "GoogleOAuthConfig":
        load_dotenv()
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

        if not client_id or not client_secret:
            raise ValueError(
                "Missing cresentials. Ensure GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are set in your environment variables or .env file."
            )

        return cls(client_id=client_id, client_secret=client_secret)

    def to_client_config(self) -> dict:
        return {
            "installed": {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "auth_uri": self.auth_uri,
                "token_uri": self.token_uri,
                "redirect_uris": [self.redirect_uri],
            }
        }


class CalendarSynchronizer:

    SCOPES = ["https://www.googleapis.com/auth/calendar"]
    CALENDAR_SUMMARY = "UniSync v2.0"
    TIMEZONE = "Asia/Kolkata"

    TOKEN_PATH = Path("secrets/token.json")
    DEPLOYMENT_PATH = Path("secrets/deployment.json")

    def __init__(self) -> None:
        self.service = self._initialize_service()

    def _initialize_service(self) -> None:
        try:
            creds = self._get_credentials()
            service = build("calendar", "v3", credentials=creds)
            return service
        except Exception as e:
            raise RuntimeError(f"Failed to initialize calendar service > {str(e)}")

    def _get_credentials(self) -> Credentials:
        creds = None

        if self.TOKEN_PATH.exists():
            creds = Credentials.from_authorized_user_file(
                str(self.TOKEN_PATH), self.SCOPES
            )

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                oauth_config = GoogleOAuthConfig.from_env()
                flow = InstalledAppFlow.from_client_config(
                    oauth_config.to_client_config(), self.SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save the credentials
            self.TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(self.TOKEN_PATH, "w") as token:
                token.write(creds.to_json())

        return creds

    def _get_week_bounds(self) -> Tuple[str, str]:
        tz = pytz.timezone(self.TIMEZONE)
        now = datetime.datetime.now(tz)

        start = now - datetime.timedelta(
            days=now.weekday() + 1,
            hours=now.hour,
            minutes=now.minute,
            seconds=now.second,
            microseconds=now.microsecond,
        )

        end = start + datetime.timedelta(days=6, hours=23, minutes=59, seconds=59)

        return start.isoformat(), end.isoformat()

    def _get_or_create_calendar(self) -> str:
        if self.DEPLOYMENT_PATH.exists():
            with open(self.DEPLOYMENT_PATH, "r") as f:
                deployment: dict = json.load(f)
                calendar_id = deployment.get("calendar_id")
                if calendar_id and self._calendar_exists(calendar_id):
                    return calendar_id

        calendar = {"summary": self.CALENDAR_SUMMARY, "timeZone": self.TIMEZONE}

        try:
            created_calendar = self.service.calendars().insert(body=calendar).execute()
            calendar_id = created_calendar["id"]

            self.DEPLOYMENT_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(self.DEPLOYMENT_PATH, "w") as f:
                json.dump({"calendar_id": calendar_id}, f, indent=4)

            return calendar_id
        except HttpError as e:
            raise RuntimeError(f"Failed to create calendar: {str(e)}")

    def _calendar_exists(self, calendar_id: str) -> bool:
        try:
            self.service.calendars().get(calendarId=calendar_id).execute()
            return True
        except HttpError:
            return False

    def _create_event(
        self, entry: ScheduleEntry, day: int, base_date: datetime.datetime
    ) -> dict:
        day_delta = datetime.timedelta(days=(day - base_date.weekday()))
        event_date = base_date + day_delta

        start_time = datetime.datetime.strptime(entry.start_timing, "%I:%M%p")
        end_time = datetime.datetime.strptime(entry.end_timing, "%I:%M%p")

        start_datetime = event_date.replace(
            hour=start_time.hour, minute=start_time.minute, second=0, microsecond=0
        )
        end_datetime = event_date.replace(
            hour=end_time.hour, minute=end_time.minute, second=0, microsecond=0
        )

        return {
            "summary": f"{entry.course_code} - {entry.component_type}",
            "location": entry.venue,
            "start": {
                "dateTime": start_datetime.isoformat(),
                "timeZone": self.TIMEZONE,
            },
            "end": {
                "dateTime": end_datetime.isoformat(),
                "timeZone": self.TIMEZONE,
            },
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "popup", "minutes": 30},
                    {"method": "popup", "minutes": 15},
                ],
            },
        }

    def synchronize_schedule(self, schedule: Dict[int, List[ScheduleEntry]]) -> None:
        try:
            calendar_id = self._get_or_create_calendar()
            self._clear_existing_events(calendar_id)
            self._create_new_events(calendar_id, schedule)
        except Exception as e:
            raise RuntimeError(f"Failed to synchronize schedule: {str(e)}")

    def _clear_existing_events(self, calendar_id: str) -> None:
        start_time, end_time = self._get_week_bounds()

        events = []
        page_token = None
        while True:
            events_result = (
                self.service.events()
                .list(
                    calendarId=calendar_id,
                    timeMin=start_time,
                    timeMax=end_time,
                    pageToken=page_token,
                )
                .execute()
            )
            events.extend(events_result.get("items", []))
            page_token = events_result.get("nextPageToken")
            if not page_token:
                break

        for i, event in enumerate(events, 1):
            self.service.events().delete(
                calendarId=calendar_id, eventId=event["id"]
            ).execute()
            progress_bar("Clearing Existing Events", i, len(events))

    def _create_new_events(
        self, calendar_id: str, schedule: Dict[int, List[ScheduleEntry]]
    ) -> None:
        days = {
            0: "Monday",
            1: "Tuesday",
            2: "Wednesday",
            3: "Thursday",
            4: "Friday",
            5: "Saturday",
            6: "Sunday",
        }

        base_date = datetime.datetime.now(pytz.timezone(self.TIMEZONE))

        for day, entries in schedule.items():
            for i, entry in enumerate(entries, 1):
                event = self._create_event(entry, day, base_date)
                self.service.events().insert(
                    calendarId=calendar_id, body=event
                ).execute()
                progress_bar(f"Creating {days[day]} Events", i, len(entries))


def main():
    """test the synchronizer"""
    try:
        from scraper import SNUERPScraper
        from parser import ScheduleParser

        scraper = SNUERPScraper(headless=False)
        html_str = scraper.get_weekly_schedule_html()
        schedule = ScheduleParser.parse_schedule_html(html_str)

        calendar_synchronizer = CalendarSynchronizer()
        calendar_synchronizer.synchronize_schedule(schedule)
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
