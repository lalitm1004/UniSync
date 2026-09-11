"""UniSync package entry point."""

import argparse

from unisync.controller import Controller
from unisync.types import ExporterType, ScraperType


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Synchronize course schedules with calendar services"
    )

    parser.add_argument(
        "--scraper",
        type=ScraperType,
        choices=list(ScraperType),
        help="Course source to scrape from",
    )

    parser.add_argument(
        "--exporter",
        type=ExporterType,
        choices=list(ExporterType),
        help="Calendar service to export to",
    )

    return parser.parse_args()


def main() -> None:
    """Run the unisync CLI."""
    args = _parse_args()

    controller = Controller()
    controller.run(args.scraper, args.exporter)
