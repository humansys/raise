"""Target classification helpers for the reliability lens (RAISE-11490).

``target_from_paths`` applies the product-wins rule to a list of changed file paths.
``changed_paths`` fetches changed files for a commit via git diff-tree.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from raise_cli.reliability.models import Target

__all__ = ["changed_paths", "target_from_paths"]

# ---------------------------------------------------------------------------
# Path classification predicates
# ---------------------------------------------------------------------------

# Extension sets for config files
_CONFIG_EXTENSIONS = frozenset(
    {".toml", ".yaml", ".yml", ".json", ".cfg", ".ini", ".lock", ".env"}
)

# Doc file extensions
_DOC_EXTENSIONS = frozenset({".md", ".rst", ".txt"})


def _is_test_path(path: str) -> bool:
    """Return True if the path belongs to a test file.

    A path is a test if it lives under a 'tests/' or 'test/' directory (at any
    depth), or if its basename starts with 'test_' or ends with '_test.py'.
    """
    parts = path.replace("\\", "/").split("/")
    basename = parts[-1]

    # Check any directory component
    for part in parts[:-1]:
        if part in {"tests", "test"}:
            return True

    # Check basename
    return basename.startswith("test_") or basename.endswith("_test.py")


def _is_doc_path(path: str) -> bool:
    """Return True if the path belongs to documentation."""
    parts = path.replace("\\", "/").split("/")
    basename = parts[-1]

    # Under docs/ directory
    if parts[0] in {"docs", "doc"}:
        return True

    # Known doc filenames at any depth
    if basename.upper() in {"README.MD", "README", "CHANGELOG.MD", "CHANGELOG"}:
        return True

    # Markdown/RST extension
    _, ext = os.path.splitext(basename)
    return ext.lower() in _DOC_EXTENSIONS


def _is_config_path(path: str) -> bool:
    """Return True if the path is a configuration file.

    Config files are:
    - Files with config-only extensions (toml, yaml, json, cfg, ini, lock, env)
      located at the root or in well-known config directories.
    - Under '.raise/', '.github/', 'config/' directories.
    """
    parts = path.replace("\\", "/").split("/")
    basename = parts[-1]

    # Well-known config directories
    if parts[0] in {".raise", ".github", "config", ".circleci"}:
        return True

    # Extension-based detection — only for shallow paths (root or 1 level deep)
    _, ext = os.path.splitext(basename)
    return ext.lower() in _CONFIG_EXTENSIONS and len(parts) <= 2


def _is_product_path(path: str) -> bool:
    """Return True if path is a product source file (non-test, non-doc, non-config)."""
    if _is_test_path(path):
        return False
    if _is_doc_path(path):
        return False
    if _is_config_path(path):
        return False

    # Must be a Python (or other source) file
    _, ext = os.path.splitext(path)
    return bool(ext) and ext.lower() not in _DOC_EXTENSIONS | _CONFIG_EXTENSIONS


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def target_from_paths(paths: list[str]) -> Target:
    """Classify a commit's changed paths to a single Target using the product-wins rule.

    Priority (first match wins):
    1. ANY path is product-source → PRODUCT
    2. ALL paths are tests → TEST
    3. ALL paths are config → CONFIG
    4. ALL paths are docs → DOCS
    5. Otherwise → OTHER

    Args:
        paths: List of changed file paths for a single commit.

    Returns:
        The dominant Target classification.
    """
    if not paths:
        return Target.OTHER

    # Product-wins rule: one product file → PRODUCT
    if any(_is_product_path(p) for p in paths):
        return Target.PRODUCT

    # Unanimous category checks
    if all(_is_test_path(p) for p in paths):
        return Target.TEST

    if all(_is_config_path(p) for p in paths):
        return Target.CONFIG

    if all(_is_doc_path(p) for p in paths):
        return Target.DOCS

    return Target.OTHER


def changed_paths(repo_path: Path, sha: str) -> list[str]:
    """Return the list of files changed by a commit.

    Uses ``git diff-tree --no-commit-id -r --name-only <sha>`` which is
    efficient (no diff content) and works for all commit types including
    initial commits.

    Args:
        repo_path: Path to the git repository root.
        sha: Commit SHA to inspect.

    Returns:
        List of changed file paths (relative to the repo root).
        Empty list on error (e.g. root commit with no parent).
    """
    result = subprocess.run(
        ["git", "diff-tree", "--no-commit-id", "-r", "--name-only", sha],
        cwd=str(repo_path),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return []
    return [line for line in result.stdout.splitlines() if line.strip()]
