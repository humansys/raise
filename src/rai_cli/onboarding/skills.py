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

from rai_cli.config.agents import AgentConfig, get_agent_config

logger = logging.getLogger(__name__)


class SkillScaffoldResult(BaseModel):
    """Result of skill scaffolding operation."""

    skills_copied: int = 0
    already_existed: bool = False
    files_copied: list[str] = Field(default_factory=list)
    files_skipped: list[str] = Field(default_factory=list)
    skills_installed: list[str] = Field(default_factory=list)
    skills_skipped_names: list[str] = Field(default_factory=list)


def _copy_skill_tree(
    source_dir: Traversable,
    dest_dir: Path,
    result: SkillScaffoldResult,
) -> int:
    """Recursively copy skill files from source to destination.

    Args:
        source_dir: Traversable resource directory.
        dest_dir: Target directory on filesystem.
        result: Result object to track copied/skipped files.

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
            dest.write_text(item.read_text(encoding="utf-8"), encoding="utf-8")
            result.files_copied.append(str(dest))
            copied += 1
            logger.debug("Copied: %s", dest)
        elif item.is_dir():
            copied += _copy_skill_tree(item, dest, result)
    return copied


def scaffold_skills(
    project_root: Path,
    *,
    agent_config: AgentConfig | None = None,
) -> SkillScaffoldResult:
    """Copy bundled skills to project skill directory.

    Copies skill files from the installed rai_cli.skills_base
    package, including reference subdirectories. Uses per-file
    idempotency — existing files are never overwritten.

    Args:
        project_root: Project root directory.
        ide_config: IDE configuration. Defaults to Claude.

    Returns:
        SkillScaffoldResult with details of what was copied or skipped.
    """
    from rai_cli.skills_base import DISTRIBUTABLE_SKILLS

    config = agent_config or get_agent_config()
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
        copied = _copy_skill_tree(source, skill_dest, result)

        if copied > 0:
            result.skills_installed.append(skill_name)
            result.skills_copied += 1

    result.already_existed = result.skills_copied == 0

    return result
