"""Migration module for multi-developer memory architecture.

Migrates session, telemetry, and calibration data from project directory
to personal directory for proper data separation.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path

_INDEX_JSONL = "index.jsonl"
_SIGNALS_JSONL = "signals.jsonl"
_CALIBRATION_JSONL = "calibration.jsonl"


@dataclass
class MigrationResult:
    """Result of a migration operation.

    Attributes:
        success: Whether migration completed without errors.
        sessions_migrated: Number of session entries migrated.
        telemetry_migrated: Number of telemetry entries migrated.
        calibration_migrated: Number of calibration entries migrated.
        message: Status message describing the migration.
        dry_run: Whether this was a dry run (no actual changes).
    """

    success: bool
    sessions_migrated: int = 0
    telemetry_migrated: int = 0
    calibration_migrated: int = 0
    message: str = ""
    dry_run: bool = False
    skipped_items: list[str] = field(default_factory=lambda: [])

    def summary(self) -> str:
        """Generate human-readable summary of migration."""
        prefix = "Would migrate" if self.dry_run else "Migrated"

        parts: list[str] = []
        if self.sessions_migrated > 0:
            parts.append(f"{self.sessions_migrated} sessions")
        if self.telemetry_migrated > 0:
            parts.append(f"{self.telemetry_migrated} telemetry")
        if self.calibration_migrated > 0:
            parts.append(f"{self.calibration_migrated} calibration")

        if not parts:
            return "Nothing to migrate"

        summary = f"{prefix}: {', '.join(parts)}"
        if self.dry_run:
            summary += " (dry run)"
        return summary


def _count_jsonl_entries(file_path: Path) -> int:
    """Count the number of valid JSON entries in a JSONL file."""
    if not file_path.exists():
        return 0

    count = 0
    with file_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    json.loads(line)
                    count += 1
                except json.JSONDecodeError:
                    pass
    return count


def _has_content(file_path: Path) -> bool:
    """Check if a JSONL file has any valid entries."""
    return _count_jsonl_entries(file_path) > 0


def needs_migration(
    memory_dir: Path,
    personal_dir: Path | None = None,
    rai_dir: Path | None = None,
) -> bool:
    """Check if migration from project to personal is needed.

    Migration is needed when:
    - Project has sessions in memory/sessions/ AND personal doesn't have sessions
    - Project has telemetry in rai/telemetry/ AND personal doesn't have telemetry
    - Project has calibration in memory/calibration.jsonl AND personal doesn't

    Args:
        memory_dir: Path to .raise/rai/memory/ directory.
        personal_dir: Path to .raise/rai/personal/ directory.
            If None, derived from memory_dir.
        rai_dir: Path to .raise/rai/ directory (for telemetry).
            If None, derived from memory_dir.

    Returns:
        True if migration is needed, False otherwise.
    """
    if personal_dir is None:
        personal_dir = memory_dir.parent / "personal"

    if rai_dir is None:
        rai_dir = memory_dir.parent

    # Check for sessions
    project_sessions = memory_dir / "sessions" / _INDEX_JSONL
    personal_sessions = personal_dir / "sessions" / _INDEX_JSONL
    if _has_content(project_sessions) and not _has_content(personal_sessions):
        return True

    # Check for telemetry
    project_telemetry = rai_dir / "telemetry" / _SIGNALS_JSONL
    personal_telemetry = personal_dir / "telemetry" / _SIGNALS_JSONL
    if _has_content(project_telemetry) and not _has_content(personal_telemetry):
        return True

    # Check for calibration
    project_calibration = memory_dir / _CALIBRATION_JSONL
    personal_calibration = personal_dir / _CALIBRATION_JSONL
    return _has_content(project_calibration) and not _has_content(personal_calibration)


def _migrate_file(
    source: Path,
    dest: Path,
    dry_run: bool = False,
) -> int:
    """Migrate a single file from source to destination.

    Args:
        source: Source file path.
        dest: Destination file path.
        dry_run: If True, don't actually move files.

    Returns:
        Number of entries migrated.
    """
    if not source.exists():
        return 0

    count = _count_jsonl_entries(source)
    if count == 0:
        return 0

    if dry_run:
        return count

    # Create destination directory
    dest.parent.mkdir(parents=True, exist_ok=True)

    # Copy file to destination
    shutil.copy2(source, dest)

    # Rename source to backup
    backup_path = source.with_suffix(source.suffix + ".backup")
    source.rename(backup_path)

    return count


def migrate_to_personal(  # noqa: C901 -- complexity 11, refactor deferred
    memory_dir: Path,
    personal_dir: Path,
    rai_dir: Path | None = None,
    dry_run: bool = False,
) -> MigrationResult:
    """Migrate session, telemetry, and calibration data to personal directory.

    Copies data from project locations to personal directory, then renames
    originals to .backup files. Does not overwrite existing personal data.

    Args:
        memory_dir: Path to .raise/rai/memory/ directory.
        personal_dir: Path to .raise/rai/personal/ directory.
        rai_dir: Path to .raise/rai/ directory (for telemetry).
            If None, derived from memory_dir.
        dry_run: If True, report what would be migrated without making changes.

    Returns:
        MigrationResult with counts and status.
    """
    if rai_dir is None:
        rai_dir = memory_dir.parent

    result = MigrationResult(success=True, dry_run=dry_run)
    skipped: list[str] = []

    # Migrate sessions
    project_sessions = memory_dir / "sessions" / _INDEX_JSONL
    personal_sessions = personal_dir / "sessions" / _INDEX_JSONL
    if _has_content(personal_sessions):
        if _has_content(project_sessions):
            skipped.append("sessions (personal already exists)")
    else:
        result.sessions_migrated = _migrate_file(
            project_sessions, personal_sessions, dry_run
        )

    # Migrate telemetry
    project_telemetry = rai_dir / "telemetry" / _SIGNALS_JSONL
    personal_telemetry = personal_dir / "telemetry" / _SIGNALS_JSONL
    if _has_content(personal_telemetry):
        if _has_content(project_telemetry):
            skipped.append("telemetry (personal already exists)")
    else:
        result.telemetry_migrated = _migrate_file(
            project_telemetry, personal_telemetry, dry_run
        )

    # Migrate calibration
    project_calibration = memory_dir / _CALIBRATION_JSONL
    personal_calibration = personal_dir / _CALIBRATION_JSONL
    if _has_content(personal_calibration):
        if _has_content(project_calibration):
            skipped.append("calibration (personal already exists)")
    else:
        result.calibration_migrated = _migrate_file(
            project_calibration, personal_calibration, dry_run
        )

    # Build message
    total = (
        result.sessions_migrated
        + result.telemetry_migrated
        + result.calibration_migrated
    )

    if total == 0 and not skipped:
        result.message = "Nothing to migrate"
    elif total == 0 and skipped:
        result.message = f"Skipped: {', '.join(skipped)}"
    else:
        result.message = result.summary()
        if skipped:
            result.message += f" (skipped: {', '.join(skipped)})"

    result.skipped_items = skipped
    return result
