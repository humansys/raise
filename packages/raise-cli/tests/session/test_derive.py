"""Tests for GitStateDeriver — git-only state derivation backend."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from raise_cli.schemas.session_state import CurrentWork
from raise_cli.session.derive import GitStateDeriver
from raise_cli.session.protocols import StateDeriver


class TestGitStateDeriverProtocol:
    """Verify GitStateDeriver satisfies the StateDeriver protocol."""

    def test_satisfies_protocol(self) -> None:
        assert isinstance(GitStateDeriver(), StateDeriver)


class TestCurrentWork:
    """Test current_work derivation from git state."""

    def test_release_branch(self, tmp_path: Path) -> None:
        deriver = GitStateDeriver()
        with (
            patch.object(deriver, "_git_current_branch", return_value="release/2.4.0"),
            patch.object(deriver, "_find_active_epic", return_value="E1248"),
            patch.object(deriver, "_resolve_project_root", return_value=tmp_path),
            patch.object(deriver, "_infer_phase", return_value="implementing"),
        ):
            work = deriver.current_work(tmp_path)
        assert work.release == "v2.4.0"
        assert work.epic == "E1248"
        assert work.story == ""
        assert work.branch == "release/2.4.0"
        assert work.phase == "implementing"

    def test_story_branch(self, tmp_path: Path) -> None:
        deriver = GitStateDeriver()
        with (
            patch.object(
                deriver,
                "_git_current_branch",
                return_value="story/s1248.1/session-protocols-git-deriver",
            ),
            patch.object(deriver, "_find_active_epic", return_value="E1248"),
            patch.object(deriver, "_resolve_project_root", return_value=tmp_path),
            patch.object(deriver, "_infer_phase", return_value="implementing"),
        ):
            work = deriver.current_work(tmp_path)
        assert work.release == ""
        assert work.story == "S1248.1"
        assert work.branch == "story/s1248.1/session-protocols-git-deriver"

    def test_main_branch(self, tmp_path: Path) -> None:
        deriver = GitStateDeriver()
        with (
            patch.object(deriver, "_git_current_branch", return_value="main"),
            patch.object(deriver, "_find_active_epic", return_value=""),
            patch.object(deriver, "_resolve_project_root", return_value=tmp_path),
            patch.object(deriver, "_infer_phase", return_value=""),
        ):
            work = deriver.current_work(tmp_path)
        assert work.release == ""
        assert work.epic == ""
        assert work.story == ""
        assert work.branch == "main"

    def test_detached_head(self, tmp_path: Path) -> None:
        deriver = GitStateDeriver()
        with (
            patch.object(deriver, "_git_current_branch", return_value=""),
            patch.object(deriver, "_find_active_epic", return_value=""),
            patch.object(deriver, "_resolve_project_root", return_value=tmp_path),
            patch.object(deriver, "_infer_phase", return_value=""),
        ):
            work = deriver.current_work(tmp_path)
        assert work == CurrentWork(branch="")


class TestParseRelease:
    """Test release version extraction from branch name."""

    def test_release_branch(self) -> None:
        assert GitStateDeriver._parse_release("release/2.4.0") == "v2.4.0"

    def test_release_with_prefix(self) -> None:
        assert GitStateDeriver._parse_release("release/3.0.0") == "v3.0.0"

    def test_non_release_branch(self) -> None:
        assert GitStateDeriver._parse_release("main") == ""

    def test_story_branch(self) -> None:
        assert GitStateDeriver._parse_release("story/s1248.1/foo") == ""

    def test_hotfix_branch(self) -> None:
        assert GitStateDeriver._parse_release("release/2.3.x") == "v2.3.x"


class TestParseStory:
    """Test story ID extraction from branch name."""

    def test_story_branch(self) -> None:
        assert (
            GitStateDeriver._parse_story("story/s1248.1/session-protocols")
            == "S1248.1"
        )

    def test_story_branch_uppercase(self) -> None:
        assert GitStateDeriver._parse_story("story/S100.3/something") == "S100.3"

    def test_non_story_branch(self) -> None:
        assert GitStateDeriver._parse_story("release/2.4.0") == ""

    def test_main_branch(self) -> None:
        assert GitStateDeriver._parse_story("main") == ""


class TestFindActiveEpic:
    """Test active epic discovery from scope.md files."""

    def test_finds_in_progress_epic(self, tmp_path: Path) -> None:
        epic_dir = tmp_path / "work" / "epics" / "e1248-git-first-session-state"
        epic_dir.mkdir(parents=True)
        (epic_dir / "scope.md").write_text(
            "# E1248\n\n> **Status:** in-progress\n> **Target:** v2.4.0\n"
        )
        deriver = GitStateDeriver()
        assert deriver._find_active_epic(tmp_path) == "E1248"

    def test_skips_complete_epic(self, tmp_path: Path) -> None:
        epic_dir = tmp_path / "work" / "epics" / "e100-old-epic"
        epic_dir.mkdir(parents=True)
        (epic_dir / "scope.md").write_text(
            "# E100\n\n> **Status:** complete\n"
        )
        deriver = GitStateDeriver()
        assert deriver._find_active_epic(tmp_path) == ""

    def test_no_epics_dir(self, tmp_path: Path) -> None:
        deriver = GitStateDeriver()
        assert deriver._find_active_epic(tmp_path) == ""

    def test_multiple_in_progress_returns_first(self, tmp_path: Path) -> None:
        for eid in ("e10-alpha", "e20-beta"):
            d = tmp_path / "work" / "epics" / eid
            d.mkdir(parents=True)
            (d / "scope.md").write_text(
                f"# {eid.split('-')[0].upper()}\n\n> **Status:** in-progress\n"
            )
        deriver = GitStateDeriver()
        result = deriver._find_active_epic(tmp_path)
        assert result in ("E10", "E20")


class TestInferPhase:
    """Test phase inference from git log."""

    def test_merge_commit_means_reviewing(self) -> None:
        deriver = GitStateDeriver()
        log_lines = [
            "abc1234|Merge branch 'story/s1248.1/foo' into release/2.4.0|Emilio|2026-04-03T12:00:00",
        ]
        with patch.object(deriver, "_git_log_lines", return_value=log_lines):
            assert deriver._infer_phase(Path("."), "release/2.4.0") == "reviewing"

    def test_recent_commits_mean_implementing(self) -> None:
        deriver = GitStateDeriver()
        log_lines = [
            "abc1234|feat: add something|Emilio|2026-04-03T12:00:00",
            "def5678|test: add tests|Emilio|2026-04-03T11:00:00",
        ]
        with patch.object(deriver, "_git_log_lines", return_value=log_lines):
            assert deriver._infer_phase(Path("."), "story/s1248.1/foo") == "implementing"

    def test_no_commits_means_planning(self) -> None:
        deriver = GitStateDeriver()
        with patch.object(deriver, "_git_log_lines", return_value=[]):
            assert deriver._infer_phase(Path("."), "story/s1248.1/foo") == "planning"


class TestResolveProjectRoot:
    """Test worktree-aware project root resolution."""

    def test_normal_repo(self, tmp_path: Path) -> None:
        deriver = GitStateDeriver()
        # In a normal repo, git-common-dir returns ".git"
        with patch.object(
            deriver,
            "_git_common_dir",
            return_value=str(tmp_path / ".git"),
        ):
            root = deriver._resolve_project_root(tmp_path)
        assert root == tmp_path

    def test_worktree(self, tmp_path: Path) -> None:
        deriver = GitStateDeriver()
        main_repo = tmp_path / "main-repo"
        main_repo.mkdir()
        worktree = tmp_path / "worktree"
        worktree.mkdir()
        # In a worktree, git-common-dir points to main repo's .git/
        with patch.object(
            deriver,
            "_git_common_dir",
            return_value=str(main_repo / ".git"),
        ):
            root = deriver._resolve_project_root(worktree)
        assert root == main_repo
