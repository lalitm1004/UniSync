from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Dict, Final, List
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

APP_CONFIG_TOML_PATH: Final[Path] = Path("app_config.toml")


@dataclass(frozen=True)
class AppConfig:
    default_start_date: date
    default_end_date: date
    default_event_color: int
    timezone: str
    excluded_dates: List[date] = field(default_factory=list)
    run_headless_browser: bool = field(default=False)

    def __post_init__(self) -> None:
        if self.default_start_date > self.default_end_date:
            raise ValueError(
                f"Start date ({self.default_start_date}) must be before or equal to "
                f"end date ({self.default_end_date})"
            )

    @classmethod
    def from_toml(cls, path: Path = APP_CONFIG_TOML_PATH) -> AppConfig:
        with open(path, "rb") as f:
            data = tomllib.load(f)

        return cls(
            default_start_date=_parse_start_date(data),
            default_end_date=_parse_end_date(data),
            default_event_color=_parse_event_color(data),
            timezone=_parse_timezone(data),
            excluded_dates=_parse_excluded_dates(data),
            run_headless_browser=_parse_headless_browser(data),
        )


def _parse_start_date(data: Dict[str, Any]) -> date:
    try:
        raw_value = data["calendar"]["defaults"]["start_date"]
    except KeyError:
        raise ValueError("Missing required config: calendar.defaults.start_date")

    if not isinstance(raw_value, str):
        raise ValueError(
            "calendar.defaults.start_date must be a string in YYYY-MM-DD format"
        )

    try:
        return date.fromisoformat(raw_value)
    except ValueError as exc:
        raise ValueError(
            f"Invalid start_date format: '{raw_value}'. Expected YYYY-MM-DD"
        ) from exc


def _parse_end_date(data: Dict[str, Any]) -> date:
    try:
        raw_value = data["calendar"]["defaults"]["end_date"]
    except KeyError:
        raise ValueError("Missing required config: calendar.defaults.end_date")

    if not isinstance(raw_value, str):
        raise ValueError(
            "calendar.defaults.end_date must be a string in YYYY-MM-DD format"
        )

    try:
        return date.fromisoformat(raw_value)
    except ValueError as exc:
        raise ValueError(
            f"Invalid end_date format: '{raw_value}'. Expected YYYY-MM-DD"
        ) from exc


def _parse_event_color(data: Dict[str, Any]) -> int:
    try:
        raw_value = data["calendar"]["defaults"]["event_color"]
    except KeyError:
        raise ValueError("Missing required config: calendar.defaults.event_color")

    if not isinstance(raw_value, int):
        raise ValueError("calendar.defaults.event_color must be an integer")

    if not 1 <= raw_value <= 11:
        raise ValueError("event_color must be between 1 and 11 inclusive")

    return raw_value


def _parse_timezone(data: Dict[str, Any]) -> str:
    try:
        raw_value = data["locale"]["timezone"]
    except KeyError:
        raise ValueError("Missing required config: locale.timezone")

    if not isinstance(raw_value, str):
        raise ValueError("locale.timezone must be a string")

    if not raw_value.strip():
        raise ValueError("locale.timezone cannot be empty")

    # validate timezone string
    try:
        ZoneInfo(raw_value)
    except ZoneInfoNotFoundError:
        raise ValueError(f"Invalid timezone: '{raw_value}'")

    return raw_value


def _parse_excluded_dates(data: Dict[str, Any]) -> List[date]:
    try:
        raw_dates = data["calendar"]["exclusions"]["excluded_dates"]
    except KeyError:
        # default to empty list
        return []

    if not isinstance(raw_dates, list):
        raise ValueError("calendar.exclusions.excluded_dates must be a list")

    result: list[date] = []

    for entry in raw_dates:
        if not isinstance(entry, str):
            raise ValueError(f"Invalid excluded_dates entry: {entry}. Must be a string")

        entry = entry.strip()

        if " - " in entry:
            # handle date ranges
            parts = entry.split(" - ")
            if len(parts) != 2:
                raise ValueError(f"Invalid date range format: '{entry}'")

            try:
                start = date.fromisoformat(parts[0].strip())
                end = date.fromisoformat(parts[1].strip())
            except ValueError as exc:
                raise ValueError(
                    f"Invalid date in range '{entry}'. Expected YYYY-MM-DD"
                ) from exc

            if start > end:
                raise ValueError(
                    f"Start date must be before or equal to end date: '{entry}'"
                )

            # expand range into individual dates
            current = start
            while current <= end:
                result.append(current)
                current += timedelta(days=1)
        else:
            # handle single date
            try:
                result.append(date.fromisoformat(entry))
            except ValueError as exc:
                raise ValueError(
                    f"Invalid date format: '{entry}'. Expected YYYY-MM-DD"
                ) from exc

    return sorted(set(result))


def _parse_headless_browser(data: Dict[str, Any]) -> bool:
    try:
        raw_value = data["execution"]["run_headless_browser"]
    except KeyError:
        # default to False
        return False

    if not isinstance(raw_value, bool):
        raise ValueError("execution.run_headless_browser must be a boolean")

    return raw_value


def main() -> None:
    try:
        config = AppConfig.from_toml()
        print("Configuration loaded successfully:")
        print(f"  Start Date: {config.default_start_date}")
        print(f"  End Date: {config.default_end_date}")
        print(f"  Event Color: {config.default_event_color}")
        print(f"  Timezone: {config.timezone}")
        print(f"  Excluded Dates: {len(config.excluded_dates)} dates")
        print(f"  Headless Browser: {config.run_headless_browser}")

        if config.excluded_dates:
            print("\n  Excluded dates:")
            for d in config.excluded_dates:
                print(f"    - {d}")
    except Exception as e:
        print(f"Error loading configuration: {e}")
        raise


if __name__ == "__main__":
    main()
