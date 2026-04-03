"""Tests for memory loader."""

from datetime import date
from pathlib import Path

import pytest

from raise_cli.memory.loader import (
    load_calibration,
    load_jsonl_file,
    load_memory_from_directory,
    load_pattern,
    load_session,
    parse_date,
)
from raise_cli.memory.models import MemoryConceptType, MemoryScope


class TestParseDate:
    """Tests for parse_date function."""

    def test_parse_valid_date(self) -> None:
        """Parse a valid date string."""
        result = parse_date("2026-01-31")
        assert result == date(2026, 1, 31)

    def test_parse_invalid_date_raises(self) -> None:
        """Invalid date string raises ValueError."""
        with pytest.raises(ValueError):
            parse_date("not-a-date")


class TestLoadPattern:
    """Tests for load_pattern function."""

    def test_load_pattern_with_all_fields(self) -> None:
        """Load a pattern with all fields."""
        data = {
            "id": "PAT-001",
            "type": "codebase",
            "content": "Singleton pattern for state",
            "context": ["testing", "module-design"],
            "learned_from": "F1.4",
            "created": "2026-01-31",
        }
        concept = load_pattern(data)

        assert concept.id == "PAT-001"
        assert concept.type == MemoryConceptType.PATTERN
        assert concept.content == "Singleton pattern for state"
        assert concept.context == ["testing", "module-design"]
        assert concept.created == date(2026, 1, 31)
        assert concept.metadata["sub_type"] == "codebase"
        assert concept.metadata["learned_from"] == "F1.4"

    def test_load_pattern_minimal(self) -> None:
        """Load a pattern with minimal fields."""
        data = {
            "id": "PAT-002",
            "content": "Simple pattern",
            "created": "2026-02-01",
        }
        concept = load_pattern(data)

        assert concept.id == "PAT-002"
        assert concept.context == []
        assert concept.metadata["sub_type"] == "unknown"
        assert concept.metadata["learned_from"] is None


class TestLoadPatternBaseVersion:
    """Tests for load_pattern with base/version fields (F14.6)."""

    def test_base_pattern_has_base_in_metadata(self) -> None:
        """Base patterns should surface base=True in metadata."""
        data = {
            "id": "BASE-001",
            "type": "process",
            "content": "TDD cycle discipline",
            "context": ["tdd", "testing"],
            "base": True,
            "version": 1,
            "created": "2026-02-05",
        }
        concept = load_pattern(data)

        assert concept.metadata["base"] is True
        assert concept.metadata["version"] == 1

    def test_personal_pattern_has_no_base_in_metadata(self) -> None:
        """Personal patterns (without base field) should not have base in metadata."""
        data = {
            "id": "PAT-001",
            "type": "codebase",
            "content": "My custom pattern",
            "created": "2026-01-31",
        }
        concept = load_pattern(data)

        assert concept.metadata.get("base") is None
        assert concept.metadata.get("version") is None

    def test_base_pattern_round_trip(self) -> None:
        """Base pattern fields should survive load cycle."""
        data = {
            "id": "BASE-015",
            "type": "technical",
            "content": "Type annotations everywhere",
            "context": ["typing", "pyright"],
            "base": True,
            "version": 2,
            "created": "2026-02-05",
        }
        concept = load_pattern(data)

        assert concept.id == "BASE-015"
        assert concept.metadata["base"] is True
        assert concept.metadata["version"] == 2
        assert concept.metadata["sub_type"] == "technical"


class TestLoadCalibration:
    """Tests for load_calibration function."""

    def test_load_calibration_with_all_fields(self) -> None:
        """Load a calibration with all fields."""
        data = {
            "id": "CAL-001",
            "feature": "F2.1",
            "name": "Concept Extraction",
            "size": "S",
            "sp": 3,
            "estimated_min": 180,
            "actual_min": 52,
            "ratio": 3.5,
            "kata_cycle": True,
            "notes": "Full kata cycle",
            "created": "2026-01-31",
        }
        concept = load_calibration(data)

        assert concept.id == "CAL-001"
        assert concept.type == MemoryConceptType.CALIBRATION
        assert "Concept Extraction" in concept.content
        assert "52min" in concept.content
        assert "3.5x" in concept.content
        assert "F2.1" in concept.context
        assert "s" in concept.context
        assert "kata-cycle" in concept.context
        assert concept.metadata["ratio"] == 3.5
        assert concept.metadata["kata_cycle"] is True

    def test_load_calibration_without_actuals(self) -> None:
        """Load a calibration without actual data."""
        data = {
            "id": "CAL-002",
            "feature": "F1.1",
            "name": "Project Scaffolding",
            "size": "S",
            "sp": 3,
            "estimated_min": None,
            "actual_min": 30,
            "ratio": None,
            "kata_cycle": False,
            "created": "2026-01-31",
        }
        concept = load_calibration(data)

        assert concept.id == "CAL-002"
        assert "kata-cycle" not in concept.context
        assert concept.metadata["ratio"] is None


