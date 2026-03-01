"""Panchanga API route."""
from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Query, HTTPException

from app.api.v1.schemas.calendar import PanchangaSchema

router = APIRouter(prefix="/panchanga", tags=["panchanga"])


@router.get("", response_model=PanchangaSchema)
def get_panchanga(
    date_str: str = Query(alias="date", description="ISO date (YYYY-MM-DD)"),
    lat: float = Query(description="Latitude (decimal degrees, N positive)"),
    lon: float = Query(description="Longitude (decimal degrees, E positive)"),
    region: str = Query(default="BD", description="Region for timezone: BD or WB"),
) -> PanchangaSchema:
    """Compute panchanga for a date and geographic location."""
    try:
        d = date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(status_code=422, detail=f"Invalid date: {date_str!r}")

    try:
        from app.core.astronomy.swisseph_provider import get_provider
        from app.core.panchanga.engine import PanchangaEngine
        provider = get_provider()
        engine = PanchangaEngine(provider)
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Astronomy engine unavailable: {e}. "
                   "Ensure pyswisseph is installed and EPHEMERIS_PATH is set.",
        )

    utc_offset = 5.5 if region.upper() == "WB" else 6.0
    try:
        p = engine.compute(d, lat, lon, utc_offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Panchanga computation failed: {e}")

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
