"""Jira discovery service — structured project, workflow, and issue type queries.

Internal service consumed by doctor and config generator (D1: not a CLI command).
Wraps JiraClient discovery methods into a structured JiraProjectMap.

RAISE-1130 (S1130.2)
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from raise_cli.adapters.jira_exceptions import JiraNotFoundError
from raise_cli.adapters.models.pm import IssueTypeInfo, ProjectInfo, WorkflowState

if TYPE_CHECKING:
    from raise_cli.adapters.jira_client import JiraClient

logger = logging.getLogger(__name__)


class JiraProjectMap(BaseModel):
    """Discovered Jira project structure."""

    model_config = ConfigDict(frozen=True)

    projects: list[ProjectInfo] = Field(..., description="Discovered projects")
    workflows: dict[str, list[WorkflowState]] = Field(
        ...,
        description="Project key → workflow states",
    )
    issue_types: dict[str, list[IssueTypeInfo]] = Field(
        ...,
        description="Project key → available issue types",
    )


class JiraDiscovery:
    """Queries a Jira instance for project, workflow, and issue type structure.

    Consumed by AdapterDoctorCheck and config generator — not user-facing.
    """

    def __init__(self, client: JiraClient) -> None:
        self._client = client

    def discover(self, project_key: str | None = None) -> JiraProjectMap:
        """Discover projects and their workflows/issue types.

        Args:
            project_key: If provided, filter to this project only.
                         Raises JiraNotFoundError if not found.

        Returns:
            JiraProjectMap with projects, workflows, and issue types.
        """
        all_projects: list[ProjectInfo] = self._client.list_projects()

        if project_key is not None:
            matched = [p for p in all_projects if p.key == project_key]
            if not matched:
                raise JiraNotFoundError(
                    f"Project '{project_key}' not found. "
                    f"Available: {', '.join(p.key for p in all_projects)}"
                )
            projects = matched
        else:
            projects = all_projects

        workflows: dict[str, list[WorkflowState]] = {}
        issue_types: dict[str, list[IssueTypeInfo]] = {}

        for project in projects:
            # Workflows — best-effort per project
            try:
                workflows[project.key] = self._client.get_project_workflows(project.key)
            except Exception:  # noqa: BLE001 — discovery is best-effort per project
                logger.debug(
                    "Failed to get workflows for project %s",
                    project.key,
                    exc_info=True,
                )
                workflows[project.key] = []

            # Issue types — best-effort per project
            try:
                issue_types[project.key] = self._client.get_issue_types(project.key)
            except Exception:  # noqa: BLE001 — discovery is best-effort per project
                logger.debug(
                    "Failed to get issue types for project %s",
                    project.key,
                    exc_info=True,
                )
                issue_types[project.key] = []

        return JiraProjectMap(
            projects=projects,
            workflows=workflows,
            issue_types=issue_types,
        )
