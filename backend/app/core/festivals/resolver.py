"""
Festival DSL rule interpreter.

Loads YAML rule files and resolves each festival rule to a concrete Gregorian
date for a given Gregorian year and region. Supports rule types:
  - fixed_gregorian:  fixed Gregorian month+day
  - fixed_bangla_bd:  fixed BD Bangla month+day
  - fixed_bangla_wb:  fixed WB Bangla month+day
  - tithi_based:      astronomical; search for matching tithi/paksha/lunar_month
  - hijri_sighting:   Hijri date with optional sighting override
  - easter_based:     Easter Sunday ± offset days
"""
from __future__ import annotations

import math
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import yaml

from app.core.interfaces import FestivalEntry, AstronomyProvider

_RULES_DIR = Path(__file__).parent / "rules"
_RULE_FILES = ["civic.yaml", "hindu.yaml", "muslim.yaml", "buddhist.yaml", "christian.yaml"]

# Amanta lunar month numbering: 1=Chaitra, 2=Vaishakha(Boishakh), ..., 12=Phalguna(Falgun)
# Map to approximate Gregorian month window for searching (±2 months added in search)
_LUNAR_MONTH_TO_GREG_APPROX = {
    1: 3, 2: 4, 3: 5, 4: 6, 5: 7, 6: 8,
    7: 9, 8: 10, 9: 11, 10: 12, 11: 1, 12: 2,
}


def _load_all_rules() -> list[dict]:
    rules = []
    for fname in _RULE_FILES:
        path = _RULES_DIR / fname
        if path.exists():
            with open(path, encoding="utf-8") as f:
                rules.extend(yaml.safe_load(f) or [])
    return rules


