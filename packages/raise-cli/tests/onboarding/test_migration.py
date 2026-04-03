"""Tests for developer profile migration."""

from __future__ import annotations

import logging
from datetime import date
from pathlib import Path

import pytest

from raise_cli.onboarding.migration import (
    _extract_sessions_data,  # pyright: ignore[reportPrivateUsage]
    _extract_skills_from_sessions,  # pyright: ignore[reportPrivateUsage]
    migrate_developer_profile,
)
from raise_cli.onboarding.profile import (
    CommunicationStyle,
    ExperienceLevel,
)


class TestExtractSessionsData:
    """Tests for _extract_sessions_data function."""

    def test_returns_zeros_if_file_missing(self, tmp_path: Path) -> None:
        """Returns zero sessions if index file doesn't exist."""
        sessions_path = tmp_path / "nonexistent.jsonl"
        total, first, last = _extract_sessions_data(sessions_path)
        assert total == 0
        assert first is None
        assert last is None

    def test_counts_sessions(self, tmp_path: Path) -> None:
        """Counts total number of sessions."""
        sessions_path = tmp_path / "index.jsonl"
        sessions_path.write_text(
            '{"id": "SES-001", "date": "2026-02-01"}\n'
            '{"id": "SES-002", "date": "2026-02-02"}\n'
            '{"id": "SES-003", "date": "2026-02-03"}\n'
        )
        total, _, _ = _extract_sessions_data(sessions_path)
        assert total == 3

    def test_extracts_date_range(self, tmp_path: Path) -> None:
        """Extracts first and last session dates."""
        sessions_path = tmp_path / "index.jsonl"
        sessions_path.write_text(
            '{"id": "SES-001", "date": "2026-02-03"}\n'
            '{"id": "SES-002", "date": "2026-02-01"}\n'
            '{"id": "SES-003", "date": "2026-02-05"}\n'
        )
        _, first, last = _extract_sessions_data(sessions_path)
        assert first == date(2026, 2, 1)
        assert last == date(2026, 2, 5)

    def test_handles_missing_dates(self, tmp_path: Path) -> None:
        """Handles sessions without date field."""
        sessions_path = tmp_path / "index.jsonl"
        sessions_path.write_text(
            '{"id": "SES-001"}\n{"id": "SES-002", "date": "2026-02-02"}\n'
        )
        total, first, last = _extract_sessions_data(sessions_path)
        assert total == 2
        assert first == date(2026, 2, 2)
        assert last == date(2026, 2, 2)

    def test_handles_invalid_json(self, tmp_path: Path) -> None:
        """Skips invalid JSON lines."""
        sessions_path = tmp_path / "index.jsonl"
        sessions_path.write_text(
            '{"id": "SES-001", "date": "2026-02-01"}\n'
            "invalid json line\n"
            '{"id": "SES-002", "date": "2026-02-02"}\n'
        )
        total, first, last = _extract_sessions_data(sessions_path)
        assert total == 2
        assert first == date(2026, 2, 1)
        assert last == date(2026, 2, 2)


class TestExtractSkillsFromSessions:
    """Tests for _extract_skills_from_sessions function."""

    def test_returns_empty_if_file_missing(self, tmp_path: Path) -> None:
        """Returns empty list if index file doesn't exist."""
        sessions_path = tmp_path / "nonexistent.jsonl"
        skills = _extract_skills_from_sessions(sessions_path)
        assert skills == []

    def test_extracts_skills_from_outcomes(self, tmp_path: Path) -> None:
        """Extracts skill names mentioned in outcomes."""
        sessions_path = tmp_path / "index.jsonl"
        sessions_path.write_text(
            '{"id": "SES-001", "outcomes": ["/rai-session-start skill created", "tests passing"]}\n'
            '{"id": "SES-002", "outcomes": ["rai-story-plan complete"]}\n'
        )
        skills = _extract_skills_from_sessions(sessions_path)
        assert "rai-session-start" in skills
        assert "rai-story-plan" in skills

    def test_extracts_skills_from_topic(self, tmp_path: Path) -> None:
        """Extracts skill names mentioned in topic."""
        sessions_path = tmp_path / "index.jsonl"
        sessions_path.write_text(
            '{"id": "SES-001", "topic": "Rai Epic Design Session"}\n'
        )
        skills = _extract_skills_from_sessions(sessions_path)
        assert "rai-epic-design" in skills

    def test_deduplicates_skills(self, tmp_path: Path) -> None:
        """Returns unique skills only."""
        sessions_path = tmp_path / "index.jsonl"
        sessions_path.write_text(
            '{"id": "SES-001", "outcomes": ["rai-session-start done"]}\n'
            '{"id": "SES-002", "outcomes": ["/rai-session-start again"]}\n'
        )
        skills = _extract_skills_from_sessions(sessions_path)
        assert skills.count("rai-session-start") == 1

    def test_returns_sorted_skills(self, tmp_path: Path) -> None:
        """Returns skills in sorted order."""
        sessions_path = tmp_path / "index.jsonl"
        sessions_path.write_text(
            '{"id": "SES-001", "outcomes": ["rai-research done", "rai-debug used"]}\n'
        )
        skills = _extract_skills_from_sessions(sessions_path)
        assert skills == sorted(skills)


