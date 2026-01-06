from __future__ import annotations

import json
from enum import StrEnum
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Final, List, Union

REVIEW_FILE_PATH: Final[Path] = Path("data/review/review-courses.json")


class Course(BaseModel):
    course_id: str
    course_name: str
    batches: List[CourseBatch] = Field(default_factory=list)


class CourseBatch(BaseModel):
    event_color: int = Field(ge=1, le=11)
    component_type: ComponentType
    batch_number: int
    timings: List[Timing] = Field(default_factory=list)


class Timing(BaseModel):
    start_time: str = Field(pattern=r"^(?:[01]?\d|2[0-3]):[0-5]\d$")
    end_time: str = Field(pattern=r"^(?:[01]?\d|2[0-3]):[0-5]\d$")
    days: List[Days] = Field(default_factory=list)
    venue: str


class ComponentType(StrEnum):
    L = "LECTURE"
    T = "TUTORIAL"
    P = "PRACTICAL"


class Days(StrEnum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"


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


def test() -> None:
    sample_courses = [
        Course(
            course_id="CS101",
            course_name="Introduction to Programming",
            batches=[
                CourseBatch(
                    event_color=5,
                    component_type=ComponentType.L,
                    batch_number=1,
                    timings=[
                        Timing(
                            start_time="09:00",
                            end_time="10:30",
                            days=[Days.MONDAY, Days.WEDNESDAY],
                            venue="Room 101",
                        ),
                        Timing(
                            start_time="12:00",
                            end_time="13:30",
                            days=[Days.MONDAY, Days.WEDNESDAY],
                            venue="Room 101",
                        ),
                    ],
                ),
                CourseBatch(
                    event_color=3,
                    component_type=ComponentType.P,
                    batch_number=1,
                    timings=[
                        Timing(
                            start_time="14:00",
                            end_time="16:00",
                            days=[Days.FRIDAY],
                            venue="Lab A",
                        )
                    ],
                ),
            ],
        ),
        Course(
            course_id="MATH201",
            course_name="Linear Algebra",
            batches=[
                CourseBatch(
                    event_color=8,
                    component_type=ComponentType.L,
                    batch_number=1,
                    timings=[
                        Timing(
                            start_time="11:00",
                            end_time="12:30",
                            days=[Days.TUESDAY, Days.THURSDAY],
                            venue="Room 205",
                        )
                    ],
                )
            ],
        ),
    ]

    write_courses_to_json(sample_courses, "data/sample/sample-courses.json")
    courses = read_courses_from_json("data/sample/sample-courses.json")
    print(courses)


if __name__ == "__main__":
    test()
