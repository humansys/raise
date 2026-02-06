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
    """Create sample memory index with concepts."""
    memory_dir = tmp_path / ".raise" / "rai" / "memory"
    memory_dir.mkdir(parents=True)

    # Create memory index with concepts
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
            assert "Memory index not found" in result.output
        finally:
            os.chdir(original_cwd)

    def test_query_basic(self, sample_unified_graph: Path, tmp_path: Path) -> None:
        """Test basic query command."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(app, ["memory", "query", "singleton pattern"])

            assert result.exit_code == 0
            assert "Querying memory" in result.stdout
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
                app, ["memory", "query", "python", "--limit", "1"]
            )

            assert result.exit_code == 0
        finally:
            os.chdir(original_cwd)

    def test_query_with_custom_index(
        self, sample_unified_graph: Path, tmp_path: Path
    ) -> None:
        """Test query with explicit index path."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(
                app,
                [
                    "memory",
                    "query",
                    "testing",
                    "--index",
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
            assert "Memory index not found" in result.output
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

    def test_list_human_format(
        self, sample_unified_graph: Path, tmp_path: Path
    ) -> None:
        """Test list with human-readable format."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(app, ["memory", "list", "--format", "human"])

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
                ["memory", "list", "--index", str(sample_unified_graph)],
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
        assert "--limit" in result.stdout

    def test_memory_list_help(self) -> None:
        """Test memory list command shows help."""
        result = runner.invoke(app, ["memory", "list", "--help"])

        assert result.exit_code == 0
        assert "list" in result.stdout.lower()
        assert "--format" in result.stdout

    def test_memory_build_help(self) -> None:
        """Test memory build command shows help."""
        result = runner.invoke(app, ["memory", "build", "--help"])

        assert result.exit_code == 0
        assert "build" in result.stdout.lower()
        assert "--output" in result.stdout

    def test_memory_validate_help(self) -> None:
        """Test memory validate command shows help."""
        result = runner.invoke(app, ["memory", "validate", "--help"])

        assert result.exit_code == 0
        assert "validate" in result.stdout.lower()
        assert "--index" in result.stdout

    def test_memory_extract_help(self) -> None:
        """Test memory extract command shows help."""
        result = runner.invoke(app, ["memory", "extract", "--help"])

        assert result.exit_code == 0
        assert "extract" in result.stdout.lower()
        assert "--format" in result.stdout


class TestMemoryBuildCommand:
    """Tests for `raise memory build` command."""

    def test_build_basic(self, tmp_path: Path) -> None:
        """Test basic build command creates index."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            # Create minimal structure
            memory_dir = tmp_path / ".raise" / "rai" / "memory"
            memory_dir.mkdir(parents=True)

            result = runner.invoke(app, ["memory", "build"])

            assert result.exit_code == 0
            assert "Building memory index" in result.stdout
            assert (memory_dir / "index.json").exists()
        finally:
            os.chdir(original_cwd)


class TestMemoryValidateCommand:
    """Tests for `raise memory validate` command."""

    def test_validate_no_index(self, tmp_path: Path) -> None:
        """Test validate fails if index not found."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(app, ["memory", "validate"])

            assert result.exit_code == 4  # ArtifactNotFoundError
            assert "Index file not found" in result.output
        finally:
            os.chdir(original_cwd)

    def test_validate_basic(
        self, sample_unified_graph: Path, tmp_path: Path
    ) -> None:
        """Test basic validate command."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(app, ["memory", "validate"])

            assert result.exit_code == 0
            assert "Memory index is valid" in result.stdout
        finally:
            os.chdir(original_cwd)
