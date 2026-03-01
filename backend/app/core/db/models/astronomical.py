"""
SQLAlchemy ORM models for pre-computed astronomical and calendar data.

These tables act as a persistent cache, eliminating repeated expensive
pyswisseph computations for historical and near-future dates.
"""
from __future__ import annotations

from datetime import date

from sqlalchemy import Date, Float, Integer, String, Boolean, DateTime, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class AstronomicalDay(Base):
    """
    Per-day astronomical data: solar/lunar positions and rise/set times.
    Pre-computed at midnight UTC for a reference location (not location-specific).
    """
    __tablename__ = "astronomical_day"

    date: Mapped[date] = mapped_column(Date, primary_key=True)
    sunrise_jd: Mapped[float | None] = mapped_column(Float, nullable=True)
    sunset_jd: Mapped[float | None] = mapped_column(Float, nullable=True)
    sun_tropical_lon: Mapped[float | None] = mapped_column(Float, nullable=True)
    moon_tropical_lon: Mapped[float | None] = mapped_column(Float, nullable=True)
    ayanamsa: Mapped[float | None] = mapped_column(Float, nullable=True)


class PanchangaSegment(Base):
    """
    Panchanga computed at sunrise for a lat/lon bucket (1° grid cells).
    Buckets reduce storage while still providing useful locality.
    """
    __tablename__ = "panchanga_segment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    # 1-degree grid buckets: round(lat), round(lon)
    lat_bucket: Mapped[int] = mapped_column(Integer, nullable=False)
    lon_bucket: Mapped[int] = mapped_column(Integer, nullable=False)
    tithi: Mapped[int] = mapped_column(Integer, nullable=False)
    paksha: Mapped[str] = mapped_column(String(10), nullable=False)
    nakshatra: Mapped[int] = mapped_column(Integer, nullable=False)
    yoga: Mapped[int] = mapped_column(Integer, nullable=False)
    karana: Mapped[str] = mapped_column(String(30), nullable=False)
    is_adhika: Mapped[bool] = mapped_column(Boolean, default=False)

    __table_args__ = (
        UniqueConstraint("date", "lat_bucket", "lon_bucket", name="uq_panchanga_segment"),
        Index("ix_panchanga_date_loc", "date", "lat_bucket", "lon_bucket"),
    )


class WBSankranti(Base):
    """
    West Bengal sankranti (solar ingress) table for years 2000–2100.
    Pre-computed via binary search; used at runtime for WB month boundaries.
    """
    __tablename__ = "wb_sankranti"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    sign: Mapped[int] = mapped_column(Integer, nullable=False)     # 0=Mesha .. 11=Mina
    sankranti_jd: Mapped[float] = mapped_column(Float, nullable=False)
    # Civil IST date when the WB month begins (after applying Bengal midnight rule)
    civil_date_ist: Mapped[date] = mapped_column(Date, nullable=False)

    __table_args__ = (
        UniqueConstraint("year", "sign", name="uq_wb_sankranti"),
        Index("ix_wb_sankranti_year", "year"),
    )


class FestivalInstance(Base):
    """
    Resolved festival instances — the output of the YAML DSL resolver.
    Pre-computed annually so runtime lookups are instant table scans.
    """
    __tablename__ = "festival_instance"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    greg_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    festival_id: Mapped[str] = mapped_column(String(100), nullable=False)
    tradition: Mapped[str] = mapped_column(String(20), nullable=False)
    region: Mapped[str] = mapped_column(String(5), nullable=False)
    name_bn: Mapped[str] = mapped_column(String(200), nullable=False)
    name_en: Mapped[str] = mapped_column(String(200), nullable=False)
    is_public_holiday: Mapped[bool] = mapped_column(Boolean, default=False)

    __table_args__ = (
        Index("ix_festival_date_region", "greg_date", "region"),
    )


class SightingOverride(Base):
    """
    Moon-sighting confirmations from the Bangladesh Islamic Foundation.
    When present, overrides the tabular Hijri date for Eid/Ramadan.
    """
    __tablename__ = "sighting_override"

    greg_date: Mapped[date] = mapped_column(Date, primary_key=True)
    hijri_year: Mapped[int] = mapped_column(Integer, nullable=False)
    hijri_month: Mapped[int] = mapped_column(Integer, nullable=False)
    hijri_day: Mapped[int] = mapped_column(Integer, nullable=False)
    source: Mapped[str] = mapped_column(String(200), nullable=False)
    confirmed_at: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
    note_bn: Mapped[str | None] = mapped_column(String(500), nullable=True)
