"""Tests for doctor integration in session start CLI."""

from __future__ import annotations

import time
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from raise_cli.cli.commands.session import session_app
from raise_cli.onboarding.profile import DeveloperProfile
from raise_cli.session.doctor import format_findings

runner = CliRunner()


def _setup_project(tmp_path: Path) -> Path:
    """Create minimal project structure for session start."""
    personal = tmp_path / ".raise" / "rai" / "personal"
    personal.mkdir(parents=True)
    (personal / "sessions").mkdir()
    return tmp_path


def _mock_profile() -> DeveloperProfile:
    return DeveloperProfile(name="Test Dev")


class TestSessionStartRunsDoctor:
    """Doctor runs during session start when project is specified."""

    def test_start_shows_clean_health(self, tmp_path: Path) -> None:
        project = _setup_project(tmp_path)

        with (
            patch(
                "raise_cli.cli.commands.session.load_developer_profile",
                return_value=_mock_profile(),
            ),
            patch("raise_cli.cli.commands.session.save_developer_profile"),
            patch("raise_cli.cli.commands.session.create_emitter"),
        ):
            result = runner.invoke(
                session_app, ["start", "--project", str(project)]
            )

        assert result.exit_code == 0
        assert "health" in result.output.lower() or "session" in result.output.lower()

    def test_start_shows_findings(self, tmp_path: Path) -> None:
        project = _setup_project(tmp_path)

        # Create stale output
        personal = project / ".raise" / "rai" / "personal"
        output = personal / "session-output.yaml"
        output.write_text("old data")
        import os

        old_time = time.time() - (26 * 3600)
        os.utime(output, (old_time, old_time))

        with (
            patch(
                "raise_cli.cli.commands.session.load_developer_profile",
                return_value=_mock_profile(),
            ),
            patch("raise_cli.cli.commands.session.save_developer_profile"),
            patch("raise_cli.cli.commands.session.create_emitter"),
        ):
            result = runner.invoke(
                session_app, ["start", "--project", str(project)]
            )

        assert result.exit_code == 0
        # Should mention the stale output finding
        assert "stale" in result.output.lower() or "session-output" in result.output.lower()

    def test_no_doctor_flag_skips(self, tmp_path: Path) -> None:
        project = _setup_project(tmp_path)

        # Create stale output that would normally be detected
        personal = project / ".raise" / "rai" / "personal"
        output = personal / "session-output.yaml"
        output.write_text("old data")
        import os

        old_time = time.time() - (26 * 3600)
        os.utime(output, (old_time, old_time))

        with (
            patch(
                "raise_cli.cli.commands.session.load_developer_profile",
                return_value=_mock_profile(),
            ),
            patch("raise_cli.cli.commands.session.save_developer_profile"),
            patch("raise_cli.cli.commands.session.create_emitter"),
        ):
            result = runner.invoke(
                session_app, ["start", "--project", str(project), "--no-doctor"]
            )

        assert result.exit_code == 0
        # Should NOT mention findings
        assert "stale" not in result.output.lower()


class TestFormatFindings:
    """format_findings() produces human-readable output."""

    def test_format_empty(self) -> None:
        output = format_findings([], [])
        assert "clean" in output.lower() or "health" in output.lower()

    def test_format_with_findings(self) -> None:
        from raise_cli.session.doctor import Finding

        findings = [
            Finding(
                category="stale_output",
                severity="info",
                description="Stale session-output.yaml (26h old)",
                detail="1.2 KB — safe to remove",
                safe_to_auto_clean=True,
                action="Remove stale output file",
            )
        ]
        output = format_findings(findings, ["Removed stale session-output.yaml"])
        assert "stale" in output.lower()
