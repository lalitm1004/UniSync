"""Shared helpers for scheduling and recurrence calculations."""

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from unisync.models import CourseBatch, Day, Timing


class DayUtils:
    """Helpers for converting :class:`Day` values to and from external formats."""

    @staticmethod
    def to_rrule(day: Day) -> str:
        """Convert a :class:`Day` to its RFC 5545 two-letter code.

        Args:
            day: The day to convert.

        Returns:
            The corresponding ``BYDAY`` value (e.g. ``"MO"``).
        """
        match day:
            case Day.MONDAY:
                return "MO"
            case Day.TUESDAY:
                return "TU"
            case Day.WEDNESDAY:
                return "WE"
            case Day.THURSDAY:
                return "TH"
            case Day.FRIDAY:
                return "FR"
            case Day.SATURDAY:
                return "SA"
            case Day.SUNDAY:
                return "SU"

    @staticmethod
    def from_weekday(weekday: int) -> Day:
        """Convert a Python weekday index to a :class:`Day`.

        Args:
            weekday: Zero-based weekday index, where Monday is ``0``.

        Returns:
            The matching :class:`Day`.

        Raises:
            ValueError: If ``weekday`` is outside ``0``-``6``.
        """
        match weekday:
            case 0:
                return Day.MONDAY
            case 1:
                return Day.TUESDAY
            case 2:
                return Day.WEDNESDAY
            case 3:
                return Day.THURSDAY
            case 4:
                return Day.FRIDAY
            case 5:
                return Day.SATURDAY
            case 6:
                return Day.SUNDAY
            case _:
                raise ValueError(f"Invalid weekday: {weekday}")


class TimeUtils:
    """Helpers for computing occurrence dates and recurrence rules."""

    @staticmethod
    def find_first_occurrence(start_date: date, days: list[Day]) -> date:
        """Return the first date on or after ``start_date`` matching a day in ``days``.

        Args:
            start_date: The earliest possible date.
            days: Days of the week to match.

        Returns:
            The first matching date, or ``start_date`` if no day matches.
        """
        if not days:
            return start_date

        current = start_date
        for _ in range(7):
            if DayUtils.from_weekday(current.weekday()) in days:
                return current
            current += timedelta(days=1)

        return start_date

    @staticmethod
    def build_recurrence(
        batch: CourseBatch,
        timing: Timing,
        timezone: str,
        excluded_dates: list[date],
    ) -> list[str]:
        """Build RFC 5545 recurrence rules for a weekly class session.

        Args:
            batch: The course batch owning the session.
            timing: The session timing.
            timezone: IANA timezone for the schedule.
            excluded_dates: Dates to exclude from the recurrence.

        Returns:
            A list of RFC 5545 recurrence and exclusion rule strings.
        """
        recurrence: list[str] = []

        if timing.days:
            byday = ",".join(DayUtils.to_rrule(day) for day in timing.days)

            until_utc = datetime.combine(
                batch.end_date,
                time(23, 59, 59),
                tzinfo=ZoneInfo(timezone),
            ).astimezone(ZoneInfo("UTC"))
            until_str = until_utc.strftime("%Y%m%dT%H%M%SZ")

            rrule = f"RRULE:FREQ=WEEKLY;BYDAY={byday};UNTIL={until_str}"
            recurrence.append(rrule)

        exdates = TimeUtils.build_exdates(batch, timing, timezone, excluded_dates)
        if exdates:
            recurrence.append(exdates)

        return recurrence

    @staticmethod
    def build_exdates(
        batch: CourseBatch,
        timing: Timing,
        timezone: str,
        excluded_dates: list[date],
    ) -> str:
        """Build an RFC 5545 ``EXDATE`` rule for excluded dates in the session range.

        Args:
            batch: The course batch owning the session.
            timing: The session timing.
            timezone: IANA timezone for the schedule.
            excluded_dates: Candidate dates to exclude.

        Returns:
            The ``EXDATE`` rule string, or an empty string if none apply.
        """
        excluded_datetimes: list[str] = []

        for excluded_date in excluded_dates:
            if not (batch.start_date <= excluded_date <= batch.end_date):
                continue

            if DayUtils.from_weekday(excluded_date.weekday()) not in timing.days:
                continue

            excluded_dt_str = datetime.combine(
                excluded_date, timing.start_time
            ).strftime("%Y%m%dT%H%M%S")
            excluded_datetimes.append(excluded_dt_str)

        if not excluded_datetimes:
            return ""

        return f"EXDATE;TZID={timezone}:{','.join(excluded_datetimes)}"
