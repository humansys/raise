"""FleetDispatchService — bridges I/O to DagDependencyResolver.

Responsibilities:
1. Accept a list of IssueDetail objects (already fetched by caller)
2. Filter out terminal-mission stories (Done/Cancelled) → plan.rejected
3. Build DispatchCandidate for non-terminal stories from IssueDetail.links
4. Invoke DagDependencyResolver.resolve(candidates)
5. Merge terminal story keys into plan.rejected
6. Log 'mission terminal: {key}' for each rejection
"""

from __future__ import annotations

import logging

from raise_cli.adapters.models.pm import IssueDetail
from raise_core.fleet.contracts import DispatchCandidate, DispatchPlan
from raise_core.fleet.resolver import DagDependencyResolver

logger = logging.getLogger(__name__)

TERMINAL_STATUSES: frozenset[str] = frozenset({"Done", "Cancelled"})

_BLOCKED_BY = "is blocked by"


class FleetDispatchService:
    """Dispatch service: filters terminal missions, delegates to DagDependencyResolver."""

    def dispatch(self, issues: list[IssueDetail]) -> DispatchPlan:
        """Partition issues into dispatchable / blocked / rejected.

        Terminal issues (Done/Cancelled status) go to rejected with a log entry.
        Remaining issues are converted to DispatchCandidate and resolved.
        """
        terminal_keys: list[str] = []
        candidates: list[DispatchCandidate] = []

        for issue in issues:
            if issue.status in TERMINAL_STATUSES:
                logger.info("mission terminal: %s", issue.key)
                terminal_keys.append(issue.key)
            else:
                blocked_by = tuple(
                    link.target for link in issue.links if link.link_type == _BLOCKED_BY
                )
                candidates.append(
                    DispatchCandidate(
                        work_id=issue.key,
                        blocked_by=blocked_by,
                        declared_scope=(),
                    )
                )

        resolver = DagDependencyResolver()
        base_plan = resolver.resolve(candidates)

        return DispatchPlan(
            dispatchable=base_plan.dispatchable,
            blocked=base_plan.blocked,
            serialized=base_plan.serialized,
            rejected=tuple(terminal_keys),
            # D2.b: uniform reason channel across every rejection source —
            # terminal-mission stories carry "terminal_status" so a
            # DispatchPlan.rejection_reasons consumer never has to special-
            # case "no reason recorded" for this rejection path.
            rejection_reasons=tuple((key, "terminal_status") for key in terminal_keys),
        )
