# Feature Scope: F128.3 — Antigravity Scaffolding

> **Epic:** RAISE-128 (IDE Integration)
> **Size:** S
> **Depends on:** F128.2 (Done)
> **Phase:** design

---

## In Scope

Generate Antigravity-specific project structure when `ide_config` is antigravity:

| # | Output | Description |
|---|--------|-------------|
| 1 | `.agent/skills/` | Skill SKILL.md files scaffolded to Antigravity conventions |
| 2 | `.agent/rules/raise.md` | Instructions file (equivalent to CLAUDE.md) |
| 3 | `.agent/workflows/*.md` | Workflow shims for user-triggered skills (slash command equivalents) |

- Uses `IdeConfig` from F128.1 and decoupled functions from F128.2
- Skills content is IDE-agnostic (already proven in F128.2) — only paths change
- Backward compatibility: existing Claude scaffolding unchanged

## Out of Scope

- `--ide` CLI flag wiring → F128.4
- End-to-end `rai init --ide antigravity` integration → F128.4
- Gemini CLI support → future story
- Memory path for Antigravity → N/A per epic scope
- Migration of existing projects → parking lot

## Done Criteria

- [ ] `scaffold_skills()` with antigravity config produces `.agent/skills/` structure
- [ ] Instructions file generated at `.agent/rules/raise.md`
- [ ] Workflow shims generated in `.agent/workflows/`
- [ ] All existing Claude scaffolding tests pass unchanged
- [ ] New tests for Antigravity scaffolding paths
- [ ] Quality gates pass (ruff, pyright, bandit, >90% coverage)
- [ ] Retrospective complete
