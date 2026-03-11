"""Workflow gates infrastructure for raise-cli.

Provides standalone quality gates that validate workflow transitions.
Gates are independent of the event emitter (AD-5) and can be invoked
directly via ``rai gate check``.

Architecture: ADR-039 §1 (WorkflowGate Protocol), §5 (Standalone gates)
"""

from raise_cli.gates.models import GateContext, GateResult
from raise_cli.gates.protocol import WorkflowGate
from raise_cli.gates.registry import GateRegistry

__all__ = [
    "GateContext",
    "GateRegistry",
    "GateResult",
    "WorkflowGate",
]
