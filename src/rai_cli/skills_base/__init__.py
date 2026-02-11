"""Base skills package for distribution.

This package contains the RaiSE skills that ship with rai-cli.
On `rai init`, skill files are copied to the project's
`.claude/skills/` directory (Claude Code) or equivalent IDE location.

All skills use the `rai-` namespace prefix to prevent collision
with user-created or third-party skills.

Contents:
    Session lifecycle:  rai-session-start, rai-session-close
    Story lifecycle:    rai-story-start, rai-story-plan, rai-story-design,
                        rai-story-implement, rai-story-review, rai-story-close
    Epic lifecycle:     rai-epic-start, rai-epic-plan, rai-epic-design, rai-epic-close
    Discovery:          rai-discover-start, rai-discover-scan,
                        rai-discover-validate, rai-discover-document
    Onboarding:         rai-project-create, rai-project-onboard
    Tools:              rai-research, rai-debug

Usage:
    from importlib.resources import files

    base_skills = files("rai_cli.skills_base")
    session_start = base_skills / "rai-session-start" / "SKILL.md"
    content = session_start.read_text()
"""

from __future__ import annotations

__version__ = "2.1.0"

DISTRIBUTABLE_SKILLS: list[str] = [
    # Session lifecycle
    "rai-session-start",
    "rai-session-close",
    # Story lifecycle
    "rai-story-start",
    "rai-story-plan",
    "rai-story-design",
    "rai-story-implement",
    "rai-story-review",
    "rai-story-close",
    # Epic lifecycle
    "rai-epic-start",
    "rai-epic-plan",
    "rai-epic-design",
    "rai-epic-close",
    # Discovery
    "rai-discover-start",
    "rai-discover-scan",
    "rai-discover-validate",
    "rai-discover-document",
    # Onboarding
    "rai-project-create",
    "rai-project-onboard",
    # Tools
    "rai-research",
    "rai-debug",
]
