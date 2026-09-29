"""Composite session-open service — S7884.2 (E7884 K1, ADR-093/ADR-024).

Ports the deterministic checks that lived as bash prose in the
rai-session-start skill (working-tree hygiene, base-branch drift, DB
health) into tested code, so bookend skills become thin presenters.

Check contract (jidoka): every check returns a ``CheckResult`` with
``status`` ok|warn|blocked plus structured ``data``. ``blocked`` means a
human decision is required — the service never auto-resolves it.
"""

from __future__ import annotations

import json
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

from raise_cli._agent_session import discover_agent_runtime
from raise_cli.compat import IS_FROZEN
from raise_cli.config.paths import checkout_scope_id
from raise_cli.context.freshness import (
    BacklogFreshnessReport,
    evaluate_backlog_freshness,
    evaluate_graph_freshness,
)
from raise_cli.core.manifest import MANIFEST_URL, fetch_manifest, is_newer

# Imported at module level to allow monkeypatching in tests.
from raise_cli.legacy.scanner import scan_project
from raise_cli.legacy.snooze import compute_set_hash, read_acknowledged_project_hash
from raise_cli.session.bundle import format_orientation_ledger
from raise_cli.session.lifecycle import SessionMeta
from raise_cli.session.update_cache import read_update_cache, write_update_cache
from raise_cli.storage.connection import get_project_db_path, get_project_id
from raise_cli.worktree.prune import has_active_lease

