"""Last-used state persistence for the cockpit (S14777.4).

Persists the last-used worktree+agent combo to ~/.rai/cockpit-last.json
so `rai --last` can relaunch without the TUI.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

_STATE_FILE: Path = Path.home() / ".rai" / "cockpit-last.json"


@dataclass
class LastUsed:
    """Last-used worktree + agent combo."""

    worktree_id: str
    agent_key: str  # "c", "o", "h", "s"


def save_last(worktree_id: str, agent_key: str) -> None:
    """Persist last used worktree+agent to _STATE_FILE.

    Creates parent directories if needed. Overwrites any existing state.

    Args:
        worktree_id: The worktree ID that was launched.
        agent_key: Single-char agent key ("c", "o", "h", "s").
    """
    _STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    _STATE_FILE.write_text(
        json.dumps({"worktree_id": worktree_id, "agent_key": agent_key}),
        encoding="utf-8",
    )


def load_last() -> LastUsed | None:
    """Return last used combo from _STATE_FILE, or None if unavailable.

    Returns None when:
    - The file does not exist.
    - The file contains invalid JSON.
    - The JSON is missing required keys.

    Returns:
        LastUsed instance, or None.
    """
    if not _STATE_FILE.exists():
        return None
    try:
        data = json.loads(_STATE_FILE.read_text(encoding="utf-8"))
        return LastUsed(
            worktree_id=data["worktree_id"],
            agent_key=data["agent_key"],
        )
    except (json.JSONDecodeError, KeyError, TypeError):
        return None
