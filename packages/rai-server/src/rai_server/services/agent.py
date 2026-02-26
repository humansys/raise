"""Agent telemetry service — orchestrates DB operations.

Stateless: receives session_factory, returns Pydantic models.
"""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from rai_server.db.agent_queries import insert_event, list_events
from rai_server.schemas.agent import (
    AgentEventCreate,
    AgentEventItem,
    AgentEventListResponse,
    AgentEventResponse,
)


async def record_event(
    session_factory: async_sessionmaker[AsyncSession],
    org_id: uuid.UUID,
    body: AgentEventCreate,
) -> AgentEventResponse:
    """Record a telemetry event and return its id."""
    async with session_factory() as session, session.begin():
        event_id = await insert_event(session, org_id, body.event_type, body.payload)
    return AgentEventResponse(id=event_id)


async def get_events(
    session_factory: async_sessionmaker[AsyncSession],
    org_id: uuid.UUID,
    limit: int = 20,
) -> AgentEventListResponse:
    """List recent events for an org."""
    async with session_factory() as session:
        rows = await list_events(session, org_id, limit=limit)
    events = [AgentEventItem(**r) for r in rows]
    return AgentEventListResponse(events=events, total=len(events))
