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

import yaml

from raise_cli.doctor.models import CheckResult, CheckStatus, DoctorContext
from raise_cli.doctor.protocol import DoctorCheck

if TYPE_CHECKING:
    from raise_core.workflow.state_machine import WorkflowStateMachine

logger = logging.getLogger(__name__)

_PIPELINES_SUBDIR = Path(".raise") / "pipelines"
_CATEGORY = "pipeline"


def collect_target_statuses(project_root: Path) -> list[str]:
    """Scan pipeline YAMLs under ``.raise/pipelines/`` and collect target_status values.

    Returns a deduplicated, sorted list of status slugs found across all
    ``target_status`` fields in every phase of every pipeline.  Non-existent
    directories and malformed YAML files are silently skipped.
    """
    pipelines_dir = project_root / _PIPELINES_SUBDIR
    if not pipelines_dir.is_dir():
        return []

    collected: set[str] = set()
    for yaml_path in pipelines_dir.glob("*.yaml"):
        try:
            raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                continue
            phases = raw.get("phases", [])
            if not isinstance(phases, list):
                continue
            for phase in phases:
                if not isinstance(phase, dict):
                    continue
                ts = phase.get("target_status")
                if ts and isinstance(ts, str):
                    collected.add(ts)
        except Exception:  # noqa: BLE001 — doctor checks must not crash
            logger.debug("Skipping unreadable pipeline YAML: %s", yaml_path)
    return sorted(collected)


def discover_machine(_project_root: Path) -> WorkflowStateMachine | None:
    """Try to load a WorkflowStateMachine from the project configuration.

    Stage 1: returns ``None`` when no workflow state machine config is found.
    Future stages will load from ``.raise/workflow.yaml`` or the Jira adapter.
    """
    # Stage 1 stub — workflow.yaml config not yet specified.
    # Returns None → caller reports "no machine configured" and skips checks.
    return None


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
    ) -> None:
        """Initialise with an optional injected machine.

        When ``machine`` is ``None`` (the default, used by the entry-point
        registry), the check attempts to discover a machine from the project
        at evaluation time.
        """
        self._machine = machine

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

        phase_statuses = collect_target_statuses(root)
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
