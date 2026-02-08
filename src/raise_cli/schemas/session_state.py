"""Session state schema for project-level working state.

Stored in .raise/rai/session-state.yaml — overwritten each session-close.
Read by session-start to assemble context bundle.
"""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class CurrentWork(BaseModel):
    """What Rai is currently working on.

    Attributes:
        epic: Epic identifier (e.g., "E15").
        story: Story identifier (e.g., "S15.7").
        phase: Current phase (e.g., "design", "implement").
        branch: Git branch name.
    """

    epic: str
    story: str
    phase: str
    branch: str


class LastSession(BaseModel):
    """Summary of the most recent session.

    Attributes:
        id: Session identifier (e.g., "SES-097").
        date: Date of the session.
        developer: Developer name.
        summary: Brief description of what was accomplished.
        patterns_captured: Pattern IDs captured during the session.
    """

    id: str
    date: date
    developer: str
    summary: str
    patterns_captured: list[str] = Field(default_factory=list)


class PendingItems(BaseModel):
    """Open items carried between sessions.

    Attributes:
        decisions: Decisions that need to be made.
        blockers: Items blocking progress.
        next_actions: Concrete next steps.
    """

    decisions: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)


class SessionState(BaseModel):
    """Project-level working state. Overwritten each session-close.

    Attributes:
        current_work: What Rai is currently working on.
        last_session: Summary of the most recent session.
        pending: Open items carried between sessions.
        notes: Free-form notes.
    """

    current_work: CurrentWork
    last_session: LastSession
    pending: PendingItems = Field(default_factory=PendingItems)
    notes: str = ""
