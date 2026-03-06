"""Graph sync and query API routes.

Thin handlers — validate input, delegate to service, return response.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request

from raise_server.auth import OrgContext, verify_api_key
from raise_server.deps import get_session_factory
from raise_server.schemas.graph import (
    GraphQueryResponse,
    GraphSyncRequest,
    GraphSyncResponse,
)
from raise_server.services.graph import query_graph, sync_graph

router = APIRouter(prefix="/api/v1/graph", tags=["graph"])

AuthCtx = Annotated[OrgContext, Depends(verify_api_key)]


@router.post("/sync", response_model=GraphSyncResponse)
async def graph_sync(
    request: Request,
    body: GraphSyncRequest,
    ctx: AuthCtx,
) -> GraphSyncResponse:
    """Sync a full knowledge graph for a project (idempotent upsert)."""
    session_factory = get_session_factory(request.app)
    return await sync_graph(session_factory, ctx.org_id, body)


@router.get("/query", response_model=GraphQueryResponse)
async def graph_query(
    request: Request,
    ctx: AuthCtx,
    q: Annotated[str, Query(min_length=1, description="Search keyword")],
    limit: Annotated[int, Query(ge=1, le=100, description="Max results")] = 20,
) -> GraphQueryResponse:
    """Search the knowledge graph by keyword."""
    session_factory = get_session_factory(request.app)
    return await query_graph(session_factory, ctx.org_id, q, limit=limit)
