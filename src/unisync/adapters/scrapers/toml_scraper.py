"""Scrape course data from a TOML file."""

import tomllib
from pathlib import Path

from pydantic import TypeAdapter

from unisync.models import Course
from unisync.ports import CourseScraper


class TomlScraper(CourseScraper):
    """Scrape course data from a TOML file.

    Attributes:
        path: Path to the TOML file containing a ``courses`` table.
    """

    def __init__(self, path: Path) -> None:
        """Initialize the scraper with the source file path.

        Args:
            path: Path to the TOML file to read from.
        """
        self.path = path

    def scrape_courses(self) -> list[Course]:
        """Parse and validate courses from the TOML file.

        Returns:
            A list of validated :class:`Course` objects.

        Raises:
            pydantic.ValidationError: If the TOML contents do not match the
                expected course models.
        """
        with self.path.open("rb") as file:
            data = tomllib.load(file)

        return TypeAdapter(list[Course]).validate_python(data["courses"])
