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

from rai_cli.cli.main import app

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
            result = runner.invoke(app, ["memory", "query", "python", "--limit", "1"])

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

    def test_list_json_format(self, sample_unified_graph: Path, tmp_path: Path) -> None:
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

    def test_validate_basic(self, sample_unified_graph: Path, tmp_path: Path) -> None:
        """Test basic validate command."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(app, ["memory", "validate"])

            assert result.exit_code == 0
            assert "Memory index is valid" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_validate_completeness_warns_missing_architecture(
        self, tmp_path: Path
    ) -> None:
        """Validate should warn when graph has no architecture nodes."""
        memory_dir = tmp_path / ".raise" / "rai" / "memory"
        memory_dir.mkdir(parents=True)

        # Graph with only pattern nodes — no architecture, no modules
        graph_data = {
            "nodes": [
                {
                    "id": "PAT-001",
                    "type": "pattern",
                    "content": "Test pattern",
                    "source_file": "test.jsonl",
                    "created": "2026-01-31",
                    "metadata": {},
                },
            ],
            "edges": [],
            "metadata": {"version": "1.0", "created": "2026-01-31"},
        }
        (memory_dir / "index.json").write_text(json.dumps(graph_data))

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(app, ["memory", "validate"])

            assert result.exit_code == 0
            assert "Completeness" in result.output
            assert "architecture" in result.output
            assert "module" in result.output
        finally:
            os.chdir(original_cwd)

    def test_validate_completeness_passes_with_architecture_and_modules(
        self, tmp_path: Path
    ) -> None:
        """Validate should pass completeness when architecture and module nodes exist."""
        memory_dir = tmp_path / ".raise" / "rai" / "memory"
        memory_dir.mkdir(parents=True)

        graph_data = {
            "nodes": [
                {
                    "id": "arch-context",
                    "type": "architecture",
                    "content": "System context",
                    "source_file": "governance/architecture/system-context.md",
                    "created": "2026-01-31",
                    "metadata": {"arch_type": "architecture_context"},
                },
                {
                    "id": "mod-core",
                    "type": "module",
                    "content": "Core module",
                    "source_file": "governance/architecture/modules/core.md",
                    "created": "2026-01-31",
                    "metadata": {},
                },
            ],
            "edges": [],
            "metadata": {"version": "1.0", "created": "2026-01-31"},
        }
        (memory_dir / "index.json").write_text(json.dumps(graph_data))

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(app, ["memory", "validate"])

            assert result.exit_code == 0
            assert "Completeness check passed" in result.output
        finally:
            os.chdir(original_cwd)


class TestMemoryAddPatternCommand:
    """Tests for `raise memory add-pattern` command."""

    def test_add_pattern_basic(self, tmp_path: Path) -> None:
        """Test basic add-pattern command."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            # Create memory directory
            memory_dir = tmp_path / ".raise" / "rai" / "memory"
            memory_dir.mkdir(parents=True)
            # Create empty patterns file
            (memory_dir / "patterns.jsonl").write_text("")

            result = runner.invoke(
                app,
                [
                    "memory",
                    "add-pattern",
                    "Test pattern content",
                    "-c",
                    "testing,python",
                ],
            )

            assert result.exit_code == 0
            assert "PAT-" in result.stdout
            assert "Test pattern content" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_add_pattern_with_type(self, tmp_path: Path) -> None:
        """Test add-pattern with custom type."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            memory_dir = tmp_path / ".raise" / "rai" / "memory"
            memory_dir.mkdir(parents=True)
            (memory_dir / "patterns.jsonl").write_text("")

            result = runner.invoke(
                app,
                ["memory", "add-pattern", "Architecture pattern", "-t", "architecture"],
            )

            assert result.exit_code == 0
            assert "PAT-" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_add_pattern_invalid_type(self, tmp_path: Path) -> None:
        """Test add-pattern with invalid type fails."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            memory_dir = tmp_path / ".raise" / "rai" / "memory"
            memory_dir.mkdir(parents=True)
            (memory_dir / "patterns.jsonl").write_text("")

            result = runner.invoke(
                app,
                ["memory", "add-pattern", "Test", "-t", "invalid_type"],
            )

            assert result.exit_code == 7
            assert "Invalid pattern type" in result.output
        finally:
            os.chdir(original_cwd)

    def test_add_pattern_creates_missing_dir(self, tmp_path: Path) -> None:
        """Test add-pattern auto-creates memory directory if missing."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            # Don't create memory directory - it should be auto-created
            result = runner.invoke(
                app,
                ["memory", "add-pattern", "Test pattern"],
            )

            assert result.exit_code == 0
            assert "PAT-" in result.stdout
            # Verify directory was created
            memory_dir = tmp_path / ".raise" / "rai" / "memory"
            assert memory_dir.exists()
        finally:
            os.chdir(original_cwd)

    def test_add_pattern_with_scope_global(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test add-pattern with --scope global writes to global dir."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            # Setup global directory
            global_rai = tmp_path / "global_rai"
            global_rai.mkdir()
            monkeypatch.setenv("RAI_HOME", str(global_rai))
            (global_rai / "patterns.jsonl").write_text("")

            result = runner.invoke(
                app,
                ["memory", "add-pattern", "Global pattern", "--scope", "global"],
            )

            assert result.exit_code == 0
            assert "PAT-" in result.stdout
            # Verify written to global
            patterns_file = global_rai / "patterns.jsonl"
            assert patterns_file.exists()
            content = patterns_file.read_text()
            assert "Global pattern" in content
        finally:
            os.chdir(original_cwd)

    def test_add_pattern_with_scope_personal(self, tmp_path: Path) -> None:
        """Test add-pattern with --scope personal writes to personal dir."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            # Setup personal directory
            personal_dir = tmp_path / ".raise" / "rai" / "personal"
            personal_dir.mkdir(parents=True)
            (personal_dir / "patterns.jsonl").write_text("")

            result = runner.invoke(
                app,
                ["memory", "add-pattern", "Personal pattern", "--scope", "personal"],
            )

            assert result.exit_code == 0
            assert "PAT-" in result.stdout
            # Verify written to personal
            patterns_file = personal_dir / "patterns.jsonl"
            content = patterns_file.read_text()
            assert "Personal pattern" in content
        finally:
            os.chdir(original_cwd)

    def test_add_pattern_invalid_scope(self, tmp_path: Path) -> None:
        """Test add-pattern with invalid scope fails."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            memory_dir = tmp_path / ".raise" / "rai" / "memory"
            memory_dir.mkdir(parents=True)
            (memory_dir / "patterns.jsonl").write_text("")

            result = runner.invoke(
                app,
                ["memory", "add-pattern", "Test", "--scope", "invalid"],
            )

            assert result.exit_code == 7
            assert "Invalid scope" in result.output
        finally:
            os.chdir(original_cwd)


class TestMemoryAddCalibrationCommand:
    """Tests for `raise memory add-calibration` command."""

    def test_add_calibration_basic(self, tmp_path: Path) -> None:
        """Test basic add-calibration command."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            memory_dir = tmp_path / ".raise" / "rai" / "memory"
            memory_dir.mkdir(parents=True)
            (memory_dir / "calibration.jsonl").write_text("")

            result = runner.invoke(
                app,
                [
                    "memory",
                    "add-calibration",
                    "F1.1",
                    "--name",
                    "Test Feature",
                    "--size",
                    "S",
                    "--actual",
                    "30",
                ],
            )

            assert result.exit_code == 0
            assert "CAL-" in result.stdout
            assert "F1.1" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_add_calibration_with_estimate(self, tmp_path: Path) -> None:
        """Test add-calibration with estimated time."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            memory_dir = tmp_path / ".raise" / "rai" / "memory"
            memory_dir.mkdir(parents=True)
            (memory_dir / "calibration.jsonl").write_text("")

            result = runner.invoke(
                app,
                [
                    "memory",
                    "add-calibration",
                    "F1.2",
                    "--name",
                    "Feature with estimate",
                    "--size",
                    "M",
                    "--actual",
                    "45",
                    "--estimated",
                    "60",
                ],
            )

            assert result.exit_code == 0
            assert "Velocity:" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_add_calibration_invalid_size(self, tmp_path: Path) -> None:
        """Test add-calibration with invalid size fails."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            memory_dir = tmp_path / ".raise" / "rai" / "memory"
            memory_dir.mkdir(parents=True)
            (memory_dir / "calibration.jsonl").write_text("")

            result = runner.invoke(
                app,
                [
                    "memory",
                    "add-calibration",
                    "F1.1",
                    "--name",
                    "Test",
                    "--size",
                    "HUGE",
                    "--actual",
                    "30",
                ],
            )

            assert result.exit_code == 7
            assert "Invalid size" in result.output
        finally:
            os.chdir(original_cwd)


