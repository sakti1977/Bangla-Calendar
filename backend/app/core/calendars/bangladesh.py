"""
Bangladesh Civil Calendar Engine (post-2019 revision).

Key properties:
- Fixed Gregorian start dates for each Bangla month
- Boishakh–Ashwin: 31 days each (6 months)
- Kartik–Magh, Chaitra: 30 days each (5 months)
- Falgun: 29 days, 30 in Gregorian leap year
- Pahela Baishakh: fixed 14 April
- Era offset: Bangla year = Greg year - 593 (on/after 14 Apr) or - 594 (before 14 Apr)
"""
from __future__ import annotations

from datetime import date, timedelta

from app.core.interfaces import BanglaDate
from app.core.locale.names_bd import (
    BD_MONTH_NAMES_BN, BD_MONTH_NAMES_EN, ERA_BN, ERA_EN
)
from app.core.locale.numerals import to_bangla_numeral
from app.core.calendars.julian_day import is_gregorian_leap


# ---------------------------------------------------------------------------
# Fixed Gregorian start dates for each Bangla month.
# Stored as (gregorian_month, gregorian_day).
# Magh (month 10) starts on Jan 15 of the *following* Gregorian year
# relative to when the Bangla year started in April.
# ---------------------------------------------------------------------------
_MONTH_GREG_STARTS = [
    (4, 14),   # 1 Boishakh
    (5, 15),   # 2 Jyoishtho
    (6, 15),   # 3 Asharh
    (7, 16),   # 4 Shraban
    (8, 16),   # 5 Bhadra
    (9, 16),   # 6 Ashwin
    (10, 17),  # 7 Kartik
    (11, 16),  # 8 Agrohayan
    (12, 16),  # 9 Poush
    (1, 15),   # 10 Magh  (next calendar year)
    (2, 14),   # 11 Falgun
    (3, 15),   # 12 Chaitra
]

# Base month lengths (Falgun handled separately)
_BASE_MONTH_LENGTHS = [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 29, 30]


def _month_start_greg(bangla_year: int, bangla_month: int) -> date:
    """Return the Gregorian date on which a given Bangla month starts."""
    gm, gd = _MONTH_GREG_STARTS[bangla_month - 1]
    # Bangla year BY starts in Gregorian year BY+593.
    # Months 1-9 (Apr–Dec) fall in BY+593.
    # Months 10-12 (Jan–Mar) fall in BY+594.
    greg_year = bangla_year + 593 if bangla_month <= 9 else bangla_year + 594
    return date(greg_year, gm, gd)


def month_length(bangla_year: int, bangla_month: int) -> int:
    """Return the number of days in the given Bangla month."""
    if bangla_month == 11:  # Falgun
        # Falgun of BY falls in Gregorian year BY+594
        return 30 if is_gregorian_leap(bangla_year + 594) else 29
    return _BASE_MONTH_LENGTHS[bangla_month - 1]


def is_leap_year(bangla_year: int) -> bool:
    """A Bangla year is a leap year iff Falgun has 30 days."""
    return month_length(bangla_year, 11) == 30


def greg_to_bd(d: date) -> BanglaDate:
    """Convert a Gregorian date to Bangladesh civil Bangla date."""
    # Determine the Bangla year the date falls in.
    # The Bangla year BY starts on 14 April of Gregorian year BY+593.
    # Try: if date >= 14 Apr of this Gregorian year → BY = Greg year - 593
    #      else → BY = Greg year - 594
    april14 = date(d.year, 4, 14)
    bangla_year = d.year - 593 if d >= april14 else d.year - 594

    # Find which Bangla month by iterating month starts
    for month in range(12, 0, -1):
        start = _month_start_greg(bangla_year, month)
        if d >= start:
            bangla_day = (d - start).days + 1
            # Sanity check: day must be within month length
            if bangla_day <= month_length(bangla_year, month):
                return _make_bangla_date(bangla_year, month, bangla_day)
            # If we overshoot (shouldn't happen with correct data), try previous month
            break

    raise ValueError(f"Could not convert {d} to Bangla date")


def bd_to_greg(bangla_year: int, bangla_month: int, bangla_day: int) -> date:
    """Convert a Bangladesh civil Bangla date to Gregorian date."""
    ml = month_length(bangla_year, bangla_month)
    if not (1 <= bangla_day <= ml):
        raise ValueError(
            f"Invalid Bangla date: {bangla_year}/{bangla_month}/{bangla_day} "
            f"(month has {ml} days)"
        )
    start = _month_start_greg(bangla_year, bangla_month)
    return start + timedelta(days=bangla_day - 1)


def _make_bangla_date(year: int, month: int, day: int) -> BanglaDate:
    return BanglaDate(
        year=year,
        month=month,
        day=day,
        month_name_bn=BD_MONTH_NAMES_BN[month - 1],
        month_name_en=BD_MONTH_NAMES_EN[month - 1],
        year_bn=to_bangla_numeral(year),
        day_bn=to_bangla_numeral(day),
        era_bn=ERA_BN,
        region="BD",
    )


class BangladeshCalendarEngine:
    """CalendarEngine implementation for the Bangladesh civil calendar."""

    region = "BD"

    def greg_to_bangla(self, d: date) -> BanglaDate:
        return greg_to_bd(d)

    def bangla_to_greg(self, year: int, month: int, day: int) -> date:
        return bd_to_greg(year, month, day)

    def month_length(self, year: int, month: int) -> int:
        return month_length(year, month)

    def is_leap_year(self, bangla_year: int) -> bool:
        return is_leap_year(bangla_year)

    def month_start_greg(self, bangla_year: int, bangla_month: int) -> date:
        """Public helper: Gregorian date of first day of a Bangla month."""
        return _month_start_greg(bangla_year, bangla_month)
