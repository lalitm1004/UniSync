"""Port defining how course data is retrieved from external sources."""

from abc import ABC, abstractmethod

from unisync.models import Course


class CourseScraper(ABC):
    """Interface for adapters that fetch course data from a source."""

    @abstractmethod
    def scrape_courses(self) -> list[Course]:
        """Scrape all courses from the underlying source.

        Returns:
            The list of courses retrieved from the source.
        """
