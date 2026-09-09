from abc import ABC, abstractmethod

from unisync.models import Course


class CourseScraper(ABC):
    @abstractmethod
    def scrape_courses(self) -> list[Course]: ...