class TestLoadSession:
    """Tests for load_session function."""

    def test_load_session_with_all_fields(self) -> None:
        """Load a session with all fields."""
        data = {
            "id": "SES-001",
            "date": "2026-02-01",
            "type": "story",
            "topic": "E3 Implementation Plan",
            "outcomes": ["/epic-plan skill complete", "Risk-First sequencing"],
            "log_path": "dev/sessions/2026-02-01-e3.md",
        }
        concept = load_session(data)

        assert concept.id == "SES-001"
        assert concept.type == MemoryConceptType.SESSION
        assert "E3 Implementation Plan" in concept.content
        assert "/epic-plan skill complete" in concept.content
        assert "story" in concept.context
        assert concept.metadata["session_type"] == "story"
        assert concept.metadata["log_path"] == "dev/sessions/2026-02-01-e3.md"

    def test_load_session_minimal(self) -> None:
        """Load a session with minimal fields."""
        data = {
            "id": "SES-002",
            "date": "2026-02-02",
            "type": "research",
            "topic": "Memory Systems",
        }
        concept = load_session(data)

        assert concept.id == "SES-002"
        assert concept.metadata["outcomes"] == []
        assert concept.metadata["log_path"] is None


class TestLoadJsonlFile:
    """Tests for load_jsonl_file function."""

    def test_load_patterns_file(self, tmp_path: Path) -> None:
        """Load a patterns JSONL file."""
        jsonl_file = tmp_path / "patterns.jsonl"
        jsonl_file.write_text(
            '{"id": "PAT-001", "type": "codebase", "content": "Test", "created": "2026-01-31"}\n'
            '{"id": "PAT-002", "type": "process", "content": "Test2", "created": "2026-01-31"}\n'
        )

        concepts, errors = load_jsonl_file(jsonl_file, MemoryConceptType.PATTERN)

        assert len(concepts) == 2
        assert len(errors) == 0
        assert concepts[0].id == "PAT-001"
        assert concepts[1].id == "PAT-002"

    def test_load_nonexistent_file(self, tmp_path: Path) -> None:
        """Loading nonexistent file returns empty list."""
        jsonl_file = tmp_path / "nonexistent.jsonl"

        concepts, errors = load_jsonl_file(jsonl_file, MemoryConceptType.PATTERN)

        assert len(concepts) == 0
        assert len(errors) == 0

    def test_load_file_with_invalid_json(self, tmp_path: Path) -> None:
        """Loading file with invalid JSON records errors."""
        jsonl_file = tmp_path / "patterns.jsonl"
        jsonl_file.write_text(
            '{"id": "PAT-001", "type": "codebase", "content": "Test", "created": "2026-01-31"}\n'
            "not valid json\n"
            '{"id": "PAT-002", "type": "process", "content": "Test2", "created": "2026-01-31"}\n'
        )

        concepts, errors = load_jsonl_file(jsonl_file, MemoryConceptType.PATTERN)

        assert len(concepts) == 2
        assert len(errors) == 1
        assert "patterns.jsonl:2" in errors[0]

    def test_load_file_with_missing_field(self, tmp_path: Path) -> None:
        """Loading file with missing required field records error."""
        jsonl_file = tmp_path / "patterns.jsonl"
        jsonl_file.write_text(
            '{"id": "PAT-001"}\n'  # missing content, created
        )

        concepts, errors = load_jsonl_file(jsonl_file, MemoryConceptType.PATTERN)

        assert len(concepts) == 0
        assert len(errors) == 1

    def test_load_file_skips_empty_lines(self, tmp_path: Path) -> None:
        """Empty lines are skipped."""
        jsonl_file = tmp_path / "patterns.jsonl"
        jsonl_file.write_text(
            '{"id": "PAT-001", "type": "codebase", "content": "Test", "created": "2026-01-31"}\n'
            "\n"
            '{"id": "PAT-002", "type": "process", "content": "Test2", "created": "2026-01-31"}\n'
        )

        concepts, errors = load_jsonl_file(jsonl_file, MemoryConceptType.PATTERN)

        assert len(concepts) == 2
        assert len(errors) == 0