class TestMemoryAddSessionCommand:
    """Tests for `raise memory add-session` command."""

    def test_add_session_basic(self, tmp_path: Path) -> None:
        """Test basic add-session command."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            memory_dir = tmp_path / ".raise" / "rai" / "memory" / "sessions"
            memory_dir.mkdir(parents=True)
            (memory_dir / "index.jsonl").write_text("")

            result = runner.invoke(
                app,
                ["memory", "add-session", "Test session topic"],
            )

            assert result.exit_code == 0
            assert "SES-" in result.stdout
            assert "Test session topic" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_add_session_with_outcomes(self, tmp_path: Path) -> None:
        """Test add-session with outcomes."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            memory_dir = tmp_path / ".raise" / "rai" / "memory" / "sessions"
            memory_dir.mkdir(parents=True)
            (memory_dir / "index.jsonl").write_text("")

            result = runner.invoke(
                app,
                [
                    "memory",
                    "add-session",
                    "Feature work",
                    "-o",
                    "Task 1 done,Task 2 done,Task 3 done",
                    "-t",
                    "story",
                ],
            )

            assert result.exit_code == 0
            assert "Outcomes:" in result.stdout
        finally:
            os.chdir(original_cwd)


class TestMemoryEmitWorkCommand:
    """Tests for `raise memory emit-work` command."""

    def test_emit_work_start(self, tmp_path: Path) -> None:
        """Test emit-work start event."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            # Create telemetry directory
            telemetry_dir = tmp_path / ".raise" / "rai" / "telemetry"
            telemetry_dir.mkdir(parents=True)

            result = runner.invoke(
                app,
                ["memory", "emit-work", "story", "F1.1", "-e", "start", "-p", "design"],
            )

            assert result.exit_code == 0
            assert "started" in result.stdout
            assert "Story F1.1" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_emit_work_complete(self, tmp_path: Path) -> None:
        """Test emit-work complete event."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            telemetry_dir = tmp_path / ".raise" / "rai" / "telemetry"
            telemetry_dir.mkdir(parents=True)

            result = runner.invoke(
                app,
                [
                    "memory",
                    "emit-work",
                    "epic",
                    "E1",
                    "-e",
                    "complete",
                    "-p",
                    "implement",
                ],
            )

            assert result.exit_code == 0
            assert "complete" in result.stdout
            assert "Epic E1" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_emit_work_blocked(self, tmp_path: Path) -> None:
        """Test emit-work blocked event."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            telemetry_dir = tmp_path / ".raise" / "rai" / "telemetry"
            telemetry_dir.mkdir(parents=True)

            result = runner.invoke(
                app,
                [
                    "memory",
                    "emit-work",
                    "story",
                    "F1.2",
                    "-e",
                    "blocked",
                    "-p",
                    "plan",
                    "-b",
                    "waiting for API",
                ],
            )

            assert result.exit_code == 0
            assert "blocked" in result.stdout
            assert "waiting for API" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_emit_work_invalid_type(self, tmp_path: Path) -> None:
        """Test emit-work with invalid work type."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(
                app,
                ["memory", "emit-work", "invalid", "X1", "-e", "start"],
            )

            assert result.exit_code == 7
            assert "Invalid work type" in result.output
        finally:
            os.chdir(original_cwd)

    def test_emit_work_invalid_event(self, tmp_path: Path) -> None:
        """Test emit-work with invalid event type."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(
                app,
                ["memory", "emit-work", "story", "F1.1", "-e", "invalid"],
            )

            assert result.exit_code == 7
            assert "Invalid event" in result.output
        finally:
            os.chdir(original_cwd)

    def test_emit_work_invalid_phase(self, tmp_path: Path) -> None:
        """Test emit-work with invalid phase."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(
                app,
                [
                    "memory",
                    "emit-work",
                    "story",
                    "F1.1",
                    "-e",
                    "start",
                    "-p",
                    "invalid",
                ],
            )

            assert result.exit_code == 7
            assert "Invalid phase" in result.output
        finally:
            os.chdir(original_cwd)


