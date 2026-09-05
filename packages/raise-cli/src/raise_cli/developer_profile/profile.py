"""Developer profile schema and pure functions (core tier).

Personal memory stored in ~/.rai/developer.yaml - cross-project relationship
between Rai and individual developers.

NOTE: This module contains ONLY pure models and functions.
Persistence (save_developer_profile) lives in developer_profile.persistence,
which holds the enrollment waiver for the adapters.filesystem_adapter import.
"""

from __future__ import annotations

import logging
from datetime import UTC, date, datetime
from enum import StrEnum
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger(__name__)


class DelegationLevel(StrEnum):
    """Delegation level for orchestrator HITL decisions."""

    REVIEW = "review"
    NOTIFY = "notify"
    AUTO = "auto"


class ExperienceLevel(StrEnum):
    """Developer experience level with RaiSE (Shu-Ha-Ri model)."""

    SHU = "shu"
    HA = "ha"
    RI = "ri"


class CommunicationStyle(StrEnum):
    """Communication style preference."""

    EXPLANATORY = "explanatory"
    BALANCED = "balanced"
    DIRECT = "direct"


class CommunicationPreferences(BaseModel):
    """Communication preferences for a developer."""

    style: CommunicationStyle = CommunicationStyle.BALANCED
    language: str = "en"
    skip_praise: bool = False
    detailed_explanations: bool = True
    redirect_when_dispersing: bool = False


class DelegationConfig(BaseModel):
    """Delegation preferences for orchestrator HITL control."""

    default_level: DelegationLevel
    overrides: dict[str, DelegationLevel] = Field(default_factory=dict)


class CurrentSession(BaseModel):
    """Active session state — DEPRECATED: use ActiveSession instead."""

    started_at: datetime
    project: str

    def is_stale(self, hours: int = 24) -> bool:
        """Return True if this session started more than `hours` ago."""
        now = datetime.now(UTC)
        age = now - self.started_at
        return age.total_seconds() > hours * 3600


class ActiveSession(BaseModel):
    """Active session instance for multi-session support."""

    session_id: str
    started_at: datetime
    project: str
    agent: str = "unknown"
    cc_session_id: str | None = None

    def is_stale(self, hours: int = 24) -> bool:
        """Return True if this session started more than `hours` ago."""
        now = datetime.now(UTC)
        age = now - self.started_at
        return age.total_seconds() > hours * 3600


class Correction(BaseModel):
    """A coaching correction episode."""

    session: str
    what: str
    lesson: str


class Deadline(BaseModel):
    """An operational deadline Rai tracks."""

    name: str
    date: date
    notes: str = ""


class RelationshipState(BaseModel):
    """State of the Rai-developer relationship."""

    quality: str = "new"
    since: date | None = None
    trajectory: str = "starting"


class CoachingContext(BaseModel):
    """Rai's coaching observations about a developer."""

    strengths: list[str] = Field(default_factory=list)
    growth_edge: str = ""
    trust_level: str = "new"
    autonomy: str = ""
    corrections: list[Correction] = Field(default_factory=lambda: list[Correction]())
    communication_notes: list[str] = Field(default_factory=list)
    relationship: RelationshipState = Field(default_factory=RelationshipState)


CORRECTIONS_MAX = 10


class DeveloperProfile(BaseModel):
    """Personal profile for a developer using RaiSE.

    Stored in ~/.rai/developer.yaml and persists across projects.
    """

    name: str
    pattern_prefix: str | None = Field(
        default=None,
        description="Single-letter prefix for pattern IDs (e.g., 'E'). "
        "Defaults to first letter of name.",
    )
    local_prefix: str | None = Field(
        default=None,
        description="Override for backlog staging key prefix (e.g., 'Em' when two devs share 'E'). "
        "Defaults to name if not set.",
    )
    experience_level: ExperienceLevel = ExperienceLevel.SHU
    communication: CommunicationPreferences = Field(
        default_factory=CommunicationPreferences
    )
    skills_mastered: list[str] = Field(default_factory=list)
    universal_patterns: list[str] = Field(default_factory=list)
    first_session: date | None = None
    last_session: date | None = None
    projects: list[str] = Field(default_factory=list)
    current_session: CurrentSession | None = None  # DEPRECATED
    active_sessions: list[ActiveSession] = Field(
        default_factory=lambda: list[ActiveSession]()
    )
    coaching: CoachingContext = Field(default_factory=CoachingContext)
    delegation: DelegationConfig | None = None
    deadlines: list[Deadline] = Field(default_factory=lambda: list[Deadline]())
    harness: str | None = None

    def get_pattern_prefix(self) -> str:
        """Return the developer's pattern prefix (explicit or first letter of name)."""
        if self.pattern_prefix:
            return self.pattern_prefix.upper()
        return self.name[0].upper() if self.name else "X"


_SHUHARI_DELEGATION: dict[ExperienceLevel, DelegationLevel] = {
    ExperienceLevel.SHU: DelegationLevel.REVIEW,
    ExperienceLevel.HA: DelegationLevel.NOTIFY,
    ExperienceLevel.RI: DelegationLevel.AUTO,
}


def resolve_delegation(profile: DeveloperProfile, skill_name: str) -> DelegationLevel:
    """Resolve the effective delegation level for a skill."""
    if profile.delegation is not None:
        if skill_name in profile.delegation.overrides:
            return profile.delegation.overrides[skill_name]
        return profile.delegation.default_level
    return _SHUHARI_DELEGATION[profile.experience_level]


