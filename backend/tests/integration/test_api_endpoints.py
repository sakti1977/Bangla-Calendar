"""
Integration tests for the Bangla Calendar API.

These tests spin up the FastAPI app via httpx's AsyncClient and hit the
real endpoints. They do NOT require a running Redis or PostgreSQL instance —
the app degrades gracefully when those services are unavailable.
"""
from __future__ import annotations

import pytest
from httpx import AsyncClient, ASGITransport
from fastapi.testclient import TestClient

from app.main import app


# ---------------------------------------------------------------------------
# Synchronous smoke tests using TestClient (no asyncio required)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_health_check(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"


def test_date_info_pahela_baishakh(client):
    """April 14, 2024 must be Bangla 1 Boishakh 1431."""
    resp = client.get("/api/v1/calendar/date-info", params={"date": "2024-04-14", "region": "BD"})
    assert resp.status_code == 200
    data = resp.json()
    bd = data["bd"]
    assert bd["year"] == 1431
    assert bd["month"] == 1
    assert bd["day"] == 1
    assert bd["month_name_en"] == "Boishakh"


def test_date_info_gregorian_feb_leap(client):
    """Feb 29, 2024 must be Falgun 16, 1430 (leap year)."""
    resp = client.get("/api/v1/calendar/date-info", params={"date": "2024-02-29", "region": "BD"})
    assert resp.status_code == 200
    data = resp.json()
    bd = data["bd"]
    assert bd["year"] == 1430
    assert bd["month"] == 11
    assert bd["day"] == 16


def test_date_info_includes_hijri(client):
    """date-info must always return a hijri date."""
    resp = client.get("/api/v1/calendar/date-info", params={"date": "2024-04-10", "region": "BD"})
    assert resp.status_code == 200
    data = resp.json()
    hijri = data["hijri"]
    assert hijri["year"] == 1445
    assert hijri["month"] == 10   # Shawwal
    assert hijri["era_bn"] == "হিজরি"


def test_date_info_invalid_date(client):
    resp = client.get("/api/v1/calendar/date-info", params={"date": "not-a-date"})
    assert resp.status_code == 422


def test_month_endpoint_april_2024(client):
    """April 2024 month endpoint: must have 30 days, first day = Boishakh 1."""
    resp = client.get("/api/v1/calendar/month", params={"year": 2024, "month": 4, "region": "BD"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["year"] == 2024
    assert data["month"] == 4
    assert data["region"] == "BD"
    days = data["days"]
    assert len(days) == 30
    # April 14 = BD 1 Boishakh (0-indexed: day 13)
    april14 = days[13]
    assert april14["bd"]["year"] == 1431
    assert april14["bd"]["month"] == 1
    assert april14["bd"]["day"] == 1


def test_month_endpoint_february_2024_leap(client):
    """February 2024 has 29 days (leap year)."""
    resp = client.get("/api/v1/calendar/month", params={"year": 2024, "month": 2, "region": "BD"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["days"]) == 29


def test_month_endpoint_invalid_month(client):
    resp = client.get("/api/v1/calendar/month", params={"year": 2024, "month": 13})
    assert resp.status_code == 422


def test_festivals_pahela_baishakh(client):
    """April 14, 2024 must include Pahela Baishakh festival."""
    resp = client.get("/api/v1/calendar/date-info", params={"date": "2024-04-14", "region": "BD"})
    assert resp.status_code == 200
    data = resp.json()
    festival_ids = [f["id"] for f in data.get("festivals", [])]
    assert "pahela_baishakh_bd" in festival_ids


def test_date_info_region_wb(client):
    """WB region requests should not error out (wb_date may be None if pyswisseph absent)."""
    resp = client.get("/api/v1/calendar/date-info", params={"date": "2024-04-14", "region": "WB"})
    assert resp.status_code == 200
    data = resp.json()
    # BD date always present
    assert data["bd"]["year"] == 1431


def test_month_response_schema(client):
    """All days in month response must have required fields."""
    resp = client.get("/api/v1/calendar/month", params={"year": 2024, "month": 1, "region": "BD"})
    assert resp.status_code == 200
    for day in resp.json()["days"]:
        assert "gregorian" in day
        assert "bd" in day
        assert "hijri" in day
        bd = day["bd"]
        assert 1 <= bd["month"] <= 12
        assert 1 <= bd["day"] <= 31
