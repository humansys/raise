"""AgentPlugin protocol and default implementation.

Defines the extensibility interface for agent-specific transformations.
Plugins can transform instructions, skills, and run post-init hooks.

Architecture: ADR-032 (Multi-agent skill distribution).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from raise_cli.config.agents import AgentConfig


@runtime_checkable
class AgentPlugin(Protocol):
    r"""Protocol for custom agent connectors.

    Implementors add agent-specific transformation logic without modifying
    the raise-cli engine. A plugin only needs to implement the methods it uses —
    duck typing, no forced inheritance.

    Example (minimal plugin):
        class MyPlugin:
            def transform_instructions(self, content, config):
                return f"<!-- {config.name} -->\n{content}"

            def transform_skill(self, frontmatter, body, config):
                return frontmatter, body

            def post_init(self, project_root, config):
                return []
    """

    def transform_instructions(self, content: str, config: AgentConfig) -> str:
        """Transform generated instructions for this target.

        Called after the instructions content is generated, before writing to disk.
        Default: pass-through (return content unchanged).

        Args:
            content: Generated markdown instructions content.
            config: Target agent configuration.

        Returns:
            Transformed content string.
        """
        ...

    def transform_skill(
        self, frontmatter: dict[str, Any], body: str, config: AgentConfig
    ) -> tuple[dict[str, Any], str]:
        """Transform a SKILL.md for this target.

        Called for each skill file during scaffolding.
        Default: pass-through (return unchanged).

        Args:
            frontmatter: Parsed YAML frontmatter dict.
            body: Skill body markdown text.
            config: Target agent configuration.

        Returns:
            Tuple of (transformed_frontmatter, transformed_body).
        """
        ...

    def post_init(self, project_root: Path, config: AgentConfig) -> list[str]:
        """Run after all files are generated.

        Called once at the end of `rai init` for this agent.
        Default: no-op (return empty list).

        Args:
            project_root: Project root directory.
            config: Target agent configuration.

        Returns:
            List of file paths created by this hook.
        """
        ...


class DefaultAgentPlugin:
    """Default no-op plugin used when no plugin is specified.

    All methods are pass-through — skills and instructions are copied
    as-is with no transformation. Four of five built-in agents use this.
    """

    def transform_instructions(self, content: str, config: AgentConfig) -> str:
        """Return content unchanged."""
        return content

    def transform_skill(
        self, frontmatter: dict[str, Any], body: str, config: AgentConfig
    ) -> tuple[dict[str, Any], str]:
        """Return frontmatter and body unchanged (copies, not references)."""
        return dict(frontmatter), body

    def post_init(self, project_root: Path, config: AgentConfig) -> list[str]:
        """No-op — return empty list."""
        return []
