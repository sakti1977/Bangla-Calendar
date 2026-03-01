"""
Async SQLAlchemy engine and session factory.

Usage in route handlers:
    async with get_session() as session:
        result = await session.execute(...)
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.config import settings

_engine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    echo=False,
)

_session_factory = async_sessionmaker(
    _engine, expire_on_commit=False, class_=AsyncSession
)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with _session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def create_all_tables() -> None:
    """Create all tables (for development / testing only; use Alembic in production)."""
    from app.core.db.models.base import Base
    import app.core.db.models.astronomical  # noqa: F401 — ensure models are registered
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
