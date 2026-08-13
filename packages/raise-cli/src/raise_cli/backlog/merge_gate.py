"""Terminal-transition merge gate — RAISE-15769.

Stream FEI transitioned 7 bugs to Done while the fixing code sat on the
local, unmerged branch `fix/rc1-stream-fei`, diverging the tracker from
git reality. `raise_backlog_transition` (mcp_tools_backlog.py) had no gate
distinguishing "commit exists" from "commit merged" for terminal
transitions — the brief said "transition when fixed" without drawing that
line, and nothing in code caught it.

`check_merge_gate` closes that gap for Done/Closed transitions: it resolves
the issue's registered worktree (`SqliteWorktreeStore.find_by_story`, the
live story->worktree binding established by RAISE-15764 D2.a) and checks
commit-reachability (`check_branch_landed`, below) to confirm the branch's
tip actually landed in its `merge_target` before a terminal transition is
allowed through.

This gate does NOT reuse `is_branch_merged` (RAISE-11104, `rai worktree
prune`'s safety check) — that function runs `git branch --merged` and
returns `False` on any failure or absence, which is the *safe* direction
for prune's question ("is it safe to delete this branch?": False = don't
delete) but the *unsafe* direction for this gate's question ("is it safe
to mark Done?": False = block). Reusing it here produced false hard-blocks
on legitimate merges (RAISE-15855 C1):
  - squash-merged branches never appear in `git branch --merged` output
    (prune.py's own docstring admits this) — a GitLab squash-merge
    permanently blocked Done.
  - a branch deleted after merge (this project's own convention: "Delete
    Branches After Merge immediately") is absent from `--merged` output —
    false block on a legitimately-shipped fix.
  - a stale/absent local `merge_target` ref (merged via MR on origin,
    local release branch never fetched) also false-blocked right after a
    real merge.

`check_branch_landed` instead asks "is the branch tip a commit-graph
ancestor of the merge target?" via `git merge-base --is-ancestor`, checked
against `origin/<merge_target>` first (fetched remote state) and the local
`<merge_target>` as fallback. It also treats a branch that no longer
exists locally as landed (not blocked): per this project's convention,
branches are deleted immediately after merge, so absence is the expected
post-merge, post-cleanup state — not evidence of an unmerged fix. Squash
merges land the (squashed) commit on the target directly, so this check
still confirms them positively once `origin/<merge_target>` is fetched;
only a genuinely unmerged branch that still exists locally blocks.

Fail-open posture (RAISE-10966): a guard that cannot prove non-merge must
not block. This gate blocks ONLY on positive evidence — exactly one
registered worktree whose branch is confirmably unmerged (git successfully
determined "not an ancestor", not merely "the check failed to run"). Every
other case (non-terminal transition, no worktree registered, 2+ worktrees
claiming the same story, an indeterminate merge check, or any lookup/git
error) allows the transition through — but see `MergeGateResult.advisory`
(RAISE-15855 C2): fail-open here means "not blocked", not "silent". Any
path where merge state could not be positively verified carries an
advisory note instead of vanishing without a trace.
"""

from __future__ import annotations

import logging
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from raise_cli.storage.worktrees import SqliteWorktreeStore

_log = logging.getLogger(__name__)

TERMINAL_STATUSES = frozenset({"done", "closed"})


def is_terminal_status(status: str) -> bool:
    """True if `status` names a terminal state (Done, Closed) — case-insensitive."""
    return status.strip().lower() in TERMINAL_STATUSES


class MergeCheck(Enum):
    """Outcome of `check_branch_landed` — see that function's docstring."""

    LANDED = "landed"
    NOT_LANDED = "not_landed"
    INDETERMINATE = "indeterminate"