class TestLoadMemoryFromDirectory:
    """Tests for load_memory_from_directory function."""

    def test_load_from_empty_directory(self, tmp_path: Path) -> None:
        """Loading from empty directory returns empty result."""
        result = load_memory_from_directory(tmp_path)

        assert result.total == 0
        assert result.files_processed == 0
        assert result.errors == []

    def test_load_all_memory_types(self, tmp_path: Path) -> None:
        """Load patterns, calibration, and sessions."""
        # Create patterns file
        (tmp_path / "patterns.jsonl").write_text(
            '{"id": "PAT-001", "type": "codebase", "content": "Pattern", "created": "2026-01-31"}\n'
        )

        # Create calibration file
        (tmp_path / "calibration.jsonl").write_text(
            '{"id": "CAL-001", "feature": "F1.1", "name": "Test", "size": "S", "created": "2026-01-31"}\n'
        )

        # Create sessions file
        sessions_dir = tmp_path / "sessions"
        sessions_dir.mkdir()
        (sessions_dir / "index.jsonl").write_text(
            '{"id": "SES-001", "date": "2026-02-01", "type": "story", "topic": "Test"}\n'
        )

        result = load_memory_from_directory(tmp_path)

        assert result.total == 3
        assert result.files_processed == 3
        assert len(result.errors) == 0

        # Check we have one of each type
        types = {c.type for c in result.concepts}
        assert MemoryConceptType.PATTERN in types
        assert MemoryConceptType.CALIBRATION in types
        assert MemoryConceptType.SESSION in types

    def test_load_with_real_rai_directory(self) -> None:
        """Load from actual .raise/rai/memory directory if available.

        Uses absolute path to be immune to CWD changes from other tests.
        """
        project_root = Path(__file__).resolve().parent.parent.parent
        rai_memory = project_root / ".raise" / "rai" / "memory"
        if not rai_memory.exists():
            pytest.skip(".raise/rai/memory directory not found")

        patterns_file = rai_memory / "patterns.jsonl"
        if not patterns_file.exists() or patterns_file.stat().st_size == 0:
            pytest.skip("patterns.jsonl not present or empty")

        result = load_memory_from_directory(rai_memory)

        # Should have loaded some concepts
        assert result.total > 0
        assert result.files_processed > 0
        # Real data should parse without errors
        assert len(result.errors) == 0


class TestMemoryScope:
    """Tests for MemoryScope enum."""

    def test_scope_values(self) -> None:
        """MemoryScope has correct values."""
        assert MemoryScope.GLOBAL.value == "global"
        assert MemoryScope.PROJECT.value == "project"
        assert MemoryScope.PERSONAL.value == "personal"

    def test_scope_is_string_enum(self) -> None:
        """MemoryScope values can be used as strings."""
        assert str(MemoryScope.GLOBAL) == "global"
        assert f"scope:{MemoryScope.PROJECT}" == "scope:project"


class TestLoadPatternWithScope:
    """Tests for load_pattern with scope tracking."""

    def test_load_pattern_includes_scope_in_metadata(self) -> None:
        """Pattern loaded with scope should have scope in metadata."""
        data = {
            "id": "PAT-001",
            "type": "codebase",
            "content": "Test pattern",
            "created": "2026-01-31",
        }
        concept = load_pattern(data, scope=MemoryScope.PROJECT)

        assert concept.metadata.get("scope") == MemoryScope.PROJECT.value

    def test_load_pattern_default_scope_is_project(self) -> None:
        """Pattern loaded without explicit scope defaults to project."""
        data = {
            "id": "PAT-002",
            "type": "process",
            "content": "Another pattern",
            "created": "2026-01-31",
        }
        concept = load_pattern(data)

        assert concept.metadata.get("scope") == MemoryScope.PROJECT.value

    def test_load_pattern_global_scope(self) -> None:
        """Pattern can be loaded with global scope."""
        data = {
            "id": "PAT-003",
            "type": "universal",
            "content": "Universal pattern",
            "created": "2026-01-31",
        }
        concept = load_pattern(data, scope=MemoryScope.GLOBAL)

        assert concept.metadata.get("scope") == MemoryScope.GLOBAL.value


class TestLoadCalibrationWithScope:
    """Tests for load_calibration with scope tracking."""

    def test_load_calibration_includes_scope(self) -> None:
        """Calibration loaded with scope should have scope in metadata."""
        data = {
            "id": "CAL-001",
            "feature": "F1.1",
            "name": "Test",
            "size": "S",
            "created": "2026-01-31",
        }
        concept = load_calibration(data, scope=MemoryScope.PERSONAL)

        assert concept.metadata.get("scope") == MemoryScope.PERSONAL.value


class TestLoadSessionWithScope:
    """Tests for load_session with scope tracking."""

    def test_load_session_includes_scope(self) -> None:
        """Session loaded with scope should have scope in metadata."""
        data = {
            "id": "SES-001",
            "date": "2026-02-01",
            "type": "story",
            "topic": "Test session",
        }
        concept = load_session(data, scope=MemoryScope.PERSONAL)

        assert concept.metadata.get("scope") == MemoryScope.PERSONAL.value


class TestLoadJsonlFileWithScope:
    """Tests for load_jsonl_file with scope parameter."""

    def test_load_jsonl_file_passes_scope_to_concepts(self, tmp_path: Path) -> None:
        """Scope should be passed to all loaded concepts."""
        jsonl_file = tmp_path / "patterns.jsonl"
        jsonl_file.write_text(
            '{"id": "PAT-001", "type": "codebase", "content": "Test", "created": "2026-01-31"}\n'
            '{"id": "PAT-002", "type": "process", "content": "Test2", "created": "2026-01-31"}\n'
        )

        concepts, _ = load_jsonl_file(
            jsonl_file, MemoryConceptType.PATTERN, scope=MemoryScope.GLOBAL
        )

        assert len(concepts) == 2
        assert all(c.metadata.get("scope") == "global" for c in concepts)
