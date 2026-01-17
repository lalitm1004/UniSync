import re
from bs4 import BeautifulSoup, Tag
from datetime import date
from typing import Dict, Final, List, Optional, Tuple, Union

from config.app_config import AppConfig
from models.course import Course, CourseBatch, Timing, ComponentType, Day

HEADER_RE = re.compile(r"([A-Z]{3}\d{3,4})\s*-\s*(.+)")
COMPONENT_RE = re.compile(r"\b([LTP])(\d+)\b")
TIME_RE = re.compile(
    r"(?P<days>(?:Mo|Tu|We|Th|Fr|Sa|Su)+)\s+"
    r"(?P<start>\d{1,2}:\d{2}[AP]M)\s*-\s*"
    r"(?P<end>\d{1,2}:\d{2}[AP]M)"
)
DAY_TOKEN_RE = re.compile(r"Mo|Tu|We|Th|Fr|Sa|Su")
DATES_RE = re.compile(r"(\d{2})/(\d{2})/(\d{4})\s*-\s*(\d{2})/(\d{2})/(\d{4})")

DAY_MAP: Final[Dict[str, Day]] = {
    "Mo": Day.MONDAY,
    "Tu": Day.TUESDAY,
    "We": Day.WEDNESDAY,
    "Th": Day.THURSDAY,
    "Fr": Day.FRIDAY,
    "Sa": Day.SATURDAY,
    "Su": Day.SUNDAY,
}

APP_CONFIG = AppConfig.from_toml()


class HTMLToCourseParser:
    @staticmethod
    def parse_raw_html(raw_html: str) -> Optional[Course]:
        soup = BeautifulSoup(raw_html, "html.parser")

        parsed_header = HTMLToCourseParser._parse_header(soup)
        if parsed_header is None:
            return None
        course_code, course_title = parsed_header

        parsed_status = HTMLToCourseParser._parse_status(soup)
        if parsed_status is None:
            return None
        is_enrolled = parsed_status

        course_batches = HTMLToCourseParser._parse_all_batches(soup)

        return Course(
            course_code=course_code,
            course_title=course_title,
            is_enrolled=is_enrolled,
            batches=course_batches,
        )

    @staticmethod
    def _parse_header(soup: BeautifulSoup) -> Optional[Tuple[str, str]]:
        header_td = soup.select_one("td.PAGROUPDIVIDER")
        if header_td is None:
            return None

        raw_text = header_td.get_text(strip=True)
        match_ = HEADER_RE.search(raw_text)
        if match_ is None:
            return None

        course_code = match_.group(1)
        course_title = match_.group(2)

        return course_code, course_title

    @staticmethod
    def _parse_status(soup: BeautifulSoup) -> Optional[bool]:
        status_span = soup.select_one('span[id^="STATUS$"]')
        if status_span is None:
            return None
        is_enrolled = status_span.get_text(strip=True).lower() == "enrolled"
        return is_enrolled

    @staticmethod
    def _parse_all_batches(soup: BeautifulSoup) -> List[CourseBatch]:
        result: List[CourseBatch] = []

        batch_trs = soup.select('tr[id^="trCLASS_MTG_VW"]')
        for batch_tr in batch_trs:
            parsed_batch = HTMLToCourseParser._parse_batch_tr(batch_tr)
            if parsed_batch is not None:
                result.append(parsed_batch)

        return result

    @staticmethod
    def _parse_batch_tr(batch_tr: Tag) -> Optional[CourseBatch]:
        component = HTMLToCourseParser._parse_component(batch_tr)
        if component is None:
            return None

        timings = HTMLToCourseParser._parse_timings(batch_tr)

        dates = HTMLToCourseParser._parse_dates(batch_tr)
        if not dates:
            start_date = APP_CONFIG.DEFAULT_START_DATE.isoformat()
            end_date = APP_CONFIG.DEFAULT_END_DATE.isoformat()
        else:
            start_date, end_date = dates[0].isoformat(), dates[1].isoformat()

        return CourseBatch(
            component=component,
            timings=timings,
            start_date=start_date,
            end_date=end_date,
        )

    @staticmethod
    def _parse_component(
        batch_tr: Tag,
    ) -> Optional[Union[Tuple[ComponentType, int], str]]:
        component_a = batch_tr.select_one('a[id^="MTG_SECTION$"]')
        if not component_a:
            return None

        raw_text = component_a.get_text(strip=True).upper()
        match_ = COMPONENT_RE.search(raw_text)
        if not match_:
            return raw_text

        code, number = match_.groups()
        return ComponentType[code], int(number)

    @staticmethod
    def _parse_timings(batch_tr: Tag) -> List[Timing]:
        timings: List[Timing] = []

        timing_span = batch_tr.select_one('span[id^="MTG_SCHED$"]')
        if timing_span is None:
            return timings

        venue_span = batch_tr.select_one('span[id^="MTG_LOC$"]')

        timing_lines = timing_span.get_text(strip=True).splitlines()

        venue_text = venue_span.get_text(strip=True) if venue_span else "TBA"
        if venue_text == "TBA":
            venue_lines = ["TBA"] * len(timing_lines)
        else:
            venue_lines = venue_text.splitlines()

        for timing_line, venue in zip(timing_lines, venue_lines):
            match_ = TIME_RE.search(timing_line)
            if not match_:
                continue

            days_block = match_.group("days")
            start_time = to_24h(match_.group("start"))
            end_time = to_24h(match_.group("end"))

            day_tokens = DAY_TOKEN_RE.findall(days_block)
            days = [DAY_MAP[token] for token in day_tokens]

            try:
                timings.append(
                    Timing(
                        start_time=start_time,
                        end_time=end_time,
                        days=days,
                        venue=venue,
                    )
                )
            except Exception:
                pass

        return timings

    @staticmethod
    def _parse_dates(batch_tr: Tag) -> Optional[Tuple[date, date]]:
        dates_span = batch_tr.select_one('span[id^="MTG_DATES$"]')
        if not dates_span:
            return None

        try:
            raw_text = dates_span.get_text(strip=True)

            match_ = DATES_RE.fullmatch(raw_text)

            if not match_:
                return None

            start_day, start_month, start_year, end_day, end_month, end_year = map(
                int, match_.groups()
            )

            start_date = date(start_year, start_month, start_day)
            end_date = date(end_year, end_month, end_day)

            return start_date, end_date
        except Exception:
            return None


def to_24h(t: str) -> str:
    hour, minute = map(int, t[:-2].split(":"))
    meridiem = t[-2:]

    if meridiem == "PM" and hour != 12:
        hour += 12
    if meridiem == "AM" and hour == 12:
        hour = 0

    return f"{hour:02d}:{minute:02d}"


def test() -> None:
    from pathlib import Path

    SAMPLE_SCHED_PATH = Path("data/sample/sample-weekly-sched.html")
    if not SAMPLE_SCHED_PATH.exists():
        raise FileNotFoundError(SAMPLE_SCHED_PATH)

    raw_html = SAMPLE_SCHED_PATH.read_text(encoding="utf-8")
    soup = BeautifulSoup(raw_html, "html.parser")

    body = soup.body
    if body is None:
        raise ValueError("No <body> tag found in HTML")

    divs = body.find_all("div", recursive=False)

    raw_div_html_list = [str(div) for div in divs]

    for i, raw_div_html in enumerate(raw_div_html_list, start=1):
        course = HTMLToCourseParser.parse_raw_html(raw_div_html)

        print(f"----- Course #{i} -----")
        if course is None:
            print("No course parsed")
        else:
            print(course.pretty_str())
        print()


if __name__ == "__main__":
    test()
