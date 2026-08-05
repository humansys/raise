"""Composite session-open service — S7884.2 (E7884 K1, ADR-093/ADR-024).

Ports the deterministic checks that lived as bash prose in the
rai-session-start skill (working-tree hygiene, base-branch drift, DB
health) into tested code, so bookend skills become thin presenters.

Check contract (jidoka): every check returns a ``CheckResult`` with
``status`` ok|warn|blocked plus structured ``data``. ``blocked`` means a
human decision is required — the service never auto-resolves it.
"""

from __future__ import annotations

import logging
import sqlite3
import subprocess
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from importlib.metadata import version
from pathlib import Path
from typing import Any, Literal

import httpx
from pydantic import BaseModel

from raise_cli.compat import IS_FROZEN
from raise_cli.self_update.manifest import MANIFEST_URL, fetch_manifest, is_newer

# Imported at module level to allow monkeypatching in tests.
from raise_cli.worktree.prune import evaluate_candidate, has_active_lease

_UPDATE_CHECK_TIMEOUT_S = 3.0

_log = logging.getLogger(__name__)

_STATUS_RANK = {"ok": 0, "warn": 1, "blocked": 2}
# Public alias for sibling composite services (story bookends — S7884.3).
STATUS_RANK = _STATUS_RANK

CheckStatus = Literal["ok", "warn", "blocked"]

# Options presented to the human when orphan staged changes are found.
# Mirrors the Step 0 gate of the legacy skill prose 1:1.
HYGIENE_OPTIONS = ["discard", "stash", "keep"]

_GIT_TIMEOUT_S = 10


class CheckResult(BaseModel):
    """Outcome of one deterministic session-open check."""

    name: str
    status: CheckStatus
    data: dict[str, Any] = {}


