"""Tests for Jira discovery service — S1130.2."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

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
