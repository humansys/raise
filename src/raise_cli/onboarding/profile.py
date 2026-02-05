"""Developer profile schema and persistence.

Personal memory stored in ~/.rai/developer.yaml - cross-project relationship
between Rai and individual developers.
"""

from __future__ import annotations

import logging
from datetime import UTC, date, datetime
from enum import Enum
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger(__name__)


class ExperienceLevel(str, Enum):
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


class CommunicationStyle(str, Enum):
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


class CurrentSession(BaseModel):
    """Active session state for detecting orphaned sessions.

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


class DeveloperProfile(BaseModel):
    """Personal profile for a developer using RaiSE.

    Stored in ~/.rai/developer.yaml and persists across projects.
    Enables Rai to adapt interaction style based on experience.

    Attributes:
        name: Developer's name for personalized interaction.
        experience_level: Current Shu-Ha-Ri level (affects verbosity).
        communication: Communication style preferences.
        skills_mastered: List of skill names the developer has mastered.
        universal_patterns: Patterns that apply across all projects.
        sessions_total: Total sessions across all projects.
        first_session: Date of first RaiSE session.
        last_session: Date of most recent session.
        projects: List of project paths worked on.
        current_session: Active session state, or None if no session active.
    """

    name: str
    experience_level: ExperienceLevel = ExperienceLevel.SHU
    communication: CommunicationPreferences = Field(
        default_factory=CommunicationPreferences
    )
    skills_mastered: list[str] = Field(default_factory=list)
    universal_patterns: list[str] = Field(default_factory=list)
    sessions_total: int = 0
    first_session: date | None = None
    last_session: date | None = None
    projects: list[str] = Field(default_factory=list)
    current_session: CurrentSession | None = None


# Constants
RAI_HOME_DIR = ".rai"
DEVELOPER_PROFILE_FILE = "developer.yaml"


def get_rai_home() -> Path:
    """Get the path to ~/.rai/ directory.

    Returns:
        Path to the user's .rai directory in their home folder.
    """
    return Path.home() / RAI_HOME_DIR


def load_developer_profile() -> DeveloperProfile | None:
    """Load developer profile from ~/.rai/developer.yaml.

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
        return DeveloperProfile.model_validate(data)
    except yaml.YAMLError as e:
        logger.warning("Invalid YAML in developer profile: %s", e)
        return None
    except ValidationError as e:
        logger.warning("Invalid developer profile schema: %s", e)
        return None


def save_developer_profile(profile: DeveloperProfile) -> None:
    """Save developer profile to ~/.rai/developer.yaml.

    Creates ~/.rai/ directory if it doesn't exist.

    Args:
        profile: The developer profile to save.
    """
    rai_home = get_rai_home()
    rai_home.mkdir(parents=True, exist_ok=True)

    profile_path = rai_home / DEVELOPER_PROFILE_FILE

    # Convert to dict with proper serialization
    data = profile.model_dump(mode="json")

    content = yaml.dump(
        data, default_flow_style=False, allow_unicode=True, sort_keys=False
    )
    profile_path.write_text(content, encoding="utf-8")
    logger.debug("Saved developer profile: %s", profile_path)


def increment_session(
    profile: DeveloperProfile, project_path: str | None = None
) -> DeveloperProfile:
    """Increment session count and update session metadata.

    Pure function that returns a new profile instance without modifying
    the original. Does NOT persist to disk - caller is responsible for saving.

    Args:
        profile: The developer profile to update.
        project_path: Optional project path to add to projects list.

    Returns:
        Updated profile with incremented session count.
    """
    updates: dict[str, object] = {
        "sessions_total": profile.sessions_total + 1,
        "last_session": date.today(),
    }

    # Add project path if provided and not already present
    if project_path is not None and project_path not in profile.projects:
        updates["projects"] = [*profile.projects, project_path]

    return profile.model_copy(update=updates)


def start_session(profile: DeveloperProfile, project_path: str) -> DeveloperProfile:
    """Mark a session as active.

    Sets current_session with timestamp and project. Use this at the
    beginning of /session-start to track active sessions.

    Args:
        profile: The developer profile to update.
        project_path: Absolute path to the project directory.

    Returns:
        Updated profile with current_session set.
    """
    session = CurrentSession(
        started_at=datetime.now(UTC),
        project=project_path,
    )
    return profile.model_copy(update={"current_session": session})


def end_session(profile: DeveloperProfile) -> DeveloperProfile:
    """Clear the active session state.

    Clears current_session. Use this at the end of /session-close
    to mark the session as properly closed.

    Args:
        profile: The developer profile to update.

    Returns:
        Updated profile with current_session cleared.
    """
    return profile.model_copy(update={"current_session": None})
