"""Tests for profile export/import portability."""

from __future__ import annotations

from datetime import date

from raise_cli.onboarding.profile import (
    CoachingContext,
    CommunicationPreferences,
    CommunicationStyle,
    Correction,
    DeveloperProfile,
    ExperienceLevel,
)
from raise_cli.onboarding.profile_portability import (
    MACHINE_LOCAL_FIELDS,
    export_profile,
    import_profile,
    parse_bundle,
    serialize_bundle,
)


def _make_profile() -> DeveloperProfile:
    """Create a fully-populated test profile."""
    return DeveloperProfile(
        name="Emilio",
        pattern_prefix="E",
        experience_level=ExperienceLevel.HA,
        communication=CommunicationPreferences(
            style=CommunicationStyle.DIRECT,
            language="es",
            skip_praise=True,
            redirect_when_dispersing=True,
        ),
        skills_mastered=["rai-story-plan", "rai-story-implement"],
        universal_patterns=["PAT-E-001"],
        first_session=date(2026, 1, 15),
        last_session=date(2026, 3, 6),
        projects=["/home/emilio/Code/raise-commons"],
        active_sessions=[],
        coaching=CoachingContext(
            strengths=["TDD", "architecture"],
            growth_edge="scope management",
            trust_level="high",
            corrections=[
                Correction(session="SES-100", what="skipped tests", lesson="always TDD")
            ],
        ),
    )


class TestExportProfile:
    """Tests for export_profile function."""

    def test_export_produces_bundle_with_meta(self) -> None:
        """Export should produce a bundle with meta containing version, timestamp, machine."""
        profile = _make_profile()
        bundle = export_profile(profile)

        assert bundle.meta.version == 1
        assert bundle.meta.source_machine != ""
        assert bundle.meta.exported_at is not None

    def test_export_strips_machine_local_fields(self) -> None:
        """Export should exclude active_sessions, current_session, projects."""
        profile = _make_profile()
        bundle = export_profile(profile)

        for field in MACHINE_LOCAL_FIELDS:
            assert field not in bundle.profile

    def test_export_preserves_portable_fields(self) -> None:
        """Export should keep name, experience_level, communication, coaching, etc."""
        profile = _make_profile()
        bundle = export_profile(profile)

        assert bundle.profile["name"] == "Emilio"
        assert bundle.profile["pattern_prefix"] == "E"
        assert bundle.profile["experience_level"] == "ha"
        assert bundle.profile["communication"]["language"] == "es"
        assert bundle.profile["coaching"]["strengths"] == ["TDD", "architecture"]

    def test_export_preserves_skills_and_patterns(self) -> None:
        """Export should keep skills_mastered and universal_patterns."""
        profile = _make_profile()
        bundle = export_profile(profile)

        assert bundle.profile["skills_mastered"] == [
            "rai-story-plan",
            "rai-story-implement",
        ]
        assert bundle.profile["universal_patterns"] == ["PAT-E-001"]


class TestSerializeBundle:
    """Tests for serialize_bundle function."""

    def test_serialize_produces_valid_yaml(self) -> None:
        """Serialized bundle should be valid YAML with _meta key."""
        import yaml

        profile = _make_profile()
        bundle = export_profile(profile)
        output = serialize_bundle(bundle)

        parsed = yaml.safe_load(output)
        assert "_meta" in parsed
        assert "profile" in parsed
        assert parsed["_meta"]["version"] == 1

    def test_serialize_meta_uses_underscore_prefix(self) -> None:
        """YAML output should use _meta (with underscore) per contract."""
        profile = _make_profile()
        bundle = export_profile(profile)
        output = serialize_bundle(bundle)

        assert "_meta:" in output


