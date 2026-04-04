"""Tests for git-derived current_work in bundle assembly (S1248.3)."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from unittest.mock import patch

from raise_cli.onboarding.profile import DeveloperProfile
from raise_cli.schemas.session_state import CurrentWork, LastSession, SessionState
from raise_cli.session.bundle_formatters import format_work_section


class TestFormatWorkSectionWithOverride:
    """format_work_section accepts optional current_work override."""

    def test_override_takes_precedence_over_state(self) -> None:
        state = _make_state(
            epic="E100", story="S100.1", phase="design", branch="old-branch"
        )
        override = CurrentWork(
            epic="E1248", story="S1248.3", phase="implementing", branch="story/s1248.3/x"
        )
        result = format_work_section(state, current_work=override)
        assert "S1248.3" in result
        assert "implementing" in result
        assert "story/s1248.3/x" in result
        # Old values should NOT appear
        assert "S100.1" not in result
        assert "old-branch" not in result

    def test_none_override_uses_state(self) -> None:
        state = _make_state(
            epic="E100", story="S100.1", phase="design", branch="release/2.4.0"
        )
        result = format_work_section(state, current_work=None)
        assert "S100.1" in result
        assert "design" in result

    def test_no_override_arg_is_backward_compatible(self) -> None:
        state = _make_state(
            epic="E100", story="S100.1", phase="design", branch="release/2.4.0"
        )
        # Call without current_work kwarg — existing behavior unchanged
        result = format_work_section(state)
        assert "S100.1" in result


class TestAssembleOrientationDerived:
    """assemble_orientation uses GitStateDeriver when available."""

    def test_uses_git_derived_work(self, tmp_path: Path) -> None:
        from raise_cli.session.bundle import assemble_orientation

        state = _make_state(
            epic="E-old", story="S-old.1", phase="planning", branch="old"
        )
        profile = _make_profile()

        derived = CurrentWork(
            release="v2.4.0",
            epic="E1248",
            story="S1248.3",
            phase="implementing",
            branch="story/s1248.3/bundle",
        )

        with patch(
            "raise_cli.session.bundle.derive_current_work",
            return_value=derived,
        ):
            result = assemble_orientation(profile, state, tmp_path)

        assert "S1248.3" in result
        assert "implementing" in result
        # Old YAML values should NOT appear in work section
        assert "S-old.1" not in result

    def test_falls_back_on_derivation_error(self, tmp_path: Path) -> None:
        from raise_cli.session.bundle import assemble_orientation

        state = _make_state(
            epic="E100", story="S100.1", phase="design", branch="release/2.4.0"
        )
        profile = _make_profile()

        with patch(
            "raise_cli.session.bundle.derive_current_work",
            side_effect=RuntimeError("not a git repo"),
        ):
            result = assemble_orientation(profile, state, tmp_path)

        # Should fall back to YAML state
        assert "S100.1" in result
        assert "design" in result

    def test_falls_back_when_derive_returns_none(self, tmp_path: Path) -> None:
        from raise_cli.session.bundle import assemble_orientation

        state = _make_state(
            epic="E100", story="S100.1", phase="design", branch="release/2.4.0"
        )
        profile = _make_profile()

        with patch(
            "raise_cli.session.bundle.derive_current_work",
            return_value=None,
        ):
            result = assemble_orientation(profile, state, tmp_path)

        assert "S100.1" in result


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_state(
    epic: str = "E1",
    story: str = "S1.1",
    phase: str = "implement",
    branch: str = "release/2.4.0",
) -> SessionState:
    return SessionState(
        current_work=CurrentWork(
            epic=epic, story=story, phase=phase, branch=branch
        ),
        last_session=LastSession(
            id="SES-001",
            date=date(2026, 4, 3),
            developer="Test",
            summary="test session",
        ),
    )


def _make_profile() -> DeveloperProfile:
    return DeveloperProfile(name="Test Developer")
