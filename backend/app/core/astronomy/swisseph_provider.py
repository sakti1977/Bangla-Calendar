"""
Swiss Ephemeris astronomy provider.

Wraps pyswisseph (https://github.com/astrorigin/pyswisseph) to provide:
- Tropical and sidereal solar/lunar longitudes
- Lahiri ayanamsa
- Sunrise and sunset times

The Swiss Ephemeris binary data files (.se1) must be placed in the EPHEMERIS_PATH
directory (configured via Settings.ephemeris_path). Download from:
https://www.astro.com/ftp/swisseph/ephe/
Required files: seas_18.se1, sepl_18.se1, semo_18.se1

pyswisseph is AGPL-licensed; comply with license terms for distribution.
"""
from __future__ import annotations

import math
from functools import lru_cache
from pathlib import Path

try:
    import swisseph as swe
    _SWE_AVAILABLE = True
except ImportError:
    _SWE_AVAILABLE = False
    swe = None  # type: ignore

from app.config import settings


def _init_swe() -> None:
    """Initialize Swiss Ephemeris with data path and Lahiri ayanamsa."""
    if not _SWE_AVAILABLE:
        raise RuntimeError(
            "pyswisseph not installed. Install it with: pip install pyswisseph"
        )
    ephe_path = str(Path(settings.ephemeris_path).resolve())
    swe.set_ephe_path(ephe_path)
    swe.set_sid_mode(swe.SIDM_LAHIRI)


class SwissEphemerisProvider:
    """
    Primary astronomy provider using Swiss Ephemeris.
    All longitudes are in degrees (0–360).
    JD = Julian Day Number (float, standard astronomical convention).
    """

    def __init__(self) -> None:
        _init_swe()

    def solar_longitude_tropical(self, jd: float) -> float:
        """Tropical (ecliptic) longitude of the Sun in degrees."""
        result = swe.calc_ut(jd, swe.SUN, swe.FLG_SPEED)
        return result[0][0] % 360

    def lunar_longitude_tropical(self, jd: float) -> float:
        """Tropical (ecliptic) longitude of the Moon in degrees."""
        result = swe.calc_ut(jd, swe.MOON, swe.FLG_SPEED)
        return result[0][0] % 360

    def solar_longitude_sidereal(self, jd: float) -> float:
        """Sidereal (Lahiri) longitude of the Sun in degrees."""
        result = swe.calc_ut(jd, swe.SUN, swe.FLG_SIDEREAL | swe.FLG_SPEED)
        return result[0][0] % 360

    def lunar_longitude_sidereal(self, jd: float) -> float:
        """Sidereal (Lahiri) longitude of the Moon in degrees."""
        result = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL | swe.FLG_SPEED)
        return result[0][0] % 360

    def lahiri_ayanamsa(self, jd: float) -> float:
        """Lahiri (Chitrapaksha) ayanamsa in degrees for the given JD."""
        return swe.get_ayanamsa_ut(jd)

    def sunrise_jd(self, jd_date: float, lat: float, lon: float) -> float:
        """
        Julian Day Number of sunrise for the given date/location.
        jd_date: JD at local midnight (start of civil day).
        lat, lon: geographic coordinates in decimal degrees (N positive, E positive).
        """
        # swe.rise_trans returns (return_code, (event_jd, ...))
        result = swe.rise_trans(
            jd_date, swe.SUN, b'', swe.CALC_RISE,
            [lon, lat, 0.0],  # geopos: [lon, lat, alt]
            0.0,  # atpress (standard atmosphere)
            0.0,  # attemp
        )
        # result[0] = error code (0=OK), result[1] = array of event times
        if result[0] != 0:
            raise RuntimeError(f"swe.rise_trans returned error code {result[0]} for sunrise")
        return result[1][0]

    def sunset_jd(self, jd_date: float, lat: float, lon: float) -> float:
        """Julian Day Number of sunset for the given date/location."""
        result = swe.rise_trans(
            jd_date, swe.SUN, b'', swe.CALC_SET,
            [lon, lat, 0.0],
            0.0, 0.0,
        )
        if result[0] != 0:
            raise RuntimeError(f"swe.rise_trans returned error code {result[0]} for sunset")
        return result[1][0]

    def find_sankranti(self, jd_start: float, sign_number: int) -> float:
        """
        Find the JD when the sidereal solar longitude first crosses
        sign_number * 30 degrees after jd_start (within 40 days).

        sign_number: 0=Mesha(Aries), 1=Vrishabha(Taurus), ..., 11=Meena(Pisces)
        Returns the JD of the exact crossing moment.
        """
        target = (sign_number * 30.0) % 360

        def solar_sid_lon(jd: float) -> float:
            return self.solar_longitude_sidereal(jd)

        # Check that we actually cross this boundary within 40 days
        lo, hi = jd_start, jd_start + 40.0

        # Find the crossing using bisection
        # We want lon at lo < target <= lon at hi (mod 360, handling wrap)
        lon_lo = solar_sid_lon(lo)
        lon_hi = solar_sid_lon(hi)

        # Handle wrap-around at 0/360
        def signed_diff(lon_from: float, target_lon: float) -> float:
            """Positive if target_lon is ahead (east) of lon_from."""
            diff = (target_lon - lon_from) % 360
            return diff if diff < 180 else diff - 360

        if signed_diff(lon_lo, target) < 0 or signed_diff(lon_hi, target) > 0:
            # Boundary not in this window — search more carefully
            # Try expanding search
            for offset in range(0, 366, 30):
                test_lo = jd_start + offset
                test_hi = test_lo + 35
                if signed_diff(solar_sid_lon(test_lo), target) >= 0 and \
                   signed_diff(solar_sid_lon(test_hi), target) <= 0:
                    lo, hi = test_lo, test_hi
                    break
            else:
                raise RuntimeError(
                    f"Sankranti for sign {sign_number} not found within 1 year of JD {jd_start}"
                )

        # Bisection to ~1-second precision (1 second ≈ 1/86400 days)
        for _ in range(60):
            mid = (lo + hi) / 2
            lon_mid = solar_sid_lon(mid)
            if signed_diff(lon_mid, target) < 0:
                lo = mid
            else:
                hi = mid
            if hi - lo < 1 / 86400:
                break

        return (lo + hi) / 2


# Module-level singleton (lazy init)
_provider: SwissEphemerisProvider | None = None


def get_provider() -> SwissEphemerisProvider:
    """Return the singleton astronomy provider, initializing on first call."""
    global _provider
    if _provider is None:
        _provider = SwissEphemerisProvider()
    return _provider
