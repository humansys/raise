"""Session state persistence.

Reads and writes .raise/rai/personal/session-state.yaml — per-developer working
state that is overwritten each session-close and read by session-start.

Migration: if the old path (.raise/rai/session-state.yaml) exists and the new
personal/ path does not, the file is moved automatically.
"""

from __future__ import annotations

import logging
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

import yaml
from pydantic import ValidationError

from raise_cli.adapters.filesystem_adapter import FilesystemAdapter
from raise_cli.config.paths import get_session_dir
from raise_cli.schemas.session_state import SessionState

logger = logging.getLogger(__name__)

_RAISE_DIR_NAME = ".raise"
_SESSION_STATE_YAML = "session-state.yaml"

# New path: personal directory (gitignored, per-developer)
SESSION_STATE_REL_PATH = (
    Path(_RAISE_DIR_NAME) / "rai" / "personal" / _SESSION_STATE_YAML
)

# Legacy path for migration
_LEGACY_SESSION_STATE_REL_PATH = Path(_RAISE_DIR_NAME) / "rai" / _SESSION_STATE_YAML


class StaleWriteError(Exception):
    """Raised when a session state write would overwrite newer data."""

    def __init__(self, path: Path, on_disk: str, incoming: str) -> None:
        super().__init__(
            f"Stale write rejected: {path} (on-disk={on_disk}, incoming={incoming})"
        )
        self.path = path
        self.on_disk_timestamp = on_disk
        self.incoming_timestamp = incoming


def get_session_state_path(project_path: Path, session_id: str | None = None) -> Path:
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


def migrate_flat_to_session(project_path: Path, session_id: str) -> bool:
    """One-time migration from flat layout to per-session directory.

    Moves:
    - personal/session-state.yaml → personal/sessions/{target_id}/state.yaml
    - personal/telemetry/signals.jsonl → personal/sessions/{target_id}/signals.jsonl

    The target directory is determined by last_session.id in the flat state file
    (the session the state actually belongs to). Falls back to session_id if
    last_session.id is not available. This prevents orphan directories.

    Args:
        project_path: Absolute path to the project root.
        session_id: Fallback session ID when last_session.id is unavailable.

    Returns:
        True if migration occurred, False if nothing to migrate.
    """
    personal_dir = project_path / _RAISE_DIR_NAME / "rai" / "personal"
    flat_state = personal_dir / _SESSION_STATE_YAML
    flat_signals = personal_dir / "telemetry" / "signals.jsonl"

    # Nothing to migrate
    if not flat_state.exists() and not flat_signals.exists():
        return False

    # Determine target ID from flat state's last_session.id
    target_id = session_id
    if flat_state.exists():
        try:
            content = yaml.safe_load(flat_state.read_text(encoding="utf-8"))
            if isinstance(content, dict) and "last_session" in content:
                last = cast("object", content["last_session"])
                if isinstance(last, dict) and "id" in last:
                    last_id = cast("object", last["id"])
                    if isinstance(last_id, str) and last_id:
                        target_id = last_id
        except (yaml.YAMLError, OSError):
            pass  # Fall back to passed session_id

    # Don't migrate if session dir already exists
    session_dir = get_session_dir(target_id, project_path)
    if session_dir.exists():
        return False

    session_dir.mkdir(parents=True, exist_ok=True)

    if flat_state.exists():
        shutil.move(str(flat_state), str(session_dir / "state.yaml"))
        logger.info("Migrated state: %s → %s/state.yaml", flat_state, session_dir)

    if flat_signals.exists():
        shutil.move(str(flat_signals), str(session_dir / "signals.jsonl"))
        logger.info(
            "Migrated signals: %s → %s/signals.jsonl", flat_signals, session_dir
        )

    return True


def cleanup_session_dir(project_path: Path, session_id: str) -> None:
    """Remove per-session directory after session close.

    Only removes the specific session directory. Does NOT remove
    shared files (index.jsonl, memory/).

    Args:
        project_path: Absolute path to the project root.
        session_id: Session ID whose directory to remove.
    """
    session_dir = get_session_dir(session_id, project_path)
    if session_dir.exists():
        shutil.rmtree(session_dir)
        logger.info("Cleaned up session dir: %s", session_dir)


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

    Uses FilesystemAdapter for atomic write semantics.
    Includes timestamp protection: rejects writes when the incoming
    ``last_modified`` is older than the on-disk value (RAISE-697).

    Args:
        project_path: Absolute path to the project root.
        state: The session state to save.
        session_id: Optional session ID for per-session isolation.

    Raises:
        StaleWriteError: If on-disk state has a newer last_modified than incoming.
    """
    state_path = get_session_state_path(project_path, session_id)
    rel_path = state_path.relative_to(project_path)

    # Timestamp protection: reject stale overwrites (RAISE-697)
    if state_path.exists():
        existing = load_session_state(project_path, session_id)
        if (
            existing
            and existing.last_modified
            and state.last_modified
            and datetime.fromisoformat(state.last_modified)
            < datetime.fromisoformat(existing.last_modified)
        ):
            raise StaleWriteError(
                state_path, existing.last_modified, state.last_modified
            )

    # Stamp outgoing data
    state = state.model_copy(update={"last_modified": datetime.now(UTC).isoformat()})
    data = state.model_dump(mode="json")
    content = yaml.dump(
        data, default_flow_style=False, allow_unicode=True, sort_keys=False
    )

    adapter = FilesystemAdapter(root=project_path)
    adapter.write(rel_path, content)
    logger.debug("Saved session state: %s", state_path)
