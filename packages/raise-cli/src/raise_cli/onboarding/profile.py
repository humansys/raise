"""Developer profile schema and persistence.

Personal memory stored in ~/.rai/developer.yaml - cross-project relationship
between Rai and individual developers.
"""

from __future__ import annotations

import logging
from datetime import UTC, date, datetime
from enum import StrEnum
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, ValidationError

from raise_cli.adapters.filesystem_adapter import FilesystemAdapter

logger = logging.getLogger(__name__)


class DelegationLevel(StrEnum):
    """Delegation level for orchestrator HITL decisions.

    Controls when the orchestrator pauses for human review.

    Levels:
        REVIEW: Pause and show work for approval before continuing.
        NOTIFY: Show summary and continue unless human intervenes.
        AUTO: Continue without pausing (only hard gates stop execution).
    """

    REVIEW = "review"
    NOTIFY = "notify"
    AUTO = "auto"


class ExperienceLevel(StrEnum):
    """Developer experience level with RaiSE (Shu-Ha-Ri model).

    Determines interaction verbosity and explanation depth.

    Levels:
        SHU: Beginner (sessions 0-5) - explain everything, guide each step
        HA: Intermediate (sessions 6-20) - explain new concepts, efficient on known
        RI: Expert (sessions 21+) - minimal ceremony, maximum efficiency
    """

    SHU = "shu"
    HA = "ha"
    RI = "ri"


class CommunicationStyle(StrEnum):
    """Communication style preference.

    Determines how much explanation Rai provides by default.

    Styles:
        EXPLANATORY: Detailed explanations, good for learning
        BALANCED: Mix of explanation and efficiency
        DIRECT: Minimal explanation, maximum efficiency
    """

    EXPLANATORY = "explanatory"
    BALANCED = "balanced"
    DIRECT = "direct"


class CommunicationPreferences(BaseModel):
    """Communication preferences for a developer.

    Controls how Rai interacts with this developer.

    Attributes:
        style: Explanation verbosity (explanatory/balanced/direct).
        language: Preferred language code (e.g., "en", "es").
        skip_praise: Avoid unnecessary praise or validation.
        detailed_explanations: Provide thorough explanations (overrides style).
        redirect_when_dispersing: Permission to gently redirect off-topic.
    """

    style: CommunicationStyle = CommunicationStyle.BALANCED
    language: str = "en"
    skip_praise: bool = False
    detailed_explanations: bool = True
    redirect_when_dispersing: bool = False


class DelegationConfig(BaseModel):
    """Delegation preferences for orchestrator HITL control.

    Stored in developer.yaml under the 'delegation' key. When absent,
    defaults are derived from the developer's ShuHaRi experience level.

    Attributes:
        default_level: Default delegation level for all skills.
        overrides: Per-skill overrides (skill name → delegation level).
    """

    default_level: DelegationLevel
    overrides: dict[str, DelegationLevel] = Field(default_factory=dict)


class CurrentSession(BaseModel):
    """Active session state for detecting orphaned sessions.

    **DEPRECATED:** Use ActiveSession instead. This model is kept for
    backward compatibility during migration from single-session to multi-session.

    Tracks when a session started and in which project, enabling detection
    of sessions that were started but never closed (e.g., due to interruption).

    Attributes:
        started_at: UTC timestamp when session began.
        project: Absolute path to the project directory.
    """

    started_at: datetime
    project: str

    def is_stale(self, hours: int = 24) -> bool:
        """Check if session is stale (started more than N hours ago).

        Args:
            hours: Number of hours after which a session is considered stale.

        Returns:
            True if session started more than `hours` ago.
        """
        now = datetime.now(UTC)
        age = now - self.started_at
        return age.total_seconds() > hours * 3600


class ActiveSession(BaseModel):
    """Active session instance for multi-session support.

    Replaces CurrentSession to support concurrent sessions on the same project.
    Multiple AI agents/terminals can run simultaneously without state corruption.

    Attributes:
        session_id: Unique session identifier (e.g., "SES-177").
        started_at: UTC timestamp when session began.
        project: Absolute path to the project directory.
        agent: Agent type metadata (e.g., "claude-code", "cursor"). Default: "unknown".
    """

    session_id: str
    started_at: datetime
    project: str
    agent: str = "unknown"

    def is_stale(self, hours: int = 24) -> bool:
        """Check if session is stale (started more than N hours ago).

        Args:
            hours: Number of hours after which a session is considered stale.

        Returns:
            True if session started more than `hours` ago.
        """
        now = datetime.now(UTC)
        age = now - self.started_at
        return age.total_seconds() > hours * 3600


