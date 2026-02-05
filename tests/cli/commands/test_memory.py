"""Tests for memory CLI commands.

Memory commands now use the unified graph with type filters,
rather than a separate memory graph. This consolidation provides
a single source of truth for all context.
"""

import json
import os
from pathlib import Path

import pytest
from typer.testing import CliRunner

from raise_cli.cli.main import app

runner = CliRunner()


@pytest.fixture
def sample_unified_graph(tmp_path: Path) -> Path:
    """Create sample unified graph with memory concepts."""
    graph_dir = tmp_path / ".raise" / "graph"
    graph_dir.mkdir(parents=True)

    # Create unified graph with memory nodes
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

    graph_path = graph_dir / "unified.json"
    graph_path.write_text(json.dumps(graph_data, indent=2))

    return graph_path


class TestMemoryQueryCommand:
    """Tests for `raise memory query` command."""

    def test_query_no_graph(self, tmp_path: Path) -> None:
        """Test query fails if unified graph not found."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(app, ["memory", "query", "testing"])

            assert result.exit_code == 4  # ArtifactNotFoundError
            # cli_error outputs to stderr, check output (combined stdout+stderr)
            assert "Unified graph not found" in result.output
        finally:
            os.chdir(original_cwd)

    def test_query_basic(self, sample_unified_graph: Path, tmp_path: Path) -> None:
        """Test basic query command."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(app, ["memory", "query", "singleton pattern"])

            assert result.exit_code == 0
            assert "Searching memory" in result.stdout
            assert "singleton" in result.stdout.lower() or "PAT-001" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_query_json_format(
        self, sample_unified_graph: Path, tmp_path: Path
    ) -> None:
        """Test query with JSON output."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(
                app, ["memory", "query", "testing", "--format", "json"]
            )

            assert result.exit_code == 0
            assert '"concepts"' in result.stdout or "concepts" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_query_with_output_file(
        self, sample_unified_graph: Path, tmp_path: Path
    ) -> None:
        """Test query saves to output file."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            output_file = tmp_path / "memory_context.md"
            result = runner.invoke(
                app,
                ["memory", "query", "python", "--output", str(output_file)],
            )

            assert result.exit_code == 0
            assert output_file.exists()
            content = output_file.read_text()
            assert "Memory Query Results" in content or "Concepts" in content
        finally:
            os.chdir(original_cwd)

    def test_query_max_results(
        self, sample_unified_graph: Path, tmp_path: Path
    ) -> None:
        """Test query respects max results."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(
                app, ["memory", "query", "python", "--max-results", "1"]
            )

            assert result.exit_code == 0
        finally:
            os.chdir(original_cwd)

    def test_query_no_expand(self, sample_unified_graph: Path, tmp_path: Path) -> None:
        """Test query without traversal expansion."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(app, ["memory", "query", "singleton", "--no-expand"])

            assert result.exit_code == 0
        finally:
            os.chdir(original_cwd)

    def test_query_with_custom_graph(
        self, sample_unified_graph: Path, tmp_path: Path
    ) -> None:
        """Test query with explicit graph path."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(
                app,
                [
                    "memory",
                    "query",
                    "testing",
                    "--graph",
                    str(sample_unified_graph),
                ],
            )

            assert result.exit_code == 0
        finally:
            os.chdir(original_cwd)


class TestMemoryListCommand:
    """Tests for `raise memory list` command."""

    def test_list_no_graph(self, tmp_path: Path) -> None:
        """Test list fails if unified graph not found."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(app, ["memory", "list"])

            assert result.exit_code == 4  # ArtifactNotFoundError
            # cli_error outputs to stderr, check output (combined stdout+stderr)
            assert "Unified graph not found" in result.output
        finally:
            os.chdir(original_cwd)

    def test_list_table_format(
        self, sample_unified_graph: Path, tmp_path: Path
    ) -> None:
        """Test list with table format (default)."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(app, ["memory", "list"])

            assert result.exit_code == 0
            assert "Memory Concepts" in result.stdout
            assert "Concepts:" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_list_json_format(
        self, sample_unified_graph: Path, tmp_path: Path
    ) -> None:
        """Test list with JSON format."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(app, ["memory", "list", "--format", "json"])

            assert result.exit_code == 0
            # JSON array of concepts
            assert "[" in result.stdout
            assert "PAT-001" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_list_markdown_format(
        self, sample_unified_graph: Path, tmp_path: Path
    ) -> None:
        """Test list with markdown format."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(app, ["memory", "list", "--format", "markdown"])

            assert result.exit_code == 0
            assert "# Memory Concepts" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_list_with_output_file(
        self, sample_unified_graph: Path, tmp_path: Path
    ) -> None:
        """Test list saves to output file."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            output_file = tmp_path / "memory.json"
            result = runner.invoke(
                app,
                ["memory", "list", "--format", "json", "--output", str(output_file)],
            )

            assert result.exit_code == 0
            assert output_file.exists()
            content = output_file.read_text()
            assert "PAT-001" in content
        finally:
            os.chdir(original_cwd)

    def test_list_with_custom_graph(
        self, sample_unified_graph: Path, tmp_path: Path
    ) -> None:
        """Test list with explicit graph path."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(
                app,
                ["memory", "list", "--graph", str(sample_unified_graph)],
            )

            assert result.exit_code == 0
            assert "Memory Concepts" in result.stdout
        finally:
            os.chdir(original_cwd)


class TestMemoryHelp:
    """Tests for memory command help."""

    def test_memory_help(self) -> None:
        """Test memory command shows help."""
        result = runner.invoke(app, ["memory", "--help"])

        assert result.exit_code == 0
        assert "memory" in result.stdout.lower()

    def test_memory_query_help(self) -> None:
        """Test memory query command shows help."""
        result = runner.invoke(app, ["memory", "query", "--help"])

        assert result.exit_code == 0
        assert "query" in result.stdout.lower()
        assert "--max-results" in result.stdout

    def test_memory_list_help(self) -> None:
        """Test memory list command shows help."""
        result = runner.invoke(app, ["memory", "list", "--help"])

        assert result.exit_code == 0
        assert "list" in result.stdout.lower()
        assert "--format" in result.stdout
