"""Tests for standalone `rai session doctor` subcommand."""

from __future__ import annotations

import time
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from raise_cli.cli.commands.session import session_app

runner = CliRunner()


class TestDoctorSubcommand:
    """rai session doctor runs a full diagnostic scan."""

    def test_doctor_exists(self) -> None:
        """Doctor subcommand exists and shows help."""
        result = runner.invoke(session_app, ["doctor", "--help"])
        assert result.exit_code == 0
        assert "doctor" in result.output.lower() or "diagnos" in result.output.lower()

    def test_doctor_clean_output(self, tmp_path: Path) -> None:
        """Doctor shows 'all clear' when no issues."""
        personal = tmp_path / ".raise" / "rai" / "personal"
        personal.mkdir(parents=True)
        (personal / "sessions").mkdir()

        result = runner.invoke(
            session_app, ["doctor", "--project", str(tmp_path)]
        )

        assert result.exit_code == 0
        assert "clean" in result.output.lower() or "clear" in result.output.lower()

    def test_doctor_shows_findings(self, tmp_path: Path) -> None:
        """Doctor shows findings when issues detected."""
        personal = tmp_path / ".raise" / "rai" / "personal"
        personal.mkdir(parents=True)
        (personal / "sessions").mkdir()

        # Create stale output
        output = personal / "session-output.yaml"
        output.write_text("old data")
        import os

        old_time = time.time() - (26 * 3600)
        os.utime(output, (old_time, old_time))

        result = runner.invoke(
            session_app, ["doctor", "--project", str(tmp_path)]
        )

        assert result.exit_code == 0
        assert "stale" in result.output.lower() or "finding" in result.output.lower()

    def test_doctor_shows_derivation_status(self, tmp_path: Path) -> None:
        """Doctor shows git state derivation result."""
        personal = tmp_path / ".raise" / "rai" / "personal"
        personal.mkdir(parents=True)
        (personal / "sessions").mkdir()

        from raise_cli.schemas.session_state import CurrentWork

        mock_work = CurrentWork(
            epic="E1248", story="S1248.5", phase="implementing", branch="story/s1248.5/session-doctor"
        )

        with patch(
            "raise_cli.cli.commands.session._derive_current_work_for_doctor",
            return_value=mock_work,
        ):
            result = runner.invoke(
                session_app, ["doctor", "--project", str(tmp_path)]
            )

        assert result.exit_code == 0
        assert "E1248" in result.output or "derivation" in result.output.lower()
