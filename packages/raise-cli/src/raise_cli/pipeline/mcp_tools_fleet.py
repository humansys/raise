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

from raise_cli.dev.provisioner import DevStackProvisioner, DevStackProvisioningError
from raise_cli.dev.reaper import reap_dev_stacks, reap_idle
from raise_cli.fleet.binding import PipelineBinder
from raise_cli.fleet.dispatch_service import FleetDispatchService
from raise_cli.fleet.heartbeat import (
    acquire_fleet_lease,
    heartbeat_fleet_lease,
    release_fleet_lease,
)
from raise_cli.fleet.notifications import format_notification
from raise_cli.fleet.provisioning import DefaultProvisioningVerifier
from raise_cli.fleet.subagent_dispatcher import (
    FleetState,
    StoryProgress,
    SubagentDispatcher,
)
from raise_cli.pipeline import _caller_context
from raise_cli.pipeline._mcp_decorators import experimental
from raise_cli.pipeline.mcp_tools_pipeline import pipeline_cancel
from raise_cli.storage.worktrees import SqliteWorktreeStore

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


def _bind_and_dispatch_story(
    binder: PipelineBinder,
    dispatcher: SubagentDispatcher,
    story_key: str,
    dispatch_model: str,
    cwd: str,
    worktree_path: str = "",
    worktree_store: SqliteWorktreeStore | None = None,
) -> dict[str, Any]:
    """Bind + dispatch_one for one story (D8), with D8.a's failure contract.

    Called only AFTER story resolution (D2.a) and workspace_integrity
    verification (D2/D10) have already passed for `worktree_path` — this
    function does no verification itself, it just binds + builds.

    Every `run_id` minted by `bind()` must end up dispatched-and-owned,
    cancelled, or surfaced in `failed_bindings` — never ownerless. Returns
    exactly one of:

        {"ok": True, "entry": {...}, "run_id": ..., "advance_token": ...}
        {"ok": False, "reason": "bind_failed: ..."}
        {"ok": False, "reason": "dispatch_failed_cancelled: ..."}
        {"ok": False, "reason": "dispatch_failed_orphan: ...",
         "run_id": ..., "advance_token": ...}

    RAISE-15770 (D6): on success, best-effort acquires a `worktree_leases`
    row keyed by `binding.run_id` — the fleet healthcheck heartbeat. Never
    raises and never turns a successful dispatch into a failure; a lease
    race or lookup miss is observability, not a dispatch gate.
    """
    binding = None
    try:
        binding = binder.bind(story_key)
        instr = dispatcher.dispatch_one(
            story_key,
            default_model=dispatch_model,
            cwd=cwd,
            run_id=binding.run_id,
            worktree_path=worktree_path,
        )
        if worktree_store is not None:
            acquire_fleet_lease(worktree_store, worktree_path, binding.run_id)
        return {
            "ok": True,
            "entry": {
                "story_key": instr.story_key,
                "phase": instr.phase,
                "skill": instr.skill,
                "model": instr.model,
                "agent_prompt": instr.agent_prompt,
                "worktree_path": instr.worktree_path,
            },
            "run_id": binding.run_id,
            "advance_token": binding.advance_token,
        }
    except Exception as exc:  # noqa: BLE001 — per-story isolation, D8.a
        if binding is None:
            # Nothing minted — safe, nothing to dispose of.
            logger.warning("fleet_dispatch: bind failed for %s: %s", story_key, exc)
            return {"ok": False, "reason": f"bind_failed: {exc}"}

        # A run EXISTS. It must end up either cancelled or owned — never
        # neither (D8.a invariant). Either way dispatch_one() may already
        # have seeded FleetState for story_key before raising (R1) — that
        # entry must not survive a story that isn't actually dispatched.
        try:
            asyncio.run(pipeline_cancel(binding.run_id, cwd=cwd))
            logger.warning(
                "fleet_dispatch: %s failed after bind — cancelled run %s: %s",
                story_key,
                binding.run_id,
                exc,
            )
            FleetState.delete(story_key)
            return {"ok": False, "reason": f"dispatch_failed_cancelled: {exc}"}
        except Exception as cancel_exc:  # noqa: BLE001
            # Cancel also failed — hand the token back so a human can drive
            # or cancel it (last resort).
            logger.error(
                "fleet_dispatch: %s failed after bind AND cancel failed — "
                "run %s orphaned: %s / %s",
                story_key,
                binding.run_id,
                exc,
                cancel_exc,
            )
            FleetState.delete(story_key)
            return {
                "ok": False,
                "reason": (
                    f"dispatch_failed_orphan: {exc}; cancel also failed: {cancel_exc}"
                ),
                "run_id": binding.run_id,
                "advance_token": binding.advance_token,
            }


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

    # An empty/unvalidated cwd here means `verify_director_session("")`
    # later resolves `.claude/settings.json` relative to the MCP SERVER
    # process's cwd, not the director's — fail-open or spuriously-refuse
    # depending on where the server happens to sit. Same guard
    # `fleet_approve` already applies for the same reason.
    _root = _caller_context.require_caller_cwd(cwd, "fleet_dispatch")
    if isinstance(_root, dict):
        return _root

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
                # D2.b: (work_id, reason) pairs for `rejected` — e.g. terminal-
                # mission rejections minted in dispatch_service.py carry
                # "terminal_status" here. Live-path verification rejections
                # (worktree_unresolved, workspace_integrity, ...) are surfaced
                # separately via the `rejected` dict in the live-dispatch
                # result — this is the dry-run/terminal-mission channel.
                "rejection_reasons": list(plan.rejection_reasons),
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
            result.update(_run_live_dispatch(plan, model, cwd))

        return result

    return await asyncio.to_thread(_run)


