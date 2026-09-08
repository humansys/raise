"""Composite story-open service — S7884.3 (E7884 K1, ADR-093/ADR-024).

Ports the deterministic sequence that lived as bash prose in the
rai-story-start skill (epic check, worktree detection, branch creation,
docs write, scope commit, backlog transition, session bind) into tested
code, so the skill becomes a thin presenter.

Check contract (jidoka): every step returns a ``CheckResult`` with
``status`` ok|warn|blocked plus structured ``data``. ``blocked`` means a
human decision is required — the service never auto-resolves it, and
steps after a blocked step are skipped.
"""

from __future__ import annotations

import logging
import sqlite3
import subprocess
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from raise_cli.backlog.hooks import assign_fix_version
from raise_cli.git.branch_guard import assert_head_branch
from raise_cli.pipeline.run_store import get_run_store
from raise_cli.project_config import resolve_dev_branch
from raise_cli.release_version import resolve_fix_version
from raise_cli.session.open_service import (
    STATUS_RANK,
    CheckResult,
    run_git,
)
from raise_cli.storage.work_items import WorkItemStore as _WorkItemStore
from raise_cli.telemetry.trailer import resolve_session_id, with_session_trailer
from raise_core.workflow.status_sets import ACTIVE_RUN_STATUSES

_log = logging.getLogger(__name__)

_DONE_EXCLUDE = ("cancel", "reject", "abandon", "void")

_TRANSITION_TIMEOUT_S = 30

# git fetch is a real network op — the shared run_git() default (10s, tuned for
# cheap local ops) is too short for it (RAISE-15825 C3).
_FETCH_TIMEOUT_S = 90

# Substring of git's own stderr meaning "origin exists but hasn't received this
# ref yet" — legitimate in greenfield repos where the dev branch hasn't been
# pushed upstream yet. Matched case-insensitively against git's fetch stderr.
_NO_MATCHING_REF_STDERR_MARKER = "couldn't find remote ref"


def _pipeline_run_active(jira_key: str, project: Path) -> bool:  # noqa: ARG001
    """Return True when a pipeline run with an active status exists for *jira_key*.

    Queries the local run store for all runs and filters by ``issue_id``.
    Returns False (fail-open) when the store is unavailable or raises any
    exception — preserving the RAISE-10966 invariant that skill flows are
    never blocked by guard errors (AC4).

    Uses ``ACTIVE_RUN_STATUSES`` from ``raise_core.workflow.status_sets`` as
    the single source of truth for what constitutes an active run (S15033).
    """
    try:
        from raise_cli.adapters.sync import run_sync

        store = get_run_store()
        # RAISE-15201: run_sync is safe from both sync and async callers;
        # bare asyncio.run() raised RuntimeError under an active event loop.
        runs: list[dict[str, object]] = run_sync(store.list_runs())
        return any(
            str(r.get("issue_id", "")) == jira_key
            and str(r.get("status", "")) in ACTIVE_RUN_STATUSES
            for r in runs
        )
    except Exception:  # noqa: BLE001 — fail-open per RAISE-10966
        _log.debug("_pipeline_run_active: store unavailable — fail-open", exc_info=True)
        return False


class StoryOpenReport(BaseModel):
    """Composite result of a story open: every deterministic step."""

    status: str
    epic: CheckResult
    worktree: CheckResult
    branch: CheckResult
    docs: CheckResult
    commit: CheckResult
    backlog: CheckResult
    bind: CheckResult
    work_items: CheckResult = Field(
        default_factory=lambda: CheckResult(
            name="work_items", status="ok", data={"skipped": True}
        )
    )


def _skipped(name: str) -> CheckResult:
    return CheckResult(name=name, status="ok", data={"skipped": True})


