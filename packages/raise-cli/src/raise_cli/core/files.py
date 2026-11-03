"""File and directory utilities.

Shared functions for file system operations used across the codebase.
"""

from __future__ import annotations

import os
from pathlib import Path

# Directories to exclude from scanning operations
EXCLUDED_DIRS: frozenset[str] = frozenset(
    {
        # Version control
        ".git",
        ".svn",
        ".hg",
        # Package managers
        "node_modules",
        # Python
        "__pycache__",
        ".tox",
        ".nox",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        "venv",
        ".venv",
        "env",
        ".env",
        # Build outputs
        "dist",
        "build",
        "target",
        # IDE
        ".idea",
        ".vscode",
    }
)


def should_exclude_dir(dir_path: Path) -> bool:
    """Check if a directory should be excluded from scanning.

    Excludes hidden directories (starting with .) and known non-project
    directories like node_modules, __pycache__, etc.

    Args:
        dir_path: Path to check.

    Returns:
        True if the directory should be excluded.

    Examples:
        >>> should_exclude_dir(Path("node_modules"))
        True
        >>> should_exclude_dir(Path(".git"))
        True
        >>> should_exclude_dir(Path("src"))
        False
    """
    name = dir_path.name
    # Exclude hidden directories (starting with .)
    if name.startswith("."):
        return True
    # Exclude known non-project directories
    return name in EXCLUDED_DIRS


def atomic_write(path: Path, content: str, *, encoding: str = "utf-8") -> None:
    """Write content to a file atomically via temp file + rename.

    Writes to a sibling ``.tmp`` file first, then uses :func:`os.replace`
    for an atomic rename. This prevents corruption if the process crashes
    mid-write.

    Args:
        path: Destination file path.
        content: Content to write.
        encoding: Text encoding (default ``utf-8``).
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding=encoding)
    os.replace(tmp, path)
