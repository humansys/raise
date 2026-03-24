"""Tests for AgentRegistry — 3-tier YAML loading with override precedence."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from raise_cli.config.agent_plugin import AgentPlugin, DefaultAgentPlugin
from raise_cli.config.agent_registry import load_registry
from raise_cli.config.agents import AgentConfig

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(data), encoding="utf-8")


# ---------------------------------------------------------------------------
# Built-in loading
# ---------------------------------------------------------------------------


class TestBuiltinLoading:
    """Registry loads 5 built-in agents from bundled YAML files."""

    def test_loads_five_builtin_agents(self) -> None:
        registry = load_registry()
        agents = registry.list_agents()
        assert set(agents) >= {"claude", "cursor", "windsurf", "copilot", "antigravity"}

    def test_claude_builtin_values(self) -> None:
        registry = load_registry()
        config = registry.get_config("claude")
        assert config.name == "Claude Code"
        assert config.agent_type == "claude"
        assert config.instructions_file == "CLAUDE.md"
        assert config.skills_dir == ".claude/skills"
        assert "CLAUDE.md" in config.detection_markers

    def test_cursor_builtin_values(self) -> None:
        registry = load_registry()
        config = registry.get_config("cursor")
        assert config.agent_type == "cursor"
        assert config.skills_dir == ".cursor/skills"
        assert config.instructions_file == ".cursor/rules/raise.mdc"

    def test_windsurf_builtin_values(self) -> None:
        registry = load_registry()
        config = registry.get_config("windsurf")
        assert config.agent_type == "windsurf"
        assert config.skills_dir == ".windsurf/skills"
        assert config.workflows_dir == ".windsurf/workflows"

    def test_copilot_has_plugin(self) -> None:
        registry = load_registry()
        config = registry.get_config("copilot")
        assert config.plugin == "raise_cli.agents.copilot_plugin"

    def test_antigravity_builtin_values(self) -> None:
        registry = load_registry()
        config = registry.get_config("antigravity")
        assert config.agent_type == "antigravity"
        assert config.skills_dir == ".agent/skills"
        assert config.workflows_dir == ".agent/workflows"

    def test_unknown_agent_raises_key_error(self) -> None:
        registry = load_registry()
        with pytest.raises(KeyError):
            registry.get_config("nonexistent")


# ---------------------------------------------------------------------------
# Plugin resolution
# ---------------------------------------------------------------------------


class TestPluginResolution:
    """Registry resolves plugin field to AgentPlugin instances."""

    def test_no_plugin_returns_default(self) -> None:
        registry = load_registry()
        plugin = registry.get_plugin("claude")
        assert isinstance(plugin, DefaultAgentPlugin)

    def test_copilot_resolves_plugin(self) -> None:
        registry = load_registry()
        plugin = registry.get_plugin("copilot")
        # Should not be the default — CopilotPlugin has its own class
        assert not isinstance(plugin, DefaultAgentPlugin)
        # Must satisfy AgentPlugin protocol
        assert isinstance(plugin, AgentPlugin)

    def test_plugin_satisfies_protocol(self) -> None:
        registry = load_registry()
        for agent_type in registry.list_agents():
            plugin = registry.get_plugin(agent_type)
            assert isinstance(plugin, AgentPlugin), (
                f"{agent_type} plugin doesn't satisfy AgentPlugin protocol"
            )


# ---------------------------------------------------------------------------
# Project-level override (.raise/agents/*.yaml)
# ---------------------------------------------------------------------------


class TestProjectOverride:
    """Project .raise/agents/ YAML overrides built-in agents."""

    def test_project_yaml_overrides_builtin(self, tmp_path: Path) -> None:
        _write_yaml(
            tmp_path / ".raise" / "agents" / "claude.yaml",
            {
                "name": "Claude Custom",
                "agent_type": "claude",
                "instructions_file": "CUSTOM.md",
                "skills_dir": ".custom/skills",
            },
        )
        registry = load_registry(project_root=tmp_path)
        config = registry.get_config("claude")
        assert config.instructions_file == "CUSTOM.md"
        assert config.name == "Claude Custom"

    def test_project_yaml_adds_new_agent(self, tmp_path: Path) -> None:
        _write_yaml(
            tmp_path / ".raise" / "agents" / "codex-cli.yaml",
            {
                "name": "Codex CLI",
                "agent_type": "codex-cli",
                "instructions_file": "AGENTS.md",
                "skills_dir": ".codex/skills",
            },
        )
        registry = load_registry(project_root=tmp_path)
        config = registry.get_config("codex-cli")
        assert config.agent_type == "codex-cli"
        assert config.instructions_file == "AGENTS.md"

    def test_project_override_does_not_affect_other_agents(
        self, tmp_path: Path
    ) -> None:
        _write_yaml(
            tmp_path / ".raise" / "agents" / "claude.yaml",
            {
                "name": "Claude Custom",
                "agent_type": "claude",
                "instructions_file": "CUSTOM.md",
                "skills_dir": ".custom/skills",
            },
        )
        registry = load_registry(project_root=tmp_path)
        cursor = registry.get_config("cursor")
        assert cursor.instructions_file == ".cursor/rules/raise.mdc"  # unchanged


# ---------------------------------------------------------------------------
# User-level override (~/.rai/agents/*.yaml)
# ---------------------------------------------------------------------------


class TestUserOverride:
    """User ~/.rai/agents/ YAML overrides both built-in and project agents."""

    def test_user_yaml_wins_over_builtin(self, tmp_path: Path) -> None:
        user_home = tmp_path / "home"
        _write_yaml(
            user_home / ".rai" / "agents" / "claude.yaml",
            {
                "name": "Claude Personal",
                "agent_type": "claude",
                "instructions_file": "PERSONAL.md",
                "skills_dir": ".claude/skills",
            },
        )
        registry = load_registry(user_home=user_home)
        config = registry.get_config("claude")
        assert config.name == "Claude Personal"
        assert config.instructions_file == "PERSONAL.md"

    def test_user_yaml_wins_over_project(self, tmp_path: Path) -> None:
        project_root = tmp_path / "project"
        user_home = tmp_path / "home"

        _write_yaml(
            project_root / ".raise" / "agents" / "claude.yaml",
            {
                "name": "Claude Project",
                "agent_type": "claude",
                "instructions_file": "PROJECT.md",
                "skills_dir": ".claude/skills",
            },
        )
        _write_yaml(
            user_home / ".rai" / "agents" / "claude.yaml",
            {
                "name": "Claude User",
                "agent_type": "claude",
                "instructions_file": "USER.md",
                "skills_dir": ".claude/skills",
            },
        )
        registry = load_registry(project_root=project_root, user_home=user_home)
        config = registry.get_config("claude")
        assert config.name == "Claude User"
        assert config.instructions_file == "USER.md"


# ---------------------------------------------------------------------------
# Agent detection
# ---------------------------------------------------------------------------


class TestAgentDetection:
    """detect_agents checks detection_markers against project filesystem."""

    def test_detects_claude_from_claude_md(self, tmp_path: Path) -> None:
        (tmp_path / "CLAUDE.md").write_text("# Claude")
        registry = load_registry()
        detected = registry.detect_agents(tmp_path)
        assert "claude" in detected

    def test_detects_windsurf_from_dir(self, tmp_path: Path) -> None:
        (tmp_path / ".windsurf").mkdir()
        registry = load_registry()
        detected = registry.detect_agents(tmp_path)
        assert "windsurf" in detected

    def test_detects_copilot_from_instructions(self, tmp_path: Path) -> None:
        (tmp_path / ".github").mkdir()
        (tmp_path / ".github" / "copilot-instructions.md").write_text("# Copilot")
        registry = load_registry()
        detected = registry.detect_agents(tmp_path)
        assert "copilot" in detected

    def test_no_markers_returns_empty(self, tmp_path: Path) -> None:
        empty_home = tmp_path / "empty-home"
        empty_home.mkdir()
        registry = load_registry()
        detected = registry.detect_agents(tmp_path, user_home=empty_home)
        assert detected == []

    def test_no_duplicate_detection(self, tmp_path: Path) -> None:
        """Same agent only detected once even if multiple markers match."""
        empty_home = tmp_path / "empty-home"
        empty_home.mkdir()
        (tmp_path / "CLAUDE.md").write_text("# Claude")
        (tmp_path / ".claude").mkdir()
        registry = load_registry()
        detected = registry.detect_agents(tmp_path, user_home=empty_home)
        assert detected.count("claude") == 1

    def test_detects_claude_from_home_claude_dir(self, tmp_path: Path) -> None:
        """~/.claude in home dir detected as claude marker (pre-init brownfield)."""
        mock_home = tmp_path / "home"
        (mock_home / ".claude").mkdir(parents=True)
        registry = load_registry()
        detected = registry.detect_agents(tmp_path, user_home=mock_home)
        assert "claude" in detected


# ---------------------------------------------------------------------------
# AgentRegistry model
# ---------------------------------------------------------------------------


class TestAgentRegistryModel:
    """AgentRegistry stores configs and returns them correctly."""

    def test_list_agents_returns_all_types(self) -> None:
        registry = load_registry()
        agents = registry.list_agents()
        assert len(agents) >= 5
        assert "claude" in agents

    def test_get_config_returns_agent_config(self) -> None:
        registry = load_registry()
        config = registry.get_config("claude")
        assert isinstance(config, AgentConfig)

    def test_invalid_yaml_in_project_is_skipped(self, tmp_path: Path) -> None:
        """Malformed YAML files are skipped with a warning, not a crash."""
        agents_dir = tmp_path / ".raise" / "agents"
        agents_dir.mkdir(parents=True)
        (agents_dir / "bad.yaml").write_text("{{not valid yaml}}: [")
        # Should not raise — skips bad file
        registry = load_registry(project_root=tmp_path)
        # Built-ins still available
        assert registry.get_config("claude").agent_type == "claude"
