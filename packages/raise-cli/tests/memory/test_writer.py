"""Tests for memory writer module."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from raise_cli.memory.models import MemoryScope, PatternSubType
from raise_cli.memory.writer import (
    CalibrationInput,
    PatternInput,
    ReinforceResult,
    SessionInput,
    append_calibration,
    append_pattern,
    append_session,
    get_memory_dir_for_scope,
    get_next_id,
    reinforce_pattern,
    validate_session_index,
)


class TestGetNextId:
    """Tests for get_next_id function."""

    def test_empty_file_returns_001(self, tmp_path: Path) -> None:
        """First ID should be 001 when file is empty."""
        file_path = tmp_path / "test.jsonl"
        file_path.touch()

        result = get_next_id(file_path, "PAT")

        assert result == "PAT-001"

    def test_nonexistent_file_returns_001(self, tmp_path: Path) -> None:
        """First ID should be 001 when file doesn't exist."""
        file_path = tmp_path / "nonexistent.jsonl"

        result = get_next_id(file_path, "PAT")

        assert result == "PAT-001"

    def test_increments_from_existing(self, tmp_path: Path) -> None:
        """Should increment from highest existing ID."""
        file_path = tmp_path / "test.jsonl"
        file_path.write_text(
            '{"id": "PAT-001", "content": "first"}\n'
            '{"id": "PAT-005", "content": "fifth"}\n'
            '{"id": "PAT-003", "content": "third"}\n'
        )

        result = get_next_id(file_path, "PAT")

        assert result == "PAT-006"

    def test_handles_different_prefixes(self, tmp_path: Path) -> None:
        """Should only count IDs matching the prefix."""
        file_path = tmp_path / "test.jsonl"
        file_path.write_text(
            '{"id": "PAT-010", "content": "pattern"}\n'
            '{"id": "CAL-005", "content": "calibration"}\n'
        )

        result = get_next_id(file_path, "CAL")

        assert result == "CAL-006"

    def test_missing_file_with_sibling_dirs_uses_directory_fallback(
        self, tmp_path: Path
    ) -> None:
        """When index.jsonl missing, scan sibling dirs for max ID."""
        sessions_dir = tmp_path / "sessions"
        sessions_dir.mkdir()
        (sessions_dir / "SES-001").mkdir()
        (sessions_dir / "SES-024").mkdir()
        file_path = sessions_dir / "index.jsonl"

        result = get_next_id(file_path, "SES")

        assert result == "SES-025"

    def test_empty_file_with_sibling_dirs_uses_directory_fallback(
        self, tmp_path: Path
    ) -> None:
        """When index.jsonl empty, scan sibling dirs for max ID."""
        sessions_dir = tmp_path / "sessions"
        sessions_dir.mkdir()
        (sessions_dir / "SES-010").mkdir()
        file_path = sessions_dir / "index.jsonl"
        file_path.touch()

        result = get_next_id(file_path, "SES")

        assert result == "SES-011"

    def test_index_wins_when_higher_than_dirs(self, tmp_path: Path) -> None:
        """Index max takes precedence when higher than directory max."""
        sessions_dir = tmp_path / "sessions"
        sessions_dir.mkdir()
        (sessions_dir / "SES-005").mkdir()
        file_path = sessions_dir / "index.jsonl"
        file_path.write_text('{"id": "SES-020", "topic": "test"}\n')

        result = get_next_id(file_path, "SES")

        assert result == "SES-021"

    def test_dirs_win_when_higher_than_index(self, tmp_path: Path) -> None:
        """Directory max takes precedence when higher than index max."""
        sessions_dir = tmp_path / "sessions"
        sessions_dir.mkdir()
        (sessions_dir / "SES-030").mkdir()
        file_path = sessions_dir / "index.jsonl"
        file_path.write_text('{"id": "SES-005", "topic": "test"}\n')

        result = get_next_id(file_path, "SES")

        assert result == "SES-031"

    def test_directory_fallback_ignores_non_matching_dirs(self, tmp_path: Path) -> None:
        """Only directories matching PREFIX-NNN pattern are counted."""
        sessions_dir = tmp_path / "sessions"
        sessions_dir.mkdir()
        (sessions_dir / "SES-010").mkdir()
        (sessions_dir / "PAT-099").mkdir()
        (sessions_dir / "random-dir").mkdir()
        file_path = sessions_dir / "index.jsonl"

        result = get_next_id(file_path, "SES")

        assert result == "SES-011"


