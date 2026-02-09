"""Bootstrap bundled base Rai assets into a project.

Copies identity, patterns, and methodology from the raise_cli.rai_base
package to the project's .raise/rai/ directory during `raise init`.

Uses importlib.resources to read bundled files (Python 3.9+).
Per-file idempotency: existing files are never overwritten.

Example:
    from raise_cli.onboarding.bootstrap import bootstrap_rai_base

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

from raise_cli.config.paths import get_framework_dir, get_identity_dir, get_memory_dir

logger = logging.getLogger(__name__)


class BootstrapResult(BaseModel):
    """Result of base Rai bootstrap operation."""

    identity_copied: bool = False
    patterns_copied: bool = False
    methodology_copied: bool = False
    scripts_copied: bool = False
    base_version: str = ""
    already_existed: bool = False
    files_copied: list[str] = Field(default_factory=list)
    files_skipped: list[str] = Field(default_factory=list)


def bootstrap_rai_base(project_root: Path) -> BootstrapResult:
    """Copy bundled base Rai assets to project .raise/rai/ directory.

    Copies identity files, base patterns, and methodology definition
    from the installed raise_cli.rai_base package. Uses per-file
    idempotency — existing files are never overwritten.

    Args:
        project_root: Project root directory.

    Returns:
        BootstrapResult with details of what was copied or skipped.
    """
    from raise_cli.rai_base import __version__ as base_version

    base = files("raise_cli.rai_base")
    result = BootstrapResult(base_version=base_version)

    # Copy identity files
    _copy_identity(base, project_root, result)

    # Copy patterns
    _copy_patterns(base, project_root, result)

    # Copy methodology
    _copy_methodology(base, project_root, result)

    # Copy hook scripts
    _copy_scripts(base, project_root, result)

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

        content = (identity_base / filename).read_text()
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content)
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
    content = source.read_text()

    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content)
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
    content = source.read_text()

    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content)
    result.files_copied.append(str(dest))
    result.methodology_copied = True
    logger.debug("Copied: %s", dest)


def _copy_scripts(
    base: Traversable, project_root: Path, result: BootstrapResult
) -> None:
    """Copy hook scripts to .raise/scripts/.

    Skills reference these scripts in their Stop hooks for telemetry.
    Per-file idempotency — existing scripts are never overwritten.

    Args:
        base: importlib.resources Traversable for rai_base package.
        project_root: Project root directory.
        result: BootstrapResult to update.
    """
    scripts_dir = project_root / ".raise" / "scripts"
    scripts_base = base / "scripts"

    script_files = [
        "log-skill-complete.sh",
        "log-skill-start.sh",
        "log-session-event.sh",
        "log-artifact-created.sh",
        "log-error-event.sh",
    ]
    copied_any = False

    for filename in script_files:
        dest = scripts_dir / filename
        if dest.exists():
            result.files_skipped.append(str(dest))
            logger.debug("Skipped (exists): %s", dest)
            continue

        content = (scripts_base / filename).read_text()
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content)
        dest.chmod(0o755)
        result.files_copied.append(str(dest))
        copied_any = True
        logger.debug("Copied: %s", dest)

    result.scripts_copied = copied_any
