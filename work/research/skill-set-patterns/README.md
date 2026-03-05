# Research: Skill Set Management Patterns

> Status: Complete
> Date: 2026-03-02
> Decision: Skill ecosystem architecture for RaiSE v2.2

## Contents

- `skill-set-patterns-report.md` — Main report with recommendation
- `sources/evidence-catalog.md` — 14 projects, 30+ sources with evidence levels

## Quick Summary

Researched 7 established OSS tools (ESLint, Prettier, Ansible, Terraform, Helm,
Oh My Zsh, Copier) and 7 AI coding tools (Cursor, Copilot, Windsurf, Cline,
Roo Code, Aider, Continue.dev).

**Recommendation:** Oh My Zsh + Helm hybrid model.
- `.raise/skills/default/` = builtin set (structural separation)
- `.raise/skills/{name}/` = team sets (same-name = custom wins)
- `.claude/skills/` = deployment target (derived)
- `rai init --skill-set X` = set selection
- Named skill sets = market differentiator (no AI tool has this)
