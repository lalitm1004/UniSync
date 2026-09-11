"""Ports defining the interfaces between the domain and adapters."""

from unisync.ports.scraper import CourseScraper
from unisync.ports.exporter import CourseExporter

__all__ = ["CourseScraper", "CourseExporter"]
