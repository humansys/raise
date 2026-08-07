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

    # Ensure .gitattributes has merge=union for append-only JSONL files
    ensure_gitattributes(project_root)

    # Scaffold .env.example with adapter credential placeholders (idempotent)
    _scaffold_env_example(project_root)

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


def _copy_patterns(
    base: Traversable, project_root: Path, result: BootstrapResult
) -> None:
    """Insert or merge base patterns into SQLite.

    First init: inserts all base patterns.
    Re-init: adds new, updates versioned, preserves project patterns.

    Args:
        base: importlib.resources Traversable for rai_base package.
        project_root: Project root directory.
        result: BootstrapResult to update.
    """
    import json

    from raise_cli.storage.connection import get_project_db, get_project_id
    from raise_cli.storage.schema import create_all

    source = base / "memory" / "patterns-base.jsonl"
    project_pid = get_project_id(project_root)
    conn = get_project_db(project_root)
    create_all(conn)

    base_lines = source.read_text(encoding="utf-8").strip().splitlines()
    added = 0
    updated = 0

    for line in base_lines:
        line = line.strip()
        if not line:
            continue
        bp = json.loads(line)
        pid = str(bp.get("id", ""))
        if not pid:
            continue

        existing = conn.execute(
            "SELECT version FROM patterns WHERE pattern_id = ?",
            (pid,),
        ).fetchone()

        if existing is None:
            context: list[str] = bp.get("context", []) or []
            conn.execute(
                "INSERT INTO patterns "
                "(project_id, pattern_id, type, content, context_json, learned_from, "
                "scope, base, version, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, 'project', 1, ?, ?)",
                (
                    project_pid,
                    pid,
                    bp.get("type", "process"),
                    bp.get("content", ""),
                    json.dumps(context),
                    bp.get("learned_from", ""),
                    bp.get("version", 1) or 1,
                    bp.get("created", ""),
                ),
            )
            added += 1
            logger.debug("Added base pattern: %s", pid)
        else:
            existing_version = existing[0] or 0
            package_version = bp.get("version", 0) or 0
            if package_version > existing_version:
                context: list[str] = bp.get("context", []) or []
                conn.execute(
                    "UPDATE patterns SET content=?, context_json=?, version=?, "
                    "updated_at=strftime('%Y-%m-%dT%H:%M:%SZ', 'now') "
                    "WHERE pattern_id=?",
                    (bp.get("content", ""), json.dumps(context), package_version, pid),
                )
                updated += 1
                logger.debug(
                    "Updated base pattern: %s v%d → v%d",
                    pid,
                    existing_version,
                    package_version,
                )

    conn.commit()
    result.patterns_added = added
    result.patterns_updated = updated
    result.patterns_copied = added > 0

    if added > 0 or updated > 0:
        result.files_copied.append("raise.db")
        logger.debug(
            "Merged base patterns into SQLite: %d added, %d updated", added, updated
        )
    else:
        result.files_skipped.append("raise.db (patterns current)")
        logger.debug("Base patterns already current in SQLite")


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


ENV_EXAMPLE_CONTENT = """\
# RaiSE adapter credentials
# Copy to .env and fill in your values.
# Never commit .env — it is gitignored.

# Jira
JIRA_URL=
JIRA_API_TOKEN=
JIRA_USERNAME=

# Confluence
CONFLUENCE_URL=
CONFLUENCE_API_TOKEN=
CONFLUENCE_USERNAME=
"""


def _scaffold_env_example(project_root: Path) -> bool:
    """Create .env.example in project root with adapter credential placeholders.

    Idempotent — never overwrites an existing file.

    Args:
        project_root: Project root directory.

    Returns:
        True if the file was created, False if it already existed.
    """
    dest = project_root / ".env.example"
    if dest.exists():
        return False
    dest.write_text(ENV_EXAMPLE_CONTENT, encoding="utf-8")
    logger.debug(_COPIED_LOG_MSG, dest)
    return True


_LEGACY_PERSONAL_COMMENT = "# RaiSE personal directory (per-developer, not shared)"
_LEGACY_PERSONAL_IGNORE = ".raise/rai/personal/"
_ENVIRONMENT_COMMENT = "# RaiSE environment files"


def _remove_legacy_managed_personal_ignore(content: str) -> tuple[str, bool]:
    """Remove the obsolete personal ignore only from RaiSE's legacy block."""
    lines = content.splitlines(keepends=True)
    for index, line in enumerate(lines):
        if line.rstrip("\r\n") != _LEGACY_PERSONAL_COMMENT:
            continue
        personal_index = index + 1
        if (
            personal_index >= len(lines)
            or lines[personal_index].rstrip("\r\n") != _LEGACY_PERSONAL_IGNORE
        ):
            continue

        del lines[personal_index]
        if personal_index >= len(lines) or not lines[personal_index].strip():
            del lines[index]
            if index > 0 and not lines[index - 1].strip():
                del lines[index - 1]
        else:
            newline = "\n" if line.endswith("\n") else ""
            lines[index] = f"{_ENVIRONMENT_COMMENT}{newline}"
        return "".join(lines), True
    return content, False