def check_work_items_registry(
    project: Path, jira_key: str, *, story_id: str = ""
) -> CheckResult:
    """Verify the story is registered in work_items before branch creation (S9).

    Returns ok when found or no jira_key, warn(missing_in_registry) when the
    key is known but absent and no story_id is available for auto-registration,
    ok(skipped) on OperationalError (pre-v53 schema).

    When ``story_id`` is provided and the item is missing, auto-registers
    the mapping (RTEST-43) and returns ok(auto_registered=True).
    Non-blocking: callers must NOT treat warn as a reason to stop.
    """
    if not jira_key:
        return CheckResult(name="work_items", status="ok", data={"skipped": True})
    try:
        store = _WorkItemStore(project)
        existing = store.get_by_jira_key(jira_key)
    except sqlite3.OperationalError:
        return CheckResult(
            name="work_items",
            status="ok",
            data={"skipped": True, "reason": "no_work_items_table"},
        )
    if existing is None:
        if story_id:
            store.upsert_jira_mapping(local_key=story_id, jira_key=jira_key)
            return CheckResult(
                name="work_items",
                status="ok",
                data={"jira_key": jira_key, "auto_registered": True},
            )
        return CheckResult(
            name="work_items",
            status="warn",
            data={"reason": "missing_in_registry", "jira_key": jira_key},
        )
    return CheckResult(
        name="work_items",
        status="ok",
        data={"jira_key": jira_key, "work_item_id": existing.id},
    )


def _normalize_epic_dir(epic_dir: str) -> str:
    """Strip ``work/epics/`` prefix so callers can pass either form."""
    stripped = epic_dir.replace("\\", "/")
    for prefix in ("work/epics/", "./work/epics/"):
        stripped = stripped.removeprefix(prefix)
    return stripped.rstrip("/")


def check_epic(project: Path, epic_dir: str) -> CheckResult:
    """Epic scope must exist when the story belongs to an epic."""
    if not epic_dir:
        return CheckResult(name="epic", status="ok", data={"standalone": True})
    epic_dir = _normalize_epic_dir(epic_dir)
    scope = project / "work" / "epics" / epic_dir / "scope.md"
    if scope.is_file():
        return CheckResult(
            name="epic",
            status="ok",
            data={"scope": str(scope.relative_to(project))},
        )
    return CheckResult(
        name="epic",
        status="blocked",
        data={
            "missing": str(scope.relative_to(project)),
            "action": "run /rai-epic-start first",
        },
    )


def _is_linked_worktree(cwd: Path) -> bool:
    """True when *cwd* sits inside a LINKED git worktree (not the main checkout).

    A linked worktree's git-dir (``.git/worktrees/<name>``) differs from the
    shared common dir (``.git``); the main checkout's are identical. Used as a
    physical fallback when a worktree isn't registered in the mission store, so a
    story still stacks on the epic's HEAD instead of branching from the
    development branch (RAISE-10283).
    """
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


def detect_worktree(project: Path, cwd: Path) -> CheckResult:
    """Mission-worktree detection: registered binding wins (RAISE-8191).

    Falls back to a physical linked-worktree check when no binding is registered,
    so a story opened inside an epic's git worktree still stacks on HEAD instead
    of silently branching from the development branch (RAISE-10283).
    """
    from raise_cli.storage.worktrees import SqliteWorktreeStore, WorktreeNotFoundError

    try:
        worktree = SqliteWorktreeStore(project).get_by_path(str(cwd))
    except WorktreeNotFoundError:
        if _is_linked_worktree(cwd):
            return CheckResult(
                name="worktree",
                status="ok",
                data={"in_worktree": True, "registered": False},
            )
        return CheckResult(name="worktree", status="ok", data={"in_worktree": False})
    return CheckResult(
        name="worktree",
        status="ok",
        data={
            "in_worktree": True,
            "registered": True,
            "worktree_id": worktree.worktree_id,
            "mission_id": worktree.mission_id,
            "merge_target": worktree.merge_target,
            "branch": worktree.branch,
        },
    )


