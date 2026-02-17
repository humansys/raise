"""IDE configuration model and factory.

Defines IDE-specific conventions (paths, file names) as data.
Each supported IDE has a pre-built IdeConfig in the registry.
Factory function returns the config for a given IDE type.

Architecture decision: ADR-031 (IdeConfig pattern).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

IdeType = Literal["claude", "antigravity"]


class IdeConfig(BaseModel):
    """IDE-specific configuration holding convention paths.

    Attributes:
        ide_type: Which IDE this config represents.
        skills_dir: Relative path to skills directory from project root.
        instructions_file: Relative path to instructions/rules file from project root.
        workflows_dir: Relative path to workflows directory (None if IDE has no equivalent).
    """

    model_config = ConfigDict(frozen=True)

    ide_type: IdeType
    skills_dir: str
    instructions_file: str
    workflows_dir: str | None = None


IDE_CONFIGS: dict[IdeType, IdeConfig] = {
    "claude": IdeConfig(
        ide_type="claude",
        skills_dir=".claude/skills",
        instructions_file="CLAUDE.md",
    ),
    "antigravity": IdeConfig(
        ide_type="antigravity",
        skills_dir=".agent/skills",
        instructions_file=".agent/rules/raise.md",
        workflows_dir=".agent/workflows",
    ),
}


def get_ide_config(ide_type: IdeType = "claude") -> IdeConfig:
    """Get the IDE configuration for a given IDE type.

    Args:
        ide_type: The IDE to get config for. Defaults to "claude".

    Returns:
        IdeConfig with paths and conventions for the requested IDE.
    """
    return IDE_CONFIGS[ide_type]
