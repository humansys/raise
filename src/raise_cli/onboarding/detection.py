"""Project type detection for RaiSE initialization.

Detects whether a directory is greenfield (no code) or brownfield (existing code)
by counting source code files while excluding common non-project directories.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

# Common code file extensions to detect
CODE_EXTENSIONS: frozenset[str] = frozenset(
    {
        # Python
        ".py",
        # JavaScript/TypeScript
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".mjs",
        ".cjs",
        # JVM
        ".java",
        ".kt",
        ".scala",
        # Systems
        ".c",
        ".cpp",
        ".cc",
        ".cxx",
        ".h",
        ".hpp",
        ".rs",
        ".go",
        # Scripting
        ".rb",
        ".php",
        ".pl",
        ".pm",
        # .NET
        ".cs",
        ".fs",
        ".vb",
        # Other
        ".swift",
        ".m",
        ".mm",
        ".lua",
        ".r",
        ".R",
        ".jl",
        ".dart",
        ".ex",
        ".exs",
        ".erl",
        ".hrl",
        ".clj",
        ".cljs",
        ".elm",
        ".hs",
    }
)

# Directories to exclude from scanning
EXCLUDED_DIRS: frozenset[str] = frozenset(
    {
        "node_modules",
        "__pycache__",
        ".git",
        ".svn",
        ".hg",
        "dist",
        "build",
        "target",
        ".tox",
        ".nox",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        "venv",
        ".venv",
        "env",
        ".env",
        "vendor",
        "coverage",
        ".coverage",
        "htmlcov",
        ".eggs",
        "*.egg-info",
    }
)


class ProjectType(str, Enum):
    """Type of project based on existing code.

    Values:
        GREENFIELD: No existing code files (new project)
        BROWNFIELD: Has existing code files
    """

    GREENFIELD = "greenfield"
    BROWNFIELD = "brownfield"


@dataclass(frozen=True)
class DetectionResult:
    """Result of project type detection.

    Attributes:
        project_type: Whether the project is greenfield or brownfield.
        code_file_count: Number of code files detected.
    """

    project_type: ProjectType
    code_file_count: int


def _should_exclude_dir(dir_path: Path) -> bool:
    """Check if a directory should be excluded from scanning.

    Args:
        dir_path: Path to check.

    Returns:
        True if the directory should be excluded.
    """
    name = dir_path.name
    # Exclude hidden directories (starting with .)
    if name.startswith("."):
        return True
    # Exclude known non-project directories
    return name in EXCLUDED_DIRS


def count_code_files(directory: Path) -> int:
    """Count code files in a directory recursively.

    Excludes hidden directories, node_modules, __pycache__, etc.

    Args:
        directory: Root directory to scan.

    Returns:
        Number of code files found.
    """
    if not directory.is_dir():
        return 0

    count = 0
    try:
        for item in directory.iterdir():
            if item.is_dir():
                if not _should_exclude_dir(item):
                    count += count_code_files(item)
            elif item.is_file() and item.suffix in CODE_EXTENSIONS:
                count += 1
    except PermissionError:
        # Skip directories we can't access
        pass

    return count


def detect_project_type(directory: Path) -> DetectionResult:
    """Detect whether a directory is greenfield or brownfield.

    A greenfield project has no code files.
    A brownfield project has at least one code file.

    Args:
        directory: Directory to analyze.

    Returns:
        DetectionResult with project type and file count.
    """
    code_file_count = count_code_files(directory)

    if code_file_count == 0:
        project_type = ProjectType.GREENFIELD
    else:
        project_type = ProjectType.BROWNFIELD

    return DetectionResult(
        project_type=project_type,
        code_file_count=code_file_count,
    )
