from scraper import SNUERPScraper
from parser import ScheduleParser
from synchronizer import CalendarSynchronizer


def main() -> None:
    try:
        target_next_week = input("Push events to next week? [y/n] > ").lower() == "y"

        scraper = SNUERPScraper(headless=True)
        html_str = scraper.get_weekly_schedule_html()
        schedule = ScheduleParser.parse_schedule_html(html_str)

        calendar_synchronizer = CalendarSynchronizer()
        calendar_synchronizer.synchronize_schedule(schedule, target_next_week)
        print("Successful")
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
