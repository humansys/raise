"""Fleet MCP tools — fleet_dispatch, fleet_status, fleet_approve, fleet_signal.

S9506.1: Walking skeleton. The --fleet flag in session.py controls session
metadata only; the MCP server is a separate process that cannot receive runtime
imports, so registration is decided at import time.

RAISE-15618: registration is NO LONGER unconditional. Fleet is outside the
shipped 3.1 scope, and MCP has no "hidden" concept — an introspecting client
receives the whole tool list — so the only way to keep discovery honest is not
to register. These tools are gated behind @experimental (RAISE_EXPERIMENTAL=1),
which also keeps them stdio-only.

Out of scope: removing this module from the wheel. The code still ships and the
functions below remain importable and callable in-process; only MCP registration
is gated. Real removal is a product decision.
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
from datetime import timedelta
from pathlib import Path
from typing import Any

from raise_cli.dev.reaper import reap_idle
from raise_cli.fleet.dispatch_service import FleetDispatchService
from raise_cli.fleet.notifications import format_notification
from raise_cli.fleet.subagent_dispatcher import FleetState, SubagentDispatcher
from raise_cli.pipeline import _caller_context
from raise_cli.pipeline._mcp_decorators import experimental

logger = logging.getLogger(__name__)

_REAP_MAX_AGE = timedelta(minutes=30)

_PROJECT_KEY_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")

_TOKENS_PER_AGENT = 80_000
_COST_PER_TOKEN: dict[str, float] = {
    "claude-sonnet-4-6": 3e-6,
    "claude-haiku-4-5": 0.25e-6,
    "claude-opus-4-8": 15e-6,
}
# Normalize full model IDs → short names used by VALID_MODELS / skill frontmatter.
# fleet_dispatch accepts full IDs for cost estimation; SubagentDispatcher uses short names.
_FULL_TO_SHORT: dict[str, str] = {
    "claude-sonnet-4-6": "sonnet",
    "claude-haiku-4-5": "haiku",
    "claude-opus-4-8": "opus",
    "claude-fable-5": "fable",
}


def _get_adapter(adapter_name: str | None, cwd: str = "") -> Any:
    from raise_cli.adapters.resolve import resolve_pm_adapter

    project_root = Path(cwd).resolve() if cwd else None
    return resolve_pm_adapter(adapter_name, project_root=project_root)


def _format_signal(event: str, story_key: str, payload: dict[str, Any] | None) -> str:
    return format_notification(event=event, story_key=story_key, payload=payload)


@experimental
async def fleet_dispatch(
    project: str,
    model: str = "claude-sonnet-4-6",
    dry_run: bool = False,
    cwd: str = "",
) -> dict[str, Any]:
    """Resolve DispatchPlan for a project and return plan + cost estimate.

    Args:
        project: Jira project key (e.g., "RAISE").
        model: Default model for cost estimation (per-phase model chosen by coordinator).
        dry_run: If True, resolves plan without dispatching subagents (S5.2 gates).
        cwd: Working directory for adapter resolution (worktree-aware).
    """
    if not _PROJECT_KEY_RE.match(project):
        return {"status": "error", "reason": f"Invalid project key: {project!r}"}

    jql = (
        f'project = "{project}" AND issuetype = Story '
        f"AND status not in (Done, Cancelled) ORDER BY created ASC"
    )

    def _run() -> dict[str, Any]:
        from raise_cli.adapters.models.pm import IssueDetail

        try:
            pm = _get_adapter(None, cwd)
            raw = pm.search(jql)
            keys = [r.key for r in raw]
            issues: list[IssueDetail] = [pm.get_issue(k) for k in keys]
        except Exception as exc:  # noqa: BLE001
            return {"status": "error", "reason": str(exc)}

        service = FleetDispatchService()
        plan = service.dispatch(issues)

        # Cost covers all dispatchable + blocked stories (blocked dispatch later).
        n_immediate = len(plan.dispatchable)
        n_total = n_immediate + len(plan.blocked) + sum(len(g) for g in plan.serialized)
        cost_usd = n_total * _TOKENS_PER_AGENT * _COST_PER_TOKEN.get(model, 3e-6)

        result: dict[str, Any] = {
            "status": "ok",
            "plan": {
                "dispatchable": list(plan.dispatchable),
                "blocked": list(plan.blocked),
                "serialized": list(plan.serialized),
                "rejected": list(plan.rejected),
            },
            "cost_estimate": {
                "model": model,
                "n_immediate": n_immediate,
                "n_total": n_total,
                "tokens_per_agent": _TOKENS_PER_AGENT,
                "usd": round(cost_usd, 4),
                "note": "total fleet cost (immediate + blocked + serialized); blocked stories dispatched after dependencies clear",
            },
            "dry_run": dry_run,
        }

        # Live dispatch: seed FleetState and return DispatchInstructions (S5.2)
        if not dry_run:
            # Auto-stop (S10841.4): barre containers raise-runner huérfanos del ciclo
            # anterior antes de arrancar el nuevo. Best-effort: nunca aborta el dispatch.
            try:
                reaped = reap_idle(_REAP_MAX_AGE)
                if reaped:
                    logger.info(
                        "fleet_dispatch: reapeados %d containers idle", len(reaped)
                    )
            except Exception:  # noqa: BLE001 — la higiene no debe bloquear el dispatch
                logger.warning(
                    "fleet_dispatch: reap_idle falló — se continúa", exc_info=True
                )

            dispatcher = SubagentDispatcher()
            # Normalize full-id → short name; VALID_MODELS and skill frontmatter use short names
            dispatch_model = _FULL_TO_SHORT.get(model, model)
            instructions = dispatcher.dispatch(
                plan=plan, default_model=dispatch_model, cwd=cwd
            )
            result["dispatch"] = [
                {
                    "story_key": instr.story_key,
                    "phase": instr.phase,
                    "skill": instr.skill,
                    "model": instr.model,
                    "agent_prompt": instr.agent_prompt,
                }
                for instr in instructions
            ]

        return result

    return await asyncio.to_thread(_run)


@experimental
async def fleet_status(cwd: str = "") -> list[Any]:  # noqa: ARG001
    """Return status of active fleet subagents.

    Returns real FleetState snapshot (S5.2). Empty list when no active dispatch.

    Args:
        cwd: Working directory (reserved for future cross-process state).
    """
    snapshot = FleetState.snapshot()
    return [
        {
            "story_key": p.story_key,
            "phase": p.phase,
            "status": p.status,
            "task_id": p.task_id,
            "model": p.model,
        }
        for p in snapshot
    ]


@experimental
async def fleet_approve(
    story_key: str,
    cwd: str = "",
    size: str = "",
    gate_passed: bool = False,
) -> str:
    """Approve a HITL gate for a fleet-dispatched story.

    When size and gate_passed are provided and an auto-approve rule matches,
    the HITL gate is skipped automatically. Otherwise falls through to the
    existing manual approve() path (backward compatible).

    Args:
        story_key: Jira key of the story to approve (e.g., "RAISE-9506").
        cwd: Caller's absolute checkout path. Required in community stdio
            mode — omitting it returns a structured ``cwd_required`` error
            (S15457.2). Inert under HTTP transport / server credentials.
        size: Story size (e.g., "XS"). Empty string = no auto-approve attempt.
        gate_passed: True when all pipeline gates are green.
    """
    _root = _caller_context.require_caller_cwd(cwd, "fleet_approve")
    if isinstance(_root, dict):
        return json.dumps(_root)

    from raise_cli.fleet.auto_approve import evaluate_auto_approve
    from raise_cli.fleet.config import load as load_fleet_config

    if size and evaluate_auto_approve(load_fleet_config(str(_root)), size, gate_passed):
        return f"✅ {story_key} auto-approved (size={size}, gates=green) — continuing fleet run"

    def _run() -> str:
        dispatcher = SubagentDispatcher()
        next_instr = dispatcher.approve(
            story_key=story_key,
            default_model="sonnet",  # short name — VALID_MODELS contract
            cwd=cwd,
        )
        if next_instr is None:
            return f"No active fleet run — {story_key} cannot be approved (start fleet with fleet_dispatch first)"
        return f"✅ {story_key} approved — next: {next_instr.agent_prompt}"

    return await asyncio.to_thread(_run)


def _get_dispatcher() -> SubagentDispatcher:
    """Return a SubagentDispatcher instance (singleton access pattern).

    Single helper avoids repeating the import + instantiation across tools.
    """
    return SubagentDispatcher()


@experimental
async def fleet_signal(
    story_key: str,
    event: str,
    payload: dict[str, Any] | None = None,
    task_id: str | None = None,
    cwd: str = "",
) -> str:
    """Emit a fleet signal from a subagent phase to the coordinator chat.

    On event=phase_complete, records the completed phase in FleetState and
    returns the next DispatchInstruction appended to the formatted signal.

    Args:
        story_key: Jira key of the emitting story (e.g., "RAISE-9506").
        event: Signal event type: phase_complete | blocked | hitl | complete.
        payload: Optional event details (e.g., {"reason": "merge conflict"}).
        task_id: Optional CC task id from the subagent (best-effort).
        cwd: Working directory for phase resolution.
    """

    def _run() -> str:
        base = _format_signal(event, story_key, payload)

        if event == "phase_complete":
            dispatcher = _get_dispatcher()
            next_instr = dispatcher.record_phase_complete(
                story_key=story_key,
                task_id=task_id,
                default_model="sonnet",  # short name — VALID_MODELS contract
                cwd=cwd,
            )
            if next_instr is not None:
                return f"{base} → next: {next_instr.agent_prompt}"

        return base

    return await asyncio.to_thread(_run)
