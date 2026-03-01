"""
Abstract protocols that define the pluggable calendar engine architecture.
All calendar engines, astronomy providers, and festival engines implement these.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Protocol, runtime_checkable


# ---------------------------------------------------------------------------
# Shared data classes
# ---------------------------------------------------------------------------

@dataclass
class BanglaDate:
    year: int
    month: int          # 1-indexed
    day: int
    month_name_bn: str
    month_name_en: str
    year_bn: str        # Bengali numeral string
    day_bn: str         # Bengali numeral string
    era_bn: str         # e.g. "বঙ্গাব্দ"
    region: str         # 'BD' | 'WB'
    is_sankranti: bool = False     # WB only: this day is a sankranti day
    sankranti_time_ist: str | None = None  # WB: ISO time of sankranti in IST


@dataclass
class HijriDate:
    year: int
    month: int
    day: int
    month_name_bn: str
    month_name_en: str
    year_bn: str
    day_bn: str
    era_bn: str = "হিজরি"
    is_sighting_confirmed: bool = False
    note_bn: str | None = None   # e.g. "গণনা ভিত্তিক (চাঁদ দেখা সাপেক্ষে)"


@dataclass
class PanchangaResult:
    tithi_number: int         # 1–30
    tithi_name_bn: str
    tithi_name_en: str
    paksha_bn: str            # "শুক্লপক্ষ" | "কৃষ্ণপক্ষ"
    paksha_en: str            # "Shukla" | "Krishna"
    nakshatra_number: int     # 1–27
    nakshatra_name_bn: str
    nakshatra_name_en: str
    yoga_number: int          # 1–27
    yoga_name_bn: str
    yoga_name_en: str
    karana_name_bn: str
    karana_name_en: str
    sunrise_local: str        # "HH:MM" in local timezone
    sunset_local: str         # "HH:MM"
    moon_longitude: float     # sidereal degrees
    sun_longitude: float      # sidereal degrees
    ayanamsa: float           # Lahiri ayanamsa in degrees
    is_adhika_masa: bool = False
    tithi_is_kshaya: bool = False   # tithi was skipped
    tithi_is_vriddhi: bool = False  # tithi spans two sunrises


@dataclass
class FestivalEntry:
    id: str
    name_bn: str
    name_en: str
    tradition: str   # 'hindu' | 'muslim' | 'buddhist' | 'christian' | 'civic'
    is_public_holiday: bool = False
    note_bn: str | None = None


@dataclass
class DayInfo:
    gregorian: date
    bd: BanglaDate | None = None
    wb: BanglaDate | None = None
    hijri: HijriDate | None = None
    panchanga: PanchangaResult | None = None
    festivals: list[FestivalEntry] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Protocol definitions
# ---------------------------------------------------------------------------

@runtime_checkable
class CalendarEngine(Protocol):
    region: str

    def greg_to_bangla(self, d: date) -> BanglaDate: ...
    def bangla_to_greg(self, year: int, month: int, day: int) -> date: ...
    def month_length(self, year: int, month: int) -> int: ...
    def is_leap_year(self, bangla_year: int) -> bool: ...


@runtime_checkable
class AstronomyProvider(Protocol):
    def solar_longitude_tropical(self, jd: float) -> float: ...   # tropical degrees
    def lunar_longitude_tropical(self, jd: float) -> float: ...   # tropical degrees
    def solar_longitude_sidereal(self, jd: float) -> float: ...   # sidereal degrees
    def lunar_longitude_sidereal(self, jd: float) -> float: ...   # sidereal degrees
    def lahiri_ayanamsa(self, jd: float) -> float: ...
    def sunrise_jd(self, jd_date: float, lat: float, lon: float) -> float: ...
    def sunset_jd(self, jd_date: float, lat: float, lon: float) -> float: ...


@runtime_checkable
class FestivalEngine(Protocol):
    def get_festivals_for_date(
        self, d: date, region: str, traditions: list[str] | None
    ) -> list[FestivalEntry]: ...

    def get_festivals_for_month(
        self, year: int, month: int, region: str
    ) -> dict[date, list[FestivalEntry]]: ...
