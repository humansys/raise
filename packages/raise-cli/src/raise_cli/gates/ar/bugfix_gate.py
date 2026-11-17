"""BugfixArchitectureReviewGate — guards bug close with mandatory AR confirmation.

Thin subclass of ArchitectureReviewGate with a different workflow point and
gate ID. All evaluation logic lives in the parent class.

Architecture: S2100.2, ADR-039 §1 (WorkflowGate Protocol)
"""

from __future__ import annotations

from typing import ClassVar

from raise_cli.gates.ar.story_gate import ArchitectureReviewGate


class BugfixArchitectureReviewGate(ArchitectureReviewGate):
    """Quality gate confirming architecture review before bug close."""

    gate_id: ClassVar[str] = "gate-ar-bugfix"
    description: ClassVar[str] = "Architecture review confirmed before bug close"
    workflow_point: ClassVar[str] = "before:bug:close"
