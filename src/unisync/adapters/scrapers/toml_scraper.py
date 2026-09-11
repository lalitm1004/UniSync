"""Scrape course data from a TOML file."""

import tomllib
from pathlib import Path
from typing import Final

from pydantic import TypeAdapter

from unisync.models import Course
from unisync.ports import CourseScraper

TOML_COURSES_PATH: Final[Path] = Path("./data/scrape/toml/courses.toml")


class TomlScraper(CourseScraper):
    """Scrape course data from a TOML file.

    Attributes:
        path: Path to the TOML file containing a ``courses`` table.
    """

    def scrape_courses(self) -> list[Course]:
        """Parse and validate courses from the TOML file.

        Returns:
            A list of validated :class:`Course` objects.

        Raises:
            pydantic.ValidationError: If the TOML contents do not match the
                expected course models.
        """
        TOML_COURSES_PATH.parent.mkdir(parents=True, exist_ok=True)

        with TOML_COURSES_PATH.open("rb") as file:
            data = tomllib.load(file)

        return TypeAdapter(list[Course]).validate_python(data["courses"])
