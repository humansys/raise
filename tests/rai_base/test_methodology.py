"""Tests for methodology.yaml framework definition.

Tests verify that:
1. File is accessible via importlib.resources
2. Valid YAML structure
3. Required sections present
4. Skills, gates, and principles defined
"""

from __future__ import annotations

from importlib.resources import files

import pytest
import yaml


class TestMethodologyPackage:
    """Tests for methodology file accessibility."""

    def test_framework_directory_accessible(self) -> None:
        """Framework directory is accessible via importlib.resources."""
        base = files("raise_cli.rai_base")
        framework = base / "framework"
        assert framework.is_dir()

    def test_methodology_yaml_exists(self) -> None:
        """methodology.yaml file exists and is readable."""
        base = files("raise_cli.rai_base")
        methodology_file = base / "framework" / "methodology.yaml"
        content = methodology_file.read_text(encoding="utf-8")
        assert len(content) > 0


class TestMethodologyValidity:
    """Tests for YAML validity and structure."""

    @pytest.fixture
    def methodology(self) -> dict:
        """Load and parse methodology.yaml."""
        base = files("raise_cli.rai_base")
        content = (base / "framework" / "methodology.yaml").read_text(encoding="utf-8")
        return yaml.safe_load(content)

    def test_valid_yaml(self, methodology: dict) -> None:
        """File parses as valid YAML."""
        assert isinstance(methodology, dict)

    def test_has_version(self, methodology: dict) -> None:
        """Has version field."""
        assert "version" in methodology
        assert methodology["version"] == 1

    def test_has_required_sections(self, methodology: dict) -> None:
        """Has all required top-level sections."""
        required = {"version", "lifecycle", "skills", "gates", "principles", "branches"}
        missing = required - set(methodology.keys())
        assert not missing, f"Missing sections: {missing}"


class TestMethodologySkills:
    """Tests for skills section."""

    @pytest.fixture
    def skills(self) -> dict:
        """Load skills section."""
        base = files("raise_cli.rai_base")
        content = (base / "framework" / "methodology.yaml").read_text(encoding="utf-8")
        methodology = yaml.safe_load(content)
        return methodology["skills"]

    def test_has_skill_categories(self, skills: dict) -> None:
        """Has expected skill categories."""
        expected = {"session", "epic", "story", "discovery", "meta", "other"}
        assert expected.issubset(set(skills.keys()))

    def test_session_skills_present(self, skills: dict) -> None:
        """Session skills are defined."""
        session_skills = skills["session"]
        names = [s["name"] for s in session_skills]
        assert "/rai-session-start" in names
        assert "/rai-session-close" in names

    def test_epic_skills_present(self, skills: dict) -> None:
        """Epic skills are defined."""
        epic_skills = skills["epic"]
        names = [s["name"] for s in epic_skills]
        assert "/rai-epic-start" in names
        assert "/rai-epic-design" in names
        assert "/rai-epic-plan" in names
        assert "/rai-epic-close" in names

    def test_story_skills_present(self, skills: dict) -> None:
        """Story skills are defined."""
        feature_skills = skills["story"]
        names = [s["name"] for s in feature_skills]
        assert "/rai-story-start" in names
        assert "/rai-story-plan" in names
        assert "/rai-story-implement" in names
        assert "/rai-story-review" in names
        assert "/rai-story-close" in names

    def test_skills_have_required_fields(self, skills: dict) -> None:
        """All skills have name, purpose, when fields."""
        for category, skill_list in skills.items():
            for skill in skill_list:
                assert "name" in skill, f"Skill in {category} missing name"
                assert "purpose" in skill, f"Skill {skill.get('name')} missing purpose"
                assert "when" in skill, f"Skill {skill.get('name')} missing when"

    def test_skill_count(self, skills: dict) -> None:
        """Has reasonable number of skills (15+)."""
        total = sum(len(skill_list) for skill_list in skills.values())
        assert total >= 15, f"Expected 15+ skills, got {total}"


class TestMethodologyGates:
    """Tests for gates section."""

    @pytest.fixture
    def gates(self) -> dict:
        """Load gates section."""
        base = files("raise_cli.rai_base")
        content = (base / "framework" / "methodology.yaml").read_text(encoding="utf-8")
        methodology = yaml.safe_load(content)
        return methodology["gates"]

    def test_has_blocking_gates(self, gates: dict) -> None:
        """Has blocking gates defined."""
        assert "blocking" in gates
        assert len(gates["blocking"]) >= 4

    def test_has_quality_gates(self, gates: dict) -> None:
        """Has quality gates defined."""
        assert "quality" in gates
        assert len(gates["quality"]) >= 2

    def test_blocking_gates_have_required_fields(self, gates: dict) -> None:
        """Blocking gates have before, require, rationale."""
        for gate in gates["blocking"]:
            assert "before" in gate, f"Gate missing 'before': {gate}"
            assert "require" in gate, f"Gate missing 'require': {gate}"
            assert "rationale" in gate, f"Gate missing 'rationale': {gate}"

    def test_epic_branch_gate_exists(self, gates: dict) -> None:
        """Epic branch poka-yoke gate exists."""
        befores = [g["before"].lower() for g in gates["blocking"]]
        assert any("epic" in b for b in befores)

    def test_story_branch_gate_exists(self, gates: dict) -> None:
        """Story branch gate exists."""
        befores = [g["before"].lower() for g in gates["blocking"]]
        assert any("story" in b for b in befores)


class TestMethodologyPrinciples:
    """Tests for principles section."""

    @pytest.fixture
    def principles(self) -> dict:
        """Load principles section."""
        base = files("raise_cli.rai_base")
        content = (base / "framework" / "methodology.yaml").read_text(encoding="utf-8")
        methodology = yaml.safe_load(content)
        return methodology["principles"]

    def test_has_principle_categories(self, principles: dict) -> None:
        """Has expected principle categories."""
        expected = {"process", "collaboration", "technical"}
        assert expected.issubset(set(principles.keys()))

    def test_tdd_principle_exists(self, principles: dict) -> None:
        """TDD principle is defined."""
        process_names = [p["name"] for p in principles["process"]]
        assert any("TDD" in name for name in process_names)

    def test_principles_have_required_fields(self, principles: dict) -> None:
        """All principles have name, rule, rationale."""
        for category, principle_list in principles.items():
            for principle in principle_list:
                assert "name" in principle, f"Principle in {category} missing name"
                assert "rule" in principle, (
                    f"Principle {principle.get('name')} missing rule"
                )
                assert "rationale" in principle, (
                    f"Principle {principle.get('name')} missing rationale"
                )


class TestMethodologyLifecycle:
    """Tests for lifecycle section."""

    @pytest.fixture
    def lifecycle(self) -> dict:
        """Load lifecycle section."""
        base = files("raise_cli.rai_base")
        content = (base / "framework" / "methodology.yaml").read_text(encoding="utf-8")
        methodology = yaml.safe_load(content)
        return methodology["lifecycle"]

    def test_has_lifecycle_levels(self, lifecycle: dict) -> None:
        """Has epic, story, session lifecycles."""
        assert "epic" in lifecycle
        assert "story" in lifecycle
        assert "session" in lifecycle

    def test_lifecycles_have_flow(self, lifecycle: dict) -> None:
        """All lifecycles define flow."""
        for level, data in lifecycle.items():
            assert "flow" in data, f"{level} lifecycle missing flow"
            assert "phases" in data, f"{level} lifecycle missing phases"
