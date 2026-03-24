"""Tests for agent configuration model and factory."""

from __future__ import annotations

import pytest

from raise_cli.config.agents import (
    BUILTIN_AGENTS,
    AgentChoice,
    AgentConfig,
    BuiltinAgentType,
    get_agent_config,
)


class TestAgentConfig:
    """Tests for AgentConfig model."""

    def test_claude_config_fields(self) -> None:
        """Claude config has correct paths."""
        config = AgentConfig(
            name="Claude Code",
            agent_type="claude",
            skills_dir=".claude/skills",
            instructions_file="CLAUDE.md",
        )
        assert config.agent_type == "claude"
        assert config.name == "Claude Code"
        assert config.skills_dir == ".claude/skills"
        assert config.instructions_file == "CLAUDE.md"
        assert config.workflows_dir is None
        assert config.detection_markers == []
        assert config.plugin is None

    def test_antigravity_config_fields(self) -> None:
        """Antigravity config has correct paths including workflows."""
        config = AgentConfig(
            name="Antigravity",
            agent_type="antigravity",
            skills_dir=".agent/skills",
            instructions_file=".agent/rules/raise.md",
            workflows_dir=".agent/workflows",
        )
        assert config.agent_type == "antigravity"
        assert config.skills_dir == ".agent/skills"
        assert config.instructions_file == ".agent/rules/raise.md"
        assert config.workflows_dir == ".agent/workflows"

    def test_copilot_config_with_plugin(self) -> None:
        """Copilot config has a plugin reference."""
        config = AgentConfig(
            name="GitHub Copilot",
            agent_type="copilot",
            skills_dir=".github/agents",
            instructions_file=".github/copilot-instructions.md",
            workflows_dir=".github/prompts",
            detection_markers=[".github/copilot-instructions.md"],
            plugin="raise_cli.agents.copilot_plugin",
        )
        assert config.plugin == "raise_cli.agents.copilot_plugin"
        assert config.detection_markers == [".github/copilot-instructions.md"]

    def test_skills_dir_can_be_none(self) -> None:
        """skills_dir can be None for agents without skill support."""
        config = AgentConfig(
            name="Minimal Agent",
            agent_type="minimal",
            instructions_file="MINIMAL.md",
            skills_dir=None,
        )
        assert config.skills_dir is None

    def test_workflows_dir_defaults_to_none(self) -> None:
        """workflows_dir defaults to None when not provided."""
        config = AgentConfig(
            name="Claude Code",
            agent_type="claude",
            skills_dir=".claude/skills",
            instructions_file="CLAUDE.md",
        )
        assert config.workflows_dir is None

    def test_frozen_immutability(self) -> None:
        """AgentConfig is frozen — cannot mutate after creation."""
        config = AgentConfig(
            name="Claude Code",
            agent_type="claude",
            skills_dir=".claude/skills",
            instructions_file="CLAUDE.md",
        )
        with pytest.raises(Exception):  # noqa: B017
            config.skills_dir = ".other/skills"  # type: ignore[misc]

    def test_detection_markers_default_empty(self) -> None:
        """detection_markers defaults to empty list."""
        config = AgentConfig(
            name="Test",
            agent_type="test",
            skills_dir=None,
            instructions_file="TEST.md",
        )
        assert config.detection_markers == []