def sync_dev_branch(cwd: Path, dev_branch: str, *, in_worktree: bool) -> CheckResult:
    """Fetch + ff-only merge *dev_branch* onto HEAD — skipped inside ANY worktree.

    Regla 2 (RAISE-15825, canonical v3 design): once a worktree exists,
    nothing auto-touches its HEAD. Full stop — no branch-selection logic
    inside a worktree at all, regardless of what its ``merge_target`` is,
    registered or not. A worktree's HEAD already reflects the branch
    context it was created with (e.g. an epic branch); fast-forwarding it
    against ANY other branch — even one that's trivially "safe" because the
    two haven't diverged yet — silently collapses that context: the
    ff-only merge succeeds with no error, HEAD moves, and a story branched
    afterwards loses its intended ancestry.

    Two prior attempts got this wrong: attempt 1 (4c959210e) skipped
    correctly but was rejected for not consulting ``merge_target``; attempt
    2 (f2d43b2f0) then synced against ``origin/{merge_target}`` instead —
    which, for the common case (``merge_target == release/3.1.0``
    regardless of what's actually checked out), silently reproduced the
    exact bug this function exists to prevent. There is intentionally no
    ``merge_target`` parameter here. Staleness is a real, separate concern
    already handled by ``session/open_service.check_base_drift`` — visible,
    never auto-corrected.

    Outside any worktree, behavior is unchanged: fetch + ff-only merge
    against the global dev branch (the long-standing, still-correct
    behavior for a long autonomous session creating stories in sequence in
    the main checkout). A missing ``origin`` remote, or an ``origin`` that
    hasn't received *dev_branch* yet (both legitimate in greenfield/local-
    only repos), is treated as "nothing to sync" (``ok``/``skipped``), not a
    blocker (C4). A fetch failure that is neither of those warns rather
    than blocks — fail-open, same convention as ``_pipeline_run_active``.
    A genuine divergence (the ff-only merge itself fails) still blocks:
    that is a real decision the skill must stop on, not paper over.
    """
    if in_worktree:
        return CheckResult(
            name="sync", status="ok", data={"skipped": True, "reason": "in-worktree"}
        )

    remote = run_git(cwd, "remote", "get-url", "origin")
    if remote is None or remote.returncode != 0:
        return CheckResult(
            name="sync", status="ok", data={"skipped": True, "reason": "no-remote"}
        )

    fetch = run_git(cwd, "fetch", "origin", dev_branch, timeout=_FETCH_TIMEOUT_S)
    if fetch is None or fetch.returncode != 0:
        stderr = fetch.stderr.strip() if fetch is not None else "git unavailable"
        if fetch is not None and _NO_MATCHING_REF_STDERR_MARKER in stderr.lower():
            return CheckResult(
                name="sync",
                status="ok",
                data={"skipped": True, "reason": "no-matching-ref"},
            )
        return CheckResult(
            name="sync",
            status="warn",
            data={"reason": "fetch-failed", "error": stderr},
        )

    merge = run_git(cwd, "merge", f"origin/{dev_branch}", "--ff-only")
    if merge is None or merge.returncode != 0:
        return CheckResult(
            name="sync",
            status="blocked",
            data={
                "reason": "dev-branch-diverged",
                "error": (merge.stderr.strip() if merge else "git unavailable"),
            },
        )
    return CheckResult(name="sync", status="ok", data={"dev_branch": dev_branch})


def create_branch(
    repo: Path,
    story_id: str,
    slug: str,
    *,
    dev_branch: str,
    in_worktree: bool,
    resume: bool = False,
) -> CheckResult:
    """Create the story branch — from HEAD in a worktree, else from dev.

    An existing branch is blocked (jidoka): silently reusing it could hide
    a previous half-finished attempt.  When ``resume`` is True the existing
    branch is checked out instead of blocking (RAISE-16908).
    """
    branch = f"story/{story_id.lower()}/{slug}"
    proc = run_git(repo, "rev-parse", "--verify", "--quiet", branch)
    if proc is not None and proc.returncode == 0:
        if not resume:
            return CheckResult(
                name="branch",
                status="blocked",
                data={"reason": "branch-exists", "branch": branch},
            )
        proc = run_git(repo, "checkout", branch)
        if proc is None or proc.returncode != 0:
            return CheckResult(
                name="branch",
                status="blocked",
                data={
                    "reason": "checkout-failed",
                    "error": (proc.stderr.strip() if proc else "git unavailable"),
                },
            )
        return CheckResult(
            name="branch",
            status="ok",
            data={"resumed": True, "branch": branch},
        )

    # Create the story branch atomically from the remote tracking ref so that
    # worktree lock conflicts are impossible (RAISE-9838).  When in_worktree
    # is True we branch from HEAD.  Otherwise prefer origin/{dev_branch} (no
    # local checkout needed → no worktree lock conflict); fall back to the
    # local branch name only when no remote tracking ref exists (e.g., repos
    # with no configured remote, as in local-only test fixtures).
    if in_worktree:
        base_ref: str = "HEAD"
    else:
        remote_ref = f"origin/{dev_branch}"
        probe = run_git(repo, "rev-parse", "--verify", "--quiet", remote_ref)
        base_ref = (
            remote_ref if (probe is not None and probe.returncode == 0) else dev_branch
        )
    proc = run_git(repo, "checkout", "-b", branch, base_ref)
    if proc is None or proc.returncode != 0:
        return CheckResult(
            name="branch",
            status="blocked",
            data={
                "reason": "checkout-failed",
                "error": (proc.stderr.strip() if proc else "git unavailable"),
            },
        )
    base = "HEAD" if in_worktree else dev_branch
    return CheckResult(
        name="branch", status="ok", data={"created": branch, "base": base}
    )


