# Plan: RAISE-243 — rai-skill-create ADR-040 Compliance

> **Story:** RAISE-243 | **Size:** S | **Date:** 2026-02-26
> **Branch:** `story/raise-243/adr040-compliance`
> **Design:** `raise-243-adr040-design.md`

---

## Tasks

### T1: Rewrite SKILL.md to ADR-040 contract

**What:** Refactor `.claude/skills/rai-skill-create/SKILL.md` in-place.

**Transformations:**
1. Replace `## Notes` with `## Quality Checklist` (penultimate section)
2. Compress 9 steps → ~5 by collapsing sub-steps into decision tables
3. Replace all prose conditionals with markdown tables
4. Fix CLI commands: `rai memory *` → `rai graph/pattern/signal *`
5. Preserve graph indexing step: `rai graph build` + `rai graph query`
6. Remove philosophy paragraphs from Notes/body

**Target structure:**
```
# Skill Create
## Purpose
## Mastery Levels (ShuHaRi)
## Context
## Steps
## Output
## Quality Checklist
## References
```

**CLI command mapping:**
| Before | After |
|--------|-------|
| `rai memory build` | `rai graph build` |
| `rai memory query` | `rai graph query` |
| `rai memory context` | `rai graph context` |
| `rai memory add-pattern` | `rai pattern add` |
| `rai memory emit-work` | `rai signal emit-work` |

**Verification:**
```bash
wc -l .claude/skills/rai-skill-create/SKILL.md    # ≤150 (body lines)
grep -c "rai memory" .claude/skills/rai-skill-create/SKILL.md  # 0
grep "^## " .claude/skills/rai-skill-create/SKILL.md  # exactly 7 sections
grep "rai graph build" .claude/skills/rai-skill-create/SKILL.md  # present
```

**Size:** M | **Depends on:** — (first task)

---

### T2: Validate and verify

**What:** Run all acceptance criteria checks.

**Verification sequence:**
```bash
# AC1: Validator passes
rai skill validate .claude/skills/rai-skill-create/SKILL.md

# AC2: Graph indexing works
rai graph build
rai graph query "skill-create" --types skill --format compact
```

**Expected:**
- `rai skill validate` exits 0, all checks passed
- `rai graph query` returns the skill in results

**Size:** XS | **Depends on:** T1

---

## Execution Order

```
T1 (Rewrite) → T2 (Validate)
```

Rationale: T1 is the risk (can everything fit in ≤150 lines?). T2 is the gate.

---

## Risks

| Risk | Mitigation |
|------|------------|
| Content can't compress to ≤150 without losing function | Check ADR-040 escape valve (≤200 for top-3 complex skills). rai-skill-create qualifies as complex — use 200 if needed |
| Validate fails on section order | Read contract-template.md section order before writing |
| Graph indexing step gets lost in compression | Explicit checklist item: verify `rai graph build` present before committing |

---

## Duration Tracking

| Task | Estimated | Actual | Notes |
|------|-----------|--------|-------|
| T1 | 20 min | — | |
| T2 | 5 min | — | |
| **Total** | **25 min** | — | |
