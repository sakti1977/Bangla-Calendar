"""
Bangla Calendar API — FastAPI application entry point.
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.v1.router import router as v1_router

app = FastAPI(
    title="Bangla Calendar API",
    description=(
        "Production-grade API for Bangladesh civil calendar, West Bengal sidereal calendar, "
        "Hijri calendar, Panchāṅga computations, and festival resolution."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(v1_router)


@app.get("/health", tags=["system"])
def health_check() -> dict:
    return {"status": "ok", "version": "0.1.0"}
