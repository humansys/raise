"""Tests for quality gate runner."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from raise_cli.publish.check import CheckResult, Gate, run_checks


class TestCheckResult:
    """Test CheckResult model."""

    def test_passed_result(self) -> None:
        r = CheckResult(gate="Tests", passed=True, message="1770 passed")
        assert r.passed is True
        assert r.gate == "Tests"

    def test_failed_result(self) -> None:
        r = CheckResult(gate="Lint", passed=False, message="3 issues")
        assert r.passed is False


class TestGate:
    """Test individual gate definitions."""

    def test_gate_has_required_fields(self) -> None:
        gate = Gate(name="Tests", command="uv run pytest", required=True)
        assert gate.name == "Tests"
        assert gate.command == "uv run pytest"
        assert gate.required is True


class TestRunChecks:
    """Test the check runner."""

    def test_all_pass(self, tmp_path: pytest.TempPathFactory) -> None:
        """When all subprocess commands succeed, all checks pass."""
        project = tmp_path  # type: ignore[assignment]
        # Create required files
        changelog = project / "CHANGELOG.md"
        changelog.write_text(
            "# Changelog\n\n## [Unreleased]\n\n### Added\n- Feature\n\n## [1.0.0]\n"
        )
        pyproject = project / "pyproject.toml"
        pyproject.write_text('version = "2.0.0a7"\n')
        init_py = project / "src" / "pkg"
        init_py.mkdir(parents=True)
        init_file = init_py / "__init__.py"
        init_file.write_text('__version__ = "2.0.0a7"\n')

        with patch("raise_cli.publish.check._run_command") as mock_run:
            mock_run.return_value = (True, "ok")
            results = run_checks(
                project_root=Path(project),  # type: ignore[arg-type]
                pyproject_path=Path(pyproject),  # type: ignore[arg-type]
                init_path=Path(init_file),  # type: ignore[arg-type]
                changelog_path=Path(changelog),  # type: ignore[arg-type]
            )

        assert all(r.passed for r in results)

    def test_failing_gate_reports_failure(
        self, tmp_path: pytest.TempPathFactory
    ) -> None:
        """When a command fails, the corresponding gate fails."""
        project = tmp_path  # type: ignore[assignment]
        changelog = project / "CHANGELOG.md"
        changelog.write_text(
            "# Changelog\n\n## [Unreleased]\n\n### Added\n- Feature\n\n## [1.0.0]\n"
        )
        pyproject = project / "pyproject.toml"
        pyproject.write_text('version = "2.0.0a7"\n')
        init_py = project / "src" / "pkg"
        init_py.mkdir(parents=True)
        init_file = init_py / "__init__.py"
        init_file.write_text('__version__ = "2.0.0a7"\n')

        def side_effect(cmd: str, cwd: Path) -> tuple[bool, str]:
            if "pytest" in cmd:
                return (False, "3 failed")
            return (True, "ok")

        with patch("raise_cli.publish.check._run_command", side_effect=side_effect):
            results = run_checks(
                project_root=Path(project),  # type: ignore[arg-type]
                pyproject_path=Path(pyproject),  # type: ignore[arg-type]
                init_path=Path(init_file),  # type: ignore[arg-type]
                changelog_path=Path(changelog),  # type: ignore[arg-type]
            )

        failed = [r for r in results if not r.passed]
        assert len(failed) >= 1
        assert any("test" in r.gate.lower() for r in failed)

    def test_changelog_missing_fails(self, tmp_path: pytest.TempPathFactory) -> None:
        """Missing CHANGELOG.md fails the changelog gate."""
        project = tmp_path  # type: ignore[assignment]
        pyproject = project / "pyproject.toml"
        pyproject.write_text('version = "2.0.0a7"\n')
        init_py = project / "src" / "pkg"
        init_py.mkdir(parents=True)
        init_file = init_py / "__init__.py"
        init_file.write_text('__version__ = "2.0.0a7"\n')

        with patch("raise_cli.publish.check._run_command", return_value=(True, "ok")):
            results = run_checks(
                project_root=Path(project),  # type: ignore[arg-type]
                pyproject_path=Path(pyproject),  # type: ignore[arg-type]
                init_path=Path(init_file),  # type: ignore[arg-type]
                changelog_path=Path(project / "CHANGELOG.md"),  # type: ignore[arg-type]
            )

        changelog_result = next(r for r in results if "changelog" in r.gate.lower())
        assert changelog_result.passed is False

    def test_version_not_pep440_fails(self, tmp_path: pytest.TempPathFactory) -> None:
        """Non-PEP-440 version fails the version gate."""
        project = tmp_path  # type: ignore[assignment]
        changelog = project / "CHANGELOG.md"
        changelog.write_text(
            "# Changelog\n\n## [Unreleased]\n\n### Added\n- Feature\n\n## [1.0.0]\n"
        )
        pyproject = project / "pyproject.toml"
        pyproject.write_text('version = "2.0.0-alpha.7"\n')
        init_py = project / "src" / "pkg"
        init_py.mkdir(parents=True)
        init_file = init_py / "__init__.py"
        init_file.write_text('__version__ = "2.0.0-alpha.7"\n')

        with patch("raise_cli.publish.check._run_command", return_value=(True, "ok")):
            results = run_checks(
                project_root=Path(project),  # type: ignore[arg-type]
                pyproject_path=Path(pyproject),  # type: ignore[arg-type]
                init_path=Path(init_file),  # type: ignore[arg-type]
                changelog_path=Path(changelog),  # type: ignore[arg-type]
            )

        version_result = next(r for r in results if "pep 440" in r.gate.lower())
        assert version_result.passed is False

    def test_version_sync_mismatch_fails(
        self, tmp_path: pytest.TempPathFactory
    ) -> None:
        """Mismatched versions between pyproject.toml and __init__.py fail."""
        project = tmp_path  # type: ignore[assignment]
        changelog = project / "CHANGELOG.md"
        changelog.write_text(
            "# Changelog\n\n## [Unreleased]\n\n### Added\n- Feature\n\n## [1.0.0]\n"
        )
        pyproject = project / "pyproject.toml"
        pyproject.write_text('version = "2.0.0a7"\n')
        init_py = project / "src" / "pkg"
        init_py.mkdir(parents=True)
        init_file = init_py / "__init__.py"
        init_file.write_text('__version__ = "2.0.0a6"\n')

        with patch("raise_cli.publish.check._run_command", return_value=(True, "ok")):
            results = run_checks(
                project_root=Path(project),  # type: ignore[arg-type]
                pyproject_path=Path(pyproject),  # type: ignore[arg-type]
                init_path=Path(init_file),  # type: ignore[arg-type]
                changelog_path=Path(changelog),  # type: ignore[arg-type]
            )

        sync_result = next(r for r in results if "sync" in r.gate.lower())
        assert sync_result.passed is False

    def test_returns_all_gate_results(self, tmp_path: pytest.TempPathFactory) -> None:
        """run_checks always returns results for all gates."""
        project = tmp_path  # type: ignore[assignment]
        changelog = project / "CHANGELOG.md"
        changelog.write_text(
            "# Changelog\n\n## [Unreleased]\n\n### Added\n- Feature\n\n## [1.0.0]\n"
        )
        pyproject = project / "pyproject.toml"
        pyproject.write_text('version = "2.0.0a7"\n')
        init_py = project / "src" / "pkg"
        init_py.mkdir(parents=True)
        init_file = init_py / "__init__.py"
        init_file.write_text('__version__ = "2.0.0a7"\n')

        with patch("raise_cli.publish.check._run_command", return_value=(True, "ok")):
            results = run_checks(
                project_root=Path(project),  # type: ignore[arg-type]
                pyproject_path=Path(pyproject),  # type: ignore[arg-type]
                init_path=Path(init_file),  # type: ignore[arg-type]
                changelog_path=Path(changelog),  # type: ignore[arg-type]
            )

        # 6 command gates + 3 file checks = 9
        assert len(results) == 9
