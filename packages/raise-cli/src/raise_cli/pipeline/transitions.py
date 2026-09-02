"""Advisory backlog transitions for pipeline phases (Stage 1, RAISE-15030).

STAGE-1 CONTRACT (Persistence Option A):
Every TransitionRecord produced by this module is a best-effort trace of a
transition ATTEMPT observed at call time. It is persisted with ordinary run
state and carries no crash-durability guarantee. The system of record for
issue status history is the adapter (e.g. Jira changelog). Absence of a
record means "unobserved", never "did not happen".
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

from raise_cli.adapters.protocols import ProjectManagementAdapter
from raise_core.workflow.models import TransitionRecord
from raise_core.workflow.state_machine import WorkflowStateMachine

_log = logging.getLogger(__name__)

_TRANSITION_TIMEOUT_S: float = 30.0

type TransitionDepsProvider = Callable[
    [Path],
    tuple[ProjectManagementAdapter | None, WorkflowStateMachine | None],
]


def empty_state_machine() -> WorkflowStateMachine:
    """Machine with no states — legality checks bypassed (fail-open).

    Meaning: workflow config is ABSENT (unconfigured is a supported state).
    """
    return WorkflowStateMachine(states={}, transitions={}, unmanaged_states=frozenset())


def resolve_transition_deps(
    project_root: Path,
) -> tuple[ProjectManagementAdapter | None, WorkflowStateMachine | None]:
    """Resolve adapter + machine from an explicit absolute root. NEVER raises.

    The ONE place ambient config/adapter resolution lives for transitions.
    Engine and MCP both call this; no per-callsite copies of the lazy pattern.

    Adapter: resolve_pm_adapter(None, project_root=root) — raises
      AdapterResolutionError (or anything) -> None + logger.warning.

    Machine: load_workflow_config(root / ".raise" / "backlog_config.yaml")
      Asymmetric failure modes:
      - file or `pipeline_workflow` section ABSENT -> empty_state_machine(),
        logger.debug (expected, supported state; fail-open)
      - file PRESENT but yaml.safe_load or model_validate raises ->
        logger.warning("workflow-config-invalid") -> machine=None
        (fail-CLOSED for Jira writes; config present = intent declared)
      - machine built with unmanaged_states slugs not in states ->
        logger.warning listing orphan slugs; machine still returned
    """
    adapter: ProjectManagementAdapter | None = None
    machine: WorkflowStateMachine | None = None

    # Resolve adapter
    try:
        from raise_cli.adapters.resolve import resolve_pm_adapter

        adapter = resolve_pm_adapter(None, project_root=project_root)
    except Exception as exc:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        _log.warning("pm-adapter-unavailable: %s (%s)", type(exc).__name__, exc)
        adapter = None

    # Resolve machine
    config_path = project_root / ".raise" / "backlog_config.yaml"
    if not config_path.exists():
        _log.debug("workflow-config-absent: %s — fail-open", config_path)
        machine = empty_state_machine()
    else:
        try:
            from raise_cli.adapters.backlog_config import load_workflow_config

            workflow_cfg = load_workflow_config(config_path)
            machine = workflow_cfg.to_state_machine()

            # Warn on orphan unmanaged_states slugs (pm.py:644-648 does no validation)
            orphans = machine.unmanaged_states - set(machine.states)
            if orphans:
                _log.warning(
                    "workflow-config-warning: unmanaged_states contains slugs "
                    "not in states (will never match): %s — check .raise/backlog_config.yaml",
                    sorted(orphans),
                )
        except Exception as exc:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
            _log.warning(
                "workflow-config-invalid: %s (%s: %s)",
                config_path,
                type(exc).__name__,
                exc,
            )
            machine = None

    return adapter, machine


def apply_phase_transition(  # noqa: C901
    *,
    phase_id: str,
    target_status: str | None,
    issue_key: str | None,
    adapter: ProjectManagementAdapter | None,
    machine: WorkflowStateMachine | None,
) -> TransitionRecord:
    """Attempt a workflow-driven backlog transition. NEVER raises.

    Performs NO file/config I/O; adapter and machine are inputs.
    Returns a TransitionRecord for every invocation.
    machine=None means "config present but invalid" — no adapter write permitted.
    Logs the resulting record at INFO before returning.
    """
    now = datetime.now(UTC)

    def _record(
        outcome: str,
        *,
        from_status: str = "",
        message: str = "",
        verified: bool = False,
        remote_synced: bool | None = None,
    ) -> TransitionRecord:
        rec = TransitionRecord(
            phase_id=phase_id,
            issue_key=issue_key or "",
            from_status=from_status,
            to_slug=target_status or "",
            outcome=outcome,  # type: ignore[arg-type]
            verified=verified,
            message=message,
            timestamp=now,
            remote_synced=remote_synced,
        )
        _log.info(
            "backlog-transition phase=%s issue=%s outcome=%s target=%s msg=%s",
            phase_id,
            issue_key,
            outcome,
            target_status,
            message,
        )
        return rec

    # Row 1 — no target_status
    if not target_status:
        return _record("skipped", message="no-target-status")

    # Row 2 — no issue_key
    if not issue_key:
        return _record("skipped", message="no-issue-key")

    # Row 3 — machine=None means config present but invalid; fail-closed
    if machine is None:
        return _record("skipped", message="workflow-config-invalid")

    # Row 4 — no adapter
    if adapter is None:
        return _record("skipped", message="no-adapter")

    # Row 5 — pre-read current status
    try:
        issue = adapter.get_issue(issue_key)
        current_raw = issue.status or ""
    except Exception as exc:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        return _record(
            "failed",
            from_status="unknown",
            message=f"status-read-failed:{type(exc).__name__}: {exc}",
        )

    # Machine is empty (no states) — resolve returns None for everything;
    # use raw normalized equality for noop check, then skip legality rows.
    machine_empty = not machine.states

    if machine_empty:
        current_resolved = None
        target_resolved = None
        current_norm = current_raw.lower().replace(" ", "-")
        target_norm = target_status.lower().replace(" ", "-")
        already_at = current_norm == target_norm
    else:
        current_resolved = machine.resolve(current_raw)
        target_resolved = machine.resolve(target_status)
        already_at = (
            current_resolved is not None
            and target_resolved is not None
            and current_resolved == target_resolved
        )

    # Row 6 — noop: already at target
    if already_at:
        slug = current_resolved or current_raw.lower().replace(" ", "-")
        return _record(
            "noop", from_status=slug, verified=True, message="already-at-target"
        )

    from_slug = current_resolved or current_raw.lower().replace(" ", "-")
    unresolved_suffix = (
        "" if (machine_empty or current_resolved is not None) else ",from-unresolved"
    )

    if not machine_empty:
        # Row 7 — current state in unmanaged_states
        if current_resolved and current_resolved in machine.unmanaged_states:
            return _record(
                "skipped",
                from_status=current_resolved,
                message=f"unmanaged-state:{current_resolved}",
            )

        # Row 8 — target not in machine; edge wizard emits diagnostic when
        # partial matches exist so operators can fix pipeline YAML / backlog_config.yaml
        if target_resolved is None:
            candidates = machine.suggest_candidates(target_status)
            if candidates:
                _log.warning(
                    "edge-wizard: target_status %r not in machine; close candidates: %s — "
                    "fix target_status in pipeline YAML or add state to .raise/backlog_config.yaml",
                    target_status,
                    candidates,
                )
            return _record(
                "illegal",
                from_status=from_slug,
                message=f"target-not-in-machine:{target_status}",
            )

        # Row 9 — undeclared / illegal move (includes undeclared backward)
        if current_resolved is not None and not machine.is_legal(
            current_resolved, target_resolved
        ):
            return _record(
                "illegal",
                from_status=from_slug,
                message=f"transition-not-declared:{current_resolved}->{target_resolved}",
            )

        # Declared backward move telemetry (free field for Stage-2 drift design)
        # target_resolved is narrowed to str by the row-8 guard above
        if current_resolved is not None:
            declared_states = list(machine.states.keys())
            cur_idx = (
                declared_states.index(current_resolved)
                if current_resolved in declared_states
                else -1
            )
            tgt_idx = (
                declared_states.index(target_resolved)
                if target_resolved in declared_states
                else -1
            )
            if cur_idx >= 0 and tgt_idx >= 0 and tgt_idx < cur_idx:
                _log.info(
                    "backward-move-applied: phase=%s issue=%s %s->%s",
                    phase_id,
                    issue_key,
                    current_resolved,
                    target_resolved,
                )

    # Attempt the transition (rows 10-11)
    # String sent to adapter: display name when machine resolves, else raw target_status
    adapter_target = target_status
    if not machine_empty and target_resolved is not None:
        spec = machine.states.get(target_resolved)
        if spec is not None:
            adapter_target = spec.name

    try:
        ref = adapter.transition_issue(issue_key, adapter_target)
    except Exception as exc:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        # Recovery read — concurrent winner may have landed first
        try:
            recovery = adapter.get_issue(issue_key)
            recovery_resolved = (
                machine.resolve(recovery.status) if not machine_empty else None
            )
            recovery_match = (
                (recovery_resolved == target_resolved)
                if not machine_empty
                else (
                    recovery.status.lower().replace(" ", "-")
                    == target_status.lower().replace(" ", "-")
                )
            )
            if recovery_match:
                return _record(
                    "noop",
                    from_status=from_slug,
                    verified=True,
                    message="concurrent-target-observed",
                )
        except Exception as recovery_exc:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
            _log.debug("recovery-read-failed: %s", recovery_exc)
        return _record(
            "failed",
            from_status=from_slug,
            message=f"transition-failed:{type(exc).__name__}: {exc}{unresolved_suffix}",
        )

    # Row 11 — applied: transition_issue returned an IssueRef
    rs = ref.remote_synced

    if rs is False:
        # Adapter reports write queued locally, not yet on remote — skip read-back
        reason = (
            ref.metadata.get("remote_sync_reason", "pending-replay")
            if ref.metadata
            else "pending-replay"
        )
        return _record(
            "applied",
            from_status=from_slug,
            verified=False,
            remote_synced=False,
            message=f"remote-queued:{reason}{unresolved_suffix}",
        )

    # Read-back to verify
    try:
        readback = adapter.get_issue(issue_key)
        rb_resolved = machine.resolve(readback.status) if not machine_empty else None
        rb_match = (
            (rb_resolved == target_resolved)
            if not machine_empty
            else (
                readback.status.lower().replace(" ", "-")
                == target_status.lower().replace(" ", "-")
            )
        )
        if rb_match:
            return _record(
                "applied",
                from_status=from_slug,
                verified=True,
                remote_synced=rs,
            )
        return _record(
            "applied",
            from_status=from_slug,
            verified=False,
            remote_synced=rs,
            message=f"read-back-mismatch: got {readback.status}{unresolved_suffix}",
        )
    except Exception as exc:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        return _record(
            "applied",
            from_status=from_slug,
            verified=False,
            remote_synced=rs,
            message=f"read-back-failed:{type(exc).__name__}{unresolved_suffix}",
        )


async def apply_phase_transition_async(
    *,
    phase_id: str,
    target_status: str | None,
    issue_key: str | None,
    adapter: ProjectManagementAdapter | None,
    machine: WorkflowStateMachine | None,
) -> TransitionRecord:
    """asyncio.wait_for(asyncio.to_thread(apply_phase_transition, ...), 30s).

    NEVER raises. On timeout -> failed/timeout-unknown-final-state.
    On any unexpected escape -> failed/internal (logger.debug exc_info=True).
    """
    now = datetime.now(UTC)

    def _failed(message: str) -> TransitionRecord:
        return TransitionRecord(
            phase_id=phase_id,
            issue_key=issue_key or "",
            from_status="",
            to_slug=target_status or "",
            outcome="failed",
            verified=False,
            message=message,
            timestamp=now,
        )

    try:
        return await asyncio.wait_for(
            asyncio.to_thread(
                apply_phase_transition,
                phase_id=phase_id,
                target_status=target_status,
                issue_key=issue_key,
                adapter=adapter,
                machine=machine,
            ),
            timeout=_TRANSITION_TIMEOUT_S,
        )
    except TimeoutError:
        _log.warning(
            "backlog-transition timeout phase=%s issue=%s target=%s "
            "(orphaned write may still land — check issue history)",
            phase_id,
            issue_key,
            target_status,
        )
        return _failed("timeout-unknown-final-state")
    except Exception as exc:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        _log.debug(
            "backlog-transition internal error phase=%s issue=%s",
            phase_id,
            issue_key,
            exc_info=True,
        )
        return _failed(f"internal: {exc}")
