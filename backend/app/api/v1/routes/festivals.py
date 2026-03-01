"""Festivals API route."""
from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel

from app.api.v1.schemas.calendar import FestivalSchema

router = APIRouter(prefix="/festivals", tags=["festivals"])


class FestivalYearResponse(BaseModel):
    greg_year: int
    region: str
    festivals: dict[str, list[FestivalSchema]]  # ISO date string → list


@router.get("", response_model=FestivalYearResponse)
def get_festivals(
    year: int = Query(description="Gregorian year"),
    region: str = Query(default="BD", description="Region: BD or WB"),
    tradition: Optional[str] = Query(
        default=None,
        description="Filter by tradition: hindu,muslim,buddhist,christian,civic (comma-separated)",
    ),
) -> FestivalYearResponse:
    """Return all festivals for a Gregorian year and region."""
    try:
        from app.core.festivals.resolver import FestivalResolver
        try:
            from app.core.astronomy.swisseph_provider import get_provider
            provider = get_provider()
        except Exception:
            provider = None
        resolver = FestivalResolver(astronomy_provider=provider)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Festival engine unavailable: {e}")

    traditions = [t.strip() for t in tradition.split(",")] if tradition else None

    try:
        festival_map = resolver.get_festivals_for_year(year, region.upper(), traditions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Festival resolution failed: {e}")

    result: dict[str, list[FestivalSchema]] = {}
    for d, entries in sorted(festival_map.items()):
        result[d.isoformat()] = [
            FestivalSchema(
                id=f.id, name_bn=f.name_bn, name_en=f.name_en,
                tradition=f.tradition, is_public_holiday=f.is_public_holiday,
            )
            for f in entries
        ]

    return FestivalYearResponse(greg_year=year, region=region.upper(), festivals=result)