class TestMemoryEmitSessionCommand:
    """Tests for `raise memory emit-session` command."""

    def test_emit_session_basic(self, tmp_path: Path) -> None:
        """Test basic emit-session command."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            telemetry_dir = tmp_path / ".raise" / "rai" / "telemetry"
            telemetry_dir.mkdir(parents=True)

            result = runner.invoke(
                app,
                ["memory", "emit-session", "-t", "story", "-o", "success"],
            )

            assert result.exit_code == 0
            assert "Session event recorded" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_emit_session_with_details(self, tmp_path: Path) -> None:
        """Test emit-session with duration and features."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            telemetry_dir = tmp_path / ".raise" / "rai" / "telemetry"
            telemetry_dir.mkdir(parents=True)

            result = runner.invoke(
                app,
                [
                    "memory",
                    "emit-session",
                    "-t",
                    "research",
                    "-o",
                    "partial",
                    "-d",
                    "90",
                    "-f",
                    "F1.1,F1.2",
                ],
            )

            assert result.exit_code == 0
            assert "Duration: 90" in result.stdout
            assert "Stories:" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_emit_session_invalid_outcome(self, tmp_path: Path) -> None:
        """Test emit-session with invalid outcome."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(
                app,
                ["memory", "emit-session", "-o", "invalid"],
            )

            assert result.exit_code == 7
            assert "Invalid outcome" in result.output
        finally:
            os.chdir(original_cwd)


class TestMemoryEmitCalibrationCommand:
    """Tests for `raise memory emit-calibration` command."""

    def test_emit_calibration_basic(self, tmp_path: Path) -> None:
        """Test basic emit-calibration command."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            telemetry_dir = tmp_path / ".raise" / "rai" / "telemetry"
            telemetry_dir.mkdir(parents=True)

            result = runner.invoke(
                app,
                [
                    "memory",
                    "emit-calibration",
                    "F1.1",
                    "-s",
                    "S",
                    "-e",
                    "60",
                    "-a",
                    "30",
                ],
            )

            assert result.exit_code == 0
            assert "Calibration event recorded" in result.stdout
            assert "Velocity: 2.0x" in result.stdout
            assert "faster than estimated" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_emit_calibration_slower(self, tmp_path: Path) -> None:
        """Test emit-calibration when slower than estimated."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            telemetry_dir = tmp_path / ".raise" / "rai" / "telemetry"
            telemetry_dir.mkdir(parents=True)

            result = runner.invoke(
                app,
                [
                    "memory",
                    "emit-calibration",
                    "F1.2",
                    "-s",
                    "M",
                    "-e",
                    "30",
                    "-a",
                    "60",
                ],
            )

            assert result.exit_code == 0
            assert "Velocity: 0.5x" in result.stdout
            assert "slower than estimated" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_emit_calibration_on_target(self, tmp_path: Path) -> None:
        """Test emit-calibration when exactly on target."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            telemetry_dir = tmp_path / ".raise" / "rai" / "telemetry"
            telemetry_dir.mkdir(parents=True)

            result = runner.invoke(
                app,
                [
                    "memory",
                    "emit-calibration",
                    "F1.3",
                    "-s",
                    "S",
                    "-e",
                    "30",
                    "-a",
                    "30",
                ],
            )

            assert result.exit_code == 0
            assert "Velocity: 1.0x" in result.stdout
            assert "on target" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_emit_calibration_invalid_size(self, tmp_path: Path) -> None:
        """Test emit-calibration with invalid size."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(
                app,
                [
                    "memory",
                    "emit-calibration",
                    "F1.1",
                    "-s",
                    "XXL",
                    "-e",
                    "30",
                    "-a",
                    "30",
                ],
            )

            assert result.exit_code == 7
            assert "Invalid size" in result.output
        finally:
            os.chdir(original_cwd)

    def test_emit_calibration_zero_estimated(self, tmp_path: Path) -> None:
        """Test emit-calibration with zero estimated fails."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(
                app,
                [
                    "memory",
                    "emit-calibration",
                    "F1.1",
                    "-s",
                    "S",
                    "-e",
                    "0",
                    "-a",
                    "30",
                ],
            )

            assert result.exit_code == 7
            assert "Estimated duration must be > 0" in result.output
        finally:
            os.chdir(original_cwd)

    def test_emit_calibration_zero_actual(self, tmp_path: Path) -> None:
        """Test emit-calibration with zero actual fails."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(
                app,
                [
                    "memory",
                    "emit-calibration",
                    "F1.1",
                    "-s",
                    "S",
                    "-e",
                    "30",
                    "-a",
                    "0",
                ],
            )

            assert result.exit_code == 7
            assert "Actual duration must be > 0" in result.output
        finally:
            os.chdir(original_cwd)


class TestMemoryQueryEdgeCases:
    """Tests for edge cases in memory query command."""

    def test_query_invalid_strategy(
        self, sample_unified_graph: Path, tmp_path: Path
    ) -> None:
        """Test query with invalid strategy fails."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(
                app,
                ["memory", "query", "test", "--strategy", "invalid_strategy"],
            )

            assert result.exit_code == 7
            assert "Invalid strategy" in result.output
        finally:
            os.chdir(original_cwd)


