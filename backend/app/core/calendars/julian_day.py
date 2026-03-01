"""
Julian Day Number (JD) ↔ Gregorian calendar conversions.
Uses the standard astronomical algorithm from Meeus "Astronomical Algorithms".
"""
from datetime import date, timezone, timedelta
import math


def gregorian_to_jd(d: date) -> float:
    """Convert a Gregorian calendar date to Julian Day Number (noon UT)."""
    y, m, day = d.year, d.month, d.day
    if m <= 2:
        y -= 1
        m += 12
    a = math.floor(y / 100)
    b = 2 - a + math.floor(a / 4)
    return math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1)) + day + b - 1524.5


def jd_to_gregorian(jd: float) -> date:
    """Convert a Julian Day Number to Gregorian calendar date."""
    jd = jd + 0.5
    z = math.floor(jd)
    f = jd - z
    if z < 2299161:
        a = z
    else:
        alpha = math.floor((z - 1867216.25) / 36524.25)
        a = z + 1 + alpha - math.floor(alpha / 4)
    b = a + 1524
    c = math.floor((b - 122.1) / 365.25)
    d_val = math.floor(365.25 * c)
    e = math.floor((b - d_val) / 30.6001)

    day = b - d_val - math.floor(30.6001 * e)
    month = e - 1 if e < 14 else e - 13
    year = c - 4716 if month > 2 else c - 4715

    return date(int(year), int(month), int(day))


def date_to_jd_noon(d: date) -> float:
    """Return JD at noon on the given Gregorian date (standard astronomical reference)."""
    return gregorian_to_jd(d) + 0.5  # noon = +0.5 from midnight JD


def jd_to_ist(jd: float) -> tuple[int, int, int]:
    """Convert JD to IST (UTC+5:30) as (hour, minute, second)."""
    # IST offset = 5.5 hours = 5.5/24 days
    day_frac = (jd + 0.5 + 5.5 / 24) % 1.0
    total_seconds = round(day_frac * 86400)
    h = total_seconds // 3600
    m = (total_seconds % 3600) // 60
    s = total_seconds % 60
    return int(h), int(m), int(s)


def jd_to_bdt(jd: float) -> tuple[int, int, int]:
    """Convert JD to BDT (Bangladesh Standard Time, UTC+6) as (hour, minute, second)."""
    day_frac = (jd + 0.5 + 6.0 / 24) % 1.0
    total_seconds = round(day_frac * 86400)
    h = total_seconds // 3600
    m = (total_seconds % 3600) // 60
    s = total_seconds % 60
    return int(h), int(m), int(s)


def is_gregorian_leap(year: int) -> bool:
    """Return True if the given Gregorian year is a leap year."""
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
