# Implementation Plan: RAISE-244 rai-bugfix

> **Story:** RAISE-244
> **Size:** S
> **Design:** `raise-244-design.md`
> **Date:** 2026-02-27

---

## Overview

One skill created via `rai-skill-create`. Risk-first: gate validates the creator before touching the filesystem. Single commit per task.

**Skill creation cycle:**
- **RED**: `rai skill check-name rai-bugfix` — valid name confirmed before scaffold
- **GREEN**: `/rai-skill-create` → fill all 6 phases → `rai skill validate` passes
- **REFACTOR**: verify cross-references (story counterparts, phase chain, ShuHaRi section)

---

## Tasks

### T1 — Gate + create `rai-bugfix` _(S, no deps)_

**Steps:**
1. Gate: `rai skill validate .claude/skills/rai-skill-create/SKILL.md` — must pass cleanly (risk-first)
2. `rai skill check-name rai-bugfix` — confirm valid (advisory warning on domain expected)
3. `/rai-skill-create` with:
   - Name: `rai-bugfix`
   - Domain: `bug` (new lifecycle domain — advisory expected)
   - `work_cycle: bug`, `fase: 1-6` (single skill, full lifecycle)
   - `prerequisites: ""`, `next: ""`
   - Purpose: guide developer through 6-phase bug fix lifecycle mirroring story cycle
   - 6 Steps with `<verification>` gates — see design for phase detail
   - ShuHaRi section
   - Output table (scope, analysis, plan, code, retro, merge)
4. `rai skill validate .claude/skills/rai-bugfix/SKILL.md` — must pass
5. Commit: `feat(RAISE-244): add rai-bugfix — 6-phase lifecycle mirroring story cycle`

**Files created:**
- `.claude/skills/rai-bugfix/SKILL.md`

**Verification:**
- `rai skill validate` exits 0
- 6 Steps present, each with `<verification>` block
- Each step references story counterpart explicitly

---

### T2 — Integration test + friction documentation _(XS, after T1)_

**Steps:**
1. Read the generated SKILL.md — spot-check: phase chain intact, story counterparts named, Step 2 mentions `/rai-debug`
2. Confirm `rai skill validate` clean (no errors, no warnings beyond domain advisory)
3. Document any friction from `rai-skill-create` run in `raise-244-retro.md` (created during `/rai-story-review`)
4. If any friction → consider `rai pattern add` (deferred to review phase)
5. Commit: `chore(RAISE-244): integration validation — rai-bugfix passes validate`

**Verification:**
- SKILL.md reads coherently end-to-end
- All 6 phases produce named artifacts
- No broken references

---

## Execution Order

```
T1 (gate + create rai-bugfix)
    ↓
T2 (integration check)
```

Linear. T2 depends on T1 output.

---

## Risks

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| `rai-skill-create` friction during fill | Medium | Document in retro; do not patch RAISE-243 in this story |
| Generated phases too thin (no `<verification>` blocks) | Low | T2 spot-check catches before close |
| `rai-bug-analyse` step duplicates `rai-debug` content | Low | Explicit note in Step 2: delegate, don't replicate |

---

## Duration Tracking

| Task | Planned | Actual | Notes |
|------|---------|--------|-------|
| T1 — gate + rai-bugfix | — | | |
| T2 — integration check | — | | |
| **Total** | — | | |