class Correction(BaseModel):
    """A coaching correction episode.

    Records when Rai observed a behavioral pattern that needed adjustment
    and the lesson learned from it.

    Attributes:
        session: Session ID where correction occurred (e.g., "SES-097").
        what: Description of the behavior observed.
        lesson: The lesson or principle derived from the correction.
    """

    session: str
    what: str
    lesson: str


class Deadline(BaseModel):
    """An operational deadline Rai tracks.

    Deadlines modulate Rai's behavior — urgency, focus, pushback.
    Not governance artifacts; these are Rai's operational context.

    Attributes:
        name: Short name for the deadline (e.g., "F&F").
        date: Target date.
        notes: Additional context about the deadline.
    """

    name: str
    date: date
    notes: str = ""


class RelationshipState(BaseModel):
    """State of the Rai-developer relationship.

    Attributes:
        quality: Relationship quality level.
        since: Date when the relationship started.
        trajectory: Direction of relationship development.
    """

    quality: str = "new"
    since: date | None = None
    trajectory: str = "starting"


class CoachingContext(BaseModel):
    """Rai's coaching observations about a developer.

    Accumulates over time in ~/.rai/developer.yaml. Corrections
    are capped at 10 (FIFO — oldest drops when new ones are added).

    Attributes:
        strengths: Observed developer strengths.
        growth_edge: Current primary growth area.
        trust_level: Trust level in the relationship.
        autonomy: Autonomy observation notes.
        corrections: Recent corrections (max 10, FIFO).
        communication_notes: Notes about communication patterns.
        relationship: State of the Rai-developer relationship.
    """

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
    Enables Rai to adapt interaction style based on experience.

    Attributes:
        name: Developer's name for personalized interaction.
        pattern_prefix: Single-letter prefix for pattern IDs (e.g., 'E' for Emilio).
            Used to prevent pattern ID collisions in multi-developer repos.
            Defaults to first letter of name if not set.
        experience_level: Current Shu-Ha-Ri level (affects verbosity).
        communication: Communication style preferences.
        skills_mastered: List of skill names the developer has mastered.
        universal_patterns: Patterns that apply across all projects.
        first_session: Date of first RaiSE session.
        last_session: Date of most recent session.
        projects: List of project paths worked on.
        current_session: Active session state, or None if no session active.
        coaching: Coaching context with corrections and relationship state.
        deadlines: Operational deadlines Rai tracks.
    """

    name: str
    pattern_prefix: str | None = Field(
        default=None,
        description="Single-letter prefix for pattern IDs (e.g., 'E'). "
        "Defaults to first letter of name.",
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
    current_session: CurrentSession | None = (
        None  # DEPRECATED: migrated to active_sessions
    )
    active_sessions: list[ActiveSession] = Field(
        default_factory=lambda: list[ActiveSession]()
    )
    coaching: CoachingContext = Field(default_factory=CoachingContext)
    delegation: DelegationConfig | None = None
    deadlines: list[Deadline] = Field(default_factory=lambda: list[Deadline]())

    def get_pattern_prefix(self) -> str:
        """Get the developer's pattern prefix.

        Returns explicit pattern_prefix if set, otherwise first letter of name (uppercased).
        """
        if self.pattern_prefix:
            return self.pattern_prefix.upper()
        return self.name[0].upper() if self.name else "X"


_SHUHARI_DELEGATION: dict[ExperienceLevel, DelegationLevel] = {
    ExperienceLevel.SHU: DelegationLevel.REVIEW,
    ExperienceLevel.HA: DelegationLevel.NOTIFY,
    ExperienceLevel.RI: DelegationLevel.AUTO,
}


def resolve_delegation(profile: DeveloperProfile, skill_name: str) -> DelegationLevel:
    """Resolve the effective delegation level for a skill.

    Precedence: per-skill override > explicit default_level > ShuHaRi derivation.

    Args:
        profile: Developer profile with optional delegation config.
        skill_name: Name of the skill (e.g., "rai-story-design").

    Returns:
        The effective delegation level for the given skill.
    """
    if profile.delegation is not None:
        if skill_name in profile.delegation.overrides:
            return profile.delegation.overrides[skill_name]
        return profile.delegation.default_level
    return _SHUHARI_DELEGATION[profile.experience_level]


# Constants
RAI_HOME_DIR = ".rai"
DEVELOPER_PROFILE_FILE = "developer.yaml"


def get_rai_home() -> Path:
    """Get the path to ~/.rai/ directory.

    Returns:
        Path to the user's .rai directory in their home folder.
    """
    return Path.home() / RAI_HOME_DIR


def _migrate_current_session(profile: DeveloperProfile) -> DeveloperProfile:
    """Migrate old current_session format to active_sessions list.

    Backward compatibility migration. Converts single
    current_session (dict) to active_sessions (list) with generated session ID.

    Args:
        profile: Profile to migrate.

    Returns:
        Profile with migration applied (may be same instance if no migration needed).
    """
    if profile.current_session is None:
        # No current session to migrate
        return profile

    if len(profile.active_sessions) > 0:
        # Already migrated or has active sessions — don't re-migrate
        logger.debug("Profile already has active_sessions, skipping migration")
        return profile

    # The old current_session is stale — it was never properly closed
    # under the old format. Clear it instead of converting to a zombie
    # SES-MIGRATED entry that blocks future session closes.
    updated = profile.model_copy(deep=True)
    updated.active_sessions = []
    updated.current_session = None

    logger.info("Migrated current_session: cleared stale session (old format)")
    return updated


def load_developer_profile() -> DeveloperProfile | None:
    """Load developer profile from ~/.rai/developer.yaml.

    Automatically migrates old current_session format to active_sessions
    if needed (backward compatibility for single→multi session migration).

    Returns:
        DeveloperProfile if file exists and is valid, None otherwise.
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

        # Migrate if needed
        migrated = _migrate_current_session(profile)
        if migrated is not profile:
            # Migration occurred — save immediately
            save_developer_profile(migrated)
            return migrated

        return profile
    except yaml.YAMLError as e:
        logger.warning("Invalid YAML in developer profile: %s", e)
        return None
    except ValidationError as e:
        logger.warning("Invalid developer profile schema: %s", e)
        return None


