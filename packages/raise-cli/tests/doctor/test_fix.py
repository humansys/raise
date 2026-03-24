"""Tests for rai doctor --fix auto-remediation.

Architecture: S352.4
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from raise_cli.doctor.fix import (
    FIX_REGISTRY,
    add_gitignore_personal,
    rebuild_graph,
    run_fixes,
)
from raise_cli.doctor.models import CheckResult, CheckStatus


@pytest.fixture
def project_dir(tmp_path: Path) -> Path:
    """Minimal project directory."""
    return tmp_path


class TestRebuildGraph:
    """Tests for rebuild-graph fix action."""

    def test_registered_in_registry(self) -> None:
        assert "rebuild-graph" in FIX_REGISTRY

    def test_calls_subprocess_with_graph_build(self, project_dir: Path) -> None:
        with patch("raise_cli.doctor.fix.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            result = rebuild_graph(project_dir)
        assert result is True
        args = mock_run.call_args
        cmd = args[0][0]
        assert "graph" in cmd
        assert "build" in cmd
        assert args[1]["cwd"] == project_dir

    def test_returns_false_on_failure(self, project_dir: Path) -> None:
        with patch("raise_cli.doctor.fix.subprocess.run") as mock_run:
            mock_run.return_value.returncode = 1
            result = rebuild_graph(project_dir)
        assert result is False


class TestAddGitignorePersonal:
    """Tests for add-gitignore-personal fix action."""

    def test_registered_in_registry(self) -> None:
        assert "add-gitignore-personal" in FIX_REGISTRY

    def test_creates_entry_when_gitignore_exists(self, project_dir: Path) -> None:
        gitignore = project_dir / ".gitignore"
        gitignore.write_text("*.pyc\n")
        result = add_gitignore_personal(project_dir)
        assert result is True
        content = gitignore.read_text()
        assert ".raise/rai/personal/" in content

    def test_creates_backup_before_modifying(self, project_dir: Path) -> None:
        gitignore = project_dir / ".gitignore"
        original = "*.pyc\n__pycache__/\n"
        gitignore.write_text(original)
        add_gitignore_personal(project_dir)
        backup = project_dir / ".gitignore.bak"
        assert backup.exists()
        assert backup.read_text() == original

    def test_idempotent_when_entry_exists(self, project_dir: Path) -> None:
        gitignore = project_dir / ".gitignore"
        gitignore.write_text("*.pyc\n.raise/rai/personal/\n")
        result = add_gitignore_personal(project_dir)
        assert result is True
        # No backup created since no modification needed
        assert not (project_dir / ".gitignore.bak").exists()

    def test_creates_gitignore_when_missing(self, project_dir: Path) -> None:
        result = add_gitignore_personal(project_dir)
        assert result is True
        gitignore = project_dir / ".gitignore"
        assert gitignore.exists()
        assert ".raise/rai/personal/" in gitignore.read_text()

    def test_returns_false_on_write_error(self, tmp_path: Path) -> None:
        """RAISE-521: returns False when file write fails (OSError).

        SonarCloud BLOCKER AZy-yCoI4PF7cDTLpgfn — function must not always return True.
        Uses mock instead of chmod so the test is reliable in root/CI environments.
        """
        from unittest.mock import patch

        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("*.pyc\n")

        with patch(
            "raise_cli.doctor.fix.open", side_effect=OSError("permission denied")
        ):
            result = add_gitignore_personal(tmp_path)

        assert result is False


class TestRunFixes:
    """Tests for the run_fixes orchestrator."""

    def test_skips_results_without_fix_id(self, project_dir: Path) -> None:
        results = [
            CheckResult(
                check_id="env-python",
                category="environment",
                status=CheckStatus.PASS,
                message="Python OK",
                fix_id="",
            ),
        ]
        outcomes = run_fixes(results, project_dir)
        assert outcomes == []

    def test_skips_unknown_fix_id(self, project_dir: Path) -> None:
        results = [
            CheckResult(
                check_id="something",
                category="misc",
                status=CheckStatus.WARN,
                message="problem",
                fix_id="nonexistent-fix",
            ),
        ]
        outcomes = run_fixes(results, project_dir)
        assert outcomes == []

    def test_runs_fix_for_matching_fix_id(self, project_dir: Path) -> None:
        gitignore = project_dir / ".gitignore"
        gitignore.write_text("*.pyc\n")
        results = [
            CheckResult(
                check_id="project-gitignore",
                category="project",
                status=CheckStatus.WARN,
                message=".raise/rai/personal/ not found",
                fix_id="add-gitignore-personal",
            ),
        ]
        outcomes = run_fixes(results, project_dir)
        assert len(outcomes) == 1
        assert outcomes[0] == ("add-gitignore-personal", True)
        assert ".raise/rai/personal/" in gitignore.read_text()

    def test_only_runs_fixes_for_non_pass_is_not_filtered(
        self, project_dir: Path
    ) -> None:
        """run_fixes runs all results with fix_id, regardless of status.

        Filtering is the caller's responsibility.
        """
        gitignore = project_dir / ".gitignore"
        gitignore.write_text(".raise/rai/personal/\n")
        results = [
            CheckResult(
                check_id="project-gitignore",
                category="project",
                status=CheckStatus.PASS,
                message="already there",
                fix_id="add-gitignore-personal",
            ),
        ]
        outcomes = run_fixes(results, project_dir)
        # Fix still runs (idempotent)
        assert len(outcomes) == 1
        assert outcomes[0][1] is True


class TestDoctorFixCLI:
    """Tests for --fix flag integration in CLI."""

    def test_fix_flag_accepted(self) -> None:
        cli_runner = CliRunner()
        from raise_cli.cli.main import app

        result = cli_runner.invoke(app, ["doctor", "--fix"])
        # Should not fail with unknown option
        assert result.exit_code in (0, 1)  # may fail due to real checks
        assert "Unknown" not in result.output

    def test_fix_flag_in_help(self) -> None:
        cli_runner = CliRunner()
        from raise_cli.cli.main import app

        result = cli_runner.invoke(app, ["doctor", "--help"])
        assert "--fix" in result.output