def ensure_gitignore(project_root: Path) -> bool:
    """Ensure .gitignore contains RaiSE environment entries.

    RaiSE v3 tracks ``.raise/rai/personal/``. This function migrates the exact
    obsolete ignore rule from RaiSE's legacy managed block, without removing a
    matching user-owned rule elsewhere. It also appends missing environment
    entries. Repeated runs are idempotent.

    Args:
        project_root: Project root directory.

    Returns:
        True if managed content changed, False if already current.
    """
    gitignore_path = project_root / ".gitignore"

    entries = [
        ".env",
        "!.env.example",
    ]

    # Read existing content (if any)
    existing_content = ""
    if gitignore_path.exists():
        existing_content = gitignore_path.read_text(encoding="utf-8")
    existing_content, removed_legacy_rule = _remove_legacy_managed_personal_ignore(
        existing_content
    )

    # Check which entries are missing
    existing_lines = {line.strip() for line in existing_content.splitlines()}
    missing = [e for e in entries if e not in existing_lines]

    if not missing:
        if removed_legacy_rule:
            gitignore_path.write_text(existing_content, encoding="utf-8")
            logger.debug("Removed obsolete RaiSE personal ignore from .gitignore")
            return True
        logger.debug("All RaiSE gitignore entries already present")
        return False

    # Build block to append
    block_lines = [
        "",
        _ENVIRONMENT_COMMENT,
    ]
    block_lines.extend(missing)
    block_lines.append("")

    block = "\n".join(block_lines)

    # Ensure file ends with newline before appending
    if existing_content and not existing_content.endswith("\n"):
        block = "\n" + block

    gitignore_path.write_text(existing_content + block, encoding="utf-8")

    logger.debug("Added RaiSE entries to .gitignore: %s", missing)
    return True


def ensure_gitattributes(project_root: Path) -> bool:
    """Ensure .gitattributes contains merge=union for append-only JSONL files.

    Appends a RaiSE-managed block to the project .gitattributes if the entries
    are not already present. Idempotent — running multiple times will not
    create duplicate entries.

    Args:
        project_root: Project root directory.

    Returns:
        True if entries were added, False if already present.
    """
    gitattributes_path = project_root / ".gitattributes"

    entries = [
        ".raise/rai/memory/calibration.jsonl merge=union",
        ".raise/rai/memory/sessions/index.jsonl merge=union",
    ]

    existing_content = ""
    if gitattributes_path.exists():
        existing_content = gitattributes_path.read_text(encoding="utf-8")

    existing_lines = {line.strip() for line in existing_content.splitlines()}
    missing = [e for e in entries if e not in existing_lines]

    if not missing:
        logger.debug("All RaiSE gitattributes entries already present")
        return False

    block_lines = [
        "",
        "# RaiSE append-only JSONL files — merge=union avoids conflicts on concurrent appends",
    ]
    block_lines.extend(missing)
    block_lines.append("")

    block = "\n".join(block_lines)

    if existing_content and not existing_content.endswith("\n"):
        block = "\n" + block

    with gitattributes_path.open("a", encoding="utf-8") as f:
        f.write(block)

    logger.debug("Added RaiSE entries to .gitattributes: %s", missing)
    return True


def _ensure_personal_dir(project_root: Path) -> None:
    """Ensure .raise/rai/personal/ exists with a .gitkeep file.

    RaiSE v3 tracks the personal directory, including the Git-portable memory
    copy. The .gitkeep ensures the directory structure exists after ``rai init``
    before any subsystem creates files.

    Args:
        project_root: Project root directory.
    """
    personal_dir = get_personal_dir(project_root)
    personal_dir.mkdir(parents=True, exist_ok=True)
    gitkeep = personal_dir / ".gitkeep"
    if not gitkeep.exists():
        gitkeep.touch()
        logger.debug("Created: %s", gitkeep)


# =========================================================================
# Standalone sync functions (for auto-upgrade on session start)
# =========================================================================


def sync_base_patterns(project_root: Path) -> tuple[int, int]:
    """Sync base patterns from package to project DB.

    Callable without BootstrapResult — used by session start auto-upgrade.

    Returns:
        (added, updated) counts.
    """
    base = files("raise_cli.rai_base")
    result = BootstrapResult()
    _copy_patterns(base, project_root, result)
    return result.patterns_added, result.patterns_updated


def sync_methodology(project_root: Path) -> bool:
    """Sync methodology.yaml from package, overwriting if package version is newer.

    Compares the ``version:`` field in the installed file vs the package file.
    If package version > installed version (or file missing), overwrites.

    Returns:
        True if file was updated.
    """
    import yaml

    base = files("raise_cli.rai_base")
    source = base / "framework" / "methodology.yaml"
    package_content = source.read_text(encoding="utf-8")
    package_data = yaml.safe_load(package_content)
    package_version = package_data.get("version", 0) or 0

    framework_dir = get_framework_dir(project_root)
    dest = framework_dir / "methodology.yaml"

    if dest.exists():
        try:
            installed_data = yaml.safe_load(dest.read_text(encoding="utf-8"))
            installed_version = (installed_data or {}).get("version", 0) or 0
        except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
            installed_version = 0

        if package_version <= installed_version:
            logger.debug("Methodology already current (v%d)", installed_version)
            return False

    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(package_content, encoding="utf-8")
    logger.debug("Methodology updated to v%d", package_version)
    return True
