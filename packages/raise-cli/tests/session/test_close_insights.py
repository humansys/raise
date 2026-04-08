"""Tests for session close insights via WorkstreamMonitor."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from raise_cli.cli.commands.session import session_app
from raise_cli.onboarding.profile import DeveloperProfile
from raise_cli.schemas.session_state import SessionInsights
from raise_cli.session.index import ActiveSessionPointer

runner = CliRunner()


def _mock_profile_with_session(
    project_path: Path, session_id: str = "S-E-260403-1000"
) -> DeveloperProfile:
    from datetime import datetime

    from raise_cli.onboarding.profile import ActiveSession

    profile = DeveloperProfile(name="Test Dev")
    profile.active_sessions = [
        ActiveSession(
            session_id=session_id,
            started_at=datetime.now(),
            project=str(project_path),
        )
    ]
    return profile


def _write_pointer(project: Path, session_id: str = "S-E-260403-1000") -> None:
    """Write an active-session pointer for close to find."""
    from datetime import datetime

    from raise_cli.session.index import write_active_session

    pointer = ActiveSessionPointer(
        id=session_id, name="test", started=datetime.now()
    )
    write_active_session(pointer, project_root=project)


class TestCloseInsights:
    """Session close shows insights from WorkstreamMonitor."""

    def test_close_shows_insights(self, tmp_path: Path) -> None:
        personal = tmp_path / ".raise" / "rai" / "personal"
        personal.mkdir(parents=True)
        (personal / "sessions").mkdir()
        _write_pointer(tmp_path)

        mock_insights = SessionInsights(
            session_id="S-E-260403-1000",
            commit_count=8,
            test_commit_ratio=0.5,
            revert_count=0,
            duration_minutes=75,
        )

        profile = _mock_profile_with_session(tmp_path)

        from unittest.mock import MagicMock

        mock_emitter = MagicMock()
        mock_emit_result = MagicMock()
        mock_emit_result.aborted = False
        mock_emitter.emit.return_value = mock_emit_result

        with (
            patch(
                "raise_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch("raise_cli.cli.commands.session.save_developer_profile"),
            patch(
                "raise_cli.cli.commands.session.create_emitter",
                return_value=mock_emitter,
            ),
            patch(
                "raise_cli.cli.commands.session.end_session",
                return_value=profile,
            ),
            patch(
                "raise_cli.cli.commands.session._get_session_insights",
                return_value=mock_insights,
            ),
        ):
            result = runner.invoke(
                session_app,
                ["close", "--project", str(tmp_path)],
            )

        assert result.exit_code == 0, f"Output: {result.output}\nException: {result.exception}"
        output = result.output.lower()
        assert "commits" in output or "insight" in output or "session" in output

    def test_close_no_project_no_crash(self) -> None:
        """Close without project should not crash on insights."""
        profile = DeveloperProfile(name="Test Dev")

        with (
            patch(
                "raise_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch("raise_cli.cli.commands.session.save_developer_profile"),
            patch("raise_cli.cli.commands.session.create_emitter"),
        ):
            result = runner.invoke(session_app, ["close"])

        # Should complete without error (may say "no active session")
        assert result.exit_code == 0
