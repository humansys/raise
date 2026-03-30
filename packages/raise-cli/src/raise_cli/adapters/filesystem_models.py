"""Filesystem adapter internal storage models.

These are NOT boundary models — they define the on-disk YAML format
used exclusively by ``FilesystemPMAdapter``. Other adapters never
consume or produce these types.

RAISE-1060: Extracted from models.py (was leaking internals into shared contract).
"""

from __future__ import annotations

from pydantic import BaseModel, Field

_DESC_CREATED_TS = "ISO 8601 creation timestamp"
_DESC_UPDATED_TS = "ISO 8601 last update timestamp"


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
    summary: str = Field(..., description="Issue title")
    issue_type: str = Field(..., description="Epic, Story, Task")
    status: str = Field(..., description="pending, in_progress, complete")
    parent: str | None = Field(default=None, description="Parent issue key")
    description: str = Field(default="", description="Issue description")
    labels: list[str] = Field(default_factory=list)
    priority: str | None = Field(default=None, description="Priority level")
    assignee: str | None = Field(default=None, description="Assignee identifier")
    comments: list[BacklogComment] = Field(default_factory=list)  # pyright: ignore[reportUnknownVariableType]
    links: list[BacklogLink] = Field(default_factory=list)  # pyright: ignore[reportUnknownVariableType]
    created: str = Field(default="", description=_DESC_CREATED_TS)
    updated: str = Field(default="", description=_DESC_UPDATED_TS)
