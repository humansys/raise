"""Tests for graph API routes — POST /api/v1/graph/sync, GET /api/v1/graph/query."""

from __future__ import annotations

import uuid
from collections.abc import Generator
from contextlib import contextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from raise_server.app import create_app
from raise_server.config import ServerConfig
from raise_server.schemas.graph import GraphQueryResponse, GraphSyncResponse, NodeResult

_DB_URL = "postgresql+asyncpg://u:p@h/db"
_ORG_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
_ORG_NAME = "acme"


@contextmanager
def _override_auth(client: TestClient) -> Generator[None, None, None]:
    """Override verify_member dependency to return a valid MemberContext."""
    from raise_server.auth import MemberContext, verify_member

    async def _fake_auth() -> MemberContext:
        return MemberContext(
            org_id=_ORG_ID,
            org_name=_ORG_NAME,
            member_id=_ORG_ID,
            email="test@example.com",
            role="admin",
            plan="team",
            features=[],
        )

    client.app.dependency_overrides[verify_member] = _fake_auth  # type: ignore[union-attr]
    try:
        yield
    finally:
        client.app.dependency_overrides.clear()  # type: ignore[union-attr]


@pytest.fixture
def client() -> TestClient:
    """Create test client with graph routes and mocked session factory."""
    config = ServerConfig(database_url=_DB_URL)
    app = create_app(config=config)
    app.state.session_factory = MagicMock()
    return TestClient(app)


class TestSyncEndpoint:
    """POST /api/v1/graph/sync upserts graph data."""

    def test_sync_returns_200_with_counts(self, client: TestClient) -> None:
        mock_response = GraphSyncResponse(
            project_id="raise-commons",
            nodes_upserted=5,
            edges_created=3,
            edges_skipped=0,
            nodes_pruned=1,
        )
        with (
            _override_auth(client),
            patch(
                "raise_server.api.v1.graph.sync_graph",
                new_callable=AsyncMock,
                return_value=mock_response,
            ),
        ):
            resp = client.post(
                "/api/v1/graph/sync",
                json={
                    "project_id": "raise-commons",
                    "nodes": [
                        {"node_id": "mod-a", "node_type": "module", "content": "A"}
                    ],
                    "edges": [],
                },
            )
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"
        assert body["nodes_upserted"] == 5
        assert body["edges_created"] == 3
        assert body["edges_skipped"] == 0
        assert body["nodes_pruned"] == 1

    def test_sync_requires_auth(self, client: TestClient) -> None:
        resp = client.post(
            "/api/v1/graph/sync",
            json={"project_id": "x", "nodes": [], "edges": []},
        )
        assert resp.status_code == 401

    def test_sync_invalid_payload_returns_422(self, client: TestClient) -> None:
        with _override_auth(client):
            resp = client.post(
                "/api/v1/graph/sync",
                json={"nodes": [], "edges": []},  # missing project_id
            )
        assert resp.status_code == 422

    def test_sync_empty_project_id_returns_422(self, client: TestClient) -> None:
        with _override_auth(client):
            resp = client.post(
                "/api/v1/graph/sync",
                json={"project_id": "", "nodes": [], "edges": []},
            )
        assert resp.status_code == 422


class TestQueryEndpoint:
    """GET /api/v1/graph/query searches the knowledge graph."""

    def test_query_returns_200_with_results(self, client: TestClient) -> None:
        mock_response = GraphQueryResponse(
            results=[
                NodeResult(
                    node_id="mod-memory",
                    node_type="module",
                    scope="project",
                    content="Memory management",
                    source_file="src/memory.py",
                    properties={},
                    rank=0.075,
                ),
            ],
            total=1,
            query="memory",
            limit=10,
        )
        with (
            _override_auth(client),
            patch(
                "raise_server.api.v1.graph.query_graph",
                new_callable=AsyncMock,
                return_value=mock_response,
            ),
        ):
            resp = client.get("/api/v1/graph/query?q=memory&limit=10")
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 1
        assert body["results"][0]["node_id"] == "mod-memory"

    def test_query_requires_auth(self, client: TestClient) -> None:
        resp = client.get("/api/v1/graph/query?q=test")
        assert resp.status_code == 401

    def test_query_without_q_returns_422(self, client: TestClient) -> None:
        with _override_auth(client):
            resp = client.get("/api/v1/graph/query")
        assert resp.status_code == 422

    def test_query_empty_results(self, client: TestClient) -> None:
        mock_response = GraphQueryResponse(
            results=[], total=0, query="nonexistent", limit=20
        )
        with (
            _override_auth(client),
            patch(
                "raise_server.api.v1.graph.query_graph",
                new_callable=AsyncMock,
                return_value=mock_response,
            ),
        ):
            resp = client.get("/api/v1/graph/query?q=nonexistent")
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 0
        assert body["results"] == []

    def test_query_limit_over_100_returns_422(self, client: TestClient) -> None:
        """Limit > 100 is rejected by FastAPI Query(le=100)."""
        with _override_auth(client):
            resp = client.get("/api/v1/graph/query?q=test&limit=200")
        assert resp.status_code == 422
