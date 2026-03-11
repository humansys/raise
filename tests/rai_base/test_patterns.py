"""Tests for base patterns catalog.

Tests verify that:
1. Patterns file is accessible via importlib.resources
2. All patterns are valid JSONL
3. Required fields are present
4. Content covers methodology areas
"""

from __future__ import annotations

import json
from importlib.resources import files

import pytest


class TestBasePatternsPackage:
    """Tests for base patterns file accessibility."""

    def test_memory_directory_accessible(self) -> None:
        """Memory directory is accessible via importlib.resources."""
        base = files("raise_cli.rai_base")
        memory = base / "memory"
        assert memory.is_dir()

    def test_patterns_base_exists(self) -> None:
        """patterns-base.jsonl file exists and is readable."""
        base = files("raise_cli.rai_base")
        patterns_file = base / "memory" / "patterns-base.jsonl"
        content = patterns_file.read_text(encoding="utf-8")
        assert len(content) > 0


class TestBasePatternsValidity:
    """Tests for patterns JSONL validity."""

    @pytest.fixture
    def patterns(self) -> list[dict]:
        """Load and parse all base patterns."""
        base = files("raise_cli.rai_base")
        content = (base / "memory" / "patterns-base.jsonl").read_text(encoding="utf-8")
        patterns = []
        for line in content.strip().split("\n"):
            if line.strip():
                patterns.append(json.loads(line))
        return patterns

    def test_valid_jsonl(self, patterns: list[dict]) -> None:
        """All lines parse as valid JSON."""
        # If we got here via fixture, all lines parsed
        assert len(patterns) > 0

    def test_minimum_pattern_count(self, patterns: list[dict]) -> None:
        """At least 15 base patterns exist."""
        assert len(patterns) >= 15

    def test_all_have_required_fields(self, patterns: list[dict]) -> None:
        """All patterns have required fields."""
        required = {"id", "type", "content", "context", "base", "version"}
        for pattern in patterns:
            missing = required - set(pattern.keys())
            assert not missing, f"Pattern {pattern.get('id', '?')} missing: {missing}"

    def test_all_ids_unique(self, patterns: list[dict]) -> None:
        """All pattern IDs are unique."""
        ids = [p["id"] for p in patterns]
        assert len(ids) == len(set(ids)), "Duplicate IDs found"

    def test_ids_use_base_prefix(self, patterns: list[dict]) -> None:
        """All pattern IDs use BASE- prefix."""
        for pattern in patterns:
            assert pattern["id"].startswith("BASE-"), (
                f"ID {pattern['id']} should start with BASE-"
            )

    def test_all_marked_as_base(self, patterns: list[dict]) -> None:
        """All patterns have base: true."""
        for pattern in patterns:
            assert pattern["base"] is True, (
                f"Pattern {pattern['id']} should have base: true"
            )

    def test_all_have_version(self, patterns: list[dict]) -> None:
        """All patterns have version >= 1."""
        for pattern in patterns:
            assert isinstance(pattern["version"], int) and pattern["version"] >= 1, (
                f"Pattern {pattern['id']} should have version >= 1"
            )

    def test_valid_types(self, patterns: list[dict]) -> None:
        """All patterns use valid types."""
        valid_types = {
            "process",
            "technical",
            "architecture",
            "collaboration",
            "codebase",
        }
        for pattern in patterns:
            assert pattern["type"] in valid_types, (
                f"Pattern {pattern['id']} has invalid type"
            )

    def test_context_is_list(self, patterns: list[dict]) -> None:
        """All patterns have context as list of strings."""
        for pattern in patterns:
            assert isinstance(pattern["context"], list), (
                f"Pattern {pattern['id']} context not list"
            )
            assert all(isinstance(k, str) for k in pattern["context"])


class TestBasePatternsContent:
    """Tests for patterns content coverage."""

    @pytest.fixture
    def patterns(self) -> list[dict]:
        """Load and parse all base patterns."""
        base = files("raise_cli.rai_base")
        content = (base / "memory" / "patterns-base.jsonl").read_text(encoding="utf-8")
        return [
            json.loads(line) for line in content.strip().split("\n") if line.strip()
        ]

    def test_has_process_patterns(self, patterns: list[dict]) -> None:
        """Has process type patterns."""
        process = [p for p in patterns if p["type"] == "process"]
        assert len(process) >= 5, "Need at least 5 process patterns"

    def test_has_technical_patterns(self, patterns: list[dict]) -> None:
        """Has technical type patterns."""
        technical = [p for p in patterns if p["type"] == "technical"]
        assert len(technical) >= 3, "Need at least 3 technical patterns"

    def test_has_collaboration_patterns(self, patterns: list[dict]) -> None:
        """Has collaboration type patterns."""
        collaboration = [p for p in patterns if p["type"] == "collaboration"]
        assert len(collaboration) >= 2, "Need at least 2 collaboration patterns"

    def test_has_architecture_patterns(self, patterns: list[dict]) -> None:
        """Has architecture type patterns."""
        architecture = [p for p in patterns if p["type"] == "architecture"]
        assert len(architecture) >= 1, "Need at least 1 architecture pattern"

    def test_covers_tdd(self, patterns: list[dict]) -> None:
        """Has pattern about TDD."""
        contents = " ".join(p["content"] for p in patterns)
        assert "TDD" in contents or "RED" in contents and "GREEN" in contents

    def test_covers_commits(self, patterns: list[dict]) -> None:
        """Has pattern about commit discipline."""
        contexts = [ctx for p in patterns for ctx in p["context"]]
        assert "commits" in contexts or "git" in contexts

    def test_covers_lifecycle(self, patterns: list[dict]) -> None:
        """Has patterns about feature/epic lifecycle."""
        contexts = [ctx for p in patterns for ctx in p["context"]]
        assert "lifecycle" in contexts

    def test_covers_collaboration(self, patterns: list[dict]) -> None:
        """Has patterns about collaboration style."""
        contexts = [ctx for p in patterns for ctx in p["context"]]
        assert "communication" in contexts or "collaboration" in contexts

    def test_no_project_specific_references(self, patterns: list[dict]) -> None:
        """No patterns reference specific features or epics."""
        for pattern in patterns:
            content = pattern["content"]
            # Should not reference specific feature/epic IDs
            assert "F1." not in content and "F2." not in content
            assert "E1" not in content and "E2" not in content
            # Should not reference specific names
            assert "Emilio" not in content
