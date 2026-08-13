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
import os
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
from raise_cli.context.freshness import evaluate_graph_freshness

# Imported at module level to allow monkeypatching in tests.
from raise_cli.legacy.scanner import scan_project
from raise_cli.legacy.snooze import compute_set_hash, read_acknowledged_project_hash
from raise_cli.self_update.manifest import MANIFEST_URL, fetch_manifest, is_newer
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


def run_git(
    repo: Path, *args: str, timeout: float = _GIT_TIMEOUT_S
) -> subprocess.CompletedProcess[str] | None:
    """Run git in *repo*; None on OS error/timeout (callers treat as blocked).

    *timeout* defaults to ``_GIT_TIMEOUT_S`` (10s), calibrated for the cheap
    local operations every other caller performs. Callers that hit the
    network (e.g. ``sync_dev_branch``'s ``git fetch``) must pass an explicit
    longer value — 10s is not enough for a real fetch (RAISE-15825 C3).
    """
    try:
        return subprocess.run(  # noqa: S603
            ["git", *args],  # noqa: S607
            cwd=repo,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            env={**os.environ, "LC_ALL": "C", "LANGUAGE": "en"},
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


def check_base_drift(
    repo: Path, merge_target: str | None, *, in_worktree: bool = False
) -> CheckResult:
    """Verify HEAD descends from the registered merge target.

    Non-blocking by design (legacy Step 0.1): drift warns, never stops — and
    that never changes here, regardless of ``in_worktree``. This function
    only reports; it has never touched HEAD. ``in_worktree`` is threaded
    through into ``data`` purely so callers one layer up (the
    rai-session-start skill, historically) can tell whether a `warn` was
    observed inside a worktree — where Regla 2 (RAISE-15825) forbids any
    automated fetch+merge reaction to it — or outside one, where an
    autonomous Ri-mode sync reaction is still legitimate (afb15fd8a). Missing
    target/ref skips silently — absence of registration is not an error
    condition.
    """
    if not merge_target:
        return CheckResult(
            name="drift",
            status="ok",
            data={"skipped": True, "in_worktree": in_worktree},
        )

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
            data={
                "skipped": True,
                "merge_target": merge_target,
                "in_worktree": in_worktree,
            },
        )

    proc = run_git(repo, "merge-base", "--is-ancestor", target_ref, "HEAD")
    if proc is not None and proc.returncode == 0:
        return CheckResult(
            name="drift",
            status="ok",
            data={"merge_target": merge_target, "in_worktree": in_worktree},
        )
    return CheckResult(
        name="drift",
        status="warn",
        data={
            "merge_target": merge_target,
            "suggestion": f"git rebase {target_ref}",
            "in_worktree": in_worktree,
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


def is_in_worktree(project: Path, cwd: Path) -> bool:
    """True when *cwd* sits inside ANY worktree — registered or not (RAISE-15825).

    Two-tier check, mirroring ``story.open_service.detect_worktree()``'s own
    logic (RAISE-10283/RAISE-15825 Regla 2 — deliberately duplicated rather
    than imported: ``story.open_service`` already imports FROM this module,
    so the reverse import would be circular):

    1. Registered binding in the mission/worktree store wins.
    2. Physical fallback: a linked worktree's git-dir
       (``.git/worktrees/<name>``) differs from the shared common dir
       (``.git``); the main checkout's are identical. Catches worktrees
       created outside the RaiSE lifecycle (plain ``git worktree add``).

    Callers use this to distinguish "inside a worktree" from "the main
    checkout" — Regla 2 forbids any automated fetch+merge reaction to a
    drift warning inside a worktree, but the main-checkout case (a long
    autonomous Ri-mode session, afb15fd8a) is still a legitimate one.
    """
    from raise_cli.storage.worktrees import SqliteWorktreeStore, WorktreeNotFoundError

    try:
        SqliteWorktreeStore(project).get_by_path(str(cwd))
        return True
    except WorktreeNotFoundError:
        pass

    gd = run_git(cwd, "rev-parse", "--absolute-git-dir")
    cd = run_git(cwd, "rev-parse", "--git-common-dir")
    if gd is None or cd is None or gd.returncode != 0 or cd.returncode != 0:
        return False
    git_dir = Path(gd.stdout.strip())
    common = Path(cd.stdout.strip())
    if not common.is_absolute():
        common = cwd / common
    try:
        return git_dir.resolve() != common.resolve()
    except OSError:
        return False


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


_FIX_HINT_GRAPH_BUILD = "rai graph build"


def check_graph_freshness(repo: Path) -> CheckResult:
    """Advisory graph staleness check (ADR-085, epic RAISE-15983 D3-D5).

    Both tiers map to status "warn" — NEVER "blocked" (D5 constraint; AC9).
    Evaluated against *repo* (the checkout, i.e. ``cwd``), not the registered
    project path — graph partitions are checkout-scoped (ADR-145 D7, SD3).
    Fail-open by contract: callers MUST wrap this in ``try/except``, exactly
    like ``check_stale_worktrees``.
    """
    freshness = evaluate_graph_freshness(repo)

    if freshness.tier == "ok":
        return CheckResult(name="graph", status="ok", data={"tier": "ok"})

    if freshness.tier == "never_built":
        return CheckResult(
            name="graph",
            status="warn",
            data={
                "tier": "never_built",
                "message": "Knowledge graph never built",
                "hint": _FIX_HINT_GRAPH_BUILD,
            },
        )

    age_days = freshness.age_days
    commits_behind = freshness.commits_behind
    commits_suffix = (
        f" ({commits_behind} commits behind)" if commits_behind is not None else ""
    )

    if freshness.tier == "critical":
        message = (
            f"Knowledge graph critically stale: {age_days} days old{commits_suffix}"
        )
        hint = (
            f"Rebuild before relying on graph-backed reviews: {_FIX_HINT_GRAPH_BUILD}"
        )
    else:  # "warn"
        message = f"Knowledge graph is {age_days} days old{commits_suffix}"
        hint = f"Consider rebuilding: {_FIX_HINT_GRAPH_BUILD}"

    return CheckResult(
        name="graph",
        status="warn",
        data={
            "tier": freshness.tier,
            "age_days": age_days,
            "commits_behind": commits_behind,
            "message": message,
            "hint": hint,
        },
    )


_HINT_CLEAN_DRY_RUN = "run: rai clean --dry-run"


def check_legacy_residues(project: Path, cwd: Path) -> CheckResult:
    """Advisory legacy-residue check for session open (S4).

    Runs ``scan_project(cwd)`` (stat/glob-only, no global scan) and compares
    the project-only hash against the acknowledged snooze hash.  Status is
    capped at ``warn`` (D6) — never ``blocked``.

    Best-effort by contract (D5): callers MUST wrap in ``try/except``.
    """
    _ = project  # D3: checkout-scoped; parity signature
    residues = scan_project(cwd).residues
    if not residues:
        return CheckResult(name="legacy", status="ok", data={"residues": 0})
    current = compute_set_hash(residues)
    if read_acknowledged_project_hash(cwd) == current:
        return CheckResult(
            name="legacy",
            status="ok",
            data={"residues": len(residues), "acknowledged": True, "set_hash": current},
        )
    return CheckResult(
        name="legacy",
        status="warn",
        data={
            "residues": len(residues),
            "acknowledged": False,
            "set_hash": current,
            "hint": _HINT_CLEAN_DRY_RUN,
        },
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
    graph: CheckResult = CheckResult(name="graph", status="ok", data={"skipped": True})
    legacy: CheckResult = CheckResult(
        name="legacy", status="ok", data={"skipped": True}
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

    # Ensure .mcp.json exists for main-checkout sessions (RAISE-15848).
    # Fail-open: .mcp.json write failure must never prevent session open.
    try:
        from raise_cli.worktree.provision import ensure_mcp_json

        ensure_mcp_json(project_path)
    except Exception:  # noqa: BLE001
        _log.debug("ensure_mcp_json failed (non-fatal)", exc_info=True)

    hygiene = check_hygiene(cwd)
    drift = check_base_drift(
        cwd,
        get_worktree_merge_target(project_path, cwd),
        in_worktree=is_in_worktree(project_path, cwd),
    )
    db = check_db_health(get_project_db_path(project_path))
    mission = resolve_mission(project_path, cwd)
    mcp = summarize_mcp(project_path, servers=mcp_servers, checker=mcp_checker)

    try:
        worktrees = check_stale_worktrees(project_path, cwd)
    except Exception as exc:  # noqa: BLE001 — stale check is best-effort
        _log.warning("Stale worktree check failed (non-fatal): %s", exc)
        worktrees = CheckResult(name="worktrees", status="ok", data={"error": str(exc)})

    update = check_update_available()

    try:
        graph = check_graph_freshness(cwd)
    except Exception as exc:  # noqa: BLE001 — graph freshness is best-effort
        _log.warning("Graph freshness check failed (non-fatal): %s", exc)
        graph = CheckResult(name="graph", status="ok", data={"error": str(exc)})

    try:
        legacy = check_legacy_residues(project_path, cwd)
    except Exception as exc:  # noqa: BLE001 — legacy check is best-effort (D5)
        _log.warning("Legacy residue check failed (non-fatal): %s", exc)
        legacy = CheckResult(name="legacy", status="ok", data={"error": str(exc)})

    checks = (hygiene, drift, db, mission, mcp, worktrees, update, graph, legacy)
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
        graph=graph,
        legacy=legacy,
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
    except (OSError, subprocess.TimeoutExpired) as exc:
        _log.warning("Bundle start subprocess timed out/failed (non-fatal): %s", exc)
        return ""
    if proc.returncode != 0:
        _log.warning(
            "Bundle start subprocess exited %d (non-fatal): %s",
            proc.returncode,
            proc.stderr.strip(),
        )
        return ""
    return proc.stdout


def bundle_skip_reason(report: OpenReport, include_bundle: bool) -> str | None:
    """Return why the mutating start flow would be skipped, or None if it can run.

    Single source of truth for the gating condition — `should_run_start_for_bundle`
    is derived from this (RAISE-16220 AR: avoid duplicating the condition).

    An explicit `--no-bundle`/`include_bundle=False` request is a deliberate
    "checks only" ask, not a reason to surface — returns None.
    """
    if not include_bundle:
        return None
    if report.status == "blocked":
        return "blocked"
    if report.mission.data.get("needs_selection"):
        return "needs_selection"
    return None


def should_run_start_for_bundle(report: OpenReport, include_bundle: bool) -> bool:
    """Return True when session-open may run the mutating start flow."""
    return include_bundle and bundle_skip_reason(report, include_bundle) is None


def run_or_log_bundle_skip(
    report: OpenReport, project: Path, include_bundle: bool
) -> OpenReport:
    """Run the start bundle, or log why it was skipped.

    Single call-site helper — keeps the run/skip/log decision in one place
    instead of duplicating the branch across every `session open` entry point
    (CLI command, MCP tool).
    """
    # should_run_start_for_bundle() gates on include_bundle first; bundle_skip_reason()
    # returns None both when ready to run AND when include_bundle=False (nothing to
    # report), so the two calls can't be collapsed into one without losing that gate.
    if should_run_start_for_bundle(report, include_bundle):
        return report.model_copy(update={"bundle": run_start_for_bundle(project)})
    reason = bundle_skip_reason(report, include_bundle)
    if reason is not None:
        _log.warning("Session start bundle skipped: %s", reason)
    return report


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
