"""
Unit tests for the Bangladesh civil calendar engine.

Ground-truth date pairs validated against official GOB calendar and
the research report's algorithmic specifications.
"""
import pytest
from datetime import date

from app.core.calendars.bangladesh import (
    greg_to_bd, bd_to_greg, month_length, is_leap_year, BangladeshCalendarEngine,
)
from app.core.calendars.julian_day import is_gregorian_leap


# ---------------------------------------------------------------------------
# Known ground-truth pairs: (gregorian_date, (bangla_year, bangla_month, bangla_day))
# ---------------------------------------------------------------------------
KNOWN_DATES = [
    # Pahela Baishakh — the most critical anchor point
    (date(2024, 4, 14), (1431, 1, 1)),
    (date(2023, 4, 14), (1430, 1, 1)),
    (date(2025, 4, 14), (1432, 1, 1)),

    # Validation case from research report: 2019-10-16 → 31 Ashwin
    # Under post-2019 reform, month 6 (Ashwin) has 31 days
    (date(2019, 10, 16), (1426, 6, 31)),
    (date(2019, 10, 17), (1426, 7, 1)),   # 1 Kartik

    # Falgun leap year: 2024 is a Gregorian leap year, Falgun 1430 has 30 days
    (date(2024, 2, 14), (1430, 11, 1)),   # 1 Falgun 1430
    (date(2024, 2, 29), (1430, 11, 16)),  # 16 Falgun (leap year day)
    (date(2024, 3, 14), (1430, 11, 30)),  # Last day of Falgun (30 days)

    # Falgun non-leap: 2025 is NOT a leap year, Falgun 1431 has 29 days
    (date(2025, 2, 14), (1431, 11, 1)),   # 1 Falgun 1431
    (date(2025, 3, 14), (1431, 11, 29)),  # Last day (29 days)
    (date(2025, 3, 15), (1431, 12, 1)),   # 1 Chaitra

    # Year boundary: Dec 31
    (date(2024, 12, 31), (1431, 9, 16)),  # 16 Poush

    # January (months 10/11 of previous Bangla year)
    (date(2024, 1, 1),  (1430, 9, 17)),   # Poush
    (date(2024, 1, 15), (1430, 10, 1)),   # 1 Magh 1430

    # Boishakh–Ashwin have 31 days
    (date(2024, 5, 14), (1431, 1, 31)),   # Last day of Boishakh
    (date(2024, 5, 15), (1431, 2, 1)),    # 1 Jyoishtho

    # Kartik has 30 days (starts Oct 17, so day 30 = Nov 15)
    (date(2024, 11, 15), (1431, 7, 30)),  # last day of Kartik
    (date(2024, 11, 16), (1431, 8, 1)),   # 1 Agrohayan
    (date(2024, 11, 17), (1431, 8, 2)),   # 2 Agrohayan
]


@pytest.mark.parametrize("greg_date,expected_bd", KNOWN_DATES)
def test_greg_to_bd_known_dates(greg_date, expected_bd):
    """Verify known Gregorian→Bangla conversions."""
    result = greg_to_bd(greg_date)
    assert (result.year, result.month, result.day) == expected_bd, (
        f"greg_to_bd({greg_date}) = ({result.year},{result.month},{result.day}) "
        f"expected {expected_bd}"
    )


@pytest.mark.parametrize("greg_date,expected_bd", KNOWN_DATES)
def test_bd_to_greg_round_trip(greg_date, expected_bd):
    """bd_to_greg(greg_to_bd(d)) == d for all known dates."""
    by, bm, bd = expected_bd
    recovered = bd_to_greg(by, bm, bd)
    assert recovered == greg_date, f"Round-trip failed: bd_to_greg{expected_bd} = {recovered}, expected {greg_date}"


