"""Gate registry with entry point discovery.

Discovers WorkflowGate implementations registered via Python entry points
(``[project.entry-points."rai.gates"]`` in pyproject.toml). Validates
Protocol conformance before accepting gates.

Architecture: ADR-039 §3 (Entry point discovery via stevedore)
"""

from __future__ import annotations

import inspect
import logging
from importlib.metadata import entry_points
from typing import Any

from raise_cli.gates.protocol import WorkflowGate

logger = logging.getLogger(__name__)

EP_GATES: str = "rai.gates"


def _dist_name(ep: Any) -> str:
    """Best-effort extraction of the distribution name for an entry point."""
    try:
        return ep.dist.name  # type: ignore[union-attr]
    except AttributeError:
        return "unknown"


class GateRegistry:
    """Discovers and manages WorkflowGate implementations.

    Example::

        registry = GateRegistry()
        registry.discover()  # loads from rai.gates entry points

        for gate in registry.gates:
            print(f"{gate.gate_id}: {gate.description}")

        gate = registry.get_gate("gate-tests")
        release_gates = registry.get_gates_for_point("before:release:publish")
    """

    def __init__(self) -> None:
        self._gates: list[WorkflowGate] = []

    @property
    def gates(self) -> list[WorkflowGate]:
        """Return a copy of registered gates."""
        return list(self._gates)

    def discover(self) -> None:
        """Load gates from ``rai.gates`` entry points.

        Skips entry points that:
        - Fail to load (ImportError, etc.)
        - Are not classes
        - Don't conform to the WorkflowGate Protocol
        """
        for ep in entry_points(group=EP_GATES):
            try:
                loaded: Any = ep.load()
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "Skipping gate entry point '%s' from '%s': %s",
                    ep.name,
                    _dist_name(ep),
                    exc,
                )
                continue

            if not inspect.isclass(loaded):
                logger.warning(
                    "Skipping gate entry point '%s' from '%s': expected a class, got %s",
                    ep.name,
                    _dist_name(ep),
                    type(loaded).__name__,
                )
                continue

            instance = loaded()
            if not isinstance(instance, WorkflowGate):
                logger.warning(
                    "Skipping gate entry point '%s' from '%s': "
                    "does not conform to WorkflowGate Protocol",
                    ep.name,
                    _dist_name(ep),
                )
                continue

            existing = self.get_gate(instance.gate_id)
            if existing is not None:
                logger.warning(
                    "Duplicate gate_id '%s' from entry point '%s' — replacing previous",
                    instance.gate_id,
                    ep.name,
                )
                self._gates = [g for g in self._gates if g.gate_id != instance.gate_id]
            self._gates.append(instance)
            logger.debug(
                "Loaded gate '%s' (id=%s, point=%s)",
                ep.name,
                instance.gate_id,
                instance.workflow_point,
            )

    def register(self, gate: WorkflowGate | Any) -> None:
        """Manually register a gate instance (useful for testing).

        Silently skips non-compliant objects. Warns on duplicate gate IDs.
        """
        if not isinstance(gate, WorkflowGate):
            logger.warning(
                "Skipping manual gate registration: %s does not conform to WorkflowGate Protocol",
                type(gate).__name__,
            )
            return
        existing = self.get_gate(gate.gate_id)
        if existing is not None:
            logger.warning(
                "Duplicate gate_id '%s': replacing %s with %s",
                gate.gate_id,
                type(existing).__name__,
                type(gate).__name__,
            )
            self._gates = [g for g in self._gates if g.gate_id != gate.gate_id]
        self._gates.append(gate)

    def get_gate(self, gate_id: str) -> WorkflowGate | None:
        """Return the gate with the given ID, or ``None``."""
        for gate in self._gates:
            if gate.gate_id == gate_id:
                return gate
        return None

    def get_gates_for_point(self, workflow_point: str) -> list[WorkflowGate]:
        """Return gates registered for the given workflow point."""
        return [g for g in self._gates if g.workflow_point == workflow_point]
