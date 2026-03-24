"""E2E integration tests for the gate pipeline.

Verifies the full flow: register → discover → check → result.
Uses real GateRegistry (no mocks on registry internals).
"""

from __future__ import annotations

from typing import ClassVar
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from raise_cli.cli.main import app
from raise_cli.gates import GateContext, GateRegistry, GateResult, WorkflowGate

runner = CliRunner()


# ---------------------------------------------------------------------------
# Test gates
# ---------------------------------------------------------------------------


class _AlwaysPassGate:
    gate_id: ClassVar[str] = "gate-pass"
    description: ClassVar[str] = "Always passes"
    workflow_point: ClassVar[str] = "before:release:publish"

    def evaluate(self, context: GateContext) -> GateResult:
        return GateResult(passed=True, gate_id=self.gate_id, message="OK")


class _CommitGate:
    gate_id: ClassVar[str] = "gate-commit"
    description: ClassVar[str] = "Commit check"
    workflow_point: ClassVar[str] = "before:commit"

    def evaluate(self, context: GateContext) -> GateResult:
        return GateResult(passed=True, gate_id=self.gate_id, message="OK")


class _AlwaysFailGate:
    gate_id: ClassVar[str] = "gate-fail"
    description: ClassVar[str] = "Always fails"
    workflow_point: ClassVar[str] = "before:release:publish"

    def evaluate(self, context: GateContext) -> GateResult:
        return GateResult(
            passed=False,
            gate_id=self.gate_id,
            message="Nope",
            details=("Detail line 1",),
        )


# ---------------------------------------------------------------------------
# E2E: Registry → Gate → Result
# ---------------------------------------------------------------------------


class TestGatePipelineE2E:
    """Full pipeline without CLI — registry + evaluate."""

    def test_register_and_evaluate(self) -> None:
        reg = GateRegistry()
        gate = _AlwaysPassGate()
        reg.register(gate)

        found = reg.get_gate("gate-pass")
        assert found is not None
        assert isinstance(found, WorkflowGate)

        result = found.evaluate(GateContext(gate_id="gate-pass"))
        assert result.passed is True

    def test_all_must_pass_semantics(self) -> None:
        """All gates run; one failure means overall failure."""
        reg = GateRegistry()
        reg.register(_AlwaysPassGate())
        reg.register(_AlwaysFailGate())

        results: list[GateResult] = []
        for gate in reg.gates:
            ctx = GateContext(gate_id=gate.gate_id)
            results.append(gate.evaluate(ctx))

        assert len(results) == 2
        assert any(r.passed for r in results)
        assert any(not r.passed for r in results)
        # All-must-pass: overall = fail
        all_passed = all(r.passed for r in results)
        assert not all_passed

    def test_get_gates_for_point_filters(self) -> None:
        reg = GateRegistry()
        reg.register(_AlwaysPassGate())  # before:release:publish
        reg.register(_CommitGate())  # before:commit

        release_gates = reg.get_gates_for_point("before:release:publish")
        assert len(release_gates) == 1
        assert release_gates[0].gate_id == "gate-pass"


# ---------------------------------------------------------------------------
# E2E: Entry point discovery → CLI
# ---------------------------------------------------------------------------


class TestGateDiscoveryE2E:
    """Entry point discovery through CLI."""

    def _make_ep(self, name: str, cls: type) -> MagicMock:
        ep = MagicMock()
        ep.name = name
        ep.load.return_value = cls
        ep.dist = MagicMock()
        ep.dist.name = "raise-cli"
        return ep

    def test_discover_and_list(self) -> None:
        ep = self._make_ep("pass", _AlwaysPassGate)
        with patch("raise_cli.gates.registry.entry_points", return_value=[ep]):
            result = runner.invoke(app, ["gate", "list"])
        assert result.exit_code == 0
        assert "gate-pass" in result.output

    def test_discover_and_check(self) -> None:
        ep = self._make_ep("pass", _AlwaysPassGate)
        with patch("raise_cli.gates.registry.entry_points", return_value=[ep]):
            result = runner.invoke(app, ["gate", "check", "gate-pass"])
        assert result.exit_code == 0

    def test_discover_and_check_all_mixed(self) -> None:
        ep1 = self._make_ep("pass", _AlwaysPassGate)
        ep2 = self._make_ep("fail", _AlwaysFailGate)
        with patch("raise_cli.gates.registry.entry_points", return_value=[ep1, ep2]):
            result = runner.invoke(app, ["gate", "check", "--all"])
        assert result.exit_code == 1
        assert "gate-pass" in result.output
        assert "gate-fail" in result.output
        assert "FAILED" in result.output


# ---------------------------------------------------------------------------
# Public API exports
# ---------------------------------------------------------------------------


class TestPublicAPI:
    """Verify __init__.py exports are correct."""

    def test_exports(self) -> None:
        from raise_cli.gates import __all__

        assert "WorkflowGate" in __all__
        assert "GateContext" in __all__
        assert "GateResult" in __all__
        assert "GateRegistry" in __all__
