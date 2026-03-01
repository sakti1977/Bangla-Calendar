"""
Redis caching utilities for the Bangla Calendar API.

Design principles:
- Graceful degradation: if Redis is unavailable, the API works without cache.
- Deterministic data (month calendar, festivals) uses a 7-day TTL.
- Cache keys are fully deterministic from request parameters.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Callable, Optional

log = logging.getLogger(__name__)

_redis_client: Optional[Any] = None


def _get_redis():
    """Return a redis.Redis client, initializing lazily. Returns None if unavailable."""
    global _redis_client
    if _redis_client is not None:
        return _redis_client
    try:
        import redis
        from app.config import settings
        client = redis.from_url(settings.redis_url, decode_responses=True, socket_connect_timeout=1)
        client.ping()
        _redis_client = client
        log.info("Redis cache connected at %s", settings.redis_url)
        return _redis_client
    except Exception as exc:
        log.warning("Redis unavailable — caching disabled: %s", exc)
        return None


def cache_get(key: str) -> Optional[Any]:
    """Retrieve a JSON-encoded value from Redis. Returns None on miss or error."""
    r = _get_redis()
    if r is None:
        return None
    try:
        raw = r.get(key)
        if raw is None:
            return None
        return json.loads(raw)
    except Exception as exc:
        log.debug("Cache GET error for %r: %s", key, exc)
        return None


def cache_set(key: str, value: Any, ttl: int = 604800) -> None:
    """Store a JSON-encodable value in Redis with a TTL (default: 7 days)."""
    r = _get_redis()
    if r is None:
        return
    try:
        r.setex(key, ttl, json.dumps(value, default=str))
    except Exception as exc:
        log.debug("Cache SET error for %r: %s", key, exc)


def cache_delete_pattern(pattern: str) -> int:
    """Delete all keys matching a glob pattern. Returns count deleted."""
    r = _get_redis()
    if r is None:
        return 0
    try:
        keys = r.keys(pattern)
        if keys:
            return r.delete(*keys)
        return 0
    except Exception as exc:
        log.debug("Cache DELETE error for pattern %r: %s", pattern, exc)
        return 0


# ---------------------------------------------------------------------------
# Key builders
# ---------------------------------------------------------------------------

def month_cache_key(year: int, month: int, region: str) -> str:
    return f"bcal:month:{year}:{month:02d}:{region.upper()}"


def date_info_cache_key(date_str: str, region: str, lat: Optional[float], lon: Optional[float]) -> str:
    loc = f"{lat:.4f},{lon:.4f}" if lat is not None and lon is not None else "no-loc"
    return f"bcal:date:{date_str}:{region.upper()}:{loc}"


def festivals_cache_key(bangla_year: int, tradition: str, region: str) -> str:
    return f"bcal:festivals:{bangla_year}:{tradition}:{region.upper()}"
