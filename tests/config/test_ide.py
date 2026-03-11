"""Tests for IDE backward-compatibility shim.

Verifies that old names still work as aliases for the new agent types.
"""

from __future__ import annotations

from raise_cli.config.ide import (
    IDE_CONFIGS,
    IdeConfig,
    IdeType,
    get_ide_config,
)


class TestIdeBackwardCompat:
    """Tests that old IDE aliases still resolve correctly."""

    def test_ide_config_is_agent_config(self) -> None:
        """IdeConfig should be an alias for AgentConfig."""
        from raise_cli.config.agents import AgentConfig

        assert IdeConfig is AgentConfig

    def test_ide_type_is_builtin_agent_type(self) -> None:
        """IdeType should be an alias for BuiltinAgentType."""
        from raise_cli.config.agents import BuiltinAgentType

        assert IdeType is BuiltinAgentType

    def test_ide_configs_is_builtin_agents(self) -> None:
        """IDE_CONFIGS should be the same dict as BUILTIN_AGENTS."""
        from raise_cli.config.agents import BUILTIN_AGENTS

        assert IDE_CONFIGS is BUILTIN_AGENTS

    def test_get_ide_config_is_get_agent_config(self) -> None:
        """get_ide_config should be the same function as get_agent_config."""
        from raise_cli.config.agents import get_agent_config

        assert get_ide_config is get_agent_config

    def test_claude_accessible_via_old_api(self) -> None:
        """Claude config should be accessible via old get_ide_config."""
        config = get_ide_config("claude")
        assert config.agent_type == "claude"
        assert config.skills_dir == ".claude/skills"
        assert config.instructions_file == "CLAUDE.md"

    def test_antigravity_accessible_via_old_api(self) -> None:
        """Antigravity config should be accessible via old get_ide_config."""
        config = get_ide_config("antigravity")
        assert config.agent_type == "antigravity"
        assert config.skills_dir == ".agent/skills"

    def test_defaults_to_claude(self) -> None:
        """get_ide_config() defaults to claude."""
        config = get_ide_config()
        assert config.agent_type == "claude"
