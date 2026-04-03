"""PID file management for daemon lifecycle.

Functions for writing, reading, validating, and cleaning up PID files.
Stale PID detection via kill -0 (works on macOS and Linux).
"""

from __future__ import annotations

import os
from pathlib import Path

DEFAULT_PID_PATH = Path(".rai/daemon.pid")


def write_pid(pid: int, path: Path = DEFAULT_PID_PATH) -> None:
    """Write a PID to file, creating parent directories if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{pid}\n")


def acquire_pid(pid: int, path: Path = DEFAULT_PID_PATH) -> int | None:
    """Atomically create PID file, returning None on success.

    Uses O_CREAT|O_EXCL for atomic creation. If the file already exists,
    checks whether the recorded PID is alive.

    Returns:
        None if the PID file was created (lock acquired).
        The existing alive PID if the file was already held.

    Raises:
        ValueError: If the existing PID file is corrupt (cleaned up).
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
        os.write(fd, f"{pid}\n".encode())
        os.close(fd)
        return None  # acquired
    except FileExistsError:
        # File exists — check if the PID inside is alive
        existing = read_pid(path)
        if existing is not None:
            return existing  # still alive
        # Stale/corrupt — read_pid cleaned it up, retry once
        try:
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
            os.write(fd, f"{pid}\n".encode())
            os.close(fd)
            return None
        except FileExistsError:
            # Another process won the race
            return read_pid(path)


def is_alive(pid: int) -> bool:
    """Check if a process is alive using kill -0."""
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        # Process exists but we can't signal it
        return True
    return True


def read_pid(path: Path = DEFAULT_PID_PATH) -> int | None:
    """Read PID from file, returning None if missing, corrupt, or stale.

    Cleans up the PID file if it's corrupt or stale.
    """
    if not path.exists():
        return None

    text = path.read_text().strip()
    try:
        pid = int(text)
    except (ValueError, TypeError):
        # Corrupt file — clean up
        path.unlink(missing_ok=True)
        return None

    if not is_alive(pid):
        # Stale PID — process is dead, clean up
        path.unlink(missing_ok=True)
        return None

    return pid


def remove(path: Path = DEFAULT_PID_PATH) -> None:
    """Remove PID file if it exists."""
    path.unlink(missing_ok=True)
