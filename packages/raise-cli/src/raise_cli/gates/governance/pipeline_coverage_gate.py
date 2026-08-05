"""Pipeline coverage gate — fail-closed C1-C7 workflow state coverage check.

Promoted from advisory (S5 RAISE-15032) to fail-closed (S10 RAISE-15037).
Returns ``passed=False`` when coverage gaps are detected so ``rai gate check``
blocks the transition rather than reporting only.

Architecture: ADR-039 (WorkflowGate Protocol), S5 (RAISE-15032), S10 (RAISE-15037)
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, ClassVar

from raise_cli.gates.models import GateContext, GateResult

if TYPE_CHECKING:
    from raise_core.workflow.state_machine import WorkflowStateMachine

logger = logging.getLogger(__name__)


class PipelineCoverageGate:
    """Fail-closed gate: pipeline phase coverage (C1-C7, blocking).

    Checks that pipeline phases' ``target_status`` values cover all managed
    states in the WorkflowStateMachine.  Any gap is reported in the gate
    message and ``passed=False`` is returned — this gate blocks a workflow
    transition when gaps are found (promoted from advisory in S10 RAISE-15037).

    Registered via ``rai.gates`` entry point in pyproject.toml.
    """

    gate_id: ClassVar[str] = "pipeline-coverage"
    description: ClassVar[str] = (
        "Pipeline phase coverage — C1-C7 workflow state checks (blocking)"
    )
    workflow_point: ClassVar[str] = "before:story:close"
    is_blocker: ClassVar[bool] = True

    def __init__(
        self,
        machine: WorkflowStateMachine | None = None,
    ) -> None:
        """Initialise with an optional injected machine.

        When ``machine`` is ``None`` (the default, used by the entry-point
        registry), the gate attempts to discover a machine from the project
        at evaluation time.
        """
        self._machine = machine

    def evaluate(self, context: GateContext) -> GateResult:
        """Run C1-C7 checks and return a fail-closed result.

        When a workflow state machine is not configured, the gate returns a
        clean pass with an explanatory skip message (no machine = no contract
        to enforce).  When checks find gaps, ``passed=False`` is returned with
        the failing check IDs in ``details`` (S10 RAISE-15037 promotion from
        advisory).
        """
        from raise_cli.doctor.checks.pipeline_coverage import (
            collect_target_statuses,
            discover_machine,
        )
        from raise_core.workflow.coverage import run_coverage_checks

        machine = self._machine or discover_machine(context.working_dir)

        if machine is None:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message=(
                    "no workflow state machine configured — "
                    "C1-C7 coverage checks skipped"
                ),
            )

        phase_statuses = collect_target_statuses(context.working_dir)
        results = run_coverage_checks(machine, phase_statuses)

        failed = [r for r in results if not r.passed]
        if not failed:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="C1-C7: all pipeline coverage checks pass",
            )

        gap_lines = [f"{r.check_id}: {r.message}" for r in failed]
        details = tuple(gap_lines)
        summary = (
            f"{len(failed)} coverage gap(s) found — "
            "pipeline phases do not cover all workflow states"
        )
        return GateResult(
            passed=False,
            gate_id=self.gate_id,
            message=summary,
            details=details,
        )
