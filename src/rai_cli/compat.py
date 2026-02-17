"""Cross-platform compatibility layer.

Centralizes all platform-specific code so the rest of the codebase
never checks sys.platform directly. Pattern used by pip, poetry, virtualenv.

All platform guards live here. Import from compat, not from fcntl/msvcrt.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import IO

IS_WINDOWS = sys.platform == "win32"


def file_lock(f: IO[str], *, exclusive: bool = True) -> None:
    """Acquire a file lock. Uses fcntl on Unix, msvcrt on Windows."""
    if sys.platform == "win32":
        import msvcrt

        msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)
    else:
        import fcntl

        fcntl.flock(f.fileno(), fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH)


def file_unlock(f: IO[str]) -> None:
    """Release a file lock. Uses fcntl on Unix, msvcrt on Windows."""
    if sys.platform == "win32":
        import msvcrt

        msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
    else:
        import fcntl

        fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def portable_path(path: Path, relative_to: Path) -> str:
    """Return forward-slash relative path string for serialization.

    Always uses forward slashes regardless of OS, ensuring consistent
    path strings in JSON, graph data, and other serialized formats.
    """
    return path.relative_to(relative_to).as_posix()


def to_file_uri(path: Path) -> str:
    """Return correct file:// URI on any platform.

    Uses pathlib's as_uri() which handles Windows drive letters correctly.
    """
    return path.resolve().as_uri()


def secure_permissions(path: Path) -> None:
    """Set restrictive file permissions (0o600). No-op on Windows.

    On Windows, POSIX chmod has no effect. For true Windows ACL
    restriction, icacls would be needed — deferred until required.
    """
    if not IS_WINDOWS:
        path.chmod(0o600)
