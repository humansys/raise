"""PID management and process lifecycle for worktree dev stacks."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path


class DevProcessError(Exception):
    """Raised when a dev process operation fails."""


def _dev_dir(worktree_path: Path) -> Path:
    """Return (and create) the .raise/dev/ directory for PID and log files."""
    dev = worktree_path / ".raise" / "dev"
    dev.mkdir(parents=True, exist_ok=True)
    return dev


def write_pid(worktree_path: Path, service: str, pid: int) -> Path:
    """Write a PID file for a service."""
    path = _dev_dir(worktree_path) / f"{service}.pid"
    path.write_text(str(pid), encoding="utf-8")
    return path


def read_pid(worktree_path: Path, service: str) -> int | None:
    """Read a PID from file. Returns None if missing or corrupt."""
    path = _dev_dir(worktree_path) / f"{service}.pid"
    if not path.exists():
        return None
    try:
        return int(path.read_text(encoding="utf-8").strip())
    except ValueError:
        return None


def is_running(pid: int) -> bool:
    """Check if a process with the given PID is alive."""
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def start_process(
    cmd: list[str],
    worktree_path: Path,
    service: str,
    *,
    env: dict[str, str] | None = None,
) -> int:
    """Start a background process, write PID file, redirect output to log.

    Returns the PID of the started process.
    """
    dev = _dev_dir(worktree_path)
    log_file = dev / f"{service}.log"
    merged_env = {**os.environ, **(env or {})}

    with open(log_file, "w", encoding="utf-8") as log:
        proc = subprocess.Popen(
            cmd,
            stdout=log,
            stderr=subprocess.STDOUT,
            env=merged_env,
            cwd=str(worktree_path),
        )

    write_pid(worktree_path, service, proc.pid)
    return proc.pid


def kill_process(worktree_path: Path, service: str) -> bool:
    """Kill a process by reading its PID file. Returns True if killed."""
    pid = read_pid(worktree_path, service)
    if pid is None:
        return False
    if not is_running(pid):
        _cleanup_pid(worktree_path, service)
        return False
    try:
        os.kill(pid, 15)  # SIGTERM
    except OSError:
        return False
    _cleanup_pid(worktree_path, service)
    return True


def _cleanup_pid(worktree_path: Path, service: str) -> None:
    """Remove the PID file for a service."""
    path = _dev_dir(worktree_path) / f"{service}.pid"
    path.unlink(missing_ok=True)
