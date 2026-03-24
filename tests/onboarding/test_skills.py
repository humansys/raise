"""Tests for the skills scaffolding module — copies bundled skills to project."""

from __future__ import annotations

from pathlib import Path

from raise_cli.config.agents import get_agent_config
from raise_cli.onboarding.skills import SkillScaffoldResult, scaffold_skills
from raise_cli.skills_base import DISTRIBUTABLE_SKILLS

TOTAL_SKILLS = len(DISTRIBUTABLE_SKILLS)

# Extra files beyond SKILL.md (templates/, references/, _references/)
EXTRA_SKILL_FILES = 9  # epic-close:1, epic-design:2, epic-plan:2, epic-start:1, research:1, story-design:1, story-start:1


class TestScaffoldSkills:
    """Tests for scaffold_skills() function."""

    def test_copies_all_skills(self, tmp_path: Path) -> None:
        """Should copy all distributable skills to .claude/skills/."""
        result = scaffold_skills(tmp_path)

        skills_dir = tmp_path / ".claude" / "skills"
        for skill_name in DISTRIBUTABLE_SKILLS:
            assert (skills_dir / skill_name / "SKILL.md").exists(), (
                f"Missing: {skill_name}"
            )
        assert result.skills_copied == TOTAL_SKILLS

    def test_copies_reference_files(self, tmp_path: Path) -> None:
        """Skills with reference subdirectories should have them copied."""
        scaffold_skills(tmp_path)

        skills_dir = tmp_path / ".claude" / "skills"
        assert (
            skills_dir / "rai-epic-plan" / "_references" / "sequencing-strategies.md"
        ).exists()
        assert (
            skills_dir / "rai-research" / "references" / "research-prompt-template.md"
        ).exists()
        assert (
            skills_dir / "rai-story-design" / "references" / "tech-design-story-v2.md"
        ).exists()

    def test_skill_content_has_frontmatter(self, tmp_path: Path) -> None:
        """Copied skills should have YAML frontmatter."""
        scaffold_skills(tmp_path)

        skill_path = tmp_path / ".claude" / "skills" / "rai-session-start" / "SKILL.md"
        content = skill_path.read_text(encoding="utf-8")
        assert content.startswith("---\n") or content.startswith("#")

    def test_skill_content_matches_bundled(self, tmp_path: Path) -> None:
        """Copied skill files should match bundled originals."""
        from importlib.resources import files

        scaffold_skills(tmp_path)

        base = files("raise_cli.skills_base")
        original = (base / "rai-session-start" / "SKILL.md").read_text(encoding="utf-8")
        copied = (
            tmp_path / ".claude" / "skills" / "rai-session-start" / "SKILL.md"
        ).read_text(encoding="utf-8")
        assert copied == original

    def test_returns_skill_names(self, tmp_path: Path) -> None:
        """Should return names of copied skills."""
        result = scaffold_skills(tmp_path)

        assert "rai-session-start" in result.skills_installed
        assert "rai-discover" in result.skills_installed
        assert "rai-story-implement" in result.skills_installed
        assert "rai-epic-design" in result.skills_installed
        assert "rai-debug" in result.skills_installed
        assert len(result.skills_installed) == TOTAL_SKILLS

    def test_reports_files_copied(self, tmp_path: Path) -> None:
        """Should list all copied files in result."""
        result = scaffold_skills(tmp_path)

        # N skills × 1 SKILL.md + extra files (templates, references)
        expected_files = TOTAL_SKILLS + EXTRA_SKILL_FILES
        assert len(result.files_copied) == expected_files
        assert len(result.files_skipped) == 0
        assert not result.already_existed


