"""Fleet lease heartbeat integration (RAISE-15770, epic design D6).

Thin glue between the fleet dispatch/signal path and `storage/leases.py`'s
`SqliteLeaseStore` — mirrors the acquire-on-launch / renew-on-activity shape
`cockpit/session_lease.py` already uses for `rai session start/close`, keyed
here to a fleet run (`run_id`) instead of a CC session id.

Reuses `SqliteLeaseStore` / `pid_alive` / `list_live_or_reap` exactly as they
are — no new table, no new liveness mechanism (ADR-094, F5). The only new
surface is this integration layer: acquire a lease when a fleet subagent is
dispatched, renew it on phase transitions, and a scriptable probe
(`probe_fleet_health`) an operator can run to distinguish a worktree whose
fleet agent is live-and-heartbeating from one whose PID died (reaped, "hung"
in the WHAT section's vocabulary) from one that was never leased at all.

Every function here is best-effort and never raises: heartbeat state is
observability, not a dispatch gate. A lease lookup/acquire failure (missing
registration, lost acquire race, sqlite contention) is logged and reported
as `False` — it must never abort a fleet dispatch or signal call.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path

from raise_cli.storage.leases import Lease, LeaseHeldError, SqliteLeaseStore
from raise_cli.storage.worktrees import SqliteWorktreeStore, WorktreeNotFoundError

logger = logging.getLogger(__name__)


def acquire_fleet_lease(
    worktree_store: SqliteWorktreeStore, worktree_path: str, session_id: str
) -> bool:
    """Acquire a `worktree_leases` row for a fleet run at dispatch/launch time.

    `session_id` is the fleet run's `run_id` (stable for the story's whole
    pipeline lifetime, per `StoryProgress.run_id`) — NOT a per-heartbeat
    value, so `heartbeat_fleet_lease` calls later in the same run can renew
    the same row. `pid` is always the calling process's own pid: fleet
    subagents in the current (in-band) dispatch model are Task calls inside
    the director's own process (ADR §F12), so the director's pid is what
    `pid_alive` must observe to detect "the agent driving this worktree is
    gone".

    Returns False (never raises) when: `worktree_path` is empty, the path
    isn't a registered worktree, or another live session already holds the
    lease (race with the pre-dispatch `workspace_integrity.lease_acquirable`
    check — logged, not fatal).
    """
    if not worktree_path:
        return False
    try:
        wt = worktree_store.get_by_path(worktree_path)
    except WorktreeNotFoundError:
        logger.warning(
            "fleet lease: %s is not a registered worktree — skipping acquire",
            worktree_path,
        )
        return False
    except Exception:  # noqa: BLE001 — best-effort, never blocks dispatch
        # RAISE-15770 quality-review C1: this call site sits inside
        # _bind_and_dispatch_story's try block, AFTER dispatch_one already
        # succeeded — an uncaught exception here (e.g. sqlite3.OperationalError
        # on a WAL lock) would be caught one frame up and cancel an already
        # -successful dispatch, exactly inverting the "never turns a
        # successful dispatch into a failure" contract this module promises.
        logger.warning(
            "fleet lease: worktree lookup failed for %s — skipping acquire",
            worktree_path,
            exc_info=True,
        )
        return False
    try:
        SqliteLeaseStore(Path(worktree_path)).acquire(
            wt.worktree_id, session_id=session_id, pid=os.getpid()
        )
        return True
    except LeaseHeldError as exc:
        logger.warning("fleet lease: acquire lost race for %s: %s", worktree_path, exc)
        return False
    except Exception:  # noqa: BLE001 — best-effort, never blocks dispatch
        logger.warning(
            "fleet lease: acquire failed for %s", worktree_path, exc_info=True
        )
        return False


def heartbeat_fleet_lease(
    worktree_store: SqliteWorktreeStore, worktree_path: str, session_id: str
) -> bool:
    """Renew `heartbeat_at` for an already-held fleet lease at a phase transition.

    `session_id` must match the `run_id` passed to the launch-time
    `acquire_fleet_lease` call for the same story — mirrors
    `SqliteLeaseStore.renew`'s "no-op unless caller holds it" contract.

    Returns False (never raises) when `worktree_path` is empty, unregistered,
    or the lease isn't currently held by `session_id` — a heartbeat miss is
    never allowed to fail the caller's fleet_signal handling.
    """
    if not worktree_path:
        return False
    try:
        wt = worktree_store.get_by_path(worktree_path)
    except WorktreeNotFoundError:
        logger.warning(
            "fleet heartbeat: %s is not a registered worktree — skipping renew",
            worktree_path,
        )
        return False
    try:
        return SqliteLeaseStore(Path(worktree_path)).renew(
            wt.worktree_id, session_id=session_id
        )
    except Exception:  # noqa: BLE001 — best-effort, never blocks fleet_signal
        logger.warning(
            "fleet heartbeat: renew failed for %s", worktree_path, exc_info=True
        )
        return False


def release_fleet_lease(
    worktree_store: SqliteWorktreeStore, worktree_path: str, session_id: str
) -> bool:
    """Release a held fleet lease when a story reaches its terminal phase.

    `session_id` must match the `run_id` passed to the launch-time
    `acquire_fleet_lease` call for the same story — `SqliteLeaseStore.release`
    is scoped by (worktree_id, project_id, session_id) and is a no-op unless
    `session_id` matches the current holder, so releasing under the wrong
    run_id never frees someone else's lease.

    Called from `fleet_signal`'s "advanced" handler (RAISE-15955) when
    `record_advanced()` reports the story has reached its terminal phase —
    the sole point in the fleet code path that authoritatively detects "this
    story is done" (`fleet_signal(event="complete")` is a separate,
    unauthenticated, format-only notification with no FleetState/run_id of
    its own and no production caller — it is not a release site).

    Returns False (never raises) when `worktree_path` is empty, unregistered,
    or the release call itself fails — a release miss is never allowed to
    fail the caller's fleet_signal handling (mirrors `heartbeat_fleet_lease`).
    Returns True once the release call has been issued, whether or not a row
    was actually deleted (idempotent: releasing an already-free lease, or one
    held by another session, both return True having done nothing harmful).
    """
    if not worktree_path:
        return False
    try:
        wt = worktree_store.get_by_path(worktree_path)
    except WorktreeNotFoundError:
        logger.warning(
            "fleet lease: %s is not a registered worktree — skipping release",
            worktree_path,
        )
        return False
    try:
        SqliteLeaseStore(Path(worktree_path)).release(
            wt.worktree_id, session_id=session_id
        )
        return True
    except Exception:  # noqa: BLE001 — best-effort, never blocks fleet_signal
        logger.warning(
            "fleet lease: release failed for %s", worktree_path, exc_info=True
        )
        return False


@dataclass
class WorktreeHealth:
    """One row of the `probe_fleet_health` scriptable probe.

    Attributes:
        worktree_id: Registry id (matches `worktree_leases.worktree_id`).
        path: Registered filesystem path.
        stories: Jira keys currently bound to this worktree.
        status: "live" (lease held, pid alive) | "dead" (lease existed, pid
            was dead — reaped by this call) | "no_lease" (never leased, or
            already released).
        lease: The live `Lease` row when status == "live", else None.
    """

    worktree_id: str
    path: str
    stories: list[str]
    status: str
    lease: Lease | None


def probe_fleet_health(project: Path) -> list[WorktreeHealth]:
    """Scriptable probe (D6): live vs. dead vs. no_lease for every open worktree.

    Wraps `SqliteLeaseStore.list_live_or_reap()` — which reaps dead-PID
    leases in place and returns only live survivors — with a before/after
    diff so callers can distinguish "never leased" from "was leased, PID
    died, just reaped here" (`list_live_or_reap()` alone drops dead rows
    silently). This is what lets an operator (or automation) tell "fleet
    agent is working" (status == "live") from "fleet agent is hung" (status
    == "dead", per the WHAT section's vocabulary: hung == dead-PID-reaped)
    without inspecting git state.
    """
    wt_store = SqliteWorktreeStore(project)
    lease_store = SqliteLeaseStore(project)
    worktrees = wt_store.list_worktrees()

    had_lease = {
        wt.worktree_id: lease_store.get(wt.worktree_id) is not None for wt in worktrees
    }
    live = lease_store.list_live_or_reap()

    results: list[WorktreeHealth] = []
    for wt in worktrees:
        lease = live.get(wt.worktree_id)
        if lease is not None:
            status = "live"
        elif had_lease[wt.worktree_id]:
            status = "dead"
        else:
            status = "no_lease"
        results.append(
            WorktreeHealth(
                worktree_id=wt.worktree_id,
                path=wt.path,
                stories=wt.stories,
                status=status,
                lease=lease,
            )
        )
    return results