class TestParseBundle:
    """Tests for parse_bundle function."""

    def test_parse_valid_bundle(self) -> None:
        """parse_bundle should reconstruct ProfileBundle from valid YAML."""
        profile = _make_profile()
        bundle = export_profile(profile)
        yaml_str = serialize_bundle(bundle)

        parsed = parse_bundle(yaml_str)
        assert parsed.meta.version == 1
        assert parsed.profile["name"] == "Emilio"

    def test_parse_rejects_missing_meta(self) -> None:
        """parse_bundle should raise ValueError when _meta is missing."""
        import pytest

        bad_yaml = "profile:\n  name: Test\n"
        with pytest.raises(ValueError, match="_meta"):
            parse_bundle(bad_yaml)

    def test_parse_rejects_wrong_version(self) -> None:
        """parse_bundle should raise ValueError for unsupported version."""
        import pytest

        bad_yaml = "_meta:\n  version: 99\n  exported_at: '2026-01-01T00:00:00Z'\n  source_machine: test\nprofile:\n  name: Test\n"
        with pytest.raises(ValueError, match="version"):
            parse_bundle(bad_yaml)

    def test_parse_rejects_missing_profile(self) -> None:
        """parse_bundle should raise ValueError when profile key is missing."""
        import pytest

        bad_yaml = "_meta:\n  version: 1\n  exported_at: '2026-01-01T00:00:00Z'\n  source_machine: test\n"
        with pytest.raises(ValueError, match="profile"):
            parse_bundle(bad_yaml)

    def test_parse_rejects_non_mapping_input(self) -> None:
        """parse_bundle should raise ValueError for scalar YAML."""
        import pytest

        with pytest.raises(ValueError, match="expected YAML mapping"):
            parse_bundle("just a string")

    def test_parse_rejects_empty_input(self) -> None:
        """parse_bundle should raise ValueError for empty input."""
        import pytest

        with pytest.raises(ValueError, match="expected YAML mapping"):
            parse_bundle("")

    def test_parse_rejects_non_dict_meta(self) -> None:
        """parse_bundle should raise ValueError when _meta is not a mapping."""
        import pytest

        bad_yaml = "_meta: not-a-dict\nprofile:\n  name: Test\n"
        with pytest.raises(ValueError, match="_meta must be a mapping"):
            parse_bundle(bad_yaml)

    def test_parse_rejects_non_dict_profile(self) -> None:
        """parse_bundle should raise ValueError when profile is not a mapping."""
        import pytest

        bad_yaml = "_meta:\n  version: 1\n  exported_at: '2026-01-01T00:00:00Z'\n  source_machine: test\nprofile: not-a-dict\n"
        with pytest.raises(ValueError, match="profile must be a mapping"):
            parse_bundle(bad_yaml)


class TestImportProfile:
    """Tests for import_profile function."""

    def test_import_returns_developer_profile(self) -> None:
        """import_profile should return a valid DeveloperProfile."""
        profile = _make_profile()
        bundle = export_profile(profile)

        imported = import_profile(bundle)
        assert isinstance(imported, DeveloperProfile)
        assert imported.name == "Emilio"

    def test_import_clears_machine_local_fields(self) -> None:
        """Imported profile should have empty machine-local fields."""
        profile = _make_profile()
        bundle = export_profile(profile)

        imported = import_profile(bundle)
        assert imported.active_sessions == []
        assert imported.current_session is None
        assert imported.projects == []

    def test_import_preserves_coaching(self) -> None:
        """Imported profile should keep coaching context intact."""
        profile = _make_profile()
        bundle = export_profile(profile)

        imported = import_profile(bundle)
        assert imported.coaching.strengths == ["TDD", "architecture"]
        assert len(imported.coaching.corrections) == 1

    def test_round_trip_preserves_portable_data(self) -> None:
        """Export -> serialize -> parse -> import should preserve all portable fields."""
        original = _make_profile()
        yaml_str = serialize_bundle(export_profile(original))
        imported = import_profile(parse_bundle(yaml_str))

        assert imported.name == original.name
        assert imported.pattern_prefix == original.pattern_prefix
        assert imported.experience_level == original.experience_level
        assert imported.communication == original.communication
        assert imported.skills_mastered == original.skills_mastered
        assert imported.universal_patterns == original.universal_patterns
        assert imported.first_session == original.first_session
        assert imported.last_session == original.last_session
