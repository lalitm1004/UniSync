from abc import ABC, abstractmethod

from unisync.models import Course


class CourseExporter(ABC):
    @abstractmethod
    def export_courses(self, course_list: list[Course]) -> None: ...
