"""
Panchanga computation engine.

Computes the five panchanga elements (tithi, nakshatra, yoga, karana, paksha)
along with sunrise/sunset for a given date and geographic location.
All computations use Lahiri ayanamsa (sidereal), evaluated at local sunrise.

Reference timezones:
- Bangladesh: Asia/Dhaka (UTC+6)
- West Bengal: Asia/Kolkata (UTC+5:30)
"""
from __future__ import annotations

import math
from datetime import date, datetime, timezone, timedelta

from app.core.interfaces import PanchangaResult, AstronomyProvider
from app.core.calendars.julian_day import gregorian_to_jd, jd_to_ist, jd_to_bdt
from app.core.locale.names_panchanga import (
    TITHI_NAMES_BN, TITHI_NAMES_EN,
    NAKSHATRA_NAMES_BN, NAKSHATRA_NAMES_EN,
    YOGA_NAMES_BN, YOGA_NAMES_EN,
    KARANA_NAMES_BN, KARANA_NAMES_EN,
    PAKSHA_SHUKLA_BN, PAKSHA_KRISHNA_BN,
    PAKSHA_SHUKLA_EN, PAKSHA_KRISHNA_EN,
)

# Arc-seconds per nakshatra/yoga segment
_NAKSHATRA_ARC = 360.0 / 27  # 13.333...°
_YOGA_ARC = 360.0 / 27       # 13.333...°
_TITHI_ARC = 12.0             # degrees per tithi
_KARANA_ARC = 6.0             # degrees per karana (half tithi)


def _karana_name(moon_sun_diff: float) -> tuple[str, str]:
    """Return (Bengali name, English name) for the karana at the given moon-sun diff."""
    # karana_index 0-59 maps to 60 karanas
    karana_index = int(moon_sun_diff / _KARANA_ARC) % 60

    if karana_index == 0:
        # Kimstughna: fixed, always the first half of Shukla Pratipada
        return KARANA_NAMES_BN[10], KARANA_NAMES_EN[10]
    elif 1 <= karana_index <= 56:
        # 56 repeating karanas (7 types × 8 repetitions)
        repeating_idx = (karana_index - 1) % 7
        return KARANA_NAMES_BN[repeating_idx], KARANA_NAMES_EN[repeating_idx]
    else:
        # Fixed ending karanas: Shakuni(57), Chatushpada(58), Naga(59)
        fixed_idx = karana_index - 57  # 0, 1, 2
        return KARANA_NAMES_BN[7 + fixed_idx], KARANA_NAMES_EN[7 + fixed_idx]


def _jd_to_local_time_str(jd: float, utc_offset_hours: float) -> str:
    """Format a JD as HH:MM in the given timezone."""
    # JD epoch is noon Jan 1, 4713 BC; convert to fractional day
    day_frac = (jd + 0.5 + utc_offset_hours / 24) % 1.0
    total_minutes = round(day_frac * 1440)
    h, m = divmod(total_minutes, 60)
    return f"{h:02d}:{m:02d}"