class TestAppendPattern:
    """Tests for append_pattern function."""

    def test_appends_pattern_successfully(self, tmp_path: Path) -> None:
        """Should append pattern and return success."""
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir()

        input_data = PatternInput(
            content="Test pattern content",
            sub_type=PatternSubType.PROCESS,
            context=["testing", "workflow"],
            learned_from="F1.1",
        )

        result = append_pattern(memory_dir, input_data)

        assert result.success is True
        assert result.id == "PAT-001"
        assert "patterns.jsonl" in result.file_path

        # Verify file content
        patterns_file = memory_dir / "patterns.jsonl"
        assert patterns_file.exists()
        content = patterns_file.read_text(encoding="utf-8")
        data = json.loads(content.strip())
        assert data["id"] == "PAT-001"
        assert data["content"] == "Test pattern content"
        assert data["context"] == ["testing", "workflow"]

    def test_auto_increments_id(self, tmp_path: Path) -> None:
        """Should auto-increment IDs."""
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir()
        patterns_file = memory_dir / "patterns.jsonl"
        patterns_file.write_text('{"id": "PAT-010", "content": "existing"}\n')

        input_data = PatternInput(content="New pattern")

        result = append_pattern(memory_dir, input_data)

        assert result.id == "PAT-011"

    def test_uses_custom_date(self, tmp_path: Path) -> None:
        """Should use custom date when provided."""
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir()

        input_data = PatternInput(content="Test")
        custom_date = date(2026, 1, 15)

        append_pattern(memory_dir, input_data, created=custom_date)

        patterns_file = memory_dir / "patterns.jsonl"
        data = json.loads(patterns_file.read_text(encoding="utf-8").strip())
        assert data["created"] == "2026-01-15"


class TestAppendCalibration:
    """Tests for append_calibration function."""

    def test_appends_calibration_with_ratio(self, tmp_path: Path) -> None:
        """Should calculate ratio when estimated and actual provided."""
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir()

        input_data = CalibrationInput(
            story="F3.5",
            name="Skills Integration",
            size="XS",
            sp=2,
            estimated_min=60,
            actual_min=20,
            kata_cycle=True,
            notes="Fast implementation",
        )

        result = append_calibration(memory_dir, input_data)

        assert result.success is True
        assert result.id == "CAL-001"

        cal_file = memory_dir / "calibration.jsonl"
        data = json.loads(cal_file.read_text(encoding="utf-8").strip())
        assert data["story"] == "F3.5"
        assert data["ratio"] == 3.0  # 60 / 20

    def test_no_ratio_without_estimate(self, tmp_path: Path) -> None:
        """Should not calculate ratio when no estimate."""
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir()

        input_data = CalibrationInput(
            story="F1.1",
            name="Test Feature",
            size="S",
            actual_min=30,
        )

        append_calibration(memory_dir, input_data)

        cal_file = memory_dir / "calibration.jsonl"
        data = json.loads(cal_file.read_text(encoding="utf-8").strip())
        assert data["ratio"] is None


class TestAppendSession:
    """Tests for append_session function."""

    def test_appends_session_successfully(self, tmp_path: Path) -> None:
        """Should append session with all fields."""
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir()

        input_data = SessionInput(
            topic="F3.5 Skills Integration",
            session_type="story",
            outcomes=["Writer API", "Hooks setup", "CLI commands"],
            log_path="dev/sessions/2026-02-02-f3.5.md",
        )

        result = append_session(memory_dir, input_data)

        assert result.success is True
        assert result.id == "SES-001"

        # Verify creates sessions directory
        sessions_file = memory_dir / "sessions" / "index.jsonl"
        assert sessions_file.exists()
        data = json.loads(sessions_file.read_text(encoding="utf-8").strip())
        assert data["topic"] == "F3.5 Skills Integration"
        assert data["outcomes"] == ["Writer API", "Hooks setup", "CLI commands"]

    def test_creates_sessions_subdirectory(self, tmp_path: Path) -> None:
        """Should create sessions/ subdirectory if missing."""
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir()

        input_data = SessionInput(topic="Test session")

        append_session(memory_dir, input_data)

        assert (memory_dir / "sessions").is_dir()
        assert (memory_dir / "sessions" / "index.jsonl").exists()


