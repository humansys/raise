# Feature Scope: F128.2 — Decouple Init from Claude Paths

> **Epic:** RAISE-128 (IDE Integration)
> **Size:** M
> **Depends on:** F128.1 (Done)
> **Phase:** design

---

## In Scope

Refactor 5 coupling points to use `IdeConfig` instead of hardcoded `.claude/` paths:

| # | File | What |
|---|------|------|
| 1 | `onboarding/skills.py` | `scaffold_skills()` → use `IdeConfig.skills_dir` |
| 2 | `onboarding/claudemd.py` | `ClaudeMdGenerator` → IDE-agnostic naming + path |
| 3 | `config/paths.py` | `get_claude_memory_path()` → use `IdeConfig.memory_path` |
| 4 | `skills/locator.py` | `get_default_skill_dir()` → use `IdeConfig.skills_dir` |
| 5 | `context/builder.py` | `load_skills()` → use `IdeConfig.skills_dir` |

- Backward compatibility: `rai init` (no `--ide` flag) produces identical output
- All existing tests continue to pass
- New tests for each refactored coupling point

## Out of Scope

- Coupling point #6 (`cli/commands/init.py` orchestration) → F128.4
- Antigravity-specific scaffolding → F128.3
- `--ide` CLI flag wiring → F128.4
- Renaming `ClaudeMdGenerator` class → cosmetic, defer unless design requires it
- Memory path for Antigravity (N/A per epic scope)

## Done Criteria

- [ ] All 5 coupling points consume `IdeConfig` instead of hardcoded strings
- [ ] `rai init` output is identical to pre-refactor (backward compat)
- [ ] Unit tests for each refactored module (>90% coverage)
- [ ] Quality gates pass (ruff, pyright, bandit)
- [ ] Retrospective complete
