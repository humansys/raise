"""Health endpoint — public, no auth required."""

from __future__ import annotations

from fastapi import APIRouter, Request
from sqlalchemy import text

router = APIRouter()


async def _check_db(request: Request) -> bool:
    """Ping the database with SELECT 1."""
    try:
        from rai_server.app import get_engine

        engine = get_engine(request.app)
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


@router.get("/health")
async def health(request: Request) -> dict[str, str]:
    """Server health check with DB connectivity status."""
    db_ok = await _check_db(request)
    return {
        "status": "ok",
        "database": "connected" if db_ok else "disconnected",
        "version": "0.1.0",
    }