_UPDATE_CHECK_TIMEOUT_S = 2.0
_UPDATE_CHECK_SILENCE_ENV_VAR = "RAI_NO_UPDATE_CHECK"

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
        return subprocess.run(
            ["git", *args],
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


def _default_mcp_configs(project: Path) -> dict[str, Any]:
    from raise_cli.mcp.registry import discover_mcp_servers

    try:
        return dict(discover_mcp_servers(project / ".raise" / "mcp"))
    except Exception:  # noqa: BLE001 — MCP discovery is advisory
        return {}


def _probe_mcp_server_available(command: str) -> bool | None:
    """Check if MCP server binary is available in PATH. None = unknown (fail-open)."""
    import shutil

    try:
        return shutil.which(command) is not None
    except Exception:  # noqa: BLE001
        return None


def summarize_mcp(
    project: Path,
    servers: list[str] | None = None,
    checker: Callable[[str], bool] | None = None,
) -> CheckResult:
    """MCP server process availability — {total, healthy, configured} (RAISE-17628).

    When ``checker`` is provided it receives server names and drives the healthy
    count (backward-compat path, primary for tests). Without a checker,
    ``shutil.which(command)`` probes each server's binary availability.
    Fail-open: unavailable binary or exception counts as unknown, not healthy.
    """
    if checker is not None:
        names = servers if servers is not None else _default_mcp_servers(project)
        n = len(names)
        healthy = sum(1 for name in names if _safe_bool(checker, name) is True)
    else:
        configs = _default_mcp_configs(project)
        if servers is not None:
            configs = {name: configs[name] for name in servers if name in configs}
            n = len(servers)
        else:
            n = len(configs)
        healthy = sum(
            1
            for cfg in configs.values()
            if _probe_mcp_server_available(cfg.server.command) is True
        )
    return CheckResult(
        name="mcp",
        status="ok",
        data={"total": n, "healthy": healthy, "configured": n},
    )


def _safe_bool(fn: Callable[[str], bool], arg: str) -> bool | None:
    """Call fn(arg) and return None on any exception (fail-open)."""
    try:
        return fn(arg)
    except Exception:  # noqa: BLE001
        return None


def check_update_available(
    *,
    is_frozen: bool = IS_FROZEN,
    manifest_url: str = MANIFEST_URL,
    current_version: str | None = None,
    timeout_s: float = _UPDATE_CHECK_TIMEOUT_S,
    transport: httpx.BaseTransport | None = None,
    cache_path: Path | None = None,
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

    Wrapped with a 24h disk cache (RAISE-15660) — only a successful fetch
    is cached, so a network/parse failure is retried on the next call
    instead of silencing the check for a full day. Set
    ``RAI_NO_UPDATE_CHECK`` to skip both the cache and the network call.
    """
    if os.environ.get(_UPDATE_CHECK_SILENCE_ENV_VAR):
        return CheckResult(
            name="update", status="ok", data={"skipped": True, "reason": "silenced"}
        )

    if not is_frozen:
        return CheckResult(
            name="update", status="ok", data={"skipped": True, "reason": "not-frozen"}
        )

    cached = read_update_cache(path=cache_path)
    if cached is not None:
        return CheckResult(name="update", status=cached.status, data=cached.data)

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
        result = CheckResult(name="update", status="ok", data={"current": local})
    else:
        data: dict[str, Any] = {
            "current": local,
            "latest": manifest.version,
            "url": manifest_url,
            "upgrade_hint": "rai upgrade",
        }
        # RAISE-15661 — only present when the manifest declares it, so
        # manifests published before this story behave exactly as before.
        if manifest.severity is not None:
            data["severity"] = manifest.severity
        result = CheckResult(name="update", status="warn", data=data)

    write_update_cache(result.status, result.data, path=cache_path)
    return result


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


def detect_stale_worktrees(
    project: Path,
    cwd: Path,
    *,
    stale_after_hours: float = 48.0,
) -> CheckResult:
    """Detect stale worktrees — pure, no side effects (S17495.5 AC-1).

    A worktree is stale when:
    - its last session (or creation) is older than *stale_after_hours*, AND
    - it has no live session lease.

    Never executes git worktree remove, git branch -d, or store.complete().
    Use ``rai worktree prune`` to reap stale worktrees.

    Best-effort by contract — callers MUST wrap in ``try/except Exception``.
    """
    from raise_cli.storage.connection import get_project_db
    from raise_cli.storage.worktrees import SqliteWorktreeStore

    _ = cwd  # kept for signature parity with the doctor check caller contract
    stale_threshold = timedelta(hours=stale_after_hours)
    now = datetime.now(UTC)

    store = SqliteWorktreeStore(project)
    conn = get_project_db(project)
    worktrees = store.list_worktrees()  # open only

    stale_ids: list[str] = []

    for wt in worktrees:
        if has_active_lease(wt.worktree_id, project):
            continue
        last_active = _worktree_last_active(conn, wt)
        if last_active is None:
            continue
        if now - last_active < stale_threshold:
            continue
        stale_ids.append(wt.worktree_id)
        _log.info(
            "Detected stale worktree '%s' (last active: %s)",
            wt.worktree_id,
            last_active.isoformat(),
        )

    status: CheckStatus = "warn" if stale_ids else "ok"
    return CheckResult(
        name="worktrees",
        status=status,
        data={"stale": stale_ids},
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


_FIX_HINT_BACKLOG_SYNC = "rai backlog sync --all"
_FIX_HINT_PORTFOLIO_GENERATE = "rai portfolio cartridge generate {project_id} {org_id}"


def _stale_portfolio_entries(
    freshness: BacklogFreshnessReport,
) -> list[dict[str, object]]:
    """Map stale ``portfolio-issues-*`` cartridges to ``data`` entries.

    RAISE-15972 — ``rai backlog sync --all`` does NOT regenerate these; the
    per-cartridge remedy is ``rai portfolio cartridge generate PROJECT_KEY ORG``,
    built from that cartridge's own ids and degraded to the literal template
    when either is absent (D3.6).
    """
    entries: list[dict[str, object]] = []
    for item in freshness.portfolio:
        if item.tier != "stale":
            continue
        entries.append(
            {
                "name": item.name,
                "age_days": item.age_days,
                "hint": _FIX_HINT_PORTFOLIO_GENERATE.format(
                    project_id=item.project_id or "<PROJECT_KEY>",
                    org_id=item.org_id or "<ORG>",
                ),
            }
        )
    return entries


def check_backlog_freshness(repo: Path) -> CheckResult:
    """Advisory backlog mirror staleness check (RAISE-16998, RAISE-15972).

    Status is capped at ``warn`` — NEVER ``blocked``.  Fail-open by contract:
    callers MUST wrap this in ``try/except``.

    Covers both backlog-derived cartridge families. ``data["portfolio"]`` is
    added only when at least one ``portfolio-issues-*`` cartridge is stale
    (RAISE-15972 D3.7), so the ``backlog-*`` output is byte-identical whenever
    the family is absent or fresh.
    """
    freshness = evaluate_backlog_freshness(repo)
    portfolio = _stale_portfolio_entries(freshness)

    if freshness.tier == "ok":
        if not portfolio:
            return CheckResult(name="backlog", status="ok", data={"tier": "ok"})
        first = portfolio[0]
        return CheckResult(
            name="backlog",
            status="warn",
            data={
                "tier": "ok",
                "portfolio": portfolio,
                "message": (
                    f"Portfolio cartridge {first['name']} is "
                    f"{first['age_days']} days old"
                ),
                "hint": f"Regenerate: {first['hint']}",
            },
        )

    if freshness.tier == "never_synced":
        data: dict[str, object] = {
            "tier": "never_synced",
            "message": "Backlog mirror never synced",
            "hint": _FIX_HINT_BACKLOG_SYNC,
        }
        if portfolio:
            data["portfolio"] = portfolio
        return CheckResult(name="backlog", status="warn", data=data)

    # "stale"
    age_days = freshness.age_days if freshness.age_days is not None else 0
    stale_data: dict[str, object] = {
        "tier": "stale",
        "age_days": age_days,
        "message": f"Backlog mirror is {age_days} days old",
        "hint": f"Consider syncing: {_FIX_HINT_BACKLOG_SYNC}",
    }
    if portfolio:
        stale_data["portfolio"] = portfolio
    return CheckResult(name="backlog", status="warn", data=stale_data)


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
    """Composite result of a session open: all checks plus the bundle.

    S1 (RAISE-17550): mission and worktrees removed from the hot path —
    their fields default to skipped so existing callers stay backward-compat.
    """

    status: CheckStatus
    hygiene: CheckResult
    drift: CheckResult
    db: CheckResult
    # S1: mission dissolved (ADR-130) — skipped default keeps payload shape stable
    mission: CheckResult = CheckResult(
        name="mission", status="ok", data={"skipped": True}
    )
    mcp: CheckResult
    # S1: stale-worktree check removed from open hot path — skipped default
    worktrees: CheckResult = CheckResult(
        name="worktrees", status="ok", data={"skipped": True}
    )
    update: CheckResult = CheckResult(
        name="update", status="ok", data={"skipped": True}
    )
    graph: CheckResult = CheckResult(name="graph", status="ok", data={"skipped": True})
    legacy: CheckResult = CheckResult(
        name="legacy", status="ok", data={"skipped": True}
    )
    backlog: CheckResult = CheckResult(
        name="backlog", status="ok", data={"skipped": True}
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
    """Run the 4 deterministic open checks and aggregate the worst status.

    S1 (RAISE-17550): slimmed from 10 → 4 checks. Diagnostic checks
    (worktrees, update, graph, legacy, backlog) removed from hot path —
    their OpenReport fields default to skipped. Mission dissolved (ADR-130).

    ensure_mcp_json now runs AFTER check_hygiene (D-S1-01): blocked hygiene
    → .mcp.json never written.
    """
    from raise_cli.storage.connection import get_project_db_path

    # Hygiene FIRST (D-S1-01): gate all writes behind this check.
    hygiene = check_hygiene(cwd)

    # ensure_mcp_json only when hygiene allows mutation (D-S1-01 / RAISE-15848).
    if hygiene.status != "blocked":
        try:
            from raise_cli.worktree.provision import ensure_mcp_json

            ensure_mcp_json(project_path)
        except Exception:  # noqa: BLE001
            _log.debug("ensure_mcp_json failed (non-fatal)", exc_info=True)

    drift = check_base_drift(
        cwd,
        get_worktree_merge_target(project_path, cwd),
        in_worktree=is_in_worktree(project_path, cwd),
    )
    db = check_db_health(get_project_db_path(project_path))
    mcp = summarize_mcp(project_path, servers=mcp_servers, checker=mcp_checker)

    checks = (hygiene, drift, db, mcp)
    worst = max(checks, key=lambda c: _STATUS_RANK[c.status]).status
    return OpenReport(
        status=worst,
        hygiene=hygiene,
        drift=drift,
        db=db,
        mcp=mcp,
        bundle=bundle,
    )


class GuardrailsBlock(BaseModel):
    """Session-time guardrails summary loaded from the graph (S17495.3).

    status values:
    - graph_not_built: no graph partition exists yet for this checkout
    - no_guardrails:   graph built, zero guardrail nodes of any level
    - no_active_must:  graph built, SHOULD/COULD nodes exist but no MUST (always_on)
    - ok:              at least one always_on=True guardrail node loaded
    """

    items: list[Any] = []
    status: Literal["ok", "graph_not_built", "no_guardrails", "no_active_must"]
    hint: str | None = None


def _count_guardrail_nodes(project_path: Path) -> int:
    """Count total guardrail nodes in the graph for this checkout (raw SQLite).

    Scoped to project_id + checkout_id — same pattern as _fetch_always_on_rows.
    Returns 0 on any error (fail-open).
    """
    try:
        db_path = get_project_db_path(project_path)
        if not db_path.is_file():
            return 0
        project_id = get_project_id(project_path)
        cid = checkout_scope_id(project_path)
        conn = sqlite3.connect(str(db_path))
        try:
            row = conn.execute(
                "SELECT COUNT(*) FROM graph_nodes"
                " WHERE project_id = ? AND checkout_id = ? AND node_type = 'guardrail'",
                (project_id, cid),
            ).fetchone()
        finally:
            conn.close()
        return int(row[0]) if row else 0
    except Exception:  # noqa: BLE001 — fail-open; never block session start
        return 0


def _load_always_on_guardrail_nodes(project_path: Path) -> list[Any]:
    """Load always_on guardrail nodes from SQLite for this checkout.

    Row format mirrors _row_to_node in sqlite.py:
    (node_id, node_type, content, source_file, metadata_json, created_at).
    Returns [] on any error (fail-open).
    """
    import json as _json

    from raise_core.graph.models import GraphNode

    try:
        db_path = get_project_db_path(project_path)
        if not db_path.is_file():
            return []
        project_id = get_project_id(project_path)
        cid = checkout_scope_id(project_path)
        conn = sqlite3.connect(str(db_path))
        try:
            rows = conn.execute(
                """
                SELECT node_id, node_type, content, source_file,
                       metadata_json, created_at
                FROM graph_nodes
                WHERE project_id = ?
                  AND checkout_id = ?
                  AND node_type = 'guardrail'
                  AND always_on = 1
                ORDER BY node_id
                """,
                (project_id, cid),
            ).fetchall()
        finally:
            conn.close()

        nodes: list[Any] = []
        for node_id, node_type, content, source_file, metadata_json, created_at in rows:
            meta: dict[str, Any] = {}
            if metadata_json:
                import contextlib

                with contextlib.suppress(ValueError, TypeError):
                    meta = _json.loads(metadata_json)
            nodes.append(
                GraphNode.model_validate(
                    {
                        "id": node_id,
                        "type": node_type,
                        "content": content,
                        "source_file": source_file or None,
                        "created": created_at,
                        "metadata": meta,
                    }
                )
            )
        return nodes
    except Exception:  # noqa: BLE001 — fail-open
        return []


def load_guardrails(project_path: Path) -> GuardrailsBlock:
    """Load session-time guardrails from the graph (always_on nodes only).

    Uses raw SQLite reads (~15ms). Falls back gracefully — never blocks session open.
    """
    try:
        if evaluate_graph_freshness(project_path).built_at is None:
            return GuardrailsBlock(
                status="graph_not_built",
                hint="rai graph build",
                items=[],
            )

        guardrail_nodes = _load_always_on_guardrail_nodes(project_path)

        if not guardrail_nodes:
            if _count_guardrail_nodes(project_path) == 0:
                return GuardrailsBlock(
                    status="no_guardrails",
                    hint="governance/guardrails.md has no rules yet — run rai graph build after adding them",
                    items=[],
                )
            return GuardrailsBlock(
                status="no_active_must",
                hint="only SHOULD/COULD guardrails defined — no MUST rules loaded as always_on",
                items=[],
            )

        return GuardrailsBlock(status="ok", hint=None, items=guardrail_nodes)
    except Exception:  # noqa: BLE001 — fail-open; never block session start
        _log.debug("load_guardrails failed; returning graph_not_built", exc_info=True)
        return GuardrailsBlock(
            status="graph_not_built",
            hint="rai graph build",
            items=[],
        )


class SessionOpenPayload(BaseModel):
    """Structured output of open_session() — carries report + lifecycle meta.

    Serialized flat (report fields merged to top-level) by serialize_payload()
    so MCP consumers keep the existing JSON shape (backward compat).
    """

    report: OpenReport
    meta: SessionMeta | None = None
    rai_meta: dict[str, Any] = {}
    readiness: dict[str, Any] | None = None
    readiness_warning: dict[str, Any] | None = None
    session_lease: dict[str, Any] | None = None
    deprecations: list[str] = []
    guardrails: GuardrailsBlock | None = None


_READINESS_GATE_ENV = "RAISE_SESSION_READINESS_GATE"


def _evaluate_readiness(
    project: Path,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    """Evaluate workspace readiness for leased worktrees (read-only, best-effort).

    Returns (readiness_dict, readiness_warning_dict) or (None, None) on skip/failure.
    """
    from contextlib import suppress

    if os.environ.get(_READINESS_GATE_ENV, "1") in ("0", "false", "False"):
        return None, None
    if not (project / ".git").is_file():
        return None, None

    with suppress(Exception):
        from raise_cli.workspace.readiness import evaluate_workspace_readiness
        from raise_cli.worktree.provision import git_worktree_readiness_policy

        wt_report = evaluate_workspace_readiness(
            project, git_worktree_readiness_policy()
        )
        readiness: dict[str, Any] = {
            "is_ready": wt_report.is_ready,
            "findings": [
                {"code": f.code, "message": f.message, "severity": f.severity}
                for f in wt_report.findings
            ],
        }
        readiness_warning: dict[str, Any] | None = None
        if not wt_report.is_ready:
            readiness_warning = {
                "message": (
                    "Workspace has readiness issues — run "
                    "'rai worktree register' to re-provision."
                ),
                "required_findings": [f.code for f in wt_report.required_findings],
            }
        return readiness, readiness_warning
    return None, None


def _acquire_lease(project: Path) -> dict[str, Any] | None:
    """Acquire a worktree session lease; returns lease dict or None (best-effort)."""
    from contextlib import suppress

    if not (project / ".git").is_file():
        return None
    with suppress(Exception):
        from raise_cli._agent_session import discover_agent_session_id
        from raise_cli.cockpit.session_lease import (
            acquire_session_lease,
            resolve_worktree_for_session,
        )
        from raise_cli.storage.leases import SqliteLeaseStore

        sid = discover_agent_session_id()
        if sid:
            wt_id = resolve_worktree_for_session(project, project)
            if wt_id:
                store = SqliteLeaseStore(project)
                acquired = acquire_session_lease(store, wt_id, sid)
                return {"worktree_id": wt_id, "acquired": acquired}
    return None


def open_session(
    project_path: Path,
    cwd: Path,
    *,
    session_meta: SessionMeta | None = None,
    mutate: bool = True,
) -> SessionOpenPayload:
    """Assemble session-open payload from a pre-run lifecycle result (T3 / RAISE-17550).

    session_meta: pass the result of ensure_session_lifecycle() (from
    raise_cli.pipeline.lifecycle) when mutation is desired. None → checks-only.
    mutate=False is deprecated — pass session_meta=None instead.
    blocked report → checks-only regardless of session_meta (D1).
    Workspace readiness is always evaluated for worktrees (read-only).
    """
    report = build_open_report(project_path, cwd)
    report.orientation_ledger = format_orientation_ledger(project_path)
    readiness, readiness_warning = _evaluate_readiness(cwd)

    guardrails_block = load_guardrails(project_path)

    if report.status == "blocked" or session_meta is None:
        deprecations: list[str] = []
        if not mutate:
            deprecations.append(
                "mutate=False → use rai doctor / raise_session_health (3.1.3)"
            )
        return SessionOpenPayload(
            report=report,
            readiness=readiness,
            readiness_warning=readiness_warning,
            rai_meta={"session_id": None, "rai_session_id": "", "agent_session_id": ""},
            deprecations=deprecations,
            guardrails=guardrails_block,
        )

    session_lease = _acquire_lease(cwd)
    agent_sid = session_meta.agent_session_id
    return SessionOpenPayload(
        report=report,
        meta=session_meta,
        readiness=readiness,
        readiness_warning=readiness_warning,
        session_lease=session_lease,
        rai_meta={
            "session_id": agent_sid,
            "rai_session_id": session_meta.session_id,
            "agent_session_id": agent_sid,
            "agent": discover_agent_runtime(),
        },
        guardrails=guardrails_block,
    )


def serialize_payload(payload: SessionOpenPayload) -> str:
    """Canonical JSON serializer — flat shape, no TypeError on Path (D-S1-03).

    Merges report fields to top-level (backward compat with existing MCP
    consumers). Uses model_dump(mode='json') so Path objects become strings.
    """
    d = payload.report.model_dump(mode="json")
    # Strip empty bundle/ledger fields (match old compact_response behavior)
    if not d.get("bundle"):
        d.pop("bundle", None)
    if not d.get("orientation_ledger"):
        d.pop("orientation_ledger", None)
    d["rai_meta"] = payload.rai_meta
    if payload.meta is not None:
        d["meta"] = payload.meta.model_dump(mode="json")
    if payload.readiness is not None:
        d["readiness"] = payload.readiness
    if payload.readiness_warning is not None:
        d["readiness_warning"] = payload.readiness_warning
    if payload.session_lease is not None:
        d["session_lease"] = payload.session_lease
    if payload.deprecations:
        d["deprecations"] = payload.deprecations
    if payload.guardrails is not None:
        d["guardrails"] = payload.guardrails.model_dump(mode="json")
    return json.dumps(d, ensure_ascii=False, separators=(",", ":"))


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
