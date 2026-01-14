from __future__ import annotations

import dotenv
import os
import tomllib
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, Final, List, Optional


@dataclass(frozen=True)
class ERPCredentials:
    netid: str
    password: str

    @classmethod
    def from_env(cls) -> ERPCredentials:
        dotenv.load_dotenv()

        netid = os.getenv("SNU_NETID")
        password = os.getenv("SNU_PASSWORD")

        if not netid or not password:
            raise ValueError(
                "Missing credentials. Ensure SNU_NETID and SNU_PASSWORD are properly configured"
            )

        return cls(netid, password)


@dataclass(frozen=True)
class GoogleOAuthConfig:
    client_id: str
    client_secret: str

    @classmethod
    def from_env(cls) -> GoogleOAuthConfig:
        dotenv.load_dotenv()

        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

        if not client_id or not client_secret:
            raise ValueError(
                "Missing cresentials. Ensure GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are properly configured"
            )

        return cls(client_id=client_id, client_secret=client_secret)

    def to_client_config(self) -> Dict:
        return {
            "installed": {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost"],
            }
        }


DEFAULT_RUN_HEADLESS_BROWSER_INSTANCE: Final[bool] = True


@dataclass(frozen=True)
class AppConfig:
    DEFAULT_START_DATE: date
    DEFAULT_END_DATE: date
    TIMEZONE: str
    EXCLUDED_DATES: List[date] = field(default_factory=list)
    RUN_HEADLESS_BROWSER_INSTANCE: bool = field(
        default=DEFAULT_RUN_HEADLESS_BROWSER_INSTANCE
    )

    @classmethod
    def from_toml(cls, path: Path = Path("app_config.toml")) -> AppConfig:
        with open(path, "rb") as f:
            data = tomllib.load(f)

        if "config" not in data:
            raise ValueError("Missing [config] section in TOML file")

        config = data["config"]
        timezone = config.get("timezone")
        if timezone is None:
            raise ValueError("Missing required config value: timezone")
        if not isinstance(timezone, str):
            raise TypeError(
                f"Expected timezone to be of string type. Recieved {type(timezone)}"
            )

        return cls(
            DEFAULT_START_DATE=_parse_date(
                config.get("default_start_date"),
                "default_start_date",
            ),
            DEFAULT_END_DATE=_parse_date(
                config.get("default_end_date"),
                "default_end_date",
            ),
            TIMEZONE=timezone,
            EXCLUDED_DATES=_parse_excluded_dates(config.get("excluded_dates", [])),
            RUN_HEADLESS_BROWSER_INSTANCE=_parse_bool(
                config.get("run_headless_browser_instance"),
                "run_headless_browser_instance",
            ),
        )


def _parse_date(value: Optional[str], field_name: str) -> date:
    if not value:
        raise ValueError(f"Missing required config value: {field_name}")

    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(
            f"Invalid date format for '{field_name}'. Expected YYYY-MM-DD"
        ) from exc


def _parse_bool(value: Optional[bool], field_name: str) -> bool:
    if value is None:
        return DEFAULT_RUN_HEADLESS_BROWSER_INSTANCE

    if not isinstance(value, bool):
        raise ValueError(f"Invalid boolean value for '{field_name}'")

    return value


def _parse_excluded_dates(excluded_dates: List[str]) -> List[date]:
    result: List[date] = []

    for entry in excluded_dates:
        entry = entry.strip()

        if " - " in entry:
            parts = entry.split(" - ")
            if len(parts) != 2:
                raise ValueError(f"Invalid date range format: '{entry}'")

            try:
                start_date = date.fromisoformat(parts[0].strip())
                end_date = date.fromisoformat(parts[1].strip())
            except ValueError as exc:
                raise ValueError(
                    f"Invalid date in range '{entry}'. Expected YYYY-MM-DD"
                ) from exc

            if start_date > end_date:
                raise ValueError(
                    f"Start date must be before or equal to end date in range: '{entry}'"
                )

            current = start_date
            while current <= end_date:
                result.append(current)
                current += timedelta(days=1)
        else:
            try:
                result.append(date.fromisoformat(entry))
            except ValueError as exc:
                raise ValueError(
                    f"Invalid date format: '{entry}'. Expected YYYY-MM-DD"
                ) from exc

    return sorted(set(result))


def test() -> None:
    app_config = AppConfig.from_toml()
    print(app_config)


if __name__ == "__main__":
    test()
