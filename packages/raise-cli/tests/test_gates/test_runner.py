"""Tests for the shared manifest-driven gate runner."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

from raise_cli.gates.models import GateContext

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _completed_process(
    returncode: int, stdout: str = "", stderr: str = ""
) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(
        args=[], returncode=returncode, stdout=stdout, stderr=stderr
    )


def _make_manifest_dict(
    *,
    test_command: str | None = "uv run pytest --tb=short",
    lint_command: str | None = "uv run ruff check",
    type_check_command: str | None = "uv run pyright",
    format_command: str | None = "uv run ruff format --check",
) -> dict[str, object]:
    """Build a minimal manifest dict for testing."""
    return {
        "version": "1.0",
        "project": {
            "name": "test-project",
            "project_type": "brownfield",
            "language": "python",
            "test_command": test_command,
            "lint_command": lint_command,
            "type_check_command": type_check_command,
            "format_command": format_command,
            "code_file_count": 10,
        },
        "branches": {"development": "dev", "main": "main"},
    }


# ---------------------------------------------------------------------------
# run_manifest_command tests
# ---------------------------------------------------------------------------


class TestRunManifestCommand:
    """Tests for run_manifest_command shared helper."""

    def test_no_manifest_returns_failed(self, tmp_path: Path) -> None:
        """When no manifest file exists, return a failed result."""
        from raise_cli.gates.builtin._runner import run_manifest_command

        ctx = GateContext(gate_id="gate-tests", working_dir=tmp_path)
        result = run_manifest_command(
            gate_id="gate-tests",
            manifest_key="test_command",
            description="All tests pass",
            context=ctx,
        )
        assert result.passed is False
        assert "manifest" in result.message.lower()

    def test_command_not_configured_returns_skip(self, tmp_path: Path) -> None:
        """When the manifest key is None, skip (return passed=True)."""
        from raise_cli.gates.builtin._runner import run_manifest_command

        ctx = GateContext(gate_id="gate-format", working_dir=tmp_path)
        manifest_data = _make_manifest_dict(format_command=None)

        with patch("raise_cli.gates.builtin._runner.load_manifest") as mock_load:
            from raise_cli.onboarding.manifest import ProjectManifest

            mock_load.return_value = ProjectManifest.model_validate(manifest_data)
            result = run_manifest_command(
                gate_id="gate-format",
                manifest_key="format_command",
                description="Format check",
                context=ctx,
            )
        assert result.passed is True
        assert (
            "not configured" in result.message.lower()
            or "skipped" in result.message.lower()
        )

    def test_command_passes(self, tmp_path: Path) -> None:
        """When the command exits 0, return passed=True."""
        from raise_cli.gates.builtin._runner import run_manifest_command

        ctx = GateContext(gate_id="gate-lint", working_dir=tmp_path)
        manifest_data = _make_manifest_dict()

        with (
            patch("raise_cli.gates.builtin._runner.load_manifest") as mock_load,
            patch(
                "raise_cli.gates.builtin._runner.subprocess.run",
                return_value=_completed_process(0, stdout="All good"),
            ),
        ):
            from raise_cli.onboarding.manifest import ProjectManifest

            mock_load.return_value = ProjectManifest.model_validate(manifest_data)
            result = run_manifest_command(
                gate_id="gate-lint",
                manifest_key="lint_command",
                description="Linting passes",
                context=ctx,
            )
        assert result.passed is True
        assert result.gate_id == "gate-lint"

    def test_command_fails(self, tmp_path: Path) -> None:
        """When the command exits non-zero, return passed=False with details."""
        from raise_cli.gates.builtin._runner import run_manifest_command

        ctx = GateContext(gate_id="gate-lint", working_dir=tmp_path)
        manifest_data = _make_manifest_dict()

        with (
            patch("raise_cli.gates.builtin._runner.load_manifest") as mock_load,
            patch(
                "raise_cli.gates.builtin._runner.subprocess.run",
                return_value=_completed_process(
                    1, stdout="E501 line too long", stderr="error: check failed"
                ),
            ),
        ):
            from raise_cli.onboarding.manifest import ProjectManifest

            mock_load.return_value = ProjectManifest.model_validate(manifest_data)
            result = run_manifest_command(
                gate_id="gate-lint",
                manifest_key="lint_command",
                description="Linting passes",
                context=ctx,
            )
        assert result.passed is False
        assert len(result.details) == 2
        assert "E501" in result.details[0]
        assert "error: check failed" in result.details[1]

    def test_subprocess_exception_returns_failed(self, tmp_path: Path) -> None:
        """When subprocess.run raises, return passed=False with exception info."""
        from raise_cli.gates.builtin._runner import run_manifest_command

        ctx = GateContext(gate_id="gate-tests", working_dir=tmp_path)
        manifest_data = _make_manifest_dict()

        with (
            patch("raise_cli.gates.builtin._runner.load_manifest") as mock_load,
            patch(
                "raise_cli.gates.builtin._runner.subprocess.run",
                side_effect=FileNotFoundError("pytest not found"),
            ),
        ):
            from raise_cli.onboarding.manifest import ProjectManifest

            mock_load.return_value = ProjectManifest.model_validate(manifest_data)
            result = run_manifest_command(
                gate_id="gate-tests",
                manifest_key="test_command",
                description="All tests pass",
                context=ctx,
            )
        assert result.passed is False
        assert "pytest not found" in result.message

    def test_uses_working_dir_as_cwd(self, tmp_path: Path) -> None:
        """The subprocess should run in the context's working_dir."""
        from raise_cli.gates.builtin._runner import run_manifest_command

        ctx = GateContext(gate_id="gate-lint", working_dir=tmp_path)
        manifest_data = _make_manifest_dict()

        with (
            patch("raise_cli.gates.builtin._runner.load_manifest") as mock_load,
            patch(
                "raise_cli.gates.builtin._runner.subprocess.run",
                return_value=_completed_process(0),
            ) as mock_run,
        ):
            from raise_cli.onboarding.manifest import ProjectManifest

            mock_load.return_value = ProjectManifest.model_validate(manifest_data)
            run_manifest_command(
                gate_id="gate-lint",
                manifest_key="lint_command",
                description="Linting passes",
                context=ctx,
            )
        assert mock_run.call_args.kwargs.get("cwd") == str(tmp_path)

    def test_splits_command_string(self, tmp_path: Path) -> None:
        """The command string should be split into a list for subprocess."""
        from raise_cli.gates.builtin._runner import run_manifest_command

        ctx = GateContext(gate_id="gate-lint", working_dir=tmp_path)
        manifest_data = _make_manifest_dict(lint_command="uv run ruff check")

        with (
            patch("raise_cli.gates.builtin._runner.load_manifest") as mock_load,
            patch(
                "raise_cli.gates.builtin._runner.subprocess.run",
                return_value=_completed_process(0),
            ) as mock_run,
        ):
            from raise_cli.onboarding.manifest import ProjectManifest

            mock_load.return_value = ProjectManifest.model_validate(manifest_data)
            run_manifest_command(
                gate_id="gate-lint",
                manifest_key="lint_command",
                description="Linting passes",
                context=ctx,
            )
        assert mock_run.call_args[0][0] == ["uv", "run", "ruff", "check"]


