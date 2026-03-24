"""Tests for interactive skill conflict resolution."""

from __future__ import annotations

from unittest.mock import patch

from raise_cli.onboarding.skill_conflict import (
    ConflictAction,
    format_skill_diff,
    prompt_skill_conflict,
)


class TestConflictAction:
    """Tests for ConflictAction enum."""

    def test_all_actions_exist(self) -> None:
        assert ConflictAction.KEEP
        assert ConflictAction.OVERWRITE
        assert ConflictAction.DIFF
        assert ConflictAction.BACKUP_OVERWRITE
        assert ConflictAction.KEEP_ALL
        assert ConflictAction.OVERWRITE_ALL


class TestFormatSkillDiff:
    """Tests for diff formatting."""

    def test_shows_unified_diff(self) -> None:
        old = "line 1\nline 2\nline 3\n"
        new = "line 1\nline 2 modified\nline 3\n"
        diff = format_skill_diff("rai-debug", old, new)
        assert "---" in diff
        assert "+++" in diff
        assert "-line 2" in diff
        assert "+line 2 modified" in diff

    def test_includes_skill_name(self) -> None:
        diff = format_skill_diff("rai-debug", "a\n", "b\n")
        assert "rai-debug" in diff


class TestPromptSkillConflict:
    """Tests for the interactive prompt."""

    def test_non_tty_returns_keep(self) -> None:
        """Non-TTY should default to keep without prompting."""
        with patch("sys.stdin") as mock_stdin:
            mock_stdin.isatty.return_value = False
            action = prompt_skill_conflict("rai-debug", "old content", "new content")
        assert action == ConflictAction.KEEP

    def test_keep_input(self) -> None:
        with (
            patch("sys.stdin") as mock_stdin,
            patch("builtins.input", return_value="k"),
        ):
            mock_stdin.isatty.return_value = True
            action = prompt_skill_conflict("rai-debug", "old", "new")
        assert action == ConflictAction.KEEP

    def test_overwrite_input(self) -> None:
        with (
            patch("sys.stdin") as mock_stdin,
            patch("builtins.input", return_value="o"),
        ):
            mock_stdin.isatty.return_value = True
            action = prompt_skill_conflict("rai-debug", "old", "new")
        assert action == ConflictAction.OVERWRITE

    def test_backup_overwrite_input(self) -> None:
        with (
            patch("sys.stdin") as mock_stdin,
            patch("builtins.input", return_value="b"),
        ):
            mock_stdin.isatty.return_value = True
            action = prompt_skill_conflict("rai-debug", "old", "new")
        assert action == ConflictAction.BACKUP_OVERWRITE

    def test_keep_all_input(self) -> None:
        with (
            patch("sys.stdin") as mock_stdin,
            patch("builtins.input", return_value="K"),
        ):
            mock_stdin.isatty.return_value = True
            action = prompt_skill_conflict("rai-debug", "old", "new")
        assert action == ConflictAction.KEEP_ALL

    def test_overwrite_all_input(self) -> None:
        with (
            patch("sys.stdin") as mock_stdin,
            patch("builtins.input", return_value="O"),
        ):
            mock_stdin.isatty.return_value = True
            action = prompt_skill_conflict("rai-debug", "old", "new")
        assert action == ConflictAction.OVERWRITE_ALL

    def test_empty_input_defaults_to_keep(self) -> None:
        with (
            patch("sys.stdin") as mock_stdin,
            patch("builtins.input", return_value=""),
        ):
            mock_stdin.isatty.return_value = True
            action = prompt_skill_conflict("rai-debug", "old", "new")
        assert action == ConflictAction.KEEP

    def test_diff_then_keep(self) -> None:
        """Pressing 'd' shows diff, then re-prompts. Second input decides."""
        with (
            patch("sys.stdin") as mock_stdin,
            patch("builtins.input", side_effect=["d", "k"]),
            patch("builtins.print") as mock_print,
        ):
            mock_stdin.isatty.return_value = True
            action = prompt_skill_conflict("rai-debug", "old\n", "new\n")

        assert action == ConflictAction.KEEP
        # Verify diff was printed
        printed = "".join(str(c) for c in mock_print.call_args_list)
        assert "---" in printed or "old" in printed

    def test_invalid_input_reprompts(self) -> None:
        """Invalid input should re-prompt."""
        with (
            patch("sys.stdin") as mock_stdin,
            patch("builtins.input", side_effect=["x", "z", "k"]),
        ):
            mock_stdin.isatty.return_value = True
            action = prompt_skill_conflict("rai-debug", "old", "new")
        assert action == ConflictAction.KEEP
