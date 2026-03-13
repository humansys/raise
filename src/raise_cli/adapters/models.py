"""Pydantic models for adapter boundaries.

Shared data types consumed by adapter Protocols. These models define
the contracts at integration boundaries — what goes in and comes out
of adapters regardless of their concrete implementation.

Architecture: ADR-033 (Open-core adapter architecture), ADR-034 (Governance extensibility)
"""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

# Shared Field descriptions (S1192)
_DESC_ISSUE_TITLE = "Issue title"
_DESC_PARENT_KEY = "Parent issue key"
_DESC_CREATED_TS = "ISO 8601 creation timestamp"
_DESC_UPDATED_TS = "ISO 8601 last update timestamp"


class CoreArtifactType(StrEnum):
    """Core governance artifact types.

    Protocols accept ``str`` — plugins are not restricted to this enum.
    Use these constants for built-in artifact types.
    """

    BACKLOG = "backlog"
    ADR = "adr"
    CONSTITUTION = "constitution"
    PRD = "prd"
    VISION = "vision"
    GUARDRAILS = "guardrails"
    GLOSSARY = "glossary"
    ROADMAP = "roadmap"
    EPIC_SCOPE = "epic_scope"


class ArtifactLocator(BaseModel):
    """Points to a governance artifact for parsing."""

    path: str = Field(..., description="Relative path from project root")
    artifact_type: str = Field(
        ..., description="Artifact type (CoreArtifactType or custom str)"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Type-specific context"
    )


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


class PublishResult(BaseModel):
    """Result of publishing documentation."""

    success: bool = Field(..., description="Whether publish succeeded")
    url: str = Field(default="", description="URL of published content")
    message: str = Field(default="", description="Status or error message")


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


class PageContent(BaseModel):
    """Full page content from documentation target."""

    id: str = Field(..., description="Page ID")
    title: str = Field(..., description="Page title")
    content: str = Field(..., description="Page content (markdown)")
    url: str = Field(default="", description="Web URL to the page")
    space_key: str = Field(default="", description="Space key (e.g., 'DEV')")
    version: int = Field(default=1, description="Page version number")


class PageSummary(BaseModel):
    """Compact page for search results. Timestamps use ISO 8601 format."""

    id: str = Field(..., description="Page ID")
    title: str = Field(..., description="Page title")
    url: str = Field(default="", description="Web URL to the page")
    space_key: str = Field(default="", description="Space key")
    updated: str = Field(default="", description=_DESC_UPDATED_TS)


class AdapterHealth(BaseModel):
    """Health check result for an adapter."""

    name: str = Field(..., description="Adapter name (e.g., 'jira')")
    healthy: bool = Field(..., description="Whether the adapter is healthy")
    message: str = Field(default="", description="Status or error message")
    latency_ms: int | None = Field(
        default=None, description="Response latency in milliseconds"
    )


# ---------------------------------------------------------------------------
# YAML store models (S347.2 — FileAdapter parity)
# ---------------------------------------------------------------------------


class BacklogLink(BaseModel):
    """Link from one backlog item to another."""

    target: str = Field(..., description="Target issue key")
    link_type: str = Field(
        ..., description="Relationship type (blocks, depends_on, relates_to)"
    )


class BacklogComment(BaseModel):
    """Comment embedded in a backlog item YAML file."""

    id: str = Field(..., description="Comment ID ({KEY}-{N})")
    body: str = Field(..., description="Comment body text")
    author: str = Field(..., description="Author identifier")
    created: str = Field(..., description=_DESC_CREATED_TS)


class BacklogItem(BaseModel):
    """Single backlog item stored as .raise/backlog/items/{KEY}.yaml."""

    key: str = Field(..., description="Issue key (E1, S1.1, etc.)")
    summary: str = Field(..., description=_DESC_ISSUE_TITLE)
    issue_type: str = Field(..., description="Epic, Story, Task")
    status: str = Field(..., description="pending, in_progress, complete")
    parent: str | None = Field(default=None, description=_DESC_PARENT_KEY)
    description: str = Field(default="", description="Issue description")
    labels: list[str] = Field(default_factory=list)
    priority: str | None = Field(default=None, description="Priority level")
    assignee: str | None = Field(default=None, description="Assignee identifier")
    comments: list[BacklogComment] = Field(default_factory=list)  # pyright: ignore[reportUnknownVariableType]
    links: list[BacklogLink] = Field(default_factory=list)  # pyright: ignore[reportUnknownVariableType]
    created: str = Field(default="", description=_DESC_CREATED_TS)
    updated: str = Field(default="", description=_DESC_UPDATED_TS)


# BackendHealth moved to raise_core.graph.backends.models (E275)
