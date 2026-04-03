"""Bootstrap bundled base Rai assets into a project.

Copies identity, patterns, and methodology from the raise_cli.rai_base
package to the project's .raise/rai/ directory during `rai init`.

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

from raise_cli.config.paths import (
    get_framework_dir,
    get_identity_dir,
    get_memory_dir,
    get_personal_dir,
)

logger = logging.getLogger(__name__)

_COPIED_LOG_MSG = "Copied: %s"


class BootstrapResult(BaseModel):
    """Result of base Rai bootstrap operation."""

    identity_copied: bool = False
    patterns_copied: bool = False
    methodology_copied: bool = False
    base_version: str = ""
    already_existed: bool = False
    files_copied: list[str] = Field(default_factory=list)
    files_skipped: list[str] = Field(default_factory=list)
    patterns_added: int = 0
    patterns_updated: int = 0


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

    # Ensure personal directory exists with .gitkeep
    _ensure_personal_dir(project_root)

    # Ensure .gitignore has entries for personal/ephemeral paths
    ensure_gitignore(project_root)

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

    identity_files = ["core.yaml", "perspective.md"]
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
        logger.debug(_COPIED_LOG_MSG, dest)

    result.identity_copied = copied_any


def _copy_patterns(  # noqa: C901 -- complexity 12, refactor deferred
    base: Traversable, project_root: Path, result: BootstrapResult
) -> None:
    """Copy or merge base patterns to .raise/rai/memory/patterns.jsonl.

    First init: copies all base patterns (fresh install).
    Re-init: merges base patterns — adds new, updates versioned, preserves project patterns.

    Args:
        base: importlib.resources Traversable for rai_base package.
        project_root: Project root directory.
        result: BootstrapResult to update.
    """
    import json
    import tempfile

    memory_dir = get_memory_dir(project_root)
    dest = memory_dir / "patterns.jsonl"
    source = base / "memory" / "patterns-base.jsonl"

    if not dest.exists():
        # Fresh install: copy all base patterns
        content = source.read_text(encoding="utf-8")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
        result.files_copied.append(str(dest))
        result.patterns_copied = True
        logger.debug(_COPIED_LOG_MSG, dest)
        return

    # Re-init: merge base patterns into existing file
    existing_lines = dest.read_text(encoding="utf-8").strip().splitlines()
    existing_patterns: list[dict[str, object]] = []
    existing_by_id: dict[str, int] = {}  # id -> index in existing_patterns

    for line in existing_lines:
        line = line.strip()
        if not line:
            continue
        pattern = json.loads(line)
        idx = len(existing_patterns)
        existing_patterns.append(pattern)
        pid = str(pattern.get("id", ""))
        if pid:
            existing_by_id[pid] = idx

    # Read base patterns from package
    base_lines = source.read_text(encoding="utf-8").strip().splitlines()
    added = 0
    updated = 0

    for line in base_lines:
        line = line.strip()
        if not line:
            continue
        base_pattern = json.loads(line)
        pid = str(base_pattern.get("id", ""))
        if not pid:
            continue

        if pid not in existing_by_id:
            # New base pattern — append
            existing_patterns.append(base_pattern)
            existing_by_id[pid] = len(existing_patterns) - 1
            added += 1
            logger.debug("Added base pattern: %s", pid)
        else:
            # Existing — check version for upgrade
            idx = existing_by_id[pid]
            existing_version = int(str(existing_patterns[idx].get("version", 0)))
            package_version = int(str(base_pattern.get("version", 0)))
            if package_version > existing_version:
                existing_patterns[idx] = base_pattern
                updated += 1
                logger.debug(
                    "Updated base pattern: %s v%d → v%d",
                    pid,
                    existing_version,
                    package_version,
                )

    result.patterns_added = added
    result.patterns_updated = updated

    if added > 0 or updated > 0:
        # Write atomically: temp file + rename
        merged_content = "\n".join(json.dumps(p) for p in existing_patterns) + "\n"
        dest.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(
            dir=str(dest.parent), suffix=".tmp", prefix="patterns_"
        )
        try:
            Path(tmp_path).write_text(merged_content, encoding="utf-8")
            Path(tmp_path).replace(dest)
        except Exception:
            Path(tmp_path).unlink(missing_ok=True)
            raise
        finally:
            import contextlib
            import os

            with contextlib.suppress(OSError):
                os.close(fd)
        result.files_copied.append(str(dest))
        logger.debug(
            "Merged base patterns into %s: %d added, %d updated", dest, added, updated
        )
    else:
        result.files_skipped.append(str(dest))
        logger.debug("Base patterns already current: %s", dest)


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
    logger.debug(_COPIED_LOG_MSG, dest)


def ensure_gitignore(project_root: Path) -> bool:
    """Ensure .gitignore contains entries for RaiSE personal/ephemeral paths.

    Appends a RaiSE-managed block to the project .gitignore if the entries
    are not already present. Idempotent — running multiple times will not
    create duplicate entries.

    Args:
        project_root: Project root directory.

    Returns:
        True if entries were added, False if already present.
    """
    gitignore_path = project_root / ".gitignore"

    # Entries to ensure are present
    entries = [
        ".raise/rai/personal/",
    ]

    # Read existing content (if any)
    existing_content = ""
    if gitignore_path.exists():
        existing_content = gitignore_path.read_text(encoding="utf-8")

    # Check which entries are missing
    existing_lines = {line.strip() for line in existing_content.splitlines()}
    missing = [e for e in entries if e not in existing_lines]

    if not missing:
        logger.debug("All RaiSE gitignore entries already present")
        return False

    # Build block to append
    block_lines = [
        "",
        "# RaiSE personal directory (per-developer, not shared)",
    ]
    block_lines.extend(missing)
    block_lines.append("")

    block = "\n".join(block_lines)

    # Ensure file ends with newline before appending
    if existing_content and not existing_content.endswith("\n"):
        block = "\n" + block

    with gitignore_path.open("a", encoding="utf-8") as f:
        f.write(block)

    logger.debug("Added RaiSE entries to .gitignore: %s", missing)
    return True


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
