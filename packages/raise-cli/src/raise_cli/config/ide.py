"""Backward-compatibility shim for IDE configuration.

All types have been moved to raise_cli.config.agents.
This module re-exports old names for external consumers.

Migration: IdeConfig → AgentConfig, IdeType → BuiltinAgentType,
IdeChoice → AgentChoice, IDE_CONFIGS → BUILTIN_AGENTS,
get_ide_config → get_agent_config.
"""

from raise_cli.config.agents import (
    BUILTIN_AGENTS as BUILTIN_AGENTS,
)
from raise_cli.config.agents import (
    AgentChoice as AgentChoice,
)
from raise_cli.config.agents import (
    AgentConfig as AgentConfig,
)
from raise_cli.config.agents import (
    BuiltinAgentType as BuiltinAgentType,
)
from raise_cli.config.agents import (
    get_agent_config as get_agent_config,
)

# Backward-compat aliases
IdeConfig = AgentConfig
IdeType = BuiltinAgentType
IdeChoice = AgentChoice
IDE_CONFIGS = BUILTIN_AGENTS
get_ide_config = get_agent_config
