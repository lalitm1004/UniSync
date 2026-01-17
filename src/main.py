import argparse
from typing import List

from parser import HTMLToCourseParser
from scraper import SNUERPScraper
from synchronizer import CalendarSynchronizer
from models.course import (
    Course,
    write_courses_to_json,
    read_courses_from_json,
    REVIEW_FILE_PATH,
)


def scrape_and_parse_courses() -> List[Course]:
    print("Scraping ERP...")
    scraper = SNUERPScraper()
    schedule_html = scraper.get_weekly_schedule_html()

    print("Parsing scraped data...")
    courses = [HTMLToCourseParser.parse_raw_html(raw) for raw in schedule_html]
    courses = [c for c in courses if c]

    return courses


def sync_to_calendar(courses: List[Course]) -> None:
    enrolled_courses = [c for c in courses if c.is_enrolled]
    print(
        f"Found {len(enrolled_courses)} enrolled course(s) out of {len(courses)} total"
    )

    if not enrolled_courses:
        print("No enrolled courses available for synchronization")
        return

    synchronizer = CalendarSynchronizer()
    synchronizer.synchronize(enrolled_courses)
    print("Course data successfully synced to Google Calendar")


def process_review_file() -> None:
    print("Review file found. Reading courses...")
    courses = read_courses_from_json(REVIEW_FILE_PATH)
    sync_to_calendar(courses)


def create_review_file() -> None:
    courses = scrape_and_parse_courses()

    print(f"Scraped {len(courses)} course(s) total")

    if not courses:
        print("No courses found. Operation aborted.")
        return

    write_courses_to_json(courses, REVIEW_FILE_PATH)
    print(f"Course data exported to: {REVIEW_FILE_PATH}")
    print("Please review the exported file and re-run the script to complete sync")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Synchronize SNU ERP courses to Google Calendar"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete the review file and force a fresh scrape from ERP",
    )
    return parser.parse_args()


def main():
    args = parse_arguments()

    try:
        if args.reset and REVIEW_FILE_PATH.exists():
            REVIEW_FILE_PATH.unlink()
            print("Reset: Review file deleted")

        if REVIEW_FILE_PATH.exists():
            process_review_file()
        else:
            create_review_file()
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise


if __name__ == "__main__":
    main()
