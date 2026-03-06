"""Agent configuration model and factory.

Defines agent-specific conventions (paths, file names) as data.
Each supported agent has a pre-built AgentConfig in the registry.
Factory function returns the config for a given agent type.

Replaces the IDE-specific model from ADR-031 with a generic agent abstraction.
Architecture decision: ADR-032 (Multi-agent skill distribution).
"""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

BuiltinAgentType = Literal[
    "claude", "cursor", "windsurf", "copilot", "antigravity", "roo"
]


class AgentChoice(StrEnum):
    """Typer-compatible enum for --agent CLI option."""

    claude = "claude"
    cursor = "cursor"
    windsurf = "windsurf"
    copilot = "copilot"
    antigravity = "antigravity"
    roo = "roo"


class AgentConfig(BaseModel):
    """Configuration for a target agent/IDE/CLI.

    Attributes:
        name: Display name for this agent.
        agent_type: Registry key (e.g. "claude", "codex-cli", "azure-devops").
        instructions_file: Relative path to instructions/rules file from project root.
        skills_dir: Relative path to skills directory (None if agent has no skills support).
        workflows_dir: Relative path to workflows directory (None if agent has no equivalent).
        detection_markers: Paths to check for presence during auto-detection.
        plugin: Python module path for custom logic (None for default pass-through).
    """

    model_config = ConfigDict(frozen=True)

    name: str
    agent_type: str
    instructions_file: str
    skills_dir: str | None = None
    workflows_dir: str | None = None
    detection_markers: list[str] = Field(default_factory=list)
    plugin: str | None = None


BUILTIN_AGENTS: dict[BuiltinAgentType, AgentConfig] = {
    "claude": AgentConfig(
        name="Claude Code",
        agent_type="claude",
        skills_dir=".claude/skills",
        instructions_file="CLAUDE.md",
        detection_markers=["CLAUDE.md", ".claude"],
    ),
    "cursor": AgentConfig(
        name="Cursor",
        agent_type="cursor",
        skills_dir=".cursor/skills",
        instructions_file=".cursor/rules/raise.mdc",
        detection_markers=[".cursor/rules", ".cursor"],
    ),
    "windsurf": AgentConfig(
        name="Windsurf",
        agent_type="windsurf",
        skills_dir=".windsurf/skills",
        instructions_file=".windsurf/rules/raise.md",
        workflows_dir=".windsurf/workflows",
        detection_markers=[".windsurf/rules", ".windsurf"],
    ),
    "copilot": AgentConfig(
        name="GitHub Copilot",
        agent_type="copilot",
        skills_dir=".github/agents",
        instructions_file=".github/copilot-instructions.md",
        workflows_dir=".github/prompts",
        detection_markers=[".github/copilot-instructions.md"],
        plugin="raise_cli.agents.copilot_plugin",
    ),
    "antigravity": AgentConfig(
        name="Antigravity",
        agent_type="antigravity",
        skills_dir=".agent/skills",
        instructions_file=".agent/rules/raise.md",
        workflows_dir=".agent/workflows",
        detection_markers=[".agent/rules", ".agent"],
    ),
    "roo": AgentConfig(
        name="Roo Code",
        agent_type="roo",
        skills_dir=".roo/skills",
        instructions_file=".roo/rules/raise.md",
        detection_markers=[".roo/rules", ".roo", ".rooignore"],
    ),
}


def get_agent_config(agent_type: BuiltinAgentType = "claude") -> AgentConfig:
    """Get the agent configuration for a given agent type.

    Args:
        agent_type: The agent to get config for. Defaults to "claude".

    Returns:
        AgentConfig with paths and conventions for the requested agent.

    Raises:
        KeyError: If agent_type is not in the built-in registry.
    """
    return BUILTIN_AGENTS[agent_type]
