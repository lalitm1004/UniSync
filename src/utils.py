from datetime import date, time
from typing import cast, List
from models.course import Course, CourseBatch, ComponentType, Timing, Day


def get_sample_course_list() -> List[Course]:
    return [
        Course(
            course_code="CSD366",
            course_title="Reinforcement Learning",
            is_enrolled=True,
            batches=[
                CourseBatch(
                    event_color=3,
                    component=(ComponentType.L, 1),
                    start_date=date(2026, 1, 12),
                    end_date=date(2026, 4, 28),
                    timings=[
                        Timing(
                            start_time=cast(time, "08:00"),
                            end_time=cast(time, "08:55"),
                            days=[Day.MONDAY, Day.WEDNESDAY],
                            venue="D217",
                        ),
                        Timing(
                            start_time=cast(time, "12:00"),
                            end_time=cast(time, "13:55"),
                            days=[Day.FRIDAY],
                            venue="D217",
                        ),
                    ],
                ),
                CourseBatch(
                    event_color=11,
                    component=(ComponentType.P, 2),
                    start_date=date(2026, 1, 12),
                    end_date=date(2026, 4, 28),
                    timings=[
                        Timing(
                            start_time=cast(time, "12:10"),
                            end_time=cast(time, "14:05"),
                            days=[Day.TUESDAY],
                            venue="C317",
                        ),
                    ],
                ),
            ],
        )
    ]
