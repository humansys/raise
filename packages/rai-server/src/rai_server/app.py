"""FastAPI application factory with lifespan management."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, AsyncSession

from rai_server.api.v1.health import router as health_router
from rai_server.config import ServerConfig
from rai_server.db.session import create_engine, create_session_factory


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Create DB engine on startup, dispose on shutdown."""
    config: ServerConfig = app.state.config  # type: ignore[has-type]
    engine = create_engine(config.database_url)
    app.state.engine = engine
    app.state.session_factory = create_session_factory(engine)
    yield
    await engine.dispose()


def create_app(config: ServerConfig | None = None) -> FastAPI:
    """Application factory — creates and configures the FastAPI app.

    Args:
        config: Optional config override (for testing). Reads env vars if None.
    """
    if config is None:
        config = ServerConfig()  # type: ignore[call-arg]  # pydantic-settings reads env
    app = FastAPI(
        title="RaiSE Server",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.state.config = config
    app.include_router(health_router)
    return app


def get_engine(app: FastAPI) -> AsyncEngine:
    """Extract the engine from app.state (typed accessor)."""
    engine: AsyncEngine = app.state.engine  # type: ignore[has-type]
    return engine


def get_session_factory(app: FastAPI) -> async_sessionmaker[AsyncSession]:
    """Extract the session factory from app.state (typed accessor)."""
    factory: async_sessionmaker[AsyncSession] = app.state.session_factory  # type: ignore[has-type]
    return factory
