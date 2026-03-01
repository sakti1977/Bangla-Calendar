"""Calendar engine registry — maps region codes to engine instances."""
from __future__ import annotations

from app.core.calendars.bangladesh import BangladeshCalendarEngine

# WestBengalCalendarEngine will be added in Phase 3
_engines: dict[str, object] = {
    "BD": BangladeshCalendarEngine(),
}


def get_engine(region: str):
    """Return the calendar engine for the given region code ('BD' | 'WB')."""
    engine = _engines.get(region.upper())
    if engine is None:
        raise ValueError(f"Unknown calendar region: {region!r}. Valid regions: {list(_engines)}")
    return engine


def register_engine(region: str, engine) -> None:
    """Register or replace a calendar engine for a region."""
    _engines[region.upper()] = engine
