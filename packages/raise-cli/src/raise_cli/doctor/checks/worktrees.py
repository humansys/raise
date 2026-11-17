"""WorktreesCheck — detects stale worktrees via detect_stale_worktrees() (S17495.5).

Pure delegation: detect_stale_worktrees() has no side effects (AC-1).
Use ``rai worktree prune`` to reap stale worktrees.
"""

from __future__ import annotations

from typing import ClassVar

from raise_cli.doctor.models import CheckResult, CheckStatus, DoctorContext
from raise_cli.doctor.protocol import DoctorCheck

# Imported at module level to allow monkeypatching in tests.
from raise_cli.session.open_service import detect_stale_worktrees
from raise_cli.worktree.idle import find_idle_worktrees, idle_days_from_env

_FIX_HINT = "rai worktree prune"


class WorktreesCheck(DoctorCheck):
    """Detect stale worktrees — pure detection only, never reaps (AC-1).

    Registered via ``rai.doctor.checks`` entry point in pyproject.toml.
    """

    check_id: ClassVar[str] = "worktrees"
    category: ClassVar[str] = "worktrees"
    description: ClassVar[str] = "Stale registered worktrees (no active lease, >48h)"
    requires_online: ClassVar[bool] = False

    def evaluate(self, context: DoctorContext) -> list[CheckResult]:
        """Detect stale and idle worktrees and report; never reap."""
        results = self._evaluate_stale(context)
        self._evaluate_idle(context, results)
        return results

    def _evaluate_idle(
        self, context: DoctorContext, results: list[CheckResult]
    ) -> None:
        """Append ``worktrees-idle``: no commit/session for N days, no live lease."""
        check_id = "worktrees-idle"
        try:
            days = idle_days_from_env()
            idle = find_idle_worktrees(context.working_dir, days)
        except Exception:  # noqa: BLE001 — best-effort, never block doctor
            self._append_result(
                results, check_id, CheckStatus.PASS, "check skipped (error)"
            )
            return
        if not idle:
            self._append_result(
                results, check_id, CheckStatus.PASS, f"no worktrees idle >{days}d"
            )
            return
        names = ", ".join(w.name for w in idle[:10])
        more = f" (+{len(idle) - 10} more)" if len(idle) > 10 else ""
        self._append_result(
            results,
            check_id,
            CheckStatus.WARN,
            f"{len(idle)} worktree(s) idle >{days}d (no commit/session/lease): "
            f"{names}{more}",
            "review, then: git worktree remove <path>",
        )

    def _evaluate_stale(self, context: DoctorContext) -> list[CheckResult]:
        """Detect stale registered worktrees."""
        try:
            result = detect_stale_worktrees(context.working_dir, context.working_dir)
        except Exception:  # noqa: BLE001 — best-effort, never block doctor
            results: list[CheckResult] = []
            self._append_result(
                results, self.check_id, CheckStatus.PASS, "check skipped (error)"
            )
            return results

        stale = result.data.get("stale", [])
        results = []
        if stale:
            self._append_result(
                results,
                self.check_id,
                CheckStatus.WARN,
                f"{len(stale)} stale worktree(s) detected",
                _FIX_HINT,
            )
        else:
            self._append_result(
                results, self.check_id, CheckStatus.PASS, "no stale worktrees"
            )
        return results
