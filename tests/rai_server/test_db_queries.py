"""Tests for graph DB query functions.

These tests mock AsyncSession to verify SQL construction without a real DB.
For integration tests with a real DB, see T5.
"""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession


def _mock_session() -> AsyncSession:
    """Create a mock AsyncSession with execute support."""
    session = AsyncMock(spec=AsyncSession)
    session.execute = AsyncMock()
    return session


@pytest.fixture
def org_id() -> uuid.UUID:
    return uuid.UUID("00000000-0000-0000-0000-000000000001")


@pytest.fixture
def repo_id() -> str:
    return "raise-commons"


class TestUpsertNodes:
    """upsert_nodes inserts new nodes and updates existing via ON CONFLICT."""

    @pytest.mark.anyio
    async def test_returns_created_and_updated_counts(
        self, org_id: uuid.UUID, repo_id: str
    ) -> None:
        from raise_server.db.queries import upsert_nodes

        session = _mock_session()
        # Simulate: execute returns result with rowcount
        mock_result = MagicMock()
        mock_result.rowcount = 2
        session.execute.return_value = mock_result

        nodes = [
            {
                "node_id": "mod-a",
                "node_type": "module",
                "scope": "project",
                "content": "A",
                "source_file": None,
                "properties": {},
            },
            {
                "node_id": "mod-b",
                "node_type": "module",
                "scope": "project",
                "content": "B",
                "source_file": "b.py",
                "properties": {"lang": "py"},
            },
        ]
        result = await upsert_nodes(session, org_id, repo_id, nodes)
        assert session.execute.called
        assert "created" in result
        assert "updated" in result
        assert result["created"] + result["updated"] == 2

    @pytest.mark.anyio
    async def test_empty_nodes_is_noop(self, org_id: uuid.UUID, repo_id: str) -> None:
        from raise_server.db.queries import upsert_nodes

        session = _mock_session()
        result = await upsert_nodes(session, org_id, repo_id, [])
        assert result == {"created": 0, "updated": 0}
        session.execute.assert_not_called()


class TestReplaceEdges:
    """replace_edges deletes old edges and inserts new ones for (org, repo)."""

    @pytest.mark.anyio
    async def test_deletes_then_inserts(self, org_id: uuid.UUID, repo_id: str) -> None:
        from raise_server.db.queries import replace_edges

        session = _mock_session()
        # First execute = delete, second = insert
        delete_result = MagicMock()
        delete_result.rowcount = 3
        insert_result = MagicMock()
        insert_result.rowcount = 2
        session.execute.side_effect = [delete_result, insert_result]

        node_a_id = uuid.uuid4()
        node_b_id = uuid.uuid4()
        edges = [
            {
                "source_id": node_a_id,
                "target_id": node_b_id,
                "edge_type": "depends_on",
                "weight": 1.0,
                "properties": {},
            },
            {
                "source_id": node_b_id,
                "target_id": node_a_id,
                "edge_type": "contains",
                "weight": 0.5,
                "properties": {},
            },
        ]
        result = await replace_edges(session, org_id, repo_id, edges)
        assert session.execute.call_count == 2  # delete + insert
        assert result["created"] == 2

    @pytest.mark.anyio
    async def test_empty_edges_still_deletes_old(
        self, org_id: uuid.UUID, repo_id: str
    ) -> None:
        from raise_server.db.queries import replace_edges

        session = _mock_session()
        delete_result = MagicMock()
        delete_result.rowcount = 0
        session.execute.return_value = delete_result

        result = await replace_edges(session, org_id, repo_id, [])
        assert session.execute.call_count == 1  # only delete
        assert result["created"] == 0


class TestPruneOrphanNodes:
    """prune_orphan_nodes deletes nodes not in the incoming set."""

    @pytest.mark.anyio
    async def test_deletes_nodes_not_in_keep_set(
        self, org_id: uuid.UUID, repo_id: str
    ) -> None:
        from raise_server.db.queries import prune_orphan_nodes

        session = _mock_session()
        mock_result = MagicMock()
        mock_result.rowcount = 3
        session.execute.return_value = mock_result

        keep_node_ids = ["mod-a", "mod-b"]
        pruned = await prune_orphan_nodes(session, org_id, repo_id, keep_node_ids)
        assert pruned == 3
        session.execute.assert_called_once()

    @pytest.mark.anyio
    async def test_empty_keep_set_deletes_all(
        self, org_id: uuid.UUID, repo_id: str
    ) -> None:
        from raise_server.db.queries import prune_orphan_nodes

        session = _mock_session()
        mock_result = MagicMock()
        mock_result.rowcount = 5
        session.execute.return_value = mock_result

        pruned = await prune_orphan_nodes(session, org_id, repo_id, [])
        assert pruned == 5


class TestSearchNodes:
    """search_nodes queries nodes using full-text search, scoped to org."""

    @pytest.mark.anyio
    async def test_returns_matching_nodes(self, org_id: uuid.UUID) -> None:
        from raise_server.db.queries import search_nodes

        session = _mock_session()
        # Simulate rows returned
        mock_row = MagicMock()
        mock_row._mapping = {
            "node_id": "mod-memory",
            "node_type": "module",
            "scope": "project",
            "content": "Memory management",
            "source_file": "src/memory.py",
            "properties": {"lang": "py"},
            "rank": 0.075,
        }
        mock_result = MagicMock()
        mock_result.mappings.return_value.all.return_value = [mock_row._mapping]
        session.execute.return_value = mock_result

        results = await search_nodes(session, org_id, "memory", limit=10)
        assert len(results) == 1
        assert results[0]["node_id"] == "mod-memory"
        assert results[0]["rank"] == 0.075

    @pytest.mark.anyio
    async def test_respects_limit(self, org_id: uuid.UUID) -> None:
        from raise_server.db.queries import search_nodes

        session = _mock_session()
        mock_result = MagicMock()
        mock_result.mappings.return_value.all.return_value = []
        session.execute.return_value = mock_result

        await search_nodes(session, org_id, "test", limit=5)
        # Verify the SQL statement includes a LIMIT clause
        call_args = session.execute.call_args
        stmt = call_args[0][0]
        compiled = str(stmt.compile())
        assert "LIMIT" in compiled.upper()
        # Verify limit value is bound as parameter
        params = stmt.compile().params
        assert params.get("param_1") == 5 or any(v == 5 for v in params.values())
