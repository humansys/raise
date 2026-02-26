"""Graph sync and query service — orchestrates DB operations.

Stateless: receives session_factory, returns Pydantic models.
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from rai_server.db.models import GraphNodeRow
from rai_server.db.queries import (
    prune_orphan_nodes,
    replace_edges,
    search_nodes,
    upsert_nodes,
)
from rai_server.schemas.graph import (
    GraphQueryResponse,
    GraphSyncRequest,
    GraphSyncResponse,
    NodeResult,
)


async def resolve_node_ids(
    session: AsyncSession,
    org_id: uuid.UUID,
    repo_id: str,
    node_ids: list[str],
) -> dict[str, uuid.UUID]:
    """Map domain node_ids to DB UUIDs for edge FK resolution."""
    if not node_ids:
        return {}

    result = await session.execute(
        select(GraphNodeRow.node_id, GraphNodeRow.id).where(
            GraphNodeRow.org_id == org_id,
            GraphNodeRow.repo_id == repo_id,
            GraphNodeRow.node_id.in_(node_ids),
        )
    )
    return {row.node_id: row.id for row in result}  # type: ignore[union-attr]  # SA Row attrs


async def sync_graph(
    session_factory: async_sessionmaker[AsyncSession],
    org_id: uuid.UUID,
    request: GraphSyncRequest,
) -> GraphSyncResponse:
    """Sync a full knowledge graph: upsert nodes, replace edges, prune orphans.

    All operations run in a single transaction.
    """
    repo_id = request.project_id
    node_dicts = [n.model_dump() for n in request.nodes]
    keep_node_ids = [n.node_id for n in request.nodes]

    async with session_factory() as session, session.begin():
        # 1. Upsert nodes
        upsert_result = await upsert_nodes(session, org_id, repo_id, node_dicts)

        # 2. Resolve domain node_ids → DB UUIDs for edge FKs
        edge_dicts: list[dict[str, Any]] = []
        if request.edges:
            id_map = await resolve_node_ids(session, org_id, repo_id, keep_node_ids)
            for e in request.edges:
                source_uuid = id_map.get(e.source_node_id)
                target_uuid = id_map.get(e.target_node_id)
                if source_uuid and target_uuid:
                    edge_dicts.append({
                        "source_id": source_uuid,
                        "target_id": target_uuid,
                        "edge_type": e.edge_type,
                        "weight": e.weight,
                        "properties": e.properties,
                    })

        # 3. Replace edges
        edge_result = await replace_edges(session, org_id, repo_id, edge_dicts)

        # 4. Prune orphan nodes
        pruned = await prune_orphan_nodes(session, org_id, repo_id, keep_node_ids)

    return GraphSyncResponse(
        project_id=repo_id,
        nodes_created=upsert_result["created"],
        nodes_updated=upsert_result["updated"],
        edges_created=edge_result["created"],
        nodes_pruned=pruned,
    )


async def query_graph(
    session_factory: async_sessionmaker[AsyncSession],
    org_id: uuid.UUID,
    query: str,
    limit: int = 20,
) -> GraphQueryResponse:
    """Search the knowledge graph by keyword."""
    async with session_factory() as session:
        rows = await search_nodes(session, org_id, query, limit=limit)

    results = [
        NodeResult(
            node_id=r["node_id"],
            node_type=r["node_type"],
            scope=r["scope"],
            content=r["content"],
            source_file=r["source_file"],
            properties=r["properties"],
            rank=r["rank"],
        )
        for r in rows
    ]

    return GraphQueryResponse(
        results=results,
        total=len(results),
        query=query,
        limit=limit,
    )
