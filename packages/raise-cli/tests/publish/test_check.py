"""Tests for quality gate runner."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from raise_cli.publish.check import CheckResult, Gate, run_checks


def _create_gates_yaml(project: Path, gates: list[dict[str, str]] | None = None) -> None:
    """Create .raise/release-gates.yaml in tmp project."""
    raise_dir = project / ".raise"
    raise_dir.mkdir(parents=True, exist_ok=True)
    if gates is None:
        gates = [
            {"name": "Tests pass", "run": "echo ok"},
            {"name": "Lint clean", "run": "echo ok"},
        ]
    import yaml

    (raise_dir / "release-gates.yaml").write_text(
        yaml.dump({"gates": gates}), encoding="utf-8"
    )


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
        gate = Gate(name="Tests", command="uv run pytest")
        assert gate.name == "Tests"
        assert gate.command == "uv run pytest"


class TestRunChecks:
    """Test the check runner."""

    def test_all_pass(self, tmp_path: pytest.TempPathFactory) -> None:
        """When all subprocess commands succeed, all checks pass."""
        project = tmp_path  # type: ignore[assignment]
        _create_gates_yaml(project)
        changelog = project / "CHANGELOG.md"
        changelog.write_text(
            "# Changelog\n\n## [Unreleased]\n\n### Added\n- Feature\n\n## [1.0.0]\n"
        )
        pyproject = project / "pyproject.toml"
        pyproject.write_text('version = "2.0.0a7"\n')

        with patch("raise_cli.publish.check._run_command") as mock_run:
            mock_run.return_value = (True, "ok")
            results = run_checks(
                project_root=Path(project),  # type: ignore[arg-type]
                pyproject_path=Path(pyproject),  # type: ignore[arg-type]
                changelog_path=Path(changelog),  # type: ignore[arg-type]
            )

        assert all(r.passed for r in results)

    def test_failing_gate_reports_failure(
        self, tmp_path: pytest.TempPathFactory
    ) -> None:
        """When a command fails, the corresponding gate fails."""
        project = tmp_path  # type: ignore[assignment]
        _create_gates_yaml(project, [{"name": "Tests pass", "run": "pytest"}])
        changelog = project / "CHANGELOG.md"
        changelog.write_text(
            "# Changelog\n\n## [Unreleased]\n\n### Added\n- Feature\n\n## [1.0.0]\n"
        )
        pyproject = project / "pyproject.toml"
        pyproject.write_text('version = "2.0.0a7"\n')

        def side_effect(cmd: str, cwd: Path) -> tuple[bool, str]:
            if "pytest" in cmd:
                return (False, "3 failed")
            return (True, "ok")

        with patch("raise_cli.publish.check._run_command", side_effect=side_effect):
            results = run_checks(
                project_root=Path(project),  # type: ignore[arg-type]
                pyproject_path=Path(pyproject),  # type: ignore[arg-type]
                changelog_path=Path(changelog),  # type: ignore[arg-type]
            )

        failed = [r for r in results if not r.passed]
        assert len(failed) >= 1
        assert any("test" in r.gate.lower() for r in failed)

    def test_changelog_missing_fails(self, tmp_path: pytest.TempPathFactory) -> None:
        """Missing CHANGELOG.md fails the changelog gate."""
        project = tmp_path  # type: ignore[assignment]
        _create_gates_yaml(project)
        pyproject = project / "pyproject.toml"
        pyproject.write_text('version = "2.0.0a7"\n')

        with patch("raise_cli.publish.check._run_command", return_value=(True, "ok")):
            results = run_checks(
                project_root=Path(project),  # type: ignore[arg-type]
                pyproject_path=Path(pyproject),  # type: ignore[arg-type]
                changelog_path=Path(project / "CHANGELOG.md"),  # type: ignore[arg-type]
            )

        changelog_result = next(r for r in results if "changelog" in r.gate.lower())
        assert changelog_result.passed is False

    def test_version_not_pep440_fails(self, tmp_path: pytest.TempPathFactory) -> None:
        """Non-PEP-440 version fails the version gate."""
        project = tmp_path  # type: ignore[assignment]
        _create_gates_yaml(project)
        changelog = project / "CHANGELOG.md"
        changelog.write_text(
            "# Changelog\n\n## [Unreleased]\n\n### Added\n- Feature\n\n## [1.0.0]\n"
        )
        pyproject = project / "pyproject.toml"
        pyproject.write_text('version = "2.0.0-alpha.7"\n')

        with patch("raise_cli.publish.check._run_command", return_value=(True, "ok")):
            results = run_checks(
                project_root=Path(project),  # type: ignore[arg-type]
                pyproject_path=Path(pyproject),  # type: ignore[arg-type]
                changelog_path=Path(changelog),  # type: ignore[arg-type]
            )

        version_result = next(r for r in results if "pep 440" in r.gate.lower())
        assert version_result.passed is False

    def test_no_gates_yaml_reports_error(self, tmp_path: pytest.TempPathFactory) -> None:
        """Missing release-gates.yaml reports a config error."""
        project = tmp_path  # type: ignore[assignment]
        changelog = project / "CHANGELOG.md"
        changelog.write_text(
            "# Changelog\n\n## [Unreleased]\n\n### Added\n- Feature\n\n## [1.0.0]\n"
        )
        pyproject = project / "pyproject.toml"
        pyproject.write_text('version = "2.0.0a7"\n')

        results = run_checks(
            project_root=Path(project),  # type: ignore[arg-type]
            pyproject_path=Path(pyproject),  # type: ignore[arg-type]
            changelog_path=Path(changelog),  # type: ignore[arg-type]
        )

        config_result = next(r for r in results if "config" in r.gate.lower())
        assert config_result.passed is False

    def test_returns_all_gate_results(self, tmp_path: pytest.TempPathFactory) -> None:
        """run_checks returns results for all YAML gates + file checks."""
        project = tmp_path  # type: ignore[assignment]
        _create_gates_yaml(project)  # 2 gates
        changelog = project / "CHANGELOG.md"
        changelog.write_text(
            "# Changelog\n\n## [Unreleased]\n\n### Added\n- Feature\n\n## [1.0.0]\n"
        )
        pyproject = project / "pyproject.toml"
        pyproject.write_text('version = "2.0.0a7"\n')

        with patch("raise_cli.publish.check._run_command", return_value=(True, "ok")):
            results = run_checks(
                project_root=Path(project),  # type: ignore[arg-type]
                pyproject_path=Path(pyproject),  # type: ignore[arg-type]
                changelog_path=Path(changelog),  # type: ignore[arg-type]
            )

        # 2 YAML command gates + 2 file checks (changelog, PEP 440) = 4
        assert len(results) == 4
