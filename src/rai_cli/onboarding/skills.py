"""Scaffold bundled skills into a project.

Copies RaiSE skills from the rai_cli.skills_base package
to the project's IDE skill directory during `rai init`.

Uses importlib.resources to read bundled skill files (Python 3.9+).
Per-file idempotency: existing files are never overwritten.
Handles reference subdirectories (e.g., references/, _references/).

Example:
    from rai_cli.onboarding.skills import scaffold_skills

    result = scaffold_skills(project_path)
    if result.skills_copied > 0:
        print(f"Installed {result.skills_copied} skills")
"""

from __future__ import annotations

import logging
from importlib.resources import files
from importlib.resources.abc import Traversable
from pathlib import Path

from pydantic import BaseModel, Field

from rai_cli.config.agent_plugin import AgentPlugin
from rai_cli.config.agents import AgentConfig, get_agent_config

logger = logging.getLogger(__name__)


class SkillScaffoldResult(BaseModel):
    """Result of skill scaffolding operation."""

    # New sync-aware fields
    skills_installed: list[str] = Field(default_factory=list)
    skills_updated: list[str] = Field(default_factory=list)
    skills_conflicted: list[str] = Field(default_factory=list)
    skills_kept: list[str] = Field(default_factory=list)
    skills_overwritten: list[str] = Field(default_factory=list)
    skills_current: list[str] = Field(default_factory=list)

    # Backward-compat fields
    skills_copied: int = 0
    already_existed: bool = False
    files_copied: list[str] = Field(default_factory=list)
    files_skipped: list[str] = Field(default_factory=list)
    skills_skipped_names: list[str] = Field(default_factory=list)


def _apply_plugin_transform(
    content: str,
    plugin: AgentPlugin,
    agent_config: AgentConfig,
) -> str:
    """Apply plugin.transform_skill to a SKILL.md content string."""
    import yaml

    from rai_cli.skills.parser import parse_frontmatter

    fm, body = parse_frontmatter(content)
    fm_out, body_out = plugin.transform_skill(fm, body, agent_config)
    # Re-serialize: frontmatter + body
    if fm_out:
        return f"---\n{yaml.dump(fm_out, default_flow_style=False, allow_unicode=True)}---\n{body_out}"
    return body_out


def _copy_skill_tree(
    source_dir: Traversable,
    dest_dir: Path,
    result: SkillScaffoldResult,
    *,
    plugin: AgentPlugin | None = None,
    agent_config: AgentConfig | None = None,
) -> int:
    """Recursively copy skill files from source to destination.

    Args:
        source_dir: Traversable resource directory.
        dest_dir: Target directory on filesystem.
        result: Result object to track copied/skipped files.
        plugin: Optional plugin to transform SKILL.md files.
        agent_config: Agent config passed to plugin.

    Returns:
        Number of files copied.
    """
    copied = 0
    for item in source_dir.iterdir():
        if item.name == "__init__.py" or item.name == "__pycache__":
            continue
        dest = dest_dir / item.name
        if item.is_file():
            if dest.exists():
                result.files_skipped.append(str(dest))
                logger.debug("Skipped (exists): %s", dest)
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            raw_content = item.read_text(encoding="utf-8")
            if plugin is not None and agent_config is not None and item.name == "SKILL.md":
                raw_content = _apply_plugin_transform(raw_content, plugin, agent_config)
            dest.write_text(raw_content, encoding="utf-8")
            result.files_copied.append(str(dest))
            copied += 1
            logger.debug("Copied: %s", dest)
        elif item.is_dir():
            copied += _copy_skill_tree(
                item, dest, result, plugin=plugin, agent_config=agent_config
            )
    return copied


def scaffold_skills(
    project_root: Path,
    *,
    agent_config: AgentConfig | None = None,
    plugin: AgentPlugin | None = None,
) -> SkillScaffoldResult:
    """Copy bundled skills to project skill directory.

    Copies skill files from the installed rai_cli.skills_base
    package, including reference subdirectories. Uses per-file
    idempotency — existing files are never overwritten.

    Args:
        project_root: Project root directory.
        agent_config: Agent configuration. Defaults to Claude.
        plugin: Optional plugin to transform SKILL.md files during copy.

    Returns:
        SkillScaffoldResult with details of what was copied or skipped.
    """
    from rai_cli.skills_base import DISTRIBUTABLE_SKILLS

    config = agent_config or get_agent_config()
    if config.skills_dir is None:
        return SkillScaffoldResult()

    base = files("rai_cli.skills_base")
    skills_dir = project_root / config.skills_dir
    result = SkillScaffoldResult()

    for skill_name in DISTRIBUTABLE_SKILLS:
        skill_dest = skills_dir / skill_name
        skill_md = skill_dest / "SKILL.md"

        if skill_md.exists():
            result.files_skipped.append(str(skill_md))
            result.skills_skipped_names.append(skill_name)
            logger.debug("Skipped (exists): %s", skill_md)
            continue

        source = base / skill_name
        copied = _copy_skill_tree(
            source, skill_dest, result, plugin=plugin, agent_config=config
        )

        if copied > 0:
            result.skills_installed.append(skill_name)
            result.skills_copied += 1

    result.already_existed = result.skills_copied == 0

    return result
