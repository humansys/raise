# Implementation Plan: RAISE-567

> **Story:** rai-bugfix: add structured retrospective to review phase
> **Size:** XS
> **Date:** 2026-03-17
> **Branch:** `story/raise-567/bugfix-retrospective`

---

## Overview

Single-file edit: update `.claude/skills/rai-bugfix/SKILL.md` Step 5 (Review) to add a structured retrospective mirroring `rai-story-review` Steps 2–4. No source code changes — validation is `rai skill validate`.

---

## Tasks

### T1: Update Step 5 (Review) in SKILL.md

**Description:** Replace the thin Step 5 content with a full retrospective structure:
1. Heutagogical checkpoint (4 questions, same as rai-story-review Step 2)
2. `rai pattern add "..." --context "..." --type process --scope project --from RAISE-{N}`
3. `rai pattern reinforce {id} --vote {1|0|-1} --from RAISE-{N}` with vote table
4. Structured `retro.md` format: summary, checkpoint answers, patterns added/reinforced

**File:** `.claude/skills/rai-bugfix/SKILL.md`

**TDD note:** Skill files have no test suite. Validation gate is `rai skill validate`. Write content → validate → done.

**Verification:**
```bash
conda run -n rai-dev rai skill validate .claude/skills/rai-bugfix/SKILL.md
```

**Size:** XS | **Depends on:** —

---

### T2: Update Quality Checklist

**Description:** Add "NEVER skip pattern reinforce" gate to the Quality Checklist section.

**File:** `.claude/skills/rai-bugfix/SKILL.md` (same file, separate logical unit)

**Note:** Folded into T1 commit since it's the same file — listed separately for clarity.

**Verification:** same as T1

**Size:** XS | **Depends on:** T1

---

## Execution Order

```
T1 (Step 5 content) → T2 (checklist) → single commit → validate
```

Both tasks fold into one commit since they touch the same file.

---

## Risks

| Risk | Mitigation |
|------|-----------|
| `rai skill validate` fails on structural change | Read current passing structure before editing; preserve required sections |

---

## Duration Tracking

| Task | Started | Completed | Notes |
|------|---------|-----------|-------|
| T1+T2 | — | — | |
