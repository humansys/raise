"""Tests for memory migration module.

Tests the migration of session, telemetry, and calibration data
from project directory to personal directory for multi-developer support.
"""

from __future__ import annotations

from pathlib import Path

from raise_cli.memory.migration import (
    MigrationResult,
    migrate_to_personal,
    needs_migration,
)


class TestNeedsMigration:
    """Tests for detecting when migration is needed."""

    def test_needs_migration_no_project_sessions(self, tmp_path: Path) -> None:
        """Returns False when project has no sessions directory."""
        memory_dir = tmp_path / ".raise" / "rai" / "memory"
        memory_dir.mkdir(parents=True)

        result = needs_migration(memory_dir)

        assert result is False

    def test_needs_migration_empty_project_sessions(self, tmp_path: Path) -> None:
        """Returns False when project sessions directory is empty."""
        sessions_dir = tmp_path / ".raise" / "rai" / "memory" / "sessions"
        sessions_dir.mkdir(parents=True)

        result = needs_migration(tmp_path / ".raise" / "rai" / "memory")

        assert result is False

    def test_needs_migration_has_project_sessions(self, tmp_path: Path) -> None:
        """Returns True when project has sessions that need migration."""
        memory_dir = tmp_path / ".raise" / "rai" / "memory"
        sessions_dir = memory_dir / "sessions"
        sessions_dir.mkdir(parents=True)
        (sessions_dir / "index.jsonl").write_text(
            '{"id":"SES-001","topic":"Test session"}\n'
        )

        result = needs_migration(memory_dir)

        assert result is True

    def test_needs_migration_already_migrated(self, tmp_path: Path) -> None:
        """Returns False when personal directory already has sessions."""
        memory_dir = tmp_path / ".raise" / "rai" / "memory"
        personal_dir = tmp_path / ".raise" / "rai" / "personal"

        # Create sessions in both locations
        (memory_dir / "sessions").mkdir(parents=True)
        (memory_dir / "sessions" / "index.jsonl").write_text(
            '{"id":"SES-001","topic":"Old session"}\n'
        )
        (personal_dir / "sessions").mkdir(parents=True)
        (personal_dir / "sessions" / "index.jsonl").write_text(
            '{"id":"SES-001","topic":"Migrated session"}\n'
        )

        # Should not need migration if personal already exists with content
        result = needs_migration(memory_dir, personal_dir)

        assert result is False

    def test_needs_migration_has_telemetry(self, tmp_path: Path) -> None:
        """Returns True when project has telemetry that needs migration."""
        memory_dir = tmp_path / ".raise" / "rai" / "memory"
        telemetry_dir = memory_dir / "telemetry"
        telemetry_dir.mkdir(parents=True)
        (telemetry_dir / "signals.jsonl").write_text(
            '{"type":"session","timestamp":"2026-02-05"}\n'
        )

        # Note: telemetry is in .raise/rai/telemetry, not memory/telemetry
        # But we check for it via the rai_dir
        rai_dir = tmp_path / ".raise" / "rai"
        (rai_dir / "telemetry").mkdir(parents=True)
        (rai_dir / "telemetry" / "signals.jsonl").write_text(
            '{"type":"session","timestamp":"2026-02-05"}\n'
        )

        result = needs_migration(memory_dir, rai_dir=rai_dir)

        assert result is True