class TestScaffoldSkillsIdempotency:
    """Tests for skills scaffolding being safe to run multiple times."""

    def test_does_not_overwrite_existing_skills(self, tmp_path: Path) -> None:
        """Should not overwrite existing skill files."""
        # First scaffold
        scaffold_skills(tmp_path)

        # Modify a skill
        skill_path = tmp_path / ".claude" / "skills" / "rai-session-start" / "SKILL.md"
        skill_path.write_text("# Custom skill")

        # Second scaffold
        result = scaffold_skills(tmp_path)

        assert skill_path.read_text(encoding="utf-8") == "# Custom skill"
        assert "rai-session-start" in result.skills_skipped_names

    def test_second_run_reports_already_existed(self, tmp_path: Path) -> None:
        """Second scaffold should report already_existed=True."""
        scaffold_skills(tmp_path)
        result = scaffold_skills(tmp_path)

        assert result.already_existed
        assert len(result.skills_current) == TOTAL_SKILLS
        assert len(result.files_copied) == 0
        assert result.skills_copied == 0

    def test_copies_only_missing_skills(self, tmp_path: Path) -> None:
        """Should copy missing skills when some already exist."""
        # Create one skill manually
        skill_dir = tmp_path / ".claude" / "skills" / "rai-session-start"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Existing")

        result = scaffold_skills(tmp_path)

        # session-start should be skipped
        assert "rai-session-start" in result.skills_skipped_names
        # Others should be copied
        assert result.skills_copied == TOTAL_SKILLS - 1
        assert (tmp_path / ".claude" / "skills" / "rai-discover" / "SKILL.md").exists()
        assert (
            tmp_path / ".claude" / "skills" / "rai-story-implement" / "SKILL.md"
        ).exists()


class TestScaffoldSkillsIdeConfig:
    """Tests for scaffold_skills() with IDE configuration."""

    def test_scaffold_to_antigravity_dir(self, tmp_path: Path) -> None:
        """Should scaffold skills to .agent/skills/ with antigravity config."""
        config = get_agent_config("antigravity")
        result = scaffold_skills(tmp_path, agent_config=config)

        agent_skills = tmp_path / ".agent" / "skills"
        for skill_name in DISTRIBUTABLE_SKILLS:
            assert (agent_skills / skill_name / "SKILL.md").exists(), (
                f"Missing: {skill_name}"
            )
        assert result.skills_copied == TOTAL_SKILLS
        # .claude/skills/ should NOT exist
        assert not (tmp_path / ".claude" / "skills").exists()

    def test_scaffold_default_is_claude(self, tmp_path: Path) -> None:
        """Default scaffold (no ide_config) still goes to .claude/skills/."""
        result = scaffold_skills(tmp_path)

        assert (tmp_path / ".claude" / "skills").exists()
        assert result.skills_copied == TOTAL_SKILLS


class TestScaffoldSkillsPartialState:
    """Tests for scaffold when .claude/ is partially populated."""

    def test_handles_existing_claude_dir(self, tmp_path: Path) -> None:
        """Should work when .claude/ exists but skills/ doesn't."""
        (tmp_path / ".claude").mkdir()

        result = scaffold_skills(tmp_path)

        assert result.skills_copied == TOTAL_SKILLS

    def test_handles_existing_skills_dir(self, tmp_path: Path) -> None:
        """Should work when .claude/skills/ exists but is empty."""
        (tmp_path / ".claude" / "skills").mkdir(parents=True)

        result = scaffold_skills(tmp_path)

        assert result.skills_copied == TOTAL_SKILLS


