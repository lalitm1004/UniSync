"""Port defining how courses are exported to an external service."""

from abc import ABC, abstractmethod

from unisync.models import Course


class CourseExporter(ABC):
    """Interface for adapters that export course data to a service."""

    @abstractmethod
    def export_courses(self, course_list: list[Course]) -> None:
        """Export the given courses to the underlying service.

        Args:
            course_list: The courses to export.
        """
