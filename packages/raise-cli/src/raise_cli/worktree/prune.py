"""Safety checks for `rai worktree prune` — RAISE-11104.

A worktree is only pruned when a conjunction of independent checks all
pass. Each check is conservative: on doubt, it reports "unsafe" rather than
risk data loss. See `evaluate_candidate` for the combined decision.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from raise_cli.storage.leases import SqliteLeaseStore, pid_alive
from raise_cli.storage.worktrees import Worktree


def is_branch_merged(repo: Path, branch: str, merge_target: str) -> bool:
    """True if `branch` is reachable from `merge_target` (`git branch --merged`).

    Squash/rebase-merged branches will NOT appear here — that is a safe
    false-negative (the candidate is skipped, never over-pruned).
    """
    result = subprocess.run(
        ["git", "-C", str(repo), "branch", "--merged", merge_target],
        capture_output=True,
        text=True,
        check=False,
    )
    # git prefixes the current branch with "*" and, when the repo has linked
    # worktrees, any branch checked out in another worktree with "+" — both
    # markers must be stripped or a merged-but-checked-out-elsewhere branch
    # (the exact case a prune candidate is in) is missed.
    merged_names = {
        line.strip().lstrip("*+").strip() for line in result.stdout.splitlines()
    }
    return branch in merged_names


def merge_target_confirmed(wt: Worktree, merge_target_checked: str) -> bool:
    """True if `merge_target_checked` is exactly the worktree's registered value.

    Invariant assertion, not an external safety condition — guards against a
    hardcoded/global-fallback regression where a caller evaluates a
    worktree's merge status against the wrong `merge_target` (e.g. one
    worktree merges into `main`, another into `release/3.1.0`; a caller
    passing a fixed default for both would produce false positives).
    """
    return merge_target_checked == wt.merge_target


def is_working_tree_clean(worktree_path: Path) -> bool:
    """True only when `git status --short` reports nothing at all.

    Untracked files (`??`) count as dirty — a conservative skip, since an
    untracked-but-important file would otherwise be lost silently.
    """
    result = subprocess.run(
        ["git", "-C", str(worktree_path), "status", "--short"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() == ""


def has_unpushed_commits(repo: Path, branch: str) -> bool:
    """True if `branch` has commits its upstream doesn't, or has no upstream.

    No upstream configured is treated as unsafe (`True`) — we cannot verify
    the branch was pushed, matching the "skip on doubt" posture used
    throughout these checks.
    """
    upstream = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "--abbrev-ref", f"{branch}@{{u}}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if upstream.returncode != 0:
        return True

    count = subprocess.run(
        ["git", "-C", str(repo), "rev-list", "--count", f"{branch}@{{u}}..{branch}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if count.returncode != 0:
        return True
    return count.stdout.strip() != "0"


def has_stash_entries(worktree_path: Path) -> bool:
    """True if `git stash list` reports any entries.

    An otherwise-clean tree (per `is_working_tree_clean`) can still have
    stashed work — `git status --short` does not surface it. Treating a
    stash as unsafe-to-prune is the conservative direction: pruning a
    worktree with a stash would silently lose that work.
    """
    result = subprocess.run(
        ["git", "-C", str(worktree_path), "stash", "list"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() != ""


def has_active_lease(worktree_id: str, project: Path) -> bool:
    """True if a live session currently holds the lease for `worktree_id`.

    All 6 other checks are git-state snapshots — none of them detect a
    developer or agent mid-conversation in the worktree with nothing
    committed yet. A lease with a live PID means someone is actively using
    the worktree right now, regardless of how clean its git state looks.

    No lease at all, or a lease whose PID is no longer alive (crashed/killed
    session, never released), is treated as "no active use" — conservative
    in the other direction: we don't want a stale DB row to permanently
    block a genuinely abandoned worktree from ever being pruned.
    """
    lease = SqliteLeaseStore(project).get(worktree_id)
    if lease is None:
        return False
    return pid_alive(lease.pid)


@dataclass
class PruneDecision:
    """Outcome of `evaluate_candidate`: safe to prune, and why not if not."""

    safe: bool
    reasons: list[str] = field(default_factory=list)


def evaluate_candidate(
    wt: Worktree,
    *,
    repo: Path,
    current_path: Path | None = None,
) -> PruneDecision:
    """Combine all safety checks into one conjunction: safe only if ALL pass.

    Any failing check appends its specific reason — a candidate is never
    silently dropped. Checks:
      1. branch is merged into its registered merge_target
      2. that merge_target check used wt.merge_target (not a stale/global one)
      3. working tree is clean (no uncommitted changes, including untracked)
      4. no stashed changes (git stash list is empty)
      5. no unpushed commits (and an upstream is actually configured)
      6. this is not the worktree the command is currently running from
      7. no live session currently holds an active lease on this worktree
    """
    reasons: list[str] = []
    wt_path = Path(wt.path)
    current = (current_path if current_path is not None else Path.cwd()).resolve()

    if wt_path.resolve() == current:
        reasons.append(
            "is the worktree currently running this command (self) — cannot prune"
        )

    merge_target_used = wt.merge_target
    if not merge_target_confirmed(wt, merge_target_used):
        reasons.append(
            "merge_target consistency check failed — evaluated against a "
            "value other than wt.merge_target"
        )
    elif not is_branch_merged(repo, wt.branch, merge_target_used):
        reasons.append(f"branch '{wt.branch}' is not merged into '{merge_target_used}'")

    if not is_working_tree_clean(wt_path):
        reasons.append("working tree has uncommitted changes")

    if has_stash_entries(wt_path):
        reasons.append("worktree has stashed changes (git stash list is non-empty)")

    if has_unpushed_commits(repo, wt.branch):
        reasons.append(
            f"branch '{wt.branch}' has unpushed commits or no upstream configured"
        )

    if has_active_lease(wt.worktree_id, repo):
        lease = SqliteLeaseStore(repo).get(wt.worktree_id)
        pid = lease.pid if lease is not None else "?"
        reasons.append(
            f"worktree has an active session lease (pid {pid} still "
            "running) — cannot prune"
        )

    return PruneDecision(safe=not reasons, reasons=reasons)
