"""Tests for memory writer module."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from raise_cli.memory.writer import (
    CalibrationInput,
    PatternInput,
    SessionInput,
    WriteResult,
    _get_next_id,
    append_calibration,
    append_pattern,
    append_session,
    validate_session_index,
)
from raise_cli.memory.models import PatternSubType


class TestGetNextId:
    """Tests for _get_next_id function."""

    def test_empty_file_returns_001(self, tmp_path: Path) -> None:
        """First ID should be 001 when file is empty."""
        file_path = tmp_path / "test.jsonl"
        file_path.touch()

        result = _get_next_id(file_path, "PAT")

        assert result == "PAT-001"

    def test_nonexistent_file_returns_001(self, tmp_path: Path) -> None:
        """First ID should be 001 when file doesn't exist."""
        file_path = tmp_path / "nonexistent.jsonl"

        result = _get_next_id(file_path, "PAT")

        assert result == "PAT-001"

    def test_increments_from_existing(self, tmp_path: Path) -> None:
        """Should increment from highest existing ID."""
        file_path = tmp_path / "test.jsonl"
        file_path.write_text(
            '{"id": "PAT-001", "content": "first"}\n'
            '{"id": "PAT-005", "content": "fifth"}\n'
            '{"id": "PAT-003", "content": "third"}\n'
        )

        result = _get_next_id(file_path, "PAT")

        assert result == "PAT-006"

    def test_handles_different_prefixes(self, tmp_path: Path) -> None:
        """Should only count IDs matching the prefix."""
        file_path = tmp_path / "test.jsonl"
        file_path.write_text(
            '{"id": "PAT-010", "content": "pattern"}\n'
            '{"id": "CAL-005", "content": "calibration"}\n'
        )

        result = _get_next_id(file_path, "CAL")

        assert result == "CAL-006"


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
        content = patterns_file.read_text()
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
        data = json.loads(patterns_file.read_text().strip())
        assert data["created"] == "2026-01-15"


class TestAppendCalibration:
    """Tests for append_calibration function."""

    def test_appends_calibration_with_ratio(self, tmp_path: Path) -> None:
        """Should calculate ratio when estimated and actual provided."""
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir()

        input_data = CalibrationInput(
            feature="F3.5",
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
        data = json.loads(cal_file.read_text().strip())
        assert data["feature"] == "F3.5"
        assert data["ratio"] == 3.0  # 60 / 20

    def test_no_ratio_without_estimate(self, tmp_path: Path) -> None:
        """Should not calculate ratio when no estimate."""
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir()

        input_data = CalibrationInput(
            feature="F1.1",
            name="Test Feature",
            size="S",
            actual_min=30,
        )

        append_calibration(memory_dir, input_data)

        cal_file = memory_dir / "calibration.jsonl"
        data = json.loads(cal_file.read_text().strip())
        assert data["ratio"] is None


class TestAppendSession:
    """Tests for append_session function."""

    def test_appends_session_successfully(self, tmp_path: Path) -> None:
        """Should append session with all fields."""
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir()

        input_data = SessionInput(
            topic="F3.5 Skills Integration",
            session_type="feature",
            outcomes=["Writer API", "Hooks setup", "CLI commands"],
            log_path="dev/sessions/2026-02-02-f3.5.md",
        )

        result = append_session(memory_dir, input_data)

        assert result.success is True
        assert result.id == "SES-001"

        # Verify creates sessions directory
        sessions_file = memory_dir / "sessions" / "index.jsonl"
        assert sessions_file.exists()
        data = json.loads(sessions_file.read_text().strip())
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


class TestCacheInvalidation:
    """Tests for cache invalidation after writes."""

    def test_pattern_invalidates_cache(self, tmp_path: Path) -> None:
        """Writing pattern should delete graph.json cache."""
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir()
        cache_file = memory_dir / "graph.json"
        cache_file.write_text('{"nodes": {}, "edges": []}')

        input_data = PatternInput(content="Test pattern")
        append_pattern(memory_dir, input_data)

        assert not cache_file.exists()

    def test_calibration_invalidates_cache(self, tmp_path: Path) -> None:
        """Writing calibration should delete graph.json cache."""
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir()
        cache_file = memory_dir / "graph.json"
        cache_file.write_text('{"nodes": {}, "edges": []}')

        input_data = CalibrationInput(
            feature="F1.1", name="Test", size="S", actual_min=30
        )
        append_calibration(memory_dir, input_data)

        assert not cache_file.exists()

    def test_session_invalidates_cache(self, tmp_path: Path) -> None:
        """Writing session should delete graph.json cache."""
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir()
        cache_file = memory_dir / "graph.json"
        cache_file.write_text('{"nodes": {}, "edges": []}')

        input_data = SessionInput(topic="Test session")
        append_session(memory_dir, input_data)

        assert not cache_file.exists()


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
        index_file.write_text('{"id": "SES-042", "date": "2026-02-01", "topic": "Test"}\n')

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
