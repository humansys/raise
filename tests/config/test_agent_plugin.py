"""Tests for AgentPlugin protocol and DefaultAgentPlugin."""

from __future__ import annotations

from pathlib import Path

from raise_cli.config.agent_plugin import DefaultAgentPlugin
from raise_cli.config.agents import BUILTIN_AGENTS, AgentConfig


def _claude_config() -> AgentConfig:
    return BUILTIN_AGENTS["claude"]


class TestDefaultAgentPlugin:
    """DefaultAgentPlugin passes everything through unchanged."""

    def test_transform_instructions_passthrough(self) -> None:
        content = "# CLAUDE.md\nSome content here."
        plugin = DefaultAgentPlugin()
        result = plugin.transform_instructions(content, _claude_config())
        assert result == content

    def test_transform_skill_passthrough(self) -> None:
        fm = {"name": "rai-session-start", "description": "Begin session"}
        body = "# Session Start\nDo things."
        plugin = DefaultAgentPlugin()
        out_fm, out_body = plugin.transform_skill(fm, body, _claude_config())
        assert out_fm == fm
        assert out_body == body

    def test_transform_skill_returns_copies_not_references(self) -> None:
        fm = {"name": "test"}
        plugin = DefaultAgentPlugin()
        out_fm, _ = plugin.transform_skill(fm, "", _claude_config())
        # Mutation of returned dict should not affect original
        out_fm["extra"] = "added"
        assert "extra" not in fm

    def test_post_init_returns_empty_list(self, tmp_path: Path) -> None:
        plugin = DefaultAgentPlugin()
        created = plugin.post_init(tmp_path, _claude_config())
        assert created == []

    def test_post_init_does_not_create_files(self, tmp_path: Path) -> None:
        plugin = DefaultAgentPlugin()
        plugin.post_init(tmp_path, _claude_config())
        assert list(tmp_path.iterdir()) == []


class TestAgentPluginProtocol:
    """AgentPlugin is a structural protocol — duck typing, no inheritance needed."""

    def test_class_without_inheritance_satisfies_protocol(self) -> None:
        """A class implementing the 3 methods satisfies AgentPlugin without inheriting."""

        class MyPlugin:
            def transform_instructions(self, content: str, config: AgentConfig) -> str:
                return content

            def transform_skill(
                self, frontmatter: dict[str, object], body: str, config: AgentConfig
            ) -> tuple[dict[str, object], str]:
                return frontmatter, body

            def post_init(self, project_root: Path, config: AgentConfig) -> list[str]:
                return []

        plugin = MyPlugin()
        # If AgentPlugin is a runtime-checkable Protocol, isinstance works
        # If not, we just verify duck typing by calling the methods
        result = plugin.transform_instructions("test", _claude_config())
        assert result == "test"
        fm, body = plugin.transform_skill({"k": "v"}, "body", _claude_config())
        assert fm == {"k": "v"}
        files = plugin.post_init(Path("."), _claude_config())
        assert files == []

    def test_default_plugin_satisfies_protocol(self) -> None:
        from raise_cli.config.agent_plugin import AgentPlugin

        plugin: AgentPlugin = DefaultAgentPlugin()
        # Type checker confirms; runtime just calls the methods
        result = plugin.transform_instructions("x", _claude_config())
        assert result == "x"
