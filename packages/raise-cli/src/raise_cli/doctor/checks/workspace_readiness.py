"""Workspace readiness doctor check — delegates to shared evaluator.

S14897.6 / RAISE-14906 — part of the cross-surface parity story.

Ensures the doctor surface rejects exactly the workspace states that
``evaluate_workspace_readiness()`` rejects, with no independent definition
of readiness.  Uses the same policy as ``rai worktree register`` (the git
worktree policy).
"""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from raise_cli.doctor.models import CheckResult, CheckStatus, DoctorContext
from raise_cli.doctor.protocol import DoctorCheck


class WorkspaceReadinessCheck(DoctorCheck):
    """Doctor check: workspace readiness via shared evaluator (git worktree policy).

    Delegates to ``evaluate_workspace_readiness()`` with
    ``git_worktree_readiness_policy()`` so the doctor surface agrees with
    ``rai worktree register`` and ``_maybe_provision`` — no independent
    readiness heuristic.

    Advisory findings are omitted from doctor output: they are informational
    only and should not inflate the doctor ERROR count.
    """

    check_id: ClassVar[str] = "workspace"
    category: ClassVar[str] = "workspace"
    description: ClassVar[str] = (
        "Workspace readiness via shared evaluator (git worktree policy)"
    )
    requires_online: ClassVar[bool] = False

    def evaluate(self, context: DoctorContext) -> list[CheckResult]:
        """Evaluate workspace readiness at ``context.working_dir``.

        Returns:
            A single PASS result when the workspace is ready, or one ERROR
            result per required finding when it is not.
        """
        # Deferred imports keep module-level load fast and break the import
        # cycle: workspace_readiness → worktree.provision → workspace.readiness.
        from raise_cli.workspace.readiness import evaluate_workspace_readiness
        from raise_cli.worktree.provision import git_worktree_readiness_policy

        path: Path = context.working_dir
        policy = git_worktree_readiness_policy()
        report = evaluate_workspace_readiness(path, policy)

        results: list[CheckResult] = []
        if report.is_ready:
            self._append_result(
                results,
                "workspace-ready",
                CheckStatus.PASS,
                f"workspace at {path} is ready",
            )
        else:
            for finding in report.required_findings:
                self._append_result(
                    results,
                    f"workspace-{finding.code}",
                    CheckStatus.ERROR,
                    finding.message,
                    fix_hint=(
                        "Run 'rai worktree register' to re-provision the workspace."
                    ),
                )
        return results
