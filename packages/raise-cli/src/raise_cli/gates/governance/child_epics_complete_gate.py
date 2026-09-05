"""ChildEpicsCompleteGate — all child Epics must be terminal before Concluded.

S14559.1 (RAISE-14588), design Decision D2: the Initiative Flow's
Concluded phase must mechanically block while any child Epic is still
non-terminal. This is a deterministic point-bound governance gate firing
at ``before:initiative:concluded``.

Data source deliberately diverges from the epic pipeline's
``epic_story_iteration`` (which parses a local ``scope.md`` stories
table): Initiatives are Jira-native portfolio entities with no local
child-Epic table, so the authoritative source here is the PM adapter's
``search()`` (JQL-shaped query for Jira). Terminal-status detection reuses
``terminal_status.is_terminal_status`` (T1), passing each search result's
``status_category`` so Spanish terminal names do not depend on English
tokens (RAISE-16985). Issue-key resolution reuses
``_initiative_context.resolve_initiative_key`` — shared with
``StrategicFitGate`` (T2) rather than cloned (design DR2 mitigation).

Opt-in: skips silently unless ``project.portfolio_gates.enabled`` is True
in ``.raise/manifest.yaml`` (mirrors ``pm_gates``).

Architecture: RAISE-14588, epic RAISE-14559 (Initiative Flow).
"""

from __future__ import annotations

import os
from typing import ClassVar

from raise_cli.gates.governance._initiative_context import resolve_initiative_key
from raise_cli.gates.governance._portfolio_config import portfolio_gates_enabled
from raise_cli.gates.models import GateContext, GateResult
from raise_cli.pipeline.terminal_status import is_terminal_status

_SKIP_ENV = "RAISE_CHILD_EPICS_SKIP"


class ChildEpicsCompleteGate:
    """Deterministic point-bound gate: all child Epics must be terminal.

    Fail-open: portfolio_gates not enabled, no initiative branch context,
    or an adapter error/no adapter configured — mirrors the fail-open style
    of ``_check_issue_type_guard``/``_check_maintenance_lock``.
    Escape hatch: ``RAISE_CHILD_EPICS_SKIP=<reason>``.
    """

    gate_id: ClassVar[str] = "gate-child-epics-complete"
    description: ClassVar[str] = "All child Epics must be terminal before Concluded"
    workflow_point: ClassVar[str] = "before:initiative:concluded"

    def evaluate(self, context: GateContext) -> GateResult:
        """Block Concluded while any child Epic under the Initiative is open."""
        if not portfolio_gates_enabled(context.working_dir):
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="portfolio_gates not configured — skipping",
            )

        skip_reason = os.environ.get(_SKIP_ENV, "").strip()
        if skip_reason:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message=f"{self.gate_id} skipped: {skip_reason}",
            )

        issue_key = resolve_initiative_key(context.working_dir)
        if not issue_key:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="No initiative branch context detected — child-epics-complete check not applicable",
            )

        from raise_cli.adapters.resolve import resolve_pm_adapter

        try:
            adapter = resolve_pm_adapter(None, context.working_dir)
            # T7 manual verification against real Jira (RAISE-14588) caught that
            # `issue_type` is not a valid JQL field — real Jira uses `issuetype`
            # (no underscore). The design/plan's own worked example used the
            # invalid field name; a fake-adapter unit test alone could not have
            # caught this since it never validates JQL syntax against a real
            # Jira instance. `issue_type = Epic AND parent = X` silently
            # returns zero results in production instead of erroring.
            # fetch_all=True: this is a completeness check (ALL child Epics must be
            # terminal), not a preview — the adapter's default limit=50 would let an
            # Initiative with >50 child Epics conclude while an untruncated Epic past
            # position 50 is still open (quality-review finding, S14559.1).
            epics = adapter.search(
                f"issuetype = Epic AND parent = {issue_key}", fetch_all=True
            )
        except Exception as exc:  # noqa: BLE001
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message=(
                    f"Could not query child Epics for {issue_key}: {exc}. "
                    f"Fail-open — escape hatch: {_SKIP_ENV}=<reason>"
                ),
            )

        non_terminal = [
            epic
            for epic in epics
            if not is_terminal_status(epic.status, status_category=epic.status_category)
        ]
        if non_terminal:
            blocker = non_terminal[0]
            return GateResult(
                passed=False,
                gate_id=self.gate_id,
                message=(
                    f"Initiative {issue_key} cannot conclude: child Epic "
                    f"{blocker.key} is '{blocker.status}' (not terminal). "
                    "Complete it, or demote it to Idea, before concluding "
                    "the Initiative."
                ),
                details=tuple(f"{epic.key}: {epic.status}" for epic in non_terminal)
                + (f"Escape: {_SKIP_ENV}=<reason>",),
            )

        return GateResult(
            passed=True,
            gate_id=self.gate_id,
            message=f"Initiative {issue_key}: all {len(epics)} child Epic(s) terminal",
        )