def run_git(repo: Path, *args: str) -> subprocess.CompletedProcess[str] | None:
    """Run git in *repo*; None on OS error/timeout (callers treat as blocked)."""
    try:
        return subprocess.run(  # noqa: S603
            ["git", *args],  # noqa: S607
            cwd=repo,
            capture_output=True,
            text=True,
            timeout=_GIT_TIMEOUT_S,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None


def commits_behind(repo: Path, target_ref: str) -> int | None:
    """Count commits in *target_ref* not yet reachable from HEAD.

    Returns ``None`` when the ref does not exist, git is unavailable, or the
    output cannot be parsed — this is INDETERMINATE, not "no drift" (RAISE-14279).
    A missing/unfetched ref is legitimate in fresh clones and offline work, so
    this fails loud (a visible local warning) rather than fail-closed — callers
    must treat ``None`` as "cannot evaluate" and proceed without blocking;
    ``0`` means the ref *was* resolved and there is genuinely no drift.
    """
    proc = run_git(repo, "rev-list", "--count", f"HEAD..{target_ref}")
    if proc is None or proc.returncode != 0:
        _log.warning(
            "commits_behind: could not resolve '%s' in %s (git unavailable or "
            "ref does not exist) — drift is indeterminate, not zero",
            target_ref,
            repo,
        )
        return None
    try:
        return int(proc.stdout.strip())
    except ValueError:
        _log.warning(
            "commits_behind: unparsable git output for '%s' in %s — "
            "drift is indeterminate, not zero",
            target_ref,
            repo,
        )
        return None


def check_hygiene(repo: Path) -> CheckResult:
    """Working-tree hygiene: staged orphans block, unstaged warn.

    Status mapping (parity with legacy Step 0 table):
    clean -> ok · untracked-only -> ok · staged -> blocked · unstaged -> warn.
    """
    proc = run_git(repo, "status", "--porcelain")
    if proc is None or proc.returncode != 0:
        return CheckResult(
            name="hygiene", status="warn", data={"reason": "git-unavailable"}
        )

    staged: list[str] = []
    unstaged: list[str] = []
    untracked: list[str] = []
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        if line.startswith("??"):
            untracked.append(line[3:])
            continue
        index_flag, tree_flag = line[0], line[1]
        path = line[3:]
        if index_flag not in (" ", "?"):
            staged.append(f"{index_flag}  {path}")
        if tree_flag not in (" ", "?"):
            unstaged.append(f"{tree_flag}  {path}")

    data: dict[str, Any] = {
        "staged": staged,
        "unstaged": unstaged,
        "untracked": untracked,
    }
    if staged:
        data["options"] = HYGIENE_OPTIONS
        return CheckResult(name="hygiene", status="blocked", data=data)
    if unstaged:
        return CheckResult(name="hygiene", status="warn", data=data)
    return CheckResult(name="hygiene", status="ok", data=data)


def check_base_drift(repo: Path, merge_target: str | None) -> CheckResult:
    """Verify HEAD descends from the registered merge target.

    Non-blocking by design (legacy Step 0.1): drift warns, never stops.
    Missing target/ref skips silently — absence of registration is not an
    error condition.
    """
    if not merge_target:
        return CheckResult(name="drift", status="ok", data={"skipped": True})

    # Prefer the remote-tracking ref (legacy behaviour); fall back to local.
    target_ref = None
    for candidate in (f"origin/{merge_target}", merge_target):
        proc = run_git(repo, "rev-parse", "--verify", "--quiet", candidate)
        if proc is not None and proc.returncode == 0:
            target_ref = candidate
            break
    if target_ref is None:
        return CheckResult(
            name="drift",
            status="ok",
            data={"skipped": True, "merge_target": merge_target},
        )

    proc = run_git(repo, "merge-base", "--is-ancestor", target_ref, "HEAD")
    if proc is not None and proc.returncode == 0:
        return CheckResult(
            name="drift", status="ok", data={"merge_target": merge_target}
        )
    return CheckResult(
        name="drift",
        status="warn",
        data={
            "merge_target": merge_target,
            "suggestion": f"git rebase {target_ref}",
        },
    )


def resolve_mission(project: Path, cwd: Path) -> CheckResult:
    """Return a fixed ok result — missions dissolved in S7 (ADR-130)."""
    _ = (project, cwd)
    return CheckResult(
        name="mission",
        status="ok",
        data={"needs_selection": False},
    )


def get_worktree_merge_target(project: Path, cwd: Path) -> str | None:
    """Merge target registered for *cwd*'s worktree, or None."""
    from raise_cli.storage.worktrees import SqliteWorktreeStore, WorktreeNotFoundError

    try:
        return SqliteWorktreeStore(project).get_by_path(str(cwd)).merge_target
    except WorktreeNotFoundError:
        return None


def _default_mcp_servers(project: Path) -> list[str]:
    from raise_cli.mcp.registry import discover_mcp_servers

    try:
        return sorted(discover_mcp_servers(project / ".raise" / "mcp"))
    except Exception:  # noqa: BLE001 — MCP discovery is advisory
        return []


def summarize_mcp(
    project: Path,
    servers: list[str] | None = None,
    checker: Callable[[str], bool] | None = None,
) -> CheckResult:
    """Registered MCP servers + best-effort health (never raises).

    The composite open runs INSIDE the rai-workspace server — checking
    self synchronously risks deadlock, so callers should exclude it or
    pass a checker that short-circuits it.
    """
    names = servers if servers is not None else _default_mcp_servers(project)
    if not names:
        return CheckResult(name="mcp", status="ok", data={"total": 0, "healthy": 0})

    down: list[str] = []
    if checker is not None:
        for name in names:
            ok = False
            try:
                ok = checker(name)
            except Exception:  # noqa: BLE001 — health is advisory
                ok = False
            if not ok:
                down.append(name)
    healthy = len(names) - len(down)
    data: dict[str, Any] = {"total": len(names), "healthy": healthy}
    if down:
        data["down"] = down
    status: CheckStatus = "warn" if down else "ok"
    return CheckResult(name="mcp", status=status, data=data)


def check_update_available(
    *,
    is_frozen: bool = IS_FROZEN,
    manifest_url: str = MANIFEST_URL,
    current_version: str | None = None,
    timeout_s: float = _UPDATE_CHECK_TIMEOUT_S,
    transport: httpx.BaseTransport | None = None,
) -> CheckResult:
    """Detect (never install) a newer published `rai` release (RAISE-15715).

    Pure detection, same contract as every other check in this module:
    report, don't act — never returns ``blocked``. Non-frozen installs,
    unreachable network, and up-to-date installs all collapse to ``ok``;
    a genuinely newer release is the only ``warn``. The actual download
    + install only happens after an explicit human "yes", elsewhere: the
    CLI (`rai session open`, real tty) or the agent asking in chat and
    running `rai self-update` (raise_session_open has no tty — see the
    rai-session-start SKILL.md).
    """
    if not is_frozen:
        return CheckResult(
            name="update", status="ok", data={"skipped": True, "reason": "not-frozen"}
        )

    local = current_version if current_version is not None else version("raise-cli")

    try:
        manifest = fetch_manifest(
            manifest_url, transport=transport, timeout_s=timeout_s
        )
    except Exception:  # noqa: BLE001 — network/parse failures are advisory, never block
        return CheckResult(
            name="update", status="ok", data={"skipped": True, "reason": "fetch-failed"}
        )

    if not is_newer(remote=manifest.version, local=local):
        return CheckResult(name="update", status="ok", data={"current": local})

    return CheckResult(
        name="update",
        status="warn",
        data={"current": local, "latest": manifest.version, "url": manifest_url},
    )


def _worktree_last_active(conn: sqlite3.Connection, wt: Any) -> datetime | None:
    """Return the most recent activity datetime for a worktree.

    Priority: last_session_id → sessions.started; fallback: created_at.
    Returns None when age cannot be determined (skip the worktree).
    """
    from raise_cli.storage.worktrees import Worktree as _Worktree

    wt_obj: _Worktree = wt
    if wt_obj.last_session_id:
        row = conn.execute(
            "SELECT started FROM sessions WHERE session_id = ?",
            (wt_obj.last_session_id,),
        ).fetchone()
        if row is not None:
            try:
                dt = datetime.fromisoformat(row[0])
                return dt if dt.tzinfo is not None else dt.replace(tzinfo=UTC)
            except (ValueError, TypeError):
                pass

    # Fallback: created_at
    try:
        dt = datetime.fromisoformat(wt_obj.created_at)
        return dt if dt.tzinfo is not None else dt.replace(tzinfo=UTC)
    except (ValueError, AttributeError):
        return None


def check_stale_worktrees(
    project: Path,
    cwd: Path,
    *,
    stale_after_hours: float = 48.0,
) -> CheckResult:
    """Detect, report, and auto-reap stale worktrees during session open.

    A worktree is stale when:
    - its last session (or creation) is older than *stale_after_hours*, AND
    - it has no live session lease.

    Safe stale candidates (per ``evaluate_candidate``) are auto-removed.
    Unsafe ones are reported as ``warn`` so the developer can act.

    Best-effort by contract — callers MUST wrap in ``try/except Exception``.
    RAISE-15000 / Closes RAISE-14995.
    """
    from raise_cli.storage.connection import get_project_db
    from raise_cli.storage.worktrees import SqliteWorktreeStore

    stale_threshold = timedelta(hours=stale_after_hours)
    now = datetime.now(UTC)

    store = SqliteWorktreeStore(project)
    conn = get_project_db(project)
    worktrees = store.list_worktrees()  # open only

    stale_ids: list[str] = []
    reaped_ids: list[str] = []

    for wt in worktrees:
        # Skip worktrees with a live session lease — someone is actively using them.
        if has_active_lease(wt.worktree_id, project):
            continue

        # Determine last activity time for staleness threshold.
        last_active = _worktree_last_active(conn, wt)
        if last_active is None:
            continue  # Cannot determine age — skip conservatively.

        if now - last_active < stale_threshold:
            continue  # Fresh — not stale.

        stale_ids.append(wt.worktree_id)
        _log.info(
            "Detected stale worktree '%s' (last active: %s)",
            wt.worktree_id,
            last_active.isoformat(),
        )

        decision = evaluate_candidate(wt, repo=project, current_path=cwd)
        if not decision.safe:
            _log.warning(
                "Protected stale worktree '%s' (cannot auto-reap): %s",
                wt.worktree_id,
                "; ".join(decision.reasons),
            )
            continue

        # Auto-reap: git worktree remove → git branch -d → mark closed.
        # Order matches worktree prune CLI (RAISE-11104 AR Q4).
        remove = subprocess.run(  # noqa: S603
            ["git", "-C", str(project), "worktree", "remove", wt.path],  # noqa: S607
            capture_output=True,
            text=True,
            check=False,
        )
        if remove.returncode != 0:
            _log.warning(
                "Failed to auto-remove stale worktree '%s': %s",
                wt.worktree_id,
                remove.stderr.strip(),
            )
            continue

        # Best-effort branch deletion — non-fatal if it fails.
        subprocess.run(  # noqa: S603
            ["git", "-C", str(project), "branch", "-d", wt.branch],  # noqa: S607
            capture_output=True,
            text=True,
            check=False,
        )
        store.complete(wt.worktree_id)
        reaped_ids.append(wt.worktree_id)
        _log.info("Auto-reaped stale worktree '%s'", wt.worktree_id)

    # warn if any stale worktrees remain unreaped.
    protected = [wid for wid in stale_ids if wid not in reaped_ids]
    status: CheckStatus = "warn" if protected else "ok"
    return CheckResult(
        name="worktrees",
        status=status,
        data={"stale": stale_ids, "auto_reaped": reaped_ids},
    )


class OpenReport(BaseModel):
    """Composite result of a session open: all checks plus the bundle."""

    status: CheckStatus
    hygiene: CheckResult
    drift: CheckResult
    db: CheckResult
    mission: CheckResult
    mcp: CheckResult
    worktrees: CheckResult
    update: CheckResult = CheckResult(
        name="update", status="ok", data={"skipped": True}
    )
    bundle: str = ""
    orientation_ledger: str = ""


def build_open_report(
    project_path: Path,
    cwd: Path,
    *,
    bundle: str = "",
    mcp_servers: list[str] | None = None,
    mcp_checker: Callable[[str], bool] | None = None,
) -> OpenReport:
    """Run every deterministic open check and aggregate the worst status."""
    from raise_cli.storage.connection import get_project_db_path

    hygiene = check_hygiene(cwd)
    drift = check_base_drift(cwd, get_worktree_merge_target(project_path, cwd))
    db = check_db_health(get_project_db_path(project_path))
    mission = resolve_mission(project_path, cwd)
    mcp = summarize_mcp(project_path, servers=mcp_servers, checker=mcp_checker)

    try:
        worktrees = check_stale_worktrees(project_path, cwd)
    except Exception as exc:  # noqa: BLE001 — stale check is best-effort
        _log.warning("Stale worktree check failed (non-fatal): %s", exc)
        worktrees = CheckResult(name="worktrees", status="ok", data={"error": str(exc)})

    update = check_update_available()

    checks = (hygiene, drift, db, mission, mcp, worktrees, update)
    worst = max(checks, key=lambda c: _STATUS_RANK[c.status]).status
    return OpenReport(
        status=worst,
        hygiene=hygiene,
        drift=drift,
        db=db,
        mission=mission,
        mcp=mcp,
        worktrees=worktrees,
        update=update,
        bundle=bundle,
    )


_BUNDLE_TIMEOUT_S = 60


def run_start_for_bundle(project: Path) -> str:
    """Run the existing start flow for the orientation bundle.

    Single reuse point — session counter, state and sync live in the CLI
    command, so the composite open must not reimplement them.
    """
    try:
        proc = subprocess.run(  # noqa: S603
            ["rai", "session", "start", "--project", str(project), "--context"],  # noqa: S607
            capture_output=True,
            text=True,
            timeout=_BUNDLE_TIMEOUT_S,
            check=False,
            cwd=project,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return proc.stdout if proc.returncode == 0 else ""


def should_run_start_for_bundle(report: OpenReport, include_bundle: bool) -> bool:
    """Return True when session-open may run the mutating start flow."""
    if not include_bundle:
        return False
    if report.status == "blocked":
        return False
    return not bool(report.mission.data.get("needs_selection"))


def surface_ledger_if_bundle_skipped(
    project_path: Path, report: OpenReport, include_bundle: bool
) -> OpenReport:
    """Populate the read-only orientation ledger when the bundle didn't run.

    RAISE-13382 — `should_run_start_for_bundle()` legitimately gates the
    *mutating* start subprocess (session record, counter, sync) behind
    mission-selection readiness and hygiene status; that gate must keep
    protecting the mutation (commit 3c5b6df00). But the orientation ledger
    (RAISE-13341 T3) is a *different* concern: read-only, in-process,
    fail-open, and keyed by agent_session_id — never by mission. It must
    surface for continuity regardless of `needs_selection` or blocked
    hygiene.

    Only exception: an explicit `--no-bundle`/`include_bundle=False` request
    is a deliberate "checks only" ask, and is honored as-is.

    When the bundle DID run, it already renders the ledger inline (via
    `assemble_orientation` -> `format_orientation_ledger`) — skip here to
    avoid duplicate rendering.
    """
    if not include_bundle or report.bundle:
        return report

    from raise_cli.session.bundle import format_orientation_ledger

    ledger_block = format_orientation_ledger(project_path)
    if not ledger_block:
        return report
    return report.model_copy(update={"orientation_ledger": ledger_block})


def check_db_health(db_path: Path) -> CheckResult:
    """Project DB sanity: phantom/corrupt warn, missing is a fresh project."""
    if not db_path.exists():
        return CheckResult(name="db", status="ok", data={"present": False})
    if db_path.stat().st_size == 0:
        return CheckResult(
            name="db", status="warn", data={"present": True, "reason": "phantom"}
        )
    try:
        conn = sqlite3.connect(db_path)
        try:
            version = conn.execute("PRAGMA user_version").fetchone()[0]
            tables = conn.execute(
                "SELECT count(*) FROM sqlite_master WHERE type='table'"
            ).fetchone()[0]
        finally:
            conn.close()
    except sqlite3.Error as exc:
        return CheckResult(
            name="db",
            status="warn",
            data={"present": True, "reason": "unreadable", "error": str(exc)},
        )
    return CheckResult(
        name="db",
        status="ok",
        data={"present": True, "schema_version": version, "tables": tables},
    )
