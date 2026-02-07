"""Base skills package for distribution.

This package contains the RaiSE skills that ship with raise-cli.
On `raise init`, skill files are copied to the project's
`.claude/skills/` directory (Claude Code) or equivalent IDE location.

Contents:
    Session lifecycle:  session-start, session-close
    Story lifecycle:    story-start, story-plan, story-design,
                        story-implement, story-review, story-close
    Epic lifecycle:     epic-start, epic-plan, epic-design, epic-close
    Discovery:          discover-start, discover-scan,
                        discover-validate, discover-complete
    Tools:              research, debug

Usage:
    from importlib.resources import files

    base_skills = files("raise_cli.skills_base")
    session_start = base_skills / "session-start" / "SKILL.md"
    content = session_start.read_text()
"""

from __future__ import annotations

__version__ = "2.0.0"

DISTRIBUTABLE_SKILLS: list[str] = [
    # Session lifecycle
    "session-start",
    "session-close",
    # Story lifecycle
    "story-start",
    "story-plan",
    "story-design",
    "story-implement",
    "story-review",
    "story-close",
    # Epic lifecycle
    "epic-start",
    "epic-plan",
    "epic-design",
    "epic-close",
    # Discovery
    "discover-start",
    "discover-scan",
    "discover-validate",
    "discover-complete",
    # Tools
    "research",
    "debug",
]
