"""Session state persistence.

Reads and writes .raise/rai/session-state.yaml — project-level working state
that is overwritten each session-close and read by session-start.
"""

from __future__ import annotations

import logging
from pathlib import Path

import yaml
from pydantic import ValidationError

from raise_cli.schemas.session_state import SessionState

logger = logging.getLogger(__name__)

# Path relative to project root
SESSION_STATE_REL_PATH = Path(".raise") / "rai" / "session-state.yaml"


def get_session_state_path(project_path: Path) -> Path:
    """Get the absolute path to session-state.yaml for a project.

    Args:
        project_path: Absolute path to the project root.

    Returns:
        Path to the session-state.yaml file.
    """
    return project_path / SESSION_STATE_REL_PATH


def load_session_state(project_path: Path) -> SessionState | None:
    """Load session state from .raise/rai/session-state.yaml.

    Args:
        project_path: Absolute path to the project root.

    Returns:
        SessionState if file exists and is valid, None otherwise.
    """
    state_path = get_session_state_path(project_path)

    if not state_path.exists():
        logger.debug("Session state not found: %s", state_path)
        return None

    try:
        content = state_path.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        if data is None:
            logger.warning("Empty session state: %s", state_path)
            return None
        return SessionState.model_validate(data)
    except yaml.YAMLError as e:
        logger.warning("Invalid YAML in session state: %s", e)
        return None
    except ValidationError as e:
        logger.warning("Invalid session state schema: %s", e)
        return None


def save_session_state(project_path: Path, state: SessionState) -> None:
    """Save session state to .raise/rai/session-state.yaml.

    Creates parent directories if they don't exist.
    Overwrites any existing file.

    Args:
        project_path: Absolute path to the project root.
        state: The session state to save.
    """
    state_path = get_session_state_path(project_path)
    state_path.parent.mkdir(parents=True, exist_ok=True)

    data = state.model_dump(mode="json")
    content = yaml.dump(
        data, default_flow_style=False, allow_unicode=True, sort_keys=False
    )
    state_path.write_text(content, encoding="utf-8")
    logger.debug("Saved session state: %s", state_path)
