from __future__ import annotations

import json
import re
from datetime import date, time
from enum import StrEnum
from pathlib import Path
from pydantic import BaseModel, Field, field_validator
from typing import Final, List, Optional, Tuple, Union

REVIEW_FILE_PATH: Final[Path] = Path("data/review/review-courses.json")

TIME_RE = re.compile(r"^(?:[01]?\d|2[0-3]):[0-5]\d$")


class Course(BaseModel):
    course_code: str
    course_title: str
    is_enrolled: bool = Field(default=True)
    batches: List[CourseBatch] = Field(default_factory=list)
    course_shorthand: Optional[str] = Field(default=None)

    def generate_course_shorthand(self) -> Course:
        self.course_shorthand = f"{self.course_code.upper()} {_convert_title_to_shorthand(self.course_title)}"
        return self

    def pretty_str(self, indent: int = 0) -> str:
        lines = []
        prefix = "    " * indent

        lines.append(f"{prefix}Course: {self.course_code}")
        lines.append(f"{prefix}Shorthand: {self.course_shorthand}")
        lines.append(f"{prefix}  Title: {self.course_title}")
        lines.append(f"{prefix}  Enrolled: {self.is_enrolled}")

        if self.batches:
            lines.append(f"{prefix}  Batches:")
            for i, batch in enumerate(self.batches, 1):
                lines.append(f"{prefix}    Batch {i}:")
                lines.append(batch.pretty_str(indent + 3))
        else:
            lines.append(f"{prefix}  Batches: None")

        return "\n".join(lines)


class CourseBatch(BaseModel):
    event_color: int = Field(ge=1, le=11, default=1)
    component: Union[Tuple[ComponentType, int], str]
    timings: List[Timing] = Field(default_factory=list)
    start_date: date
    end_date: date

    def pretty_str(self, indent: int = 0) -> str:
        lines = []
        prefix = "    " * indent

        if isinstance(self.component, tuple):
            comp_str = f"{self.component[0].value} {self.component[1]}"
        else:
            comp_str = self.component

        lines.append(f"{prefix}Component: {comp_str}")
        lines.append(f"{prefix}Color: {self.event_color}")
        lines.append(f"{prefix}DateRange: {self.start_date} to {self.end_date}")

        if self.timings:
            lines.append(f"{prefix}Timings:")
            for timing in self.timings:
                lines.append(timing.pretty_str(indent + 1))
        else:
            lines.append(f"{prefix}Timings: None")

        return "\n".join(lines)


class Timing(BaseModel):
    start_time: time
    end_time: time
    days: List[Days] = Field(default_factory=list)
    venue: str

    @field_validator("start_time", "end_time", mode="before")
    def _convert_time(cls, value: str) -> time:
        if not isinstance(value, str):
            raise ValueError(f"Invalid type for time: {type(value)}. Expected a string")

        if not TIME_RE.match(value):
            raise ValueError(
                f"invalid time format, expected HH:MM 24-hour, got: {value}"
            )

        hour_str, minute_str = value.split(":")
        hour = int(hour_str)
        minute = int(minute_str)

        return time(hour, minute)

    def pretty_str(self, indent: int = 0) -> str:
        prefix = "    " * indent
        time_str = (
            f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"
        )
        days_str = (
            ", ".join(day.value.capitalize() for day in self.days)
            if self.days
            else "No days"
        )

        return f"{prefix}{time_str} | {days_str} | {self.venue}"


class ComponentType(StrEnum):
    L = "L"
    T = "T"
    P = "P"


class Days(StrEnum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"


def _convert_title_to_shorthand(title: str) -> str:
    # remove punctuation
    title = re.sub(r"[^\w\s]", "", title)

    # recursively reduce double spaces to single space
    while "  " in title:
        title = title.replace("  ", " ")

    # split by whitespace, take first letter of each token, capitalize
    tokens = title.split()
    shorthand = "".join(token[0] for token in tokens if token)

    return shorthand.upper()


def write_courses_to_json(
    courses: List[Course], path: Union[str, Path] = REVIEW_FILE_PATH
) -> None:
    if isinstance(path, str):
        path = Path(path)

    path.parent.mkdir(parents=True, exist_ok=True)

    courses_date = [c.model_dump() for c in courses]

    with open(path, "w", encoding="utf-8") as f:
        json.dump(courses_date, f, indent=4, ensure_ascii=False)


def read_courses_from_json(path: Union[str, Path] = REVIEW_FILE_PATH) -> List[Course]:
    if isinstance(path, str):
        path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Course file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("Invalid course file format: expected a list")

    return [Course.model_validate(item) for item in data]
