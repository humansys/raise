"""Pipeline coverage doctor check — C1-C7 workflow state coverage checks.

Validates that a project's pipeline YAML phases have ``target_status`` fields
that cover all states defined in the WorkflowStateMachine.  All findings are
advisory (WARN, never ERROR) — coverage gaps are reported without blocking.

Architecture: ADR-045 (DoctorCheck Protocol), S5 (RAISE-15032)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

from raise_cli.doctor.models import CheckResult, CheckStatus, DoctorContext
from raise_cli.doctor.protocol import DoctorCheck

if TYPE_CHECKING:
    from raise_cli.pipeline.loader import PipelineLoader
    from raise_core.workflow.state_machine import WorkflowStateMachine

logger = logging.getLogger(__name__)

_CATEGORY = "pipeline"


def collect_target_statuses(
    project_root: Path,
    loader: PipelineLoader | None = None,
) -> list[str]:
    """Collect ``target_status`` values from every pipeline this project resolves.

    Routes through the pipeline loader's three-tier resolution — builtin
    ``pipelines_base/`` < project ``.raise/pipelines/`` < user
    ``~/.raise/pipelines/`` — rather than globbing the project tier alone.
    Every ``target_status`` that ships with RaiSE lives in the builtin tier, so
    the old single-tier glob reported total non-coverage even for a correctly
    configured project (RAISE-16986, epic RAISE-16981 design section 2.6).

    Resolution is per pipeline *name*, so a higher tier shadowing a lower one
    contributes only the winning file's statuses.  The result is therefore the
    **effective** set: the statuses the pipelines this project would actually
    run will target.  A blind union across tiers would instead credit a
    shadowed builtin pipeline with coverage the project does not have.

    Args:
        project_root: Project root, used to build the default loader.
        loader: Optional pre-built loader.  Injected by tests to bound the scan
            to explicit search paths — the default loader reads
            ``~/.raise/pipelines``, which would otherwise make assertions depend
            on the developer's home directory.

    Returns:
        Deduplicated, sorted status slugs.  Unloadable pipelines (unparseable
        YAML, schema violations, sub-pipeline depth errors) are skipped: a
        doctor check must never crash.
    """
    from raise_cli.pipeline.loader import create_loader

    active = loader if loader is not None else create_loader(project_root)

    collected: set[str] = set()
    for name in active.list_available():
        try:
            definition = active.load(name)
        except Exception:  # noqa: BLE001 — doctor checks must not crash
            logger.debug("Skipping unloadable pipeline: %s", name)
            continue
        for phase in definition.phases:
            if phase.target_status:
                collected.add(phase.target_status)
    return sorted(collected)


def discover_machine(project_root: Path) -> WorkflowStateMachine | None:
    """Load a WorkflowStateMachine from backlog.yaml via ``derive_state_machine``.

    Returns ``None`` when no workflow states are configured — the caller
    reports "no machine configured" and skips C1-C7 checks.
    """
    from raise_cli.adapters.backlog_config import derive_state_machine

    machine = derive_state_machine(project_root)
    return machine if machine.states else None


class PipelineCoverageCheck(DoctorCheck):
    """Doctor check: pipeline phase coverage — C1-C7 workflow state coverage.

    Validates that pipeline phases' ``target_status`` values cover all managed
    states in the WorkflowStateMachine.  All results are advisory (WARN level);
    gaps are surfaced without blocking.

    Registered via ``rai.doctor.checks`` entry point in pyproject.toml.
    """

    check_id: ClassVar[str] = "pipeline-coverage"
    category: ClassVar[str] = _CATEGORY
    description: ClassVar[str] = (
        "Pipeline phase coverage — C1-C7 workflow state coverage checks (advisory)"
    )
    requires_online: ClassVar[bool] = False

    def __init__(
        self,
        machine: WorkflowStateMachine | None = None,
        loader: PipelineLoader | None = None,
    ) -> None:
        """Initialise with an optional injected machine and pipeline loader.

        When ``machine`` is ``None`` (the default, used by the entry-point
        registry), the check attempts to discover a machine from the project
        at evaluation time.  ``loader`` is likewise optional and exists so
        tests can bound the pipeline scan to explicit search paths.
        """
        self._machine = machine
        self._loader = loader

    def evaluate(self, context: DoctorContext) -> list[CheckResult]:
        """Run C1-C7 checks and map results to doctor CheckResult objects.

        Returns:
            One WARN CheckResult per coverage gap, or a single PASS result
            when all checks pass.  If no machine is configured, returns a
            single WARN explaining that coverage checks require a workflow
            state machine.
        """
        from raise_core.workflow.coverage import run_coverage_checks

        root = context.working_dir
        machine = self._machine or discover_machine(root)

        if machine is None:
            return [
                CheckResult(
                    check_id="pipeline-coverage-machine",
                    category=self.category,
                    status=CheckStatus.WARN,
                    message=(
                        "no workflow state machine configured — "
                        "C1-C7 coverage checks skipped"
                    ),
                    fix_hint=(
                        "configure a workflow state machine to enable coverage checks"
                    ),
                )
            ]

        phase_statuses = collect_target_statuses(root, loader=self._loader)
        coverage_results = run_coverage_checks(machine, phase_statuses)

        check_results: list[CheckResult] = []
        all_passed = True
        for cr in coverage_results:
            if cr.passed:
                self._append_result(
                    check_results,
                    f"pipeline-coverage-{cr.check_id.lower()}",
                    CheckStatus.PASS,
                    cr.message,
                )
            else:
                all_passed = False
                detail = f"uncovered: {cr.uncovered}" if cr.uncovered else ""
                self._append_result(
                    check_results,
                    f"pipeline-coverage-{cr.check_id.lower()}",
                    CheckStatus.WARN,
                    cr.message,
                    fix_hint=detail,
                )

        if all_passed:
            # Consolidate 7 PASS results into one summary when everything is clean
            return [
                CheckResult(
                    check_id="pipeline-coverage",
                    category=self.category,
                    status=CheckStatus.PASS,
                    message="C1-C7: all pipeline coverage checks pass",
                )
            ]

        return check_results
