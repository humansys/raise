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


class TestMemoryHelp:
    """Tests for memory command help."""

    def test_memory_help(self) -> None:
        """Test memory command shows help."""
        result = runner.invoke(app, ["memory", "--help"])
        assert result.exit_code == 0
        assert "memory" in result.stdout.lower()


class TestMemoryAddPatternCommand:
    """Tests for `rai memory add-pattern` command."""

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
            content = patterns_file.read_text(encoding="utf-8")
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
            content = patterns_file.read_text(encoding="utf-8")
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

    def test_add_pattern_deprecation_warning(self, tmp_path: Path) -> None:
        """Test that rai memory add-pattern emits a deprecation warning."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(
                app,
                ["memory", "add-pattern", "Test deprecation"],
            )

            assert result.exit_code == 0
            assert "DEPRECATED" in result.output
            assert "rai pattern add" in result.output
        finally:
            os.chdir(original_cwd)


class TestMemoryReinforceCommand:
    """Tests for `rai memory reinforce` deprecation shim."""

    def test_reinforce_deprecation_warning(self, tmp_path: Path) -> None:
        """Test that rai memory reinforce emits a deprecation warning."""
        import json

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            memory_dir = tmp_path / ".raise" / "rai" / "memory"
            memory_dir.mkdir(parents=True)
            pattern_data = {
                "id": "PAT-E-001",
                "content": "Test pattern",
                "sub_type": "process",
                "context": [],
                "positives": 0,
                "negatives": 0,
                "evaluations": 0,
                "created": "2026-01-01",
                "learned_from": None,
            }
            (memory_dir / "patterns.jsonl").write_text(
                json.dumps(pattern_data) + "\n", encoding="utf-8"
            )

            result = runner.invoke(
                app,
                [
                    "memory",
                    "reinforce",
                    "PAT-E-001",
                    "--vote",
                    "1",
                    "--memory-dir",
                    str(memory_dir),
                ],
            )

            assert result.exit_code == 0
            assert "DEPRECATED" in result.output
            assert "rai pattern reinforce" in result.output
        finally:
            os.chdir(original_cwd)


class TestMemoryEmitWorkCommand:
    """Tests for `rai memory emit-work` command."""

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


class TestEmitSessionRouting:
    """Tests for --session flag routing signals to per-session directories."""

    def test_emit_work_with_session_flag(self, tmp_path: Path) -> None:
        """Test emit-work with --session writes to per-session directory."""
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
                    "design",
                    "--session",
                    "SES-999",
                ],
            )

            assert result.exit_code == 0
            assert "started" in result.stdout
            # Signal should land in per-session directory
            session_signals = (
                tmp_path
                / ".raise"
                / "rai"
                / "personal"
                / "sessions"
                / "SES-999"
                / "signals.jsonl"
            )
            assert session_signals.exists()
            content = session_signals.read_text(encoding="utf-8")
            assert "F1.1" in content
        finally:
            os.chdir(original_cwd)

    def test_emit_session_with_session_flag(self, tmp_path: Path) -> None:
        """Test emit-session with --session writes to per-session directory."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(
                app,
                [
                    "memory",
                    "emit-session",
                    "-t",
                    "story",
                    "-o",
                    "success",
                    "--session",
                    "SES-999",
                ],
            )

            assert result.exit_code == 0
            session_signals = (
                tmp_path
                / ".raise"
                / "rai"
                / "personal"
                / "sessions"
                / "SES-999"
                / "signals.jsonl"
            )
            assert session_signals.exists()
        finally:
            os.chdir(original_cwd)

    def test_emit_calibration_with_session_flag(self, tmp_path: Path) -> None:
        """Test emit-calibration with --session writes to per-session directory."""
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
                    "15",
                    "--session",
                    "SES-999",
                ],
            )

            assert result.exit_code == 0
            session_signals = (
                tmp_path
                / ".raise"
                / "rai"
                / "personal"
                / "sessions"
                / "SES-999"
                / "signals.jsonl"
            )
            assert session_signals.exists()
        finally:
            os.chdir(original_cwd)

    def test_emit_work_with_session_env_var(self, tmp_path: Path) -> None:
        """Test emit-work falls back to RAI_SESSION_ID env var."""
        original_cwd = os.getcwd()
        original_env = os.environ.get("RAI_SESSION_ID")
        try:
            os.chdir(tmp_path)
            os.environ["RAI_SESSION_ID"] = "SES-888"
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
                    "design",
                ],
            )

            assert result.exit_code == 0
            session_signals = (
                tmp_path
                / ".raise"
                / "rai"
                / "personal"
                / "sessions"
                / "SES-888"
                / "signals.jsonl"
            )
            assert session_signals.exists()
        finally:
            os.chdir(original_cwd)
            if original_env is None:
                os.environ.pop("RAI_SESSION_ID", None)
            else:
                os.environ["RAI_SESSION_ID"] = original_env

    def test_emit_work_session_flag_overrides_env(self, tmp_path: Path) -> None:
        """Test --session flag takes priority over RAI_SESSION_ID."""
        original_cwd = os.getcwd()
        original_env = os.environ.get("RAI_SESSION_ID")
        try:
            os.chdir(tmp_path)
            os.environ["RAI_SESSION_ID"] = "SES-888"
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
                    "design",
                    "--session",
                    "SES-777",
                ],
            )

            assert result.exit_code == 0
            # Flag should win over env var
            flag_signals = (
                tmp_path
                / ".raise"
                / "rai"
                / "personal"
                / "sessions"
                / "SES-777"
                / "signals.jsonl"
            )
            env_signals = (
                tmp_path
                / ".raise"
                / "rai"
                / "personal"
                / "sessions"
                / "SES-888"
                / "signals.jsonl"
            )
            assert flag_signals.exists()
            assert not env_signals.exists()
        finally:
            os.chdir(original_cwd)
            if original_env is None:
                os.environ.pop("RAI_SESSION_ID", None)
            else:
                os.environ["RAI_SESSION_ID"] = original_env


class TestMemoryEmitSessionCommand:
    """Tests for `rai memory emit-session` command."""

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
    """Tests for `rai memory emit-calibration` command."""

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


class TestMemoryEmitSignalShims:
    """Tests for `rai memory emit-*` deprecation shims (extracted to signal group)."""

    def test_emit_work_deprecation_warning(self, tmp_path: Path) -> None:
        """Test that rai memory emit-work shows deprecation warning with correct target."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            telemetry_dir = tmp_path / ".raise" / "rai" / "telemetry"
            telemetry_dir.mkdir(parents=True)

            result = runner.invoke(
                app,
                ["memory", "emit-work", "story", "S1", "-e", "start", "-p", "design"],
            )

            assert result.exit_code == 0
            assert "DEPRECATED" in result.output
            assert "rai signal emit-work" in result.output
        finally:
            os.chdir(original_cwd)

    def test_emit_session_deprecation_warning(self, tmp_path: Path) -> None:
        """Test that rai memory emit-session shows deprecation warning with correct target."""
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
            assert "DEPRECATED" in result.output
            assert "rai signal emit-session" in result.output
        finally:
            os.chdir(original_cwd)

    def test_emit_calibration_deprecation_warning(self, tmp_path: Path) -> None:
        """Test that rai memory emit-calibration shows deprecation warning with correct target."""
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
                    "S1",
                    "-s",
                    "S",
                    "-e",
                    "30",
                    "-a",
                    "22",
                ],
            )

            assert result.exit_code == 0
            assert "DEPRECATED" in result.output
            assert "rai signal emit-calibration" in result.output
        finally:
            os.chdir(original_cwd)
