"""Tests for developer profile schema and operations."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from raise_cli.onboarding.profile import (
    CommunicationPreferences,
    CommunicationStyle,
    CurrentSession,
    DeveloperProfile,
    ExperienceLevel,
    end_session,
    get_rai_home,
    increment_session,
    load_developer_profile,
    save_developer_profile,
    start_session,
)


class TestExperienceLevel:
    """Tests for ExperienceLevel enum."""

    def test_has_shu_level(self) -> None:
        """ExperienceLevel has shu (beginner) level."""
        assert ExperienceLevel.SHU.value == "shu"

    def test_has_ha_level(self) -> None:
        """ExperienceLevel has ha (intermediate) level."""
        assert ExperienceLevel.HA.value == "ha"

    def test_has_ri_level(self) -> None:
        """ExperienceLevel has ri (expert) level."""
        assert ExperienceLevel.RI.value == "ri"

    def test_only_three_levels(self) -> None:
        """ExperienceLevel has exactly three levels."""
        assert len(ExperienceLevel) == 3


class TestCommunicationStyle:
    """Tests for CommunicationStyle enum."""

    def test_has_explanatory_style(self) -> None:
        """CommunicationStyle has explanatory option."""
        assert CommunicationStyle.EXPLANATORY.value == "explanatory"

    def test_has_balanced_style(self) -> None:
        """CommunicationStyle has balanced option."""
        assert CommunicationStyle.BALANCED.value == "balanced"

    def test_has_direct_style(self) -> None:
        """CommunicationStyle has direct option."""
        assert CommunicationStyle.DIRECT.value == "direct"

    def test_only_three_styles(self) -> None:
        """CommunicationStyle has exactly three options."""
        assert len(CommunicationStyle) == 3


class TestCommunicationPreferences:
    """Tests for CommunicationPreferences model."""

    def test_default_style_is_balanced(self) -> None:
        """Default communication style is balanced."""
        prefs = CommunicationPreferences()
        assert prefs.style == CommunicationStyle.BALANCED

    def test_default_language_is_english(self) -> None:
        """Default language is English."""
        prefs = CommunicationPreferences()
        assert prefs.language == "en"

    def test_default_skip_praise_is_false(self) -> None:
        """Default skip_praise is False (praise allowed)."""
        prefs = CommunicationPreferences()
        assert prefs.skip_praise is False

    def test_default_detailed_explanations_is_true(self) -> None:
        """Default detailed_explanations is True."""
        prefs = CommunicationPreferences()
        assert prefs.detailed_explanations is True

    def test_default_redirect_is_false(self) -> None:
        """Default redirect_when_dispersing is False."""
        prefs = CommunicationPreferences()
        assert prefs.redirect_when_dispersing is False

    def test_custom_preferences(self) -> None:
        """CommunicationPreferences accepts all custom values."""
        prefs = CommunicationPreferences(
            style=CommunicationStyle.DIRECT,
            language="es",
            skip_praise=True,
            detailed_explanations=False,
            redirect_when_dispersing=True,
        )
        assert prefs.style == CommunicationStyle.DIRECT
        assert prefs.language == "es"
        assert prefs.skip_praise is True
        assert prefs.detailed_explanations is False
        assert prefs.redirect_when_dispersing is True

    def test_style_from_string(self) -> None:
        """CommunicationStyle can be set from string value."""
        prefs = CommunicationPreferences(style="direct")
        assert prefs.style == CommunicationStyle.DIRECT


class TestDeveloperProfile:
    """Tests for DeveloperProfile model."""

    def test_requires_name(self) -> None:
        """DeveloperProfile requires name field."""
        with pytest.raises(ValidationError):
            DeveloperProfile()  # type: ignore[call-arg]

    def test_minimal_profile(self) -> None:
        """DeveloperProfile can be created with just name."""
        profile = DeveloperProfile(name="Fer")
        assert profile.name == "Fer"

    def test_default_experience_level_is_shu(self) -> None:
        """New developers default to shu (beginner) level."""
        profile = DeveloperProfile(name="Fer")
        assert profile.experience_level == ExperienceLevel.SHU

    def test_default_dates_are_none(self) -> None:
        """New profiles have no session dates."""
        profile = DeveloperProfile(name="Fer")
        assert profile.first_session is None
        assert profile.last_session is None

    def test_default_projects_is_empty(self) -> None:
        """New profiles have no projects."""
        profile = DeveloperProfile(name="Fer")
        assert profile.projects == []

    def test_default_communication_preferences(self) -> None:
        """New profiles have default communication preferences."""
        profile = DeveloperProfile(name="Fer")
        assert profile.communication.style == CommunicationStyle.BALANCED
        assert profile.communication.language == "en"

    def test_default_skills_mastered_is_empty(self) -> None:
        """New profiles have no mastered skills."""
        profile = DeveloperProfile(name="Fer")
        assert profile.skills_mastered == []

    def test_default_universal_patterns_is_empty(self) -> None:
        """New profiles have no universal patterns."""
        profile = DeveloperProfile(name="Fer")
        assert profile.universal_patterns == []

    def test_full_profile(self) -> None:
        """DeveloperProfile accepts all fields."""
        communication = CommunicationPreferences(
            style=CommunicationStyle.DIRECT,
            language="en",
            skip_praise=True,
            detailed_explanations=False,
            redirect_when_dispersing=True,
        )
        profile = DeveloperProfile(
            name="Emilio",
            experience_level=ExperienceLevel.RI,
            communication=communication,
            skills_mastered=["session-start", "story-plan"],
            universal_patterns=["Commit after each task"],

            first_session=date(2026, 2, 1),
            last_session=date(2026, 2, 4),
            projects=["/home/emilio/Code/raise-commons"],
        )
        assert profile.name == "Emilio"
        assert profile.experience_level == ExperienceLevel.RI
        assert profile.communication.style == CommunicationStyle.DIRECT
        assert profile.communication.skip_praise is True
        assert len(profile.skills_mastered) == 2
        assert len(profile.universal_patterns) == 1
        assert profile.first_session == date(2026, 2, 1)
        assert profile.last_session == date(2026, 2, 4)
        assert len(profile.projects) == 1

    def test_experience_level_from_string(self) -> None:
        """ExperienceLevel can be set from string value."""
        profile = DeveloperProfile(name="Test", experience_level="ha")
        assert profile.experience_level == ExperienceLevel.HA

    def test_invalid_experience_level_rejected(self) -> None:
        """Invalid experience level raises ValidationError."""
        with pytest.raises(ValidationError):
            DeveloperProfile(name="Test", experience_level="expert")


class TestGetRaiHome:
    """Tests for get_rai_home function."""

    def test_returns_path_in_home_directory(self) -> None:
        """get_rai_home returns path under user's home directory."""
        rai_home = get_rai_home()
        assert rai_home.parent == Path.home()

    def test_returns_dot_rai_directory(self) -> None:
        """get_rai_home returns .rai directory."""
        rai_home = get_rai_home()
        assert rai_home.name == ".rai"


