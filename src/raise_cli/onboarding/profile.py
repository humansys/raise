"""Developer profile schema and persistence.

Personal memory stored in ~/.rai/developer.yaml - cross-project relationship
between Rai and individual developers.
"""

from __future__ import annotations

import logging
from datetime import date
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


class DeveloperProfile(BaseModel):
    """Personal profile for a developer using RaiSE.

    Stored in ~/.rai/developer.yaml and persists across projects.
    Enables Rai to adapt interaction style based on experience.

    Attributes:
        name: Developer's name for personalized interaction.
        experience_level: Current Shu-Ha-Ri level (affects verbosity).
        sessions_total: Total sessions across all projects.
        first_session: Date of first RaiSE session.
        last_session: Date of most recent session.
        projects: List of project paths worked on.
    """

    name: str
    experience_level: ExperienceLevel = ExperienceLevel.SHU
    sessions_total: int = 0
    first_session: date | None = None
    last_session: date | None = None
    projects: list[str] = Field(default_factory=list)


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

    content = yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)
    profile_path.write_text(content, encoding="utf-8")
    logger.debug("Saved developer profile: %s", profile_path)
