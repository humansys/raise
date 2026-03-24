"""Tests for WorkflowGate Protocol and gate dataclasses."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path
from typing import ClassVar

import pytest

from raise_cli.gates.models import GateContext, GateResult
from raise_cli.gates.protocol import WorkflowGate

# ---------------------------------------------------------------------------
# Fixtures — conformant and non-conformant gate implementations
# ---------------------------------------------------------------------------


class _ValidGate:
    """Minimal conformant WorkflowGate implementation."""

    gate_id: ClassVar[str] = "gate-test"
    description: ClassVar[str] = "Test gate"
    workflow_point: ClassVar[str] = "before:release:publish"

    def evaluate(self, context: GateContext) -> GateResult:
        return GateResult(passed=True, gate_id=self.gate_id)


class _FailingGate:
    """Gate that always fails with actionable message."""

    gate_id: ClassVar[str] = "gate-failing"
    description: ClassVar[str] = "Always fails"
    workflow_point: ClassVar[str] = "before:release:publish"

    def evaluate(self, context: GateContext) -> GateResult:
        return GateResult(
            passed=False,
            gate_id=self.gate_id,
            message="Tests failing. Run `pytest`.",
            details=("FAILED tests/test_foo.py::test_bar",),
        )


class _MissingEvaluate:
    """Non-conformant: missing evaluate method."""

    gate_id: ClassVar[str] = "gate-broken"
    description: ClassVar[str] = "Broken gate"
    workflow_point: ClassVar[str] = "before:release:publish"


# ---------------------------------------------------------------------------
# WorkflowGate Protocol conformance
# ---------------------------------------------------------------------------


class TestWorkflowGateProtocol:
    """Protocol conformance checks."""

    def test_valid_gate_is_instance(self) -> None:
        gate = _ValidGate()
        assert isinstance(gate, WorkflowGate)

    def test_missing_evaluate_is_not_instance(self) -> None:
        obj = _MissingEvaluate()
        assert not isinstance(obj, WorkflowGate)

    def test_protocol_is_runtime_checkable(self) -> None:
        assert hasattr(WorkflowGate, "__protocol_attrs__") or hasattr(
            WorkflowGate, "__abstractmethods__"
        )


# ---------------------------------------------------------------------------
# GateContext dataclass
# ---------------------------------------------------------------------------


class TestGateContext:
    """GateContext frozen dataclass tests."""

    def test_default_working_dir_is_cwd(self) -> None:
        ctx = GateContext(gate_id="gate-test")
        assert ctx.working_dir == Path.cwd()

    def test_custom_working_dir(self) -> None:
        ctx = GateContext(gate_id="gate-test", working_dir=Path("/tmp"))
        assert ctx.working_dir == Path("/tmp")

    def test_frozen(self) -> None:
        ctx = GateContext(gate_id="gate-test")
        with pytest.raises(FrozenInstanceError):
            ctx.gate_id = "mutated"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# GateResult dataclass
# ---------------------------------------------------------------------------


class TestGateResult:
    """GateResult frozen dataclass tests."""

    def test_passed_result(self) -> None:
        result = GateResult(passed=True, gate_id="gate-test")
        assert result.passed is True
        assert result.gate_id == "gate-test"
        assert result.message == ""
        assert result.details == ()

    def test_failed_result_with_details(self) -> None:
        result = GateResult(
            passed=False,
            gate_id="gate-types",
            message="Type errors found",
            details=("src/foo.py:12 — Incompatible type",),
        )
        assert result.passed is False
        assert result.message == "Type errors found"
        assert len(result.details) == 1

    def test_frozen(self) -> None:
        result = GateResult(passed=True, gate_id="gate-test")
        with pytest.raises(FrozenInstanceError):
            result.passed = False  # type: ignore[misc]
