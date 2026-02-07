"""Base skills package for distribution.

This package contains the onboarding skills that ship with raise-cli.
On `raise init`, these SKILL.md files are copied to the project's
`.claude/skills/` directory (Claude Code) or equivalent IDE location.

Contents:
    session-start/      Session lifecycle skill
    discover-start/     Codebase discovery initialization
    discover-scan/      Symbol extraction and synthesis
    discover-validate/  Human validation of components
    discover-complete/  Export to graph format

Usage:
    from importlib.resources import files

    base_skills = files("raise_cli.skills_base")
    session_start = base_skills / "session-start" / "SKILL.md"
    content = session_start.read_text()
"""

from __future__ import annotations

__version__ = "1.0.0"

DISTRIBUTABLE_SKILLS: list[str] = [
    "session-start",
    "discover-start",
    "discover-scan",
    "discover-validate",
    "discover-complete",
]
