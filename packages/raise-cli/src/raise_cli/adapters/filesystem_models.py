"""Filesystem adapter internal storage models.

These are NOT boundary models — they define the on-disk YAML format
used exclusively by ``FilesystemPMAdapter``. Other adapters never
consume or produce these types.

RAISE-1060: Extracted from models.py (was leaking internals into shared contract).
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator

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
    fix_versions: list[str] = Field(
        default_factory=list,
        description="Fix versions (e.g. release tags) the issue is targeted at",
    )
    created: str = Field(default="", description=_DESC_CREATED_TS)
    updated: str = Field(default="", description=_DESC_UPDATED_TS)

    @field_validator("parent", "priority", "assignee", "issue_type", mode="before")
    @classmethod
    def _coerce_wire_shaped_str(cls, value: Any) -> Any:
        """Coerce a Jira-wire-shaped dict into its scalar key.

        RAISE-14593: these fields are typed ``str | None`` but callers (e.g.
        ``update_issue``) may pass a wire-shaped dict such as ``{"key": "E1"}``
        or ``{"name": "High"}``. Relying on Pydantic's union validation to
        *reject* the dict is version-fragile — in some Pydantic v2 configs the
        dict is serialized verbatim (with only a warning), corrupting the YAML
        mirror. Coercing here, in ``mode="before"``, guarantees a clean scalar
        on every read/write path regardless of Pydantic's union behavior.
        """
        if isinstance(value, dict):
            wire: dict[str, Any] = value
            for candidate in ("key", "name", "value", "id"):
                extracted = wire.get(candidate)
                if isinstance(extracted, str):
                    return extracted
            return str(wire)
        return value

    @field_validator("fix_versions", mode="before")
    @classmethod
    def _coerce_fix_versions(cls, value: Any) -> Any:
        """Coerce Jira wire formats for fixVersions into a plain list[str].

        RAISE-15669: two callers pass different shapes:
        - ``--fix-version 3.1.0b2``  → a bare string ``"3.1.0b2"``
        - ``-F fixVersions=[…]``      → a list of Jira name-objects
                                        ``[{"name": "3.1.0b2"}, …]``

        Both are valid Jira representations; Pydantic's ``list[str]``
        validator rejects them without this coercion, leaving the local
        YAML mirror stale and causing the close-sync gate to fail.
        """
        if isinstance(value, str):
            return [value] if value else []
        if isinstance(value, list):
            result: list[str] = []
            for item in value:
                if isinstance(item, str):
                    result.append(item)
                elif isinstance(item, dict):
                    name = item.get("name")
                    if isinstance(name, str) and name:
                        result.append(name)
            return result
        return value
