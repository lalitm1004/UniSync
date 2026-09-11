"""Application configuration.

Loads runtime settings from a TOML file and sensitive credentials from
environment variables.
"""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Final

import dotenv


@dataclass(frozen=True)
class ERPCredentials:
    """Credentials for authenticating with the SNU ERP.

    Attributes:
        netid: The student's network ID.
        password: The student's ERP password.
    """

    netid: str
    password: str

    @classmethod
    def from_env(cls) -> ERPCredentials:
        """Load ERP credentials from environment variables.

        Returns:
            The parsed credentials.

        Raises:
            ValueError: If either required environment variable is missing.
        """
        dotenv.load_dotenv()

        netid = os.getenv("SNU_NETID")
        password = os.getenv("SNU_PASSWORD")

        if not netid or not password:
            raise ValueError("Missing SNU Credentials")

        return cls(netid, password)


@dataclass(frozen=True)
class GoogleOAuthConfig:
    """Google OAuth client credentials.

    Attributes:
        client_id: The OAuth client ID.
        client_secret: The OAuth client secret.
    """

    client_id: str
    client_secret: str

    @classmethod
    def from_env(cls) -> GoogleOAuthConfig:
        """Load Google OAuth credentials from environment variables.

        Returns:
            The parsed credentials.

        Raises:
            ValueError: If either required environment variable is missing.
        """
        dotenv.load_dotenv()

        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

        if not client_id or not client_secret:
            raise ValueError("Missing Google credentials")

        return cls(client_id=client_id, client_secret=client_secret)

    def to_client_config(self) -> dict[str, Any]:
        """Serialize credentials into a Google OAuth client configuration.

        Returns:
            A dict suitable for ``InstalledAppFlow.from_client_config``.
        """
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
    """Runtime configuration for the application.

    Attributes:
        DEFAULT_START_DATE: Fallback start date for a semester.
        DEFAULT_END_DATE: Fallback end date for a semester.
        TIMEZONE: IANA timezone used for scheduling.
        EXCLUDED_DATES: Dates excluded from generated schedules.
        RUN_HEADLESS_BROWSER_INSTANCE: Whether the browser should run headless.
    """

    DEFAULT_START_DATE: date
    DEFAULT_END_DATE: date
    TIMEZONE: str
    EXCLUDED_DATES: list[date] = field(default_factory=list[date])
    RUN_HEADLESS_BROWSER_INSTANCE: bool = field(
        default=DEFAULT_RUN_HEADLESS_BROWSER_INSTANCE
    )

    @classmethod
    def from_toml(cls, path: Path = Path("config.toml")) -> AppConfig:
        """Load configuration from a TOML file.

        Args:
            path: Path to the TOML configuration file.

        Returns:
            The parsed configuration.

        Raises:
            ValueError: If a required value is missing or invalid.
            TypeError: If a value has an unexpected type.
        """
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


def _parse_date(value: Any, field_name: str) -> date:
    """Parse a ``YYYY-MM-DD`` string into a :class:`date`.

    Args:
        value: The raw configuration value.
        field_name: Name of the field, used in error messages.

    Returns:
        The parsed date.

    Raises:
        ValueError: If the value is missing or not a valid ISO date.
    """
    if not value:
        raise ValueError(f"Missing required config value: {field_name}")

    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(
            f"Invalid date format for '{field_name}'. Expected YYYY-MM-DD"
        ) from exc


def _parse_bool(value: Any, field_name: str) -> bool:
    """Parse an optional boolean configuration value.

    Args:
        value: The raw configuration value.
        field_name: Name of the field, used in error messages.

    Returns:
        The parsed boolean, falling back to the default when ``value`` is None.

    Raises:
        ValueError: If the value is not a boolean.
    """
    if value is None:
        return DEFAULT_RUN_HEADLESS_BROWSER_INSTANCE

    if not isinstance(value, bool):
        raise ValueError(f"Invalid boolean value for '{field_name}'")

    return value


def _parse_excluded_dates(excluded_dates: list[str]) -> list[date]:
    """Parse excluded date entries, expanding ranges into individual dates.

    Args:
        excluded_dates: Raw string entries, each either a single ``YYYY-MM-DD``
            date or a ``YYYY-MM-DD - YYYY-MM-DD`` range.

    Returns:
        A sorted, deduplicated list of excluded dates.

    Raises:
        ValueError: If any entry is malformed.
    """
    result: list[date] = []

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
