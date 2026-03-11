"""
Calendar API routes.

GET /api/v1/date-info  — full info for a single date
GET /api/v1/month      — bulk data for all days in a Gregorian month
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Query, HTTPException
from app.core.cache.redis_cache import (
    cache_get, cache_set,
    month_cache_key, date_info_cache_key,
)

from app.api.v1.schemas.calendar import (
    DateInfoResponse, MonthResponse, MonthDaySchema,
    BanglaDateSchema, PanchangaSchema, FestivalSchema,
)
from app.core.interfaces import BanglaDate, PanchangaResult, FestivalEntry

router = APIRouter(prefix="/calendar", tags=["calendar"])


def _bd_to_schema(bd: BanglaDate) -> BanglaDateSchema:
    return BanglaDateSchema(
        year=bd.year, month=bd.month, day=bd.day,
        month_name_bn=bd.month_name_bn, month_name_en=bd.month_name_en,
        year_bn=bd.year_bn, day_bn=bd.day_bn, era_bn=bd.era_bn,
        region=bd.region, is_sankranti=bd.is_sankranti,
        sankranti_time_ist=bd.sankranti_time_ist,
    )


def _panchanga_to_schema(p: PanchangaResult) -> PanchangaSchema:
    return PanchangaSchema(
        tithi_number=p.tithi_number, tithi_name_bn=p.tithi_name_bn,
        tithi_name_en=p.tithi_name_en, paksha_bn=p.paksha_bn, paksha_en=p.paksha_en,
        nakshatra_number=p.nakshatra_number, nakshatra_name_bn=p.nakshatra_name_bn,
        nakshatra_name_en=p.nakshatra_name_en, yoga_number=p.yoga_number,
        yoga_name_bn=p.yoga_name_bn, yoga_name_en=p.yoga_name_en,
        karana_name_bn=p.karana_name_bn, karana_name_en=p.karana_name_en,
        sunrise_local=p.sunrise_local, sunset_local=p.sunset_local,
        moon_longitude=p.moon_longitude, sun_longitude=p.sun_longitude,
        ayanamsa=p.ayanamsa, is_adhika_masa=p.is_adhika_masa,
        tithi_is_kshaya=p.tithi_is_kshaya, tithi_is_vriddhi=p.tithi_is_vriddhi,
    )


def _festival_to_schema(f: FestivalEntry) -> FestivalSchema:
    return FestivalSchema(
        id=f.id, name_bn=f.name_bn, name_en=f.name_en,
        tradition=f.tradition, is_public_holiday=f.is_public_holiday,
    )


def _get_wb_engine():
    """Lazily return WB engine if available."""
    try:
        from app.core.calendars.registry import get_engine
        return get_engine("WB")
    except (ValueError, Exception):
        return None


def _get_festival_resolver():
    """Lazily return festival resolver."""
    try:
        from app.core.festivals.resolver import FestivalResolver
        try:
            from app.core.astronomy.swisseph_provider import get_provider
            provider = get_provider()
        except Exception:
            provider = None
        return FestivalResolver(astronomy_provider=provider)
    except Exception:
        return None


def _get_panchanga_engine():
    """Lazily return panchanga engine."""
    try:
        from app.core.astronomy.swisseph_provider import get_provider
        from app.core.panchanga.engine import PanchangaEngine
        return PanchangaEngine(get_provider())
    except Exception:
        return None


@router.get("/date-info", response_model=DateInfoResponse)
def get_date_info(
    date_str: str = Query(alias="date", description="ISO date (YYYY-MM-DD)"),
    region: str = Query(default="BD", description="Region: BD or WB"),
    lat: Optional[float] = Query(default=None, description="Latitude for panchanga"),
    lon: Optional[float] = Query(default=None, description="Longitude for panchanga"),
    include_panchanga: bool = Query(default=False, description="Include panchanga data"),
) -> DateInfoResponse:
    """Return complete date information for a single Gregorian date."""
    try:
        d = date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(status_code=422, detail=f"Invalid date format: {date_str!r}")

    # Cache lookup (only cache non-panchanga requests; panchanga is location-specific)
    if not include_panchanga:
        cache_key = date_info_cache_key(date_str, region, lat, lon)
        cached = cache_get(cache_key)
        if cached is not None:
            return DateInfoResponse.model_validate(cached)

    # WB date (if engine registered)
    wb_schema = None
    wb_engine = _get_wb_engine()
    if wb_engine:
        try:
            wb_date = wb_engine.greg_to_bangla(d)
            wb_schema = _bd_to_schema(wb_date)
        except Exception:
            pass

    # Panchanga (optional)
    panchanga_schema = None
    if include_panchanga and lat is not None and lon is not None:
        p_engine = _get_panchanga_engine()
        if p_engine:
            try:
                utc_offset = 5.5 if region.upper() == "WB" else 6.0
                p = p_engine.compute(d, lat, lon, utc_offset)
                panchanga_schema = _panchanga_to_schema(p)
            except Exception as e:
                pass  # Panchanga optional; don't fail the whole request

    # Festivals
    festivals: list[FestivalSchema] = []
    resolver = _get_festival_resolver()
    if resolver:
        try:
            entries = resolver.get_festivals_for_date(d, region.upper())
            festivals = [_festival_to_schema(f) for f in entries]
        except Exception:
            pass

    response = DateInfoResponse(
        gregorian=d,
        wb=wb_schema,
        panchanga=panchanga_schema,
        festivals=festivals,
    )
    if not include_panchanga:
        cache_set(date_info_cache_key(date_str, region, lat, lon), response.model_dump(), ttl=86400)
    return response


@router.get("/month", response_model=MonthResponse)
def get_month(
    year: int = Query(description="Gregorian year"),
    month: int = Query(ge=1, le=12, description="Gregorian month (1-12)"),
    region: str = Query(default="BD", description="Region: BD or WB"),
    lat: Optional[float] = Query(default=None, description="Latitude for panchanga"),
    lon: Optional[float] = Query(default=None, description="Longitude for panchanga"),
) -> MonthResponse:
    """
    Return calendar data for all days in a Gregorian month.
    This is the hot path used for rendering the monthly calendar grid.
    Responses are Redis-cached with a 7-day TTL.
    """
    # Cache lookup (7-day TTL). If lat/lon provided, isolate cache by location.
    # We round lat/lon slightly so nearby locations share same panchanga cache
    lat_key = f"{lat:.2f}" if lat is not None else "none"
    lon_key = f"{lon:.2f}" if lon is not None else "none"
    ck = month_cache_key(year, month, region) + f":{lat_key}:{lon_key}"
    
    cached = cache_get(ck)
    if cached is not None:
        return MonthResponse.model_validate(cached)

    # Determine days in this month
    if month == 12:
        next_month_start = date(year + 1, 1, 1)
    else:
        next_month_start = date(year, month + 1, 1)
    month_start = date(year, month, 1)
    num_days = (next_month_start - month_start).days

    wb_engine = _get_wb_engine()
    resolver = _get_festival_resolver()
    p_engine = _get_panchanga_engine() if lat is not None and lon is not None else None
    utc_offset = 5.5 if region.upper() == "WB" else 6.0

    # Pre-compute all festivals for this year to avoid repeated resolution
    festival_map: dict[date, list[FestivalSchema]] = {}
    if resolver:
        try:
            year_festivals = resolver.get_festivals_for_year(year, region.upper())
            for d, entries in year_festivals.items():
                festival_map[d] = [_festival_to_schema(f) for f in entries]
        except Exception:
            pass

    days = []
    for day_num in range(num_days):
        d = month_start + timedelta(days=day_num)

        wb_schema = None
        if wb_engine:
            try:
                wb_date = wb_engine.greg_to_bangla(d)
                wb_schema = _bd_to_schema(wb_date)
            except Exception:
                pass

        festivals = festival_map.get(d, [])

        panchanga_schema = None
        if p_engine and lat is not None and lon is not None:
            try:
                p = p_engine.compute(d, lat, lon, utc_offset)
                panchanga_schema = _panchanga_to_schema(p)
            except Exception:
                pass

        days.append(MonthDaySchema(
            gregorian=d,
            wb=wb_schema,
            panchanga=panchanga_schema,
            festivals=festivals,
        ))

    result = MonthResponse(year=year, month=month, region=region.upper(), days=days)
    cache_set(ck, result.model_dump(), ttl=604800)  # 7 days
    return result
