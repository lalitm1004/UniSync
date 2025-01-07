import pandas as pd
from bs4 import BeautifulSoup
from dataclasses import dataclass
from io import StringIO
from typing import Dict, List

from utilities import progress_bar

@dataclass
class ScheduleEntry:
    course_code: str
    component_type: str
    start_timing: str
    end_timing: str
    venue: str

    def __str__(self) -> str:
        return f"<{self.course_code} | {self.component_type} | {self.start_timing}-{self.end_timing} | {self.venue}>"

class ScheduleParser:
    EXCLUDED_TOKENS = {"", "-", "Floor", "Block", "G.", "F.", "S.", "T.", "A", "B", "C", "D"}

    @staticmethod
    def extract_table_data(html_str: str) -> pd.DataFrame:
        soup = BeautifulSoup(html_str, "html.parser")
        table_element = soup.find("table", id="WEEKLY_SCHED_HTMLAREA")
        if not table_element:
            raise ValueError("Schedule table not found in HTML.")
        return pd.read_html(StringIO(str(table_element)))[0]

    @staticmethod
    def create_raw_schedule(table: pd.DataFrame) -> Dict[int, List[str]]:
        return {
            day: table[table.columns[day + 1]].to_list()
            for day in range(7)
        }

    @staticmethod
    def clean_schedule_entry(entry: str) -> List[str]:
        return [
            token for token in entry.split()
            if token not in ScheduleParser.EXCLUDED_TOKENS
        ]

    @staticmethod
    def is_valid_entry(entry: str) -> bool:
        return (
            entry == entry and # not NaN
            entry.count("Floor") <= 1 and
            entry.count("Block") <= 1 # elminate clash blocks
        )

    @staticmethod
    def process_venue(venue: str) -> str:
        return "TBA" if "location" in venue.lower() else venue

    @staticmethod
    def create_schedule_entry(tokens: List[str]) -> ScheduleEntry:
        return ScheduleEntry(
            course_code=tokens[1],
            component_type=tokens[2],
            start_timing=tokens[4],
            end_timing=tokens[5],
            venue=ScheduleParser.process_venue(tokens[6])
        )

    @classmethod
    def parse_schedule_html(cls, html_str: str) -> Dict[int, List[ScheduleEntry]]:
        table = cls.extract_table_data(html_str)
        raw_schedule = cls.create_raw_schedule(table)

        formatted_schedule = {}
        for day in range(7):
            valid_entries = {
                entry for entry in raw_schedule[day]
                if cls.is_valid_entry(entry)
            }

            day_schedule = []
            for entry in valid_entries:
                tokens = cls.clean_schedule_entry(entry)
                if len(tokens) >= 7: # ensure we have enoug tokens
                    schedule_entry = cls.create_schedule_entry(tokens)
                    day_schedule.append(schedule_entry)

            formatted_schedule[day] = day_schedule
            progress_bar("Formatting Schedule", day + 1, 7)

        return formatted_schedule

def main():
    """test the parser."""
    from scraper import SNUERPScraper

    scraper = SNUERPScraper(headless=False)
    html_str = scraper.get_weekly_schedule_html()
    parsed_schedule = ScheduleParser.parse_schedule_html(html_str)

    # Print schedule for each day
    for day, entries in parsed_schedule.items():
        print(f"\nday > {day}:")
        for entry in entries:
            print(f"  {entry}")

if __name__ == "__main__":
    main()