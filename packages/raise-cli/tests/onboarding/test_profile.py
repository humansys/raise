"""Tests for developer profile schema and operations."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from raise_cli.onboarding.profile import (
    CORRECTIONS_MAX,
    ActiveSession,
    CoachingContext,
    CommunicationPreferences,
    CommunicationStyle,
    Correction,
    CurrentSession,
    Deadline,
    DeveloperProfile,
    ExperienceLevel,
    RelationshipState,
    add_correction,
    add_deadline,
    end_session,
    get_rai_home,
    increment_session,
    load_developer_profile,
    save_developer_profile,
    start_session,
    update_coaching,
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
            skills_mastered=["rai-session-start", "rai-story-plan"],
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

        profile = DeveloperProfile(name="Fer", experience_level=ExperienceLevel.HA)
        save_developer_profile(profile)

        profile_file = rai_home / "developer.yaml"
        assert profile_file.exists()

        content = yaml.safe_load(profile_file.read_text(encoding="utf-8"))
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
            skills_mastered=["rai-session-start", "rai-story-plan"],
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

        content = yaml.safe_load(profile_file.read_text(encoding="utf-8"))
        assert content["name"] == "New"


class TestSaveDeveloperProfileAdapter:
    """Verify save_developer_profile uses FilesystemAdapter (S1040.2 T4)."""

    def test_delegates_to_adapter_write(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """save_developer_profile should use FilesystemAdapter.write."""
        from unittest.mock import patch

        rai_home = tmp_path / ".rai"
        monkeypatch.setattr(
            "raise_cli.onboarding.profile.get_rai_home", lambda: rai_home
        )

        profile = DeveloperProfile(name="Test")

        with patch(
            "raise_cli.onboarding.profile.FilesystemAdapter"
        ) as mock_adapter_cls:
            save_developer_profile(profile)

            mock_adapter_cls.assert_called_once_with(root=rai_home)
            mock_adapter_cls.return_value.write.assert_called_once()

    def test_adapter_root_is_rai_home(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Adapter should be rooted at ~/.rai, not project root."""
        from unittest.mock import patch

        rai_home = tmp_path / ".rai"
        monkeypatch.setattr(
            "raise_cli.onboarding.profile.get_rai_home", lambda: rai_home
        )

        profile = DeveloperProfile(name="Test")

        with patch(
            "raise_cli.onboarding.profile.FilesystemAdapter"
        ) as mock_adapter_cls:
            save_developer_profile(profile)

            # Verify the adapter is rooted at rai_home
            call_kwargs = mock_adapter_cls.call_args
            assert call_kwargs == ((), {"root": rai_home})


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


# Old tests for deprecated start_session/end_session with current_session removed.
# These functions now use active_sessions list. See TestStartSessionWithActiveSessions
# and TestEndSessionWithActiveSessions for current behavior.


class TestCoachingModels:
    """Tests for coaching-related models."""

    def test_correction_requires_all_fields(self) -> None:
        """Correction requires session, what, lesson."""
        with pytest.raises(ValidationError):
            Correction()  # type: ignore[call-arg]

    def test_correction_valid(self) -> None:
        """Correction accepts all required fields."""
        c = Correction(session="SES-097", what="Skipped design", lesson="Always design")
        assert c.session == "SES-097"
        assert c.what == "Skipped design"
        assert c.lesson == "Always design"

    def test_deadline_requires_name_and_date(self) -> None:
        """Deadline requires name and date."""
        with pytest.raises(ValidationError):
            Deadline()  # type: ignore[call-arg]

    def test_deadline_notes_default_empty(self) -> None:
        """Deadline notes defaults to empty string."""
        d = Deadline(name="F&F", date=date(2026, 2, 9))
        assert d.notes == ""

    def test_relationship_state_defaults(self) -> None:
        """RelationshipState has sensible defaults."""
        r = RelationshipState()
        assert r.quality == "new"
        assert r.since is None
        assert r.trajectory == "starting"

    def test_coaching_context_defaults(self) -> None:
        """CoachingContext defaults to empty/new state."""
        c = CoachingContext()
        assert c.strengths == []
        assert c.growth_edge == ""
        assert c.trust_level == "new"
        assert c.autonomy == ""
        assert c.corrections == []
        assert c.communication_notes == []
        assert c.relationship.quality == "new"


