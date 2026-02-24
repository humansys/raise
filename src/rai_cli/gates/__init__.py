"""Workflow gates infrastructure for rai-cli.

Provides standalone quality gates that validate workflow transitions.
Gates are independent of the event emitter (AD-5) and can be invoked
directly via ``rai gate check``.

Architecture: ADR-039 §1 (WorkflowGate Protocol), §5 (Standalone gates)
"""

from rai_cli.gates.models import GateContext, GateResult
from rai_cli.gates.protocol import WorkflowGate
from rai_cli.gates.registry import GateRegistry

__all__ = [
    "GateContext",
    "GateRegistry",
    "GateResult",
    "WorkflowGate",
]