class TestValidateSessionIndex:
    """Tests for validate_session_index function (Jidoka check)."""

    def test_valid_index_returns_is_valid_true(self, tmp_path: Path) -> None:
        """Clean index should validate successfully."""
        memory_dir = tmp_path / "memory"
        sessions_dir = memory_dir / "sessions"
        sessions_dir.mkdir(parents=True)

        index_file = sessions_dir / "index.jsonl"
        index_file.write_text(
            '{"id": "SES-001", "date": "2026-02-01", "topic": "First"}\n'
            '{"id": "SES-002", "date": "2026-02-01", "topic": "Second"}\n'
            '{"id": "SES-003", "date": "2026-02-02", "topic": "Third"}\n'
        )

        result = validate_session_index(memory_dir)

        assert result.is_valid is True
        assert result.total_entries == 3
        assert result.max_id == 3
        assert result.entries_without_id == 0
        assert result.non_standard_ids == []
        assert result.duplicate_ids == []
        assert result.gaps == []

    def test_detects_missing_id(self, tmp_path: Path) -> None:
        """Should detect entries without ID field."""
        memory_dir = tmp_path / "memory"
        sessions_dir = memory_dir / "sessions"
        sessions_dir.mkdir(parents=True)

        index_file = sessions_dir / "index.jsonl"
        index_file.write_text(
            '{"id": "SES-001", "date": "2026-02-01", "topic": "First"}\n'
            '{"date": "2026-02-01", "topic": "Missing ID"}\n'
            '{"id": "SES-003", "date": "2026-02-02", "topic": "Third"}\n'
        )

        result = validate_session_index(memory_dir)

        assert result.is_valid is False
        assert result.entries_without_id == 1

    def test_detects_non_standard_ids(self, tmp_path: Path) -> None:
        """Should detect IDs not matching SES-NNN format."""
        memory_dir = tmp_path / "memory"
        sessions_dir = memory_dir / "sessions"
        sessions_dir.mkdir(parents=True)

        index_file = sessions_dir / "index.jsonl"
        index_file.write_text(
            '{"id": "SES-001", "date": "2026-02-01", "topic": "First"}\n'
            '{"id": "SESSION-2026-01-01", "date": "2026-01-01", "topic": "Legacy"}\n'
            '{"id": "ses-1234567890", "date": "2026-02-01", "topic": "Timestamp"}\n'
        )

        result = validate_session_index(memory_dir)

        assert result.is_valid is False
        assert len(result.non_standard_ids) == 2
        assert "SESSION-2026-01-01" in result.non_standard_ids
        assert "ses-1234567890" in result.non_standard_ids

    def test_detects_duplicate_ids(self, tmp_path: Path) -> None:
        """Should detect duplicate IDs."""
        memory_dir = tmp_path / "memory"
        sessions_dir = memory_dir / "sessions"
        sessions_dir.mkdir(parents=True)

        index_file = sessions_dir / "index.jsonl"
        index_file.write_text(
            '{"id": "SES-001", "date": "2026-02-01", "topic": "First"}\n'
            '{"id": "SES-002", "date": "2026-02-01", "topic": "Second"}\n'
            '{"id": "SES-001", "date": "2026-02-02", "topic": "Duplicate!"}\n'
        )

        result = validate_session_index(memory_dir)

        assert result.is_valid is False
        assert "SES-001" in result.duplicate_ids

    def test_detects_large_gaps(self, tmp_path: Path) -> None:
        """Should detect gaps > 5 in sequence."""
        memory_dir = tmp_path / "memory"
        sessions_dir = memory_dir / "sessions"
        sessions_dir.mkdir(parents=True)

        index_file = sessions_dir / "index.jsonl"
        index_file.write_text(
            '{"id": "SES-001", "date": "2026-02-01", "topic": "First"}\n'
            '{"id": "SES-002", "date": "2026-02-01", "topic": "Second"}\n'
            '{"id": "SES-010", "date": "2026-02-02", "topic": "Jump!"}\n'
        )

        result = validate_session_index(memory_dir)

        assert result.is_valid is False
        assert (2, 10) in result.gaps

    def test_small_gaps_are_valid(self, tmp_path: Path) -> None:
        """Gaps <= 5 should not trigger validation failure."""
        memory_dir = tmp_path / "memory"
        sessions_dir = memory_dir / "sessions"
        sessions_dir.mkdir(parents=True)

        index_file = sessions_dir / "index.jsonl"
        index_file.write_text(
            '{"id": "SES-001", "date": "2026-02-01", "topic": "First"}\n'
            '{"id": "SES-005", "date": "2026-02-01", "topic": "Fifth"}\n'
        )

        result = validate_session_index(memory_dir)

        assert result.is_valid is True
        assert result.gaps == []

    def test_nonexistent_index_is_valid(self, tmp_path: Path) -> None:
        """Missing index file should validate as empty but valid."""
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir()

        result = validate_session_index(memory_dir)

        assert result.is_valid is True
        assert result.total_entries == 0

    def test_summary_for_valid_index(self, tmp_path: Path) -> None:
        """Summary should indicate OK for valid index."""
        memory_dir = tmp_path / "memory"
        sessions_dir = memory_dir / "sessions"
        sessions_dir.mkdir(parents=True)

        index_file = sessions_dir / "index.jsonl"
        index_file.write_text(
            '{"id": "SES-042", "date": "2026-02-01", "topic": "Test"}\n'
        )

        result = validate_session_index(memory_dir)

        assert "OK" in result.summary()
        assert "42" in result.summary()

    def test_summary_for_invalid_index(self, tmp_path: Path) -> None:
        """Summary should list issues for invalid index."""
        memory_dir = tmp_path / "memory"
        sessions_dir = memory_dir / "sessions"
        sessions_dir.mkdir(parents=True)

        index_file = sessions_dir / "index.jsonl"
        index_file.write_text(
            '{"date": "2026-02-01", "topic": "No ID"}\n'
            '{"id": "legacy-format", "date": "2026-02-01", "topic": "Bad ID"}\n'
        )

        result = validate_session_index(memory_dir)

        summary = result.summary()
        assert "issues" in summary
        assert "missing ID" in summary
        assert "non-standard" in summary