def save_developer_profile(profile: DeveloperProfile) -> None:
    """Save developer profile to ~/.rai/developer.yaml.

    Uses FilesystemAdapter for atomic write semantics.
    Creates ~/.rai/ directory if it doesn't exist.

    Args:
        profile: The developer profile to save.
    """
    rai_home = get_rai_home()

    # Convert to dict with proper serialization
    data = profile.model_dump(mode="json")

    content = yaml.dump(
        data, default_flow_style=False, allow_unicode=True, sort_keys=False
    )

    adapter = FilesystemAdapter(root=rai_home)
    adapter.write(Path(DEVELOPER_PROFILE_FILE), content)
    logger.debug("Saved developer profile: %s", rai_home / DEVELOPER_PROFILE_FILE)


def increment_session(
    profile: DeveloperProfile, project_path: str | None = None
) -> DeveloperProfile:
    """Update session metadata (last_session date and projects list).

    Pure function that returns a new profile instance without modifying
    the original. Does NOT persist to disk - caller is responsible for saving.

    Note: Session count is derived from sessions/index.jsonl, not tracked here.

    Args:
        profile: The developer profile to update.
        project_path: Optional project path to add to projects list.

    Returns:
        Updated profile with session metadata.
    """
    updates: dict[str, object] = {
        "last_session": date.today(),
    }

    # Add project path if provided and not already present
    if project_path is not None and project_path not in profile.projects:
        updates["projects"] = [*profile.projects, project_path]

    return profile.model_copy(update=updates)


