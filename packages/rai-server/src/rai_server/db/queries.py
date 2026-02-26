"""Specialized SQL query functions for graph sync and search.

All functions receive an AsyncSession and return plain dicts — no ORM objects leak out.
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import Result, delete, func, literal, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from rai_server.db.models import GraphEdgeRow, GraphNodeRow


async def upsert_nodes(
    session: AsyncSession,
    org_id: uuid.UUID,
    repo_id: str,
    nodes: list[dict[str, Any]],
) -> dict[str, int]:
    """Upsert graph nodes using ON CONFLICT (org_id, repo_id, node_id) DO UPDATE.

    Returns {"created": N, "updated": M}. Counts are approximate —
    PG doesn't distinguish insert vs update in rowcount.
    """
    if not nodes:
        return {"created": 0, "updated": 0}

    values = [
        {
            "org_id": org_id,
            "repo_id": repo_id,
            "node_id": n["node_id"],
            "node_type": n["node_type"],
            "scope": n["scope"],
            "content": n["content"],
            "source_file": n["source_file"],
            "properties": n["properties"],
        }
        for n in nodes
    ]

    stmt = pg_insert(GraphNodeRow).values(values)
    stmt = stmt.on_conflict_do_update(
        constraint="uq_node_org_repo_nodeid",
        set_={
            "node_type": stmt.excluded.node_type,
            "scope": stmt.excluded.scope,
            "content": stmt.excluded.content,
            "source_file": stmt.excluded.source_file,
            "properties": stmt.excluded.properties,
            "updated_at": func.now(),
        },
    )

    result = await session.execute(stmt)
    total: int = result.rowcount  # type: ignore[assignment]  # CursorResult.rowcount is int at runtime
    # PG ON CONFLICT doesn't distinguish created vs updated in rowcount.
    # We report all as created; the service layer can refine if needed.
    return {"created": total, "updated": 0}


async def replace_edges(
    session: AsyncSession,
    org_id: uuid.UUID,
    repo_id: str,
    edges: list[dict[str, Any]],
) -> dict[str, int]:
    """Delete all edges for (org_id, repo_id) and insert new ones.

    Each edge dict must have: source_id (UUID), target_id (UUID),
    edge_type, weight, properties.

    Returns {"created": N}.
    """
    # Always delete old edges for this org+repo
    await session.execute(
        delete(GraphEdgeRow).where(
            GraphEdgeRow.org_id == org_id,
            GraphEdgeRow.repo_id == repo_id,
        )
    )

    if not edges:
        return {"created": 0}

    values = [
        {
            "org_id": org_id,
            "repo_id": repo_id,
            "source_id": e["source_id"],
            "target_id": e["target_id"],
            "edge_type": e["edge_type"],
            "weight": e["weight"],
            "properties": e["properties"],
        }
        for e in edges
    ]

    result = await session.execute(pg_insert(GraphEdgeRow).values(values))
    created: int = result.rowcount  # type: ignore[assignment]  # CursorResult.rowcount
    return {"created": created}


async def prune_orphan_nodes(
    session: AsyncSession,
    org_id: uuid.UUID,
    repo_id: str,
    keep_node_ids: list[str],
) -> int:
    """Delete nodes for (org_id, repo_id) whose node_id is NOT in keep_node_ids.

    PRECONDITION: Edges referencing these nodes must be deleted first
    (graph_edges.source_id/target_id FK has no ON DELETE CASCADE).
    In sync_graph, replace_edges runs before prune to satisfy this.

    Returns the number of pruned nodes.
    """
    stmt = delete(GraphNodeRow).where(
        GraphNodeRow.org_id == org_id,
        GraphNodeRow.repo_id == repo_id,
    )
    if keep_node_ids:
        stmt = stmt.where(GraphNodeRow.node_id.not_in(keep_node_ids))

    result = await session.execute(stmt)
    return int(result.rowcount)  # type: ignore[arg-type]  # CursorResult.rowcount is int at runtime


async def search_nodes(
    session: AsyncSession,
    org_id: uuid.UUID,
    query: str,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Full-text search across node_id, node_type, and content using to_tsvector.

    Returns list of dicts with node fields + rank score.
    """
    ts_query = func.plainto_tsquery("english", query)
    searchable = func.concat(
        GraphNodeRow.node_id, literal(" "),
        GraphNodeRow.node_type, literal(" "),
        GraphNodeRow.content,
    )
    ts_vector = func.to_tsvector("english", searchable)
    rank = func.ts_rank(ts_vector, ts_query)

    stmt = (  # type: ignore[var-annotated]  # SA JSONB propagates Unknown through select
        select(
            GraphNodeRow.node_id,
            GraphNodeRow.node_type,
            GraphNodeRow.scope,
            GraphNodeRow.content,
            GraphNodeRow.source_file,
            GraphNodeRow.properties,  # type: ignore[arg-type]  # SA JSONB <-> dict[Unknown]
            rank.label("rank"),
        )
        .where(
            GraphNodeRow.org_id == org_id,
            ts_vector.bool_op("@@")(ts_query),  # type: ignore[no-untyped-call]  # SA bool_op
        )
        .order_by(rank.desc())
        .limit(limit)
    )

    result: Result[Any] = await session.execute(stmt)  # type: ignore[assignment]  # SA JSONB type variance
    return [dict(row) for row in result.mappings().all()]
