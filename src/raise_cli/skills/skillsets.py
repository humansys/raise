"""Skill set management — create, list, and diff skill sets.

Skill sets live in ``.raise/skills/{name}/`` and contain skill directories
with SKILL.md files. They overlay builtins when deployed with
``rai init --skill-set``.
"""

from __future__ import annotations

import logging
from importlib.resources import files
from pathlib import Path

from pydantic import BaseModel, Field

from raise_cli.config.paths import get_raise_dir
from raise_cli.onboarding.skill_manifest import compute_content_hash
from raise_cli.onboarding.skills import copy_skill_tree

logger = logging.getLogger(__name__)

SKILL_MD_FILENAME = "SKILL.md"


class CreateResult(BaseModel):
    """Result of skill set creation."""

    created: bool
    name: str
    path: str | None = None
    skill_count: int = 0
    error: str | None = None


class SkillSetInfo(BaseModel):
    """Info about an existing skill set."""

    name: str
    path: str
    skill_count: int = 0


class SkillSetDiff(BaseModel):
    """Diff of a skill set against builtins."""

    name: str
    added: list[str] = Field(default_factory=list)
    modified: list[str] = Field(default_factory=list)
    unchanged: list[str] = Field(default_factory=list)


def _skills_dir(project_root: Path) -> Path:
    """Get the .raise/skills/ directory."""
    return get_raise_dir(project_root) / "skills"


def _count_skills(set_dir: Path) -> int:
    """Count skill directories containing SKILL.md."""
    if not set_dir.is_dir():
        return 0
    return sum(
        1 for d in set_dir.iterdir() if d.is_dir() and (d / SKILL_MD_FILENAME).exists()
    )


def create_skill_set(
    name: str,
    project_root: Path,
    *,
    empty: bool = False,
) -> CreateResult:
    """Create a new skill set directory, optionally from builtins.

    Args:
        name: Skill set name (e.g., "my-team").
        project_root: Project root directory.
        empty: If True, create empty directory. Otherwise copy all builtins.

    Returns:
        CreateResult with creation status.
    """
    from raise_cli.onboarding.skills import SkillScaffoldResult
    from raise_cli.skills_base import DISTRIBUTABLE_SKILLS

    set_dir = _skills_dir(project_root) / name

    if set_dir.exists():
        return CreateResult(
            created=False,
            name=name,
            error=f"Skill set '{name}' already exists at {set_dir}",
        )

    set_dir.mkdir(parents=True)

    if empty:
        return CreateResult(created=True, name=name, path=str(set_dir), skill_count=0)

    # Copy builtins
    base = files("raise_cli.skills_base")
    result = SkillScaffoldResult()
    for skill_name in DISTRIBUTABLE_SKILLS:
        source = base / skill_name
        dest = set_dir / skill_name
        copy_skill_tree(source, dest, result, overwrite=True)

    return CreateResult(
        created=True,
        name=name,
        path=str(set_dir),
        skill_count=len(DISTRIBUTABLE_SKILLS),
    )


def list_skill_sets(project_root: Path) -> list[SkillSetInfo]:
    """List all skill sets in .raise/skills/.

    Args:
        project_root: Project root directory.

    Returns:
        List of SkillSetInfo, sorted by name.
    """
    skills_root = _skills_dir(project_root)
    if not skills_root.is_dir():
        return []

    sets: list[SkillSetInfo] = []
    for item in sorted(skills_root.iterdir()):
        if not item.is_dir():
            continue
        sets.append(
            SkillSetInfo(
                name=item.name,
                path=str(item),
                skill_count=_count_skills(item),
            )
        )

    return sets


def diff_skill_set(
    name: str,
    project_root: Path,
) -> SkillSetDiff | None:
    """Compare a skill set against builtins.

    Args:
        name: Skill set name.
        project_root: Project root directory.

    Returns:
        SkillSetDiff with added/modified/unchanged, or None if set doesn't exist.
    """
    from raise_cli.skills_base import DISTRIBUTABLE_SKILLS

    set_dir = _skills_dir(project_root) / name
    if not set_dir.is_dir():
        return None

    base = files("raise_cli.skills_base")
    builtin_names = set(DISTRIBUTABLE_SKILLS)

    added: list[str] = []
    modified: list[str] = []
    unchanged: list[str] = []

    # Check each skill in the set
    for skill_dir in sorted(set_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / SKILL_MD_FILENAME
        if not skill_md.exists():
            continue

        skill_name = skill_dir.name

        if skill_name not in builtin_names:
            added.append(skill_name)
            continue

        # Compare against builtin
        set_hash = compute_content_hash(skill_md.read_text(encoding="utf-8"))
        builtin_content = (base / skill_name / SKILL_MD_FILENAME).read_text(
            encoding="utf-8"
        )
        builtin_hash = compute_content_hash(builtin_content)

        if set_hash == builtin_hash:
            unchanged.append(skill_name)
        else:
            modified.append(skill_name)

    return SkillSetDiff(
        name=name,
        added=added,
        modified=modified,
        unchanged=unchanged,
    )
