"""Advisory diagnostics for project-scoped backlog workflow configuration."""

from __future__ import annotations

from typing import ClassVar

from raise_cli.adapters.backlog_config import load_backlog_config
from raise_cli.doctor.models import CheckResult, CheckStatus, DoctorContext
from raise_cli.doctor.protocol import DoctorCheck


class BacklogWorkflowScopeCheck(DoctorCheck):
    """Warn when project workflow resolution falls back to unscoped sections."""

    check_id: ClassVar[str] = "backlog-workflow-scope"
    category: ClassVar[str] = "adapters"
    description: ClassVar[str] = "Backlog workflow project-scope diagnostics (advisory)"
    requires_online: ClassVar[bool] = False

    def evaluate(self, context: DoctorContext) -> list[CheckResult]:
        """Return advisory findings without ever failing the doctor run."""
        try:
            config = load_backlog_config(context.working_dir, "jira")
        except Exception as exc:  # noqa: BLE001 — doctor checks never crash
            return [
                CheckResult(
                    check_id=self.check_id,
                    category=self.category,
                    status=CheckStatus.WARN,
                    message=f"backlog workflow scope unavailable: {exc}",
                )
            ]

        results: list[CheckResult] = []
        for project_key, project in config.projects.items():
            if not project.issue_types and config.workflow:
                results.append(
                    CheckResult(
                        check_id=f"{self.check_id}-{project_key.lower()}",
                        category=self.category,
                        status=CheckStatus.WARN,
                        message=(
                            f"project {project_key} has no issue_types; roles resolve "
                            "against the unscoped merge"
                        ),
                        fix_hint=f"rai backlog issue-types discover {project_key}",
                    )
                )
            for issue_type in project.issue_types:
                if (
                    issue_type in config.workflow
                    and issue_type not in config.project_workflow.get(project_key, {})
                ):
                    results.append(
                        CheckResult(
                            check_id=f"{self.check_id}-{project_key.lower()}-{issue_type.lower()}",
                            category=self.category,
                            status=CheckStatus.WARN,
                            message=(
                                f"project {project_key} resolves {issue_type} via "
                                "the unscoped tier"
                            ),
                        )
                    )
        return results or [
            CheckResult(
                check_id=self.check_id,
                category=self.category,
                status=CheckStatus.PASS,
                message="backlog workflow scopes are configured",
            )
        ]
