"""Tests for the skill manifest — tracks distributed skills for upgrade detection."""

from __future__ import annotations

import json
from pathlib import Path

from raise_cli.onboarding.skill_manifest import (
    SkillEntry,
    SkillManifest,
    SkillSyncAction,
    classify_skill,
    compute_content_hash,
    load_skill_manifest,
    save_skill_manifest,
)


class TestSkillEntry:
    """Tests for SkillEntry model."""

    def test_creates_with_required_fields(self) -> None:
        entry = SkillEntry(sha256="abc123", version="2.1.0", origin="framework")
        assert entry.sha256 == "abc123"
        assert entry.version == "2.1.0"
        assert entry.origin == "framework"

    def test_origin_defaults_to_framework(self) -> None:
        entry = SkillEntry(sha256="abc123", version="2.1.0")
        assert entry.origin == "framework"

    def test_distributed_at_is_set(self) -> None:
        entry = SkillEntry(sha256="abc123", version="2.1.0")
        assert entry.distributed_at is not None


class TestSkillManifest:
    """Tests for SkillManifest model."""

    def test_empty_manifest(self) -> None:
        manifest = SkillManifest()
        assert manifest.schema_version == "1.0"
        assert manifest.skills == {}
        assert manifest.raise_cli_version is not None

    def test_manifest_with_skills(self) -> None:
        manifest = SkillManifest(
            skills={
                "rai-session-start": SkillEntry(
                    sha256="abc", version="2.0.0", origin="framework"
                )
            }
        )
        assert "rai-session-start" in manifest.skills
        assert manifest.skills["rai-session-start"].sha256 == "abc"


class TestSaveLoadManifest:
    """Tests for manifest persistence."""

    def test_save_creates_file(self, tmp_path: Path) -> None:
        manifest = SkillManifest(
            skills={"rai-session-start": SkillEntry(sha256="abc123", version="2.0.0")}
        )
        save_skill_manifest(manifest, tmp_path)

        manifest_path = tmp_path / ".raise" / "manifests" / "skills.json"
        assert manifest_path.exists()

    def test_save_produces_valid_json(self, tmp_path: Path) -> None:
        manifest = SkillManifest(
            skills={"rai-session-start": SkillEntry(sha256="abc123", version="2.0.0")}
        )
        save_skill_manifest(manifest, tmp_path)

        manifest_path = tmp_path / ".raise" / "manifests" / "skills.json"
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert data["schema_version"] == "1.0"
        assert "rai-session-start" in data["skills"]

    def test_load_roundtrip(self, tmp_path: Path) -> None:
        original = SkillManifest(
            skills={
                "rai-session-start": SkillEntry(
                    sha256="abc123", version="2.0.0", origin="framework"
                ),
                "rai-epic-close": SkillEntry(
                    sha256="def456", version="2.0.0", origin="org"
                ),
            }
        )
        save_skill_manifest(original, tmp_path)
        loaded = load_skill_manifest(tmp_path)

        assert loaded is not None
        assert loaded.skills["rai-session-start"].sha256 == "abc123"
        assert loaded.skills["rai-epic-close"].origin == "org"

    def test_load_missing_file_returns_none(self, tmp_path: Path) -> None:
        result = load_skill_manifest(tmp_path)
        assert result is None

    def test_load_corrupt_json_returns_none(self, tmp_path: Path) -> None:
        manifest_dir = tmp_path / ".raise" / "manifests"
        manifest_dir.mkdir(parents=True)
        (manifest_dir / "skills.json").write_text("not json {{{", encoding="utf-8")

        result = load_skill_manifest(tmp_path)
        assert result is None

    def test_load_invalid_schema_returns_none(self, tmp_path: Path) -> None:
        manifest_dir = tmp_path / ".raise" / "manifests"
        manifest_dir.mkdir(parents=True)
        (manifest_dir / "skills.json").write_text(
            '{"schema_version": "1.0", "skills": {"x": {"bad": true}}}',
            encoding="utf-8",
        )

        result = load_skill_manifest(tmp_path)
        assert result is None


class TestComputeContentHash:
    """Tests for SHA256 hash computation."""

    def test_deterministic(self) -> None:
        h1 = compute_content_hash("hello world")
        h2 = compute_content_hash("hello world")
        assert h1 == h2

    def test_different_content_different_hash(self) -> None:
        h1 = compute_content_hash("hello")
        h2 = compute_content_hash("world")
        assert h1 != h2

    def test_returns_hex_string(self) -> None:
        h = compute_content_hash("test")
        assert isinstance(h, str)
        assert len(h) == 64  # SHA256 hex digest


class TestClassifySkill:
    """Tests for the dpkg three-hash classification algorithm."""

    def test_all_same_is_current(self) -> None:
        assert classify_skill("aaa", "aaa", "aaa") == SkillSyncAction.CURRENT

    def test_upstream_changed_user_untouched_is_auto_update(self) -> None:
        assert classify_skill("aaa", "aaa", "bbb") == SkillSyncAction.AUTO_UPDATE

    def test_user_changed_upstream_same_is_keep(self) -> None:
        assert classify_skill("aaa", "bbb", "aaa") == SkillSyncAction.KEEP_USER

    def test_both_changed_is_conflict(self) -> None:
        assert classify_skill("aaa", "bbb", "ccc") == SkillSyncAction.CONFLICT

    def test_both_changed_to_same_is_current(self) -> None:
        # User happened to make same change as upstream
        assert classify_skill("aaa", "bbb", "bbb") == SkillSyncAction.CURRENT

    def test_no_distributed_hash_is_legacy(self) -> None:
        assert classify_skill(None, "aaa", "bbb") == SkillSyncAction.LEGACY

    def test_no_distributed_hash_matching_new_is_legacy(self) -> None:
        assert classify_skill(None, "aaa", "aaa") == SkillSyncAction.LEGACY
