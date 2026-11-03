"""Built-in GateBridgeHook — bridges gate system into before: events.

Subscribes to ``before:`` events and delegates to the unified
gate-execution seam (``gates/execution.py``, RAISE-13749). Returns
``abort`` if any gate fails, preventing the guarded operation from
proceeding.

This is the bridge between the independent gate and hook systems (PAT-E-454).
Gates remain standalone (AD-5) — the bridge is the only coupling point.

Architecture: ADR-039 §5 (Built-in hooks), S248.6
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import ClassVar

from raise_cli.gates.execution import run_gates_for_point
from raise_cli.hooks.events import HookEvent, HookResult

logger = logging.getLogger(__name__)


class GateBridgeHook:
    """Bridges WorkflowGates into the hook lifecycle.

    Subscribes to ``before:`` events and delegates to
    ``run_gates_for_point`` for discovery, context construction, and
    exception isolation — returns ``abort`` if any gate fails. Priority
    100 ensures gates run before other hooks.

    Registered via ``rai.hooks`` entry point in pyproject.toml.
    """

    events: ClassVar[list[str]] = [
        "before:release:publish",
        "before:session:close",
        "before:bug:close",
        "before:story:close",
        "before:initiative:validated",
        "before:initiative:concluded",
    ]
    priority: ClassVar[int] = 100

    def handle(self, event: HookEvent) -> HookResult:
        """Run matching gates and abort if any fail."""
        workflow_point = event.event_name

        # RAISE-11004 / feedback_inprocess_mcp_tool_staleness: today's two
        # emit sites are fresh CLI processes where Path.cwd() is already
        # correct. If an in-process emitter is ever wired here (e.g.
        # raise_session_close_full), it MUST populate event.working_dir —
        # otherwise this silently resolves against the MCP server's
        # pinned main-worktree CWD instead of the caller's checkout.
        event_working_dir: str = getattr(event, "working_dir", "")
        working_dir = Path(event_working_dir) if event_working_dir else Path.cwd()

        # RAISE-12207: an in-process emitter (the pipeline engine) supplies the
        # agent session id it resolved from the run, so session-scoped gates
        # (gate-ar-bugfix) resolve the marker under the caller's session rather
        # than the MCP server's absent/foreign env.
        event_session_id: str | None = getattr(event, "session_id", None)
        event_issue_id: str | None = getattr(event, "issue_id", None) or None

        report = run_gates_for_point(
            workflow_point,
            working_dir,
            session_id=event_session_id,
            issue_id=event_issue_id,
        )

        if report.failures:
            summary = "; ".join(f"{f.gate_id}: {f.message}" for f in report.failures)
            logger.debug(
                "GateBridgeHook: gates failed for '%s': %s", workflow_point, summary
            )
            return HookResult(status="abort", message=f"Gates failed: {summary}")

        return HookResult(status="ok")
