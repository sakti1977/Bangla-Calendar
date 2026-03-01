"""Bengali numeral conversion utilities."""
from __future__ import annotations

_BANGLA_DIGITS = "০১২৩৪৫৬৭৮৯"


def to_bangla_numeral(n) -> str:
    """Convert an integer (or digit string) to Bengali numeral string."""
    return "".join(_BANGLA_DIGITS[int(ch)] if ch.isdigit() else ch for ch in str(n))


def to_arabic_numeral(s: str) -> str:
    """Convert a Bengali numeral string back to Arabic digits."""
    result = []
    for ch in s:
        idx = _BANGLA_DIGITS.find(ch)
        result.append(str(idx) if idx != -1 else ch)
    return "".join(result)
