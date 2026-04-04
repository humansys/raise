"""Session state schema for project-level working state.

Stored in .raise/rai/session-state.yaml — overwritten each session-close.
Read by session-start to assemble context bundle.

Session protocol models (ActivityEntry, SessionInfo, SessionOutcome,
SessionInsights, Improvement) added for E1248 / ADR-038.
"""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

from pydantic import BaseModel, Field, field_validator


class CurrentWork(BaseModel):
    """What Rai is currently working on.

    All fields default to empty string so the model is valid even when
    there is no active epic/story (e.g., between epics after session close).

    Attributes:
        epic: Epic identifier (e.g., "E15"), or empty string.
        story: Story identifier (e.g., "S15.7"), or empty string.
        phase: Current phase (e.g., "design", "implement"), or empty string.
        branch: Git branch name, or empty string.
    """

    release: str = ""
    epic: str = ""
    story: str = ""
    phase: str = ""
    branch: str = ""

    @field_validator("release", "epic", "story", "phase", "branch", mode="before")
    @classmethod
    def coerce_none_to_empty(cls, v: object) -> object:
        """Accept None from YAML and coerce to empty string."""
        return "" if v is None else v


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


class EpicProgress(BaseModel):
    """Progress tracking for the current epic.

    Attributes:
        epic: Epic identifier (e.g., "E15").
        stories_done: Number of completed stories.
        stories_total: Total number of stories.
        sp_done: Story points completed.
        sp_total: Total story points.
    """

    epic: str
    stories_done: int
    stories_total: int
    sp_done: int
    sp_total: int


class SessionState(BaseModel):
    """Project-level working state. Overwritten each session-close.

    Attributes:
        current_work: What Rai is currently working on.
        last_session: Summary of the most recent session.
        pending: Open items carried between sessions.
        notes: Free-form notes.
        progress: Epic progress tracking.
        completed_epics: List of completed epic identifiers.
    """

    current_work: CurrentWork
    last_session: LastSession
    pending: PendingItems = Field(default_factory=PendingItems)
    notes: str = ""
    narrative: str = Field(
        default="",
        description="Structured session context for cross-session continuity. "
        "Contains decisions, research, artifacts, and branch state from the last session.",
    )
    next_session_prompt: str = Field(
        default="",
        description="Forward-looking guidance from Rai to her future self. "
        "Written during session-close, read at session-start for better continuity.",
    )
    progress: EpicProgress | None = None
    completed_epics: list[str] = Field(default_factory=list)
    last_modified: str | None = Field(
        default=None,
        description="ISO 8601 timestamp of last write. Used for stale-overwrite protection.",
    )


# ---------------------------------------------------------------------------
# Session protocol models (E1248 / ADR-038)
# ---------------------------------------------------------------------------


class ActivityEntry(BaseModel, frozen=True):
    """A single entry from recent git activity."""

    commit_hash: str
    subject: str
    author: str
    timestamp: datetime
    story_id: str = ""
    epic_id: str = ""


class SessionInfo(BaseModel, frozen=True):
    """Metadata for an active session."""

    session_id: str
    developer: str
    project: Path
    branch: str
    started: datetime


class SessionOutcome(BaseModel, frozen=True):
    """Result of a completed session."""

    summary: str
    patterns_captured: list[str] = Field(default_factory=list)
    stories_completed: list[str] = Field(default_factory=list)


class SessionInsights(BaseModel, frozen=True):
    """Analysis results for a session."""

    session_id: str
    commit_count: int
    test_commit_ratio: float
    revert_count: int
    duration_minutes: int


class Improvement(BaseModel, frozen=True):
    """A suggested improvement from workstream analysis."""

    category: str
    description: str
    suggestion: str
