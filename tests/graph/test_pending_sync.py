"""Tests for pending_sync marker helpers."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from raise_cli.graph.backends.pending import (
    PendingSyncMarker,
    clear_pending_marker,
    read_pending_marker,
    write_pending_marker,
)


class TestPendingSyncMarker:
    """PendingSyncMarker Pydantic model."""

    def test_model_fields(self) -> None:
        marker = PendingSyncMarker(
            timestamp=datetime(2026, 2, 26, 14, 30, tzinfo=UTC),
            graph_path=".raise/rai/graph-index.json",
            node_count=42,
            edge_count=67,
            error="Connection refused",
        )
        assert marker.node_count == 42
        assert marker.edge_count == 67
        assert marker.error == "Connection refused"
        assert marker.graph_path == ".raise/rai/graph-index.json"

    def test_model_serializes_to_json(self) -> None:
        marker = PendingSyncMarker(
            timestamp=datetime(2026, 2, 26, 14, 30, tzinfo=UTC),
            graph_path=".raise/rai/graph-index.json",
            node_count=10,
            edge_count=5,
            error="timeout",
        )
        data = json.loads(marker.model_dump_json())
        assert "timestamp" in data
        assert data["node_count"] == 10


class TestWritePendingMarker:
    """write_pending_marker creates file."""

    def test_creates_marker_file(self, tmp_path: Path) -> None:
        raise_dir = tmp_path / ".raise"
        raise_dir.mkdir()
        marker = PendingSyncMarker(
            timestamp=datetime(2026, 2, 26, 14, 30, tzinfo=UTC),
            graph_path=".raise/rai/graph-index.json",
            node_count=42,
            edge_count=67,
            error="Connection refused",
        )
        write_pending_marker(raise_dir, marker)
        marker_path = raise_dir / "pending_sync.json"
        assert marker_path.exists()
        data = json.loads(marker_path.read_text())
        assert data["node_count"] == 42
        assert data["error"] == "Connection refused"

    def test_overwrites_existing_marker(self, tmp_path: Path) -> None:
        raise_dir = tmp_path / ".raise"
        raise_dir.mkdir()
        old = PendingSyncMarker(
            timestamp=datetime(2026, 2, 26, 14, 0, tzinfo=UTC),
            graph_path="old",
            node_count=1,
            edge_count=1,
            error="old error",
        )
        write_pending_marker(raise_dir, old)
        new = PendingSyncMarker(
            timestamp=datetime(2026, 2, 26, 15, 0, tzinfo=UTC),
            graph_path="new",
            node_count=99,
            edge_count=88,
            error="new error",
        )
        write_pending_marker(raise_dir, new)
        result = read_pending_marker(raise_dir)
        assert result is not None
        assert result.node_count == 99


class TestReadPendingMarker:
    """read_pending_marker returns model or None."""

    def test_returns_none_when_missing(self, tmp_path: Path) -> None:
        raise_dir = tmp_path / ".raise"
        raise_dir.mkdir()
        assert read_pending_marker(raise_dir) is None

    def test_returns_marker_when_present(self, tmp_path: Path) -> None:
        raise_dir = tmp_path / ".raise"
        raise_dir.mkdir()
        marker = PendingSyncMarker(
            timestamp=datetime(2026, 2, 26, 14, 30, tzinfo=UTC),
            graph_path="test",
            node_count=5,
            edge_count=3,
            error="err",
        )
        write_pending_marker(raise_dir, marker)
        result = read_pending_marker(raise_dir)
        assert result is not None
        assert result.node_count == 5

    def test_returns_none_on_corrupt_json(self, tmp_path: Path) -> None:
        raise_dir = tmp_path / ".raise"
        raise_dir.mkdir()
        (raise_dir / "pending_sync.json").write_text("not json")
        assert read_pending_marker(raise_dir) is None


class TestClearPendingMarker:
    """clear_pending_marker deletes file."""

    def test_returns_true_when_file_exists(self, tmp_path: Path) -> None:
        raise_dir = tmp_path / ".raise"
        raise_dir.mkdir()
        marker = PendingSyncMarker(
            timestamp=datetime(2026, 2, 26, 14, 30, tzinfo=UTC),
            graph_path="test",
            node_count=1,
            edge_count=1,
            error="err",
        )
        write_pending_marker(raise_dir, marker)
        assert clear_pending_marker(raise_dir) is True
        assert not (raise_dir / "pending_sync.json").exists()

    def test_returns_false_when_no_file(self, tmp_path: Path) -> None:
        raise_dir = tmp_path / ".raise"
        raise_dir.mkdir()
        assert clear_pending_marker(raise_dir) is False
