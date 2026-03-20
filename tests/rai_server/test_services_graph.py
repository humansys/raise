"""Tests for graph service layer.

Service functions orchestrate DB queries and domain logic.
DB functions are mocked — service tests verify orchestration, not SQL.
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from raise_server.schemas.graph import EdgeInput, GraphSyncRequest, NodeInput
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


def _mock_session_factory() -> async_sessionmaker[AsyncSession]:
    """Create a mock session factory whose __call__ returns an async CM yielding a session."""
    session = AsyncMock(spec=AsyncSession)

    # session.begin() must return an async CM
    begin_cm = AsyncMock()
    begin_cm.__aenter__ = AsyncMock(return_value=None)
    begin_cm.__aexit__ = AsyncMock(return_value=None)
    session.begin.return_value = begin_cm

    @asynccontextmanager
    async def _session_cm() -> AsyncGenerator[AsyncSession, None]:
        yield session

    factory = MagicMock(spec=async_sessionmaker)
    factory.return_value = _session_cm()
    # Make each call return a fresh CM
    factory.side_effect = lambda: _session_cm()
    return factory  # type: ignore[return-value]


@pytest.fixture
def org_id() -> uuid.UUID:
    return uuid.UUID("00000000-0000-0000-0000-000000000001")


@pytest.fixture
def sync_request() -> GraphSyncRequest:
    return GraphSyncRequest(
        project_id="raise-commons",
        nodes=[
            NodeInput(node_id="mod-a", node_type="module", content="Module A"),
            NodeInput(node_id="mod-b", node_type="module", content="Module B"),
        ],
        edges=[
            EdgeInput(
                source_node_id="mod-a", target_node_id="mod-b", edge_type="depends_on"
            ),
        ],
    )


class TestSyncGraph:
    """sync_graph orchestrates upsert, edge replace, and orphan pruning."""

    @pytest.mark.anyio
    async def test_calls_all_db_operations(
        self, org_id: uuid.UUID, sync_request: GraphSyncRequest
    ) -> None:
        from raise_server.services.graph import sync_graph

        factory = _mock_session_factory()

        with (
            patch(
                "raise_server.services.graph.upsert_nodes", new_callable=AsyncMock
            ) as mock_upsert,
            patch(
                "raise_server.services.graph.replace_edges", new_callable=AsyncMock
            ) as mock_replace,
            patch(
                "raise_server.services.graph.prune_orphan_nodes", new_callable=AsyncMock
            ) as mock_prune,
            patch(
                "raise_server.services.graph.resolve_node_ids", new_callable=AsyncMock
            ) as mock_resolve,
        ):
            mock_upsert.return_value = {"created": 2, "updated": 0}
            mock_resolve.return_value = {
                "mod-a": uuid.uuid4(),
                "mod-b": uuid.uuid4(),
            }
            mock_replace.return_value = {"created": 1}
            mock_prune.return_value = 0

            result = await sync_graph(factory, org_id, sync_request)

            mock_upsert.assert_called_once()
            mock_replace.assert_called_once()
            mock_prune.assert_called_once()
            assert result.nodes_upserted == 2
            assert result.edges_created == 1
            assert result.edges_skipped == 0
            assert result.nodes_pruned == 0
            assert result.project_id == "raise-commons"

    @pytest.mark.anyio
    async def test_empty_graph_sync(self, org_id: uuid.UUID) -> None:
        from raise_server.services.graph import sync_graph

        factory = _mock_session_factory()
        empty_request = GraphSyncRequest(project_id="empty", nodes=[], edges=[])

        with (
            patch(
                "raise_server.services.graph.upsert_nodes", new_callable=AsyncMock
            ) as mock_upsert,
            patch(
                "raise_server.services.graph.replace_edges", new_callable=AsyncMock
            ) as mock_replace,
            patch(
                "raise_server.services.graph.prune_orphan_nodes", new_callable=AsyncMock
            ) as mock_prune,
        ):
            mock_upsert.return_value = {"created": 0, "updated": 0}
            mock_replace.return_value = {"created": 0}
            mock_prune.return_value = 0

            result = await sync_graph(factory, org_id, empty_request)
            assert result.nodes_upserted == 0
            assert result.edges_created == 0
            assert result.edges_skipped == 0

    @pytest.mark.anyio
    async def test_edges_skipped_when_node_missing(self, org_id: uuid.UUID) -> None:
        """Edges referencing nodes not in the payload are skipped, not silently lost."""
        from raise_server.services.graph import sync_graph

        factory = _mock_session_factory()
        request = GraphSyncRequest(
            project_id="test",
            nodes=[NodeInput(node_id="mod-a", node_type="module", content="A")],
            edges=[
                EdgeInput(
                    source_node_id="mod-a",
                    target_node_id="mod-MISSING",
                    edge_type="depends_on",
                ),
            ],
        )

        with (
            patch(
                "raise_server.services.graph.upsert_nodes", new_callable=AsyncMock
            ) as mock_upsert,
            patch(
                "raise_server.services.graph.replace_edges", new_callable=AsyncMock
            ) as mock_replace,
            patch(
                "raise_server.services.graph.prune_orphan_nodes", new_callable=AsyncMock
            ) as mock_prune,
            patch(
                "raise_server.services.graph.resolve_node_ids", new_callable=AsyncMock
            ) as mock_resolve,
        ):
            mock_upsert.return_value = {"created": 1, "updated": 0}
            # Only mod-a resolved, mod-MISSING not found
            mock_resolve.return_value = {"mod-a": uuid.uuid4()}
            mock_replace.return_value = {"created": 0}
            mock_prune.return_value = 0

            result = await sync_graph(factory, org_id, request)
            assert result.edges_skipped == 1
            assert result.edges_created == 0


class TestQueryGraph:
    """query_graph delegates to search_nodes and wraps results."""

    @pytest.mark.anyio
    async def test_returns_query_response(self, org_id: uuid.UUID) -> None:
        from raise_server.services.graph import query_graph

        factory = _mock_session_factory()

        with patch(
            "raise_server.services.graph.search_nodes", new_callable=AsyncMock
        ) as mock_search:
            mock_search.return_value = [
                {
                    "node_id": "mod-memory",
                    "node_type": "module",
                    "scope": "project",
                    "content": "Memory management",
                    "source_file": "src/memory.py",
                    "properties": {},
                    "rank": 0.075,
                },
            ]

            result = await query_graph(factory, org_id, "memory", limit=10)
            assert result.total == 1
            assert result.results[0].node_id == "mod-memory"
            assert result.results[0].rank == 0.075
            assert result.query == "memory"
            assert result.limit == 10

    @pytest.mark.anyio
    async def test_empty_results(self, org_id: uuid.UUID) -> None:
        from raise_server.services.graph import query_graph

        factory = _mock_session_factory()

        with patch(
            "raise_server.services.graph.search_nodes", new_callable=AsyncMock
        ) as mock_search:
            mock_search.return_value = []

            result = await query_graph(factory, org_id, "nonexistent", limit=20)
            assert result.total == 0
            assert result.results == []