class PanchangaEngine:
    """Compute all five panchanga elements for a given date/location."""

    def __init__(self, provider: AstronomyProvider) -> None:
        self._p = provider

    def compute(
        self, d: date, lat: float, lon: float, utc_offset_hours: float = 5.5
    ) -> PanchangaResult:
        """
        Compute panchanga for date d at the given location.

        lat, lon: decimal degrees (N/E positive)
        utc_offset_hours: timezone offset (5.5 for IST, 6.0 for BDT)
        """
        # JD at local midnight = JD at UTC midnight - utc_offset_hours/24
        jd_midnight = gregorian_to_jd(d) - utc_offset_hours / 24

        # Get sunrise JD; use noon as initial search point
        jd_noon = jd_midnight + 0.5
        sunrise_jd = self._p.sunrise_jd(jd_midnight, lat, lon)
        sunset_jd = self._p.sunset_jd(jd_midnight, lat, lon)

        # Get tomorrow's sunrise for edge case detection
        tomorrow_jd_midnight = jd_midnight + 1.0
        tomorrow_sunrise_jd = self._p.sunrise_jd(tomorrow_jd_midnight, lat, lon)

        # --- Compute at today's sunrise ---
        sun_sid = self._p.solar_longitude_sidereal(sunrise_jd)
        moon_sid = self._p.lunar_longitude_sidereal(sunrise_jd)
        ayanamsa = self._p.lahiri_ayanamsa(sunrise_jd)

        moon_sun_diff = (moon_sid - sun_sid) % 360.0

        # Tithi (1-30)
        tithi_number = int(moon_sun_diff / _TITHI_ARC) + 1
        tithi_number = min(tithi_number, 30)  # clamp to 30

        # Paksha
        is_shukla = tithi_number <= 15
        paksha_bn = PAKSHA_SHUKLA_BN if is_shukla else PAKSHA_KRISHNA_BN
        paksha_en = PAKSHA_SHUKLA_EN if is_shukla else PAKSHA_KRISHNA_EN

        # Tithi name (index 0-29 → position in TITHI_NAMES arrays)
        tithi_idx = tithi_number - 1
        tithi_name_bn = TITHI_NAMES_BN[tithi_idx]
        tithi_name_en = TITHI_NAMES_EN[tithi_idx]

        # Nakshatra (1-27)
        nakshatra_number = int(moon_sid / _NAKSHATRA_ARC) + 1
        nakshatra_number = min(nakshatra_number, 27)
        nakshatra_name_bn = NAKSHATRA_NAMES_BN[nakshatra_number - 1]
        nakshatra_name_en = NAKSHATRA_NAMES_EN[nakshatra_number - 1]

        # Yoga (1-27): (moon_sid + sun_sid) mod 360 / arc
        yoga_sum = (moon_sid + sun_sid) % 360.0
        yoga_number = int(yoga_sum / _YOGA_ARC) + 1
        yoga_number = min(yoga_number, 27)
        yoga_name_bn = YOGA_NAMES_BN[yoga_number - 1]
        yoga_name_en = YOGA_NAMES_EN[yoga_number - 1]

        # Karana
        karana_name_bn, karana_name_en = _karana_name(moon_sun_diff)

        # Tithi edge cases: compare tithi at today's vs tomorrow's sunrise
        tomorrow_sun_sid = self._p.solar_longitude_sidereal(tomorrow_sunrise_jd)
        tomorrow_moon_sid = self._p.lunar_longitude_sidereal(tomorrow_sunrise_jd)
        tomorrow_diff = (tomorrow_moon_sid - tomorrow_sun_sid) % 360.0
        tomorrow_tithi = int(tomorrow_diff / _TITHI_ARC) + 1

        is_kshaya = (tomorrow_tithi == tithi_number + 2 % 30)   # tithi skipped
        is_vriddhi = (tomorrow_tithi == tithi_number)             # tithi repeated

        # Format times
        sunrise_str = _jd_to_local_time_str(sunrise_jd, utc_offset_hours)
        sunset_str = _jd_to_local_time_str(sunset_jd, utc_offset_hours)

        return PanchangaResult(
            tithi_number=tithi_number,
            tithi_name_bn=tithi_name_bn,
            tithi_name_en=tithi_name_en,
            paksha_bn=paksha_bn,
            paksha_en=paksha_en,
            nakshatra_number=nakshatra_number,
            nakshatra_name_bn=nakshatra_name_bn,
            nakshatra_name_en=nakshatra_name_en,
            yoga_number=yoga_number,
            yoga_name_bn=yoga_name_bn,
            yoga_name_en=yoga_name_en,
            karana_name_bn=karana_name_bn,
            karana_name_en=karana_name_en,
            sunrise_local=sunrise_str,
            sunset_local=sunset_str,
            moon_longitude=round(moon_sid, 4),
            sun_longitude=round(sun_sid, 4),
            ayanamsa=round(ayanamsa, 4),
            tithi_is_kshaya=is_kshaya,
            tithi_is_vriddhi=is_vriddhi,
        )

    def compute_at_jd(self, jd: float, lat: float, lon: float, utc_offset_hours: float = 5.5):
        """Compute panchanga at an arbitrary JD (for festival critical-window checks)."""
        sun_sid = self._p.solar_longitude_sidereal(jd)
        moon_sid = self._p.lunar_longitude_sidereal(jd)
        moon_sun_diff = (moon_sid - sun_sid) % 360.0
        tithi_number = int(moon_sun_diff / _TITHI_ARC) + 1
        tithi_number = min(tithi_number, 30)
        nakshatra_number = int(moon_sid / _NAKSHATRA_ARC) + 1
        return {
            "tithi": tithi_number,
            "paksha": "shukla" if tithi_number <= 15 else "krishna",
            "nakshatra": nakshatra_number,
            "moon_sun_diff": moon_sun_diff,
        }
