"""Async database engine and session factory.

Usage (after S275.3 config is available):
    engine = create_engine("postgresql+asyncpg://...")
    async with get_session(engine) as session:
        ...
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


def create_engine(database_url: str) -> AsyncEngine:
    """Create an async SQLAlchemy engine."""
    return create_async_engine(database_url, echo=False)


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Create an async session factory bound to the engine."""
    return async_sessionmaker(engine, expire_on_commit=False)


@asynccontextmanager
async def get_session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Convenience context manager for a single async session."""
    factory = create_session_factory(engine)
    async with factory() as session:
        yield session
