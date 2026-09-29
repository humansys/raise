"""RevertScopeGate — advisory diffstat check for RAISE-17599.

RAISE-17598 (2026-09-16): a `git revert` of a legitimate merge commit
(d01153d5f2, adding a small, self-contained change) landed on release/3.2.0
via a governed MR and destroyed +9748/-171918 across 1075 files — concurrent
work from other sessions merged into the same branch between the target
commit and the revert. The diagnosis was correct (the target commit landed
on the wrong release line); the correction tool was disproportionate (a
full merge-commit revert instead of a surgical fix).

This gate detects a `git revert`-of-merge-commit in the candidate branch
(the standard `This reverts commit <sha>` message marker) and compares its
own net diffstat against the target commit's diffstat (relative to its
first parent — `git diff --stat {commit}^1 {commit}`, the ticket's own
formula). It never hard-blocks — `git revert` remains a legitimate tool,
and release/* permissions are already correct (RAISE-17599 out-of-scope
note) — it only sets `GateResult.advisory=True` (an existing field, reused
here, not reinvented) with an explicit warning when the revert's scope
significantly exceeds the target's, the signal that concurrent work got
swept up.
"""

from __future__ import annotations

import re
import subprocess
from typing import ClassVar

from raise_cli.gates.models import GateContext, GateResult
from raise_cli.storage.worktrees import SqliteWorktreeStore, WorktreeNotFoundError

# Standard `git revert` message marker (git's own generated text).
_REVERTS_RE = re.compile(r"This reverts commit ([0-9a-f]{7,40})")

# A revert is flagged disproportionate when its net diffstat exceeds the
# target commit's by both a ratio and an absolute floor — the floor avoids
# noise on trivially small commits where any ratio is meaningless.
_RATIO_THRESHOLD = 3
_ABSOLUTE_FLOOR = 20


def _run_git(args: list[str], cwd: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )  # noqa: S603, S607
    return result.stdout if result.returncode == 0 else ""


def _revert_commits_in_range(
    merge_target: str, working_dir: str
) -> list[tuple[str, str]]:
    """Return (revert_sha, target_sha) pairs found in `{merge_target}..HEAD`."""
    log_output = _run_git(
        [
            "log",
            f"{merge_target}..HEAD",
            "--grep=This reverts commit",
            "--format=%H%n%B%x00",
        ],
        working_dir,
    )
    pairs: list[tuple[str, str]] = []
    for entry in log_output.split("\x00"):
        entry = entry.strip("\n")
        if not entry:
            continue
        lines = entry.split("\n", 1)
        if len(lines) < 2:
            continue
        revert_sha, message = lines[0], lines[1]
        match = _REVERTS_RE.search(message)
        if match:
            pairs.append((revert_sha, match.group(1)))
    return pairs


def _net_diffstat(sha: str, working_dir: str) -> int:
    """Return total added+deleted lines for `sha` against its first parent."""
    numstat = _run_git(["diff", "--numstat", f"{sha}^1", sha], working_dir)
    total = 0
    for line in numstat.splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        added, deleted = parts[0], parts[1]
        if added.isdigit():
            total += int(added)
        if deleted.isdigit():
            total += int(deleted)
    return total


class RevertScopeGate:
    """Advisory gate: warns when a revert-of-merge-commit exceeds its target's scope.

    Registered via ``rai.gates`` entry point in pyproject.toml.
    """

    gate_id: ClassVar[str] = "gate-revert-scope"
    description: ClassVar[str] = (
        "Advisory: warns when a git-revert of a merge commit significantly "
        "exceeds the diffstat of the commit it targets (RAISE-17599)"
    )
    workflow_point: ClassVar[str] = "before:mr:create"
    # Deliberately never hard-blocks — git revert is a legitimate tool
    # (RAISE-17599 out-of-scope note). Do not "fix" this into True.
    is_blocker: ClassVar[bool] = False

    def evaluate(self, context: GateContext) -> GateResult:
        """Compare revert diffstat against target diffstat for the candidate branch."""
        working_dir = str(context.working_dir)
        try:
            worktree = SqliteWorktreeStore(context.working_dir).get_by_path(working_dir)
        except (WorktreeNotFoundError, OSError):
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="no registered worktree — nothing to check",
                skipped=True,
            )

        pairs = _revert_commits_in_range(worktree.merge_target, working_dir)
        if not pairs:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="no revert-of-merge-commit found in candidate range",
            )

        warnings: list[str] = []
        pair_labels: list[str] = []
        for revert_sha, target_sha in pairs:
            revert_magnitude = _net_diffstat(revert_sha, working_dir)
            target_magnitude = _net_diffstat(target_sha, working_dir)
            disproportionate = (
                revert_magnitude > _RATIO_THRESHOLD * target_magnitude
                and (revert_magnitude - target_magnitude) > _ABSOLUTE_FLOOR
            )
            if disproportionate:
                label = f"{revert_sha[:8]} reverts {target_sha[:8]}"
                pair_labels.append(label)
                warnings.append(
                    f"{label}: {revert_magnitude} lines changed vs "
                    f"{target_magnitude} in the target — disproportionate, "
                    "review before merging (RAISE-17599)"
                )

        if not warnings:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="revert(s) found, diffstat proportional to target(s)",
            )

        return GateResult(
            passed=True,
            gate_id=self.gate_id,
            message=(
                f"{len(warnings)} disproportionate revert(s) found "
                f"({', '.join(pair_labels)}) — human confirmation recommended"
            ),
            details=tuple(warnings),
            advisory=True,
        )