class TestMigrateDeveloperProfile:
    """Tests for migrate_developer_profile function."""

    def test_creates_profile_with_name(self, tmp_path: Path) -> None:
        """Creates profile with correct name."""
        profile = migrate_developer_profile(tmp_path)
        assert profile.name == "Developer"

    def test_creates_profile_with_custom_name(self, tmp_path: Path) -> None:
        """Creates profile with custom name."""
        profile = migrate_developer_profile(tmp_path, name="Test")
        assert profile.name == "Test"

    def test_sets_ri_experience_level(self, tmp_path: Path) -> None:
        """Sets experience level to Ri (expert)."""
        profile = migrate_developer_profile(tmp_path)
        assert profile.experience_level == ExperienceLevel.RI

    def test_sets_direct_communication_style(self, tmp_path: Path) -> None:
        """Sets communication style to direct."""
        profile = migrate_developer_profile(tmp_path)
        assert profile.communication.style == CommunicationStyle.DIRECT

    def test_sets_skip_praise_true(self, tmp_path: Path) -> None:
        """Sets skip_praise to True."""
        profile = migrate_developer_profile(tmp_path)
        assert profile.communication.skip_praise is True

    def test_sets_redirect_permission_true(self, tmp_path: Path) -> None:
        """Sets redirect_when_dispersing to True."""
        profile = migrate_developer_profile(tmp_path)
        assert profile.communication.redirect_when_dispersing is True

    def test_includes_universal_patterns(self, tmp_path: Path) -> None:
        """Includes known universal patterns."""
        profile = migrate_developer_profile(tmp_path)
        assert len(profile.universal_patterns) > 0
        assert "Commit after each completed task" in profile.universal_patterns

    def test_includes_project_path(self, tmp_path: Path) -> None:
        """Includes project path in projects list."""
        profile = migrate_developer_profile(tmp_path)
        assert str(tmp_path) in profile.projects

    def test_extracts_sessions_from_real_data(self, tmp_path: Path) -> None:
        """Extracts session data from memory directory."""
        # Create mock memory structure
        memory_path = tmp_path / ".raise/rai" / "memory" / "sessions"
        memory_path.mkdir(parents=True)
        index_path = memory_path / "index.jsonl"
        index_path.write_text(
            '{"id": "SES-001", "date": "2026-02-01", "outcomes": ["rai-session-start created"]}\n'
            '{"id": "SES-002", "date": "2026-02-02", "outcomes": ["rai-story-plan done"]}\n'
            '{"id": "SES-003", "date": "2026-02-03", "outcomes": ["rai-epic-design complete"]}\n'
        )

        profile = migrate_developer_profile(tmp_path)

        assert profile.first_session == date(2026, 2, 1)
        assert profile.last_session == date(2026, 2, 3)
        assert "rai-session-start" in profile.skills_mastered
        assert "rai-story-plan" in profile.skills_mastered
        assert "rai-epic-design" in profile.skills_mastered

    def test_handles_missing_memory_directory(self, tmp_path: Path) -> None:
        """Handles missing .raise/rai/memory directory gracefully."""
        profile = migrate_developer_profile(tmp_path)
        assert profile.first_session is None
        assert profile.last_session is None

    def test_accepts_additional_skills(self, tmp_path: Path) -> None:
        """Accepts additional skills parameter."""
        profile = migrate_developer_profile(
            tmp_path,
            additional_skills=["custom-skill", "another-skill"],
        )
        assert "custom-skill" in profile.skills_mastered
        assert "another-skill" in profile.skills_mastered

    def test_merges_detected_and_additional_skills(self, tmp_path: Path) -> None:
        """Merges detected skills with additional skills."""
        memory_path = tmp_path / ".raise/rai" / "memory" / "sessions"
        memory_path.mkdir(parents=True)
        index_path = memory_path / "index.jsonl"
        index_path.write_text('{"id": "SES-001", "outcomes": ["rai-debug used"]}\n')

        profile = migrate_developer_profile(
            tmp_path,
            additional_skills=["custom-skill"],
        )

        assert "rai-debug" in profile.skills_mastered
        assert "custom-skill" in profile.skills_mastered


class TestLogInjection:
    """Regression tests for log injection (RAISE-533)."""

    def test_control_chars_stripped_from_log_output(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Control characters in JSONL must be sanitized before logging (RAISE-533)."""
        sessions_path = tmp_path / "index.jsonl"
        # Craft a line with ANSI escape and carriage return (survive splitlines)
        malicious = "bad json \x1b[31mRED\x1b[0m \x00null"
        sessions_path.write_text(malicious + "\n")

        with caplog.at_level(logging.WARNING, logger="raise_cli.onboarding.migration"):
            _extract_sessions_data(sessions_path)

        for record in caplog.records:
            msg = record.getMessage()
            assert "\x1b" not in msg, f"ANSI escape in log: {msg!r}"
            assert "\x00" not in msg, f"Null byte in log: {msg!r}"
