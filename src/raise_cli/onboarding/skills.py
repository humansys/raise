"""Scaffold bundled skills into a project.

Copies onboarding skills from the raise_cli.skills_base package
to the project's .claude/skills/ directory during `raise init`.

Uses importlib.resources to read bundled SKILL.md files (Python 3.9+).
Per-file idempotency: existing files are never overwritten.

Example:
    from raise_cli.onboarding.skills import scaffold_skills

    result = scaffold_skills(project_path)
    if result.skills_copied > 0:
        print(f"Installed {result.skills_copied} skills")
"""

from __future__ import annotations

import logging
from importlib.resources import files
from pathlib import Path

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class SkillScaffoldResult(BaseModel):
    """Result of skill scaffolding operation."""

    skills_copied: int = 0
    already_existed: bool = False
    files_copied: list[str] = Field(default_factory=list)
    files_skipped: list[str] = Field(default_factory=list)
    skills_installed: list[str] = Field(default_factory=list)
    skills_skipped_names: list[str] = Field(default_factory=list)


def scaffold_skills(project_root: Path) -> SkillScaffoldResult:
    """Copy bundled skills to project .claude/skills/ directory.

    Copies SKILL.md files from the installed raise_cli.skills_base
    package. Uses per-file idempotency — existing files are never
    overwritten.

    Args:
        project_root: Project root directory.

    Returns:
        SkillScaffoldResult with details of what was copied or skipped.
    """
    from raise_cli.skills_base import DISTRIBUTABLE_SKILLS

    base = files("raise_cli.skills_base")
    skills_dir = project_root / ".claude" / "skills"
    result = SkillScaffoldResult()

    for skill_name in DISTRIBUTABLE_SKILLS:
        dest = skills_dir / skill_name / "SKILL.md"

        if dest.exists():
            result.files_skipped.append(str(dest))
            result.skills_skipped_names.append(skill_name)
            logger.debug("Skipped (exists): %s", dest)
            continue

        source = base / skill_name / "SKILL.md"
        content = source.read_text()

        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content)
        result.files_copied.append(str(dest))
        result.skills_installed.append(skill_name)
        result.skills_copied += 1
        logger.debug("Copied: %s", dest)

    result.already_existed = result.skills_copied == 0

    return result
