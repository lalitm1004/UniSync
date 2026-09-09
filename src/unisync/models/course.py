"""Course-related domain models.

These models describe the courses a student is enrolled in, their
lecture/tutorial/practical batches, and the weekly timings of each session.
"""

from __future__ import annotations

from datetime import date, time
from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, Strict


StrictDate = Annotated[date, Strict()]
StrictTime = Annotated[time, Strict()]


class Course(BaseModel):
    """A course in which the student may be enrolled.

    Attributes:
        course_code: Unique identifier for the course (e.g. ``"CSD361"``).
        course_title: Human-readable name of the course.
        is_enrolled: Whether the student is currently enrolled.
        batches: Lecture/tutorial/practical sections belonging to the course.
    """

    course_code: str
    course_title: str
    is_enrolled: bool
    batches: list[CourseBatch]


class CourseBatch(BaseModel):
    """A single section of a course with a fixed schedule.

    Attributes:
        component: Section type, such as a lecture (``"L1"``) or
            practical (``"P1"``).
        timings: Weekly class sessions for this batch.
        start_date: First day the batch is scheduled.
        end_date: Last day the batch is scheduled.
    """

    component: str
    timings: list[Timing]
    start_date: StrictDate
    end_date: StrictDate


class Timing(BaseModel):
    """A weekly class session at a specific time and venue.

    Attributes:
        start_time: Time the session begins.
        end_time: Time the session ends.
        venue: Room or location where the session is held (e.g. ``"D210"``).
        days: Days of the week the session is held.
    """

    start_time: StrictTime
    end_time: StrictTime
    venue: str
    days: list[Day]


class Day(StrEnum):
    """Day of the week on which a class session is held."""

    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"
