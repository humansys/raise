"""Skills module for RaiSE skill management.

Skills are AI-executed process guides that leverage the RaiSE toolkit.
This module provides:
- Schema models for SKILL.md parsing
- Parser for extracting frontmatter and body
- Locator for finding skills in the codebase
- Validator for checking skill compliance
- Naming utilities for ontology compliance
- Scaffold for generating new skills
"""

from __future__ import annotations

from raise_cli.skills.locator import (
    SkillLocator,
    get_default_skill_dir,
    list_skills,
)
from raise_cli.skills.parser import ParseError, parse_frontmatter, parse_skill
from raise_cli.skills.schema import (
    Skill,
    SkillFrontmatter,
    SkillHook,
    SkillHookCommand,
    SkillMetadata,
)

__all__ = [
    # Schema
    "Skill",
    "SkillFrontmatter",
    "SkillHook",
    "SkillHookCommand",
    "SkillMetadata",
    # Parser
    "ParseError",
    "parse_frontmatter",
    "parse_skill",
    # Locator
    "SkillLocator",
    "get_default_skill_dir",
    "list_skills",
]
