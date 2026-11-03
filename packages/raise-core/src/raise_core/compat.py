"""Cross-platform compatibility utilities for raise-core."""

from __future__ import annotations

from pathlib import Path


def portable_path(path: Path, relative_to: Path) -> str:
    """Return forward-slash relative path string for serialization.

    Always uses forward slashes regardless of OS, ensuring consistent
    path strings in JSON, graph data, and other serialized formats.
    """
    return path.relative_to(relative_to).as_posix()
