"""Agent registry — 3-tier YAML loading with override precedence.

Loads agent configurations from:
  1. Built-in YAML files (bundled in raise_cli.agents package)
  2. Project-level .raise/agents/*.yaml
  3. User-level ~/.rai/agents/*.yaml

Last-wins precedence: user > project > built-in.

Architecture: ADR-032 (Multi-agent skill distribution).
"""

from __future__ import annotations

import importlib
import logging
from importlib.resources import files
from pathlib import Path
from typing import Any, cast

import yaml

from raise_cli.config.agent_plugin import AgentPlugin, DefaultAgentPlugin
from raise_cli.config.agents import AgentConfig

logger = logging.getLogger(__name__)

_DEFAULT_PLUGIN = DefaultAgentPlugin()


def _parse_agent_config(data: dict[str, Any]) -> AgentConfig:
    """Parse a YAML dict into an AgentConfig model."""
    return AgentConfig(
        name=data["name"],
        agent_type=data["agent_type"],
        instructions_file=data["instructions_file"],
        skills_dir=data.get("skills_dir"),
        workflows_dir=data.get("workflows_dir"),
        detection_markers=data.get("detection_markers", []),
        plugin=data.get("plugin"),
    )


def _load_yaml_dir(directory: Path) -> dict[str, AgentConfig]:
    """Load all *.yaml files from a directory into agent configs."""
    configs: dict[str, AgentConfig] = {}
    if not directory.exists():
        return configs
    for yaml_file in sorted(directory.glob("*.yaml")):
        try:
            raw = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                logger.warning("Skipping %s: not a YAML mapping", yaml_file)
                continue
            config = _parse_agent_config(cast("dict[str, Any]", raw))
            configs[config.agent_type] = config
        except (yaml.YAMLError, KeyError, TypeError, ValueError) as e:
            logger.warning("Skipping %s: %s", yaml_file, e)
    return configs


def _load_builtin_agents() -> dict[str, AgentConfig]:
    """Load agent configs from the bundled raise_cli.agents package."""
    configs: dict[str, AgentConfig] = {}
    agents_pkg = files("raise_cli.agents")
    for entry in agents_pkg.iterdir():
        if not entry.name.endswith(".yaml"):
            continue
        try:
            raw = yaml.safe_load(entry.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                logger.warning("Skipping built-in %s: not a YAML mapping", entry.name)
                continue
            config = _parse_agent_config(cast("dict[str, Any]", raw))
            configs[config.agent_type] = config
        except (yaml.YAMLError, KeyError, TypeError, ValueError) as e:
            logger.warning("Skipping built-in %s: %s", entry.name, e)
    return configs


def _resolve_plugin(plugin_path: str | None) -> AgentPlugin:
    """Resolve a plugin module path string to an AgentPlugin instance.

    Expects the module to contain a class with the same name as the last
    segment of the module path (PascalCase), or a class named 'Plugin'.

    Args:
        plugin_path: Module path like "raise_cli.agents.copilot_plugin",
                     or None for default pass-through.

    Returns:
        AgentPlugin instance.
    """
    if not plugin_path:
        return _DEFAULT_PLUGIN

    try:
        module = importlib.import_module(plugin_path)
    except ImportError as e:
        logger.warning("Could not import plugin %r: %s — using default", plugin_path, e)
        return _DEFAULT_PLUGIN

    # Convention: look for class named Plugin, or derive from module name
    # e.g. "copilot_plugin" → "CopilotPlugin"
    segments = plugin_path.split(".")
    module_name = segments[-1]  # e.g. "copilot_plugin"
    class_name = "".join(part.capitalize() for part in module_name.split("_"))
    # e.g. "CopilotPlugin"

    cls = getattr(module, class_name, None) or getattr(module, "Plugin", None)
    if cls is None:
        logger.warning(
            "Plugin module %r has no class %r or 'Plugin' — using default",
            plugin_path,
            class_name,
        )
        return _DEFAULT_PLUGIN

    try:
        return cls()
    except Exception as e:
        logger.warning(
            "Could not instantiate %r from %r: %s", class_name, plugin_path, e
        )
        return _DEFAULT_PLUGIN


class AgentRegistry:
    """Registry of agent configurations loaded from 3-tier YAML sources.

    Provides config and plugin lookup by agent_type key.
    """

    def __init__(self, configs: dict[str, AgentConfig]) -> None:
        self._configs = configs
        self._plugins: dict[str, AgentPlugin] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_config(self, agent_type: str) -> AgentConfig:
        """Return AgentConfig for the given agent_type.

        Raises:
            KeyError: If agent_type is not registered.
        """
        return self._configs[agent_type]

    def get_plugin(self, agent_type: str) -> AgentPlugin:
        """Return AgentPlugin for the given agent_type (cached after first call).

        Falls back to DefaultAgentPlugin if no plugin specified or load fails.

        Raises:
            KeyError: If agent_type is not registered.
        """
        if agent_type not in self._configs:
            raise KeyError(agent_type)
        if agent_type not in self._plugins:
            config = self._configs[agent_type]
            self._plugins[agent_type] = _resolve_plugin(config.plugin)
        return self._plugins[agent_type]

    def list_agents(self) -> list[str]:
        """Return sorted list of all registered agent_type keys."""
        return sorted(self._configs.keys())

    def detect_agents(
        self, project_root: Path, user_home: Path | None = None
    ) -> list[str]:
        """Detect which registered agents have marker files in project_root.

        Checks each agent's detection_markers list; stops at first match per
        agent. Markers starting with ``~/`` are resolved against user_home
        (defaults to Path.home()) instead of project_root.

        Args:
            project_root: Directory to check for project-relative marker paths.
            user_home: Home directory for ``~/`` markers (defaults to Path.home()).

        Returns:
            Sorted list of detected agent_type strings.
        """
        home = user_home if user_home is not None else Path.home()
        detected: list[str] = []
        for agent_type, config in self._configs.items():
            for marker in config.detection_markers:
                if marker.startswith("~/"):
                    check_path = home / marker[2:]
                else:
                    check_path = project_root / marker
                if check_path.exists():
                    detected.append(agent_type)
                    break
        return sorted(detected)


def load_registry(
    project_root: Path | None = None,
    user_home: Path | None = None,
) -> AgentRegistry:
    """Load the 3-tier agent registry.

    Loading order (last-wins):
    1. Built-in YAML files bundled in raise_cli.agents package
    2. Project-level .raise/agents/*.yaml (if project_root provided)
    3. User-level ~/.rai/agents/*.yaml (if user_home provided; defaults to Path.home())

    Args:
        project_root: Project root directory for .raise/agents/ lookup.
        user_home: Home directory for ~/.rai/agents/ lookup.
                   Defaults to Path.home() if not provided.

    Returns:
        AgentRegistry populated with merged configs.
    """
    # Tier 1: built-in
    configs: dict[str, AgentConfig] = _load_builtin_agents()

    # Tier 2: project-level
    if project_root is not None:
        project_agents_dir = project_root / ".raise" / "agents"
        project_configs = _load_yaml_dir(project_agents_dir)
        configs.update(project_configs)

    # Tier 3: user-level
    home = user_home if user_home is not None else Path.home()
    user_agents_dir = home / ".rai" / "agents"
    user_configs = _load_yaml_dir(user_agents_dir)
    configs.update(user_configs)

    return AgentRegistry(configs)
