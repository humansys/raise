"""Terminal identity resolution and binding table.

Provides a stable per-terminal key (CC PID) for mission isolation
across concurrent Claude Code sessions on the same repo.

Architecture: E2491 Mission Primitive, S2491.13
"""

from __future__ import annotations

import json
import logging
import os
import platform
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from raise_cli.compat import file_lock, file_unlock
from raise_cli.core.files import atomic_write

logger = logging.getLogger(__name__)

_BINDINGS_FILE = "_terminal_bindings.json"


@dataclass(frozen=True)
class TerminalInfo:
    """Identity of a CC terminal instance."""

    pid: int
    tty: str | None
    key: str


def resolve_terminal_id(*, pid: int | None = None) -> TerminalInfo:
    """Resolve the terminal identity for the current CC session.

    Uses CC PID as the stable key. On Linux, enriches with TTY
    from /proc/$PID/stat for human-readable display.

    Args:
        pid: Override PID (for testing). Defaults to os.getppid().
    """
    resolved_pid = pid if pid is not None else os.getppid()
    tty = _resolve_tty(resolved_pid) if platform.system() == "Linux" else None
    return TerminalInfo(pid=resolved_pid, tty=tty, key=str(resolved_pid))


def _resolve_tty(pid: int) -> str | None:
    """Resolve TTY from /proc/$PID/stat field 7 (tty_nr)."""
    stat_path = Path(f"/proc/{pid}/stat")
    if not stat_path.exists():
        return None
    try:
        fields = stat_path.read_text().split()
        tty_nr = int(fields[6])
        if tty_nr == 0:
            return None
        pts_nr = tty_nr & 0xFF
        return f"/dev/pts/{pts_nr}"
    except (IndexError, ValueError, OSError):
        return None


class TerminalBindingTable:
    """Per-terminal mission bindings stored in a shared JSON file.

    File location: ``{sessions_dir}/_terminal_bindings.json``

    Keyed by CC PID (string). Uses file_lock for concurrent safety.
    Stale entries (dead PIDs) cleaned on read (Linux only).
    """

    def __init__(self, sessions_dir: Path) -> None:
        self._path = sessions_dir / _BINDINGS_FILE

    def get_mission(self, pid_key: str) -> str | None:
        """Return the mission_id bound to this terminal, or None."""
        bindings = self.read_all(cleanup_stale=False)
        entry = bindings.get(pid_key)
        return entry["mission_id"] if entry else None

    def read_all(self, *, cleanup_stale: bool = True) -> dict[str, dict[str, Any]]:
        """Read all bindings, optionally cleaning stale PIDs on Linux."""
        if not self._path.exists():
            return {}
        try:
            raw: object = json.loads(self._path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            logger.warning(
                "Corrupt terminal bindings at %s — returning empty", self._path
            )
            return {}
        if not isinstance(raw, dict):
            return {}
        result: dict[str, dict[str, Any]] = {
            str(k): v for k, v in raw.items() if isinstance(v, dict)
        }
        if cleanup_stale and platform.system() == "Linux":
            cleaned = {
                pid: info
                for pid, info in result.items()
                if Path(f"/proc/{pid}").exists()
            }
            if len(cleaned) < len(result):
                self._write_raw(cleaned)
            return cleaned
        return result

    def write(
        self,
        pid_key: str,
        *,
        mission_id: str,
        tty: str | None = None,
        session_id: str | None = None,
        branch: str | None = None,
    ) -> None:
        """Write or update a terminal binding (atomic read-modify-write)."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if not self._path.exists():
            self._path.write_text("{}\n", encoding="utf-8")
        with self._path.open("r+", encoding="utf-8") as fh:
            file_lock(fh)
            try:
                try:
                    bindings: dict[str, Any] = json.load(fh)
                except json.JSONDecodeError:
                    bindings = {}
                bindings[pid_key] = {
                    "mission_id": mission_id,
                    "tty": tty,
                    "session_id": session_id,
                    "branch": branch,
                    "updated_at": datetime.now(UTC).isoformat(),
                }
                self._write_raw(bindings)
            finally:
                file_unlock(fh)

    def _write_raw(self, data: dict[str, Any]) -> None:
        content = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
        atomic_write(self._path, content)