def test_falgun_length_leap_years():
    """Falgun length depends on the Gregorian year in which it falls (BY+594)."""
    # 2024 is a Gregorian leap year: Falgun 1430 is in Greg year 1430+594=2024 → 30 days
    assert month_length(1430, 11) == 30
    # 2025 is NOT a leap year: Falgun 1431 is in Greg year 1431+594=2025 → 29 days
    assert month_length(1431, 11) == 29
    # 2028 IS a leap year: Falgun 1434
    assert is_gregorian_leap(1434 + 594)  # 2028
    assert month_length(1434, 11) == 30
    # 1900 is NOT a leap year (div by 100 but not 400): Falgun 1306 (1306+594=1900)
    assert not is_gregorian_leap(1306 + 594)
    assert month_length(1306, 11) == 29
    # 2000 IS a leap year (div by 400): Falgun 1406 (1406+594=2000)
    assert is_gregorian_leap(1406 + 594)
    assert month_length(1406, 11) == 30


def test_month_lengths_sum_to_year():
    """Sum of all month lengths in a Bangla year must be 365 or 366."""
    for by in range(1425, 1435):
        total = sum(month_length(by, m) for m in range(1, 13))
        assert total in (365, 366), f"Bangla year {by} has {total} days"


def test_month_lengths_post_2019():
    """Verify fixed month lengths per post-2019 reform."""
    # Test a non-leap year
    by = 1431  # non-leap (2025 not a leap year)
    expected = [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 29, 30]
    for m in range(1, 13):
        assert month_length(by, m) == expected[m - 1], (
            f"Month {m} of BY {by}: got {month_length(by, m)}, expected {expected[m - 1]}"
        )


def test_invalid_day_raises():
    """bd_to_greg with invalid day should raise ValueError."""
    with pytest.raises(ValueError):
        bd_to_greg(1431, 11, 30)  # Falgun 1431 has only 29 days

    with pytest.raises(ValueError):
        bd_to_greg(1431, 1, 32)   # Month 1 has 31 days max

    with pytest.raises(ValueError):
        bd_to_greg(1431, 7, 31)   # Kartik has 30 days


def test_engine_interface():
    """BangladeshCalendarEngine implements CalendarEngine protocol."""
    engine = BangladeshCalendarEngine()
    d = date(2024, 4, 14)
    bd = engine.greg_to_bangla(d)
    assert bd.year == 1431
    assert bd.month == 1
    assert bd.day == 1
    assert bd.month_name_bn == "বৈশাখ"
    assert bd.region == "BD"
    assert engine.is_leap_year(1430) is True   # Falgun 1430 → 2024 leap
    assert engine.is_leap_year(1431) is False  # Falgun 1431 → 2025 not leap


def test_bangla_numeral_in_date():
    """BanglaDate should have Bengali numeral representations."""
    bd = greg_to_bd(date(2024, 4, 14))
    assert bd.year_bn == "১৪৩১"
    assert bd.day_bn == "১"
    assert bd.era_bn == "বঙ্গাব্দ"


def test_continuous_gregorian_sequence():
    """Ensure that consecutive Gregorian days map to consecutive Bangla days."""
    d = date(2024, 1, 1)
    prev_bd = greg_to_bd(d)

    for offset in range(1, 400):
        next_d = d + __import__('datetime').timedelta(days=offset)
        curr_bd = greg_to_bd(next_d)
        # Either same day + 1, or first day of next month, or 1st of Boishakh
        total_prev = prev_bd.year * 10000 + prev_bd.month * 100 + prev_bd.day
        total_curr = curr_bd.year * 10000 + curr_bd.month * 100 + curr_bd.day
        assert total_curr > total_prev, (
            f"Non-monotonic: {next_d} → {curr_bd.year}/{curr_bd.month}/{curr_bd.day} "
            f"after {d + __import__('datetime').timedelta(days=offset-1)} "
            f"→ {prev_bd.year}/{prev_bd.month}/{prev_bd.day}"
        )
        prev_bd = curr_bd
