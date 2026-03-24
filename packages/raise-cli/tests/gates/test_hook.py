"""Tests for the pre-commit hook module.

Verifies that the hook runs lint, format, and type-check commands
from manifest, skips test_command, and reports pass/fail correctly.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from raise_cli.onboarding.detection import ProjectType
from raise_cli.onboarding.manifest import ProjectInfo, ProjectManifest


def _make_manifest(
    *,
    lint: str | None = "ruff check .",
    fmt: str | None = "ruff format --check .",
    typecheck: str | None = "pyright",
    test: str | None = "pytest",
) -> ProjectManifest:
    """Create a manifest with configurable commands."""
    return ProjectManifest(
        project=ProjectInfo(
            name="test-project",
            project_type=ProjectType.GREENFIELD,
            lint_command=lint,
            format_command=fmt,
            type_check_command=typecheck,
            test_command=test,
        ),
    )


class TestHookAllPass:
    """When all configured commands pass, hook returns 0."""

    def test_returns_zero_when_all_pass(self) -> None:
        from raise_cli.gates.hook import run_hook

        manifest = _make_manifest()
        completed = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )

        with (
            patch("raise_cli.gates.hook.load_manifest", return_value=manifest),
            patch("raise_cli.gates.hook.subprocess.run", return_value=completed),
        ):
            result = run_hook(Path("/fake"))

        assert result == 0


class TestHookFailure:
    """When any command fails, hook returns 1."""

    def test_returns_one_when_lint_fails(self) -> None:
        from raise_cli.gates.hook import run_hook

        manifest = _make_manifest()

        def fake_run(args: Any, **kwargs: Any) -> subprocess.CompletedProcess[str]:
            # lint fails, others pass
            if args[0] == "ruff" and args[1] == "check":
                return subprocess.CompletedProcess(args=args, returncode=1)
            return subprocess.CompletedProcess(args=args, returncode=0)

        with (
            patch("raise_cli.gates.hook.load_manifest", return_value=manifest),
            patch("raise_cli.gates.hook.subprocess.run", side_effect=fake_run),
        ):
            result = run_hook(Path("/fake"))

        assert result == 1

    def test_output_shows_which_check_failed(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        from raise_cli.gates.hook import run_hook

        manifest = _make_manifest()

        def fake_run(args: Any, **kwargs: Any) -> subprocess.CompletedProcess[str]:
            if args[0] == "ruff" and args[1] == "check":
                return subprocess.CompletedProcess(args=args, returncode=1)
            return subprocess.CompletedProcess(args=args, returncode=0)

        with (
            patch("raise_cli.gates.hook.load_manifest", return_value=manifest),
            patch("raise_cli.gates.hook.subprocess.run", side_effect=fake_run),
        ):
            run_hook(Path("/fake"))

        captured = capsys.readouterr()
        assert "[FAIL]" in captured.out
        assert "lint" in captured.out.lower()


class TestHookNoManifest:
    """When no manifest is found, hook returns 1."""

    def test_returns_one_when_no_manifest(self) -> None:
        from raise_cli.gates.hook import run_hook

        with patch("raise_cli.gates.hook.load_manifest", return_value=None):
            result = run_hook(Path("/fake"))

        assert result == 1


class TestHookSkipUnconfigured:
    """When a command is None in manifest, it is skipped gracefully."""

    def test_skips_unconfigured_command(self) -> None:
        from raise_cli.gates.hook import run_hook

        manifest = _make_manifest(lint=None, fmt=None, typecheck=None)
        mock_run = MagicMock()

        with (
            patch("raise_cli.gates.hook.load_manifest", return_value=manifest),
            patch("raise_cli.gates.hook.subprocess.run", mock_run),
        ):
            result = run_hook(Path("/fake"))

        # No subprocess calls should be made
        mock_run.assert_not_called()
        assert result == 0


class TestHookSkipsTestCommand:
    """test_command is never executed, even when configured."""

    def test_test_command_never_called(self) -> None:
        from raise_cli.gates.hook import run_hook

        manifest = _make_manifest(
            lint="ruff check .",
            fmt=None,
            typecheck=None,
            test="pytest --tb=short",
        )
        mock_run = MagicMock(
            return_value=subprocess.CompletedProcess(args=[], returncode=0)
        )

        with (
            patch("raise_cli.gates.hook.load_manifest", return_value=manifest),
            patch("raise_cli.gates.hook.subprocess.run", mock_run),
        ):
            run_hook(Path("/fake"))

        # Only lint should be called, not test
        assert mock_run.call_count == 1
        called_args = mock_run.call_args_list[0]
        assert "pytest" not in str(called_args)
