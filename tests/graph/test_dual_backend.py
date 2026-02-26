"""Tests for DualWriteBackend."""

from __future__ import annotations

import logging
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from rai_core.graph.backends.models import BackendHealth
from rai_core.graph.backends.protocol import KnowledgeGraphBackend
from rai_core.graph.engine import Graph
from rai_core.graph.models import GraphNode


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
        from rai_cli.graph.backends.dual import DualWriteBackend

        local = _make_mock_backend()
        remote = _make_mock_backend()
        backend = DualWriteBackend(local=local, remote=remote)
        assert isinstance(backend, KnowledgeGraphBackend)


class TestDualWriteBackendPersist:
    def test_persist_calls_both_backends(self) -> None:
        from rai_cli.graph.backends.dual import DualWriteBackend

        local = _make_mock_backend()
        remote = _make_mock_backend()
        backend = DualWriteBackend(local=local, remote=remote)
        graph = _make_sample_graph()

        backend.persist(graph)

        local.persist.assert_called_once_with(graph)
        remote.persist.assert_called_once_with(graph)

    def test_persist_local_first(self) -> None:
        """Local persist is called before remote."""
        from rai_cli.graph.backends.dual import DualWriteBackend

        call_order: list[str] = []
        local = _make_mock_backend()
        remote = _make_mock_backend()
        local.persist.side_effect = lambda g: call_order.append("local")
        remote.persist.side_effect = lambda g: call_order.append("remote")
        backend = DualWriteBackend(local=local, remote=remote)

        backend.persist(_make_sample_graph())

        assert call_order == ["local", "remote"]

    def test_persist_remote_failure_does_not_raise(self, caplog: pytest.LogCaptureFixture) -> None:
        from rai_cli.graph.backends.dual import DualWriteBackend

        local = _make_mock_backend()
        remote = _make_mock_backend(persist_error=ConnectionError("refused"))
        backend = DualWriteBackend(local=local, remote=remote)

        with caplog.at_level(logging.WARNING):
            backend.persist(_make_sample_graph())  # should NOT raise

        local.persist.assert_called_once()
        assert "refused" in caplog.text.lower() or "remote" in caplog.text.lower()

    def test_persist_local_failure_does_raise(self) -> None:
        """Local failure is not swallowed — it's critical."""
        from rai_cli.graph.backends.dual import DualWriteBackend

        local = _make_mock_backend(persist_error=OSError("disk full"))
        remote = _make_mock_backend()
        backend = DualWriteBackend(local=local, remote=remote)

        with pytest.raises(OSError, match="disk full"):
            backend.persist(_make_sample_graph())


class TestDualWriteBackendLoad:
    def test_load_delegates_to_local(self) -> None:
        from rai_cli.graph.backends.dual import DualWriteBackend

        local = _make_mock_backend()
        remote = _make_mock_backend()
        backend = DualWriteBackend(local=local, remote=remote)

        result = backend.load()

        local.load.assert_called_once()
        remote.load.assert_not_called()
        assert result.node_count == 1


class TestDualWriteBackendHealth:
    def test_health_both_healthy(self) -> None:
        from rai_cli.graph.backends.dual import DualWriteBackend

        local = _make_mock_backend(healthy=True)
        remote = _make_mock_backend(healthy=True)
        backend = DualWriteBackend(local=local, remote=remote)

        health = backend.health()

        assert health.status == "healthy"

    def test_health_remote_unavailable_is_degraded(self) -> None:
        from rai_cli.graph.backends.dual import DualWriteBackend

        local = _make_mock_backend(healthy=True)
        remote = _make_mock_backend(healthy=False)
        backend = DualWriteBackend(local=local, remote=remote)

        health = backend.health()

        assert health.status == "degraded"

    def test_health_local_unavailable_is_unavailable(self) -> None:
        from rai_cli.graph.backends.dual import DualWriteBackend

        local = _make_mock_backend(healthy=False)
        remote = _make_mock_backend(healthy=True)
        backend = DualWriteBackend(local=local, remote=remote)

        health = backend.health()

        assert health.status == "unavailable"

    def test_health_metadata_has_backend_dual(self) -> None:
        from rai_cli.graph.backends.dual import DualWriteBackend

        local = _make_mock_backend(healthy=True)
        remote = _make_mock_backend(healthy=True)
        backend = DualWriteBackend(local=local, remote=remote)

        health = backend.health()

        assert health.metadata["backend"] == "dual"
