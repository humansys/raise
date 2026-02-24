"""Tests for built-in quality gates (tests, types, lint, coverage)."""

from __future__ import annotations

import subprocess
from unittest.mock import patch

import pytest

from rai_cli.gates.models import GateContext, GateResult
from rai_cli.gates.protocol import WorkflowGate
from rai_cli.gates.registry import GateRegistry

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _completed_process(returncode: int, stdout: str = "", stderr: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(
        args=[], returncode=returncode, stdout=stdout, stderr=stderr
    )


# ---------------------------------------------------------------------------
# Protocol conformance — all 4 gates
# ---------------------------------------------------------------------------


class TestProtocolConformance:
    """All built-in gates must implement WorkflowGate Protocol."""

    @pytest.fixture(
        params=[
            "rai_cli.gates.builtin.tests:TestGate",
            "rai_cli.gates.builtin.types:TypeGate",
            "rai_cli.gates.builtin.lint:LintGate",
            "rai_cli.gates.builtin.coverage:CoverageGate",
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
        with patch("subprocess.run", return_value=_completed_process(0)):
            result = gate_instance.evaluate(ctx)
        assert isinstance(result, GateResult)
        assert result.gate_id == gate_instance.gate_id


# ---------------------------------------------------------------------------
# TestGate
# ---------------------------------------------------------------------------


class TestTestGate:
    """TestGate runs pytest -x --tb=short."""

    def test_pass(self) -> None:
        from rai_cli.gates.builtin.tests import TestGate

        gate = TestGate()
        ctx = GateContext(gate_id="gate-tests")
        with patch("subprocess.run", return_value=_completed_process(0, stdout="4 passed")) as mock:
            result = gate.evaluate(ctx)
        assert result.passed is True
        assert result.gate_id == "gate-tests"
        mock.assert_called_once()
        args = mock.call_args
        assert "pytest" in args[0][0]

    def test_fail(self) -> None:
        from rai_cli.gates.builtin.tests import TestGate

        gate = TestGate()
        ctx = GateContext(gate_id="gate-tests")
        with patch("subprocess.run", return_value=_completed_process(1, stdout="FAILED test_foo")):
            result = gate.evaluate(ctx)
        assert result.passed is False
        assert result.details != ()

    def test_exception_returns_failed(self) -> None:
        from rai_cli.gates.builtin.tests import TestGate

        gate = TestGate()
        ctx = GateContext(gate_id="gate-tests")
        with patch("subprocess.run", side_effect=FileNotFoundError("pytest not found")):
            result = gate.evaluate(ctx)
        assert result.passed is False
        assert "pytest not found" in result.message

    def test_uses_working_dir(self, tmp_path: object) -> None:
        from pathlib import Path

        from rai_cli.gates.builtin.tests import TestGate

        gate = TestGate()
        ctx = GateContext(gate_id="gate-tests", working_dir=Path("/some/project"))
        with patch("subprocess.run", return_value=_completed_process(0)) as mock:
            gate.evaluate(ctx)
        assert mock.call_args.kwargs.get("cwd") == str(Path("/some/project"))


# ---------------------------------------------------------------------------
# TypeGate
# ---------------------------------------------------------------------------


class TestTypeGate:
    """TypeGate runs pyright."""

    def test_pass(self) -> None:
        from rai_cli.gates.builtin.types import TypeGate

        gate = TypeGate()
        ctx = GateContext(gate_id="gate-types")
        with patch("subprocess.run", return_value=_completed_process(0)) as mock:
            result = gate.evaluate(ctx)
        assert result.passed is True
        mock.assert_called_once()
        assert "pyright" in mock.call_args[0][0]

    def test_fail(self) -> None:
        from rai_cli.gates.builtin.types import TypeGate

        gate = TypeGate()
        ctx = GateContext(gate_id="gate-types")
        with patch("subprocess.run", return_value=_completed_process(1, stdout="1 error")):
            result = gate.evaluate(ctx)
        assert result.passed is False

    def test_exception_returns_failed(self) -> None:
        from rai_cli.gates.builtin.types import TypeGate

        gate = TypeGate()
        ctx = GateContext(gate_id="gate-types")
        with patch("subprocess.run", side_effect=FileNotFoundError("pyright not found")):
            result = gate.evaluate(ctx)
        assert result.passed is False
        assert "pyright not found" in result.message


# ---------------------------------------------------------------------------
# LintGate
# ---------------------------------------------------------------------------


class TestLintGate:
    """LintGate runs ruff check."""

    def test_pass(self) -> None:
        from rai_cli.gates.builtin.lint import LintGate

        gate = LintGate()
        ctx = GateContext(gate_id="gate-lint")
        with patch("subprocess.run", return_value=_completed_process(0)) as mock:
            result = gate.evaluate(ctx)
        assert result.passed is True
        mock.assert_called_once()
        assert "ruff" in mock.call_args[0][0]

    def test_fail(self) -> None:
        from rai_cli.gates.builtin.lint import LintGate

        gate = LintGate()
        ctx = GateContext(gate_id="gate-lint")
        with patch("subprocess.run", return_value=_completed_process(1, stdout="E501 line too long")):
            result = gate.evaluate(ctx)
        assert result.passed is False

    def test_exception_returns_failed(self) -> None:
        from rai_cli.gates.builtin.lint import LintGate

        gate = LintGate()
        ctx = GateContext(gate_id="gate-lint")
        with patch("subprocess.run", side_effect=FileNotFoundError("ruff not found")):
            result = gate.evaluate(ctx)
        assert result.passed is False


# ---------------------------------------------------------------------------
# CoverageGate
# ---------------------------------------------------------------------------


class TestCoverageGate:
    """CoverageGate runs pytest --cov."""

    def test_pass(self) -> None:
        from rai_cli.gates.builtin.coverage import CoverageGate

        gate = CoverageGate()
        ctx = GateContext(gate_id="gate-coverage")
        with patch("subprocess.run", return_value=_completed_process(0)) as mock:
            result = gate.evaluate(ctx)
        assert result.passed is True
        mock.assert_called_once()
        assert "--cov" in mock.call_args[0][0]

    def test_fail(self) -> None:
        from rai_cli.gates.builtin.coverage import CoverageGate

        gate = CoverageGate()
        ctx = GateContext(gate_id="gate-coverage")
        with patch("subprocess.run", return_value=_completed_process(1, stdout="TOTAL 45%")):
            result = gate.evaluate(ctx)
        assert result.passed is False

    def test_exception_returns_failed(self) -> None:
        from rai_cli.gates.builtin.coverage import CoverageGate

        gate = CoverageGate()
        ctx = GateContext(gate_id="gate-coverage")
        with patch("subprocess.run", side_effect=FileNotFoundError("pytest not found")):
            result = gate.evaluate(ctx)
        assert result.passed is False


# ---------------------------------------------------------------------------
# Entry point discovery
# ---------------------------------------------------------------------------


class TestEntryPointDiscovery:
    """All 4 gates are discoverable via rai.gates entry points."""

    def test_registry_discovers_all_four(self) -> None:
        registry = GateRegistry()
        registry.discover()
        gate_ids = {g.gate_id for g in registry.gates}
        assert "gate-tests" in gate_ids
        assert "gate-types" in gate_ids
        assert "gate-lint" in gate_ids
        assert "gate-coverage" in gate_ids

    def test_all_gates_target_release_publish(self) -> None:
        registry = GateRegistry()
        registry.discover()
        for gate in registry.gates:
            if gate.gate_id.startswith("gate-"):
                assert gate.workflow_point == "before:release:publish"
