"""Skill locator for finding and loading skills.

Discovers skills in the IDE skill directory (e.g. .claude/skills/
for Claude Code, .agent/skills/ for Antigravity) and provides
methods for loading and organizing them.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from raise_cli.config.agents import AgentConfig, get_agent_config
from raise_cli.skills.parser import parse_skill
from raise_cli.skills.schema import Skill

SKILL_MD_FILENAME = "SKILL.md"


def get_default_skill_dir(
    project_root: Path | None = None,
    *,
    agent_config: AgentConfig | None = None,
) -> Path:
    """Get the default skill directory path.

    Args:
        project_root: Project root directory. Defaults to current directory.
        agent_config: Agent configuration. Defaults to Claude.

    Returns:
        Path to the agent's skill directory.
    """
    root = project_root or Path.cwd()
    config = agent_config or get_agent_config()
    skills_dir = config.skills_dir or ".claude/skills"
    return root / skills_dir


class SkillLocator:
    """Locates and loads skills from a skill directory.

    Typical usage:
        locator = SkillLocator()
        skills = locator.load_all_skills()
        grouped = locator.group_by_lifecycle(skills)
    """

    def __init__(self, skill_dir: Path | None = None) -> None:
        """Initialize the locator.

        Args:
            skill_dir: Path to skill directory. Defaults to .claude/skills/.
        """
        self.skill_dir = skill_dir or get_default_skill_dir()

    def find_skill_dirs(self) -> list[Path]:
        """Find all skill directories containing SKILL.md.

        Returns:
            List of paths to skill directories, sorted by name.
        """
        if not self.skill_dir.exists():
            return []

        dirs: list[Path] = []
        for item in self.skill_dir.iterdir():
            if item.is_dir() and (item / SKILL_MD_FILENAME).exists():
                dirs.append(item)

        return sorted(dirs, key=lambda p: p.name)

    def load_skill(self, name: str) -> Skill | None:
        """Load a skill by name.

        Args:
            name: Skill name (directory name).

        Returns:
            Parsed Skill object, or None if not found.
        """
        skill_path = self.skill_dir / name / SKILL_MD_FILENAME
        if not skill_path.exists():
            return None

        return parse_skill(skill_path)

    def load_all_skills(self) -> list[Skill]:
        """Load all skills from the skill directory.

        Returns:
            List of parsed Skill objects, sorted by name.
        """
        skills: list[Skill] = []
        for skill_dir in self.find_skill_dirs():
            skill_path = skill_dir / SKILL_MD_FILENAME
            try:
                skill = parse_skill(skill_path)
                skills.append(skill)
            except Exception:  # noqa: S112 -- best-effort skill loading, skip unparseable
                continue

        return skills

    def group_by_lifecycle(self, skills: list[Skill]) -> dict[str, list[Skill]]:
        """Group skills by their lifecycle.

        Args:
            skills: List of skills to group.

        Returns:
            Dictionary mapping lifecycle name to list of skills.
        """
        grouped: dict[str, list[Skill]] = defaultdict(list)
        for skill in skills:
            lifecycle = skill.lifecycle or "unknown"
            grouped[lifecycle].append(skill)

        return dict(grouped)


def list_skills(
    skill_dir: Path | None = None,
    project_root: Path | None = None,
    *,
    agent_config: AgentConfig | None = None,
) -> list[Skill]:
    """Convenience function to list all skills.

    Args:
        skill_dir: Direct path to skill directory.
        project_root: Project root (resolves via agent_config).
        agent_config: Agent configuration. Defaults to Claude.

    Returns:
        List of parsed Skill objects.
    """
    if skill_dir is None and project_root is not None:
        skill_dir = get_default_skill_dir(project_root, agent_config=agent_config)

    locator = SkillLocator(skill_dir)
    return locator.load_all_skills()
