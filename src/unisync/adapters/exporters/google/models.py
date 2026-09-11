"""Google Calendar event models and course-to-event mapping."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel
from zoneinfo import ZoneInfo

from unisync.models import Course, CourseBatch, Timing
from unisync.config import AppConfig
from unisync.utils import TimeUtils

APP_CONFIG = AppConfig.from_toml()


class GoogleCalendarEvent(BaseModel):
    """A single event as understood by the Google Calendar API.

    Attributes:
        summary: Event title.
        description: Longer event description.
        location: Venue where the session is held.
        start: Start time of the first occurrence.
        end: End time of the first occurrence.
        colorId: Google Calendar color identifier.
        reminders: Popup reminders to apply to the event.
        recurrence: RFC 5545 recurrence and exclusion rules.
    """

    summary: str
    description: str
    location: str
    start: GoogleCalendarTime
    end: GoogleCalendarTime
    colorId: str

    reminders: dict[str, Any] = {
        "useDefault": False,
        "override": [
            {"method": "popup", "minutes": 15},
            {"method": "popup", "minutes": 30},
        ],
    }
    recurrence: list[str]

    @staticmethod
    def from_course_list(course_list: list[Course]) -> list[GoogleCalendarEvent]:
        """Flatten a list of courses into a list of calendar events.

        Args:
            course_list: The courses to convert.

        Returns:
            All events generated from every batch and timing of every course.
        """
        return [
            event
            for course in course_list
            for event in GoogleCalendarEvent.from_course(course)
        ]

    @staticmethod
    def from_course(course: Course) -> list[GoogleCalendarEvent]:
        """Generate one event per timing of every batch in ``course``.

        Args:
            course: The course to convert.

        Returns:
            The events generated from the course.
        """
        events: list[GoogleCalendarEvent] = []

        for batch in course.batches:
            course_summary = f"{course.course_code} - {batch.component}"

            for timing in batch.timings:
                event = _create_event_from_timing(
                    summary=course_summary,
                    description=course.course_title,
                    batch=batch,
                    timing=timing,
                )

                events.append(event)

        return events


class GoogleCalendarTime(BaseModel):
    """A timezone-aware instant as expected by the Google Calendar API.

    Attributes:
        dateTime: ISO 8601 datetime string.
        timeZone: IANA timezone of the datetime.
    """

    dateTime: str
    timeZone: str = APP_CONFIG.TIMEZONE


def _create_event_from_timing(
    summary: str,
    description: str,
    batch: CourseBatch,
    timing: Timing,
) -> GoogleCalendarEvent:
    """Build a :class:`GoogleCalendarEvent` for a single weekly session.

    Args:
        summary: Event title.
        description: Event description.
        batch: The course batch owning the session.
        timing: The session timing.

    Returns:
        The generated calendar event.
    """
    tz = ZoneInfo(APP_CONFIG.TIMEZONE)

    first_occurrence = TimeUtils.find_first_occurrence(batch.start_date, timing.days)

    start_dt = datetime.combine(first_occurrence, timing.start_time, tzinfo=tz)
    end_dt = datetime.combine(first_occurrence, timing.end_time, tzinfo=tz)

    recurrence = TimeUtils.build_recurrence(
        batch, timing, APP_CONFIG.TIMEZONE, APP_CONFIG.EXCLUDED_DATES
    )

    return GoogleCalendarEvent(
        summary=summary,
        description=description,
        location=timing.venue,
        start=GoogleCalendarTime(dateTime=start_dt.isoformat()),
        end=GoogleCalendarTime(dateTime=end_dt.isoformat()),
        colorId=str(""),
        recurrence=recurrence,
    )