class TestLoadDeveloperProfile:
    """Tests for load_developer_profile function."""

    def test_returns_none_if_file_missing(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """load_developer_profile returns None if file doesn't exist."""
        monkeypatch.setattr(
            "raise_cli.onboarding.profile.get_rai_home", lambda: tmp_path / ".rai"
        )
        result = load_developer_profile()
        assert result is None

    def test_returns_none_if_directory_missing(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """load_developer_profile returns None if ~/.rai/ doesn't exist."""
        fake_home = tmp_path / "nonexistent" / ".rai"
        monkeypatch.setattr(
            "raise_cli.onboarding.profile.get_rai_home", lambda: fake_home
        )
        result = load_developer_profile()
        assert result is None

    def test_loads_valid_profile(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """load_developer_profile returns DeveloperProfile if file is valid."""
        rai_home = tmp_path / ".rai"
        rai_home.mkdir(parents=True)
        profile_file = rai_home / "developer.yaml"
        profile_file.write_text("name: Fer\nexperience_level: shu\n")

        monkeypatch.setattr(
            "raise_cli.onboarding.profile.get_rai_home", lambda: rai_home
        )
        result = load_developer_profile()

        assert result is not None
        assert result.name == "Fer"
        assert result.experience_level == ExperienceLevel.SHU

    def test_returns_none_for_invalid_yaml(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """load_developer_profile returns None for invalid YAML."""
        rai_home = tmp_path / ".rai"
        rai_home.mkdir(parents=True)
        profile_file = rai_home / "developer.yaml"
        profile_file.write_text("invalid: yaml: content: [")

        monkeypatch.setattr(
            "raise_cli.onboarding.profile.get_rai_home", lambda: rai_home
        )
        result = load_developer_profile()
        assert result is None

    def test_returns_none_for_invalid_schema(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """load_developer_profile returns None for invalid schema."""
        rai_home = tmp_path / ".rai"
        rai_home.mkdir(parents=True)
        profile_file = rai_home / "developer.yaml"
        profile_file.write_text("not_a_name: Test\n")  # Missing required 'name' field

        monkeypatch.setattr(
            "raise_cli.onboarding.profile.get_rai_home", lambda: rai_home
        )
        result = load_developer_profile()
        assert result is None


class TestSaveDeveloperProfile:
    """Tests for save_developer_profile function."""

    def test_creates_rai_directory_if_missing(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """save_developer_profile creates ~/.rai/ if it doesn't exist."""
        rai_home = tmp_path / ".rai"
        monkeypatch.setattr(
            "raise_cli.onboarding.profile.get_rai_home", lambda: rai_home
        )

        profile = DeveloperProfile(name="Test")
        save_developer_profile(profile)

        assert rai_home.exists()
        assert rai_home.is_dir()

    def test_writes_valid_yaml(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """save_developer_profile writes valid YAML file."""
        rai_home = tmp_path / ".rai"
        monkeypatch.setattr(
            "raise_cli.onboarding.profile.get_rai_home", lambda: rai_home
        )

        profile = DeveloperProfile(
            name="Fer", experience_level=ExperienceLevel.HA
        )
        save_developer_profile(profile)

        profile_file = rai_home / "developer.yaml"
        assert profile_file.exists()

        content = yaml.safe_load(profile_file.read_text())
        assert content["name"] == "Fer"
        assert content["experience_level"] == "ha"

    def test_roundtrip_save_load(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Saved profile can be loaded back correctly."""
        rai_home = tmp_path / ".rai"
        monkeypatch.setattr(
            "raise_cli.onboarding.profile.get_rai_home", lambda: rai_home
        )

        communication = CommunicationPreferences(
            style=CommunicationStyle.DIRECT,
            skip_praise=True,
            redirect_when_dispersing=True,
        )
        original = DeveloperProfile(
            name="Emilio",
            experience_level=ExperienceLevel.RI,
            communication=communication,
            skills_mastered=["session-start", "story-plan"],
            universal_patterns=["Commit after each task"],

            first_session=date(2026, 2, 1),
            last_session=date(2026, 2, 4),
            projects=["/home/emilio/Code/raise-commons"],
        )
        save_developer_profile(original)
        loaded = load_developer_profile()

        assert loaded is not None
        assert loaded.name == original.name
        assert loaded.experience_level == original.experience_level
        assert loaded.communication.style == original.communication.style
        assert loaded.communication.skip_praise == original.communication.skip_praise
        assert loaded.skills_mastered == original.skills_mastered
        assert loaded.universal_patterns == original.universal_patterns
        assert loaded.first_session == original.first_session
        assert loaded.last_session == original.last_session
        assert loaded.projects == original.projects

    def test_overwrites_existing_profile(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """save_developer_profile overwrites existing file."""
        rai_home = tmp_path / ".rai"
        rai_home.mkdir(parents=True)
        profile_file = rai_home / "developer.yaml"
        profile_file.write_text("name: Old\n")

        monkeypatch.setattr(
            "raise_cli.onboarding.profile.get_rai_home", lambda: rai_home
        )

        profile = DeveloperProfile(name="New")
        save_developer_profile(profile)

        content = yaml.safe_load(profile_file.read_text())
        assert content["name"] == "New"


class TestIncrementSession:
    """Tests for increment_session function."""

    def test_updates_last_session_to_today(self) -> None:
        """increment_session sets last_session to today's date."""
        profile = DeveloperProfile(name="Test", last_session=date(2026, 1, 1))
        updated = increment_session(profile)
        assert updated.last_session == date.today()

    def test_adds_new_project_path(self) -> None:
        """increment_session adds project_path to projects list."""
        profile = DeveloperProfile(name="Test", projects=[])
        updated = increment_session(profile, project_path="/home/user/project")
        assert "/home/user/project" in updated.projects

    def test_does_not_duplicate_project_path(self) -> None:
        """increment_session doesn't add duplicate project paths."""
        profile = DeveloperProfile(name="Test", projects=["/home/user/project"])
        updated = increment_session(profile, project_path="/home/user/project")
        assert updated.projects.count("/home/user/project") == 1
        assert len(updated.projects) == 1

    def test_preserves_existing_projects(self) -> None:
        """increment_session preserves existing projects when adding new one."""
        profile = DeveloperProfile(name="Test", projects=["/home/user/project1"])
        updated = increment_session(profile, project_path="/home/user/project2")
        assert "/home/user/project1" in updated.projects
        assert "/home/user/project2" in updated.projects
        assert len(updated.projects) == 2

    def test_works_without_project_path(self) -> None:
        """increment_session works when project_path is None."""
        profile = DeveloperProfile(name="Test", projects=["/existing"])
        updated = increment_session(profile)
        assert updated.last_session == date.today()
        assert updated.projects == ["/existing"]

    def test_returns_new_instance(self) -> None:
        """increment_session returns a new profile instance (immutable)."""
        profile = DeveloperProfile(name="Test", last_session=date(2026, 1, 1))
        updated = increment_session(profile)
        assert profile is not updated
        assert profile.last_session == date(2026, 1, 1)  # Original unchanged

    def test_preserves_other_fields(self) -> None:
        """increment_session preserves all other profile fields."""
        profile = DeveloperProfile(
            name="Emilio",
            experience_level=ExperienceLevel.RI,
            skills_mastered=["skill1", "skill2"],
            universal_patterns=["pattern1"],
            first_session=date(2026, 1, 1),

        )
        updated = increment_session(profile, project_path="/new/project")
        assert updated.name == "Emilio"
        assert updated.experience_level == ExperienceLevel.RI
        assert updated.skills_mastered == ["skill1", "skill2"]
        assert updated.universal_patterns == ["pattern1"]
        assert updated.first_session == date(2026, 1, 1)


class TestCurrentSession:
    """Tests for CurrentSession model."""

    def test_requires_started_at_and_project(self) -> None:
        """CurrentSession requires both started_at and project."""
        now = datetime.now(UTC)
        session = CurrentSession(started_at=now, project="/home/user/project")
        assert session.started_at == now
        assert session.project == "/home/user/project"

    def test_is_stale_returns_false_for_recent_session(self) -> None:
        """is_stale returns False for session started recently."""
        now = datetime.now(UTC)
        session = CurrentSession(started_at=now, project="/test")
        assert session.is_stale() is False

    def test_is_stale_returns_true_for_old_session(self) -> None:
        """is_stale returns True for session started more than 24h ago."""
        old_time = datetime.now(UTC) - timedelta(hours=25)
        session = CurrentSession(started_at=old_time, project="/test")
        assert session.is_stale() is True

    def test_is_stale_custom_hours(self) -> None:
        """is_stale respects custom hours parameter."""
        old_time = datetime.now(UTC) - timedelta(hours=5)
        session = CurrentSession(started_at=old_time, project="/test")
        assert session.is_stale(hours=4) is True
        assert session.is_stale(hours=6) is False

    def test_is_stale_boundary_at_24_hours(self) -> None:
        """is_stale boundary: under 24h is not stale, over 24h is."""
        # Just under 24 hours - not stale
        under_24h = datetime.now(UTC) - timedelta(hours=23, minutes=59)
        session = CurrentSession(started_at=under_24h, project="/test")
        assert session.is_stale() is False

        # Just over 24 hours - stale
        over_24h = datetime.now(UTC) - timedelta(hours=24, minutes=1)
        session_old = CurrentSession(started_at=over_24h, project="/test")
        assert session_old.is_stale() is True


class TestStartSession:
    """Tests for start_session function."""

    def test_sets_current_session(self) -> None:
        """start_session sets current_session field."""
        profile = DeveloperProfile(name="Test")
        updated = start_session(profile, "/home/user/project")
        assert updated.current_session is not None
        assert updated.current_session.project == "/home/user/project"

    def test_sets_started_at_to_now(self) -> None:
        """start_session sets started_at to current UTC time."""
        profile = DeveloperProfile(name="Test")
        before = datetime.now(UTC)
        updated = start_session(profile, "/test")
        after = datetime.now(UTC)

        assert updated.current_session is not None
        assert before <= updated.current_session.started_at <= after

    def test_returns_new_instance(self) -> None:
        """start_session returns new profile instance (immutable)."""
        profile = DeveloperProfile(name="Test")
        updated = start_session(profile, "/test")
        assert profile is not updated
        assert profile.current_session is None  # Original unchanged

    def test_preserves_other_fields(self) -> None:
        """start_session preserves all other profile fields."""
        profile = DeveloperProfile(
            name="Emilio",
            experience_level=ExperienceLevel.RI,
        )
        updated = start_session(profile, "/test")
        assert updated.name == "Emilio"
        assert updated.experience_level == ExperienceLevel.RI


class TestEndSession:
    """Tests for end_session function."""

    def test_clears_current_session(self) -> None:
        """end_session clears current_session field."""
        profile = DeveloperProfile(name="Test")
        with_session = start_session(profile, "/test")
        assert with_session.current_session is not None

        ended = end_session(with_session)
        assert ended.current_session is None

    def test_works_when_no_session_active(self) -> None:
        """end_session is a no-op when no session is active."""
        profile = DeveloperProfile(name="Test")
        assert profile.current_session is None
        ended = end_session(profile)
        assert ended.current_session is None

    def test_returns_new_instance(self) -> None:
        """end_session returns new profile instance (immutable)."""
        profile = DeveloperProfile(name="Test")
        with_session = start_session(profile, "/test")
        ended = end_session(with_session)
        assert with_session is not ended
        assert with_session.current_session is not None  # Original unchanged

    def test_preserves_other_fields(self) -> None:
        """end_session preserves all other profile fields."""
        profile = DeveloperProfile(
            name="Emilio",
            experience_level=ExperienceLevel.RI,
        )
        with_session = start_session(profile, "/test")
        ended = end_session(with_session)
        assert ended.name == "Emilio"
        assert ended.experience_level == ExperienceLevel.RI


class TestDeveloperProfileCurrentSession:
    """Tests for current_session field in DeveloperProfile."""

    def test_default_current_session_is_none(self) -> None:
        """New profiles have no active session."""
        profile = DeveloperProfile(name="Test")
        assert profile.current_session is None

    def test_current_session_roundtrip(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """current_session survives save/load roundtrip."""
        rai_home = tmp_path / ".rai"
        monkeypatch.setattr(
            "raise_cli.onboarding.profile.get_rai_home", lambda: rai_home
        )

        profile = DeveloperProfile(name="Test")
        with_session = start_session(profile, "/test/project")
        save_developer_profile(with_session)

        loaded = load_developer_profile()
        assert loaded is not None
        assert loaded.current_session is not None
        assert loaded.current_session.project == "/test/project"
