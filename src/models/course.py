from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class Component(str, Enum):
    LECTURE = "LECTURE"
    TUTORIAL = "TUTORIAL"
    PRACTICAL = "PRACTICAL"


class Day(str, Enum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"


@dataclass
class Course:
    course_code: str
    course_title: str
    course_sections: List[CourseSection]
    timings: List[Timing]
    rooms: List[str]
    start_date: Optional[str]
    end_date: Optional[str]


@dataclass
class CourseSection:
    section: str
    component: Component


@dataclass
class Timing:
    start_time: Optional[str]
    end_time: Optional[str]
    days: List[Day]
