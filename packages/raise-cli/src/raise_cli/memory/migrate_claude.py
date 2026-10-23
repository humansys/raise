"""Migrate flat Claude Code memory files into mission-scoped subdirectories.

Moves files from ``memory/*.md`` into ``_global/``, ``missions/{id}/``,
or ``_unassigned/`` based on frontmatter ``type`` field and optional
epic→mission mapping.
"""

from __future__ import annotations

import logging
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from raise_cli.memory.memory_index import extract_frontmatter, regenerate_memory_index

_logger = logging.getLogger(__name__)

_GLOBAL_TYPES = frozenset({"user", "feedback", "reference"})


@dataclass
class MigrationPlan:
    """Planned file movements for a memory migration."""

    to_global: list[tuple[Path, str]] = field(
        default_factory=lambda: list[tuple[Path, str]]()
    )
    to_missions: list[tuple[Path, str, str]] = field(
        default_factory=lambda: list[tuple[Path, str, str]]()
    )
    to_unassigned: list[tuple[Path, str]] = field(
        default_factory=lambda: list[tuple[Path, str]]()
    )
    skipped: list[tuple[Path, str]] = field(
        default_factory=lambda: list[tuple[Path, str]]()
    )

    @property
    def total_moves(self) -> int:
        """Count of files that will be moved."""
        return len(self.to_global) + len(self.to_missions) + len(self.to_unassigned)

    def format_summary(self) -> str:
        """Format a human-readable migration summary."""
        total = (
            len(self.to_global)
            + len(self.to_missions)
            + len(self.to_unassigned)
            + len(self.skipped)
        )
        lines = [
            f"Migration plan for {total} memory files:",
            f"  → _global/:      {len(self.to_global)} files",
            f"  → missions/:     {len(self.to_missions)} files",
            f"  → _unassigned/:  {len(self.to_unassigned)} files",
        ]
        if self.skipped:
            lines.append(
                f"  → skipped:       {len(self.skipped)} files (no frontmatter)"
            )
        return "\n".join(lines)


def plan_migration(
    memory_dir: Path,
    epic_mission_map: dict[str, str] | None = None,
) -> MigrationPlan:
    """Classify flat memory files into target subdirectories."""
    plan = MigrationPlan()
    mapping = epic_mission_map or {}

    for md_file in sorted(memory_dir.glob("*.md")):
        if md_file.name == "MEMORY.md":
            continue

        frontmatter = extract_frontmatter(md_file)
        if frontmatter is None:
            plan.skipped.append((md_file, "no frontmatter"))
            continue

        mem_type = frontmatter.get("type", "").strip()
        if not mem_type:
            plan.skipped.append((md_file, "no type field"))
            continue

        if mem_type in _GLOBAL_TYPES:
            plan.to_global.append((md_file, mem_type))
            continue

        mission_id = _match_mission(md_file, frontmatter, mapping)
        if mission_id:
            plan.to_missions.append((md_file, mem_type, mission_id))
        else:
            plan.to_unassigned.append((md_file, mem_type))

    return plan


def execute_migration(
    memory_dir: Path,
    plan: MigrationPlan,
    *,
    active_mission_id: str | None = None,
) -> Path:
    """Execute the migration plan: backup, move files, regenerate index.

    Returns the backup directory path.
    """
    backup_dir = _create_backup(memory_dir)

    global_dir = memory_dir / "_global"
    global_dir.mkdir(exist_ok=True)

    unassigned_dir = memory_dir / "_unassigned"

    for src, _type in plan.to_global:
        _move_file(src, global_dir / src.name)

    for src, _type, mission_id in plan.to_missions:
        mission_dir = memory_dir / "missions" / mission_id
        mission_dir.mkdir(parents=True, exist_ok=True)
        _move_file(src, mission_dir / src.name)

    for src, _type in plan.to_unassigned:
        unassigned_dir.mkdir(exist_ok=True)
        _move_file(src, unassigned_dir / src.name)

    regenerate_memory_index(memory_dir, active_mission_id=active_mission_id)

    return backup_dir


def _create_backup(memory_dir: Path) -> Path:
    """Create a timestamped backup of all flat .md files."""
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    backup_dir = memory_dir / "_backup" / timestamp
    backup_dir.mkdir(parents=True, exist_ok=True)

    for md_file in sorted(memory_dir.glob("*.md")):
        shutil.copy2(md_file, backup_dir / md_file.name)

    return backup_dir


def _move_file(src: Path, dst: Path) -> None:
    """Move a file, overwriting destination if it exists."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst))


def _match_mission(
    path: Path,
    frontmatter: dict[str, str],
    mapping: dict[str, str],
) -> str | None:
    """Try to match a memory file to a mission via epic→mission mapping."""
    filename = path.stem.lower()
    description = frontmatter.get("description", "").lower()
    name = frontmatter.get("name", "").lower()
    combined = f"{filename} {name} {description}"

    for epic_key, mission_id in mapping.items():
        if epic_key.lower() in combined:
            return mission_id

    return None
