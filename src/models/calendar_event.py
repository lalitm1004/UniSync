from __future__ import annotations

from datetime import date, datetime, time, timedelta
from pydantic import BaseModel
from typing import Dict, List
from zoneinfo import ZoneInfo

from models.course import Course, CourseBatch, Day, Timing
from config import AppConfig

APP_CONFIG = AppConfig.from_toml()


class CalendarTime(BaseModel):
    dateTime: str
    timeZone: str = APP_CONFIG.TIMEZONE


class CalendarEvent(BaseModel):
    summary: str
    description: str
    location: str
    start: CalendarTime
    end: CalendarTime
    colorId: str
    reminders: Dict = {
        "useDefault": False,
        "overrides": [
            {"method": "popup", "minutes": 15},
            {"method": "popup", "minutes": 30},
        ],
    }
    recurrence: List[str]

    @staticmethod
    def from_course_list(course_list: List[Course]) -> List[CalendarEvent]:
        return [
            event
            for course in course_list
            for event in CalendarEvent.from_course(course)
        ]

    @staticmethod
    def from_course(course: Course) -> List[CalendarEvent]:
        events: List[CalendarEvent] = []

        for batch in course.batches:
            if isinstance(batch.component, tuple):
                component_type, batch_num = batch.component
                component_str = f"{component_type.value}{batch_num}"
            else:
                component_str = batch.component

            # use course_shorthand if available, otherwise generate it
            shorthand = course.course_shorthand
            if shorthand is None:
                shorthand = f"{course.course_code.upper()} {course.course_title}"

            summary = f"{shorthand} - {component_str}"

            for timing in batch.timings:
                event = _create_event_from_timing(
                    summary=summary,
                    description=course.course_title,
                    batch=batch,
                    timing=timing,
                )
                events.append(event)

        return events


def _create_event_from_timing(
    summary: str,
    description: str,
    batch: CourseBatch,
    timing: Timing,
) -> CalendarEvent:
    tz = ZoneInfo(APP_CONFIG.TIMEZONE)

    first_occurrence = _find_first_occurrence(batch.start_date_obj, timing.days)

    start_dt = datetime.combine(first_occurrence, timing.start_time_obj, tzinfo=tz)
    end_dt = datetime.combine(first_occurrence, timing.end_time_obj, tzinfo=tz)

    recurrence = _build_recurrence(batch, timing)

    return CalendarEvent(
        summary=summary,
        description=description,
        location=timing.venue,
        start=CalendarTime(dateTime=start_dt.isoformat()),
        end=CalendarTime(dateTime=end_dt.isoformat()),
        colorId=str(batch.event_color),
        recurrence=recurrence,
    )


def _find_first_occurrence(start_date: date, days: List[Day]) -> date:
    if not days:
        return start_date

    current = start_date
    for _ in range(7):
        weekday = current.weekday()
        if Day.from_weekday(weekday) in days:
            return current
        current += timedelta(days=1)

    return start_date


def _build_recurrence(batch: CourseBatch, timing: Timing) -> List[str]:
    recurrence: List[str] = []

    if timing.days:
        byday = ",".join(day.rrule for day in timing.days)

        until_utc = datetime.combine(
            batch.end_date_obj,
            time(23, 59, 59),
            tzinfo=ZoneInfo(APP_CONFIG.TIMEZONE),
        ).astimezone(ZoneInfo("UTC"))
        until_str = until_utc.strftime("%Y%m%dT%H%M%SZ")

        rrule = f"RRULE:FREQ=WEEKLY;BYDAY={byday};UNTIL={until_str}"
        recurrence.append(rrule)

    exdates = _build_exdates(batch, timing)
    if exdates:
        recurrence.append(exdates)

    return recurrence


def _build_exdates(batch: CourseBatch, timing: Timing) -> str:
    excluded_datetimes: List[str] = []

    for excluded_date in APP_CONFIG.EXCLUDED_DATES:
        # check if excluded date is within the batch date range
        if not (batch.start_date_obj <= excluded_date <= batch.end_date_obj):
            continue

        # check if excluded date's weekday matches any timing day
        weekday = excluded_date.weekday()
        if Day.from_weekday(weekday) not in timing.days:
            continue

        # format as YYYYMMDDTHHMMSS (local time with TZID)
        excluded_dt_str = datetime.combine(excluded_date, timing.start_time_obj).strftime(
            "%Y%m%dT%H%M%S"
        )
        excluded_datetimes.append(excluded_dt_str)

    if not excluded_datetimes:
        return ""

    return f"EXDATE;TZID={APP_CONFIG.TIMEZONE}:{','.join(excluded_datetimes)}"


def test() -> None:
    from utils import get_sample_course_list

    sample_course = get_sample_course_list()[0]
    print(sample_course.pretty_str())

    events = CalendarEvent.from_course(sample_course)

    print(f"\nGenerated {len(events)} CalendarEvent(s):\n")

    for i, event in enumerate(events, 1):
        print(f"--- Event {i} ---")
        print(f"Summary: {event.summary}")
        print(f"Location: {event.location}")
        print(f"Start: {event.start.dateTime} ({event.start.timeZone})")
        print(f"End: {event.end.dateTime} ({event.end.timeZone})")
        print(f"Color ID: {event.colorId}")
        print("Recurrence:")
        for rule in event.recurrence:
            print(f"  {rule}")
        print()


if __name__ == "__main__":
    test()
