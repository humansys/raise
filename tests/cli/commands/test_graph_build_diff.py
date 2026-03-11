"""Tests for raise memory build --diff integration.

Tests the CLI wiring: old graph loading, diff computation,
persistence to personal dir, and --no-diff flag.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from raise_cli.cli.main import app
from raise_cli.context.diff import GraphDiff
from raise_core.graph.backends.filesystem import FilesystemGraphBackend
from raise_core.graph.engine import Graph
from raise_core.graph.models import GraphNode

runner = CliRunner()


def _make_graph(*nodes: tuple[str, str, str]) -> Graph:
    """Build a Graph from (id, type, content) tuples."""
    graph = Graph()
    for node_id, node_type, content in nodes:
        graph.add_concept(
            GraphNode(
                id=node_id,
                type=node_type,  # type: ignore[arg-type]
                content=content,
                created="2026-02-09",
            )
        )
    return graph


class TestBuildWithDiff:
    """Build command diffs by default."""

    @patch("raise_cli.cli.commands.graph.GraphBuilder")
    def test_diff_computed_and_saved(
        self, mock_builder_cls: MagicMock, tmp_path: Path
    ) -> None:
        """Build produces diff and saves to personal dir."""
        old_graph = _make_graph(("PAT-001", "pattern", "old"))
        new_graph = _make_graph(
            ("PAT-001", "pattern", "updated"), ("mod-x", "module", "new module")
        )

        # Save old graph as the "existing" index
        index_path = tmp_path / "memory" / "index.json"
        index_path.parent.mkdir(parents=True)
        FilesystemGraphBackend(index_path).persist(old_graph)

        # Mock builder to return new graph
        mock_builder_cls.return_value.build.return_value = new_graph

        # Mock paths
        personal_dir = tmp_path / "personal"
        personal_dir.mkdir()

        with (
            patch(
                "raise_cli.cli.commands.graph._get_default_index_path",
                return_value=index_path,
            ),
            patch(
                "raise_cli.cli.commands.graph.get_personal_dir",
                return_value=personal_dir,
            ),
        ):
            result = runner.invoke(app, ["graph", "build"])

        assert result.exit_code == 0, result.output

        # Diff should be persisted
        diff_path = personal_dir / "last-diff.json"
        assert diff_path.exists()

        diff_data = json.loads(diff_path.read_text(encoding="utf-8"))
        diff = GraphDiff.model_validate(diff_data)
        assert len(diff.node_changes) == 2  # 1 modified + 1 added
        assert diff.impact == "module"
        assert "mod-x" in diff.affected_modules

    @patch("raise_cli.cli.commands.graph.GraphBuilder")
    def test_diff_summary_in_output(
        self, mock_builder_cls: MagicMock, tmp_path: Path
    ) -> None:
        """Build prints diff summary to console."""
        old_graph = _make_graph(("PAT-001", "pattern", "old"))
        new_graph = _make_graph(("PAT-001", "pattern", "new"))

        index_path = tmp_path / "memory" / "index.json"
        index_path.parent.mkdir(parents=True)
        FilesystemGraphBackend(index_path).persist(old_graph)

        mock_builder_cls.return_value.build.return_value = new_graph

        personal_dir = tmp_path / "personal"
        personal_dir.mkdir()

        with (
            patch(
                "raise_cli.cli.commands.graph._get_default_index_path",
                return_value=index_path,
            ),
            patch(
                "raise_cli.cli.commands.graph.get_personal_dir",
                return_value=personal_dir,
            ),
        ):
            result = runner.invoke(app, ["graph", "build"])

        assert result.exit_code == 0, result.output
        assert "1 nodes changed" in result.output

    @patch("raise_cli.cli.commands.graph.GraphBuilder")
    def test_first_build_no_old_graph(
        self, mock_builder_cls: MagicMock, tmp_path: Path
    ) -> None:
        """First build (no existing index) skips diff gracefully."""
        new_graph = _make_graph(("PAT-001", "pattern", "content"))

        index_path = tmp_path / "memory" / "index.json"
        # Don't create old graph — simulates first build

        mock_builder_cls.return_value.build.return_value = new_graph

        personal_dir = tmp_path / "personal"
        personal_dir.mkdir()

        with (
            patch(
                "raise_cli.cli.commands.graph._get_default_index_path",
                return_value=index_path,
            ),
            patch(
                "raise_cli.cli.commands.graph.get_personal_dir",
                return_value=personal_dir,
            ),
        ):
            result = runner.invoke(app, ["graph", "build"])

        assert result.exit_code == 0, result.output
        # No diff file on first build
        diff_path = personal_dir / "last-diff.json"
        assert not diff_path.exists()

    @patch("raise_cli.cli.commands.graph.GraphBuilder")
    def test_no_changes_diff(self, mock_builder_cls: MagicMock, tmp_path: Path) -> None:
        """Identical graphs produce 'no changes' diff."""
        graph = _make_graph(("PAT-001", "pattern", "same"))

        index_path = tmp_path / "memory" / "index.json"
        index_path.parent.mkdir(parents=True)
        FilesystemGraphBackend(index_path).persist(graph)

        mock_builder_cls.return_value.build.return_value = graph

        personal_dir = tmp_path / "personal"
        personal_dir.mkdir()

        with (
            patch(
                "raise_cli.cli.commands.graph._get_default_index_path",
                return_value=index_path,
            ),
            patch(
                "raise_cli.cli.commands.graph.get_personal_dir",
                return_value=personal_dir,
            ),
        ):
            result = runner.invoke(app, ["graph", "build"])

        assert result.exit_code == 0, result.output
        assert "no changes" in result.output


class TestNoDiffFlag:
    """--no-diff skips diff computation."""

    @patch("raise_cli.cli.commands.graph.GraphBuilder")
    def test_no_diff_flag_skips_diff(
        self, mock_builder_cls: MagicMock, tmp_path: Path
    ) -> None:
        """--no-diff builds without diffing."""
        old_graph = _make_graph(("PAT-001", "pattern", "old"))
        new_graph = _make_graph(("PAT-001", "pattern", "new"))

        index_path = tmp_path / "memory" / "index.json"
        index_path.parent.mkdir(parents=True)
        FilesystemGraphBackend(index_path).persist(old_graph)

        mock_builder_cls.return_value.build.return_value = new_graph

        personal_dir = tmp_path / "personal"
        personal_dir.mkdir()

        with (
            patch(
                "raise_cli.cli.commands.graph._get_default_index_path",
                return_value=index_path,
            ),
            patch(
                "raise_cli.cli.commands.graph.get_personal_dir",
                return_value=personal_dir,
            ),
        ):
            result = runner.invoke(app, ["graph", "build", "--no-diff"])

        assert result.exit_code == 0, result.output
        # No diff file created
        diff_path = personal_dir / "last-diff.json"
        assert not diff_path.exists()
