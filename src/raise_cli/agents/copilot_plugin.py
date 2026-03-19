"""CopilotPlugin — transforms RaiSE skills to GitHub Copilot agent format.

GitHub Copilot uses:
  - .github/agents/*.SKILL.md   (different frontmatter: tools, infer)
  - .github/prompts/*.prompt.md (one per skill, for Copilot workflows)

This plugin handles both transformations via AgentPlugin protocol hooks.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, cast

from raise_cli.config.agents import AgentConfig

logger = logging.getLogger(__name__)

_COPILOT_TOOLS = ["execute", "read", "edit", "search"]
_REMOVE_FIELDS = {"license", "compatibility"}


class CopilotPlugin:
    """Transform RaiSE skills and instructions for GitHub Copilot.

    Copilot uses a different frontmatter schema for .github/agents/ files
    and supports .github/prompts/*.prompt.md workflow files.
    """

    def transform_instructions(self, content: str, _config: AgentConfig) -> str:
        """Return instructions unchanged — Copilot reads standard markdown."""
        return content

    def transform_skill(
        self, frontmatter: dict[str, Any], body: str, _config: AgentConfig
    ) -> tuple[dict[str, Any], str]:
        """Transform skill frontmatter to Copilot agent format.

        Adds Copilot-specific fields (tools, infer).
        Removes fields unsupported by Copilot (license, compatibility).
        """
        fm = {k: v for k, v in frontmatter.items() if k not in _REMOVE_FIELDS}
        fm["tools"] = list(_COPILOT_TOOLS)
        fm["infer"] = True
        return fm, body

    def post_init(self, project_root: Path, config: AgentConfig) -> list[str]:
        """Generate .prompt.md files from skills in .github/agents/.

        Reads each SKILL.md in the skills_dir, extracts name and description
        from frontmatter, and writes a .prompt.md to .github/prompts/.

        Args:
            project_root: Project root directory.
            config: Copilot agent configuration.

        Returns:
            List of created .prompt.md file paths.
        """
        if config.skills_dir is None:
            return []

        agents_dir = project_root / config.skills_dir
        if not agents_dir.exists():
            return []

        prompts_dir = project_root / ".github" / "prompts"
        prompts_dir.mkdir(parents=True, exist_ok=True)

        created: list[str] = []
        for skill_dir in sorted(agents_dir.iterdir()):
            if not skill_dir.is_dir():
                continue
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                continue

            skill_name = skill_dir.name
            frontmatter = _read_frontmatter(skill_md)
            name = frontmatter.get("name", skill_name)
            description = frontmatter.get("description", "")

            prompt_content = _build_prompt_md(skill_name, name, str(description))
            prompt_file = prompts_dir / f"{skill_name}.prompt.md"
            prompt_file.write_text(prompt_content, encoding="utf-8")
            created.append(str(prompt_file))
            logger.debug("Created Copilot prompt: %s", prompt_file)

        return created


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _read_frontmatter(skill_md: Path) -> dict[str, Any]:
    """Parse YAML frontmatter from a SKILL.md file (best-effort)."""
    try:
        import yaml

        content = skill_md.read_text(encoding="utf-8")
        if not content.startswith("---"):
            return {}
        parts = content.split("---", 2)
        if len(parts) < 3:
            return {}
        raw: Any = yaml.safe_load(parts[1])
        if not isinstance(raw, dict):
            return {}
        return cast("dict[str, Any]", raw)
    except Exception as e:
        logger.debug("Failed to parse frontmatter from %s: %s", skill_md, e)
        return {}


def _build_prompt_md(skill_name: str, name: str, description: str) -> str:
    """Build .prompt.md content for a Copilot workflow prompt."""
    return (
        f"# {name}\n\n"
        f"{description.strip()}\n\n"
        f"---\n\n"
        f"Run the `{skill_name}` skill from `.github/agents/{skill_name}/SKILL.md`.\n"
    )
