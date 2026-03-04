# E346: Skill Lifecycle Hardening — Design

## Gemba Summary

Audited 5 skills on 2026-03-02. Key findings:

| Skill | Builtin | Deployment | Language Bias |
|-------|---------|------------|---------------|
| `/rai-epic-run` | yes | yes (identical) | None |
| `/rai-story-run` | yes | yes (identical) | None |
| `/rai-story-review` | yes | yes (identical) | Python (pytest hardcoded) |
| `/rai-architecture-review` | **NO** | yes | None (generic heuristics) |
| `/rai-quality-review` | **NO** | yes | **Heavy** (*.py filter, pytest, type:ignore, except) |

### Orchestrator Flow (current, already correct)

```
epic-run:  start → design → AR(epic) → plan → [story-run iterations] → close
story-run: start → design → plan → implement → AR(story) → QR → story-review → close
```

Both orchestrators already integrate review skills with hard gates:
- AR SIMPLIFY → blocks all delegation levels
- QR FAIL → blocks all delegation levels

### Python Bias in quality-review (Step-by-step)

1. **Step 1:** `git diff ... -- '*.py'` — filters only Python files
2. **Step 2:** `type: ignore`, `cast()`, `except Exception`, `raise X from exc`
3. **Step 3:** Test heuristics reference pytest patterns
4. **Step 4:** `__all__`, `_`-prefix conventions

### Python Bias in story-review

1. **Step 1:** `uv run pytest --tb=short` hardcoded
2. **Step 5:** `rai signal emit-calibration` — not Python-specific but uses uv

## Design Decisions

### D1: Keep skill names as-is

quality-review covers more than "code review" (semantic bugs, test quality, API surface, security). The name is accurate. architecture-review is already the canonical name.

### D2: Genericize via language detection

Quality-review should detect project language from `.raise/manifest.yaml` (field: `project.languages` or file extensions) and adapt:
- File filter: `*.py` → language-appropriate extensions
- Semantic checks: language-appropriate patterns (e.g., unchecked casts in TS, null safety in C#)
- Test checks: framework-appropriate (pytest → jest/vitest/xunit)
- API surface: language-appropriate idioms

**Approach:** Replace hardcoded Python examples with a language-adaptive section that provides equivalent checks per detected language. Keep the 7 test heuristics (they're universal) but change the examples.

### D3: Promote to builtin

AR and QR move to `src/rai_cli/skills_base/` following the established pattern:
1. Create `src/rai_cli/skills_base/{name}/SKILL.md`
2. Copy content from `.claude/skills/{name}/SKILL.md`
3. Verify with diff that both are identical
4. Register in skill manifests if needed

## Target Components

| Component | Change |
|-----------|--------|
| `.claude/skills/rai-quality-review/SKILL.md` | Genericize language references |
| `.claude/skills/rai-story-review/SKILL.md` | Remove pytest hardcoding |
| `src/rai_cli/skills_base/rai-quality-review/SKILL.md` | Create (promote from deployment) |
| `src/rai_cli/skills_base/rai-architecture-review/SKILL.md` | Create (promote from deployment) |
| `src/rai_cli/skills_base/rai-story-review/SKILL.md` | Update (sync after genericize) |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Genericized QR loses Python-specific value | Medium | Medium | Keep Python as first-class example, add others alongside |
| Language detection unreliable | Low | Low | Fall back to file extension scanning if manifest missing |
| Builtin/deployment drift after promote | Low | High | Diff verification in S346.4, add to quality checklist |
