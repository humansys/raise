"""Agent telemetry API routes.

Thin handlers — validate input, delegate to service, return response.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query, Request

from raise_server.auth import MemberContext, requires_plan
from raise_server.deps import get_session_factory
from raise_server.schemas.agent import (
    AgentEventCreate,
    AgentEventListResponse,
    AgentEventResponse,
)
from raise_server.services.agent import get_events, record_event

router = APIRouter(prefix="/api/v1/agent", tags=["agent"])

TeamCtx = Annotated[MemberContext, requires_plan("team")]


@router.post("/events", response_model=AgentEventResponse)
async def create_event(
    request: Request,
    body: AgentEventCreate,
    ctx: TeamCtx,
) -> AgentEventResponse:
    """Record a telemetry event from an agent."""
    session_factory = get_session_factory(request.app)
    return await record_event(session_factory, ctx.org_id, body)


@router.get("/events", response_model=AgentEventListResponse)
async def list_agent_events(
    request: Request,
    ctx: TeamCtx,
    limit: Annotated[int, Query(ge=1, le=100, description="Max results")] = 20,
) -> AgentEventListResponse:
    """List recent telemetry events."""
    session_factory = get_session_factory(request.app)
    return await get_events(session_factory, ctx.org_id, limit=limit)
