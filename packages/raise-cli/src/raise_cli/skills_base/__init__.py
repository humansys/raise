"""Base skills package for distribution.

This package contains the RaiSE skills that ship with raise-cli.
On `rai init`, skill files are copied to the project's
`.claude/skills/` directory (Claude Code) or equivalent IDE location.

All skills use the `rai-` namespace prefix to prevent collision
with user-created or third-party skills.

Contents:
    Session lifecycle:  rai-session-start, rai-session-close, rai-session-diary
    Story lifecycle:    rai-story-start, rai-story-plan, rai-story-design,
                        rai-story-implement, rai-story-review, rai-story-close,
                        rai-story-run
    Epic lifecycle:     rai-epic-start, rai-epic-plan, rai-epic-design,
                        rai-epic-docs, rai-epic-run, rai-epic-close
    Bugfix lifecycle:   rai-bugfix-start, rai-bugfix-triage, rai-bugfix-analyse,
                        rai-bugfix-plan, rai-bugfix-fix, rai-bugfix-review,
                        rai-bugfix-close, rai-bugfix-run
    Discovery:          rai-discover
    Onboarding:         rai-project-create, rai-project-onboard, rai-welcome
    Governance:         rai-docs-update
    MCP:                rai-mcp-add, rai-mcp-remove, rai-mcp-status
    Tools:              rai-research, rai-debug, rai-doctor, rai-problem-shape,
                        rai-adapter-setup

Note: Internal skills (rai-framework-sync, rai-publish, rai-skillset-manage,
      rai-sonarqube, rai-code-audit, rai-quality-review, rai-architecture-review)
      are excluded from distribution.

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
    "rai-session-diary",
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
    "rai-adapter-setup",
    "rai-architecture-review",
    "rai-bugfix-analyse",
    "rai-bugfix-close",
    "rai-bugfix-fix",
    "rai-bugfix-plan",
    "rai-bugfix-review",
    "rai-bugfix-run",
    "rai-bugfix-start",
    "rai-bugfix-triage",
    "rai-debug",
    "rai-discover",
    "rai-doctor",
    "rai-mcp-add",
    "rai-mcp-remove",
    "rai-mcp-status",
    "rai-problem-shape",
    "rai-quality-review",
    "rai-research",
] = [
    # Session lifecycle
    "rai-session-close",
    "rai-session-diary",
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
    # Bugfix lifecycle
    "rai-bugfix-analyse",
    "rai-bugfix-close",
    "rai-bugfix-fix",
    "rai-bugfix-plan",
    "rai-bugfix-review",
    "rai-bugfix-run",
    "rai-bugfix-start",
    "rai-bugfix-triage",
    # Onboarding
    "rai-project-create",
    "rai-project-onboard",
    "rai-welcome",
    # Governance
    "rai-docs-update",
    # Tools
    "rai-adapter-setup",
    "rai-architecture-review",
    "rai-debug",
    "rai-discover",
    "rai-doctor",
    "rai-mcp-add",
    "rai-mcp-remove",
    "rai-mcp-status",
    "rai-problem-shape",
    "rai-quality-review",
    "rai-research",
]