RAI_HOME_DIR = ".rai"
DEVELOPER_PROFILE_FILE = "developer.yaml"


def get_rai_home() -> Path:
    """Get the path to ~/.rai/ directory."""
    return Path.home() / RAI_HOME_DIR


def _migrate_current_session(profile: DeveloperProfile) -> DeveloperProfile:
    """Migrate old current_session format to active_sessions list (in-memory only)."""
    if profile.current_session is None:
        return profile
    if len(profile.active_sessions) > 0:
        logger.debug("Profile already has active_sessions, skipping migration")
        return profile
    updated = profile.model_copy(deep=True)
    updated.active_sessions = []
    updated.current_session = None
    logger.info("Migrated current_session: cleared stale session (old format)")
    return updated


def load_developer_profile() -> DeveloperProfile | None:
    """Load developer profile from ~/.rai/developer.yaml.

    Performs in-memory migration of old current_session format if needed.
    Does NOT auto-save after migration (D-S4-4: no FilesystemAdapter import
    in this module). Callers that need persistence call save_developer_profile.
    """
    rai_home = get_rai_home()
    profile_path = rai_home / DEVELOPER_PROFILE_FILE

    if not profile_path.exists():
        logger.debug("Developer profile not found: %s", profile_path)
        return None

    try:
        content = profile_path.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        if data is None:
            logger.warning("Empty developer profile: %s", profile_path)
            return None

        profile = DeveloperProfile.model_validate(data)
        return _migrate_current_session(profile)

    except yaml.YAMLError as e:
        logger.warning("Invalid YAML in developer profile: %s", e)
        return None
    except ValidationError as e:
        logger.warning("Invalid developer profile schema: %s", e)
        return None


def increment_session(
    profile: DeveloperProfile, project_path: str | None = None
) -> DeveloperProfile:
    """Update session metadata. Pure function — does not persist."""
    updates: dict[str, object] = {"last_session": date.today()}
    if project_path is not None and project_path not in profile.projects:
        updates["projects"] = [*profile.projects, project_path]
    return profile.model_copy(update=updates)


def start_session(
    profile: DeveloperProfile,
    session_id: str,
    project_path: str,
    agent: str = "unknown",
    cc_session_id: str | None = None,
) -> tuple[DeveloperProfile, list[ActiveSession]]:
    """Mark a session as active. Pure function — does not persist."""
    stale_sessions = [
        session
        for session in profile.active_sessions
        if session.project == project_path and session.is_stale(hours=24)
    ]
    new_session = ActiveSession(
        session_id=session_id,
        started_at=datetime.now(UTC),
        project=project_path,
        agent=agent,
        cc_session_id=cc_session_id,
    )
    updated_sessions = [s for s in profile.active_sessions if s.project != project_path]
    updated_sessions.append(new_session)
    updated = profile.model_copy(update={"active_sessions": updated_sessions})
    return updated, stale_sessions


def end_session(profile: DeveloperProfile, session_id: str) -> DeveloperProfile:
    """Remove a session from active_sessions. Pure function — does not persist."""
    updated_sessions = [
        s for s in profile.active_sessions if s.session_id != session_id
    ]
    return profile.model_copy(update={"active_sessions": updated_sessions})


def add_correction(
    profile: DeveloperProfile, session_id: str, what: str, lesson: str
) -> DeveloperProfile:
    """Add a coaching correction. Pure function — does not persist."""
    correction = Correction(session=session_id, what=what, lesson=lesson)
    corrections = [*profile.coaching.corrections, correction]
    if len(corrections) > CORRECTIONS_MAX:
        corrections = corrections[-CORRECTIONS_MAX:]
    coaching = profile.coaching.model_copy(update={"corrections": corrections})
    return profile.model_copy(update={"coaching": coaching})


def add_deadline(
    profile: DeveloperProfile, name: str, deadline_date: date, notes: str = ""
) -> DeveloperProfile:
    """Add an operational deadline. Pure function — does not persist."""
    deadline = Deadline(name=name, date=deadline_date, notes=notes)
    deadlines = [d for d in profile.deadlines if d.name != name]
    deadlines.append(deadline)
    return profile.model_copy(update={"deadlines": deadlines})


def update_coaching(  # noqa: C901
    profile: DeveloperProfile,
    strengths: list[str] | None = None,
    growth_edge: str | None = None,
    trust_level: str | None = None,
    autonomy: str | None = None,
    relationship: dict[str, str] | None = None,
    communication_notes: list[str] | None = None,
) -> DeveloperProfile:
    """Update coaching context fields. Pure function — does not persist."""
    updates: dict[str, object] = {}
    if strengths is not None:
        updates["strengths"] = strengths
    if growth_edge is not None:
        updates["growth_edge"] = growth_edge
    if trust_level is not None:
        updates["trust_level"] = trust_level
    if autonomy is not None:
        updates["autonomy"] = autonomy
    if communication_notes is not None:
        updates["communication_notes"] = communication_notes
    if relationship is not None:
        rel_updates: dict[str, object] = {}
        if "quality" in relationship:
            rel_updates["quality"] = relationship["quality"]
        if "trajectory" in relationship:
            rel_updates["trajectory"] = relationship["trajectory"]
        if rel_updates:
            updated_rel = profile.coaching.relationship.model_copy(update=rel_updates)
            updates["relationship"] = updated_rel
    if not updates:
        return profile
    coaching = profile.coaching.model_copy(update=updates)
    return profile.model_copy(update={"coaching": coaching})
