"""Islamic (Hijri) date API route."""
from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Query, HTTPException

from app.api.v1.schemas.calendar import HijriDateSchema
from app.core.calendars.hijri import HijriCalendarEngine

router = APIRouter(prefix="/islamic-date", tags=["islamic"])

_engine = HijriCalendarEngine()


@router.get("", response_model=HijriDateSchema)
def get_islamic_date(
    date_str: str = Query(alias="date", description="ISO date (YYYY-MM-DD)"),
) -> HijriDateSchema:
    """Convert a Gregorian date to Hijri date."""
    try:
        d = date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(status_code=422, detail=f"Invalid date: {date_str!r}")

    h = _engine.greg_to_hijri(d)
    return HijriDateSchema(
        year=h.year, month=h.month, day=h.day,
        month_name_bn=h.month_name_bn, month_name_en=h.month_name_en,
        year_bn=h.year_bn, day_bn=h.day_bn, era_bn=h.era_bn,
        is_sighting_confirmed=h.is_sighting_confirmed, note_bn=h.note_bn,
    )
