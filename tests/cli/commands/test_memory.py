"""Tests for memory CLI commands."""

import os
from pathlib import Path

import pytest
from typer.testing import CliRunner

from raise_cli.cli.main import app

runner = CliRunner()


@pytest.fixture
def sample_memory_dir(tmp_path: Path) -> Path:
    """Create sample memory directory with JSONL files."""
    memory_dir = tmp_path / ".rai" / "memory"
    memory_dir.mkdir(parents=True)

    # Create patterns.jsonl
    (memory_dir / "patterns.jsonl").write_text(
        '{"id": "PAT-001", "type": "codebase", "content": "Singleton pattern with get/set", "context": ["testing", "python"], "created": "2026-01-31"}\n'
        '{"id": "PAT-002", "type": "technical", "content": "BFS traversal for graphs", "context": ["algorithm", "python"], "created": "2026-01-30"}\n'
    )

    # Create calibration.jsonl
    (memory_dir / "calibration.jsonl").write_text(
        '{"feature": "F2.1", "estimated": "60min", "actual": "45min", "ratio": 0.75, "date": "2026-01-31"}\n'
    )

    # Create sessions/index.jsonl
    sessions_dir = memory_dir / "sessions"
    sessions_dir.mkdir()
    (sessions_dir / "index.jsonl").write_text(
        '{"id": "SES-001", "date": "2026-01-31", "topic": "E2 Governance", "duration": "2h", "outcomes": ["F2.1 complete"]}\n'
    )

    return memory_dir


class TestMemoryQueryCommand:
    """Tests for `raise memory query` command."""

    def test_query_no_memory_dir(self, tmp_path: Path) -> None:
        """Test query fails if memory directory not found."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(app, ["memory", "query", "testing"])

            assert result.exit_code == 1
            assert "Memory directory not found" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_query_basic(self, sample_memory_dir: Path, tmp_path: Path) -> None:
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

    def test_query_json_format(self, sample_memory_dir: Path, tmp_path: Path) -> None:
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
        self, sample_memory_dir: Path, tmp_path: Path
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

    def test_query_max_results(self, sample_memory_dir: Path, tmp_path: Path) -> None:
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

    def test_query_no_expand(self, sample_memory_dir: Path, tmp_path: Path) -> None:
        """Test query without traversal expansion."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(app, ["memory", "query", "singleton", "--no-expand"])

            assert result.exit_code == 0
        finally:
            os.chdir(original_cwd)

    def test_query_with_custom_memory_dir(
        self, sample_memory_dir: Path, tmp_path: Path
    ) -> None:
        """Test query with explicit memory directory."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(
                app,
                [
                    "memory",
                    "query",
                    "testing",
                    "--memory-dir",
                    str(sample_memory_dir),
                ],
            )

            assert result.exit_code == 0
        finally:
            os.chdir(original_cwd)


class TestMemoryDumpCommand:
    """Tests for `raise memory dump` command."""

    def test_dump_no_memory_dir(self, tmp_path: Path) -> None:
        """Test dump fails if memory directory not found."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(app, ["memory", "dump"])

            assert result.exit_code == 1
            assert "Memory directory not found" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_dump_table_format(self, sample_memory_dir: Path, tmp_path: Path) -> None:
        """Test dump with table format (default)."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(app, ["memory", "dump"])

            assert result.exit_code == 0
            assert "Memory Graph" in result.stdout
            assert "Nodes:" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_dump_json_format(self, sample_memory_dir: Path, tmp_path: Path) -> None:
        """Test dump with JSON format."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(app, ["memory", "dump", "--format", "json"])

            assert result.exit_code == 0
            assert '"nodes"' in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_dump_markdown_format(
        self, sample_memory_dir: Path, tmp_path: Path
    ) -> None:
        """Test dump with markdown format."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(app, ["memory", "dump", "--format", "markdown"])

            assert result.exit_code == 0
            assert "# Memory Graph" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_dump_with_output_file(
        self, sample_memory_dir: Path, tmp_path: Path
    ) -> None:
        """Test dump saves to output file."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            output_file = tmp_path / "graph.json"
            result = runner.invoke(
                app,
                ["memory", "dump", "--format", "json", "--output", str(output_file)],
            )

            assert result.exit_code == 0
            assert output_file.exists()
            content = output_file.read_text()
            assert "nodes" in content
        finally:
            os.chdir(original_cwd)

    def test_dump_with_custom_memory_dir(
        self, sample_memory_dir: Path, tmp_path: Path
    ) -> None:
        """Test dump with explicit memory directory."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(
                app,
                ["memory", "dump", "--memory-dir", str(sample_memory_dir)],
            )

            assert result.exit_code == 0
            assert "Memory Graph" in result.stdout
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

    def test_memory_dump_help(self) -> None:
        """Test memory dump command shows help."""
        result = runner.invoke(app, ["memory", "dump", "--help"])

        assert result.exit_code == 0
        assert "dump" in result.stdout.lower()
        assert "--format" in result.stdout
