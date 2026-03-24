"""Tests for core.tools module."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from raise_cli.core.tools import (
    GitStatus,
    SearchMatch,
    ToolResult,
    check_tool,
    git_branch,
    git_diff,
    git_root,
    git_status,
    require_tool,
    rg_search,
    run_tool,
    sg_search,
)
from raise_cli.exceptions import DependencyError


class TestToolResult:
    """Tests for ToolResult dataclass."""

    def test_success_true_when_returncode_zero(self) -> None:
        result = ToolResult(returncode=0, stdout="output", stderr="")
        assert result.success is True

    def test_success_false_when_returncode_nonzero(self) -> None:
        result = ToolResult(returncode=1, stdout="", stderr="error")
        assert result.success is False


class TestCheckTool:
    """Tests for check_tool function."""

    def test_returns_true_for_existing_tool(self) -> None:
        # python3 is guaranteed to exist in the CI image (python:3.12-slim)
        assert check_tool("python3") is True

    def test_returns_false_for_nonexistent_tool(self) -> None:
        assert check_tool("nonexistent_tool_12345") is False


class TestRequireTool:
    """Tests for require_tool function."""

    def test_does_not_raise_for_existing_tool(self) -> None:
        require_tool("python3")  # Should not raise

    def test_raises_dependency_error_for_missing_tool(self) -> None:
        with pytest.raises(DependencyError) as exc_info:
            require_tool("nonexistent_tool_12345")

        assert "not installed" in str(exc_info.value)

    def test_provides_hint_for_known_tools(self) -> None:
        with patch("raise_cli.core.tools.check_tool", return_value=False):
            with pytest.raises(DependencyError) as exc_info:
                require_tool("git")

            assert exc_info.value.hint is not None
            assert "git-scm.com" in exc_info.value.hint


class TestRunTool:
    """Tests for run_tool function."""

    def test_raises_on_empty_args(self) -> None:
        with pytest.raises(ValueError, match="must not be empty"):
            run_tool([])

    def test_captures_stdout(self) -> None:
        result = run_tool(["echo", "hello"])
        assert result.stdout == "hello"
        assert result.returncode == 0

    def test_captures_stderr(self) -> None:
        # Using python3 to write to stderr — guaranteed available in CI image
        result = run_tool(
            ["python3", "-c", "import sys; sys.stderr.write('error'); sys.exit(1)"]
        )
        assert result.returncode != 0
        assert result.stderr != ""

    def test_raises_on_missing_tool(self) -> None:
        with pytest.raises(DependencyError):
            run_tool(["nonexistent_tool_12345"])


class TestGitRoot:
    """Tests for git_root function."""

    def test_returns_path_in_repo(self, tmp_path: Path) -> None:
        # Create a git repo
        (tmp_path / ".git").mkdir()

        with patch("raise_cli.core.tools.run_tool") as mock_run:
            mock_run.return_value = ToolResult(
                returncode=0,
                stdout=str(tmp_path),
                stderr="",
            )
            root = git_root(tmp_path)

        assert root == tmp_path

    def test_raises_when_not_in_repo(self) -> None:
        with patch("raise_cli.core.tools.run_tool") as mock_run:
            mock_run.return_value = ToolResult(
                returncode=128,
                stdout="",
                stderr="fatal: not a git repository",
            )

            with pytest.raises(DependencyError, match="Not in a git repository"):
                git_root()


class TestGitBranch:
    """Tests for git_branch function."""

    def test_returns_branch_name(self) -> None:
        with patch("raise_cli.core.tools.run_tool") as mock_run:
            mock_run.return_value = ToolResult(
                returncode=0,
                stdout="main",
                stderr="",
            )
            branch = git_branch()

        assert branch == "main"

    def test_raises_on_failure(self) -> None:
        with patch("raise_cli.core.tools.run_tool") as mock_run:
            mock_run.return_value = ToolResult(
                returncode=128,
                stdout="",
                stderr="fatal: not a git repository",
            )

            with pytest.raises(DependencyError, match="Cannot determine git branch"):
                git_branch()


class TestGitStatus:
    """Tests for git_status function."""

    def test_parses_staged_files(self) -> None:
        with patch("raise_cli.core.tools.run_tool") as mock_run:
            mock_run.side_effect = [
                ToolResult(returncode=0, stdout="main", stderr=""),  # git_branch
                ToolResult(
                    returncode=0,
                    stdout="A  new_file.py\nM  modified.py",
                    stderr="",
                ),  # git status
            ]
            status = git_status()

        assert "new_file.py" in status.staged
        assert "modified.py" in status.staged

    def test_parses_modified_files(self) -> None:
        with patch("raise_cli.core.tools.run_tool") as mock_run:
            mock_run.side_effect = [
                ToolResult(returncode=0, stdout="main", stderr=""),
                ToolResult(
                    returncode=0,
                    stdout=" M unstaged.py",
                    stderr="",
                ),
            ]
            status = git_status()

        assert "unstaged.py" in status.modified

    def test_parses_untracked_files(self) -> None:
        with patch("raise_cli.core.tools.run_tool") as mock_run:
            mock_run.side_effect = [
                ToolResult(returncode=0, stdout="main", stderr=""),
                ToolResult(
                    returncode=0,
                    stdout="?? untracked.py",
                    stderr="",
                ),
            ]
            status = git_status()

        assert "untracked.py" in status.untracked

    def test_includes_branch(self) -> None:
        with patch("raise_cli.core.tools.run_tool") as mock_run:
            mock_run.side_effect = [
                ToolResult(returncode=0, stdout="feature/test", stderr=""),
                ToolResult(returncode=0, stdout="", stderr=""),
            ]
            status = git_status()

        assert status.branch == "feature/test"

    def test_handles_branch_failure(self) -> None:
        with patch("raise_cli.core.tools.run_tool") as mock_run:
            mock_run.side_effect = [
                ToolResult(
                    returncode=128, stdout="", stderr="fatal"
                ),  # git_branch fails
                ToolResult(returncode=0, stdout="", stderr=""),  # git status succeeds
            ]
            status = git_status()

        assert status.branch == ""

    def test_handles_status_failure(self) -> None:
        with patch("raise_cli.core.tools.run_tool") as mock_run:
            mock_run.side_effect = [
                ToolResult(returncode=0, stdout="main", stderr=""),
                ToolResult(returncode=128, stdout="", stderr="fatal"),  # status fails
            ]
            status = git_status()

        assert status.branch == "main"
        assert status.staged == []

    def test_skips_short_lines(self) -> None:
        with patch("raise_cli.core.tools.run_tool") as mock_run:
            mock_run.side_effect = [
                ToolResult(returncode=0, stdout="main", stderr=""),
                ToolResult(
                    returncode=0, stdout="AB\n?? valid.py", stderr=""
                ),  # AB is too short
            ]
            status = git_status()

        assert "valid.py" in status.untracked
        assert len(status.staged) == 0  # AB was skipped


class TestGitDiff:
    """Tests for git_diff function."""

    def test_returns_diff_output(self) -> None:
        with patch("raise_cli.core.tools.run_tool") as mock_run:
            mock_run.return_value = ToolResult(
                returncode=0,
                stdout="diff --git a/file.py b/file.py\n+new line",
                stderr="",
            )
            diff = git_diff()

        assert "new line" in diff

    def test_staged_flag(self) -> None:
        with patch("raise_cli.core.tools.run_tool") as mock_run:
            mock_run.return_value = ToolResult(returncode=0, stdout="", stderr="")
            git_diff(staged=True)

        args = mock_run.call_args[0][0]
        assert "--staged" in args


class TestRgSearch:
    """Tests for rg_search function."""

    def test_parses_matches(self) -> None:
        with patch("raise_cli.core.tools.run_tool") as mock_run:
            mock_run.return_value = ToolResult(
                returncode=0,
                stdout="src/file.py:10:def hello():",
                stderr="",
            )
            matches = rg_search("def ", Path("src"))

        assert len(matches) == 1
        assert matches[0].path == Path("src/file.py")
        assert matches[0].line == 10
        assert matches[0].text == "def hello():"

    def test_returns_empty_on_no_matches(self) -> None:
        with patch("raise_cli.core.tools.run_tool") as mock_run:
            mock_run.return_value = ToolResult(
                returncode=1,  # rg returns 1 on no matches
                stdout="",
                stderr="",
            )
            matches = rg_search("nonexistent_pattern_xyz")

        assert matches == []

    def test_glob_filter(self) -> None:
        with patch("raise_cli.core.tools.run_tool") as mock_run:
            mock_run.return_value = ToolResult(returncode=0, stdout="", stderr="")
            rg_search("pattern", glob="*.py")

        args = mock_run.call_args[0][0]
        assert "--glob" in args
        assert "*.py" in args

    def test_ignore_case(self) -> None:
        with patch("raise_cli.core.tools.run_tool") as mock_run:
            mock_run.return_value = ToolResult(returncode=0, stdout="", stderr="")
            rg_search("pattern", ignore_case=True)

        args = mock_run.call_args[0][0]
        assert "--ignore-case" in args


class TestSgSearch:
    """Tests for sg_search function."""

    def test_parses_matches(self) -> None:
        with patch("raise_cli.core.tools.run_tool") as mock_run:
            mock_run.return_value = ToolResult(
                returncode=0,
                stdout="src/file.py:5:1:def foo():",
                stderr="",
            )
            matches = sg_search("def $NAME($$$ARGS)", Path("src"), lang="python")

        assert len(matches) == 1
        assert matches[0].path == Path("src/file.py")
        assert matches[0].line == 5

    def test_lang_filter(self) -> None:
        with patch("raise_cli.core.tools.run_tool") as mock_run:
            mock_run.return_value = ToolResult(returncode=0, stdout="", stderr="")
            sg_search("pattern", lang="python")

        args = mock_run.call_args[0][0]
        assert "--lang" in args
        assert "python" in args

    def test_returns_empty_on_no_matches(self) -> None:
        with patch("raise_cli.core.tools.run_tool") as mock_run:
            mock_run.return_value = ToolResult(
                returncode=1,
                stdout="",
                stderr="",
            )
            matches = sg_search("nonexistent $PATTERN")

        assert matches == []

    def test_skips_malformed_output(self) -> None:
        with patch("raise_cli.core.tools.run_tool") as mock_run:
            mock_run.return_value = ToolResult(
                returncode=0,
                stdout="file.py:notanumber:1:text\nvalid.py:5:1:def foo():",
                stderr="",
            )
            matches = sg_search("pattern")

        # Malformed line skipped, valid line parsed
        assert len(matches) == 1
        assert matches[0].path == Path("valid.py")


class TestSearchMatch:
    """Tests for SearchMatch dataclass."""

    def test_creation(self) -> None:
        match = SearchMatch(path=Path("test.py"), line=42, text="hello")
        assert match.path == Path("test.py")
        assert match.line == 42
        assert match.text == "hello"


class TestGitStatusDataclass:
    """Tests for GitStatus dataclass."""

    def test_defaults(self) -> None:
        status = GitStatus()
        assert status.staged == []
        assert status.modified == []
        assert status.untracked == []
        assert status.branch == ""