def _easter_sunday(year: int) -> date:
    """Compute Easter Sunday for the given Gregorian year (Anonymous Gregorian algorithm)."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


class FestivalResolver:
    """Resolves festival rules into concrete dates."""

    def __init__(self, astronomy_provider: AstronomyProvider | None = None) -> None:
        self._rules = _load_all_rules()
        self._astronomy = astronomy_provider
        # Import lazily to avoid circular imports
        self._bd_engine = None
        self._wb_engine = None
        self._hijri_engine = None

    def _get_bd_engine(self):
        if self._bd_engine is None:
            from app.core.calendars.bangladesh import BangladeshCalendarEngine
            self._bd_engine = BangladeshCalendarEngine()
        return self._bd_engine

    def _get_hijri_engine(self):
        if self._hijri_engine is None:
            from app.core.calendars.hijri import HijriCalendarEngine
            self._hijri_engine = HijriCalendarEngine()
        return self._hijri_engine

    def get_festivals_for_date(
        self, d: date, region: str, traditions: list[str] | None = None
    ) -> list[FestivalEntry]:
        """Return all festivals that fall on the given Gregorian date for the region."""
        results = []
        year = d.year
        for rule in self._rules:
            if region not in rule.get("regions", []):
                continue
            if traditions and rule.get("tradition") not in traditions:
                continue
            try:
                resolved = self._resolve_rule(rule, year, region)
            except Exception:
                continue
            if resolved == d:
                results.append(FestivalEntry(
                    id=rule["id"],
                    name_bn=rule["name_bn"],
                    name_en=rule["name_en"],
                    tradition=rule["tradition"],
                    is_public_holiday=rule.get("is_public_holiday", False),
                ))
        return results

    def get_festivals_for_year(
        self, greg_year: int, region: str, traditions: list[str] | None = None
    ) -> dict[date, list[FestivalEntry]]:
        """Return a dict mapping dates to festival lists for a full Gregorian year."""
        result: dict[date, list[FestivalEntry]] = {}
        for rule in self._rules:
            if region not in rule.get("regions", []):
                continue
            if traditions and rule.get("tradition") not in traditions:
                continue
            try:
                resolved = self._resolve_rule(rule, greg_year, region)
            except Exception:
                continue
            if resolved:
                entry = FestivalEntry(
                    id=rule["id"],
                    name_bn=rule["name_bn"],
                    name_en=rule["name_en"],
                    tradition=rule["tradition"],
                    is_public_holiday=rule.get("is_public_holiday", False),
                )
                result.setdefault(resolved, []).append(entry)
        return result

    def _resolve_rule(self, rule: dict, year: int, region: str) -> date | None:
        r = rule["rule"]
        rtype = r["type"]

        if rtype == "fixed_gregorian":
            try:
                return date(year, r["greg_month"], r["greg_day"])
            except ValueError:
                return None

        elif rtype == "fixed_bangla_bd":
            # Pahela Baishakh etc: resolve for the Bangla year starting in this Greg year
            engine = self._get_bd_engine()
            bangla_year = year - 593  # approximate; year starts in April
            try:
                return engine.bangla_to_greg(bangla_year, r["bangla_month"], r["bangla_day"])
            except Exception:
                return None

        elif rtype == "fixed_bangla_wb":
            if self._wb_engine is None:
                return None
            bangla_year = year - 593
            try:
                return self._wb_engine.bangla_to_greg(bangla_year, r["bangla_month"], r["bangla_day"])
            except Exception:
                return None

        elif rtype == "hijri_sighting":
            hijri_month = r["hijri_month"]
            hijri_day = r["hijri_day"]
            engine = self._get_hijri_engine()
            # Compute approximate Hijri year for this Greg year
            # Hijri year ≈ greg_year * 1.0307 - 621.57
            approx_hijri_year = round(year * 1.0307 - 621.57)
            for hy in [approx_hijri_year, approx_hijri_year - 1, approx_hijri_year + 1]:
                try:
                    d = engine.hijri_to_greg(hy, hijri_month, hijri_day)
                    if d.year == year:
                        return d
                except Exception:
                    continue
            return None

        elif rtype == "tithi_based":
            return self._resolve_tithi_based(r, year, region)

        elif rtype == "easter_based":
            easter = _easter_sunday(year)
            return easter + timedelta(days=r.get("offset_days", 0))

        return None

    def _resolve_tithi_based(self, rule: dict, year: int, region: str) -> date | None:
        """Search for the day matching the tithi/paksha/lunar_month condition."""
        if self._astronomy is None:
            return None

        from app.core.panchanga.engine import PanchangaEngine
        from app.core.calendars.julian_day import gregorian_to_jd

        target_tithi = rule["tithi"]
        target_paksha = rule["paksha"]  # "shukla" or "krishna"
        target_lunar_month = rule.get("lunar_month")
        critical_window = rule.get("critical_window", "sunrise")
        tie_break = rule.get("tie_break", "prevailing_at_sunrise")

        # Reference city for panchanga computation
        if region == "WB":
            lat, lon, utc_offset = 22.5726, 88.3639, 5.5  # Kolkata
        else:
            lat, lon, utc_offset = 23.8103, 90.4125, 6.0  # Dhaka

        engine = PanchangaEngine(self._astronomy)

        # Approximate search window: ±2 months around expected lunar month
        approx_greg_month = _LUNAR_MONTH_TO_GREG_APPROX.get(target_lunar_month or 0, 6)
        # Build a 70-day search window centered on the approximate month
        search_start = date(year, approx_greg_month, 1) - timedelta(days=15)
        candidates = []

        for offset in range(70):
            d = search_start + timedelta(days=offset)
            if d.year != year:
                continue
            try:
                panchanga = engine.compute(d, lat, lon, utc_offset)
            except Exception:
                continue

            p_tithi = panchanga.tithi_number
            p_paksha = "shukla" if p_tithi <= 15 else "krishna"
            # Normalize tithi within paksha (1-15)
            p_tithi_in_paksha = p_tithi if p_tithi <= 15 else p_tithi - 15

            if p_tithi_in_paksha != target_tithi:
                continue
            if p_paksha != target_paksha:
                continue

            # Apply critical_window filter
            jd_date = gregorian_to_jd(d) - utc_offset / 24

            if critical_window == "sunrise":
                candidates.append(d)
            elif critical_window == "midnight":
                # Check tithi at midnight (local)
                midnight_jd = jd_date + 1.0 - utc_offset / 24  # next midnight
                at_midnight = engine.compute_at_jd(midnight_jd, lat, lon, utc_offset)
                m_tithi_in_paksha = at_midnight["tithi"] if at_midnight["tithi"] <= 15 else at_midnight["tithi"] - 15
                if m_tithi_in_paksha == target_tithi and at_midnight["paksha"] == target_paksha:
                    candidates.append(d)
            elif critical_window in ("full_day", "pradosh"):
                candidates.append(d)

        if not candidates:
            return None
        if len(candidates) == 1:
            return candidates[0]

        # Tie-break
        if tie_break == "next_day_if_spans_two":
            return candidates[-1]
        elif tie_break == "prior_day_if_spans_two":
            return candidates[0]
        else:  # prevailing_at_sunrise or midnight_prevailing
            return candidates[0]
