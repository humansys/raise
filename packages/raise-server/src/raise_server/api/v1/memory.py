"""Memory pattern API routes.

Thin handlers — validate input, delegate to service, return response.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request

from rai_server.auth import OrgContext, verify_api_key
from rai_server.deps import get_session_factory
from rai_server.schemas.memory import (
    MemoryPatternCreate,
    MemoryPatternListResponse,
    MemoryPatternResponse,
)
from rai_server.services.memory import add_pattern, get_patterns

router = APIRouter(prefix="/api/v1/memory", tags=["memory"])

AuthCtx = Annotated[OrgContext, Depends(verify_api_key)]


@router.post("/patterns", response_model=MemoryPatternResponse)
async def create_pattern(
    request: Request,
    body: MemoryPatternCreate,
    ctx: AuthCtx,
) -> MemoryPatternResponse:
    """Add a learned pattern from an agent."""
    session_factory = get_session_factory(request.app)
    return await add_pattern(session_factory, ctx.org_id, body)


@router.get("/patterns", response_model=MemoryPatternListResponse)
async def list_memory_patterns(
    request: Request,
    ctx: AuthCtx,
    limit: Annotated[int, Query(ge=1, le=100, description="Max results")] = 50,
) -> MemoryPatternListResponse:
    """List memory patterns for the org."""
    session_factory = get_session_factory(request.app)
    return await get_patterns(session_factory, ctx.org_id, limit=limit)