class TestMigrateToPersonal:
    """Tests for migrating data to personal directory."""

    def test_migrate_sessions(self, tmp_path: Path) -> None:
        """Migrates sessions from project to personal directory."""
        memory_dir = tmp_path / ".raise" / "rai" / "memory"
        personal_dir = tmp_path / ".raise" / "rai" / "personal"
        sessions_dir = memory_dir / "sessions"
        sessions_dir.mkdir(parents=True)

        session_content = '{"id":"SES-001","topic":"Test session"}\n{"id":"SES-002","topic":"Another session"}\n'
        (sessions_dir / "index.jsonl").write_text(session_content)

        result = migrate_to_personal(memory_dir, personal_dir)

        assert result.success is True
        assert result.sessions_migrated == 2
        assert (personal_dir / "sessions" / "index.jsonl").exists()
        assert (personal_dir / "sessions" / "index.jsonl").read_text(
            encoding="utf-8"
        ) == session_content

    def test_migrate_creates_backup(self, tmp_path: Path) -> None:
        """Creates backup of original files before migration."""
        memory_dir = tmp_path / ".raise" / "rai" / "memory"
        personal_dir = tmp_path / ".raise" / "rai" / "personal"
        sessions_dir = memory_dir / "sessions"
        sessions_dir.mkdir(parents=True)

        session_content = '{"id":"SES-001","topic":"Test session"}\n'
        (sessions_dir / "index.jsonl").write_text(session_content)

        result = migrate_to_personal(memory_dir, personal_dir)

        assert result.success is True
        # Original should be renamed to .backup
        assert (sessions_dir / "index.jsonl.backup").exists()
        # Original should not exist
        assert not (sessions_dir / "index.jsonl").exists()

    def test_migrate_telemetry(self, tmp_path: Path) -> None:
        """Migrates telemetry from project to personal directory."""
        rai_dir = tmp_path / ".raise" / "rai"
        memory_dir = rai_dir / "memory"
        personal_dir = rai_dir / "personal"
        telemetry_dir = rai_dir / "telemetry"

        memory_dir.mkdir(parents=True)
        telemetry_dir.mkdir(parents=True)

        telemetry_content = '{"type":"session","timestamp":"2026-02-05"}\n'
        (telemetry_dir / "signals.jsonl").write_text(telemetry_content)

        result = migrate_to_personal(memory_dir, personal_dir, rai_dir=rai_dir)

        assert result.success is True
        assert result.telemetry_migrated == 1
        assert (personal_dir / "telemetry" / "signals.jsonl").exists()
        assert (personal_dir / "telemetry" / "signals.jsonl").read_text(
            encoding="utf-8"
        ) == telemetry_content

    def test_migrate_calibration(self, tmp_path: Path) -> None:
        """Migrates calibration from project memory to personal directory."""
        memory_dir = tmp_path / ".raise" / "rai" / "memory"
        personal_dir = tmp_path / ".raise" / "rai" / "personal"
        memory_dir.mkdir(parents=True)

        calibration_content = '{"id":"CAL-001","feature":"F1.1","actual_min":30}\n'
        (memory_dir / "calibration.jsonl").write_text(calibration_content)

        result = migrate_to_personal(memory_dir, personal_dir)

        assert result.success is True
        assert result.calibration_migrated == 1
        assert (personal_dir / "calibration.jsonl").exists()
        assert (personal_dir / "calibration.jsonl").read_text(
            encoding="utf-8"
        ) == calibration_content

    def test_migrate_nothing_to_migrate(self, tmp_path: Path) -> None:
        """Returns success with zero counts when nothing to migrate."""
        memory_dir = tmp_path / ".raise" / "rai" / "memory"
        personal_dir = tmp_path / ".raise" / "rai" / "personal"
        memory_dir.mkdir(parents=True)

        result = migrate_to_personal(memory_dir, personal_dir)

        assert result.success is True
        assert result.sessions_migrated == 0
        assert result.telemetry_migrated == 0
        assert result.calibration_migrated == 0
        assert "Nothing to migrate" in result.message

    def test_migrate_preserves_existing_personal(self, tmp_path: Path) -> None:
        """Does not overwrite existing personal data."""
        memory_dir = tmp_path / ".raise" / "rai" / "memory"
        personal_dir = tmp_path / ".raise" / "rai" / "personal"

        # Create sessions in project
        (memory_dir / "sessions").mkdir(parents=True)
        (memory_dir / "sessions" / "index.jsonl").write_text(
            '{"id":"SES-001","topic":"Project session"}\n'
        )

        # Create sessions in personal (already migrated)
        (personal_dir / "sessions").mkdir(parents=True)
        (personal_dir / "sessions" / "index.jsonl").write_text(
            '{"id":"SES-002","topic":"Personal session"}\n'
        )

        result = migrate_to_personal(memory_dir, personal_dir)

        # Should skip migration, not overwrite
        assert result.success is True
        assert result.sessions_migrated == 0
        assert "skipped" in result.message.lower() or result.sessions_migrated == 0
        # Personal data should be unchanged
        assert "SES-002" in (personal_dir / "sessions" / "index.jsonl").read_text(
            encoding="utf-8"
        )

    def test_migrate_dry_run(self, tmp_path: Path) -> None:
        """Dry run reports what would be migrated without making changes."""
        memory_dir = tmp_path / ".raise" / "rai" / "memory"
        personal_dir = tmp_path / ".raise" / "rai" / "personal"
        sessions_dir = memory_dir / "sessions"
        sessions_dir.mkdir(parents=True)

        session_content = '{"id":"SES-001","topic":"Test session"}\n'
        (sessions_dir / "index.jsonl").write_text(session_content)

        result = migrate_to_personal(memory_dir, personal_dir, dry_run=True)

        assert result.success is True
        assert result.sessions_migrated == 1
        assert result.dry_run is True
        # Original file should still exist (no actual migration)
        assert (sessions_dir / "index.jsonl").exists()
        # Personal directory should not be created
        assert not personal_dir.exists()


class TestMigrationResult:
    """Tests for MigrationResult dataclass."""

    def test_migration_result_summary(self) -> None:
        """MigrationResult provides human-readable summary."""
        result = MigrationResult(
            success=True,
            sessions_migrated=5,
            telemetry_migrated=10,
            calibration_migrated=3,
            message="Migration complete",
            dry_run=False,
        )

        summary = result.summary()

        assert "5 sessions" in summary
        assert "10 telemetry" in summary
        assert "3 calibration" in summary

    def test_migration_result_dry_run_summary(self) -> None:
        """Dry run summary indicates it was a dry run."""
        result = MigrationResult(
            success=True,
            sessions_migrated=5,
            telemetry_migrated=0,
            calibration_migrated=0,
            message="Dry run complete",
            dry_run=True,
        )

        summary = result.summary()

        assert "dry run" in summary.lower() or "would migrate" in summary.lower()
