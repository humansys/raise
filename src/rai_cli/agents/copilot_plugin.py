"""CopilotPlugin — transforms RaiSE skills to GitHub Copilot agent format.

Stub implementation. Full logic implemented in Task 6 (RAISE-197).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from rai_cli.config.agents import AgentConfig


class CopilotPlugin:
    """Transform RaiSE skills and instructions for GitHub Copilot.

    Copilot uses a different frontmatter schema for .github/agents/ files
    and supports .github/prompts/*.prompt.md workflow files.

    Full implementation: RAISE-197 Task 6.
    """

    def transform_instructions(self, content: str, config: AgentConfig) -> str:
        """Return instructions unchanged (Copilot reads standard markdown)."""
        return content

    def transform_skill(
        self, frontmatter: dict[str, Any], body: str, config: AgentConfig
    ) -> tuple[dict[str, Any], str]:
        """Transform skill frontmatter to Copilot agent format.

        Adds Copilot-specific fields; removes incompatible ones.
        Full implementation in Task 6.
        """
        fm = dict(frontmatter)
        fm["tools"] = ["execute", "read", "edit", "search"]
        fm["infer"] = True
        fm.pop("license", None)
        fm.pop("compatibility", None)
        return fm, body

    def post_init(self, project_root: Path, config: AgentConfig) -> list[str]:
        """Generate .prompt.md files from skills. Full implementation in Task 6."""
        return []
