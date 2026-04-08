"""Tests for rai gate install-hook and uninstall-hook CLI commands.

Verifies hook file creation, overwrite protection, marker-based
uninstall safety, and --force flag behavior.
"""

from __future__ import annotations

import stat
from pathlib import Path

import pytest
from typer.testing import CliRunner

from raise_cli.cli.commands.gate import gate_app

runner = CliRunner()

_MARKER = "# Installed by: rai gate install-hook"

_EXPECTED_SHIM = (
    "#!/usr/bin/env bash\n"
    "# Installed by: rai gate install-hook\n"
    "# Remove with:  rai gate uninstall-hook\n"
    "uv run python -m raise_cli.gates.hook\n"
)


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    """Create a fake git repo with .git/hooks/ directory."""
    hooks_dir = tmp_path / ".git" / "hooks"
    hooks_dir.mkdir(parents=True)
    return tmp_path


class TestInstallHook:
    """rai gate install-hook creates the pre-commit hook file."""

    def test_creates_hook_file_with_correct_content(
        self, git_repo: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(git_repo)
        result = runner.invoke(gate_app, ["install-hook"], catch_exceptions=False)

        assert result.exit_code == 0
        hook_file = git_repo / ".git" / "hooks" / "pre-commit"
        assert hook_file.exists()
        assert hook_file.read_text() == _EXPECTED_SHIM
        # Check executable permission
        mode = hook_file.stat().st_mode
        assert mode & stat.S_IXUSR

    def test_refuses_overwrite_existing_non_rai_hook(
        self, git_repo: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(git_repo)
        hook_file = git_repo / ".git" / "hooks" / "pre-commit"
        hook_file.write_text("#!/bin/sh\necho custom hook\n")

        result = runner.invoke(gate_app, ["install-hook"], catch_exceptions=False)

        assert result.exit_code == 1
        # Original content preserved
        assert "custom hook" in hook_file.read_text()

    def test_force_overwrites_existing_hook(
        self, git_repo: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(git_repo)
        hook_file = git_repo / ".git" / "hooks" / "pre-commit"
        hook_file.write_text("#!/bin/sh\necho custom hook\n")

        result = runner.invoke(
            gate_app, ["install-hook", "--force"], catch_exceptions=False
        )

        assert result.exit_code == 0
        assert hook_file.read_text() == _EXPECTED_SHIM

    def test_updates_existing_rai_hook_silently(
        self, git_repo: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """If hook already has rai marker, overwrite without --force."""
        monkeypatch.chdir(git_repo)
        hook_file = git_repo / ".git" / "hooks" / "pre-commit"
        hook_file.write_text(
            "#!/usr/bin/env bash\n# Installed by: rai gate install-hook\nold content\n"
        )

        result = runner.invoke(gate_app, ["install-hook"], catch_exceptions=False)

        assert result.exit_code == 0
        assert hook_file.read_text() == _EXPECTED_SHIM


class TestUninstallHook:
    """rai gate uninstall-hook removes only rai-installed hooks."""

    def test_removes_rai_hook(
        self, git_repo: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(git_repo)
        hook_file = git_repo / ".git" / "hooks" / "pre-commit"
        hook_file.write_text(_EXPECTED_SHIM)

        result = runner.invoke(gate_app, ["uninstall-hook"], catch_exceptions=False)

        assert result.exit_code == 0
        assert not hook_file.exists()

    def test_refuses_to_remove_non_rai_hook(
        self, git_repo: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(git_repo)
        hook_file = git_repo / ".git" / "hooks" / "pre-commit"
        hook_file.write_text("#!/bin/sh\necho custom hook\n")

        result = runner.invoke(gate_app, ["uninstall-hook"], catch_exceptions=False)

        assert result.exit_code == 1
        assert hook_file.exists()

    def test_warns_when_no_hook_exists(
        self, git_repo: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(git_repo)

        result = runner.invoke(gate_app, ["uninstall-hook"], catch_exceptions=False)

        assert result.exit_code == 1
