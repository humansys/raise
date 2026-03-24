"""Tests for skill set management (S340.4)."""

from __future__ import annotations

from pathlib import Path

from raise_cli.skills.skillsets import (
    create_skill_set,
    diff_skill_set,
    list_skill_sets,
)


class TestCreateSkillSet:
    """Tests for create_skill_set()."""

    def test_create_from_builtins(self, tmp_path: Path) -> None:
        """Should copy all builtins to .raise/skills/<name>/."""
        from raise_cli.skills_base import DISTRIBUTABLE_SKILLS

        result = create_skill_set("my-team", tmp_path)

        assert result.created
        set_dir = tmp_path / ".raise" / "skills" / "my-team"
        assert set_dir.is_dir()
        for skill_name in DISTRIBUTABLE_SKILLS:
            assert (set_dir / skill_name / "SKILL.md").exists(), (
                f"Missing: {skill_name}"
            )

    def test_create_empty(self, tmp_path: Path) -> None:
        """--empty should create directory only."""
        result = create_skill_set("my-team", tmp_path, empty=True)

        assert result.created
        set_dir = tmp_path / ".raise" / "skills" / "my-team"
        assert set_dir.is_dir()
        # No skills inside
        assert list(set_dir.iterdir()) == []

    def test_create_fails_if_exists(self, tmp_path: Path) -> None:
        """Should fail if set already exists."""
        (tmp_path / ".raise" / "skills" / "my-team").mkdir(parents=True)

        result = create_skill_set("my-team", tmp_path)

        assert not result.created
        assert "exists" in (result.error or "").lower()


class TestListSkillSets:
    """Tests for list_skill_sets()."""

    def test_list_empty(self, tmp_path: Path) -> None:
        """No sets → empty list."""
        result = list_skill_sets(tmp_path)
        assert result == []

    def test_list_with_sets(self, tmp_path: Path) -> None:
        """Should return info for each set."""
        # Create two sets with skills
        for name in ("team-a", "team-b"):
            skill_dir = tmp_path / ".raise" / "skills" / name / "my-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("# Test", encoding="utf-8")

        result = list_skill_sets(tmp_path)

        assert len(result) == 2
        names = [s.name for s in result]
        assert "team-a" in names
        assert "team-b" in names
        assert all(s.skill_count == 1 for s in result)

    def test_list_ignores_empty_dirs(self, tmp_path: Path) -> None:
        """Directories without SKILL.md inside should still appear with count 0."""
        (tmp_path / ".raise" / "skills" / "empty-set").mkdir(parents=True)

        result = list_skill_sets(tmp_path)

        assert len(result) == 1
        assert result[0].skill_count == 0


class TestDiffSkillSet:
    """Tests for diff_skill_set()."""

    def test_diff_unmodified(self, tmp_path: Path) -> None:
        """Set created from builtins should show all unchanged."""
        create_skill_set("my-team", tmp_path)

        diff = diff_skill_set("my-team", tmp_path)

        assert len(diff.unchanged) > 0
        assert len(diff.modified) == 0
        assert len(diff.added) == 0

    def test_diff_modified(self, tmp_path: Path) -> None:
        """Modified skill should show in modified list."""
        create_skill_set("my-team", tmp_path)

        # Modify one skill
        skill_md = tmp_path / ".raise" / "skills" / "my-team" / "rai-debug" / "SKILL.md"
        skill_md.write_text("# Custom Debug", encoding="utf-8")

        diff = diff_skill_set("my-team", tmp_path)

        assert "rai-debug" in diff.modified

    def test_diff_added(self, tmp_path: Path) -> None:
        """New skill not in builtins should show in added list."""
        create_skill_set("my-team", tmp_path)

        # Add a team-specific skill
        new_skill = tmp_path / ".raise" / "skills" / "my-team" / "team-review"
        new_skill.mkdir()
        (new_skill / "SKILL.md").write_text("# Team Review", encoding="utf-8")

        diff = diff_skill_set("my-team", tmp_path)

        assert "team-review" in diff.added

    def test_diff_nonexistent_set(self, tmp_path: Path) -> None:
        """Nonexistent set should return None."""
        diff = diff_skill_set("does-not-exist", tmp_path)

        assert diff is None