_BINDINGS_WARNING = (
    "Secrets authorizing pipeline_advance for these runs only. Keep "
    "them in the fleet director; do NOT include any advance_token "
    "in a subagent brief or Agent() prompt."
)


def _worktree_register_hint(story_key: str) -> str:
    """Actionable remediation for `worktree_unresolved` (D2.a.1).

    Mirrors the real `rai worktree register` CLI surface
    (cli/commands/worktree.py) — all named flags, not positionals.
    """
    return (
        f"run: rai worktree register --name <name> --path <path> "
        f"--branch <branch> --merge-target <merge_target> "
        f"--stories {story_key} --update"
    )


def _resolve_and_verify_story(
    worktree_store: SqliteWorktreeStore,
    verifier: DefaultProvisioningVerifier,
    story_key: str,
) -> tuple[str, str]:
    """D2.a resolve + D10 pt2 workspace_integrity verify for one story.

    Extracted from `_run_live_dispatch`'s loop to keep it under the McCabe
    complexity gate. Returns `(worktree_path, "")` on success, or
    `("", reason)` on rejection — never both non-empty.

    Fail closed on both edges of D2.a: 0 matches -> worktree_unresolved
    (with an actionable remediation command), 2+ matches -> worktree_ambiguous
    (never disambiguated by recency, never falls back to cwd).
    """
    matches = worktree_store.find_by_story(story_key)
    if not matches:
        return "", (
            f"worktree_unresolved: no open worktree registers {story_key} — "
            f"{_worktree_register_hint(story_key)}"
        )
    if len(matches) > 1:
        return "", (
            f"worktree_ambiguous: {len(matches)} open worktrees claim "
            f"{story_key}: {', '.join(matches)}"
        )
    worktree_path = matches[0]

    # D10 pt2: workspace_integrity is the BLOCKING per-story gate.
    # session_governance is also computed by verify() and present in the
    # report, but is ADVISORY here (D10 pt3) — the in-band subagent
    # inherits the director's session (checked once, pre-loop — see
    # `_run_live_dispatch`), not this worktree's settings.json, so
    # blocking on it would be governance theater. verify() never mutates
    # state (ADR §1, pure read).
    report = verifier.verify(worktree_path, story_key)
    if not report.workspace_integrity_satisfied:
        unsatisfied = "; ".join(
            c.detail for c in report.workspace_integrity if not c.satisfied
        )
        return "", f"workspace_integrity: {unsatisfied}"

    return worktree_path, ""