def write_docs(
    project: Path,
    epic_dir: str,
    story_id: str,
    story_content: str,
    scope_content: str,
    resume: bool = False,
) -> CheckResult:
    """Write story.md + scope.md locally (content is LLM judgment — D2).

    When ``resume`` is True, existing non-empty files are preserved
    (RAISE-16908).
    """
    epic_dir = _normalize_epic_dir(epic_dir)
    sid = story_id.lower()
    stories_dir = project / "work" / "epics" / epic_dir / "stories"
    try:
        stories_dir.mkdir(parents=True, exist_ok=True)
        story_path = stories_dir / f"{sid}-story.md"
        scope_path = stories_dir / f"{sid}-scope.md"
        skipped = 0
        for path, content in ((story_path, story_content), (scope_path, scope_content)):
            if resume and path.exists() and path.stat().st_size > 0:
                skipped += 1
                continue
            path.write_text(content, encoding="utf-8")
    except OSError as exc:
        return CheckResult(name="docs", status="blocked", data={"error": str(exc)})
    written = 2 - skipped
    data: dict[str, Any] = {
        "written": written,
        "paths": [
            str(story_path.relative_to(project)),
            str(scope_path.relative_to(project)),
        ],
    }
    if skipped:
        data["skipped"] = skipped
    return CheckResult(name="docs", status="ok", data=data)


def commit_scope(
    repo: Path,
    *,
    expected_branch: str,
    paths: list[str],
    message: str,
) -> CheckResult:
    """Stage and commit only the scope docs, asserting the branch first.

    Re-asserts the branch after the commit lands (RAISE-11103) — the
    pre-commit check above leaves a TOCTOU window between the assertion
    and the commit where a concurrent checkout in another session could
    land the commit on the wrong branch undetected.

    The explicit commit pathspec isolates automation from unrelated files
    already staged by the caller (RAISE-14913).
    """
    proc = run_git(repo, "branch", "--show-current")
    current = proc.stdout.strip() if proc else ""
    if current != expected_branch:
        return CheckResult(
            name="commit",
            status="blocked",
            data={
                "reason": "wrong-branch",
                "expected": expected_branch,
                "current": current,
            },
        )
    proc = run_git(repo, "add", *paths)
    if proc is None or proc.returncode != 0:
        return CheckResult(
            name="commit",
            status="blocked",
            data={"reason": "add-failed", "error": proc.stderr.strip() if proc else ""},
        )
    # Idempotent: if all paths are already committed, nothing to do (RAISE-16908).
    diff_proc = run_git(repo, "diff", "--cached", "--name-only", "--", *paths)
    if (
        diff_proc is not None
        and diff_proc.returncode == 0
        and not diff_proc.stdout.strip()
    ):
        return CheckResult(name="commit", status="ok", data={"skipped": True})
    session_id = resolve_session_id()
    message = with_session_trailer(message, session_id)
    proc = run_git(repo, "commit", "-m", message, "--", *paths)
    if proc is None or proc.returncode != 0:
        return CheckResult(
            name="commit",
            status="blocked",
            data={
                "reason": "commit-failed",
                "error": proc.stderr.strip() if proc else "",
            },
        )
    sha_proc = run_git(repo, "rev-parse", "--short", "HEAD")
    sha = sha_proc.stdout.strip() if sha_proc else ""
    # Post-commit branch-drift assertion (RAISE-11103, closes the TOCTOU window)
    branch_ok, current_branch = assert_head_branch(repo, expected_branch)
    if not branch_ok:
        return CheckResult(
            name="commit",
            status="blocked",
            data={
                "reason": "branch-drift-after-commit",
                "expected": expected_branch,
                "current": current_branch,
                "sha": sha,
            },
        )
    return CheckResult(name="commit", status="ok", data={"sha": sha})


