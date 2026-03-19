"""Tests for built-in quality gates (tests, types, lint, coverage, format).

All gates delegate to run_manifest_command, so tests mock at the _runner level.
CoverageGate is a special case — it imports load_manifest directly.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from raise_cli.gates.models import GateContext, GateResult
from raise_cli.gates.protocol import WorkflowGate
from raise_cli.gates.registry import GateRegistry
from raise_cli.onboarding.manifest import ProjectManifest


def _completed_process(
    returncode: int, stdout: str = "", stderr: str = ""
) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(
        args=[], returncode=returncode, stdout=stdout, stderr=stderr
    )


def _make_manifest(
    *,
    test_command: str | None = "uv run pytest --tb=short",
    lint_command: str | None = "uv run ruff check",
    type_check_command: str | None = "uv run pyright",
    format_command: str | None = "uv run ruff format --check",
) -> ProjectManifest:
    return ProjectManifest.model_validate(
        {
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
    )


class TestProtocolConformance:
    @pytest.fixture(
        params=[
            "raise_cli.gates.builtin.tests:TestGate",
            "raise_cli.gates.builtin.types:TypeGate",
            "raise_cli.gates.builtin.lint:LintGate",
            "raise_cli.gates.builtin.coverage:CoverageGate",
            "raise_cli.gates.builtin.format:FormatGate",
        ]
    )
    def gate_instance(self, request: pytest.FixtureRequest) -> WorkflowGate:
        module_path, cls_name = request.param.rsplit(":", 1)
        import importlib

        mod = importlib.import_module(module_path)
        cls = getattr(mod, cls_name)
        return cls()  # type: ignore[return-value]

    def test_isinstance_check(self, gate_instance: WorkflowGate) -> None:
        assert isinstance(gate_instance, WorkflowGate)

    def test_has_gate_id(self, gate_instance: WorkflowGate) -> None:
        assert isinstance(gate_instance.gate_id, str)
        assert gate_instance.gate_id.startswith("gate-")

    def test_has_description(self, gate_instance: WorkflowGate) -> None:
        assert isinstance(gate_instance.description, str)
        assert len(gate_instance.description) > 0

    def test_has_workflow_point(self, gate_instance: WorkflowGate) -> None:
        assert gate_instance.workflow_point == "before:release:publish"

    def test_evaluate_returns_gate_result(self, gate_instance: WorkflowGate) -> None:
        ctx = GateContext(gate_id=gate_instance.gate_id)
        with (
            patch(
                "raise_cli.gates.builtin._runner.load_manifest",
                return_value=_make_manifest(),
            ),
            patch(
                "raise_cli.gates.builtin._runner.subprocess.run",
                return_value=_completed_process(0),
            ),
            patch(
                "raise_cli.gates.builtin.coverage.load_manifest",
                return_value=_make_manifest(),
            ),
            patch(
                "raise_cli.gates.builtin.coverage.subprocess.run",
                return_value=_completed_process(0),
            ),
        ):
            result = gate_instance.evaluate(ctx)
        assert isinstance(result, GateResult)
        assert result.gate_id == gate_instance.gate_id


class TestTestGate:
    def test_pass(self) -> None:
        from raise_cli.gates.builtin.tests import TestGate

        gate = TestGate()
        ctx = GateContext(gate_id="gate-tests")
        with (
            patch(
                "raise_cli.gates.builtin._runner.load_manifest",
                return_value=_make_manifest(),
            ),
            patch(
                "raise_cli.gates.builtin._runner.subprocess.run",
                return_value=_completed_process(0, stdout="4 passed"),
            ) as mock_run,
        ):
            result = gate.evaluate(ctx)
        assert result.passed is True
        assert result.gate_id == "gate-tests"
        mock_run.assert_called_once()

    def test_fail(self) -> None:
        from raise_cli.gates.builtin.tests import TestGate

        gate = TestGate()
        ctx = GateContext(gate_id="gate-tests")
        with (
            patch(
                "raise_cli.gates.builtin._runner.load_manifest",
                return_value=_make_manifest(),
            ),
            patch(
                "raise_cli.gates.builtin._runner.subprocess.run",
                return_value=_completed_process(1, stdout="FAILED test_foo"),
            ),
        ):
            result = gate.evaluate(ctx)
        assert result.passed is False
        assert result.details != ()

    def test_exception_returns_failed(self) -> None:
        from raise_cli.gates.builtin.tests import TestGate

        gate = TestGate()
        ctx = GateContext(gate_id="gate-tests")
        with (
            patch(
                "raise_cli.gates.builtin._runner.load_manifest",
                return_value=_make_manifest(),
            ),
            patch(
                "raise_cli.gates.builtin._runner.subprocess.run",
                side_effect=FileNotFoundError("pytest not found"),
            ),
        ):
            result = gate.evaluate(ctx)
        assert result.passed is False
        assert "pytest not found" in result.message

    def test_uses_working_dir(self) -> None:
        from raise_cli.gates.builtin.tests import TestGate

        gate = TestGate()
        ctx = GateContext(gate_id="gate-tests", working_dir=Path("/some/project"))
        with (
            patch(
                "raise_cli.gates.builtin._runner.load_manifest",
                return_value=_make_manifest(),
            ),
            patch(
                "raise_cli.gates.builtin._runner.subprocess.run",
                return_value=_completed_process(0),
            ) as mock_run,
        ):
            gate.evaluate(ctx)
        assert mock_run.call_args.kwargs.get("cwd") == str(Path("/some/project"))

    def test_skips_when_not_configured(self) -> None:
        from raise_cli.gates.builtin.tests import TestGate

        gate = TestGate()
        ctx = GateContext(gate_id="gate-tests")
        with patch(
            "raise_cli.gates.builtin._runner.load_manifest",
            return_value=_make_manifest(test_command=None),
        ):
            result = gate.evaluate(ctx)
        assert result.passed is True
        assert "not configured" in result.message.lower()


class TestTypeGate:
    def test_pass(self) -> None:
        from raise_cli.gates.builtin.types import TypeGate

        gate = TypeGate()
        ctx = GateContext(gate_id="gate-types")
        with (
            patch(
                "raise_cli.gates.builtin._runner.load_manifest",
                return_value=_make_manifest(),
            ),
            patch(
                "raise_cli.gates.builtin._runner.subprocess.run",
                return_value=_completed_process(0),
            ) as mock_run,
        ):
            result = gate.evaluate(ctx)
        assert result.passed is True
        mock_run.assert_called_once()

    def test_fail(self) -> None:
        from raise_cli.gates.builtin.types import TypeGate

        gate = TypeGate()
        ctx = GateContext(gate_id="gate-types")
        with (
            patch(
                "raise_cli.gates.builtin._runner.load_manifest",
                return_value=_make_manifest(),
            ),
            patch(
                "raise_cli.gates.builtin._runner.subprocess.run",
                return_value=_completed_process(1, stdout="1 error"),
            ),
        ):
            result = gate.evaluate(ctx)
        assert result.passed is False

    def test_exception_returns_failed(self) -> None:
        from raise_cli.gates.builtin.types import TypeGate

        gate = TypeGate()
        ctx = GateContext(gate_id="gate-types")
        with (
            patch(
                "raise_cli.gates.builtin._runner.load_manifest",
                return_value=_make_manifest(),
            ),
            patch(
                "raise_cli.gates.builtin._runner.subprocess.run",
                side_effect=FileNotFoundError("pyright not found"),
            ),
        ):
            result = gate.evaluate(ctx)
        assert result.passed is False
        assert "pyright not found" in result.message


class TestLintGate:
    def test_pass(self) -> None:
        from raise_cli.gates.builtin.lint import LintGate

        gate = LintGate()
        ctx = GateContext(gate_id="gate-lint")
        with (
            patch(
                "raise_cli.gates.builtin._runner.load_manifest",
                return_value=_make_manifest(),
            ),
            patch(
                "raise_cli.gates.builtin._runner.subprocess.run",
                return_value=_completed_process(0),
            ) as mock_run,
        ):
            result = gate.evaluate(ctx)
        assert result.passed is True
        mock_run.assert_called_once()

    def test_fail(self) -> None:
        from raise_cli.gates.builtin.lint import LintGate

        gate = LintGate()
        ctx = GateContext(gate_id="gate-lint")
        with (
            patch(
                "raise_cli.gates.builtin._runner.load_manifest",
                return_value=_make_manifest(),
            ),
            patch(
                "raise_cli.gates.builtin._runner.subprocess.run",
                return_value=_completed_process(1, stdout="E501 line too long"),
            ),
        ):
            result = gate.evaluate(ctx)
        assert result.passed is False

    def test_exception_returns_failed(self) -> None:
        from raise_cli.gates.builtin.lint import LintGate

        gate = LintGate()
        ctx = GateContext(gate_id="gate-lint")
        with (
            patch(
                "raise_cli.gates.builtin._runner.load_manifest",
                return_value=_make_manifest(),
            ),
            patch(
                "raise_cli.gates.builtin._runner.subprocess.run",
                side_effect=FileNotFoundError("ruff not found"),
            ),
        ):
            result = gate.evaluate(ctx)
        assert result.passed is False


class TestCoverageGate:
    def test_pass(self) -> None:
        from raise_cli.gates.builtin.coverage import CoverageGate

        gate = CoverageGate()
        ctx = GateContext(gate_id="gate-coverage")
        with (
            patch(
                "raise_cli.gates.builtin.coverage.load_manifest",
                return_value=_make_manifest(),
            ),
            patch(
                "raise_cli.gates.builtin.coverage.subprocess.run",
                return_value=_completed_process(0),
            ) as mock_run,
        ):
            result = gate.evaluate(ctx)
        assert result.passed is True
        mock_run.assert_called_once()
        cmd_args = mock_run.call_args[0][0]
        assert "--cov" in cmd_args

    def test_fail(self) -> None:
        from raise_cli.gates.builtin.coverage import CoverageGate

        gate = CoverageGate()
        ctx = GateContext(gate_id="gate-coverage")
        with (
            patch(
                "raise_cli.gates.builtin.coverage.load_manifest",
                return_value=_make_manifest(),
            ),
            patch(
                "raise_cli.gates.builtin.coverage.subprocess.run",
                return_value=_completed_process(1, stdout="TOTAL 45%"),
            ),
        ):
            result = gate.evaluate(ctx)
        assert result.passed is False

    def test_exception_returns_failed(self) -> None:
        from raise_cli.gates.builtin.coverage import CoverageGate

        gate = CoverageGate()
        ctx = GateContext(gate_id="gate-coverage")
        with (
            patch(
                "raise_cli.gates.builtin.coverage.load_manifest",
                return_value=_make_manifest(),
            ),
            patch(
                "raise_cli.gates.builtin.coverage.subprocess.run",
                side_effect=FileNotFoundError("pytest not found"),
            ),
        ):
            result = gate.evaluate(ctx)
        assert result.passed is False

    def test_skips_when_test_command_not_configured(self) -> None:
        from raise_cli.gates.builtin.coverage import CoverageGate

        gate = CoverageGate()
        ctx = GateContext(gate_id="gate-coverage")
        with patch(
            "raise_cli.gates.builtin.coverage.load_manifest",
            return_value=_make_manifest(test_command=None),
        ):
            result = gate.evaluate(ctx)
        assert result.passed is True
        assert "not configured" in result.message.lower()


class TestFormatGate:
    def test_pass(self) -> None:
        from raise_cli.gates.builtin.format import FormatGate

        gate = FormatGate()
        ctx = GateContext(gate_id="gate-format")
        with (
            patch(
                "raise_cli.gates.builtin._runner.load_manifest",
                return_value=_make_manifest(),
            ),
            patch(
                "raise_cli.gates.builtin._runner.subprocess.run",
                return_value=_completed_process(0),
            ) as mock_run,
        ):
            result = gate.evaluate(ctx)
        assert result.passed is True
        assert result.gate_id == "gate-format"
        mock_run.assert_called_once()

    def test_fail(self) -> None:
        from raise_cli.gates.builtin.format import FormatGate

        gate = FormatGate()
        ctx = GateContext(gate_id="gate-format")
        with (
            patch(
                "raise_cli.gates.builtin._runner.load_manifest",
                return_value=_make_manifest(),
            ),
            patch(
                "raise_cli.gates.builtin._runner.subprocess.run",
                return_value=_completed_process(1, stdout="Would reformat: src/foo.py"),
            ),
        ):
            result = gate.evaluate(ctx)
        assert result.passed is False
        assert result.details != ()

    def test_skip_when_not_configured(self) -> None:
        from raise_cli.gates.builtin.format import FormatGate

        gate = FormatGate()
        ctx = GateContext(gate_id="gate-format")
        with patch(
            "raise_cli.gates.builtin._runner.load_manifest",
            return_value=_make_manifest(format_command=None),
        ):
            result = gate.evaluate(ctx)
        assert result.passed is True
        assert "not configured" in result.message.lower()

    def test_no_manifest_returns_failed(self) -> None:
        from raise_cli.gates.builtin.format import FormatGate

        gate = FormatGate()
        ctx = GateContext(gate_id="gate-format")
        with patch("raise_cli.gates.builtin._runner.load_manifest", return_value=None):
            result = gate.evaluate(ctx)
        assert result.passed is False
        assert "manifest" in result.message.lower()

    def test_exception_returns_failed(self) -> None:
        from raise_cli.gates.builtin.format import FormatGate

        gate = FormatGate()
        ctx = GateContext(gate_id="gate-format")
        with (
            patch(
                "raise_cli.gates.builtin._runner.load_manifest",
                return_value=_make_manifest(),
            ),
            patch(
                "raise_cli.gates.builtin._runner.subprocess.run",
                side_effect=FileNotFoundError("ruff not found"),
            ),
        ):
            result = gate.evaluate(ctx)
        assert result.passed is False


class TestEntryPointDiscovery:
    def test_registry_discovers_all_five(self) -> None:
        registry = GateRegistry()
        registry.discover()
        gate_ids = {g.gate_id for g in registry.gates}
        assert "gate-tests" in gate_ids
        assert "gate-types" in gate_ids
        assert "gate-lint" in gate_ids
        assert "gate-coverage" in gate_ids
        assert "gate-format" in gate_ids

    def test_all_gates_target_release_publish(self) -> None:
        registry = GateRegistry()
        registry.discover()
        for gate in registry.gates:
            if gate.gate_id.startswith("gate-"):
                assert gate.workflow_point == "before:release:publish"
