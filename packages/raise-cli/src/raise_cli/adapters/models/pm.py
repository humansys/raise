"""Project Management boundary models.

Typed inputs and outputs for the ``ProjectManagementAdapter`` protocol.

Architecture: ADR-033 (PM adapter)
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# Shared field descriptions
_DESC_ISSUE_TITLE = "Issue title"
_DESC_PARENT_KEY = "Parent issue key"
_DESC_CREATED_TS = "ISO 8601 creation timestamp"
_DESC_UPDATED_TS = "ISO 8601 last update timestamp"


# ── Discovery models (S1130.2) ──────────────────────────────────────


class TransitionInfo(BaseModel):
    """A workflow transition available from a status."""

    model_config = ConfigDict(frozen=True)

    id: str = Field(..., description="Transition numeric ID")
    name: str = Field(..., description="Transition display name")
    to_status: str = Field(..., description="Target status name")


class WorkflowState(BaseModel):
    """A status in a project workflow."""

    model_config = ConfigDict(frozen=True)

    name: str = Field(..., description="Status name (e.g. 'In Progress')")
    status_category: str = Field(..., description="Category: new, indeterminate, done")
    transitions: list[TransitionInfo] = Field(
        ..., description="Transitions available from this status"
    )


class ProjectInfo(BaseModel):
    """Summary of a Jira project for discovery."""

    model_config = ConfigDict(frozen=True)

    key: str = Field(..., description="Project key (e.g. 'RAISE')")
    name: str = Field(..., description="Project display name")
    project_type_key: str = Field(
        ..., description="Project type (e.g. 'software', 'business')"
    )


class IssueTypeInfo(BaseModel):
    """An issue type available in a project."""

    model_config = ConfigDict(frozen=True)

    id: str = Field(..., description="Issue type ID")
    name: str = Field(..., description="Issue type name (e.g. 'Story', 'Bug')")
    subtask: bool = Field(..., description="Whether this is a subtask type")


# ── Issue CRUD models ───────────────────────────────────────────────


class IssueSpec(BaseModel):
    """Specification for creating a PM issue."""

    summary: str = Field(..., description=_DESC_ISSUE_TITLE)
    description: str = Field(default="", description="Issue body (markdown)")
    issue_type: str = Field(default="Task", description="Issue type name")
    labels: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="PM-specific fields"
    )


class IssueRef(BaseModel):
    """Reference to an existing PM issue."""

    key: str = Field(..., description="Issue key (e.g., 'PROJ-123')")
    url: str = Field(default="", description="Web URL to the issue")
    metadata: dict[str, Any] = Field(default_factory=dict)


class IssueDetail(IssueRef):
    """Full issue details — extends IssueRef (inherits key, url, metadata).

    Timestamps use ISO 8601 format (e.g. ``2026-02-27T10:30:00Z``).
    Empty string means timestamp not available.
    """

    summary: str = Field(..., description=_DESC_ISSUE_TITLE)
    description: str = Field(default="", description="Issue body (markdown)")
    status: str = Field(..., description="Current status name")
    issue_type: str = Field(..., description="Issue type (e.g., 'Story', 'Bug')")
    parent_key: str | None = Field(default=None, description=_DESC_PARENT_KEY)
    labels: list[str] = Field(default_factory=list)
    assignee: str | None = Field(default=None, description="Assignee identifier")
    priority: str | None = Field(default=None, description="Priority name")
    created: str = Field(default="", description=_DESC_CREATED_TS)
    updated: str = Field(default="", description=_DESC_UPDATED_TS)


class IssueSummary(BaseModel):
    """Compact issue for search results and listings."""

    key: str = Field(..., description="Issue key (e.g., 'PROJ-123')")
    summary: str = Field(..., description=_DESC_ISSUE_TITLE)
    status: str = Field(..., description="Current status name")
    issue_type: str = Field(..., description="Issue type name")
    parent_key: str | None = Field(default=None, description=_DESC_PARENT_KEY)


class Comment(BaseModel):
    """Issue comment. Timestamps use ISO 8601 format."""

    id: str = Field(..., description="Comment ID")
    body: str = Field(..., description="Comment body (markdown)")
    author: str = Field(..., description="Author identifier")
    created: str = Field(..., description=_DESC_CREATED_TS)


class CommentRef(BaseModel):
    """Reference to a created comment."""

    id: str = Field(..., description="Comment ID")
    url: str = Field(default="", description="Web URL to the comment")


class FailureDetail(BaseModel):
    """A single failure in a batch operation."""

    key: str = Field(..., description="Issue key that failed")
    error: str = Field(..., description="Error description")


class BatchResult(BaseModel):
    """Result of a batch operation."""

    succeeded: list[IssueRef] = Field(default_factory=lambda: list[IssueRef]())
    failed: list[FailureDetail] = Field(default_factory=lambda: list[FailureDetail]())