def _workflow_states(project: Path) -> list[dict[str, Any]]:
    """Configured workflow states from .raise/backlog.yaml, or []."""
    import yaml

    cfg_path = project / ".raise" / "backlog.yaml"
    if not cfg_path.is_file():
        return []
    try:
        cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        return []
    states = cfg.get("jira", {}).get("workflow", {}).get("states", [])
    return states if isinstance(states, list) else []


def transition_backlog(project: Path, jira_key: str, *, kind: str) -> CheckResult:
    """Infer the target status and transition via the rai CLI.

    Jidoka (D4): one candidate transitions silently; multiple block with
    the list; zero (or no adapter) skips. The transition subprocess keeps
    credential handling in the CLI adapter layer.

    Engine-owned guard (S15033 / RAISE-15027 Stage 2): when a pipeline run
    is active for *jira_key*, skill-initiated transitions are skipped and a
    warn result with ``engine_owned=True`` is returned. Fail-open per RAISE-10966.
    """
    if not jira_key:
        return CheckResult(name="backlog", status="ok", data={"skipped": True})
    states = _workflow_states(project)
    if not states:
        return CheckResult(
            name="backlog",
            status="ok",
            data={"skipped": True, "reason": "no-workflow-config"},
        )

    # Engine-owned guard: skip skill transition when engine is running (AC3)
    if _pipeline_run_active(jira_key, project):
        _log.info(
            "pipeline run active — skipping skill transition (engine owns this)",
            extra={"jira_key": jira_key},
        )
        return CheckResult(
            name="backlog",
            status="warn",
            data={"engine_owned": True, "jira_key": jira_key},
        )

    if kind == "start":
        # Engine-owned: explicit target_status in YAML supersedes keyword heuristics.
        # All indeterminate states are candidates; jidoka blocks when ambiguous (RAISE-15038).
        candidates = [
            s["name"] for s in states if s.get("status_category") == "indeterminate"
        ]
    else:
        candidates = [
            s["name"]
            for s in states
            if s.get("status_category") == "done"
            and not any(k in str(s.get("name", "")).lower() for k in _DONE_EXCLUDE)
        ]

    if not candidates:
        return CheckResult(
            name="backlog",
            status="ok",
            data={"skipped": True, "reason": "no-candidates"},
        )
    if len(candidates) > 1:
        return CheckResult(
            name="backlog",
            status="blocked",
            data={
                "reason": f"multiple-{kind}-candidates",
                "candidates": candidates,
            },
        )

    status = candidates[0]
    # The terminal close is an invariant: a failed Done transition BLOCKS
    # (not warn) so Jira cannot silently diverge from git (RAISE-10966).
    fail_status = "blocked" if kind == "done" else "warn"
    try:
        proc = subprocess.run(
            ["rai", "backlog", "transition", jira_key, status],
            capture_output=True,
            text=True,
            timeout=_TRANSITION_TIMEOUT_S,
            check=False,
            cwd=project,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return CheckResult(name="backlog", status=fail_status, data={"error": str(exc)})
    if proc.returncode != 0:
        return CheckResult(
            name="backlog",
            status=fail_status,
            data={"error": proc.stderr.strip() or proc.stdout.strip()},
        )
    if kind == "done":
        return _finalize_done(project, jira_key, status)
    return CheckResult(name="backlog", status="ok", data={"transitioned": status})


def _finalize_done(project: Path, jira_key: str, status: str) -> CheckResult:
    """Assign the active-release fixVersion after a successful Done transition.

    Blocks the close if the fixVersion assignment fails, so version drift
    cannot accumulate silently (RAISE-10966). When no release version can be
    derived (non-release dev branch) the close completes without a version.

    Delegates fixVersion assignment to ``raise_cli.backlog.hooks.assign_fix_version``
    (extracted in RAISE-15033 as part of Stage 2 ownership-flip enforcement).
    """
    version = _active_release_version(project)
    if version:
        assign_error = assign_fix_version(project, jira_key, version)
        if assign_error is not None:
            return CheckResult(
                name="backlog",
                status="blocked",
                data={"error": assign_error, "transitioned": status},
            )
    return CheckResult(name="backlog", status="ok", data={"transitioned": status})


def bind_session(project: Path, jira_key: str) -> CheckResult:
    """Bind RAISE_SESSION_JIRA_KEY to the active agent session (best-effort)."""
    if not jira_key:
        return CheckResult(name="bind", status="ok", data={"skipped": True})
    try:
        from raise_cli._agent_session import discover_agent_session_id
        from raise_cli.session.context_env import write_context_env

        session_id = discover_agent_session_id()
        if not session_id:
            return CheckResult(
                name="bind",
                status="warn",
                data={"reason": "no-agent-session"},
            )
        write_context_env(project, session_id, "RAISE_SESSION_JIRA_KEY", jira_key)
    except Exception as exc:  # noqa: BLE001 — bind is best-effort by contract
        return CheckResult(name="bind", status="warn", data={"error": str(exc)})
    return CheckResult(name="bind", status="ok", data={"key": jira_key})


def _active_release_version(project: Path) -> str | None:
    """Release version derived from the development branch, or None."""
    return resolve_fix_version(project, resolve_dev_branch(project))


def build_story_open_report(
    *,
    project_path: Path,
    cwd: Path,
    story_id: str,
    slug: str,
    jira_key: str,
    epic_dir: str,
    story_content: str,
    scope_content: str,
    dev_branch: str = "",
    commit_message: str = "",
    resume: bool = False,
) -> StoryOpenReport:
    """Run the full story-open sequence; skip everything after a block."""
    dev_branch = dev_branch or resolve_dev_branch(project_path)
    sid = story_id.lower()
    branch_name = f"story/{sid}/{slug}"

    epic = check_epic(project_path, epic_dir)
    worktree = detect_worktree(project_path, cwd)
    work_items = check_work_items_registry(project_path, jira_key, story_id=story_id)

    blocked = epic.status == "blocked"
    branch = (
        _skipped("branch")
        if blocked
        else create_branch(
            cwd,
            story_id,
            slug,
            dev_branch=dev_branch,
            in_worktree=bool(worktree.data.get("in_worktree")),
            resume=resume,
        )
    )
    blocked = blocked or branch.status == "blocked"
    docs = (
        _skipped("docs")
        if blocked
        else write_docs(
            project_path,
            epic_dir,
            story_id,
            story_content,
            scope_content,
            resume=resume,
        )
    )
    blocked = blocked or docs.status == "blocked"
    commit = (
        _skipped("commit")
        if blocked
        else commit_scope(
            cwd,
            expected_branch=branch_name,
            paths=list(docs.data.get("paths", [])),
            message=commit_message
            or f"feat({sid}): initialize story scope\n\nCo-Authored-By: Rai <rai@humansys.ai>",
        )
    )
    blocked = blocked or commit.status == "blocked"
    backlog = (
        _skipped("backlog")
        if blocked
        else transition_backlog(project_path, jira_key, kind="start")
    )
    bind = _skipped("bind") if blocked else bind_session(project_path, jira_key)

    checks = (epic, worktree, branch, docs, commit, backlog, bind, work_items)
    worst = max(checks, key=lambda c: STATUS_RANK[c.status]).status
    return StoryOpenReport(
        status=worst,
        epic=epic,
        worktree=worktree,
        branch=branch,
        docs=docs,
        commit=commit,
        backlog=backlog,
        bind=bind,
        work_items=work_items,
    )
