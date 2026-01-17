from __future__ import annotations

import re
from datetime import datetime, date, time
from enum import StrEnum
from pydantic import BaseModel, Field, field_validator, model_validator
from re import Pattern
from typing import Final, List, Optional, Tuple, Union

from config import APP_CONFIG

VENUE_RE: Final[Pattern] = re.compile(r"[A-Za-z]\d{3}[A-Za-z]?")


class Course(BaseModel):
    course_code: str
    course_title: str
    shorthand: Optional[str]
    is_enrolled: bool
    batches: List[CourseBatch]

    @model_validator(mode="after")
    def _generate_course_shorthand(self) -> Course:
        if self.course_shorthand is None:
            # remove punctuation
            title = re.sub(r"[^\w\s]", "", self.course_title)

            # recursively reduce double spaces to single space
            while "  " in title:
                title = title.replace("  ", " ")

            # split by whitespace, take first letter of each token, capitalize
            tokens = title.split()
            shorthand = "".join(token[0] for token in tokens if token)

            self.course_shorthand = f"{self.course_code.upper()} {shorthand}"
        return self


class CourseBatch(BaseModel):
    event_color: int = Field(ge=1, le=11)
    component: Union[Tuple[ComponentType, int], str]
    timings: List[Timing]
    start_date: str = Field(default=APP_CONFIG.default_start_date.isoformat())
    end_date: str = Field(default=APP_CONFIG.default_end_date.isoformat())

    @field_validator("start_date", "end_date", mode="before")
    def _convert_date(cls, value: Union[date, str]) -> str:
        if isinstance(value, date):
            return value.isoformat()

        if isinstance(value, str):
            try:
                parsed = datetime.strptime(value, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError("Date must be in YYYY-MM-DD ISO format")

            return parsed.isoformat()

        raise TypeError(
            f"Invalid type for date field: {type(value)}. Expected a Union[date, str]"
        )


class ComponentType(StrEnum):
    L = "L"
    T = "T"
    P = "P"


class Timing(BaseModel):
    start_time: str
    end_time: str
    days: List[Day]
    venue: str = Field(default="TBA")

    @field_validator("start_time", "end_time", mode="before")
    def _convert_time(cls, value: Union[time, str]) -> str:
        if isinstance(value, time):
            return value.strftime("%H:%M")

        if isinstance(value, str):
            try:
                parsed = datetime.strptime(value, "%H:%M").time()
            except ValueError:
                raise ValueError("Time must be in HH:MM 24-hour format")

            return parsed.strftime("%H:%M")

        raise TypeError(
            f"Invalid type for time field: {type(value)}. Expected a Union[time, str]"
        )

    @field_validator("venue", mode="before")
    def _convert_venue(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError(f"Invalid type for venue: {type(value)}. Expected a str")

        match_ = VENUE_RE.search(value)
        if match_:
            return match_.group(0)

        return value


class Day(StrEnum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"

    @property
    def rrule(self) -> str:
        match self:
            case Day.MONDAY:
                return "MO"
            case Day.TUESDAY:
                return "TU"
            case Day.WEDNESDAY:
                return "WE"
            case Day.THURSDAY:
                return "TH"
            case Day.FRIDAY:
                return "FR"
            case Day.SATURDAY:
                return "SA"
            case Day.SUNDAY:
                return "SU"

    @classmethod
    def from_weekday(cls, weekday: int) -> Day:
        match weekday:
            case 0:
                return cls.MONDAY
            case 1:
                return cls.TUESDAY
            case 2:
                return cls.WEDNESDAY
            case 3:
                return cls.THURSDAY
            case 4:
                return cls.FRIDAY
            case 5:
                return cls.SATURDAY
            case 6:
                return cls.SUNDAY
            case _:
                raise ValueError(f"Invalid weekday: {weekday}")
