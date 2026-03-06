"""Typed accessors for FastAPI app.state — breaks circular imports.

app.py, auth.py, and health.py all import from here instead of from each other.
"""

from __future__ import annotations

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker


def get_engine(app: FastAPI) -> AsyncEngine:
    """Extract the async engine from app.state."""
    engine: AsyncEngine = app.state.engine  # type: ignore[has-type]
    return engine


def get_session_factory(app: FastAPI) -> async_sessionmaker[AsyncSession]:
    """Extract the async session factory from app.state."""
    factory: async_sessionmaker[AsyncSession] = app.state.session_factory  # type: ignore[has-type]
    return factory