def _run_git(args: list[str], repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def _ref_resolves(repo: Path, ref: str) -> bool:
    """True if `ref` (branch, remote-tracking branch, ...) resolves to a commit."""
    return _run_git(["rev-parse", "--verify", "--quiet", ref], repo).returncode == 0


def _resolve_target_ref(repo: Path, merge_target: str) -> str | None:
    """Prefer `origin/<merge_target>` (fetched remote state); fall back to local.

    Returns None if neither resolves — e.g. the local checkout never
    fetched `origin` and no local branch of that name exists either.
    """
    origin_ref = f"origin/{merge_target}"
    if _ref_resolves(repo, origin_ref):
        return origin_ref
    if _ref_resolves(repo, merge_target):
        return merge_target
    return None


def check_branch_landed(
    repo: Path, branch: str, merge_target: str
) -> tuple[MergeCheck, str]:
    """Positive-evidence check: has `branch` landed in `merge_target`'s history?

    Uses `git merge-base --is-ancestor <branch-tip> <target-ref>` — commit
    reachability, not `git branch --merged` — so squash-merges (which land
    a new commit on the target rather than replaying the branch's commits)
    are confirmed correctly once `origin/<merge_target>` carries them.

    Three outcomes, deliberately not collapsed into a bool (that collapse
    is exactly RAISE-15855 C1's bug):
      - LANDED: positive evidence the branch is merged, OR the branch no
        longer exists locally (deleted-after-merge is this project's own
        convention — treated as landed, not as "can't check so allow").
      - NOT_LANDED: `git merge-base --is-ancestor` ran successfully and
        determined the branch tip is NOT an ancestor of the target — a
        real block signal.
      - INDETERMINATE: the check itself could not run to a conclusion
        (neither `origin/<merge_target>` nor `<merge_target>` resolves,
        the branch tip can't be resolved, or the git command errored for
        a reason other than "not an ancestor") — no evidence either way.
    """
    if not _ref_resolves(repo, f"refs/heads/{branch}"):
        return (
            MergeCheck.LANDED,
            f"branch '{branch}' no longer exists locally — treated as "
            "merged-and-cleaned-up per project convention (branches are "
            "deleted immediately after merge)",
        )

    target_ref = _resolve_target_ref(repo, merge_target)
    if target_ref is None:
        return (
            MergeCheck.INDETERMINATE,
            f"neither 'origin/{merge_target}' nor '{merge_target}' resolves "
            "to a commit — cannot verify merge state",
        )

    branch_sha_result = _run_git(["rev-parse", "--verify", "--quiet", branch], repo)
    if branch_sha_result.returncode != 0:
        return (
            MergeCheck.INDETERMINATE,
            f"could not resolve '{branch}' to a commit",
        )
    branch_sha = branch_sha_result.stdout.strip()

    result = _run_git(["merge-base", "--is-ancestor", branch_sha, target_ref], repo)
    if result.returncode == 0:
        return MergeCheck.LANDED, f"'{branch}' is an ancestor of '{target_ref}'"
    if result.returncode == 1:
        return (
            MergeCheck.NOT_LANDED,
            f"'{branch}' is NOT an ancestor of '{target_ref}'",
        )
    # Any other exit code means the command itself failed to run to a
    # conclusion (bad revision, git internal error, ...) — not evidence.
    return (
        MergeCheck.INDETERMINATE,
        f"'git merge-base --is-ancestor' failed (exit {result.returncode}): "
        f"{result.stderr.strip()}",
    )


@dataclass(frozen=True)
class MergeGateResult:
    """Outcome of a terminal-transition merge check.

    `allowed=False` only when the gate found positive evidence of an
    unmerged branch for a terminal transition — see module docstring for
    the fail-open posture on every other path.

    `advisory` is set (non-None) whenever `allowed=True` but merge state
    could NOT be positively verified — no worktree binding, an ambiguous
    binding, or an indeterminate git check (RAISE-15855 C2). It is None
    when the transition is non-terminal (gate inapplicable), when merge
    state WAS positively confirmed, or when the transition is blocked.
    Callers surface this in their response so a fail-open outcome is never
    silent.
    """

    allowed: bool
    reason: str
    advisory: str | None = None


def check_merge_gate(issue_key: str, status: str, cwd: str) -> MergeGateResult:
    """Guard terminal transitions (Done, Closed) on merge state (RAISE-15769).

    Non-terminal transitions are always allowed — no gate applies.

    For terminal transitions, resolves the story's registered worktree via
    `SqliteWorktreeStore.find_by_story` and checks commit-reachability
    (`check_branch_landed`) against its registered `merge_target`.
    Fail-open (`allowed=True`) when the story->worktree binding can't be
    resolved unambiguously, or when any lookup raises or the git check is
    indeterminate — mirrors the RAISE-10966 invariant that guard errors
    never block CLI/MCP flows. Every fail-open path carries a non-None
    `advisory` (RAISE-15855 C2) so the caller can surface it instead of the
    outcome vanishing silently. Blocks only when exactly one worktree is
    registered for `issue_key` and `check_branch_landed` positively
    determines its branch is NOT an ancestor of `merge_target`.
    """
    if not is_terminal_status(status):
        return MergeGateResult(
            allowed=True, reason="non-terminal transition — no merge gate"
        )

    project = Path(cwd) if cwd else Path.cwd()

    try:
        store = SqliteWorktreeStore(project)
        matches = store.find_by_story(issue_key)
    except Exception as exc:  # noqa: BLE001 — fail-open, guard errors never block (RAISE-10966)
        _log.debug(
            "merge gate: worktree lookup failed for %s — fail-open",
            issue_key,
            exc_info=True,
        )
        reason = f"merge gate unavailable ({exc}) — allowing transition (fail-open)"
        return MergeGateResult(allowed=True, reason=reason, advisory=reason)

    if not matches:
        reason = (
            f"merge state unverified — no worktree binding found for "
            f"{issue_key}; verify manually before transitioning to '{status}'"
        )
        return MergeGateResult(allowed=True, reason=reason, advisory=reason)
    if len(matches) > 1:
        reason = (
            f"merge state unverified — {len(matches)} open worktrees claim "
            f"{issue_key} (ambiguous); verify manually before transitioning "
            f"to '{status}'"
        )
        return MergeGateResult(allowed=True, reason=reason, advisory=reason)

    try:
        wt = store.get_by_path(matches[0])
        outcome, detail = check_branch_landed(project, wt.branch, wt.merge_target)
    except Exception as exc:  # noqa: BLE001 — fail-open, guard errors never block (RAISE-10966)
        _log.debug(
            "merge gate: merge check failed for %s — fail-open",
            issue_key,
            exc_info=True,
        )
        reason = f"merge check failed ({exc}) — allowing transition (fail-open)"
        return MergeGateResult(allowed=True, reason=reason, advisory=reason)

    if outcome is MergeCheck.LANDED:
        return MergeGateResult(
            allowed=True,
            reason=f"branch '{wt.branch}' confirmed merged into '{wt.merge_target}' ({detail})",
        )
    if outcome is MergeCheck.INDETERMINATE:
        reason = (
            f"merge state unverified for '{wt.branch}' -> '{wt.merge_target}' "
            f"({detail}); verify manually before transitioning to '{status}'"
        )
        return MergeGateResult(allowed=True, reason=reason, advisory=reason)
    return MergeGateResult(
        allowed=False,
        reason=(
            f"branch '{wt.branch}' is NOT merged into '{wt.merge_target}' — "
            f"{issue_key} cannot transition to '{status}' until the fix is "
            f"merged ({detail}) (RAISE-15769)"
        ),
    )
