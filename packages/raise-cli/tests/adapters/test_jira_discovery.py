"""Tests for Jira discovery service — S1130.2."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from raise_cli.adapters.jira_client import JiraClient
from raise_cli.adapters.jira_exceptions import JiraAuthError
from raise_cli.adapters.models.pm import (
    IssueTypeInfo,
    ProjectInfo,
    TransitionInfo,
    WorkflowState,
)

# ── T1: Discovery models ────────────────────────────────────────────


class TestProjectInfo:
    def test_fields(self) -> None:
        p = ProjectInfo(key="RAISE", name="RaiSE", project_type_key="software")
        assert p.key == "RAISE"
        assert p.name == "RaiSE"
        assert p.project_type_key == "software"

    def test_frozen(self) -> None:
        p = ProjectInfo(key="RAISE", name="RaiSE", project_type_key="software")
        with pytest.raises(ValidationError):
            p.key = "OTHER"  # type: ignore[misc]


class TestWorkflowState:
    def test_fields_with_transitions(self) -> None:
        t = TransitionInfo(id="31", name="Done", to_status="Done")
        ws = WorkflowState(
            name="In Progress",
            status_category="indeterminate",
            transitions=[t],
        )
        assert ws.name == "In Progress"
        assert ws.status_category == "indeterminate"
        assert len(ws.transitions) == 1
        assert ws.transitions[0].id == "31"
        assert ws.transitions[0].to_status == "Done"

    def test_frozen(self) -> None:
        ws = WorkflowState(name="To Do", status_category="new", transitions=[])
        with pytest.raises(ValidationError):
            ws.name = "Other"  # type: ignore[misc]


class TestIssueTypeInfo:
    def test_fields(self) -> None:
        it = IssueTypeInfo(id="10001", name="Story", subtask=False)
        assert it.id == "10001"
        assert it.name == "Story"
        assert it.subtask is False

    def test_subtask_flag(self) -> None:
        it = IssueTypeInfo(id="10003", name="Sub-task", subtask=True)
        assert it.subtask is True

    def test_frozen(self) -> None:
        it = IssueTypeInfo(id="10001", name="Story", subtask=False)
        with pytest.raises(ValidationError):
            it.name = "Bug"  # type: ignore[misc]


# ── T2: JiraClient discovery methods ────────────────────────────────

# Raw API response fixtures matching atlassian-python-api shapes

RAW_PROJECTS: list[dict[str, Any]] = [
    {"key": "RAISE", "name": "RaiSE", "projectTypeKey": "software"},
    {"key": "OPS", "name": "Operations", "projectTypeKey": "business"},
]

# get_status_for_project returns list of dicts grouped by issue type
RAW_STATUSES: list[dict[str, Any]] = [
    {
        "name": "Story",
        "statuses": [
            {"name": "To Do", "statusCategory": {"key": "new"}},
            {"name": "In Progress", "statusCategory": {"key": "indeterminate"}},
            {"name": "Done", "statusCategory": {"key": "done"}},
        ],
    },
    {
        "name": "Bug",
        "statuses": [
            {"name": "To Do", "statusCategory": {"key": "new"}},
            {"name": "Done", "statusCategory": {"key": "done"}},
        ],
    },
]

# issue_createmeta_issuetypes returns paginated response
RAW_ISSUE_TYPES: dict[str, Any] = {
    "values": [
        {"id": "10001", "name": "Story", "subtask": False},
        {"id": "10002", "name": "Bug", "subtask": False},
        {"id": "10003", "name": "Sub-task", "subtask": True},
    ],
}


def _make_client() -> JiraClient:
    """Create a JiraClient with mocked atlassian.Jira."""
    with patch("atlassian.Jira") as mock_jira_cls:
        mock_jira = MagicMock()
        mock_jira_cls.return_value = mock_jira
        client = JiraClient(url="https://test.atlassian.net", username="u", token="t")
    return client


class TestJiraClientListProjects:
    def test_returns_project_info_list(self) -> None:
        client = _make_client()
        client._client.projects.return_value = RAW_PROJECTS  # noqa: SLF001
        result = client.list_projects()
        assert len(result) == 2
        assert isinstance(result[0], ProjectInfo)
        assert result[0].key == "RAISE"
        assert result[1].project_type_key == "business"

    def test_auth_error_propagated(self) -> None:
        from atlassian.errors import ApiPermissionError

        client = _make_client()
        client._client.projects.side_effect = ApiPermissionError("Forbidden")  # noqa: SLF001
        with pytest.raises(JiraAuthError):
            client.list_projects()


class TestJiraClientGetProjectWorkflows:
    def test_returns_unique_workflow_states(self) -> None:
        client = _make_client()
        client._client.get_status_for_project.return_value = RAW_STATUSES  # noqa: SLF001
        result = client.get_project_workflows("RAISE")
        # Should deduplicate: To Do, In Progress, Done (3 unique)
        assert len(result) == 3
        names = {s.name for s in result}
        assert names == {"To Do", "In Progress", "Done"}
        # Verify status categories
        done = next(s for s in result if s.name == "Done")
        assert done.status_category == "done"

    def test_calls_with_project_key(self) -> None:
        """Contract: verify correct parameter passed to API (PAT from S1130.1 QR)."""
        client = _make_client()
        client._client.get_status_for_project.return_value = []  # noqa: SLF001
        client.get_project_workflows("RAISE")
        client._client.get_status_for_project.assert_called_once_with("RAISE")  # noqa: SLF001


class TestJiraClientGetIssueTypes:
    def test_returns_issue_type_list(self) -> None:
        client = _make_client()
        client._client.issue_createmeta_issuetypes.return_value = RAW_ISSUE_TYPES  # noqa: SLF001
        result = client.get_issue_types("RAISE")
        assert len(result) == 3
        assert isinstance(result[0], IssueTypeInfo)
        assert result[0].name == "Story"
        assert result[2].subtask is True

    def test_calls_with_project_key(self) -> None:
        """Contract: verify correct parameter passed to API."""
        client = _make_client()
        client._client.issue_createmeta_issuetypes.return_value = RAW_ISSUE_TYPES  # noqa: SLF001
        client.get_issue_types("RAISE")
        client._client.issue_createmeta_issuetypes.assert_called_once_with("RAISE")  # noqa: SLF001
