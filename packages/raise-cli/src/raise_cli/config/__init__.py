"""Configuration module for raise-cli.

Provides configuration settings and XDG-compliant directory helpers.
"""

from __future__ import annotations

from raise_cli.config.agents import (
    BUILTIN_AGENTS,
    AgentChoice,
    AgentConfig,
    BuiltinAgentType,
    get_agent_config,
)
from raise_cli.config.paths import get_cache_dir, get_config_dir, get_data_dir
from raise_cli.config.settings import RaiSettings

# Backward-compat aliases
IDE_CONFIGS = BUILTIN_AGENTS
IdeChoice = AgentChoice
IdeConfig = AgentConfig
IdeType = BuiltinAgentType
get_ide_config = get_agent_config

__all__ = [
    "BUILTIN_AGENTS",
    "AgentChoice",
    "AgentConfig",
    "BuiltinAgentType",
    "get_agent_config",
    # Backward-compat
    "IDE_CONFIGS",
    "IdeChoice",
    "IdeConfig",
    "IdeType",
    "get_ide_config",
    "get_cache_dir",
    "get_config_dir",
    "get_data_dir",
    "RaiSettings",
]
