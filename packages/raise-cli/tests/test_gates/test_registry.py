"""Tests for GateRegistry with entry point discovery."""

from __future__ import annotations

from typing import Any, ClassVar
from unittest.mock import MagicMock, patch

from raise_cli.gates.models import GateContext, GateResult
from raise_cli.gates.registry import EP_GATES, GateRegistry

# ---------------------------------------------------------------------------
# Test gate implementations
# ---------------------------------------------------------------------------


class _TestGate:
    gate_id: ClassVar[str] = "gate-tests"
    description: ClassVar[str] = "All tests pass"
    workflow_point: ClassVar[str] = "before:release:publish"

    def evaluate(self, context: GateContext) -> GateResult:
        return GateResult(passed=True, gate_id=self.gate_id)


class _LintGate:
    gate_id: ClassVar[str] = "gate-lint"
    description: ClassVar[str] = "Linting passes"
    workflow_point: ClassVar[str] = "before:release:publish"

    def evaluate(self, context: GateContext) -> GateResult:
        return GateResult(passed=True, gate_id=self.gate_id)


class _CommitGate:
    gate_id: ClassVar[str] = "gate-commit"
    description: ClassVar[str] = "Commit checks"
    workflow_point: ClassVar[str] = "before:commit"

    def evaluate(self, context: GateContext) -> GateResult:
        return GateResult(passed=True, gate_id=self.gate_id)


class _NotAGate:
    """Non-conformant — missing evaluate."""

    gate_id: ClassVar[str] = "gate-broken"
    description: ClassVar[str] = "Broken"
    workflow_point: ClassVar[str] = "before:release:publish"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_entry_point(name: str, cls: type[Any]) -> MagicMock:
    ep = MagicMock()
    ep.name = name
    ep.load.return_value = cls
    ep.dist = MagicMock()
    ep.dist.name = "test-dist"
    return ep


# ---------------------------------------------------------------------------
# Registry basics
# ---------------------------------------------------------------------------


class TestGateRegistryBasics:
    def test_empty_registry(self) -> None:
        reg = GateRegistry()
        assert reg.gates == []

    def test_register_conformant_gate(self) -> None:
        reg = GateRegistry()
        reg.register(_TestGate())
        assert len(reg.gates) == 1

    def test_register_non_conformant_skipped(self) -> None:
        reg = GateRegistry()
        reg.register(_NotAGate())  # type: ignore[arg-type]
        assert len(reg.gates) == 0

    def test_gates_returns_copy(self) -> None:
        reg = GateRegistry()
        reg.register(_TestGate())
        gates1 = reg.gates
        gates2 = reg.gates
        assert gates1 is not gates2
        assert len(gates1) == len(gates2)

    def test_duplicate_gate_id_replaces(self) -> None:
        reg = GateRegistry()
        gate1 = _TestGate()
        gate2 = _TestGate()
        reg.register(gate1)
        reg.register(gate2)
        assert len(reg.gates) == 1
        assert reg.gates[0] is gate2


# ---------------------------------------------------------------------------
# Lookup methods
# ---------------------------------------------------------------------------


class TestGateRegistryLookup:
    def test_get_gate_by_id(self) -> None:
        reg = GateRegistry()
        reg.register(_TestGate())
        reg.register(_LintGate())
        gate = reg.get_gate("gate-tests")
        assert gate is not None
        assert gate.gate_id == "gate-tests"

    def test_get_gate_not_found(self) -> None:
        reg = GateRegistry()
        reg.register(_TestGate())
        assert reg.get_gate("nonexistent") is None

    def test_get_gates_for_point(self) -> None:
        reg = GateRegistry()
        reg.register(_TestGate())
        reg.register(_LintGate())
        reg.register(_CommitGate())
        release_gates = reg.get_gates_for_point("before:release:publish")
        assert len(release_gates) == 2
        ids = {g.gate_id for g in release_gates}
        assert ids == {"gate-tests", "gate-lint"}

    def test_get_gates_for_point_no_match(self) -> None:
        reg = GateRegistry()
        reg.register(_TestGate())
        assert reg.get_gates_for_point("before:deploy") == []


# ---------------------------------------------------------------------------
# Entry point discovery
# ---------------------------------------------------------------------------


class TestGateRegistryDiscover:
    def test_discover_loads_conformant_gates(self) -> None:
        ep = _make_entry_point("tests", _TestGate)
        with patch("raise_cli.gates.registry.entry_points", return_value=[ep]):
            reg = GateRegistry()
            reg.discover()
        assert len(reg.gates) == 1
        assert reg.gates[0].gate_id == "gate-tests"

    def test_discover_skips_non_class(self) -> None:
        ep = _make_entry_point("func", _TestGate)
        ep.load.return_value = "not-a-class"  # not a class
        with patch("raise_cli.gates.registry.entry_points", return_value=[ep]):
            reg = GateRegistry()
            reg.discover()
        assert len(reg.gates) == 0

    def test_discover_skips_non_conformant(self) -> None:
        ep = _make_entry_point("broken", _NotAGate)
        with patch("raise_cli.gates.registry.entry_points", return_value=[ep]):
            reg = GateRegistry()
            reg.discover()
        assert len(reg.gates) == 0

    def test_discover_skips_import_error(self) -> None:
        ep = _make_entry_point("bad", _TestGate)
        ep.load.side_effect = ImportError("missing module")
        with patch("raise_cli.gates.registry.entry_points", return_value=[ep]):
            reg = GateRegistry()
            reg.discover()
        assert len(reg.gates) == 0

    def test_discover_uses_correct_group(self) -> None:
        assert EP_GATES == "rai.gates"
        with patch("raise_cli.gates.registry.entry_points", return_value=[]) as mock_ep:
            reg = GateRegistry()
            reg.discover()
        mock_ep.assert_called_once_with(group="rai.gates")

    def test_discover_multiple_gates(self) -> None:
        ep1 = _make_entry_point("tests", _TestGate)
        ep2 = _make_entry_point("lint", _LintGate)
        with patch("raise_cli.gates.registry.entry_points", return_value=[ep1, ep2]):
            reg = GateRegistry()
            reg.discover()
        assert len(reg.gates) == 2
