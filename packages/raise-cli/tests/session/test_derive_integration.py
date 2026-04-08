"""Integration tests for GitStateDeriver against the real raise-commons repo.

These tests run actual git commands — no mocking. They validate that
the deriver works correctly in a real repository context.

Marked with @pytest.mark.integration for CI filtering.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from raise_cli.session.derive import GitStateDeriver

# Resolve to the repo root (this file is deep in the tree)
_REPO_ROOT = Path(__file__).resolve().parents[4]


@pytest.mark.integration
class TestGitStateDeriverIntegration:
    """Run GitStateDeriver against the actual raise-commons repo."""

    def test_derives_current_branch(self) -> None:
        deriver = GitStateDeriver()
        work = deriver.current_work(_REPO_ROOT)
        # We're on some branch — should never be empty in a real repo
        assert work.branch != ""

    def test_finds_active_epic(self) -> None:
        deriver = GitStateDeriver()
        work = deriver.current_work(_REPO_ROOT)
        # Should be empty or a valid epic ID (E + digits)
        assert work.epic == "" or (work.epic.startswith("E") and work.epic[1:].isdigit())

    def test_recent_activity_returns_entries(self) -> None:
        deriver = GitStateDeriver()
        entries = deriver.recent_activity(_REPO_ROOT, limit=5)
        assert len(entries) > 0
        # Each entry should have required fields
        for entry in entries:
            assert entry.commit_hash != ""
            assert entry.subject != ""
            assert entry.author != ""

    def test_branch_parsing_consistency(self) -> None:
        deriver = GitStateDeriver()
        work = deriver.current_work(_REPO_ROOT)
        # If on a story branch, story should be set
        if work.branch.startswith("story/"):
            assert work.story != ""
        # If on a release branch, release should be set
        if work.branch.startswith("release/"):
            assert work.release != ""

    def test_resolve_project_root(self) -> None:
        deriver = GitStateDeriver()
        root = deriver._resolve_project_root(_REPO_ROOT)  # pyright: ignore[reportPrivateUsage]
        # Root should contain .raise/ directory
        assert (root / ".raise").is_dir()

    def test_phase_is_valid(self) -> None:
        deriver = GitStateDeriver()
        work = deriver.current_work(_REPO_ROOT)
        assert work.phase in ("planning", "implementing", "reviewing", "")