def _resolve_and_verify_story_isolated(
    worktree_store: SqliteWorktreeStore,
    verifier: DefaultProvisioningVerifier,
    story_key: str,
) -> tuple[str, str]:
    """Per-story exception isolation (D8.a) around `_resolve_and_verify_story`.

    Nothing is minted by resolve/verify (`bind()` hasn't run yet for this
    story), so there is no run to cancel if it raises — just turn the
    exception into a rejection. Without this guard an exception here (e.g.
    a sqlite3 WAL lock timeout, not caught by `_load_registered_worktree`'s
    narrower ``(WorktreeNotFoundError, OSError)`` handler) would propagate
    out of `_run()` and abort the whole loop, silently orphaning any runs
    already minted for prior stories. Extracted out of `_run_live_dispatch`
    to keep it under the McCabe complexity gate.
    """
    try:
        return _resolve_and_verify_story(worktree_store, verifier, story_key)
    except Exception as exc:  # noqa: BLE001 — per-story isolation, D8.a
        logger.warning(
            "fleet_dispatch: resolve/verify raised for %s — rejecting, "
            "no run minted: %s",
            story_key,
            exc,
        )
        return "", f"resolve_failed: {exc}"


def _ensure_dev_stack_isolated(
    provisioner: DevStackProvisioner,
    story_key: str,
    worktree_path: str,
) -> str:
    """Per-story exception isolation (D8.a) around DevStackProvisioner.ensure_up.

    Returns ``""`` on success (including ``skipped``), or a rejection reason
    prefixed with ``dev_stack:`` on failure. Nothing is minted at this point
    (bind hasn't run), so there is no run to cancel -- just reject.
    """
    try:
        report = provisioner.ensure_up(Path(worktree_path))
        logger.info(
            "fleet_dispatch: dev_stack %s for %s at %s — %s",
            report.status,
            story_key,
            worktree_path,
            report.detail,
        )
        return ""
    except DevStackProvisioningError as exc:
        logger.warning(
            "fleet_dispatch: dev_stack provisioning failed for %s — rejecting: %s",
            story_key,
            exc,
        )
        return f"dev_stack: {exc}"
    except Exception as exc:  # noqa: BLE001 — per-story isolation, D8.a
        logger.warning(
            "fleet_dispatch: dev_stack unexpected error for %s — rejecting: %s",
            story_key,
            exc,
        )
        return f"dev_stack: {exc}"


def _reap_stale_containers() -> None:
    """Best-effort reap of orphan containers before dispatch.

    Auto-stop (S10841.4 + S16534.2): reap both idle raise-runner containers
    and orphan compose dev-stack containers from the previous cycle. Never
    aborts the dispatch — all exceptions are caught and logged.
    """
    try:
        reaped = reap_idle(_REAP_MAX_AGE)
        if reaped:
            logger.info("fleet_dispatch: reapeados %d containers idle", len(reaped))
    except Exception:  # noqa: BLE001 — la higiene no debe bloquear el dispatch
        logger.warning("fleet_dispatch: reap_idle falló — se continúa", exc_info=True)

    try:
        reaped_dev = reap_dev_stacks()
        if reaped_dev:
            logger.info(
                "fleet_dispatch: reaped %d orphan dev-stack containers",
                len(reaped_dev),
            )
    except Exception:  # noqa: BLE001 — best-effort, never blocks dispatch
        logger.warning(
            "fleet_dispatch: reap_dev_stacks failed — continuing", exc_info=True
        )


