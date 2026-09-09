from __future__ import annotations

from datetime import date, time
from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, Strict


StrictDate = Annotated[date, Strict()]
StrictTime = Annotated[time, Strict()]


class Course(BaseModel):
    course_code: str
    course_title: str
    is_enrolled: bool
    batches: list[CourseBatch]


class CourseBatch(BaseModel):
    component: str
    timings: list[Timing]
    start_date: StrictDate
    end_date: StrictDate


class Timing(BaseModel):
    start_time: StrictTime
    end_time: StrictTime
    venue: str
    days: list[Day]


class Day(StrEnum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"
