"""Tests for graph CLI commands.

The graph group owns the knowledge graph commands: build, validate, query,
context, list, viz, extract. These were extracted from memory.py in S247.1.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
from typer.testing import CliRunner

from raise_cli.cli.main import app

runner = CliRunner()


@pytest.fixture
def sample_graph(tmp_path: Path) -> Path:
    """Create sample memory index with concepts."""
    memory_dir = tmp_path / ".raise" / "rai" / "memory"
    memory_dir.mkdir(parents=True)

    graph_data = {
        "nodes": [
            {
                "id": "PAT-001",
                "type": "pattern",
                "content": "Singleton pattern with get/set for module state",
                "source_file": ".raise/rai/memory/patterns.jsonl",
                "created": "2026-01-31",
                "metadata": {"context": ["testing", "python"]},
            },
            {
                "id": "PAT-002",
                "type": "pattern",
                "content": "BFS traversal for graph algorithms",
                "source_file": ".raise/rai/memory/patterns.jsonl",
                "created": "2026-01-30",
                "metadata": {"context": ["algorithm", "python"]},
            },
            {
                "id": "CAL-001",
                "type": "calibration",
                "content": "F2.1: Concept Extraction - 45min actual, 60min estimated",
                "source_file": ".raise/rai/memory/calibration.jsonl",
                "created": "2026-01-31",
                "metadata": {"ratio": 0.75},
            },
            {
                "id": "SES-001",
                "type": "session",
                "content": "E2 Governance - F2.1 complete",
                "source_file": ".raise/rai/memory/sessions/index.jsonl",
                "created": "2026-01-31",
                "metadata": {"duration": "2h"},
            },
        ],
        "edges": [],
        "metadata": {"version": "1.0", "created": "2026-01-31"},
    }

    index_path = memory_dir / "index.json"
    index_path.write_text(json.dumps(graph_data, indent=2))
    return index_path


class TestGraphQueryCommand:
    """Tests for `rai graph query` command."""

    def test_query_no_graph(self, tmp_path: Path) -> None:
        """Query fails if graph index not found."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(app, ["graph", "query", "testing"])
        finally:
            os.chdir(original_cwd)
        assert result.exit_code != 0

    def test_query_basic(self, sample_graph: Path, tmp_path: Path) -> None:
        """Query returns results from graph index."""
        result = runner.invoke(
            app, ["graph", "query", "testing", "--index", str(sample_graph)]
        )
        assert result.exit_code == 0
        assert "Memory Query Results" in result.output

    def test_query_json_format(self, sample_graph: Path, tmp_path: Path) -> None:
        """Query with --format json returns valid JSON."""
        result = runner.invoke(
            app,
            [
                "graph",
                "query",
                "testing",
                "--index",
                str(sample_graph),
                "--format",
                "json",
            ],
        )
        assert result.exit_code == 0

    def test_query_with_output_file(self, sample_graph: Path, tmp_path: Path) -> None:
        """Query with --output writes to file."""
        output_file = tmp_path / "results.md"
        result = runner.invoke(
            app,
            [
                "graph",
                "query",
                "testing",
                "--index",
                str(sample_graph),
                "--output",
                str(output_file),
            ],
        )
        assert result.exit_code == 0
        assert output_file.exists()

    def test_query_compact_format(self, sample_graph: Path, tmp_path: Path) -> None:
        """Query with --format compact returns compact output."""
        result = runner.invoke(
            app,
            [
                "graph",
                "query",
                "pattern",
                "--index",
                str(sample_graph),
                "--format",
                "compact",
            ],
        )
        assert result.exit_code == 0

    def test_query_invalid_strategy(self, sample_graph: Path, tmp_path: Path) -> None:
        """Query with invalid strategy returns error."""
        result = runner.invoke(
            app,
            [
                "graph",
                "query",
                "testing",
                "--index",
                str(sample_graph),
                "--strategy",
                "invalid_strategy",
            ],
        )
        assert result.exit_code != 0


class TestGraphBuildCommand:
    """Tests for `rai graph build` command."""

    def test_build_basic(self, tmp_path: Path) -> None:
        """Build creates a graph index."""
        from unittest.mock import MagicMock, patch

        from raise_core.graph.engine import Graph
        from raise_core.graph.models import GraphNode

        graph = Graph()
        graph.add_concept(
            GraphNode(
                id="PAT-001",
                type="pattern",
                content="test pattern",
                created="2026-01-31",
            )
        )

        output_path = tmp_path / "index.json"

        with patch("raise_cli.cli.commands.graph.GraphBuilder") as mock_cls:
            mock_builder = MagicMock()
            mock_builder.build.return_value = graph
            mock_cls.return_value = mock_builder

            with patch(
                "raise_cli.cli.commands.graph.get_active_backend"
            ) as mock_backend_fn:
                mock_backend = MagicMock()
                mock_backend.load.side_effect = FileNotFoundError
                mock_backend_fn.return_value = mock_backend

                result = runner.invoke(
                    app, ["graph", "build", "--output", str(output_path)]
                )

        assert result.exit_code == 0


class TestGraphValidateCommand:
    """Tests for `rai graph validate` command."""

    def test_validate_no_index(self, tmp_path: Path) -> None:
        """Validate fails if index not found."""
        missing = tmp_path / "missing.json"
        result = runner.invoke(app, ["graph", "validate", "--index", str(missing)])
        assert result.exit_code != 0

    def test_validate_basic(self, sample_graph: Path, tmp_path: Path) -> None:
        """Validate passes on a valid graph."""
        result = runner.invoke(app, ["graph", "validate", "--index", str(sample_graph)])
        assert result.exit_code == 0


