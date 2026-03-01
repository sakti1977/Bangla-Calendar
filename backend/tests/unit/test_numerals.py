"""Unit tests for Bengali numeral conversion."""
import pytest

from app.core.locale.numerals import to_bangla_numeral, to_arabic_numeral


NUMERAL_PAIRS = [
    (0, "০"),
    (1, "১"),
    (9, "৯"),
    (10, "১০"),
    (14, "১৪"),
    (31, "৩১"),
    (100, "১০০"),
    (1431, "১৪৩১"),
    (2024, "২০২৪"),
]


@pytest.mark.parametrize("arabic,bangla", NUMERAL_PAIRS)
def test_to_bangla_numeral(arabic, bangla):
    assert to_bangla_numeral(arabic) == bangla


@pytest.mark.parametrize("arabic,bangla", NUMERAL_PAIRS)
def test_to_arabic_numeral(arabic, bangla):
    assert to_arabic_numeral(bangla) == str(arabic)


def test_round_trip():
    for n in range(0, 10000, 37):
        bn = to_bangla_numeral(n)
        recovered = int(to_arabic_numeral(bn))
        assert recovered == n
