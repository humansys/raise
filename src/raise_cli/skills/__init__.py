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

from raise_cli.skills.schema import (
    Skill,
    SkillFrontmatter,
    SkillHook,
    SkillHookCommand,
    SkillMetadata,
)

__all__ = [
    "Skill",
    "SkillFrontmatter",
    "SkillHook",
    "SkillHookCommand",
    "SkillMetadata",
]
