"""Service type enums used for registry-based dispatch."""

from enum import StrEnum


class ScraperType(StrEnum):
    """Types of course scrapers supported by UniSync."""

    TOML = "toml"
    ERP = "erp"


class ExporterType(StrEnum):
    """Types of course exporters supported by UniSync."""

    GOOGLE_CALENDAR = "google-calendar"
