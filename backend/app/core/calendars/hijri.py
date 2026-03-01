"""
Hijri (Islamic) calendar conversion using Meeus 30-year tabular algorithm.

Provides a computed Hijri date for any Gregorian date. For Bangladesh, the
official dates for Islamic festivals may differ due to moon-sighting. The
sighting override is applied at a higher layer (see festivals/sighting_overlay.py).

References:
- Jean Meeus, "Astronomical Algorithms", Ch. 9
- Dershowitz & Reingold, "Calendrical Calculations"
"""
from __future__ import annotations

from datetime import date
from dataclasses import dataclass

from app.core.interfaces import HijriDate
from app.core.locale.names_hijri import (
    HIJRI_MONTH_NAMES_BN, HIJRI_MONTH_NAMES_EN, ERA_BN, ERA_EN
)
from app.core.locale.numerals import to_bangla_numeral


# Hijri epoch in Julian Day Number (1 Muharram 1 AH = 16 July 622 CE Julian)
_HIJRI_EPOCH_JD = 1948439.5

# 30-year cycle: which years are leap (355-day) years
_LEAP_YEARS_IN_CYCLE = frozenset({2, 5, 7, 10, 13, 15, 18, 21, 24, 26, 29})

# Month lengths: 12 months alternating 30/29, with month 12 gaining a day in leap years
_MONTH_LENGTHS = [30, 29, 30, 29, 30, 29, 30, 29, 30, 29, 30, 29]
_MONTH_LENGTHS_LEAP = [30, 29, 30, 29, 30, 29, 30, 29, 30, 29, 30, 30]


def _is_hijri_leap(year: int) -> bool:
    return (year % 30) in _LEAP_YEARS_IN_CYCLE


def _hijri_month_lengths(year: int) -> list[int]:
    return _MONTH_LENGTHS_LEAP if _is_hijri_leap(year) else _MONTH_LENGTHS


def _jd_to_hijri(jd: float) -> tuple[int, int, int]:
    """Convert Julian Day Number (midnight) to Hijri (year, month, day)."""
    day = int(round(jd - _HIJRI_EPOCH_JD))
    cycle, day_in_cycle = divmod(day, 10631)
    year = int(30 * cycle)

    # Work through 30-year cycle
    remaining = day_in_cycle
    for y in range(1, 31):
        year_days = 355 if _is_hijri_leap(y) else 354
        if remaining < year_days:
            break
        remaining -= year_days
        year += 1
    year += 1  # year is 1-indexed: completed years + 1 = current year

    # Work through months of the year
    month_lengths = _hijri_month_lengths(year)
    month = 1
    for m, ml in enumerate(month_lengths, 1):
        if remaining < ml:
            month = m
            break
        remaining -= ml

    day_of_month = int(remaining) + 1
    return year, month, day_of_month


def _hijri_to_jd(year: int, month: int, day: int) -> float:
    """Convert Hijri date to Julian Day Number."""
    cycle, year_in_cycle = divmod(year - 1, 30)
    jd = _HIJRI_EPOCH_JD + cycle * 10631

    # Add days for completed years in this 30-year cycle
    for y in range(1, year_in_cycle + 1):
        jd += 355 if _is_hijri_leap(y) else 354

    # Add days for completed months
    month_lengths = _hijri_month_lengths(year)
    for m in range(1, month):
        jd += month_lengths[m - 1]

    # Add day of month
    jd += day - 1
    return jd


def _greg_to_jd(d: date) -> float:
    """Minimal Gregorian to JD for internal use."""
    y, m, day = d.year, d.month, d.day
    if m <= 2:
        y -= 1
        m += 12
    a = y // 100
    b = 2 - a + a // 4
    return int(365.25 * (y + 4716)) + int(30.6001 * (m + 1)) + day + b - 1524.5


def greg_to_hijri(d: date) -> HijriDate:
    """Convert a Gregorian date to Hijri date (tabular computation)."""
    jd = _greg_to_jd(d)  # midnight JD
    year, month, day = _jd_to_hijri(jd)
    return HijriDate(
        year=year,
        month=month,
        day=day,
        month_name_bn=HIJRI_MONTH_NAMES_BN[month - 1],
        month_name_en=HIJRI_MONTH_NAMES_EN[month - 1],
        year_bn=to_bangla_numeral(year),
        day_bn=to_bangla_numeral(day),
        era_bn=ERA_BN,
        is_sighting_confirmed=False,
        note_bn="গণনা ভিত্তিক (চাঁদ দেখা সাপেক্ষে)",
    )


def hijri_to_greg(year: int, month: int, day: int) -> date:
    """Convert a Hijri date to Gregorian date (tabular computation)."""
    import math
    jd = _hijri_to_jd(year, month, day)
    # JD to Gregorian (Meeus algorithm)
    jd2 = jd + 0.5
    z = math.floor(jd2)
    alpha = math.floor((z - 1867216.25) / 36524.25)
    a = z + 1 + alpha - math.floor(alpha / 4)
    b = a + 1524
    c = math.floor((b - 122.1) / 365.25)
    d_val = math.floor(365.25 * c)
    e = math.floor((b - d_val) / 30.6001)
    day_g = b - d_val - math.floor(30.6001 * e)
    month_g = e - 1 if e < 14 else e - 13
    year_g = c - 4716 if month_g > 2 else c - 4715
    return date(int(year_g), int(month_g), int(day_g))


class HijriCalendarEngine:
    """Provides Hijri date computation."""

    def greg_to_hijri(self, d: date) -> HijriDate:
        return greg_to_hijri(d)

    def hijri_to_greg(self, year: int, month: int, day: int) -> date:
        return hijri_to_greg(year, month, day)
