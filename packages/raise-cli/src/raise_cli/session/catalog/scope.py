"""ScopeSpec — discriminated union for session catalog scope resolution.

Three levels, narrowest first:
  WorktreeScope — filter by worktree_id + project_id (most specific)
  ProjectScope  — filter by project_id only
  HostScope     — all sessions on this host (widest)

``resolve_scope_spec()`` returns the narrowest scope available from
the current process context (worktree registry + project_id).
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field


class WorktreeScope(BaseModel, frozen=True):
    """Narrowest scope: sessions for a specific worktree within a project."""

    kind: Literal["worktree"] = Field(default="worktree", frozen=True)
    worktree_id: str
    project_id: str


class ProjectScope(BaseModel, frozen=True):
    """Mid-level scope: all sessions for a project, any worktree."""

    kind: Literal["project"] = Field(default="project", frozen=True)
    project_id: str


class HostScope(BaseModel, frozen=True):
    """Widest scope: all sessions on this host."""

    kind: Literal["host"] = Field(default="host", frozen=True)


ScopeSpec = Annotated[
    WorktreeScope | ProjectScope | HostScope,
    Field(discriminator="kind"),
]
