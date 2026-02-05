"""Tests for developer profile schema and operations."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from raise_cli.onboarding.profile import (
    CommunicationPreferences,
    CommunicationStyle,
    DeveloperProfile,
    ExperienceLevel,
    get_rai_home,
    load_developer_profile,
    save_developer_profile,
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

    def test_default_sessions_total_is_zero(self) -> None:
        """New developers start with zero sessions."""
        profile = DeveloperProfile(name="Fer")
        assert profile.sessions_total == 0

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
            skills_mastered=["session-start", "feature-plan"],
            universal_patterns=["Commit after each task"],
            sessions_total=40,
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
        assert profile.sessions_total == 40
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

    def test_returns_none_if_file_missing(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """load_developer_profile returns None if file doesn't exist."""
        monkeypatch.setattr("raise_cli.onboarding.profile.get_rai_home", lambda: tmp_path / ".rai")
        result = load_developer_profile()
        assert result is None

    def test_returns_none_if_directory_missing(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """load_developer_profile returns None if ~/.rai/ doesn't exist."""
        fake_home = tmp_path / "nonexistent" / ".rai"
        monkeypatch.setattr("raise_cli.onboarding.profile.get_rai_home", lambda: fake_home)
        result = load_developer_profile()
        assert result is None

    def test_loads_valid_profile(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """load_developer_profile returns DeveloperProfile if file is valid."""
        rai_home = tmp_path / ".rai"
        rai_home.mkdir(parents=True)
        profile_file = rai_home / "developer.yaml"
        profile_file.write_text("name: Fer\nexperience_level: shu\nsessions_total: 5\n")

        monkeypatch.setattr("raise_cli.onboarding.profile.get_rai_home", lambda: rai_home)
        result = load_developer_profile()

        assert result is not None
        assert result.name == "Fer"
        assert result.experience_level == ExperienceLevel.SHU
        assert result.sessions_total == 5

    def test_returns_none_for_invalid_yaml(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """load_developer_profile returns None for invalid YAML."""
        rai_home = tmp_path / ".rai"
        rai_home.mkdir(parents=True)
        profile_file = rai_home / "developer.yaml"
        profile_file.write_text("invalid: yaml: content: [")

        monkeypatch.setattr("raise_cli.onboarding.profile.get_rai_home", lambda: rai_home)
        result = load_developer_profile()
        assert result is None

    def test_returns_none_for_invalid_schema(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """load_developer_profile returns None for invalid schema."""
        rai_home = tmp_path / ".rai"
        rai_home.mkdir(parents=True)
        profile_file = rai_home / "developer.yaml"
        profile_file.write_text("not_a_name: Test\n")  # Missing required 'name' field

        monkeypatch.setattr("raise_cli.onboarding.profile.get_rai_home", lambda: rai_home)
        result = load_developer_profile()
        assert result is None


class TestSaveDeveloperProfile:
    """Tests for save_developer_profile function."""

    def test_creates_rai_directory_if_missing(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """save_developer_profile creates ~/.rai/ if it doesn't exist."""
        rai_home = tmp_path / ".rai"
        monkeypatch.setattr("raise_cli.onboarding.profile.get_rai_home", lambda: rai_home)

        profile = DeveloperProfile(name="Test")
        save_developer_profile(profile)

        assert rai_home.exists()
        assert rai_home.is_dir()

    def test_writes_valid_yaml(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """save_developer_profile writes valid YAML file."""
        rai_home = tmp_path / ".rai"
        monkeypatch.setattr("raise_cli.onboarding.profile.get_rai_home", lambda: rai_home)

        profile = DeveloperProfile(name="Fer", experience_level=ExperienceLevel.HA, sessions_total=10)
        save_developer_profile(profile)

        profile_file = rai_home / "developer.yaml"
        assert profile_file.exists()

        content = yaml.safe_load(profile_file.read_text())
        assert content["name"] == "Fer"
        assert content["experience_level"] == "ha"
        assert content["sessions_total"] == 10

    def test_roundtrip_save_load(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Saved profile can be loaded back correctly."""
        rai_home = tmp_path / ".rai"
        monkeypatch.setattr("raise_cli.onboarding.profile.get_rai_home", lambda: rai_home)

        communication = CommunicationPreferences(
            style=CommunicationStyle.DIRECT,
            skip_praise=True,
            redirect_when_dispersing=True,
        )
        original = DeveloperProfile(
            name="Emilio",
            experience_level=ExperienceLevel.RI,
            communication=communication,
            skills_mastered=["session-start", "feature-plan"],
            universal_patterns=["Commit after each task"],
            sessions_total=40,
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
        assert loaded.sessions_total == original.sessions_total
        assert loaded.first_session == original.first_session
        assert loaded.last_session == original.last_session
        assert loaded.projects == original.projects

    def test_overwrites_existing_profile(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """save_developer_profile overwrites existing file."""
        rai_home = tmp_path / ".rai"
        rai_home.mkdir(parents=True)
        profile_file = rai_home / "developer.yaml"
        profile_file.write_text("name: Old\n")

        monkeypatch.setattr("raise_cli.onboarding.profile.get_rai_home", lambda: rai_home)

        profile = DeveloperProfile(name="New")
        save_developer_profile(profile)

        content = yaml.safe_load(profile_file.read_text())
        assert content["name"] == "New"