def _run_live_dispatch(plan: Any, model: str, cwd: str) -> dict[str, Any]:
    """Run the D8 per-story resolve→verify→bind→dispatch loop.

    Extracted from fleet_dispatch's live-dispatch branch to keep both
    functions under the McCabe complexity gate.
    """
    verifier = DefaultProvisioningVerifier()

    # D10.1: session_governance checked ONCE against the fleet DIRECTOR's
    # own cwd, before any story is touched. Fleet subagents are Task calls
    # INSIDE the director's session (F12) — an ungoverned director session
    # means every subagent inherits it, so an ungoverned director refuses
    # the WHOLE batch here: zero pipeline_start calls, no per-story
    # verification even attempted.
    director_report = verifier.verify_director_session(cwd)
    if not director_report.session_governance_satisfied:
        unsatisfied = "; ".join(
            c.detail for c in director_report.session_governance if not c.satisfied
        )
        reason = f"director_ungoverned: {unsatisfied}"
        logger.warning("fleet_dispatch: refusing whole batch — %s", reason)
        return {
            "dispatch": [],
            "bindings": {},
            "bindings_warning": _BINDINGS_WARNING,
            "run_ids": {},
            "rejected": dict.fromkeys(plan.dispatchable, reason),
        }

    _reap_stale_containers()

    provisioner = DevStackProvisioner()
    dispatcher = SubagentDispatcher()
    # Normalize full-id → short name; VALID_MODELS and skill frontmatter use short names
    dispatch_model = _FULL_TO_SHORT.get(model, model)
    binder = PipelineBinder(cwd=cwd)
    worktree_store = SqliteWorktreeStore(Path(cwd))

    # Clear stale state from any prior dispatch run before seeding fresh
    # state. Re-dispatching without clearing would silently clobber in-flight
    # progress and leave orphan records from stories not in the new plan.
    # Binding now happens per-story at this MCP-tool boundary (D1) rather
    # than inside SubagentDispatcher.dispatch(), so the clear moves here.
    FleetState.clear()

    dispatch_entries: list[dict[str, Any]] = []
    bindings: dict[str, str] = {}
    run_ids: dict[str, str] = {}
    failed_bindings: dict[str, str] = {}
    rejected: dict[str, str] = {}

    # D8: per-story resolve -> verify -> bind -> dispatch_one, wrapped per
    # story (D8.a) so one story's failure never orphans a minted run or
    # aborts the batch — every run_id ends dispatched-and-owned (bindings),
    # cancelled, or surfaced in failed_bindings. Never none of them.
    for story_key in plan.dispatchable:
        worktree_path, rejection = _resolve_and_verify_story_isolated(
            worktree_store, verifier, story_key
        )
        if rejection:
            rejected[story_key] = rejection
            continue

        # S16534.2: ensure dev stack is up before bind
        dev_rejection = _ensure_dev_stack_isolated(
            provisioner, story_key, worktree_path
        )
        if dev_rejection:
            rejected[story_key] = dev_rejection
            continue

        outcome = _bind_and_dispatch_story(
            binder,
            dispatcher,
            story_key,
            dispatch_model,
            cwd,
            worktree_path,
            worktree_store=worktree_store,
        )
        if outcome["ok"]:
            dispatch_entries.append(outcome["entry"])
            bindings[outcome["run_id"]] = outcome["advance_token"]
            run_ids[story_key] = outcome["run_id"]
            continue

        rejected[story_key] = outcome["reason"]
        if "advance_token" in outcome:
            failed_bindings[outcome["run_id"]] = outcome["advance_token"]

    # D9: tokens live ONLY in this separate top-level field, never
    # interleaved with dispatch entries a director copies into an
    # Agent()/Task prompt — mirrors pipeline_start's
    # advance_token/advance_token_warning pair (mcp_tools_pipeline.py).
    live: dict[str, Any] = {
        "dispatch": dispatch_entries,
        "bindings": bindings,
        "bindings_warning": _BINDINGS_WARNING,
        "run_ids": run_ids,
    }
    if failed_bindings:
        live["failed_bindings"] = failed_bindings
    if rejected:
        live["rejected"] = rejected
    return live


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


