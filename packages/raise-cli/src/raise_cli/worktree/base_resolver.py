"""Shared worktree base-branch resolver — RAISE-15825 Regla 1.

Three independent places create/manage worktree base branches today (the
``rai-worktree-open`` skill, the cockpit's ``n`` key, and the pipeline
engine's ``WorktreeManager``); the first two duplicated fetch/reconcile
logic, which is the root of "sometimes it's release/3.1.0, sometimes it's
something else, I can't control it". This module is the single source of
truth both now delegate to (the pipeline engine needs no change — its
``base="HEAD"`` is already Regla 1 case 3 done correctly by construction).

Resolution order:

1. Explicit base given by the caller — use it, no reconciliation.
2. No explicit base — default to the manifest's ``branches.development``,
   reconciled against the newest ``origin/release/*`` branch (RAISE-14694).
3. If the resolved branch (explicit or default) is currently checked out in
   a sibling worktree — i.e. it may be local-only / unpushed — base
   directly off that local branch. Do NOT fetch origin in this case: the
   remote ref may not exist yet or may be stale, and fetching would
   silently drop the sibling worktree's unpushed commits.
4. Never hard-blocks. Worst case is a warning; ``base_ref`` always resolves
   to *something* usable — verified via ``git rev-parse --verify`` before
   being trusted, not assumed from fetch's exit code alone. A successful
   fetch does NOT guarantee ``origin/{branch}`` exists: in shallow or
   single-branch clones the remote-tracking ref may never get created even
   though ``FETCH_HEAD`` did (RAISE-15825 F3). Fallback chain when the
   preferred ref doesn't pan out: ``origin/{branch}`` → ``FETCH_HEAD`` →
   local ``{branch}``.
"""

from __future__ import annotations

import re
from pathlib import Path

from raise_cli.project_config import resolve_dev_branch
from raise_cli.session.open_service import CheckResult, run_git

# git fetch is a real network op — the shared run_git() default (10s, tuned
# for cheap local ops) is too short for it (mirrors RAISE-15825 C3).
_FETCH_TIMEOUT_S = 90


def _sibling_worktree_branch_ref(project: Path, branch: str) -> bool:
    """True when *branch* is checked out in a SIBLING worktree of *project*.

    Detects Regla 1 case 3: the branch may be local-only / unpushed, so
    basing off ``origin/{branch}`` would silently ignore those commits.
    Uses ``git worktree list --porcelain``, which lists ALL worktrees
    (registered in RaiSE's DB or not) — consistent with
    ``story.open_service.detect_worktree()``'s own physical fallback
    (RAISE-10283).

    Excludes *project* itself: ``git worktree list`` always includes the
    worktree the command runs from, so when *branch* happens to be
    *project*'s own currently checked-out branch (the common, non-sibling
    case), that must NOT count as a "sibling" match — it's just the normal
    base branch, and case 3's local-only-ref concern does not apply to it.
    """
    proc = run_git(project, "worktree", "list", "--porcelain")
    if proc is None or proc.returncode != 0:
        return False
    project_resolved = project.resolve()
    target = f"branch refs/heads/{branch}"
    current_path: Path | None = None
    for line in proc.stdout.splitlines():
        if line.startswith("worktree "):
            current_path = Path(line.removeprefix("worktree ").strip())
            continue
        if line.strip() != target or current_path is None:
            continue
        try:
            is_self = current_path.resolve() == project_resolved
        except OSError:
            is_self = False
        if not is_self:
            return True
    return False


def _sibling_worktree_branches(project: Path) -> list[str]:
    """All branches checked out in SIBLING worktrees of *project* (excludes self).

    Same porcelain-parsing approach as ``_sibling_worktree_branch_ref``, but
    collects every match instead of testing one target branch.
    """
    proc = run_git(project, "worktree", "list", "--porcelain")
    if proc is None or proc.returncode != 0:
        return []
    project_resolved = project.resolve()
    branches: list[str] = []
    current_path: Path | None = None
    for line in proc.stdout.splitlines():
        if line.startswith("worktree "):
            current_path = Path(line.removeprefix("worktree ").strip())
            continue
        if not line.startswith("branch refs/heads/") or current_path is None:
            continue
        try:
            is_self = current_path.resolve() == project_resolved
        except OSError:
            is_self = False
        if not is_self:
            branches.append(line.removeprefix("branch refs/heads/").strip())
    return branches


def _recent_local_branches(project: Path) -> list[str]:
    """Local branches, most-recently-committed first."""
    proc = run_git(
        project,
        "for-each-ref",
        "--sort=-committerdate",
        "--format=%(refname:short)",
        "refs/heads/",
    )
    if proc is None or proc.returncode != 0:
        return []
    return [b.strip() for b in proc.stdout.splitlines() if b.strip()]


def list_branch_candidates(project: Path, *, limit: int = 8) -> list[str]:
    """Short list of candidate base branches for the cockpit's `n` prompt (RAISE-15911).

    Before this, the "Base branch" prompt was free-text only — the developer
    had to already know and type the exact branch name. Sibling-worktree
    branches (already-active work, likeliest pick) sort first; remaining
    local branches follow, most-recently-committed first. Never raises: on
    any git failure (e.g. *project* is not a repo) this returns ``[]``, same
    as ``resolve_worktree_base``'s never-hard-blocks stance (rule 4).
    """
    seen: set[str] = set()
    candidates: list[str] = []
    for branch in [
        *_sibling_worktree_branches(project),
        *_recent_local_branches(project),
    ]:
        if branch in seen:
            continue
        seen.add(branch)
        candidates.append(branch)
        if len(candidates) >= limit:
            break
    return candidates