class TestMemoryListEdgeCases:
    """Tests for edge cases in memory list command."""

    def test_list_memory_only(self, sample_unified_graph: Path, tmp_path: Path) -> None:
        """Test list with --memory-only flag."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(app, ["memory", "list", "--memory-only"])

            assert result.exit_code == 0
            # Should show pattern, calibration, session but not other types
            assert "Memory Concepts" in result.stdout
        finally:
            os.chdir(original_cwd)


class TestMemoryGenerateCommand:
    """Tests for `raise memory generate` command."""

    def test_generate_shows_deprecation(self, tmp_path: Path) -> None:
        """Generate command shows deprecation notice."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            # Create minimal structure
            memory_dir = tmp_path / ".raise" / "rai" / "memory"
            memory_dir.mkdir(parents=True)

            result = runner.invoke(app, ["memory", "generate"])

            assert result.exit_code == 0
            assert (
                "deprecated" in result.output.lower()
                or "skipped" in result.output.lower()
            )
        finally:
            os.chdir(original_cwd)

    def test_generate_does_not_write_canonical_memory_md(self, tmp_path: Path) -> None:
        """Generate command does not write canonical MEMORY.md."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            memory_dir = tmp_path / ".raise" / "rai" / "memory"
            memory_dir.mkdir(parents=True)

            runner.invoke(app, ["memory", "generate"])

            canonical_path = memory_dir / "MEMORY.md"
            assert not canonical_path.exists()
        finally:
            os.chdir(original_cwd)

    def test_generate_suggests_memory_build(self, tmp_path: Path) -> None:
        """Generate command suggests using memory build instead."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            memory_dir = tmp_path / ".raise" / "rai" / "memory"
            memory_dir.mkdir(parents=True)

            result = runner.invoke(app, ["memory", "generate"])

            assert result.exit_code == 0
            assert "raise memory build" in result.output
        finally:
            os.chdir(original_cwd)


