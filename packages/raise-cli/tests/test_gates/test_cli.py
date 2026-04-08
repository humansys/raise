"""Tests for ``rai gate`` CLI commands."""

from __future__ import annotations

from typing import ClassVar
from unittest.mock import patch

from typer.testing import CliRunner

from raise_cli.cli.main import app
from raise_cli.gates.models import GateContext, GateResult
from raise_cli.gates.registry import GateRegistry

runner = CliRunner()


# ---------------------------------------------------------------------------
# Test gate implementations
# ---------------------------------------------------------------------------


class _PassingGate:
    gate_id: ClassVar[str] = "gate-tests"
    description: ClassVar[str] = "All tests pass"
    workflow_point: ClassVar[str] = "before:release:publish"

    def evaluate(self, context: GateContext) -> GateResult:
        return GateResult(passed=True, gate_id=self.gate_id, message="Tests pass")


class _FailingGate:
    gate_id: ClassVar[str] = "gate-types"
    description: ClassVar[str] = "No type errors"
    workflow_point: ClassVar[str] = "before:release:publish"

    def evaluate(self, context: GateContext) -> GateResult:
        return GateResult(
            passed=False,
            gate_id=self.gate_id,
            message="Type errors found",
            details=("src/foo.py:12 — Incompatible type",),
        )


class _ExplodingGate:
    gate_id: ClassVar[str] = "gate-explode"
    description: ClassVar[str] = "Explodes on evaluate"
    workflow_point: ClassVar[str] = "before:release:publish"

    def evaluate(self, context: GateContext) -> GateResult:
        msg = "Boom!"
        raise RuntimeError(msg)


def _registry_with(*gates: object) -> GateRegistry:
    reg = GateRegistry()
    for g in gates:
        reg.register(g)
    return reg


# ---------------------------------------------------------------------------
# rai gate list
# ---------------------------------------------------------------------------


class TestGateList:
    def test_list_no_gates(self) -> None:
        with patch(
            "raise_cli.cli.commands.gate._get_registry",
            return_value=_registry_with(),
        ):
            result = runner.invoke(app, ["gate", "list"])
        assert result.exit_code == 0
        assert "No gates discovered" in result.output

    def test_list_shows_gates(self) -> None:
        with patch(
            "raise_cli.cli.commands.gate._get_registry",
            return_value=_registry_with(_PassingGate(), _FailingGate()),
        ):
            result = runner.invoke(app, ["gate", "list"])
        assert result.exit_code == 0
        assert "gate-tests" in result.output
        assert "gate-types" in result.output
        assert "All tests pass" in result.output

    def test_list_json(self) -> None:
        with patch(
            "raise_cli.cli.commands.gate._get_registry",
            return_value=_registry_with(_PassingGate()),
        ):
            result = runner.invoke(app, ["gate", "list", "--format", "json"])
        assert result.exit_code == 0
        assert '"gate_id"' in result.output
        assert '"gate-tests"' in result.output


# ---------------------------------------------------------------------------
# rai gate check <gate-id>
# ---------------------------------------------------------------------------


class TestGateCheckSingle:
    def test_check_passing_gate(self) -> None:
        with patch(
            "raise_cli.cli.commands.gate._get_registry",
            return_value=_registry_with(_PassingGate()),
        ):
            result = runner.invoke(app, ["gate", "check", "gate-tests"])
        assert result.exit_code == 0
        assert "gate-tests" in result.output

    def test_check_failing_gate(self) -> None:
        with patch(
            "raise_cli.cli.commands.gate._get_registry",
            return_value=_registry_with(_FailingGate()),
        ):
            result = runner.invoke(app, ["gate", "check", "gate-types"])
        assert result.exit_code == 1
        assert "gate-types" in result.output
        assert "Type errors found" in result.output

    def test_check_unknown_gate(self) -> None:
        with patch(
            "raise_cli.cli.commands.gate._get_registry",
            return_value=_registry_with(_PassingGate()),
        ):
            result = runner.invoke(app, ["gate", "check", "nonexistent"])
        assert result.exit_code == 1
        assert "not found" in result.output.lower()

    def test_check_exploding_gate_isolated(self) -> None:
        with patch(
            "raise_cli.cli.commands.gate._get_registry",
            return_value=_registry_with(_ExplodingGate()),
        ):
            result = runner.invoke(app, ["gate", "check", "gate-explode"])
        assert result.exit_code == 1
        assert "gate-explode" in result.output


# ---------------------------------------------------------------------------
# rai gate check --all
# ---------------------------------------------------------------------------


class TestGateCheckAll:
    def test_all_pass(self) -> None:
        with patch(
            "raise_cli.cli.commands.gate._get_registry",
            return_value=_registry_with(_PassingGate()),
        ):
            result = runner.invoke(app, ["gate", "check", "--all"])
        assert result.exit_code == 0
        assert "gate-tests" in result.output

    def test_some_fail(self) -> None:
        with patch(
            "raise_cli.cli.commands.gate._get_registry",
            return_value=_registry_with(_PassingGate(), _FailingGate()),
        ):
            result = runner.invoke(app, ["gate", "check", "--all"])
        assert result.exit_code == 1
        assert "gate-tests" in result.output
        assert "gate-types" in result.output

    def test_no_gates(self) -> None:
        with patch(
            "raise_cli.cli.commands.gate._get_registry",
            return_value=_registry_with(),
        ):
            result = runner.invoke(app, ["gate", "check", "--all"])
        assert result.exit_code == 0
        assert "No gates discovered" in result.output

    def test_check_all_json(self) -> None:
        with patch(
            "raise_cli.cli.commands.gate._get_registry",
            return_value=_registry_with(_PassingGate(), _FailingGate()),
        ):
            result = runner.invoke(app, ["gate", "check", "--all", "--format", "json"])
        assert result.exit_code == 1
        assert '"passed"' in result.output

    def test_exploding_gate_in_all(self) -> None:
        with patch(
            "raise_cli.cli.commands.gate._get_registry",
            return_value=_registry_with(_PassingGate(), _ExplodingGate()),
        ):
            result = runner.invoke(app, ["gate", "check", "--all"])
        assert result.exit_code == 1
        assert "gate-explode" in result.output
