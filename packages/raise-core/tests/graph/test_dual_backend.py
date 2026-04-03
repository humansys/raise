"""Tests for DualWriteBackend."""

from __future__ import annotations

import logging
from datetime import UTC
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from raise_core.graph.backends.models import BackendHealth
from raise_core.graph.backends.protocol import KnowledgeGraphBackend
from raise_core.graph.engine import Graph
from raise_core.graph.models import GraphNode


def _make_sample_graph() -> Graph:
    graph = Graph()
    graph.add_concept(
        GraphNode(
            id="PAT-001",
            type="pattern",
            content="Test pattern",
            created="2026-01-01",
        )
    )
    return graph


def _make_mock_backend(
    *, healthy: bool = True, persist_error: Exception | None = None
) -> MagicMock:
    """Create a mock KnowledgeGraphBackend."""
    mock = MagicMock(spec=KnowledgeGraphBackend)
    if persist_error:
        mock.persist.side_effect = persist_error
    mock.load.return_value = _make_sample_graph()
    status = "healthy" if healthy else "unavailable"
    mock.health.return_value = BackendHealth(
        status=status,
        message=f"Mock {status}",
        metadata={"backend": "mock"},
    )
    return mock


class TestDualWriteBackendProtocol:
    def test_implements_protocol(self) -> None:
        from raise_cli.graph.backends.dual import DualWriteBackend

        local = _make_mock_backend()
        remote = _make_mock_backend()
        backend = DualWriteBackend(local=local, remote=remote)
        assert isinstance(backend, KnowledgeGraphBackend)


