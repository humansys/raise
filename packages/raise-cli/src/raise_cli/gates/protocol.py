"""WorkflowGate Protocol — contract for gate implementations.

Gates guard workflow transitions. They validate and block operations.
A gate failure prevents the operation with an actionable message.

Architecture: ADR-039 §1 (WorkflowGate Protocol)
"""

from __future__ import annotations

from typing import ClassVar, Protocol, runtime_checkable

from raise_cli.gates.models import GateContext, GateResult


@runtime_checkable
class WorkflowGate(Protocol):
    """Contract for workflow gate implementations.

    Attributes:
        gate_id: Unique identifier (e.g. ``"gate-tests"``).
        description: Human-readable purpose (e.g. ``"All tests pass"``).
        workflow_point: When this gate runs (e.g. ``"before:release:publish"``).

    Example::

        class TestGate:
            gate_id = "gate-tests"
            description = "All tests pass"
            workflow_point = "before:release:publish"

            def evaluate(self, context: GateContext) -> GateResult:
                # run pytest, return result...
                return GateResult(passed=True, gate_id=self.gate_id)
    """

    gate_id: ClassVar[str]
    description: ClassVar[str]
    workflow_point: ClassVar[str]

    def evaluate(self, context: GateContext) -> GateResult: ...