class TestProfileBackwardCompat:
    """Tests for backward compatibility of DeveloperProfile extensions."""

    def test_profile_without_coaching_loads(self) -> None:
        """Profile created without coaching field loads with defaults."""
        profile = DeveloperProfile(name="OldUser")
        assert profile.coaching.strengths == []
        assert profile.coaching.corrections == []
        assert profile.deadlines == []

    def test_load_yaml_without_coaching(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Existing developer.yaml without coaching loads correctly."""
        rai_home = tmp_path / ".rai"
        rai_home.mkdir(parents=True)
        profile_file = rai_home / "developer.yaml"
        # Simulate a pre-S15.7 YAML (no coaching, no deadlines)
        profile_file.write_text(
            "name: LegacyUser\nexperience_level: ha\n"
            "skills_mastered:\n- rai-session-start\n"
        )
        monkeypatch.setattr(
            "raise_cli.onboarding.profile.get_rai_home", lambda: rai_home
        )
        result = load_developer_profile()
        assert result is not None
        assert result.name == "LegacyUser"
        assert result.coaching.strengths == []
        assert result.deadlines == []

    def test_roundtrip_with_coaching(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Profile with coaching survives save/load roundtrip."""
        rai_home = tmp_path / ".rai"
        monkeypatch.setattr(
            "raise_cli.onboarding.profile.get_rai_home", lambda: rai_home
        )
        coaching = CoachingContext(
            strengths=["architecture", "naming"],
            growth_edge="speed over process",
            trust_level="high",
            corrections=[
                Correction(
                    session="SES-096",
                    what="Offered to skip design",
                    lesson="Knowledge != behavior",
                )
            ],
        )
        deadlines = [
            Deadline(name="F&F", date=date(2026, 2, 9), notes="Pre-launch"),
        ]
        original = DeveloperProfile(
            name="Emilio",
            experience_level=ExperienceLevel.RI,
            coaching=coaching,
            deadlines=deadlines,
        )
        save_developer_profile(original)
        loaded = load_developer_profile()

        assert loaded is not None
        assert loaded.coaching.strengths == ["architecture", "naming"]
        assert loaded.coaching.growth_edge == "speed over process"
        assert loaded.coaching.trust_level == "high"
        assert len(loaded.coaching.corrections) == 1
        assert loaded.coaching.corrections[0].session == "SES-096"
        assert len(loaded.deadlines) == 1
        assert loaded.deadlines[0].name == "F&F"
        assert loaded.deadlines[0].date == date(2026, 2, 9)


class TestAddCorrection:
    """Tests for add_correction helper."""

    def test_adds_correction(self) -> None:
        """add_correction adds a correction to coaching."""
        profile = DeveloperProfile(name="Test")
        updated = add_correction(profile, "SES-001", "rushed", "slow down")
        assert len(updated.coaching.corrections) == 1
        assert updated.coaching.corrections[0].what == "rushed"

    def test_fifo_cap(self) -> None:
        """add_correction drops oldest when at CORRECTIONS_MAX."""
        profile = DeveloperProfile(name="Test")
        # Fill to capacity
        for i in range(CORRECTIONS_MAX):
            profile = add_correction(
                profile, f"SES-{i:03d}", f"what-{i}", f"lesson-{i}"
            )
        assert len(profile.coaching.corrections) == CORRECTIONS_MAX
        assert profile.coaching.corrections[0].session == "SES-000"

        # Add one more — oldest drops
        profile = add_correction(profile, "SES-NEW", "new-what", "new-lesson")
        assert len(profile.coaching.corrections) == CORRECTIONS_MAX
        assert profile.coaching.corrections[0].session == "SES-001"
        assert profile.coaching.corrections[-1].session == "SES-NEW"

    def test_preserves_other_coaching_fields(self) -> None:
        """add_correction doesn't touch other coaching fields."""
        coaching = CoachingContext(strengths=["arch"], growth_edge="speed")
        profile = DeveloperProfile(name="Test", coaching=coaching)
        updated = add_correction(profile, "SES-001", "what", "lesson")
        assert updated.coaching.strengths == ["arch"]
        assert updated.coaching.growth_edge == "speed"

    def test_returns_new_instance(self) -> None:
        """add_correction returns a new profile (immutable)."""
        profile = DeveloperProfile(name="Test")
        updated = add_correction(profile, "SES-001", "what", "lesson")
        assert profile is not updated
        assert len(profile.coaching.corrections) == 0


class TestAddDeadline:
    """Tests for add_deadline helper."""

    def test_adds_deadline(self) -> None:
        """add_deadline adds a new deadline."""
        profile = DeveloperProfile(name="Test")
        updated = add_deadline(profile, "F&F", date(2026, 2, 9))
        assert len(updated.deadlines) == 1
        assert updated.deadlines[0].name == "F&F"

    def test_replaces_existing_by_name(self) -> None:
        """add_deadline replaces deadline with same name."""
        profile = DeveloperProfile(name="Test")
        profile = add_deadline(profile, "F&F", date(2026, 2, 9), "old")
        profile = add_deadline(profile, "F&F", date(2026, 2, 10), "updated")
        assert len(profile.deadlines) == 1
        assert profile.deadlines[0].date == date(2026, 2, 10)
        assert profile.deadlines[0].notes == "updated"

    def test_multiple_deadlines(self) -> None:
        """add_deadline supports multiple different deadlines."""
        profile = DeveloperProfile(name="Test")
        profile = add_deadline(profile, "F&F", date(2026, 2, 9))
        profile = add_deadline(profile, "Launch", date(2026, 2, 15))
        assert len(profile.deadlines) == 2

    def test_returns_new_instance(self) -> None:
        """add_deadline returns a new profile (immutable)."""
        profile = DeveloperProfile(name="Test")
        updated = add_deadline(profile, "F&F", date(2026, 2, 9))
        assert profile is not updated
        assert len(profile.deadlines) == 0


class TestUpdateCoaching:
    """Tests for update_coaching helper."""

    def test_updates_strengths(self) -> None:
        """update_coaching updates strengths."""
        profile = DeveloperProfile(name="Test")
        updated = update_coaching(profile, strengths=["arch", "naming"])
        assert updated.coaching.strengths == ["arch", "naming"]

    def test_updates_growth_edge(self) -> None:
        """update_coaching updates growth_edge."""
        profile = DeveloperProfile(name="Test")
        updated = update_coaching(profile, growth_edge="speed over process")
        assert updated.coaching.growth_edge == "speed over process"

    def test_updates_trust_level(self) -> None:
        """update_coaching updates trust_level."""
        profile = DeveloperProfile(name="Test")
        updated = update_coaching(profile, trust_level="high")
        assert updated.coaching.trust_level == "high"

    def test_partial_update_preserves_others(self) -> None:
        """update_coaching only changes specified fields."""
        coaching = CoachingContext(
            strengths=["arch"], growth_edge="speed", trust_level="growing"
        )
        profile = DeveloperProfile(name="Test", coaching=coaching)
        updated = update_coaching(profile, trust_level="high")
        assert updated.coaching.strengths == ["arch"]
        assert updated.coaching.growth_edge == "speed"
        assert updated.coaching.trust_level == "high"

    def test_no_updates_returns_same_profile(self) -> None:
        """update_coaching with no args returns same profile."""
        profile = DeveloperProfile(name="Test")
        updated = update_coaching(profile)
        assert profile is updated

    def test_returns_new_instance(self) -> None:
        """update_coaching returns a new profile (immutable) when updating."""
        profile = DeveloperProfile(name="Test")
        updated = update_coaching(profile, strengths=["test"])
        assert profile is not updated

    def test_updates_relationship_quality(self) -> None:
        """update_coaching updates relationship quality."""
        profile = DeveloperProfile(name="Test")
        updated = update_coaching(profile, relationship={"quality": "productive"})
        assert updated.coaching.relationship.quality == "productive"
        assert updated.coaching.relationship.trajectory == "starting"

    def test_updates_relationship_trajectory(self) -> None:
        """update_coaching updates relationship trajectory."""
        profile = DeveloperProfile(name="Test")
        updated = update_coaching(profile, relationship={"trajectory": "growing"})
        assert updated.coaching.relationship.trajectory == "growing"
        assert updated.coaching.relationship.quality == "new"

    def test_updates_relationship_both_fields(self) -> None:
        """update_coaching updates both relationship fields."""
        profile = DeveloperProfile(name="Test")
        updated = update_coaching(
            profile,
            relationship={"quality": "productive", "trajectory": "growing"},
        )
        assert updated.coaching.relationship.quality == "productive"
        assert updated.coaching.relationship.trajectory == "growing"

    def test_relationship_preserves_existing_fields(self) -> None:
        """update_coaching relationship update preserves unspecified fields."""
        rel = RelationshipState(quality="established", trajectory="stable")
        coaching = CoachingContext(relationship=rel)
        profile = DeveloperProfile(name="Test", coaching=coaching)
        updated = update_coaching(profile, relationship={"trajectory": "growing"})
        assert updated.coaching.relationship.quality == "established"
        assert updated.coaching.relationship.trajectory == "growing"

    def test_updates_communication_notes(self) -> None:
        """update_coaching updates communication_notes."""
        profile = DeveloperProfile(name="Test")
        updated = update_coaching(
            profile, communication_notes=["prefers direct", "skip praise"]
        )
        assert updated.coaching.communication_notes == [
            "prefers direct",
            "skip praise",
        ]

    def test_communication_notes_replaces_existing(self) -> None:
        """update_coaching replaces existing communication_notes."""
        coaching = CoachingContext(communication_notes=["old note"])
        profile = DeveloperProfile(name="Test", coaching=coaching)
        updated = update_coaching(profile, communication_notes=["new note"])
        assert updated.coaching.communication_notes == ["new note"]


class TestActiveSession:
    """Tests for ActiveSession model."""

    def test_creates_with_required_fields(self) -> None:
        """ActiveSession can be created with required fields."""
        session = ActiveSession(
            session_id="SES-177",
            started_at=datetime.now(UTC),
            project="/path/to/project",
        )
        assert session.session_id == "SES-177"
        assert session.project == "/path/to/project"

    def test_agent_defaults_to_unknown(self) -> None:
        """ActiveSession agent field defaults to 'unknown'."""
        session = ActiveSession(
            session_id="SES-177",
            started_at=datetime.now(UTC),
            project="/path/to/project",
        )
        assert session.agent == "unknown"

    def test_agent_can_be_specified(self) -> None:
        """ActiveSession agent field can be set explicitly."""
        session = ActiveSession(
            session_id="SES-177",
            started_at=datetime.now(UTC),
            project="/path/to/project",
            agent="claude-code",
        )
        assert session.agent == "claude-code"

    def test_is_stale_fresh_session(self) -> None:
        """ActiveSession.is_stale() returns False for recent sessions."""
        session = ActiveSession(
            session_id="SES-177",
            started_at=datetime.now(UTC) - timedelta(hours=1),
            project="/path/to/project",
        )
        assert not session.is_stale(hours=24)

    def test_is_stale_old_session(self) -> None:
        """ActiveSession.is_stale() returns True for sessions >24h old."""
        session = ActiveSession(
            session_id="SES-177",
            started_at=datetime.now(UTC) - timedelta(hours=25),
            project="/path/to/project",
        )
        assert session.is_stale(hours=24)

    def test_is_stale_custom_threshold(self) -> None:
        """ActiveSession.is_stale() accepts custom threshold."""
        session = ActiveSession(
            session_id="SES-177",
            started_at=datetime.now(UTC) - timedelta(hours=10),
            project="/path/to/project",
        )
        assert not session.is_stale(hours=24)
        assert session.is_stale(hours=8)


class TestBackwardCompatMigration:
    """Tests for backward compatibility migration."""

    def test_migrates_current_session_clears_stale(self, tmp_path: Path) -> None:
        """load_developer_profile clears stale current_session on migration."""
        # Create old format YAML with current_session (dict)
        old_data = {
            "name": "Test",
            "experience_level": "ri",
            "current_session": {
                "started_at": datetime.now(UTC).isoformat(),
                "project": "/path/to/project",
            },
        }
        profile_path = tmp_path / "developer.yaml"
        with open(profile_path, "w") as f:
            yaml.dump(old_data, f)

        # Mock get_rai_home to return tmp_path
        import raise_cli.onboarding.profile as profile_module

        original_get_rai_home = profile_module.get_rai_home
        profile_module.get_rai_home = lambda: tmp_path

        try:
            # Load profile — should migrate by clearing stale session
            profile = load_developer_profile()

            assert profile is not None
            # active_sessions should be empty (stale session cleared)
            assert len(profile.active_sessions) == 0
            # current_session should be None (removed)
            assert profile.current_session is None

            # Reload to verify migration was saved
            reloaded = load_developer_profile()
            assert reloaded is not None
            assert len(reloaded.active_sessions) == 0
            assert reloaded.current_session is None
        finally:
            profile_module.get_rai_home = original_get_rai_home

    def test_no_migration_when_already_new_format(self, tmp_path: Path) -> None:
        """load_developer_profile doesn't re-migrate new format."""
        # Create new format YAML with active_sessions
        new_data = {
            "name": "Test",
            "experience_level": "ri",
            "active_sessions": [
                {
                    "session_id": "SES-100",
                    "started_at": datetime.now(UTC).isoformat(),
                    "project": "/path/to/project",
                    "agent": "claude-code",
                }
            ],
        }
        profile_path = tmp_path / "developer.yaml"
        with open(profile_path, "w") as f:
            yaml.dump(new_data, f)

        import raise_cli.onboarding.profile as profile_module

        original_get_rai_home = profile_module.get_rai_home
        profile_module.get_rai_home = lambda: tmp_path

        try:
            profile = load_developer_profile()

            assert profile is not None
            assert len(profile.active_sessions) == 1
            assert profile.active_sessions[0].session_id == "SES-100"
        finally:
            profile_module.get_rai_home = original_get_rai_home


class TestStartSessionWithActiveSessions:
    """Tests for start_session using active_sessions list (Task 4)."""

    def test_adds_session_to_active_sessions_list(self) -> None:
        """start_session adds ActiveSession to active_sessions list."""
        profile = DeveloperProfile(name="Test")
        updated, stale = start_session(
            profile,
            session_id="SES-177",
            project_path="/test/project",
            agent="claude-code",
        )
        assert len(updated.active_sessions) == 1
        assert updated.active_sessions[0].session_id == "SES-177"
        assert updated.active_sessions[0].project == "/test/project"
        assert updated.active_sessions[0].agent == "claude-code"
        assert len(stale) == 0  # No stale sessions

    def test_agent_defaults_to_unknown(self) -> None:
        """start_session defaults agent to 'unknown' when not specified."""
        profile = DeveloperProfile(name="Test")
        updated, _ = start_session(profile, session_id="SES-177", project_path="/test")
        assert updated.active_sessions[0].agent == "unknown"

    def test_adds_multiple_sessions(self) -> None:
        """start_session can add multiple sessions for concurrent work."""
        profile = DeveloperProfile(name="Test")
        profile, _ = start_session(profile, session_id="SES-100", project_path="/proj1")
        profile, _ = start_session(
            profile, session_id="SES-101", project_path="/proj2", agent="cursor"
        )
        assert len(profile.active_sessions) == 2
        assert profile.active_sessions[0].session_id == "SES-100"
        assert profile.active_sessions[1].session_id == "SES-101"

    def test_preserves_existing_sessions(self) -> None:
        """start_session preserves existing active_sessions when adding new one."""
        existing = ActiveSession(
            session_id="SES-100",
            started_at=datetime.now(UTC),
            project="/existing",
            agent="other",
        )
        profile = DeveloperProfile(name="Test", active_sessions=[existing])
        updated, _ = start_session(profile, session_id="SES-101", project_path="/new")
        assert len(updated.active_sessions) == 2
        assert updated.active_sessions[0].session_id == "SES-100"
        assert updated.active_sessions[1].session_id == "SES-101"

    def test_returns_stale_sessions_warning(self) -> None:
        """start_session returns list of stale sessions when detected."""
        # Create profile with stale session (>24h old)
        stale = ActiveSession(
            session_id="SES-OLD",
            started_at=datetime.now(UTC) - timedelta(hours=25),
            project="/old",
        )
        profile = DeveloperProfile(name="Test", active_sessions=[stale])

        updated, stale_list = start_session(
            profile, session_id="SES-NEW", project_path="/new"
        )

        assert len(updated.active_sessions) == 2  # Both old and new
        assert len(stale_list) == 1
        assert stale_list[0].session_id == "SES-OLD"

    def test_no_warning_for_fresh_sessions(self) -> None:
        """start_session returns empty list when no stale sessions."""
        fresh = ActiveSession(
            session_id="SES-FRESH",
            started_at=datetime.now(UTC) - timedelta(hours=1),
            project="/fresh",
        )
        profile = DeveloperProfile(name="Test", active_sessions=[fresh])

        updated, stale_list = start_session(
            profile, session_id="SES-NEW", project_path="/new"
        )

        assert len(stale_list) == 0


class TestEndSessionWithActiveSessions:
    """Tests for end_session using active_sessions list (Task 4)."""

    def test_removes_session_from_active_sessions(self) -> None:
        """end_session removes specified session from active_sessions list."""
        session = ActiveSession(
            session_id="SES-177",
            started_at=datetime.now(UTC),
            project="/test",
        )
        profile = DeveloperProfile(name="Test", active_sessions=[session])
        updated = end_session(profile, session_id="SES-177")
        assert len(updated.active_sessions) == 0

    def test_preserves_other_sessions(self) -> None:
        """end_session only removes specified session, keeps others."""
        sessions = [
            ActiveSession(
                session_id="SES-100",
                started_at=datetime.now(UTC),
                project="/proj1",
            ),
            ActiveSession(
                session_id="SES-101",
                started_at=datetime.now(UTC),
                project="/proj2",
            ),
        ]
        profile = DeveloperProfile(name="Test", active_sessions=sessions)
        updated = end_session(profile, session_id="SES-100")

        assert len(updated.active_sessions) == 1
        assert updated.active_sessions[0].session_id == "SES-101"

    def test_noop_when_session_not_found(self) -> None:
        """end_session is no-op when session_id doesn't exist."""
        session = ActiveSession(
            session_id="SES-100",
            started_at=datetime.now(UTC),
            project="/test",
        )
        profile = DeveloperProfile(name="Test", active_sessions=[session])
        updated = end_session(profile, session_id="SES-999")

        # Session list unchanged
        assert len(updated.active_sessions) == 1
        assert updated.active_sessions[0].session_id == "SES-100"

    def test_returns_new_instance(self) -> None:
        """end_session returns new profile instance (immutable)."""
        session = ActiveSession(
            session_id="SES-177",
            started_at=datetime.now(UTC),
            project="/test",
        )
        profile = DeveloperProfile(name="Test", active_sessions=[session])
        updated = end_session(profile, session_id="SES-177")

        assert profile is not updated
        assert len(profile.active_sessions) == 1  # Original unchanged
