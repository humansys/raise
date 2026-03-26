"""FastAPI application factory with lifespan management."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from raise_server import __version__
from raise_server.api.v1.agent import router as agent_router
from raise_server.api.v1.graph import router as graph_router
from raise_server.api.v1.health import router as health_router
from raise_server.api.v1.memory import router as memory_router
from raise_server.api.v1.members import router as member_router
from raise_server.api.v1.organizations import router as org_router
from raise_server.config import ServerConfig
from raise_server.db.session import create_engine, create_session_factory


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
        version=__version__,
        lifespan=lifespan,
    )
    app.state.config = config
    app.include_router(health_router)
    app.include_router(graph_router)
    app.include_router(agent_router)
    app.include_router(memory_router)
    app.include_router(org_router)
    app.include_router(member_router)
    return app
