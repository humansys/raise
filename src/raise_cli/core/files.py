"""File and directory utilities.

Shared functions for file system operations used across the codebase.
"""

from __future__ import annotations

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
