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
        return [
            event
            for course in course_list
            for event in GoogleCalendarEvent.from_course(course)
        ]

    @staticmethod
    def from_course(course: Course) -> list[GoogleCalendarEvent]:
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
    dateTime: str
    timeZone: str = APP_CONFIG.TIMEZONE


def _create_event_from_timing(
    summary: str,
    description: str,
    batch: CourseBatch,
    timing: Timing,
) -> GoogleCalendarEvent:
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
