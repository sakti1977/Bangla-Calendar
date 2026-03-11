"""Pydantic response schemas for calendar API endpoints."""
from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class BanglaDateSchema(BaseModel):
    year: int
    month: int
    day: int
    month_name_bn: str
    month_name_en: str
    year_bn: str = Field(description="Year in Bengali numerals")
    day_bn: str = Field(description="Day in Bengali numerals")
    era_bn: str
    region: str
    is_sankranti: bool = False
    sankranti_time_ist: Optional[str] = None

    model_config = {"from_attributes": True}


class HijriDateSchema(BaseModel):
    year: int
    month: int
    day: int
    month_name_bn: str
    month_name_en: str
    year_bn: str = Field(description="Year in Bengali numerals")
    day_bn: str = Field(description="Day in Bengali numerals")
    era_bn: str
    is_sighting_confirmed: bool = False
    note_bn: Optional[str] = None

    model_config = {"from_attributes": True}



class PanchangaSchema(BaseModel):
    tithi_number: int
    tithi_name_bn: str
    tithi_name_en: str
    paksha_bn: str
    paksha_en: str
    nakshatra_number: int
    nakshatra_name_bn: str
    nakshatra_name_en: str
    yoga_number: int
    yoga_name_bn: str
    yoga_name_en: str
    karana_name_bn: str
    karana_name_en: str
    sunrise_local: str
    sunset_local: str
    moon_longitude: float
    sun_longitude: float
    ayanamsa: float
    is_adhika_masa: bool = False
    tithi_is_kshaya: bool = False
    tithi_is_vriddhi: bool = False

    model_config = {"from_attributes": True}


class FestivalSchema(BaseModel):
    id: str
    name_bn: str
    name_en: str
    tradition: str
    is_public_holiday: bool = False
    note_bn: Optional[str] = None

    model_config = {"from_attributes": True}


class DateInfoResponse(BaseModel):
    gregorian: date
    bd: Optional[BanglaDateSchema] = None
    wb: Optional[BanglaDateSchema] = None
    hijri: Optional[HijriDateSchema] = None
    panchanga: Optional[PanchangaSchema] = None
    festivals: list[FestivalSchema] = []


class MonthDaySchema(BaseModel):
    gregorian: date
    bd: Optional[BanglaDateSchema] = None
    wb: Optional[BanglaDateSchema] = None
    hijri: Optional[HijriDateSchema] = None
    panchanga: Optional[PanchangaSchema] = None
    festivals: list[FestivalSchema] = []


class MonthResponse(BaseModel):
    year: int
    month: int
    region: str
    days: list[MonthDaySchema]
