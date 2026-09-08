"""Pipeline coverage gate — report-only C1-C7 workflow state coverage check.

Promoted from advisory (S5 RAISE-15032) to fail-closed (S10 RAISE-15037), and
reverted to report-only here (RAISE-16986, Epic RAISE-16981): coverage gaps are
reported as advisory findings and never block a transition.  Enforcement
returns in Epic B (3.1.2) by flipping ``passed`` back to ``False``.

Architecture: ADR-039 (WorkflowGate Protocol), S5 (RAISE-15032),
S10 (RAISE-15037), RAISE-16986
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, ClassVar

from raise_cli.gates.models import GateContext, GateResult

if TYPE_CHECKING:
    from raise_core.workflow.state_machine import WorkflowStateMachine

logger = logging.getLogger(__name__)


class PipelineCoverageGate:
    """Report-only gate: pipeline phase coverage (C1-C7, non-blocking).

    Checks that pipeline phases' ``target_status`` values cover all managed
    states in the WorkflowStateMachine.  Gaps are returned as an *advisory*
    result — ``passed=True`` with ``advisory=True`` and the failing check IDs
    in ``details`` — so ``rai gate check`` reports them without blocking
    (RAISE-16986, reverting the S10 RAISE-15037 promotion).

    Registered via ``rai.gates`` entry point in pyproject.toml.
    """

    gate_id: ClassVar[str] = "pipeline-coverage"
    description: ClassVar[str] = (
        "Pipeline phase coverage — C1-C7 workflow state checks (report-only)"
    )
    workflow_point: ClassVar[str] = "before:story:close"
    # Presentation only: ``is_blocker`` is read once in ``src``, at
    # ``cli/commands/gate.py:135``, purely as a "[BLOCKER]" tag in
    # ``rai gate list``.  The exit code derives from ``passed`` alone
    # (``gate.py:266`` and ``gate.py:307-311``), so this flag is *not* the
    # mechanism that makes the gate non-blocking — ``advisory`` below is.
    is_blocker: ClassVar[bool] = False

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
        """Run C1-C7 checks and return a report-only result.

        When a workflow state machine is not configured, the gate returns a
        clean pass with an explanatory skip message (no machine = no contract
        to enforce).  When checks find gaps, ``passed=True`` is returned with
        ``advisory=True`` and the failing check IDs in ``details``:
        ``GateResult.advisory`` (RAISE-14280) means "carries live findings that
        do not flip ``passed``", so the gaps stay visible and machine-readable
        while the exit code stays 0.
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
            passed=True,
            advisory=True,
            gate_id=self.gate_id,
            message=summary,
            details=details,
        )
