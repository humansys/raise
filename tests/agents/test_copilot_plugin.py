"""Tests for CopilotPlugin — frontmatter transformation and .prompt.md generation."""

from __future__ import annotations

from pathlib import Path

from raise_cli.agents.copilot_plugin import CopilotPlugin
from raise_cli.config.agents import BUILTIN_AGENTS


def _copilot_config():
    return BUILTIN_AGENTS["copilot"]


class TestTransformInstructions:
    """CopilotPlugin.transform_instructions — pass-through for now."""

    def test_returns_content_unchanged(self) -> None:
        plugin = CopilotPlugin()
        content = "# Copilot Instructions\nDo things."
        assert plugin.transform_instructions(content, _copilot_config()) == content

    def test_handles_empty_string(self) -> None:
        plugin = CopilotPlugin()
        assert plugin.transform_instructions("", _copilot_config()) == ""


class TestTransformSkill:
    """CopilotPlugin.transform_skill — adds Copilot-specific frontmatter fields."""

    def test_adds_tools_field(self) -> None:
        plugin = CopilotPlugin()
        fm = {"name": "rai-session-start", "description": "Begin session"}
        out_fm, _ = plugin.transform_skill(fm, "body", _copilot_config())
        assert "tools" in out_fm
        assert isinstance(out_fm["tools"], list)
        assert len(out_fm["tools"]) > 0

    def test_adds_infer_field(self) -> None:
        plugin = CopilotPlugin()
        fm = {"name": "rai-session-start"}
        out_fm, _ = plugin.transform_skill(fm, "body", _copilot_config())
        assert out_fm["infer"] is True

    def test_removes_license_field(self) -> None:
        plugin = CopilotPlugin()
        fm = {"name": "test", "license": "MIT"}
        out_fm, _ = plugin.transform_skill(fm, "body", _copilot_config())
        assert "license" not in out_fm

    def test_removes_compatibility_field(self) -> None:
        plugin = CopilotPlugin()
        fm = {"name": "test", "compatibility": ["claude-code"]}
        out_fm, _ = plugin.transform_skill(fm, "body", _copilot_config())
        assert "compatibility" not in out_fm

    def test_preserves_other_fields(self) -> None:
        plugin = CopilotPlugin()
        fm = {"name": "test", "description": "A skill", "version": "1.0"}
        out_fm, _ = plugin.transform_skill(fm, "body", _copilot_config())
        assert out_fm["name"] == "test"
        assert out_fm["description"] == "A skill"
        assert out_fm["version"] == "1.0"

    def test_body_unchanged(self) -> None:
        plugin = CopilotPlugin()
        body = "# Skill content\nDo things here."
        _, out_body = plugin.transform_skill({}, body, _copilot_config())
        assert out_body == body

    def test_does_not_mutate_original_frontmatter(self) -> None:
        plugin = CopilotPlugin()
        fm = {"name": "test", "license": "MIT"}
        plugin.transform_skill(fm, "", _copilot_config())
        assert "license" in fm  # original unchanged


class TestPostInit:
    """CopilotPlugin.post_init — generates .prompt.md files from skills."""

    def test_returns_empty_when_no_skills(self, tmp_path: Path) -> None:
        plugin = CopilotPlugin()
        created = plugin.post_init(tmp_path, _copilot_config())
        assert created == []

    def test_generates_prompt_md_for_each_skill(self, tmp_path: Path) -> None:
        """Creates one .prompt.md per skill in .github/agents/."""
        _scaffold_skills(tmp_path)

        plugin = CopilotPlugin()
        created = plugin.post_init(tmp_path, _copilot_config())

        prompts_dir = tmp_path / ".github" / "prompts"
        assert (prompts_dir / "rai-session-start.prompt.md").exists()
        assert (prompts_dir / "rai-debug.prompt.md").exists()
        assert len(created) == 2

    def test_prompt_file_contains_skill_name(self, tmp_path: Path) -> None:
        _scaffold_skills(tmp_path)
        plugin = CopilotPlugin()
        plugin.post_init(tmp_path, _copilot_config())

        content = (
            tmp_path / ".github" / "prompts" / "rai-session-start.prompt.md"
        ).read_text()
        assert "rai-session-start" in content

    def test_creates_prompts_directory(self, tmp_path: Path) -> None:
        _scaffold_skills(tmp_path)
        plugin = CopilotPlugin()
        plugin.post_init(tmp_path, _copilot_config())
        assert (tmp_path / ".github" / "prompts").is_dir()

    def test_idempotent_second_call(self, tmp_path: Path) -> None:
        """Running post_init twice doesn't raise or duplicate files."""
        _scaffold_skills(tmp_path)
        plugin = CopilotPlugin()
        plugin.post_init(tmp_path, _copilot_config())
        created2 = plugin.post_init(tmp_path, _copilot_config())
        # Second run can overwrite — no crash
        assert isinstance(created2, list)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _scaffold_skills(project_root: Path) -> None:
    """Create minimal .github/agents/ skill structure for testing."""
    agents_dir = project_root / ".github" / "agents"
    for skill_name in ["rai-session-start", "rai-debug"]:
        skill_dir = agents_dir / skill_name
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(
            f"---\nname: {skill_name}\ndescription: Test skill\n---\n# {skill_name}\n"
        )
