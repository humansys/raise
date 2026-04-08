"""Integration tests for bundle assembly with git-derived state (S1248.3).

Validates that assemble_context_bundle() in a real git repo produces output
with correct branch info derived from git, not from YAML.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from raise_cli.onboarding.profile import DeveloperProfile
from raise_cli.schemas.session_state import CurrentWork, LastSession, SessionState
from raise_cli.session.bundle import assemble_orientation, derive_current_work


@pytest.mark.integration
class TestBundleWithGitDerived:
    """Bundle assembly uses git-derived state in a real repo."""

    def test_derive_current_work_returns_valid_result(self) -> None:
        """derive_current_work() returns non-None in a real git repo."""
        repo_root = Path(__file__).resolve().parents[4]  # packages/raise-cli/tests/session -> repo root
        result = derive_current_work(repo_root)
        assert result is not None
        assert isinstance(result, CurrentWork)
        assert result.branch != ""  # should detect current branch

    def test_orientation_includes_git_branch(self) -> None:
        """assemble_orientation() output includes git-derived branch."""
        repo_root = Path(__file__).resolve().parents[4]
        profile = DeveloperProfile(name="Test")
        state = SessionState(
            current_work=CurrentWork(
                epic="E-yaml", story="S-yaml.1", phase="old", branch="old-branch"
            ),
            last_session=LastSession(
                id="SES-001",
                date=date(2026, 4, 3),
                developer="Test",
                summary="test",
            ),
        )

        result = assemble_orientation(profile, state, repo_root)

        # Should contain git-derived branch, NOT the YAML "old-branch"
        assert "old-branch" not in result
        # Should contain the actual branch (story/s1248.3/... or release/2.4.0)
        assert "Branch:" in result

    def test_derive_returns_none_for_non_git_dir(self, tmp_path: Path) -> None:
        """derive_current_work() returns None for non-git directories."""
        result = derive_current_work(tmp_path)
        assert result is None
