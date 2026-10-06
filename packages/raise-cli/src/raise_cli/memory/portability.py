"""CC Memory git portability — export/import between CC memory and git-tracked copy.

Architecture (ADR-027 local-first):
    ~/.claude/projects/{encoded}/memory/   ←── CC memory dir (machine-local)
            ↕  rai memory sync export/import
    .raise/rai/personal/memory/            ←── git-tracked copy

Usage:
    export_memory(project_root)   # CC memory → git-tracked copy
    import_memory(project_root)   # git-tracked copy → CC memory
"""

from __future__ import annotations

import re
import shutil
import time
from dataclasses import dataclass, field
from pathlib import Path

from raise_cli.config.paths import get_claude_memory_dir, get_personal_dir

# =============================================================================
# Secrets scan patterns
# =============================================================================

#: Patterns that indicate a file contains secret credentials.
#: Files matching ANY pattern are SKIPPED during export (not blocked).
SECRETS_PATTERNS: list[re.Pattern[str]] = [
    # OpenAI / Anthropic API keys: sk-<20+ chars>
    re.compile(r"sk-[A-Za-z0-9\-_]{20,}"),
    # GitHub personal access tokens: ghp_<36+ chars>
    re.compile(r"ghp_[A-Za-z0-9]{36,}"),
    # AWS access key IDs: AKIA<16 uppercase alphanums>
    re.compile(r"AKIA[0-9A-Z]{16}"),
    # Base64 blobs longer than 40 chars (potential encoded secrets)
    re.compile(r"[A-Za-z0-9+/=]{40,}"),
]

# Subdirectory under .raise/rai/personal/ where CC memory is mirrored
_PERSONAL_MEMORY_SUBDIR = "memory"


def _has_secret(content: str) -> bool:
    """Return True if content matches any secrets pattern."""
    return any(p.search(content) for p in SECRETS_PATTERNS)


def _get_personal_memory_dir(project_root: Path) -> Path:
    """Get .raise/rai/personal/memory/ for the project."""
    return get_personal_dir(project_root) / _PERSONAL_MEMORY_SUBDIR


# =============================================================================
# Result type
# =============================================================================


@dataclass
class SyncResult:
    """Result of an export or import operation.

    Attributes:
        copied: Files successfully copied (or that would be, in dry-run).
        skipped: Files skipped with reason (e.g., "secret detected", "dest newer").
        elapsed_ms: Elapsed time in milliseconds.
    """

    copied: list[Path] = field(default_factory=list)
    skipped: list[tuple[Path, str]] = field(default_factory=list)
    elapsed_ms: float = 0.0


# =============================================================================
# Export: CC memory → git-tracked personal/memory/
# =============================================================================


def export_memory(
    project_root: Path,
    dry_run: bool = False,
    secrets_scan: bool = True,
) -> SyncResult:
    """Export CC memory files to the git-tracked personal/memory/ directory.

    Args:
        project_root: Absolute path to the project root.
        dry_run: If True, report what would be copied without making changes.
        secrets_scan: If True (default), skip files containing secret patterns.

    Returns:
        SyncResult with lists of copied and skipped files and elapsed time.
    """
    start = time.monotonic()
    result = SyncResult()

    source_dir = get_claude_memory_dir(project_root)
    dest_dir = _get_personal_memory_dir(project_root)

    if not source_dir.exists():
        result.elapsed_ms = (time.monotonic() - start) * 1000
        return result

    for src_file in source_dir.rglob("*"):
        if not src_file.is_file():
            continue

        rel = src_file.relative_to(source_dir)
        dest_file = dest_dir / rel

        # Secrets scan
        if secrets_scan:
            try:
                content = src_file.read_text(encoding="utf-8", errors="replace")
            except OSError:
                result.skipped.append((src_file, "read error"))
                continue

            if _has_secret(content):
                result.skipped.append((src_file, "secret detected"))
                continue

        result.copied.append(src_file)

        if not dry_run:
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(src_file), str(dest_file))

    result.elapsed_ms = (time.monotonic() - start) * 1000
    return result


# =============================================================================
# Import: git-tracked personal/memory/ → CC memory
# =============================================================================


def import_memory(
    project_root: Path,
    dry_run: bool = False,
    overwrite: bool = False,
) -> SyncResult:
    """Import files from git-tracked personal/memory/ to CC memory directory.

    Merge strategy:
    - Default (LWW): skip destination file if it is newer than source.
    - overwrite=True: always copy regardless of mtime.

    Args:
        project_root: Absolute path to the project root.
        dry_run: If True, report what would be copied without making changes.
        overwrite: If True, force copy even if destination is newer.

    Returns:
        SyncResult with lists of copied and skipped files and elapsed time.
    """
    start = time.monotonic()
    result = SyncResult()

    source_dir = _get_personal_memory_dir(project_root)
    dest_dir = get_claude_memory_dir(project_root)

    if not source_dir.exists():
        result.elapsed_ms = (time.monotonic() - start) * 1000
        return result

    for src_file in source_dir.rglob("*"):
        if not src_file.is_file():
            continue

        rel = src_file.relative_to(source_dir)
        dest_file = dest_dir / rel

        # LWW: skip if destination exists and is newer
        if not overwrite and dest_file.exists():
            src_mtime = src_file.stat().st_mtime
            dest_mtime = dest_file.stat().st_mtime
            if dest_mtime >= src_mtime:
                result.skipped.append((src_file, "dest newer (LWW)"))
                continue

        result.copied.append(src_file)

        if not dry_run:
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(src_file), str(dest_file))

    result.elapsed_ms = (time.monotonic() - start) * 1000
    return result
