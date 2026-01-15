from colorama import Fore, Style, init
from typing import List

from models.course import Course, CourseBatch, ComponentType, Timing, Day

init(autoreset=True)


def log_info(message: str) -> None:
    print(f"{Fore.CYAN}INFO: {message}{Style.RESET_ALL}")


def log_success(message: str) -> None:
    print(f"{Fore.GREEN}SUCCESS: {message}{Style.RESET_ALL}")


def log_warning(message: str) -> None:
    print(f"{Fore.YELLOW}WARNING: {message}{Style.RESET_ALL}")


def log_error(message: str) -> None:
    print(f"{Fore.RED}ERROR: {message}{Style.RESET_ALL}")


def log_action(message: str) -> None:
    print(f"{Fore.MAGENTA}ACTION REQUIRED: {message}{Style.RESET_ALL}")


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
                    start_date="2026-01-12",
                    end_date="2026-04-28",
                    timings=[
                        Timing(
                            start_time="08:00",
                            end_time="08:55",
                            days=[Day.MONDAY, Day.WEDNESDAY],
                            venue="D217",
                        ),
                        Timing(
                            start_time="12:00",
                            end_time="13:55",
                            days=[Day.FRIDAY],
                            venue="D217",
                        ),
                    ],
                ),
                CourseBatch(
                    event_color=11,
                    component=(ComponentType.P, 2),
                    start_date="2026-01-12",
                    end_date="2026-04-28",
                    timings=[
                        Timing(
                            start_time="12:10",
                            end_time="14:05",
                            days=[Day.TUESDAY],
                            venue="C317",
                        ),
                    ],
                ),
            ],
        )
    ]
