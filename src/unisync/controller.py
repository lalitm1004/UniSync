"""Application controller that orchestrates scraping and exporting."""

from collections.abc import Callable

from unisync.adapters.exporters.google.exporter import GoogleCalendarExporter
from unisync.adapters.scrapers.toml_scraper import TomlScraper
from unisync.ports import CourseExporter, CourseScraper
from unisync.registry import Registry
from unisync.types import ExporterType, ScraperType


class Controller:
    """Resolve services by type and run a single scrape-then-export cycle."""

    def __init__(self) -> None:
        self._scrapers: Registry[ScraperType, Callable[[], CourseScraper]] = Registry()
        self._exporters: Registry[ExporterType, Callable[[], CourseExporter]] = (
            Registry()
        )
        self._register_defaults()

    def _register_defaults(self) -> None:
        self._scrapers.register(ScraperType.TOML, lambda: TomlScraper())
        self._exporters.register(ExporterType.GOOGLE_CALENDAR, GoogleCalendarExporter)

    def run(self, scraper_type: ScraperType, exporter_type: ExporterType) -> None:
        """Scrape courses using ``scraper_type`` and export via ``exporter_type``."""
        scraper = self._scrapers.get(scraper_type)()
        exporter = self._exporters.get(exporter_type)()

        courses = scraper.scrape_courses()
        exporter.export_courses(courses)
