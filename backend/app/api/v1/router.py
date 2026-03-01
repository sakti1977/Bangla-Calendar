"""Aggregate all v1 API routes."""
from fastapi import APIRouter

from app.api.v1.routes import calendar, panchanga, festivals, islamic

router = APIRouter(prefix="/api/v1")

router.include_router(calendar.router)
router.include_router(panchanga.router)
router.include_router(festivals.router)
router.include_router(islamic.router)