class TestDualWriteBackendPersist:
    def test_persist_calls_both_backends(self) -> None:
        from raise_cli.graph.backends.dual import DualWriteBackend

        local = _make_mock_backend()
        remote = _make_mock_backend()
        backend = DualWriteBackend(local=local, remote=remote)
        graph = _make_sample_graph()

        backend.persist(graph)

        local.persist.assert_called_once_with(graph)
        remote.persist.assert_called_once_with(graph)

    def test_persist_local_first(self) -> None:
        """Local persist is called before remote."""
        from raise_cli.graph.backends.dual import DualWriteBackend

        call_order: list[str] = []
        local = _make_mock_backend()
        remote = _make_mock_backend()
        local.persist.side_effect = lambda g: call_order.append("local")
        remote.persist.side_effect = lambda g: call_order.append("remote")
        backend = DualWriteBackend(local=local, remote=remote)

        backend.persist(_make_sample_graph())

        assert call_order == ["local", "remote"]

    def test_persist_remote_failure_does_not_raise(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        from raise_cli.graph.backends.dual import DualWriteBackend

        local = _make_mock_backend()
        remote = _make_mock_backend(persist_error=ConnectionError("refused"))
        backend = DualWriteBackend(local=local, remote=remote)

        with caplog.at_level(logging.WARNING):
            backend.persist(_make_sample_graph())  # should NOT raise

        local.persist.assert_called_once()
        assert "refused" in caplog.text.lower() or "remote" in caplog.text.lower()

    def test_persist_http_error_logs_response_body(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        import httpx

        from raise_cli.graph.backends.dual import DualWriteBackend

        local = _make_mock_backend()
        remote = _make_mock_backend()
        mock_response = MagicMock()
        mock_response.status_code = 422
        mock_response.text = '{"detail":"validation error: node_id missing"}'
        remote.persist.side_effect = httpx.HTTPStatusError(
            "422", request=MagicMock(), response=mock_response
        )
        backend = DualWriteBackend(local=local, remote=remote)

        with caplog.at_level(logging.WARNING):
            backend.persist(_make_sample_graph())

        assert "validation error" in caplog.text.lower()

    def test_persist_local_failure_does_raise(self) -> None:
        """Local failure is not swallowed — it's critical."""
        from raise_cli.graph.backends.dual import DualWriteBackend

        local = _make_mock_backend(persist_error=OSError("disk full"))
        remote = _make_mock_backend()
        backend = DualWriteBackend(local=local, remote=remote)

        with pytest.raises(OSError, match="disk full"):
            backend.persist(_make_sample_graph())


class TestDualWriteBackendLoad:
    def test_load_delegates_to_local(self) -> None:
        from raise_cli.graph.backends.dual import DualWriteBackend

        local = _make_mock_backend()
        remote = _make_mock_backend()
        backend = DualWriteBackend(local=local, remote=remote)

        result = backend.load()

        local.load.assert_called_once()
        remote.load.assert_not_called()
        assert result.node_count == 1


class TestDualWriteBackendHealth:
    def test_health_both_healthy(self) -> None:
        from raise_cli.graph.backends.dual import DualWriteBackend

        local = _make_mock_backend(healthy=True)
        remote = _make_mock_backend(healthy=True)
        backend = DualWriteBackend(local=local, remote=remote)

        health = backend.health()

        assert health.status == "healthy"

    def test_health_remote_unavailable_is_degraded(self) -> None:
        from raise_cli.graph.backends.dual import DualWriteBackend

        local = _make_mock_backend(healthy=True)
        remote = _make_mock_backend(healthy=False)
        backend = DualWriteBackend(local=local, remote=remote)

        health = backend.health()

        assert health.status == "degraded"

    def test_health_local_unavailable_is_unavailable(self) -> None:
        from raise_cli.graph.backends.dual import DualWriteBackend

        local = _make_mock_backend(healthy=False)
        remote = _make_mock_backend(healthy=True)
        backend = DualWriteBackend(local=local, remote=remote)

        health = backend.health()

        assert health.status == "unavailable"

    def test_health_metadata_has_backend_dual(self) -> None:
        from raise_cli.graph.backends.dual import DualWriteBackend

        local = _make_mock_backend(healthy=True)
        remote = _make_mock_backend(healthy=True)
        backend = DualWriteBackend(local=local, remote=remote)

        health = backend.health()

        assert health.metadata["backend"] == "dual"


class TestDualWriteBackendPendingSync:
    """Pending sync marker integration with DualWriteBackend."""

    def test_remote_failure_creates_marker(self, tmp_path: Path) -> None:
        from raise_cli.graph.backends.dual import DualWriteBackend
        from raise_cli.graph.backends.pending import read_pending_marker

        raise_dir = tmp_path / ".raise"
        raise_dir.mkdir()
        local = _make_mock_backend()
        remote = _make_mock_backend(persist_error=ConnectionError("refused"))
        backend = DualWriteBackend(local=local, remote=remote, raise_dir=raise_dir)

        backend.persist(_make_sample_graph())

        marker = read_pending_marker(raise_dir)
        assert marker is not None
        assert marker.error == "refused"
        assert marker.node_count == 1
        assert marker.edge_count == 0

    def test_remote_success_clears_existing_marker(self, tmp_path: Path) -> None:
        from raise_cli.graph.backends.dual import DualWriteBackend
        from raise_cli.graph.backends.pending import (
            PendingSyncMarker,
            read_pending_marker,
            write_pending_marker,
        )

        raise_dir = tmp_path / ".raise"
        raise_dir.mkdir()
        # Pre-existing marker from previous failure
        from datetime import datetime

        write_pending_marker(
            raise_dir,
            PendingSyncMarker(
                timestamp=datetime(2026, 1, 1, tzinfo=UTC),
                graph_path="old",
                node_count=1,
                edge_count=0,
                error="old",
            ),
        )
        local = _make_mock_backend()
        remote = _make_mock_backend()  # succeeds
        backend = DualWriteBackend(local=local, remote=remote, raise_dir=raise_dir)

        backend.persist(_make_sample_graph())

        assert read_pending_marker(raise_dir) is None

    def test_remote_success_no_marker_is_noop(self, tmp_path: Path) -> None:
        from raise_cli.graph.backends.dual import DualWriteBackend
        from raise_cli.graph.backends.pending import read_pending_marker

        raise_dir = tmp_path / ".raise"
        raise_dir.mkdir()
        local = _make_mock_backend()
        remote = _make_mock_backend()
        backend = DualWriteBackend(local=local, remote=remote, raise_dir=raise_dir)

        backend.persist(_make_sample_graph())

        assert read_pending_marker(raise_dir) is None

    def test_no_raise_dir_skips_marker(self) -> None:
        """When raise_dir is None, marker behavior is skipped entirely."""
        from raise_cli.graph.backends.dual import DualWriteBackend

        local = _make_mock_backend()
        remote = _make_mock_backend(persist_error=ConnectionError("refused"))
        backend = DualWriteBackend(local=local, remote=remote)

        backend.persist(_make_sample_graph())  # should not raise