def _version_key(branch: str) -> tuple[int, ...]:
    """Numeric-aware sort key so 'release/3.1.10' sorts after 'release/3.1.9'."""
    return tuple(int(n) for n in re.findall(r"\d+", branch))


def _reconcile_against_remote_releases(
    project: Path, manifest_branch: str
) -> tuple[str, str | None]:
    """Cross-check *manifest_branch* against the newest ``origin/release/*``.

    Mirrors the rai-worktree-open skill's existing reconciliation
    (RAISE-14694): the local manifest silently goes stale when a new
    release branch opens elsewhere. Returns ``(branch_to_use, warning)`` —
    warning is ``None`` when nothing needed correcting (including when
    reconciliation itself could not run, e.g. offline — that is a
    legitimate, silent case, not a warning).
    """
    fetch = run_git(project, "fetch", "origin", timeout=_FETCH_TIMEOUT_S)
    if fetch is None or fetch.returncode != 0:
        return manifest_branch, None
    proc = run_git(project, "branch", "-r", "--list", "origin/release/*")
    if proc is None or proc.returncode != 0 or not proc.stdout.strip():
        return manifest_branch, None
    candidates = [
        line.strip().removeprefix("origin/")
        for line in proc.stdout.splitlines()
        if line.strip()
    ]
    if not candidates:
        return manifest_branch, None
    remote_dev = max(candidates, key=_version_key)
    if remote_dev != manifest_branch:
        return remote_dev, (
            f"local manifest has '{manifest_branch}', remote latest is "
            f"'{remote_dev}' — using '{remote_dev}'"
        )
    return manifest_branch, None


def resolve_worktree_base(project: Path, *, explicit_base: str = "") -> CheckResult:
    """Resolve the branch + base ref for a new worktree/branch (Regla 1).

    Returns a ``CheckResult`` (name ``worktree_base``) whose ``data`` always
    has: ``branch`` (the resolved branch name, no ``origin/`` prefix),
    ``base_ref`` (the ref callers should actually pass to
    ``git worktree add -b <new> <base_ref>`` / ``git checkout -b``),
    ``source`` (``explicit`` | ``manifest`` | ``manifest-reconciled``),
    ``local_sibling`` (whether case 3 applied), and ``warnings`` (list[str],
    possibly empty). Status is ``warn`` whenever ``warnings`` is non-empty,
    ``ok`` otherwise — never ``blocked`` (rule 4).
    """
    warnings: list[str] = []
    if explicit_base:
        branch = explicit_base
        source = "explicit"
    else:
        manifest_branch = resolve_dev_branch(project)
        branch, warning = _reconcile_against_remote_releases(project, manifest_branch)
        if warning:
            warnings.append(warning)
            source = "manifest-reconciled"
        else:
            source = "manifest"

    if _sibling_worktree_branch_ref(project, branch):
        return CheckResult(
            name="worktree_base",
            status="warn" if warnings else "ok",
            data={
                "branch": branch,
                "base_ref": branch,
                "source": source,
                "local_sibling": True,
                "warnings": warnings,
            },
        )

    fetch = run_git(project, "fetch", "origin", branch, timeout=_FETCH_TIMEOUT_S)
    remote_ref = f"origin/{branch}"
    if fetch is not None and fetch.returncode == 0:
        # A successful fetch (rc=0) does NOT guarantee origin/{branch} is a
        # resolvable ref — in shallow/single-branch clones the repo-level
        # remote.origin.fetch refspec may not map this branch at all, so
        # only FETCH_HEAD gets populated (RAISE-15825 F3). Verify before
        # trusting it; a `git worktree add ... origin/{branch}` on an
        # unresolvable ref fails with `fatal: invalid reference`.
        verify = run_git(project, "rev-parse", "--verify", "--quiet", remote_ref)
        if verify is not None and verify.returncode == 0:
            base_ref = remote_ref
        else:
            fetch_head = run_git(
                project, "rev-parse", "--verify", "--quiet", "FETCH_HEAD"
            )
            if fetch_head is not None and fetch_head.returncode == 0:
                warnings.append(
                    f"fetched '{branch}' but '{remote_ref}' was not created "
                    "(shallow/single-branch clone?) — basing on FETCH_HEAD instead"
                )
                base_ref = "FETCH_HEAD"
            else:
                warnings.append(
                    f"fetch succeeded but neither '{remote_ref}' nor FETCH_HEAD "
                    f"resolve — basing on local '{branch}' instead"
                )
                base_ref = branch
    else:
        warnings.append(
            f"could not fetch 'origin/{branch}' — basing on local '{branch}' instead"
        )
        base_ref = branch

    return CheckResult(
        name="worktree_base",
        status="warn" if warnings else "ok",
        data={
            "branch": branch,
            "base_ref": base_ref,
            "source": source,
            "local_sibling": False,
            "warnings": warnings,
        },
    )