class TestGraphListCommand:
    """Tests for `rai graph list` command."""

    def test_list_no_graph(self, tmp_path: Path) -> None:
        """List fails if index not found."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(app, ["graph", "list"])
        finally:
            os.chdir(original_cwd)
        assert result.exit_code != 0

    def test_list_table_format(self, sample_graph: Path, tmp_path: Path) -> None:
        """List renders table by default."""
        result = runner.invoke(app, ["graph", "list", "--index", str(sample_graph)])
        assert result.exit_code == 0

    def test_list_json_format(self, sample_graph: Path, tmp_path: Path) -> None:
        """List with --format json returns JSON."""
        result = runner.invoke(
            app, ["graph", "list", "--index", str(sample_graph), "--format", "json"]
        )
        assert result.exit_code == 0

    def test_list_memory_only(self, sample_graph: Path, tmp_path: Path) -> None:
        """List with --memory-only filters to pattern/calibration/session."""
        result = runner.invoke(
            app, ["graph", "list", "--index", str(sample_graph), "--memory-only"]
        )
        assert result.exit_code == 0


class TestGraphExtractCommand:
    """Tests for `rai graph extract` command."""

    def test_extract_missing_file(self, tmp_path: Path) -> None:
        """Extract fails on missing file."""
        missing = tmp_path / "missing.md"
        result = runner.invoke(app, ["graph", "extract", str(missing)])
        assert result.exit_code != 0


class TestGraphHelp:
    """Tests for graph group help output."""

    def test_graph_help(self) -> None:
        """Graph group shows help."""
        result = runner.invoke(app, ["graph", "--help"])
        assert result.exit_code == 0
        assert "graph" in result.output.lower()

    def test_graph_build_help(self) -> None:
        """Graph build shows help."""
        result = runner.invoke(app, ["graph", "build", "--help"])
        assert result.exit_code == 0

    def test_graph_query_help(self) -> None:
        """Graph query shows help."""
        result = runner.invoke(app, ["graph", "query", "--help"])
        assert result.exit_code == 0

    def test_graph_validate_help(self) -> None:
        """Graph validate shows help."""
        result = runner.invoke(app, ["graph", "validate", "--help"])
        assert result.exit_code == 0

    def test_graph_list_help(self) -> None:
        """Graph list shows help."""
        result = runner.invoke(app, ["graph", "list", "--help"])
        assert result.exit_code == 0

    def test_graph_extract_help(self) -> None:
        """Graph extract shows help."""
        result = runner.invoke(app, ["graph", "extract", "--help"])
        assert result.exit_code == 0

    def test_graph_context_help(self) -> None:
        """Graph context shows help."""
        result = runner.invoke(app, ["graph", "context", "--help"])
        assert result.exit_code == 0

    def test_graph_viz_help(self) -> None:
        """Graph viz shows help."""
        result = runner.invoke(app, ["graph", "viz", "--help"])
        assert result.exit_code == 0


class TestMemoryDeprecationWrappers:
    """Tests for backward-compat deprecation wrappers on memory group."""

    def test_memory_build_deprecated(self, tmp_path: Path) -> None:
        """Rai memory build prints DEPRECATED warning."""
        # Only verify the wrapper prints the deprecation warning.
        # Functional behavior is covered by TestGraphBuildCommand::test_build_basic.
        from unittest.mock import patch

        with patch("raise_cli.cli.commands.graph.build") as mock_build:
            mock_build.return_value = None
            result = runner.invoke(app, ["memory", "build"])

        assert "DEPRECATED" in result.output
        mock_build.assert_called_once()

    def test_memory_query_deprecated(self, sample_graph: Path, tmp_path: Path) -> None:
        """Rai memory query prints DEPRECATED and still works."""
        result = runner.invoke(
            app, ["memory", "query", "testing", "--index", str(sample_graph)]
        )
        assert result.exit_code == 0
        assert "DEPRECATED" in result.output

    def test_memory_validate_deprecated(self, sample_graph: Path) -> None:
        """Rai memory validate prints DEPRECATED and still works."""
        result = runner.invoke(
            app, ["memory", "validate", "--index", str(sample_graph)]
        )
        assert result.exit_code == 0
        assert "DEPRECATED" in result.output

    def test_memory_list_deprecated(self, sample_graph: Path) -> None:
        """Rai memory list prints DEPRECATED and still works."""
        result = runner.invoke(app, ["memory", "list", "--index", str(sample_graph)])
        assert result.exit_code == 0
        assert "DEPRECATED" in result.output

    def test_memory_extract_deprecated(self, tmp_path: Path) -> None:
        """Rai memory extract prints DEPRECATED (missing file still errors)."""
        missing = tmp_path / "missing.md"
        result = runner.invoke(app, ["memory", "extract", str(missing)])
        # Should print DEPRECATED before failing on missing file
        assert "DEPRECATED" in result.output

    def test_memory_context_deprecated(self, tmp_path: Path) -> None:
        """Rai memory context prints DEPRECATED (missing index still errors)."""
        missing = tmp_path / "missing.json"
        result = runner.invoke(
            app, ["memory", "context", "mod-x", "--index", str(missing)]
        )
        assert "DEPRECATED" in result.output

    def test_memory_viz_deprecated(self, tmp_path: Path) -> None:
        """Rai memory viz prints DEPRECATED (missing index still errors)."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(app, ["memory", "viz", "--no-open"])
        finally:
            os.chdir(original_cwd)
        assert "DEPRECATED" in result.output
