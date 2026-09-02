"""Base skills package for distribution.

This package contains the RaiSE skills that ship with raise-cli.
On `rai init`, skill files are copied to the project's
`.claude/skills/` directory (Claude Code) or equivalent IDE location.

All skills use the `rai-` namespace prefix to prevent collision
with user-created or third-party skills.

RaiSE ships two skillsets:
- **Default skillset** (no suffix): lean ceremony, fast turnaround. Use when scope
  is known, no human review gates needed. E.g. `rai-bugfix-start`.
- **Enterprise skillset** (`-enterprise` suffix): full ceremony, compliance-grade.
  Use when human reviewers, ADRs, or governance audit trails are required.
  E.g. `rai-bugfix-start-enterprise`.

Contents:
    Session lifecycle:  rai-session-start, rai-session-close, rai-session-diary
    Story lifecycle:    rai-story-design, rai-story-implement, rai-story-plan,
                        rai-story-review
    Story default:      rai-story-start, rai-story-close
    Story enterprise:   rai-story-start-enterprise, rai-story-close-enterprise
    Story lean:         (colapsados en rai-story-start/close — ADR-143 B1+B2)
    Epic lifecycle:     rai-epic-ux-design, rai-epic-plan, rai-epic-docs,
                        rai-epic-journal
    Epic default:       rai-epic-start, rai-epic-design, rai-epic-close
    Epic enterprise:    rai-epic-start-enterprise, rai-epic-design-enterprise,
                        rai-epic-close-enterprise
    Bugfix lifecycle:   rai-bugfix-triage, rai-bugfix-analyse, rai-bugfix-plan,
                        rai-bugfix-review, rai-bugfix-pir
    Bugfix default:     rai-bugfix-start, rai-bugfix-fix, rai-bugfix-close
    Bugfix enterprise:  rai-bugfix-start-enterprise, rai-bugfix-fix-enterprise,
                        rai-bugfix-close-enterprise
    Bugfix lean:        rai-bugfix-start-lean, rai-bugfix-fix-lean,
                        rai-bugfix-close-lean (ADR-134 v2 lean residues)
    Initiative default: rai-initiative-shaped, rai-initiative-delivering
    Pipeline:           rai-pipeline-run
    Discovery:          rai-discover
    Onboarding:         rai-project-create, rai-project-onboard, rai-welcome
    Governance:         rai-docs-update
    Meta:               rai-skill-create, rai-skillset-manage
    MCP:                rai-mcp-add, rai-mcp-remove, rai-mcp-status
    Tools:              rai-research, rai-debug, rai-doctor, rai-problem-shape,
                        rai-backlog-setup, rai-docs-setup, rai-docs-setup-advanced,
                        rai-architecture-review, rai-quality-review

Skillset manifests:
    Stored under ``skillsets/`` (not in DISTRIBUTABLE_SKILLS, which lists individual skills only).
    ``skillsets/enterprise.yaml`` — the 8 enterprise skill variants as a named set.
    Project-level copy: ``.raise/skillsets/enterprise.yaml``
    See docs/lean-pipeline-guide.md — "Switching to Enterprise Skillset".

Note: Internal skills (rai-framework-sync, rai-publish, rai-sonarqube,
      rai-code-audit) and deprecated runbook skills
      (rai-story-run, rai-epic-run, rai-bugfix-run, rai-adapter-setup) are excluded from
      distribution.

Usage:
    from importlib.resources import files

    base_skills = files("raise_cli.skills_base")
    session_start = base_skills / "rai-session-start" / "SKILL.md"
    content = session_start.read_text(encoding="utf-8")
"""

from __future__ import annotations

__version__ = "3.0.0a1"

DEPRECATED_SKILLS: list[str] = [
    "rai-story-run",
    "rai-epic-run",
    "rai-bugfix-run",
    "rai-adapter-setup",
    "rai-pipeline-run-lean",
]


DISTRIBUTABLE_SKILLS: list[str] = [
    # Session lifecycle
    "rai-session-close",
    "rai-session-diary",
    "rai-session-start",
    # Story lifecycle
    "rai-story-close",
    "rai-story-close-enterprise",
    "rai-story-design",
    "rai-story-implement",
    "rai-story-plan",
    "rai-story-review",
    "rai-story-start",
    "rai-story-start-enterprise",
    # Epic lifecycle
    "rai-epic-close",
    "rai-epic-close-enterprise",
    "rai-epic-design",
    "rai-epic-design-enterprise",
    "rai-epic-docs",
    "rai-epic-journal",
    "rai-epic-plan",
    "rai-epic-predesign-evidence",
    "rai-epic-start",
    "rai-epic-start-enterprise",
    "rai-epic-ux-design",
    # Bugfix lifecycle
    "rai-bugfix-analyse",
    "rai-bugfix-close",
    "rai-bugfix-close-enterprise",
    "rai-bugfix-close-lean",
    "rai-bugfix-fix",
    "rai-bugfix-fix-enterprise",
    "rai-bugfix-fix-lean",
    "rai-bugfix-pir",
    "rai-bugfix-plan",
    "rai-bugfix-review",
    "rai-bugfix-start",
    "rai-bugfix-start-enterprise",
    "rai-bugfix-start-lean",
    "rai-bugfix-triage",
    # Discovery
    "rai-discover",
    # Onboarding
    "rai-project-create",
    "rai-project-onboard",
    "rai-welcome",
    # Governance
    "rai-docs-update",
    # Meta
    "rai-skill-create",
    "rai-skillset-manage",
    # MCP
    "rai-mcp-add",
    "rai-mcp-remove",
    "rai-mcp-status",
    # Worktree
    "rai-worktree-close",
    "rai-worktree-open",
    # Tools
    "rai-adversarial-review",
    "rai-architecture-review",
    "rai-backlog-setup",
    "rai-bug-file",
    "rai-cartridge-agent",
    "rai-corpus-curate",
    "rai-debug",
    "rai-docs-setup",
    "rai-docs-setup-advanced",
    "rai-doctor",
    "rai-initiative-delivering",
    "rai-initiative-shaped",
    "rai-kc-build",
    "rai-mr-create",
    "rai-mr-merge",
    "rai-onboard-repo",
    "rai-pipeline-run",
    "rai-problem-shape",
    "rai-project-upgrade",
    "rai-quality-review",
    "rai-research",
    "rai-research-critic",
    "rai-research-evidence",
    "rai-research-frame",
    "rai-research-run",
    "rai-research-scope",
    "rai-research-search",
    "rai-research-synthesize",
    "rai-research-verify",
    "rai-spike-close",
    "rai-spike-journal",
    "rai-spike-start",
]