class TestSkillSyncUpgrade:
    """Tests for version-aware skill sync (dpkg three-hash algorithm)."""

    def test_first_run_writes_manifest(self, tmp_path: Path) -> None:
        """First scaffold should create .raise/manifests/skills.json."""
        scaffold_skills(tmp_path)

        manifest_path = tmp_path / ".raise" / "manifests" / "skills.json"
        assert manifest_path.exists()

    def test_first_run_records_all_skills_in_manifest(self, tmp_path: Path) -> None:
        """Manifest should contain entries for all distributed skills."""
        import json

        scaffold_skills(tmp_path)

        manifest_path = tmp_path / ".raise" / "manifests" / "skills.json"
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        for skill_name in DISTRIBUTABLE_SKILLS:
            assert skill_name in data["skills"], f"Missing manifest entry: {skill_name}"

    def test_auto_updates_untouched_skill(self, tmp_path: Path) -> None:
        """Skill not modified by user should be auto-updated when upstream changes."""
        import json

        scaffold_skills(tmp_path)

        # Simulate upstream change: modify the manifest hash to differ from new
        manifest_path = tmp_path / ".raise" / "manifests" / "skills.json"
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        skill_name = "rai-debug"
        skill_md = tmp_path / ".claude" / "skills" / skill_name / "SKILL.md"
        current_content = skill_md.read_text(encoding="utf-8")

        # Set distributed hash to a fake old hash (simulating old version was different)
        # But on-disk still matches distributed (user didn't touch it)
        fake_old_hash = "0" * 64
        data["skills"][skill_name]["sha256"] = fake_old_hash
        manifest_path.write_text(json.dumps(data), encoding="utf-8")

        # Also write the fake old content to disk so on-disk == distributed
        skill_md.write_text("old content from previous version", encoding="utf-8")
        data["skills"][skill_name]["sha256"] = (
            __import__("hashlib")
            .sha256(b"old content from previous version")
            .hexdigest()
        )
        manifest_path.write_text(json.dumps(data), encoding="utf-8")

        # Re-run scaffold — should auto-update since user didn't customize
        result = scaffold_skills(tmp_path)

        assert skill_name in result.skills_updated
        # File should now match bundled content again
        updated_content = skill_md.read_text(encoding="utf-8")
        assert updated_content == current_content

    def test_keeps_customized_skill(self, tmp_path: Path) -> None:
        """Customized skill should not be overwritten when upstream hasn't changed."""
        scaffold_skills(tmp_path)

        # User customizes a skill
        skill_md = tmp_path / ".claude" / "skills" / "rai-debug" / "SKILL.md"
        skill_md.write_text("# My custom debug skill", encoding="utf-8")

        scaffold_skills(tmp_path)

        # Should be classified as current (upstream didn't change)
        assert skill_md.read_text(encoding="utf-8") == "# My custom debug skill"

    def test_conflict_defaults_to_keep(self, tmp_path: Path) -> None:
        """When both sides changed, default is keep user's version."""
        import json

        scaffold_skills(tmp_path)

        skill_name = "rai-debug"
        skill_md = tmp_path / ".claude" / "skills" / skill_name / "SKILL.md"

        # Simulate: user modified AND upstream changed
        # Set distributed hash to something different from both on-disk and new
        manifest_path = tmp_path / ".raise" / "manifests" / "skills.json"
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        data["skills"][skill_name]["sha256"] = "a" * 64
        manifest_path.write_text(json.dumps(data), encoding="utf-8")

        # User's customized content
        skill_md.write_text("# User customized version", encoding="utf-8")

        result = scaffold_skills(tmp_path)

        # In non-TTY (test env), prompt returns KEEP → goes to skills_kept
        assert skill_name in result.skills_kept
        assert skill_md.read_text(encoding="utf-8") == "# User customized version"

    def test_force_overwrites_conflicts(self, tmp_path: Path) -> None:
        """--force should overwrite even conflicted skills."""
        import json

        scaffold_skills(tmp_path)

        skill_name = "rai-debug"
        skill_md = tmp_path / ".claude" / "skills" / skill_name / "SKILL.md"

        # Create conflict scenario
        manifest_path = tmp_path / ".raise" / "manifests" / "skills.json"
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        data["skills"][skill_name]["sha256"] = "a" * 64
        manifest_path.write_text(json.dumps(data), encoding="utf-8")
        skill_md.write_text("# User version", encoding="utf-8")

        result = scaffold_skills(tmp_path, force=True)

        assert skill_name in result.skills_overwritten
        assert skill_md.read_text(encoding="utf-8") != "# User version"

    def test_skip_updates_keeps_all(self, tmp_path: Path) -> None:
        """--skip-updates should keep all existing files."""
        import json

        scaffold_skills(tmp_path)

        skill_name = "rai-debug"
        skill_md = tmp_path / ".claude" / "skills" / skill_name / "SKILL.md"

        # Simulate upstream change with untouched file
        manifest_path = tmp_path / ".raise" / "manifests" / "skills.json"
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        data["skills"][skill_name]["sha256"] = "b" * 64
        manifest_path.write_text(json.dumps(data), encoding="utf-8")

        # Write content matching the fake old hash
        skill_md.write_text("old version content", encoding="utf-8")
        data["skills"][skill_name]["sha256"] = (
            __import__("hashlib").sha256(b"old version content").hexdigest()
        )
        manifest_path.write_text(json.dumps(data), encoding="utf-8")

        result = scaffold_skills(tmp_path, skip_updates=True)

        # Should not update even though upstream changed
        assert skill_name not in result.skills_updated

    def test_dry_run_does_not_write(self, tmp_path: Path) -> None:
        """--dry-run should not write any files."""
        # Fresh project — dry run should report what it would do
        result = scaffold_skills(tmp_path, dry_run=True)

        assert len(result.skills_installed) == TOTAL_SKILLS
        # But no manifest should exist
        assert not (tmp_path / ".raise" / "manifests" / "skills.json").exists()
        # And no skill files should exist
        assert not (tmp_path / ".claude" / "skills").exists()

    def test_legacy_project_no_manifest(self, tmp_path: Path) -> None:
        """Project with existing skills but no manifest should be handled."""
        # Create a skill without using scaffold (simulating legacy project)
        skill_dir = tmp_path / ".claude" / "skills" / "rai-debug"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Legacy skill", encoding="utf-8")

        result = scaffold_skills(tmp_path)

        # rai-debug should be treated as legacy (current, recorded in manifest)
        assert "rai-debug" in result.skills_current
        # Manifest should now exist
        assert (tmp_path / ".raise" / "manifests" / "skills.json").exists()

    def test_new_skill_added_in_upgrade(self, tmp_path: Path) -> None:
        """Skills added in newer raise-cli should be installed on upgrade."""
        scaffold_skills(tmp_path)

        # Remove one skill to simulate it being new in next version
        import json
        import shutil

        skill_name = "rai-debug"
        skill_dir = tmp_path / ".claude" / "skills" / skill_name
        shutil.rmtree(skill_dir)

        manifest_path = tmp_path / ".raise" / "manifests" / "skills.json"
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        del data["skills"][skill_name]
        manifest_path.write_text(json.dumps(data), encoding="utf-8")

        # Re-run — should install the "new" skill
        result = scaffold_skills(tmp_path)

        assert skill_name in result.skills_installed
        assert (skill_dir / "SKILL.md").exists()


