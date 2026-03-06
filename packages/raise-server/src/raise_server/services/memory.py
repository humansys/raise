"""Memory pattern service — orchestrates DB operations.

Stateless: receives session_factory, returns Pydantic models.
"""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from raise_server.db.memory_queries import insert_pattern, list_patterns
from raise_server.schemas.memory import (
    MemoryPatternCreate,
    MemoryPatternItem,
    MemoryPatternListResponse,
    MemoryPatternResponse,
)


async def add_pattern(
    session_factory: async_sessionmaker[AsyncSession],
    org_id: uuid.UUID,
    body: MemoryPatternCreate,
) -> MemoryPatternResponse:
    """Add a learned pattern and return its id."""
    async with session_factory() as session, session.begin():
        pattern_id = await insert_pattern(
            session, org_id, body.content, body.context, body.properties
        )
    return MemoryPatternResponse(id=pattern_id)


async def get_patterns(
    session_factory: async_sessionmaker[AsyncSession],
    org_id: uuid.UUID,
    limit: int = 50,
) -> MemoryPatternListResponse:
    """List patterns for an org."""
    async with session_factory() as session:
        rows = await list_patterns(session, org_id, limit=limit)
    patterns = [MemoryPatternItem(**r) for r in rows]
    return MemoryPatternListResponse(patterns=patterns, count=len(patterns))