# ---------------------------------------------------------------------------
# Model extension tests
# ---------------------------------------------------------------------------


class TestModelExtensions:
    """Verify format_command field was added to models."""

    def test_toolchain_info_has_format_command(self) -> None:
        from raise_cli.onboarding.detection import ToolchainInfo

        info = ToolchainInfo(
            language="python", format_command="uv run ruff format --check"
        )
        assert info.format_command == "uv run ruff format --check"

    def test_toolchain_info_format_command_defaults_none(self) -> None:
        from raise_cli.onboarding.detection import ToolchainInfo

        info = ToolchainInfo(language="python")
        assert info.format_command is None

    def test_project_info_has_format_command(self) -> None:
        from raise_cli.onboarding.manifest import ProjectInfo

        info = ProjectInfo(
            name="test",
            project_type="brownfield",
            format_command="uv run ruff format --check",
        )
        assert info.format_command == "uv run ruff format --check"

    def test_project_info_format_command_defaults_none(self) -> None:
        from raise_cli.onboarding.manifest import ProjectInfo

        info = ProjectInfo(name="test", project_type="brownfield")
        assert info.format_command is None

    def test_python_toolchain_includes_format_command(self) -> None:
        from raise_cli.onboarding.detection import LANGUAGE_TOOLCHAIN

        python_tc = LANGUAGE_TOOLCHAIN["python"]
        assert python_tc.format_command is not None
        assert "format" in python_tc.format_command
