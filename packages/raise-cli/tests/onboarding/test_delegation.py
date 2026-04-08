"""Tests for delegation profile model (S325.2)."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from raise_cli.onboarding.profile import (
    DelegationConfig,
    DelegationLevel,
    DeveloperProfile,
    ExperienceLevel,
    load_developer_profile,
    resolve_delegation,
    save_developer_profile,
)


class TestDelegationLevel:
    """Tests for DelegationLevel enum."""

    def test_enum_values(self) -> None:
        """Enum has exactly review, notify, auto."""
        assert DelegationLevel.REVIEW == "review"
        assert DelegationLevel.NOTIFY == "notify"
        assert DelegationLevel.AUTO == "auto"
        assert len(DelegationLevel) == 3

    def test_enum_from_string(self) -> None:
        """Enum constructs from lowercase string."""
        assert DelegationLevel("review") == DelegationLevel.REVIEW
        assert DelegationLevel("notify") == DelegationLevel.NOTIFY
        assert DelegationLevel("auto") == DelegationLevel.AUTO


class TestDelegationConfig:
    """Tests for DelegationConfig model."""

    def test_minimal_config(self) -> None:
        """Config with just default_level is valid."""
        config = DelegationConfig(default_level=DelegationLevel.NOTIFY)
        assert config.default_level == DelegationLevel.NOTIFY
        assert config.overrides == {}

    def test_config_with_overrides(self) -> None:
        """Config accepts skill-name to level overrides."""
        config = DelegationConfig(
            default_level=DelegationLevel.AUTO,
            overrides={"rai-story-design": DelegationLevel.REVIEW},
        )
        assert config.overrides["rai-story-design"] == DelegationLevel.REVIEW

    def test_config_validates_override_values(self) -> None:
        """Override values must be valid DelegationLevel."""
        with pytest.raises(ValidationError):
            DelegationConfig(
                default_level=DelegationLevel.AUTO,
                overrides={"rai-story-design": "banana"},  # type: ignore[dict-item]
            )


class TestResolveDelegation:
    """Tests for resolve_delegation() precedence."""

    def test_shu_defaults_to_review(self) -> None:
        """Shu experience level → review delegation."""
        profile = DeveloperProfile(name="Dev", experience_level=ExperienceLevel.SHU)
        assert resolve_delegation(profile, "rai-story-design") == DelegationLevel.REVIEW

    def test_ha_defaults_to_notify(self) -> None:
        """Ha experience level → notify delegation."""
        profile = DeveloperProfile(name="Dev", experience_level=ExperienceLevel.HA)
        assert resolve_delegation(profile, "rai-story-design") == DelegationLevel.NOTIFY

    def test_ri_defaults_to_auto(self) -> None:
        """Ri experience level → auto delegation."""
        profile = DeveloperProfile(name="Dev", experience_level=ExperienceLevel.RI)
        assert resolve_delegation(profile, "rai-story-plan") == DelegationLevel.AUTO

    def test_explicit_default_overrides_shuhari(self) -> None:
        """Explicit default_level takes precedence over ShuHaRi derivation."""
        profile = DeveloperProfile(
            name="Dev",
            experience_level=ExperienceLevel.SHU,
            delegation=DelegationConfig(default_level=DelegationLevel.AUTO),
        )
        assert resolve_delegation(profile, "rai-story-design") == DelegationLevel.AUTO

    def test_override_takes_precedence(self) -> None:
        """Per-skill override beats default_level."""
        profile = DeveloperProfile(
            name="Dev",
            experience_level=ExperienceLevel.RI,
            delegation=DelegationConfig(
                default_level=DelegationLevel.AUTO,
                overrides={"rai-story-design": DelegationLevel.REVIEW},
            ),
        )
        assert resolve_delegation(profile, "rai-story-design") == DelegationLevel.REVIEW
        assert resolve_delegation(profile, "rai-story-plan") == DelegationLevel.AUTO

    def test_no_delegation_section_backward_compat(self) -> None:
        """Profile without delegation field uses ShuHaRi defaults."""
        profile = DeveloperProfile(name="Dev", experience_level=ExperienceLevel.HA)
        assert profile.delegation is None
        assert resolve_delegation(profile, "any-skill") == DelegationLevel.NOTIFY

    def test_unknown_skill_uses_default(self) -> None:
        """Skill not in overrides falls back to default_level."""
        profile = DeveloperProfile(
            name="Dev",
            experience_level=ExperienceLevel.HA,
            delegation=DelegationConfig(
                default_level=DelegationLevel.NOTIFY,
                overrides={"rai-story-design": DelegationLevel.REVIEW},
            ),
        )
        assert resolve_delegation(profile, "rai-story-close") == DelegationLevel.NOTIFY


class TestDelegationYamlRoundTrip:
    """Tests for YAML persistence of delegation config."""

    def test_save_and_load_with_delegation(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Profile with delegation round-trips through YAML."""
        monkeypatch.setattr(
            "raise_cli.onboarding.profile.get_rai_home", lambda: tmp_path
        )
        profile = DeveloperProfile(
            name="Dev",
            experience_level=ExperienceLevel.RI,
            delegation=DelegationConfig(
                default_level=DelegationLevel.AUTO,
                overrides={"rai-story-design": DelegationLevel.REVIEW},
            ),
        )
        save_developer_profile(profile)
        loaded = load_developer_profile()
        assert loaded is not None
        assert loaded.delegation is not None
        assert loaded.delegation.default_level == DelegationLevel.AUTO
        assert loaded.delegation.overrides["rai-story-design"] == DelegationLevel.REVIEW

    def test_load_without_delegation_backward_compat(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Profile YAML without delegation key loads fine."""
        monkeypatch.setattr(
            "raise_cli.onboarding.profile.get_rai_home", lambda: tmp_path
        )
        profile = DeveloperProfile(name="Dev", experience_level=ExperienceLevel.HA)
        save_developer_profile(profile)
        loaded = load_developer_profile()
        assert loaded is not None
        assert loaded.delegation is None
        assert resolve_delegation(loaded, "any-skill") == DelegationLevel.NOTIFY
