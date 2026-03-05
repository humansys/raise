"""Bootstrap bundled base Rai assets into a project.

Copies identity, patterns, and methodology from the rai_cli.rai_base
package to the project's .raise/rai/ directory during `raise init`.

Uses importlib.resources to read bundled files (Python 3.9+).
Per-file idempotency: existing files are never overwritten.

Example:
    from rai_cli.onboarding.bootstrap import bootstrap_rai_base

    result = bootstrap_rai_base(project_path)
    if result.identity_copied:
        print("Base identity installed")
"""

from __future__ import annotations

import logging
from importlib.resources import files
from importlib.resources.abc import Traversable
from pathlib import Path

from pydantic import BaseModel, Field

from rai_cli.config.paths import (
    get_framework_dir,
    get_identity_dir,
    get_memory_dir,
    get_personal_dir,
)

logger = logging.getLogger(__name__)


class BootstrapResult(BaseModel):
    """Result of base Rai bootstrap operation."""

    identity_copied: bool = False
    patterns_copied: bool = False
    methodology_copied: bool = False
    base_version: str = ""
    already_existed: bool = False
    files_copied: list[str] = Field(default_factory=list)
    files_skipped: list[str] = Field(default_factory=list)


def bootstrap_rai_base(project_root: Path) -> BootstrapResult:
    """Copy bundled base Rai assets to project .raise/rai/ directory.

    Copies identity files, base patterns, and methodology definition
    from the installed rai_cli.rai_base package. Uses per-file
    idempotency — existing files are never overwritten.

    Args:
        project_root: Project root directory.

    Returns:
        BootstrapResult with details of what was copied or skipped.
    """
    from rai_cli.rai_base import __version__ as base_version

    base = files("rai_cli.rai_base")
    result = BootstrapResult(base_version=base_version)

    # Copy identity files
    _copy_identity(base, project_root, result)

    # Copy patterns
    _copy_patterns(base, project_root, result)

    # Copy methodology
    _copy_methodology(base, project_root, result)

    # Ensure personal directory exists with .gitkeep
    _ensure_personal_dir(project_root)

    # Determine if everything already existed
    result.already_existed = len(result.files_copied) == 0

    return result


def _copy_identity(
    base: Traversable, project_root: Path, result: BootstrapResult
) -> None:
    """Copy base identity files to .raise/rai/identity/.

    Args:
        base: importlib.resources Traversable for rai_base package.
        project_root: Project root directory.
        result: BootstrapResult to update.
    """
    identity_dir = get_identity_dir(project_root)
    identity_base = base / "identity"

    identity_files = ["core.md", "perspective.md"]
    copied_any = False

    for filename in identity_files:
        dest = identity_dir / filename
        if dest.exists():
            result.files_skipped.append(str(dest))
            logger.debug("Skipped (exists): %s", dest)
            continue

        content = (identity_base / filename).read_text(encoding="utf-8")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
        result.files_copied.append(str(dest))
        copied_any = True
        logger.debug("Copied: %s", dest)

    result.identity_copied = copied_any


def _copy_patterns(
    base: Traversable, project_root: Path, result: BootstrapResult
) -> None:
    """Copy base patterns to .raise/rai/memory/patterns.jsonl.

    Args:
        base: importlib.resources Traversable for rai_base package.
        project_root: Project root directory.
        result: BootstrapResult to update.
    """
    memory_dir = get_memory_dir(project_root)
    dest = memory_dir / "patterns.jsonl"

    if dest.exists():
        result.files_skipped.append(str(dest))
        logger.debug("Skipped (exists): %s", dest)
        return

    source = base / "memory" / "patterns-base.jsonl"
    content = source.read_text(encoding="utf-8")

    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8")
    result.files_copied.append(str(dest))
    result.patterns_copied = True
    logger.debug("Copied: %s", dest)


def _copy_methodology(
    base: Traversable, project_root: Path, result: BootstrapResult
) -> None:
    """Copy methodology.yaml to .raise/rai/framework/.

    Args:
        base: importlib.resources Traversable for rai_base package.
        project_root: Project root directory.
        result: BootstrapResult to update.
    """
    framework_dir = get_framework_dir(project_root)
    dest = framework_dir / "methodology.yaml"

    if dest.exists():
        result.files_skipped.append(str(dest))
        logger.debug("Skipped (exists): %s", dest)
        return

    source = base / "framework" / "methodology.yaml"
    content = source.read_text(encoding="utf-8")

    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8")
    result.files_copied.append(str(dest))
    result.methodology_copied = True
    logger.debug("Copied: %s", dest)


def _ensure_personal_dir(project_root: Path) -> None:
    """Ensure .raise/rai/personal/ exists with a .gitkeep file.

    The personal directory is gitignored and stores per-developer data
    (sessions, telemetry, calibration). The .gitkeep ensures the directory
    structure exists after `rai init` before any subsystem creates files.

    Args:
        project_root: Project root directory.
    """
    personal_dir = get_personal_dir(project_root)
    personal_dir.mkdir(parents=True, exist_ok=True)
    gitkeep = personal_dir / ".gitkeep"
    if not gitkeep.exists():
        gitkeep.touch()
        logger.debug("Created: %s", gitkeep)
