"""
West Bengal Sidereal Solar Calendar Engine.

Each month starts on the day the Sun enters a new zodiac sign (sankranti),
adjusted for the Bengal midnight rule:
- If sankranti occurs before 23:36 IST → month starts that civil day
- If sankranti occurs 23:36–24:00 IST → month starts the NEXT civil day

Month numbering follows the same zodiac-to-month mapping as classical:
  Mesha (0°)    → Boishakh (month 1)
  Vrishabha (30°) → Jyoishtho (month 2)
  ...

The Bangla year boundary for WB is the Mesha sankranti (Sun enters Aries).
"""
from __future__ import annotations

import math
from datetime import date, timedelta
from typing import TYPE_CHECKING

from app.core.interfaces import BanglaDate
from app.core.locale.names_wb import WB_MONTH_NAMES_BN, WB_MONTH_NAMES_EN, ERA_BN
from app.core.locale.numerals import to_bangla_numeral
from app.core.calendars.julian_day import jd_to_gregorian, gregorian_to_jd

if TYPE_CHECKING:
    from app.core.astronomy.swisseph_provider import SwissEphemerisProvider

# IST = UTC+5:30 = 5.5 hours
_IST_OFFSET_DAYS = 5.5 / 24

# Bengal midnight rule cutoff: 23:36 IST = 23.6/24 of a day
_BENGAL_CUTOFF = 23.6 / 24

# Zodiac sign → month number (0-indexed sign → 1-indexed Bangla month)
# Sign 0 (Mesha/Aries) → month 1 (Boishakh)
_SIGN_TO_MONTH = {i: (i % 12) + 1 for i in range(12)}


def _sankranti_to_wb_month_start(sankranti_jd: float) -> date:
    """
    Apply the Bengal midnight rule to determine the civil date on which
    the WB month starts, given the JD of a solar sankranti.

    Returns the Gregorian civil date (IST) on which the WB month begins.
    """
    # Convert sankranti JD to IST fractional day
    ist_frac = (sankranti_jd + 0.5 + _IST_OFFSET_DAYS) % 1.0
    civil_date = jd_to_gregorian(sankranti_jd + _IST_OFFSET_DAYS)

    if ist_frac < _BENGAL_CUTOFF:
        # Sankranti before 23:36 IST: month starts on this civil day
        return civil_date
    else:
        # Sankranti between 23:36–24:00 IST: month starts the next day
        return civil_date + timedelta(days=1)


def _bangla_year_for_mesha(mesha_greg_date: date) -> int:
    """Compute the Bangla year from the Gregorian date of Mesha sankranti."""
    # Same era offset as BD: BY = greg_year - 593 (on/after ~14 April)
    return mesha_greg_date.year - 593


class WestBengalCalendarEngine:
    """
    CalendarEngine for the West Bengal sidereal solar calendar.

    Requires an AstronomyProvider (SwissEphemerisProvider) and a
    precomputed sankranti table (year → list of 12 month-start dates).

    The sankranti table is built lazily for the requested year range.
    """

    region = "WB"

    def __init__(self, provider: "SwissEphemerisProvider") -> None:
        self._provider = provider
        # Cache: bangla_year → dict(month_number → Gregorian start date)
        self._cache: dict[int, dict[int, date]] = {}

    def _build_year(self, bangla_year: int) -> dict[int, date]:
        """Compute all 12 month-start dates for the given Bangla year."""
        if bangla_year in self._cache:
            return self._cache[bangla_year]

        # Mesha sankranti of BY falls around 14 April of Greg year BY+593
        # Search starting from 1 January of Greg year BY+593
        search_start = date(bangla_year + 593, 1, 1)
        jd_start = gregorian_to_jd(search_start)

        month_starts: dict[int, date] = {}

        # Find all 12 sankrantis (sign 0..11 = Mesha..Meena)
        for sign in range(12):
            sankranti_jd = self._provider.find_sankranti(jd_start, sign)
            month_start = _sankranti_to_wb_month_start(sankranti_jd)
            month_num = sign + 1  # Mesha → 1, Vrishabha → 2, ...
            month_starts[month_num] = month_start
            # Next sign search starts from this sankranti + 25 days
            jd_start = sankranti_jd + 25.0

        self._cache[bangla_year] = month_starts
        return month_starts

    def _month_start_greg(self, bangla_year: int, bangla_month: int) -> date:
        return self._build_year(bangla_year)[bangla_month]

    def month_length(self, bangla_year: int, bangla_month: int) -> int:
        start = self._month_start_greg(bangla_year, bangla_month)
        if bangla_month < 12:
            end = self._month_start_greg(bangla_year, bangla_month + 1)
        else:
            # Month 12: end = month 1 of next year
            next_year_starts = self._build_year(bangla_year + 1)
            end = next_year_starts[1]
        return (end - start).days

    def is_leap_year(self, bangla_year: int) -> bool:
        """WB year is a leap year if it has 366 days (month lengths sum to 366)."""
        total = sum(self.month_length(bangla_year, m) for m in range(1, 13))
        return total == 366

    def greg_to_bangla(self, d: date) -> BanglaDate:
        """Convert a Gregorian date to WB Bangla date."""
        # Determine approximate Bangla year
        guess_year = d.year - 593 if d.month >= 4 else d.year - 594

        for by in [guess_year, guess_year - 1, guess_year + 1]:
            try:
                month_starts = self._build_year(by)
            except Exception:
                continue
            # Check all months in reverse to find the containing month
            for bm in range(12, 0, -1):
                start = month_starts.get(bm)
                if start and d >= start:
                    bd = (d - start).days + 1
                    ml = self.month_length(by, bm)
                    if 1 <= bd <= ml:
                        return self._make_date(by, bm, bd)
        raise ValueError(f"Could not convert {d} to WB Bangla date")

    def bangla_to_greg(self, year: int, month: int, day: int) -> date:
        """Convert WB Bangla date to Gregorian date."""
        start = self._month_start_greg(year, month)
        ml = self.month_length(year, month)
        if not (1 <= day <= ml):
            raise ValueError(f"Invalid WB date {year}/{month}/{day}, month has {ml} days")
        return start + timedelta(days=day - 1)

    def _make_date(self, year: int, month: int, day: int) -> BanglaDate:
        return BanglaDate(
            year=year,
            month=month,
            day=day,
            month_name_bn=WB_MONTH_NAMES_BN[month - 1],
            month_name_en=WB_MONTH_NAMES_EN[month - 1],
            year_bn=to_bangla_numeral(year),
            day_bn=to_bangla_numeral(day),
            era_bn=ERA_BN,
            region="WB",
        )