class TestMemoryQueryEdgeTypeFilter:
    """Tests for --edge-types CLI option."""

    @pytest.fixture
    def graph_with_edges(self, tmp_path: Path) -> Path:
        """Create graph with edges for edge-type filtering tests."""
        memory_dir = tmp_path / ".raise" / "rai" / "memory"
        memory_dir.mkdir(parents=True)

        graph_data = {
            "directed": True,
            "multigraph": True,
            "graph": {},
            "nodes": [
                {
                    "id": "mod-memory",
                    "type": "module",
                    "content": "Memory module manages patterns and calibration",
                    "source_file": "governance/architecture/modules/memory.md",
                    "created": "2026-02-08",
                    "metadata": {},
                },
                {
                    "id": "GR-testing",
                    "type": "guardrail",
                    "content": "Testing guardrail: >90% coverage required",
                    "source_file": "governance/guardrails.md",
                    "created": "2026-02-08",
                    "metadata": {},
                },
                {
                    "id": "mod-context",
                    "type": "module",
                    "content": "Context module provides graph and query",
                    "source_file": "governance/architecture/modules/context.md",
                    "created": "2026-02-08",
                    "metadata": {},
                },
            ],
            "edges": [
                {
                    "source": "mod-memory",
                    "target": "GR-testing",
                    "type": "constrained_by",
                    "weight": 1.0,
                    "key": 0,
                },
                {
                    "source": "mod-memory",
                    "target": "mod-context",
                    "type": "depends_on",
                    "weight": 1.0,
                    "key": 0,
                },
            ],
        }

        index_path = memory_dir / "index.json"
        index_path.write_text(json.dumps(graph_data, indent=2))
        return index_path

    def test_edge_types_flag_filters_neighbors(
        self, graph_with_edges: Path, tmp_path: Path
    ) -> None:
        """--edge-types filters to only matching edge types."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(
                app,
                [
                    "memory",
                    "query",
                    "mod-memory",
                    "--strategy",
                    "concept_lookup",
                    "--edge-types",
                    "constrained_by",
                ],
            )

            assert result.exit_code == 0
            assert "GR-testing" in result.stdout
            assert "mod-context" not in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_edge_types_flag_multiple(
        self, graph_with_edges: Path, tmp_path: Path
    ) -> None:
        """--edge-types accepts comma-separated values."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(
                app,
                [
                    "memory",
                    "query",
                    "mod-memory",
                    "--strategy",
                    "concept_lookup",
                    "--edge-types",
                    "constrained_by,depends_on",
                ],
            )

            assert result.exit_code == 0
            assert "GR-testing" in result.stdout
            assert "mod-context" in result.stdout
        finally:
            os.chdir(original_cwd)