class TestSkillSetOverlay:
    """Tests for --skill-set overlay deployment (S340.1)."""

    def _create_overlay(
        self, project: Path, set_name: str, skills: dict[str, str]
    ) -> None:
        """Helper: create .raise/skills/{set}/{name}/SKILL.md files."""
        for name, content in skills.items():
            skill_dir = project / ".raise" / "skills" / set_name / name
            skill_dir.mkdir(parents=True, exist_ok=True)
            (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")

    def test_overlay_adds_new_skill(self, tmp_path: Path) -> None:
        """Overlay skill not in builtins should be added to deployment."""
        self._create_overlay(
            tmp_path,
            "my-team",
            {
                "team-review": "# Team Review Skill",
            },
        )

        scaffold_skills(tmp_path, skill_set="my-team")

        deployed = tmp_path / ".claude" / "skills" / "team-review" / "SKILL.md"
        assert deployed.exists()
        assert deployed.read_text(encoding="utf-8") == "# Team Review Skill"

    def test_overlay_overrides_builtin(self, tmp_path: Path) -> None:
        """Overlay skill with same name as builtin should replace it."""
        custom_content = "# Custom Debug Skill\n\nMy team's version."
        self._create_overlay(
            tmp_path,
            "my-team",
            {
                "rai-debug": custom_content,
            },
        )

        scaffold_skills(tmp_path, skill_set="my-team")

        deployed = tmp_path / ".claude" / "skills" / "rai-debug" / "SKILL.md"
        assert deployed.read_text(encoding="utf-8") == custom_content

    def test_overlay_marks_origin_project(self, tmp_path: Path) -> None:
        """Overlay skills should have origin='project' in manifest."""
        import json

        self._create_overlay(
            tmp_path,
            "my-team",
            {
                "team-review": "# Team Review",
            },
        )

        scaffold_skills(tmp_path, skill_set="my-team")

        manifest_path = tmp_path / ".raise" / "manifests" / "skills.json"
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert data["skills"]["team-review"]["origin"] == "project"

    def test_no_skill_set_works_as_before(self, tmp_path: Path) -> None:
        """Without --skill-set, behavior is unchanged."""
        result = scaffold_skills(tmp_path)

        assert result.skills_copied == TOTAL_SKILLS
        assert (tmp_path / ".claude" / "skills" / "rai-debug" / "SKILL.md").exists()

    def test_nonexistent_skill_set_warns(self, tmp_path: Path) -> None:
        """Nonexistent skill set directory should not crash."""
        result = scaffold_skills(tmp_path, skill_set="does-not-exist")

        # Builtins should still be deployed
        assert result.skills_copied == TOTAL_SKILLS

    def test_manifest_records_skill_set(self, tmp_path: Path) -> None:
        """Manifest should record which skill set was deployed."""
        import json

        self._create_overlay(
            tmp_path,
            "my-team",
            {
                "team-review": "# Team Review",
            },
        )

        scaffold_skills(tmp_path, skill_set="my-team")

        manifest_path = tmp_path / ".raise" / "manifests" / "skills.json"
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert data["skill_set"] == "my-team"

    def test_overlay_copies_subdirectories(self, tmp_path: Path) -> None:
        """Overlay skills with subdirs (templates/, references/) should copy them."""
        overlay_dir = tmp_path / ".raise" / "skills" / "my-team" / "team-review"
        overlay_dir.mkdir(parents=True)
        (overlay_dir / "SKILL.md").write_text("# Team Review", encoding="utf-8")
        refs_dir = overlay_dir / "references"
        refs_dir.mkdir()
        (refs_dir / "guide.md").write_text("# Guide", encoding="utf-8")

        scaffold_skills(tmp_path, skill_set="my-team")

        deployed_ref = (
            tmp_path / ".claude" / "skills" / "team-review" / "references" / "guide.md"
        )
        assert deployed_ref.exists()
        assert deployed_ref.read_text(encoding="utf-8") == "# Guide"


class TestCopySkillTreePath:
    """Tests for copy_skill_tree accepting Path source (AR R1)."""

    def test_copy_from_path_source(self, tmp_path: Path) -> None:
        """copy_skill_tree should work with Path source, not just Traversable."""
        from raise_cli.onboarding.skills import copy_skill_tree

        source = tmp_path / "source" / "my-skill"
        source.mkdir(parents=True)
        (source / "SKILL.md").write_text("# Test Skill", encoding="utf-8")

        dest = tmp_path / "dest" / "my-skill"
        result = SkillScaffoldResult()

        copied = copy_skill_tree(source, dest, result, overwrite=True)

        assert copied == 1
        assert (dest / "SKILL.md").read_text(encoding="utf-8") == "# Test Skill"


class TestSkillScaffoldResult:
    """Tests for SkillScaffoldResult model."""

    def test_default_values(self) -> None:
        """Should have sensible defaults."""
        result = SkillScaffoldResult()

        assert result.skills_copied == 0
        assert not result.already_existed
        assert result.files_copied == []
        assert result.files_skipped == []
        assert result.skills_installed == []
        assert result.skills_skipped_names == []
