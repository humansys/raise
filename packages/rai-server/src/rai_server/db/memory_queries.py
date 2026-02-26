"""SQL query functions for memory patterns.

All functions receive an AsyncSession and return plain dicts or scalars.
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import Result, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from rai_server.db.models import MemoryPatternRow


async def insert_pattern(
    session: AsyncSession,
    org_id: uuid.UUID,
    content: str,
    context: list[str],
    properties: dict[str, Any],
) -> uuid.UUID:
    """Insert a memory pattern. Returns the new pattern's UUID."""
    stmt = (
        pg_insert(MemoryPatternRow)
        .values(
            org_id=org_id,
            content=content,
            context=context,
            properties=properties,
        )
        .returning(MemoryPatternRow.id)
    )
    result: Result[Any] = await session.execute(stmt)
    return result.scalar_one()  # type: ignore[return-value]  # SA UUID scalar


async def list_patterns(
    session: AsyncSession,
    org_id: uuid.UUID,
) -> list[dict[str, Any]]:
    """List all patterns for an org, newest first."""
    stmt = (  # type: ignore[var-annotated]  # SA JSONB propagates Unknown through select
        select(
            MemoryPatternRow.id,
            MemoryPatternRow.content,
            MemoryPatternRow.context,  # type: ignore[arg-type]  # SA JSONB
            MemoryPatternRow.properties,  # type: ignore[arg-type]  # SA JSONB
            MemoryPatternRow.created_at,
        )
        .where(MemoryPatternRow.org_id == org_id)
        .order_by(MemoryPatternRow.created_at.desc())
    )
    result: Result[Any] = await session.execute(stmt)  # type: ignore[arg-type]  # SA JSONB type variance
    return [dict(row) for row in result.mappings().all()]
