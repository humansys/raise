"""C1-C7 coverage checks: validate pipeline phases cover all workflow states.

Checks whether a pipeline's declared ``target_status`` values cover the
states defined in the WorkflowStateMachine. These checks are diagnostic
(report-only, allow_failure=True in gate/doctor integration).

Stage 1 ships C1 and C2 as real checks; C3-C7 are stubs reserved for
subsequent stages.

Story: S5 (RAISE-15032) — Coverage Validator
"""

from __future__ import annotations

from dataclasses import dataclass, field

from raise_core.workflow.state_machine import WorkflowStateMachine


@dataclass(frozen=True)
class CoverageResult:
    """Result of a single coverage check.

    Attributes:
        check_id: Identifier in the form "C1" through "C7".
        passed: True when the check finds no gap.
        message: Human-readable summary suitable for CLI output.
        uncovered: State slugs that are not covered (empty when passed).
    """

    check_id: str
    passed: bool
    message: str
    uncovered: list[str] = field(default_factory=list)


def check_all_states_covered(
    machine: WorkflowStateMachine,
    phase_target_statuses: list[str],
) -> CoverageResult:
    """C1: Every managed state has at least one phase with target_status pointing to it.

    Unmanaged states (``machine.unmanaged_states``) are excluded from the gap
    analysis — they are advisory / external states not governed by the pipeline.

    Args:
        machine: The workflow state machine defining the managed state space.
        phase_target_statuses: Slugs collected from pipeline phase ``target_status``
            fields.

    Returns:
        CoverageResult with ``check_id="C1"``.
    """
    managed = frozenset(machine.states.keys()) - machine.unmanaged_states
    covered = frozenset(phase_target_statuses)
    uncovered = sorted(managed - covered)
    if uncovered:
        return CoverageResult(
            check_id="C1",
            passed=False,
            message=f"Uncovered managed states: {uncovered}",
            uncovered=uncovered,
        )
    return CoverageResult(
        check_id="C1",
        passed=True,
        message="All managed states are covered by pipeline phases",
        uncovered=[],
    )


def check_terminal_states_reachable(
    machine: WorkflowStateMachine,
    phase_target_statuses: list[str],
) -> CoverageResult:
    """C2: Every terminal state (no outgoing transitions) is a target_status in some phase.

    A terminal state that no phase targets is a dead-end that the pipeline can
    never reach through governed transitions — a governance gap.

    Args:
        machine: The workflow state machine.
        phase_target_statuses: Slugs collected from pipeline phase ``target_status``
            fields.

    Returns:
        CoverageResult with ``check_id="C2"``.
    """
    terminal = [slug for slug in machine.states if not machine.transitions.get(slug)]
    covered_terminals = frozenset(phase_target_statuses)
    uncovered = sorted(set(terminal) - covered_terminals)
    if uncovered:
        return CoverageResult(
            check_id="C2",
            passed=False,
            message=f"Terminal states not targeted by any phase: {uncovered}",
            uncovered=uncovered,
        )
    return CoverageResult(
        check_id="C2",
        passed=True,
        message="All terminal states are reachable via pipeline phases",
        uncovered=[],
    )


def run_coverage_checks(
    machine: WorkflowStateMachine,
    phase_target_statuses: list[str],
) -> list[CoverageResult]:
    """Run all C1-C7 coverage checks and return results in order.

    C1 and C2 are implemented in Stage 1.  C3-C7 are stubs that always
    return ``passed=True`` — they are reserved for subsequent stages.

    Args:
        machine: The workflow state machine defining the managed state space.
        phase_target_statuses: Target status slugs extracted from all pipeline
            phases' ``target_status`` fields.

    Returns:
        Exactly 7 ``CoverageResult`` objects, one per check, in C1..C7 order.
    """
    results: list[CoverageResult] = [
        check_all_states_covered(machine, phase_target_statuses),
        check_terminal_states_reachable(machine, phase_target_statuses),
    ]
    # C3-C7: stubs — not yet implemented in Stage 1
    for i in range(3, 8):
        results.append(
            CoverageResult(
                check_id=f"C{i}",
                passed=True,
                message="Not yet implemented (Stage 1 stub)",
                uncovered=[],
            )
        )
    return results
