import tomllib
from pathlib import Path

from pydantic import TypeAdapter

from unisync.models import Course
from unisync.ports import CourseScraper


class TomlScraper(CourseScraper):
    def __init__(self, path: Path) -> None:
        self.path = path

    def scrape_courses(self) -> list[Course]:
        with self.path.open("rb") as file:
            data = tomllib.load(file)

        return TypeAdapter(list[Course]).validate_python(data["courses"])
