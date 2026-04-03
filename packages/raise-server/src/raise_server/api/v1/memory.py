"""Memory pattern API routes.

Thin handlers — validate input, delegate to service, return response.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query, Request

from raise_server.auth import MemberContext, requires_plan
from raise_server.deps import get_session_factory
from raise_server.schemas.memory import (
    MemoryPatternCreate,
    MemoryPatternListResponse,
    MemoryPatternResponse,
)
from raise_server.services.memory import add_pattern, get_patterns

router = APIRouter(prefix="/api/v1/memory", tags=["memory"])

TeamCtx = Annotated[MemberContext, requires_plan("team")]


@router.post("/patterns", response_model=MemoryPatternResponse)
async def create_pattern(
    request: Request,
    body: MemoryPatternCreate,
    ctx: TeamCtx,
) -> MemoryPatternResponse:
    """Add a learned pattern from an agent."""
    session_factory = get_session_factory(request.app)
    return await add_pattern(session_factory, ctx.org_id, body)


@router.get("/patterns", response_model=MemoryPatternListResponse)
async def list_memory_patterns(
    request: Request,
    ctx: TeamCtx,
    limit: Annotated[int, Query(ge=1, le=100, description="Max results")] = 50,
) -> MemoryPatternListResponse:
    """List memory patterns for the org."""
    session_factory = get_session_factory(request.app)
    return await get_patterns(session_factory, ctx.org_id, limit=limit)
