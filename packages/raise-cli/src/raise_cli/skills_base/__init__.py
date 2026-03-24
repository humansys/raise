"""Base skills package for distribution.

This package contains the RaiSE skills that ship with raise-cli.
On `rai init`, skill files are copied to the project's
`.claude/skills/` directory (Claude Code) or equivalent IDE location.

All skills use the `rai-` namespace prefix to prevent collision
with user-created or third-party skills.

Contents:
    Session lifecycle:  rai-session-start, rai-session-close
    Story lifecycle:    rai-story-start, rai-story-plan, rai-story-design,
                        rai-story-implement, rai-story-review, rai-story-close
    Epic lifecycle:     rai-epic-start, rai-epic-plan, rai-epic-design, rai-epic-close
    Discovery:          rai-discover
    Onboarding:         rai-project-create, rai-project-onboard, rai-welcome
    Governance:         rai-docs-update
    MCP:                rai-mcp-add, rai-mcp-remove, rai-mcp-status
    Tools:              rai-research, rai-debug, rai-doctor, rai-problem-shape

Note: Internal skills (rai-framework-sync, rai-publish, rai-skillset-manage,
      rai-bugfix) are excluded from distribution.

Usage:
    from importlib.resources import files

    base_skills = files("raise_cli.skills_base")
    session_start = base_skills / "rai-session-start" / "SKILL.md"
    content = session_start.read_text(encoding="utf-8")
"""

from __future__ import annotations

__version__ = "2.2.0"

DISTRIBUTABLE_SKILLS: list[str] = [
    # Session lifecycle
    "rai-session-close",
    "rai-session-start",
    # Story lifecycle
    "rai-story-close",
    "rai-story-design",
    "rai-story-implement",
    "rai-story-plan",
    "rai-story-review",
    "rai-story-run",
    "rai-story-start",
    # Epic lifecycle
    "rai-epic-close",
    "rai-epic-design",
    "rai-epic-docs",
    "rai-epic-plan",
    "rai-epic-run",
    "rai-epic-start",
    # Onboarding
    "rai-project-create",
    "rai-project-onboard",
    "rai-welcome",
    # Governance
    "rai-docs-update",
    # Tools
    "rai-debug",
    "rai-discover",
    "rai-doctor",
    "rai-mcp-add",
    "rai-mcp-remove",
    "rai-mcp-status",
    "rai-problem-shape",
    "rai-research",
]
