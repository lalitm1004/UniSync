# UniSync

Simply give it courses, it turns every weekly session into a recurring calendar
event and pushes them to the calendar service you pick. Swapping in a new
source or backend is easy.

## Why

- **Ports & adapters.** Courses live behind `CourseScraper` and
  `CourseExporter`. Scrapers and exporters are separate, swappable adapters.
- **Registry dispatch.** Pick a service with an enum (`ScraperType`,
  `ExporterType`), resolved from a typed registry. No `if/else` chains.
- **Strict models.** Courses, batches, and timings are Pydantic models with
  strict date/time types.
- **Real recurrences.** A weekly class is one event with an `RRULE` and
  `EXDATE`s for holidays, not a pile of duplicate events.
- **Review first.** Events go to a JSON file you can check before anything is
  synced.
- **Cached OAuth.** Authorize Google once; tokens refresh on their own.

## Architecture

```
src/unisync/
├── models/        # Course, CourseBatch, Timing, Day
├── ports/         # CourseScraper, CourseExporter
├── adapters/
│   ├── scrapers/  # TomlScraper (ERP soon)
│   └── exporters/ # GoogleCalendarExporter
├── registry.py    # typed service registry
├── types.py       # ScraperType / ExporterType enums
├── controller.py  # scrape -> export
└── __init__.py    # CLI entry point
```

## Requirements

- [uv](https://docs.astral.sh/uv/)

## Setup

```bash
uv sync
cp .env.example .env   # fill in the values
```

`GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` come from a Google Cloud project
with the Calendar API enabled and a "Desktop app" OAuth client.

## Configuration

Settings live in `config.toml`:

```toml
[config]
default_start_date = "2026-08-17"
default_end_date   = "2026-12-01"
excluded_dates = [
    "2026-10-02",              # single day
    "2026-10-03 - 2026-10-10", # range
]
timezone = "Asia/Kolkata"
run_headless_browser_instance = false
```

`excluded_dates` takes single dates or `start - end` ranges.

## Usage

```bash
unisync [--scraper {toml,erp}] [--exporter {google-calendar}]
```

Defaults to the `toml` scraper and `google-calendar` exporter.

### Scrapers

#### TOML (`--scraper toml`)

Reads `data/scrape/toml/courses.toml`:

```toml
[[courses]]
course_code  = "CSD361"
course_title = "Introduction to Machine Learning"
is_enrolled  = true
batches = [
    { component = "L1", start_date = 2026-08-17, end_date = 2026-12-01, timings = [
        { start_time = 08:00:00, end_time = 08:55:00, venue = "C309", days = ["MONDAY", "FRIDAY"] },
    ] },
]
```

#### ERP (`--scraper erp`)

Coming soon. Will log into the university portal and pull the weekly schedule.

### Exporters

#### Google Calendar (`--exporter google-calendar`)

Uploads events to a "UniSync" calendar.

1. Writes events to `data/export/google/review.json`.
2. Waits for you to edit the file and press Enter.
3. Uploads, with a `tqdm` progress bar.

First run opens your browser for Google auth. Token and calendar details are
cached under `data/export/google/`.

## Adding a service

1. Add an enum member in `types.py`.
2. Implement `CourseScraper` or `CourseExporter`.
3. Re-export it from the package `__init__.py`.
4. Register it in `Controller._register_defaults`.

## Roadmap

- ERP scraper (logging into the university portal).
- More calendar exporters.

## Development

```bash
uv run ruff check src/
```