def start_session(
    profile: DeveloperProfile,
    session_id: str,
    project_path: str,
    agent: str = "unknown",
) -> tuple[DeveloperProfile, list[ActiveSession]]:
    """Mark a session as active by adding to active_sessions list.

    Adds an ActiveSession to the profile's active_sessions list. Also detects
    stale sessions (started >24h ago) and returns them for warning.

    Args:
        profile: The developer profile to update.
        session_id: Unique session identifier (e.g., "SES-177").
        project_path: Absolute path to the project directory.
        agent: Agent type (e.g., "claude-code", "cursor"). Default: "unknown".

    Returns:
        Tuple of (updated profile, list of stale sessions for warning).
    """
    # Detect stale sessions before adding new one
    stale_sessions = [s for s in profile.active_sessions if s.is_stale(hours=24)]

    # Create new active session
    new_session = ActiveSession(
        session_id=session_id,
        started_at=datetime.now(UTC),
        project=project_path,
        agent=agent,
    )

    # Remove existing session for same project (idempotency)
    updated_sessions = [s for s in profile.active_sessions if s.project != project_path]
    updated_sessions.append(new_session)
    updated = profile.model_copy(update={"active_sessions": updated_sessions})

    return updated, stale_sessions


def end_session(profile: DeveloperProfile, session_id: str) -> DeveloperProfile:
    """Remove a session from active_sessions list.

    Removes the specified session from the profile's active_sessions list.
    If session_id doesn't exist, returns profile unchanged (no-op).

    Args:
        profile: The developer profile to update.
        session_id: Session identifier to remove (e.g., "SES-177").

    Returns:
        Updated profile with session removed from active_sessions.
    """
    # Filter out the specified session
    updated_sessions = [
        s for s in profile.active_sessions if s.session_id != session_id
    ]
    return profile.model_copy(update={"active_sessions": updated_sessions})


def add_correction(
    profile: DeveloperProfile, session_id: str, what: str, lesson: str
) -> DeveloperProfile:
    """Add a coaching correction to the profile.

    Maintains FIFO cap of CORRECTIONS_MAX — oldest correction is dropped
    when a new one is added and the list is at capacity.

    Args:
        profile: The developer profile to update.
        session_id: Session ID where correction occurred.
        what: Description of the behavior observed.
        lesson: The lesson derived from the correction.

    Returns:
        Updated profile with new correction added.
    """
    correction = Correction(session=session_id, what=what, lesson=lesson)
    corrections = [*profile.coaching.corrections, correction]
    if len(corrections) > CORRECTIONS_MAX:
        corrections = corrections[-CORRECTIONS_MAX:]
    coaching = profile.coaching.model_copy(update={"corrections": corrections})
    return profile.model_copy(update={"coaching": coaching})


def add_deadline(
    profile: DeveloperProfile, name: str, deadline_date: date, notes: str = ""
) -> DeveloperProfile:
    """Add an operational deadline to the profile.

    If a deadline with the same name exists, it is replaced.

    Args:
        profile: The developer profile to update.
        name: Short name for the deadline.
        deadline_date: Target date.
        notes: Additional context.

    Returns:
        Updated profile with deadline added or updated.
    """
    deadline = Deadline(name=name, date=deadline_date, notes=notes)
    # Replace existing deadline with same name, or append
    deadlines = [d for d in profile.deadlines if d.name != name]
    deadlines.append(deadline)
    return profile.model_copy(update={"deadlines": deadlines})


def update_coaching(  # noqa: C901 -- complexity 11, refactor deferred
    profile: DeveloperProfile,
    strengths: list[str] | None = None,
    growth_edge: str | None = None,
    trust_level: str | None = None,
    autonomy: str | None = None,
    relationship: dict[str, str] | None = None,
    communication_notes: list[str] | None = None,
) -> DeveloperProfile:
    """Update coaching context fields.

    Only updates fields that are explicitly provided (not None).

    Args:
        profile: The developer profile to update.
        strengths: New strengths list (replaces existing).
        growth_edge: New growth edge description.
        trust_level: New trust level.
        autonomy: New autonomy observation.
        relationship: Dict with optional keys (quality, trajectory).
            Updates RelationshipState fields individually.
        communication_notes: Notes about communication patterns (replaces existing).

    Returns:
        Updated profile with coaching changes.
    """
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
