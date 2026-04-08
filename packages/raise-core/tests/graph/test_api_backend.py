"""Tests for ApiGraphBackend."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import httpx
import pytest

from raise_core.graph.backends.models import BackendHealth
from raise_core.graph.backends.protocol import KnowledgeGraphBackend
from raise_core.graph.engine import Graph
from raise_core.graph.models import GraphEdge, GraphNode


def _make_sample_graph() -> Graph:
    """Create a graph with nodes and edges for testing."""
    graph = Graph()
    graph.add_concept(
        GraphNode(
            id="PAT-001",
            type="pattern",
            content="Test pattern",
            created="2026-01-01",
            source_file="test.py",
            metadata={"confidence": 0.9},
        )
    )
    graph.add_concept(
        GraphNode(
            id="SES-001",
            type="session",
            content="Test session",
            created="2026-01-02",
        )
    )
    graph.add_relationship(
        GraphEdge(
            source="PAT-001",
            target="SES-001",
            type="learned_from",
            weight=1.0,
        )
    )
    return graph


class TestApiGraphBackendProtocol:
    """ApiGraphBackend implements KnowledgeGraphBackend protocol."""

    def test_implements_protocol(self) -> None:
        from raise_cli.graph.backends.api import ApiGraphBackend

        backend = ApiGraphBackend(
            server_url="http://localhost:8000",
            api_key="rsk_test_abc",
            project_id="test-project",
        )
        assert isinstance(backend, KnowledgeGraphBackend)


class TestApiGraphBackendPersist:
    """persist() sends correct GraphSyncRequest to server."""

    def test_persist_sends_post_to_sync_endpoint(self) -> None:
        from raise_cli.graph.backends.api import ApiGraphBackend

        backend = ApiGraphBackend(
            server_url="http://localhost:8000",
            api_key="rsk_test_abc",
            project_id="test-project",
        )
        graph = _make_sample_graph()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()

        with patch.object(
            backend._client, "post", return_value=mock_response
        ) as mock_post:
            backend.persist(graph)

            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert call_args.kwargs["url"] == "/api/v1/graph/sync"

    def test_persist_sends_correct_payload(self) -> None:
        from raise_cli.graph.backends.api import ApiGraphBackend

        backend = ApiGraphBackend(
            server_url="http://localhost:8000",
            api_key="rsk_test_abc",
            project_id="test-project",
        )
        graph = _make_sample_graph()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()

        with patch.object(
            backend._client, "post", return_value=mock_response
        ) as mock_post:
            backend.persist(graph)

            payload = mock_post.call_args.kwargs["json"]
            assert payload["project_id"] == "test-project"
            assert len(payload["nodes"]) == 2
            assert len(payload["edges"]) == 1

            # Check node structure
            node_ids = {n["node_id"] for n in payload["nodes"]}
            assert node_ids == {"PAT-001", "SES-001"}

            pat_node = next(n for n in payload["nodes"] if n["node_id"] == "PAT-001")
            assert pat_node["node_type"] == "pattern"
            assert pat_node["content"] == "Test pattern"
            assert pat_node["source_file"] == "test.py"
            assert pat_node["properties"] == {"confidence": 0.9}

            # Check edge structure
            edge = payload["edges"][0]
            assert edge["source_node_id"] == "PAT-001"
            assert edge["target_node_id"] == "SES-001"
            assert edge["edge_type"] == "learned_from"
            assert edge["weight"] == 1.0

    def test_persist_includes_auth_header(self) -> None:
        from raise_cli.graph.backends.api import ApiGraphBackend

        backend = ApiGraphBackend(
            server_url="http://localhost:8000",
            api_key="rsk_test_abc",
            project_id="test-project",
        )

        # Check that the client has the auth header
        assert backend._client.headers["authorization"] == "Bearer rsk_test_abc"


class TestApiGraphBackendHealth:
    """health() returns status based on server availability."""

    def test_health_returns_healthy_when_server_responds(self) -> None:
        from raise_cli.graph.backends.api import ApiGraphBackend

        backend = ApiGraphBackend(
            server_url="http://localhost:8000",
            api_key="rsk_test_abc",
            project_id="test-project",
        )

        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch.object(backend._client, "get", return_value=mock_response):
            health = backend.health()

        assert isinstance(health, BackendHealth)
        assert health.status == "healthy"
        assert health.metadata["backend"] == "api"

    def test_health_returns_unavailable_on_connection_error(self) -> None:
        from raise_cli.graph.backends.api import ApiGraphBackend

        backend = ApiGraphBackend(
            server_url="http://localhost:8000",
            api_key="rsk_test_abc",
            project_id="test-project",
        )

        with patch.object(
            backend._client, "get", side_effect=httpx.ConnectError("refused")
        ):
            health = backend.health()

        assert health.status == "unavailable"
        assert (
            "refused" in health.message.lower() or "connect" in health.message.lower()
        )

    def test_health_returns_unavailable_on_timeout(self) -> None:
        from raise_cli.graph.backends.api import ApiGraphBackend

        backend = ApiGraphBackend(
            server_url="http://localhost:8000",
            api_key="rsk_test_abc",
            project_id="test-project",
        )

        with patch.object(
            backend._client, "get", side_effect=httpx.TimeoutException("timeout")
        ):
            health = backend.health()

        assert health.status == "unavailable"

    def test_health_returns_unavailable_on_read_error(self) -> None:
        from raise_cli.graph.backends.api import ApiGraphBackend

        backend = ApiGraphBackend(
            server_url="http://localhost:8000",
            api_key="rsk_test_abc",
            project_id="test-project",
        )

        with patch.object(
            backend._client, "get", side_effect=httpx.ReadError("connection reset")
        ):
            health = backend.health()

        assert health.status == "unavailable"


class TestApiGraphBackendLoad:
    """load() raises NotImplementedError."""

    def test_load_raises_not_implemented(self) -> None:
        from raise_cli.graph.backends.api import ApiGraphBackend

        backend = ApiGraphBackend(
            server_url="http://localhost:8000",
            api_key="rsk_test_abc",
            project_id="test-project",
        )

        with pytest.raises(NotImplementedError, match="local"):
            backend.load()


class TestApiGraphBackendTimeout:
    """Client has appropriate timeout configuration."""

    def test_client_has_timeout(self) -> None:
        from raise_cli.graph.backends.api import ApiGraphBackend

        backend = ApiGraphBackend(
            server_url="http://localhost:8000",
            api_key="rsk_test_abc",
            project_id="test-project",
        )

        assert backend._client.timeout.connect == 5.0
        assert backend._client.timeout.read == 30.0
