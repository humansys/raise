"""Tests for signal CLI commands.

The signal group owns telemetry emit commands (emit-work, emit-session,
emit-calibration). Extracted from the `memory` God Object in RAISE-247 (ADR-038).
"""

import os
from pathlib import Path

from typer.testing import CliRunner

from raise_cli.cli.main import app

runner = CliRunner()


class TestSignalEmitWork:
    """Tests for `rai signal emit-work` command."""

    def test_emit_work_start(self, tmp_path: Path) -> None:
        """Test emit-work start event."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            telemetry_dir = tmp_path / ".raise" / "rai" / "telemetry"
            telemetry_dir.mkdir(parents=True)

            result = runner.invoke(
                app,
                [
                    "signal",
                    "emit-work",
                    "story",
                    "S247.3",
                    "-e",
                    "start",
                    "-p",
                    "design",
                ],
            )

            assert result.exit_code == 0
            assert "started" in result.stdout
            assert "Story S247.3" in result.stdout
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
                    "signal",
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
                    "signal",
                    "emit-work",
                    "story",
                    "S1.2",
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
                ["signal", "emit-work", "invalid", "X1", "-e", "start"],
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
                ["signal", "emit-work", "story", "S1.1", "-e", "invalid"],
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
                    "signal",
                    "emit-work",
                    "story",
                    "S1.1",
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


class TestSignalEmitSession:
    """Tests for `rai signal emit-session` command."""

    def test_emit_session_basic(self, tmp_path: Path) -> None:
        """Test basic emit-session command."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            telemetry_dir = tmp_path / ".raise" / "rai" / "telemetry"
            telemetry_dir.mkdir(parents=True)

            result = runner.invoke(
                app,
                ["signal", "emit-session", "-t", "story", "-o", "success"],
            )

            assert result.exit_code == 0
            assert "Session event recorded" in result.stdout
        finally:
            os.chdir(original_cwd)

    def test_emit_session_with_details(self, tmp_path: Path) -> None:
        """Test emit-session with duration and stories."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            telemetry_dir = tmp_path / ".raise" / "rai" / "telemetry"
            telemetry_dir.mkdir(parents=True)

            result = runner.invoke(
                app,
                [
                    "signal",
                    "emit-session",
                    "-t",
                    "research",
                    "-o",
                    "partial",
                    "-d",
                    "90",
                    "-f",
                    "S1.1,S1.2",
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
                ["signal", "emit-session", "-o", "invalid"],
            )

            assert result.exit_code == 7
            assert "Invalid outcome" in result.output
        finally:
            os.chdir(original_cwd)


class TestSignalEmitCalibration:
    """Tests for `rai signal emit-calibration` command."""

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
                    "signal",
                    "emit-calibration",
                    "S1.1",
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
                    "signal",
                    "emit-calibration",
                    "S1.2",
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
                    "signal",
                    "emit-calibration",
                    "S1.3",
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
                    "signal",
                    "emit-calibration",
                    "S1.1",
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
                    "signal",
                    "emit-calibration",
                    "S1.1",
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
                    "signal",
                    "emit-calibration",
                    "S1.1",
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


class TestSignalSessionRouting:
    """Tests for --session flag routing signals to per-session directories."""

    def test_emit_work_with_session_flag(self, tmp_path: Path) -> None:
        """Test emit-work with --session writes to per-session directory."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(
                app,
                [
                    "signal",
                    "emit-work",
                    "story",
                    "S1.1",
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
            assert "S1.1" in content
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
                    "signal",
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
                    "signal",
                    "emit-calibration",
                    "S1.1",
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