class TestBuiltinAgents:
    """Tests for BUILTIN_AGENTS registry."""

    def test_six_builtin_agents(self) -> None:
        """Registry contains exactly 6 built-in agents."""
        expected: set[BuiltinAgentType] = {
            "claude",
            "cursor",
            "windsurf",
            "copilot",
            "antigravity",
            "roo",
        }
        assert set(BUILTIN_AGENTS.keys()) == expected

    def test_claude_registry_values(self) -> None:
        """Claude registry entry has correct values."""
        config = BUILTIN_AGENTS["claude"]
        assert config.name == "Claude Code"
        assert config.agent_type == "claude"
        assert config.skills_dir == ".claude/skills"
        assert config.instructions_file == "CLAUDE.md"
        assert config.workflows_dir is None
        assert config.detection_markers == ["CLAUDE.md", ".claude"]
        assert config.plugin is None

    def test_cursor_registry_values(self) -> None:
        """Cursor registry entry has correct values."""
        config = BUILTIN_AGENTS["cursor"]
        assert config.name == "Cursor"
        assert config.agent_type == "cursor"
        assert config.skills_dir == ".cursor/skills"
        assert config.instructions_file == ".cursor/rules/raise.mdc"
        assert config.detection_markers == [".cursor/rules", ".cursor"]

    def test_windsurf_registry_values(self) -> None:
        """Windsurf registry entry has correct values."""
        config = BUILTIN_AGENTS["windsurf"]
        assert config.name == "Windsurf"
        assert config.agent_type == "windsurf"
        assert config.skills_dir == ".windsurf/skills"
        assert config.instructions_file == ".windsurf/rules/raise.md"
        assert config.workflows_dir == ".windsurf/workflows"
        assert config.detection_markers == [".windsurf/rules", ".windsurf"]

    def test_copilot_registry_values(self) -> None:
        """Copilot registry entry has plugin reference."""
        config = BUILTIN_AGENTS["copilot"]
        assert config.name == "GitHub Copilot"
        assert config.agent_type == "copilot"
        assert config.skills_dir == ".github/agents"
        assert config.instructions_file == ".github/copilot-instructions.md"
        assert config.workflows_dir == ".github/prompts"
        assert config.detection_markers == [".github/copilot-instructions.md"]
        assert config.plugin == "raise_cli.agents.copilot_plugin"

    def test_antigravity_registry_values(self) -> None:
        """Antigravity registry entry has correct values."""
        config = BUILTIN_AGENTS["antigravity"]
        assert config.name == "Antigravity"
        assert config.agent_type == "antigravity"
        assert config.skills_dir == ".agent/skills"
        assert config.instructions_file == ".agent/rules/raise.md"
        assert config.workflows_dir == ".agent/workflows"
        assert config.detection_markers == [".agent/rules", ".agent"]

    def test_roo_registry_values(self) -> None:
        """Roo Code registry entry has correct values."""
        config = BUILTIN_AGENTS["roo"]
        assert config.name == "Roo Code"
        assert config.agent_type == "roo"
        assert config.skills_dir == ".roo/skills"
        assert config.instructions_file == ".roo/rules/raise.md"
        assert config.workflows_dir is None
        assert ".roo/rules" in config.detection_markers
        assert ".roo" in config.detection_markers
        assert ".rooignore" in config.detection_markers
        assert config.plugin is None

    def test_all_agents_have_skills_dir(self) -> None:
        """All 6 built-in agents have skills_dir set."""
        for agent_type, config in BUILTIN_AGENTS.items():
            assert config.skills_dir is not None, f"{agent_type} missing skills_dir"


class TestAgentChoice:
    """Tests for AgentChoice enum."""

    def test_all_builtin_types_in_enum(self) -> None:
        """AgentChoice has all 6 built-in types."""
        assert AgentChoice.claude.value == "claude"
        assert AgentChoice.cursor.value == "cursor"
        assert AgentChoice.windsurf.value == "windsurf"
        assert AgentChoice.copilot.value == "copilot"
        assert AgentChoice.antigravity.value == "antigravity"
        assert AgentChoice.roo.value == "roo"


class TestGetAgentConfig:
    """Tests for get_agent_config factory function."""

    def test_returns_claude_config(self) -> None:
        """Factory returns correct config for claude."""
        config = get_agent_config("claude")
        assert config.agent_type == "claude"
        assert config.skills_dir == ".claude/skills"

    def test_returns_cursor_config(self) -> None:
        """Factory returns correct config for cursor."""
        config = get_agent_config("cursor")
        assert config.agent_type == "cursor"

    def test_returns_antigravity_config(self) -> None:
        """Factory returns correct config for antigravity."""
        config = get_agent_config("antigravity")
        assert config.agent_type == "antigravity"

    def test_defaults_to_claude(self) -> None:
        """Factory defaults to claude when called with no args."""
        config = get_agent_config()
        assert config.agent_type == "claude"

    def test_returns_same_instance_from_registry(self) -> None:
        """Factory returns the registry instance (not a copy)."""
        config = get_agent_config("claude")
        assert config is BUILTIN_AGENTS["claude"]

    def test_unknown_type_raises_key_error(self) -> None:
        """Unknown agent type raises KeyError."""
        with pytest.raises(KeyError):
            get_agent_config("nonexistent")  # type: ignore[arg-type]
