"""Agent telemetry API routes.

Thin handlers — validate input, delegate to service, return response.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request

from rai_server.auth import OrgContext, verify_api_key
from rai_server.deps import get_session_factory
from rai_server.schemas.agent import (
    AgentEventCreate,
    AgentEventListResponse,
    AgentEventResponse,
)
from rai_server.services.agent import get_events, record_event

router = APIRouter(prefix="/api/v1/agent", tags=["agent"])

AuthCtx = Annotated[OrgContext, Depends(verify_api_key)]


@router.post("/events", response_model=AgentEventResponse)
async def create_event(
    request: Request,
    body: AgentEventCreate,
    ctx: AuthCtx,
) -> AgentEventResponse:
    """Record a telemetry event from an agent."""
    session_factory = get_session_factory(request.app)
    return await record_event(session_factory, ctx.org_id, body)


@router.get("/events", response_model=AgentEventListResponse)
async def list_agent_events(
    request: Request,
    ctx: AuthCtx,
    limit: Annotated[int, Query(ge=1, le=100, description="Max results")] = 20,
) -> AgentEventListResponse:
    """List recent telemetry events."""
    session_factory = get_session_factory(request.app)
    return await get_events(session_factory, ctx.org_id, limit=limit)