class TestGetMemoryDirForScope:
    """Tests for get_memory_dir_for_scope helper."""

    def test_global_scope_returns_global_dir(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Global scope should return ~/.rai directory."""
        global_rai = tmp_path / "global_rai"
        global_rai.mkdir()
        monkeypatch.setenv("RAI_HOME", str(global_rai))

        result = get_memory_dir_for_scope(MemoryScope.GLOBAL, tmp_path)

        assert result == global_rai

    def test_project_scope_returns_memory_dir(self, tmp_path: Path) -> None:
        """Project scope should return .raise/rai/memory directory."""
        result = get_memory_dir_for_scope(MemoryScope.PROJECT, tmp_path)

        expected = tmp_path / ".raise" / "rai" / "memory"
        assert result == expected

    def test_personal_scope_returns_personal_dir(self, tmp_path: Path) -> None:
        """Personal scope should return .raise/rai/personal directory."""
        result = get_memory_dir_for_scope(MemoryScope.PERSONAL, tmp_path)

        expected = tmp_path / ".raise" / "rai" / "personal"
        assert result == expected


class TestGetNextIdWithPrefix:
    """Tests for get_next_id with developer prefix."""

    def test_with_prefix_returns_prefixed_id(self, tmp_path: Path) -> None:
        """Should generate PAT-E-001 with prefix 'E'."""
        file_path = tmp_path / "test.jsonl"
        file_path.touch()

        result = get_next_id(file_path, "PAT", developer_prefix="E")

        assert result == "PAT-E-001"

    def test_increments_from_existing_prefixed(self, tmp_path: Path) -> None:
        """Should increment from highest existing prefixed ID."""
        file_path = tmp_path / "test.jsonl"
        file_path.write_text(
            '{"id": "PAT-E-001", "content": "first"}\n'
            '{"id": "PAT-E-005", "content": "fifth"}\n'
        )

        result = get_next_id(file_path, "PAT", developer_prefix="E")

        assert result == "PAT-E-006"

    def test_ignores_other_developer_prefixes(self, tmp_path: Path) -> None:
        """Should only count IDs matching own prefix."""
        file_path = tmp_path / "test.jsonl"
        file_path.write_text(
            '{"id": "PAT-E-010", "content": "emilio"}\n'
            '{"id": "PAT-F-003", "content": "fer"}\n'
        )

        result = get_next_id(file_path, "PAT", developer_prefix="F")

        assert result == "PAT-F-004"

    def test_handles_mixed_old_and_new_format(self, tmp_path: Path) -> None:
        """Should handle files with both PAT-NNN and PAT-X-NNN formats."""
        file_path = tmp_path / "test.jsonl"
        file_path.write_text(
            '{"id": "PAT-100", "content": "old format"}\n'
            '{"id": "PAT-E-005", "content": "new format"}\n'
        )

        result = get_next_id(file_path, "PAT", developer_prefix="E")

        assert result == "PAT-E-006"

    def test_no_prefix_preserves_old_behavior(self, tmp_path: Path) -> None:
        """Without prefix, should produce old format PAT-NNN."""
        file_path = tmp_path / "test.jsonl"
        file_path.write_text('{"id": "PAT-010", "content": "existing"}\n')

        result = get_next_id(file_path, "PAT")

        assert result == "PAT-011"


class TestAppendPatternWithPrefix:
    """Tests for append_pattern with developer_prefix."""

    def test_appends_with_developer_prefix(self, tmp_path: Path) -> None:
        """Should generate prefixed ID when developer_prefix provided."""
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir()

        input_data = PatternInput(content="Test pattern")

        result = append_pattern(memory_dir, input_data, developer_prefix="E")

        assert result.success is True
        assert result.id == "PAT-E-001"

        patterns_file = memory_dir / "patterns.jsonl"
        data = json.loads(patterns_file.read_text(encoding="utf-8").strip())
        assert data["id"] == "PAT-E-001"

    def test_appends_without_prefix_backward_compat(self, tmp_path: Path) -> None:
        """Without prefix, should still produce PAT-NNN (backward compat)."""
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir()

        input_data = PatternInput(content="Test pattern")

        result = append_pattern(memory_dir, input_data)

        assert result.id == "PAT-001"


class TestAppendPatternBaseVersion:
    """Tests for base/version fields in pattern versioning (F14.6)."""

    def test_base_pattern_includes_base_and_version(self, tmp_path: Path) -> None:
        """Base patterns should include base=True and version in output."""
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir()

        input_data = PatternInput(
            content="TDD cycle discipline",
            sub_type=PatternSubType.PROCESS,
            context=["tdd", "testing"],
            base=True,
            version=1,
        )

        result = append_pattern(memory_dir, input_data)

        assert result.success is True
        patterns_file = memory_dir / "patterns.jsonl"
        data = json.loads(patterns_file.read_text(encoding="utf-8").strip())
        assert data["base"] is True
        assert data["version"] == 1

    def test_personal_pattern_omits_base_and_version(self, tmp_path: Path) -> None:
        """Personal patterns (default) should not have base/version fields."""
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir()

        input_data = PatternInput(
            content="My custom pattern",
            sub_type=PatternSubType.CODEBASE,
            context=["custom"],
        )

        append_pattern(memory_dir, input_data)

        patterns_file = memory_dir / "patterns.jsonl"
        data = json.loads(patterns_file.read_text(encoding="utf-8").strip())
        assert "base" not in data
        assert "version" not in data

    def test_base_false_omits_fields(self, tmp_path: Path) -> None:
        """Explicit base=False should not include base/version in output."""
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir()

        input_data = PatternInput(content="Not a base pattern", base=False)

        append_pattern(memory_dir, input_data)

        patterns_file = memory_dir / "patterns.jsonl"
        data = json.loads(patterns_file.read_text(encoding="utf-8").strip())
        assert "base" not in data
        assert "version" not in data


class TestAppendPatternWithScope:
    """Tests for append_pattern with scope parameter."""

    def test_writes_to_project_by_default(self, tmp_path: Path) -> None:
        """Default scope should write to project memory directory."""
        project_dir = tmp_path / ".raise" / "rai" / "memory"
        project_dir.mkdir(parents=True)

        input_data = PatternInput(content="Project pattern")

        result = append_pattern(project_dir, input_data)

        assert result.success is True
        assert (project_dir / "patterns.jsonl").exists()

    def test_writes_to_global_with_scope(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Global scope should write to ~/.rai directory."""
        global_rai = tmp_path / "global_rai"
        global_rai.mkdir()
        monkeypatch.setenv("RAI_HOME", str(global_rai))

        input_data = PatternInput(content="Global pattern")

        result = append_pattern(
            get_memory_dir_for_scope(MemoryScope.GLOBAL, tmp_path),
            input_data,
            scope=MemoryScope.GLOBAL,
        )

        assert result.success is True
        patterns_file = global_rai / "patterns.jsonl"
        assert patterns_file.exists()
        data = json.loads(patterns_file.read_text(encoding="utf-8").strip())
        assert data["content"] == "Global pattern"

    def test_writes_to_personal_with_scope(self, tmp_path: Path) -> None:
        """Personal scope should write to .raise/rai/personal directory."""
        personal_dir = tmp_path / ".raise" / "rai" / "personal"
        personal_dir.mkdir(parents=True)

        input_data = PatternInput(content="Personal pattern")

        result = append_pattern(
            personal_dir,
            input_data,
            scope=MemoryScope.PERSONAL,
        )

        assert result.success is True
        patterns_file = personal_dir / "patterns.jsonl"
        assert patterns_file.exists()


class TestAppendCalibrationWithScope:
    """Tests for append_calibration with scope parameter."""

    def test_writes_to_personal_with_scope(self, tmp_path: Path) -> None:
        """Personal scope should write to .raise/rai/personal directory."""
        personal_dir = tmp_path / ".raise" / "rai" / "personal"
        personal_dir.mkdir(parents=True)

        input_data = CalibrationInput(
            story="F1.1",
            name="Test Feature",
            size="S",
            actual_min=30,
        )

        result = append_calibration(
            personal_dir,
            input_data,
            scope=MemoryScope.PERSONAL,
        )

        assert result.success is True
        cal_file = personal_dir / "calibration.jsonl"
        assert cal_file.exists()


class TestAppendSessionAlwaysPersonal:
    """Tests for append_session always writing to personal directory."""

    def test_session_writes_to_personal_dir(self, tmp_path: Path) -> None:
        """Sessions should always write to personal directory."""
        personal_dir = tmp_path / ".raise" / "rai" / "personal"
        personal_dir.mkdir(parents=True)

        input_data = SessionInput(topic="Test session")

        result = append_session(personal_dir, input_data)

        assert result.success is True
        sessions_file = personal_dir / "sessions" / "index.jsonl"
        assert sessions_file.exists()


class TestReinforcePattern:
    """Tests for reinforce_pattern function (RAISE-170)."""

    def _make_patterns_file(self, tmp_path: Path, lines: list[dict]) -> Path:
        """Create a patterns.jsonl file with given records."""
        f = tmp_path / "patterns.jsonl"
        f.write_text(
            "\n".join(json.dumps(line) for line in lines) + "\n",
            encoding="utf-8",
        )
        return f

    def test_positive_vote_increments_positives_and_evaluations(
        self, tmp_path: Path
    ) -> None:
        """Vote +1 increments positives and evaluations."""
        f = self._make_patterns_file(
            tmp_path,
            [{"id": "PAT-E-001", "content": "test pattern", "created": "2026-02-01"}],
        )
        result = reinforce_pattern(f, "PAT-E-001", vote=1)

        assert result.pattern_id == "PAT-E-001"
        assert result.positives == 1
        assert result.negatives == 0
        assert result.evaluations == 1
        assert result.was_updated is True

        data = json.loads(f.read_text(encoding="utf-8").strip())
        assert data["positives"] == 1
        assert data["evaluations"] == 1

    def test_negative_vote_increments_negatives_and_evaluations(
        self, tmp_path: Path
    ) -> None:
        """Vote -1 increments negatives and evaluations."""
        f = self._make_patterns_file(
            tmp_path,
            [{"id": "PAT-E-001", "content": "test", "created": "2026-02-01"}],
        )
        result = reinforce_pattern(f, "PAT-E-001", vote=-1)

        assert result.negatives == 1
        assert result.evaluations == 1
        assert result.was_updated is True

    def test_zero_vote_does_not_update(self, tmp_path: Path) -> None:
        """Vote 0 (N/A) does not modify evaluations or counts."""
        f = self._make_patterns_file(
            tmp_path,
            [
                {
                    "id": "PAT-E-001",
                    "content": "test",
                    "created": "2026-02-01",
                    "positives": 2,
                    "negatives": 0,
                    "evaluations": 2,
                }
            ],
        )
        original_text = f.read_text(encoding="utf-8")
        result = reinforce_pattern(f, "PAT-E-001", vote=0)

        assert result.was_updated is False
        assert result.positives == 2
        assert result.evaluations == 2
        assert f.read_text(encoding="utf-8") == original_text  # file unchanged

    def test_pattern_not_found_raises(self, tmp_path: Path) -> None:
        """KeyError raised when pattern ID not found."""
        f = self._make_patterns_file(
            tmp_path,
            [{"id": "PAT-E-001", "content": "test", "created": "2026-02-01"}],
        )
        with pytest.raises(KeyError):
            reinforce_pattern(f, "PAT-E-999", vote=1)

    def test_increments_from_existing_counts(self, tmp_path: Path) -> None:
        """Increments existing positives/negatives/evaluations (not reset)."""
        f = self._make_patterns_file(
            tmp_path,
            [
                {
                    "id": "PAT-E-001",
                    "content": "test",
                    "created": "2026-02-01",
                    "positives": 3,
                    "negatives": 1,
                    "evaluations": 4,
                }
            ],
        )
        result = reinforce_pattern(f, "PAT-E-001", vote=1)

        assert result.positives == 4
        assert result.negatives == 1
        assert result.evaluations == 5

    def test_last_evaluated_set_on_nonzero_vote(self, tmp_path: Path) -> None:
        """last_evaluated updated to today for +1 and -1 votes."""
        f = self._make_patterns_file(
            tmp_path,
            [{"id": "PAT-E-001", "content": "test", "created": "2026-02-01"}],
        )
        reinforce_pattern(f, "PAT-E-001", vote=1)

        data = json.loads(f.read_text(encoding="utf-8").strip())
        assert data["last_evaluated"] == date.today().isoformat()

    def test_last_evaluated_not_set_on_zero_vote(self, tmp_path: Path) -> None:
        """last_evaluated NOT updated for vote=0."""
        f = self._make_patterns_file(
            tmp_path,
            [{"id": "PAT-E-001", "content": "test", "created": "2026-02-01"}],
        )
        reinforce_pattern(f, "PAT-E-001", vote=0)

        data = json.loads(f.read_text(encoding="utf-8").strip())
        assert "last_evaluated" not in data

    def test_multi_pattern_file_only_updates_target(self, tmp_path: Path) -> None:
        """Only target pattern is modified; others remain unchanged."""
        f = self._make_patterns_file(
            tmp_path,
            [
                {"id": "PAT-E-001", "content": "first", "created": "2026-02-01"},
                {"id": "PAT-E-002", "content": "second", "created": "2026-02-01"},
                {"id": "PAT-E-003", "content": "third", "created": "2026-02-01"},
            ],
        )
        reinforce_pattern(f, "PAT-E-002", vote=1)

        lines = [
            json.loads(line)
            for line in f.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        assert len(lines) == 3
        assert lines[0]["id"] == "PAT-E-001"
        assert "positives" not in lines[0]
        assert lines[1]["positives"] == 1
        assert lines[2]["id"] == "PAT-E-003"
        assert "positives" not in lines[2]

    def test_reinforce_result_model(self) -> None:
        """ReinforceResult is a Pydantic model with expected fields."""
        r = ReinforceResult(
            pattern_id="PAT-E-001",
            vote=1,
            positives=2,
            negatives=0,
            evaluations=2,
            last_evaluated="2026-02-19",
            was_updated=True,
        )
        assert r.pattern_id == "PAT-E-001"
        assert r.was_updated is True

    def test_resolves_file_path_internally(self, tmp_path: Path) -> None:
        """RAISE-522: reinforce_pattern resolves file_path at entry (defense-in-depth).

        Even when called with a non-canonical path containing '..' components,
        the function must resolve it and operate on the correct file.
        """
        real_dir = tmp_path / "memory"
        real_dir.mkdir()
        real_file = real_dir / "patterns.jsonl"
        real_file.write_text(
            '{"id": "PAT-E-001", "content": "test", "created": "2026-01-01"}\n',
            encoding="utf-8",
        )

        # Construct a non-canonical path: tmp/memory/../memory/patterns.jsonl
        traversal_path = tmp_path / "memory" / ".." / "memory" / "patterns.jsonl"

        result = reinforce_pattern(traversal_path, "PAT-E-001", vote=1)

        assert result.was_updated is True
        assert result.positives == 1
        # The actual file on disk was updated — not some other path
        data = json.loads(real_file.read_text(encoding="utf-8").splitlines()[0])
        assert data["positives"] == 1


class TestAppendJsonlUsesAdapter:
    """Verify _append_jsonl delegates to FilesystemAdapter.append (S1040.2 T1)."""

    def test_append_jsonl_delegates_to_adapter(self, tmp_path: Path) -> None:
        """_append_jsonl should use FilesystemAdapter.append internally."""
        from unittest.mock import patch

        from raise_cli.memory.writer import _append_jsonl

        file_path = tmp_path / "patterns.jsonl"
        data = {"id": "PAT-001", "content": "test"}

        with patch("raise_cli.memory.writer.FilesystemAdapter") as mock_adapter_cls:
            _append_jsonl(file_path, data)

            mock_adapter_cls.assert_called_once_with(root=tmp_path)
            mock_adapter_cls.return_value.append.assert_called_once_with(
                Path(file_path.name), json.dumps(data)
            )

    def test_append_jsonl_produces_correct_output(self, tmp_path: Path) -> None:
        """End-to-end: appended line is valid JSONL with trailing newline."""
        from raise_cli.memory.writer import _append_jsonl

        file_path = tmp_path / "test.jsonl"
        data = {"id": "PAT-001", "content": "hello"}

        _append_jsonl(file_path, data)

        content = file_path.read_text(encoding="utf-8")
        assert content.endswith("\n")
        parsed = json.loads(content.strip())
        assert parsed == data

    def test_append_jsonl_creates_parent_dirs(self, tmp_path: Path) -> None:
        """Adapter handles parent directory creation."""
        from raise_cli.memory.writer import _append_jsonl

        file_path = tmp_path / "deep" / "nested" / "test.jsonl"
        data = {"id": "PAT-001"}

        _append_jsonl(file_path, data)

        assert file_path.exists()
        parsed = json.loads(file_path.read_text(encoding="utf-8").strip())
        assert parsed["id"] == "PAT-001"


class TestReinforcePatternUsesAdapter:
    """Verify reinforce_pattern uses FilesystemAdapter.write (S1040.2 T3b)."""

    def test_reinforce_delegates_to_adapter_write(self, tmp_path: Path) -> None:
        """reinforce_pattern should use FilesystemAdapter.write for atomic rewrite."""
        from unittest.mock import patch

        f = tmp_path / "patterns.jsonl"
        f.write_text(
            '{"id": "PAT-E-001", "content": "test", "created": "2026-02-01"}\n',
            encoding="utf-8",
        )

        with patch("raise_cli.memory.writer.FilesystemAdapter") as mock_adapter_cls:
            reinforce_pattern(f, "PAT-E-001", vote=1)

            mock_adapter_cls.assert_called_with(root=tmp_path)
            mock_adapter_cls.return_value.write.assert_called_once()

    def test_reinforce_output_identical_after_migration(self, tmp_path: Path) -> None:
        """End-to-end: reinforce produces identical JSONL content."""
        f = tmp_path / "patterns.jsonl"
        f.write_text(
            '{"id": "PAT-E-001", "content": "test", "created": "2026-02-01"}\n'
            '{"id": "PAT-E-002", "content": "second", "created": "2026-02-01"}\n',
            encoding="utf-8",
        )

        reinforce_pattern(f, "PAT-E-001", vote=1)

        lines = [
            json.loads(line)
            for line in f.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        assert len(lines) == 2
        assert lines[0]["positives"] == 1
        assert lines[0]["evaluations"] == 1
        assert lines[1]["id"] == "PAT-E-002"
        assert "positives" not in lines[1]
