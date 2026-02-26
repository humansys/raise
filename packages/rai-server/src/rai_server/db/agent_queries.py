"""SQL query functions for agent telemetry events.

All functions receive an AsyncSession and return plain dicts or scalars.
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import Result, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from rai_server.db.models import AgentEventRow


async def insert_event(
    session: AsyncSession,
    org_id: uuid.UUID,
    event_type: str,
    payload: dict[str, Any],
) -> uuid.UUID:
    """Insert a telemetry event. Returns the new event's UUID."""
    stmt = (
        pg_insert(AgentEventRow)
        .values(org_id=org_id, event_type=event_type, payload=payload)
        .returning(AgentEventRow.id)
    )
    result: Result[Any] = await session.execute(stmt)
    return result.scalar_one()  # type: ignore[return-value]  # SA UUID scalar


async def list_events(
    session: AsyncSession,
    org_id: uuid.UUID,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """List recent events for an org, newest first."""
    stmt = (
        select(
            AgentEventRow.id,
            AgentEventRow.event_type,
            AgentEventRow.payload,  # type: ignore[arg-type]  # SA JSONB
            AgentEventRow.created_at,
        )
        .where(AgentEventRow.org_id == org_id)
        .order_by(AgentEventRow.created_at.desc())
        .limit(limit)
    )
    result: Result[Any] = await session.execute(stmt)
    return [dict(row) for row in result.mappings().all()]