def _update_lease_on_signal(
    cwd: str,
    story_key: str,
    progress: StoryProgress | None,
    result: dict[str, Any],
) -> None:
    """RAISE-15770/RAISE-15955: keep the fleet lease in sync with signal results.

    Called from both `phase_complete` and `advanced` handlers (scope.md:
    "Heartbeat is called at phase transitions"). On any non-terminal result
    this renews `heartbeat_at` — keeps `probe_fleet_health` from having to
    distinguish "genuinely hung" from "just hasn't advanced in a while".

    When `record_advanced()` reports the story has reached its terminal
    phase (`result["status"] == "complete"`) — the only point in the fleet
    code path that authoritatively detects "this story is done" — this
    releases the lease instead of renewing it (RAISE-15955). Without this,
    the terminal `advanced` call was the LAST heartbeat: it renewed the
    lease for another full TTL on the exact call that ends the story,
    leaking it until the director process itself dies.
    (`fleet_signal(event="complete")` is a separate, unauthenticated,
    format-only notification path with no FleetState/run_id of its own and
    no production caller — it is not a release site.)

    No-op (never raises into `fleet_signal`) when: the story was never seen
    by `FleetState` (`progress is None` — the `unknown_story` fail-closed
    path), it has no resolved `worktree_path` (seeded outside the
    bind→dispatch_one flow, e.g. dry-run/tests — no lease was ever
    acquired for it), or `result` carries no `run_id` to act under.
    """
    if progress is None or not progress.worktree_path:
        return
    run_id = result.get("run_id") or progress.run_id
    if not run_id:
        return
    try:
        worktree_store = SqliteWorktreeStore(Path(cwd) if cwd else Path.cwd())
        if result.get("status") == "complete":
            release_fleet_lease(worktree_store, progress.worktree_path, run_id)
        else:
            heartbeat_fleet_lease(worktree_store, progress.worktree_path, run_id)
    except Exception:  # noqa: BLE001 — best-effort, never fails fleet_signal
        logger.warning(
            "fleet_signal: lease update failed for %s (%s)",
            story_key,
            progress.worktree_path,
            exc_info=True,
        )


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
    """Emit a fleet signal — routes phase_complete/advanced through the D3 split.

    Per the amended ADR (§2), the DIRECTOR advances the pipeline run, never
    the subagent. `phase_complete` and `advanced` are therefore two distinct
    handlers, each returning a JSON-encoded object (D3.a structured return
    shape — matches the `json.dumps(...)` convention `fleet_approve` already
    uses):

    - event="phase_complete": bookkeeping only. Sets FleetState status to
      "awaiting_advance" and returns a directive — NEVER a next-phase
      instruction (that was F2's duplicate-dispatch defect). The subagent
      cannot act on the directive itself (no advance_token); it only
      reaches the director because the subagent's Task ends and this
      return value surfaces in the director's context.
    - event="advanced": the director calls this AFTER it has itself called
      pipeline_advance. Verifies the run store's live phase actually moved
      (compare_and_advance CAS, D3.a/D3.b) before returning an instruction;
      idempotent no-op ("not_advanced") otherwise.

    Other events (blocked, hitl, complete, ...) are unchanged: a
    human-readable emoji-formatted string via `_format_signal`.

    Args:
        story_key: Jira key of the emitting story (e.g., "RAISE-9506").
        event: Signal event type: phase_complete | advanced | blocked | hitl | complete.
        payload: Optional event details (e.g., {"reason": "merge conflict"}).
        task_id: Optional CC task id from the subagent (best-effort).
        cwd: Working directory for phase resolution.
    """

    def _run() -> str:
        if event == "phase_complete":
            dispatcher = _get_dispatcher()
            progress = FleetState.get(story_key)
            result = dispatcher.record_phase_complete(
                story_key=story_key,
                task_id=task_id,
            )
            _update_lease_on_signal(cwd, story_key, progress, result)
            return json.dumps(result)

        if event == "advanced":
            dispatcher = _get_dispatcher()
            progress = FleetState.get(story_key)
            result = dispatcher.record_advanced(
                story_key=story_key,
                default_model="sonnet",  # short name — VALID_MODELS contract
                cwd=cwd,
            )
            _update_lease_on_signal(cwd, story_key, progress, result)
            return json.dumps(result)

        return _format_signal(event, story_key, payload)

    return await asyncio.to_thread(_run)
