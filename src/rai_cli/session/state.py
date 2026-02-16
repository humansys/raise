"""Session state persistence.

Reads and writes .raise/rai/personal/session-state.yaml — per-developer working
state that is overwritten each session-close and read by session-start.

Migration: if the old path (.raise/rai/session-state.yaml) exists and the new
personal/ path does not, the file is moved automatically.
"""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

import yaml
from pydantic import ValidationError

from rai_cli.config.paths import get_session_dir
from rai_cli.schemas.session_state import SessionState

logger = logging.getLogger(__name__)

# New path: personal directory (gitignored, per-developer)
SESSION_STATE_REL_PATH = Path(".raise") / "rai" / "personal" / "session-state.yaml"

# Legacy path for migration
_LEGACY_SESSION_STATE_REL_PATH = Path(".raise") / "rai" / "session-state.yaml"


def get_session_state_path(
    project_path: Path, session_id: str | None = None
) -> Path:
    """Get the absolute path to session state file.

    When session_id is provided, returns per-session path:
        .raise/rai/personal/sessions/{session_id}/state.yaml

    When session_id is None, returns legacy flat path:
        .raise/rai/personal/session-state.yaml

    Args:
        project_path: Absolute path to the project root.
        session_id: Optional session ID for per-session isolation.

    Returns:
        Path to the session state file.
    """
    if session_id is not None:
        return get_session_dir(session_id, project_path) / "state.yaml"
    return project_path / SESSION_STATE_REL_PATH


def _migrate_session_state(project_path: Path) -> None:
    """Migrate session-state.yaml from old shared path to personal/.

    Moves .raise/rai/session-state.yaml → .raise/rai/personal/session-state.yaml
    if old exists and new does not.
    """
    old_path = project_path / _LEGACY_SESSION_STATE_REL_PATH
    new_path = get_session_state_path(project_path)

    if old_path.exists() and not new_path.exists():
        new_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(old_path), str(new_path))
        logger.info("Migrated session state: %s → %s", old_path, new_path)


def load_session_state(
    project_path: Path, session_id: str | None = None
) -> SessionState | None:
    """Load session state from per-session directory or flat file.

    When session_id is provided, loads from per-session directory.
    When session_id is None, loads from legacy flat file (with migration).

    Args:
        project_path: Absolute path to the project root.
        session_id: Optional session ID for per-session isolation.

    Returns:
        SessionState if file exists and is valid, None otherwise.
    """
    if session_id is None:
        _migrate_session_state(project_path)
    state_path = get_session_state_path(project_path, session_id)

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


def save_session_state(
    project_path: Path, state: SessionState, session_id: str | None = None
) -> None:
    """Save session state to per-session directory or flat file.

    When session_id is provided, writes to per-session directory.
    When session_id is None, writes to legacy flat file.

    Creates parent directories if they don't exist.
    Overwrites any existing file.

    Args:
        project_path: Absolute path to the project root.
        state: The session state to save.
        session_id: Optional session ID for per-session isolation.
    """
    state_path = get_session_state_path(project_path, session_id)
    state_path.parent.mkdir(parents=True, exist_ok=True)

    data = state.model_dump(mode="json")
    content = yaml.dump(
        data, default_flow_style=False, allow_unicode=True, sort_keys=False
    )
    state_path.write_text(content, encoding="utf-8")
    logger.debug("Saved session state: %s", state_path)
