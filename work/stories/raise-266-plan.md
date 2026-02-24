# Plan: RAISE-266 Contract Chain Lean

**Size:** M | **Tasks:** 6 | **Date:** 2026-02-24
**Design:** `raise-266-design.md`

---

## Tasks

### Task 1: Create templates (brief.md, story.md, design.md)

**Objective:** Create the 3 artifact templates that skills will reference.

**Files:**
- Create: `.claude/skills/rai-epic-start/templates/brief.md`
- Create: `.claude/skills/rai-story-start/templates/story.md`
- Create: `.claude/skills/rai-epic-design/templates/design.md`

**Verification:** Templates exist, match RAISE-249 contract formats (lean).

**Size:** S | **Dependencies:** None

---

### Task 2: `rai-epic-design` — trim + chain (RISK-FIRST)

**Objective:** Get from 164→≤150 lines while adding brief.md input + design.md output.

**Changes:**
- Step 1: +1 line (check for `brief.md`)
- Step 5: +2 lines (produce `design.md` alongside `scope.md`)
- Output table: +1 line (design.md row)
- Trim: ShuHaRi, Context, Step 1 heuristics, Step 3 heuristics, Step 4 risk placeholder

**Files:** Modify `.claude/skills/rai-epic-design/SKILL.md`

**Verification:** `wc -l` ≤ 150. Reads brief.md. Produces scope.md + design.md.

**Size:** M | **Dependencies:** Task 1 (template exists)

---

### Task 3: `rai-epic-start` — add brief.md artifact

**Objective:** Step 3 produces `brief.md` alongside `scope.md`.

**Changes:**
- Step 3: +4 lines (create brief.md using template)
- Output table: +1 line

**Files:** Modify `.claude/skills/rai-epic-start/SKILL.md`

**Verification:** `wc -l` ≤ 150. Step 3 references brief.md template.

**Size:** S | **Dependencies:** Task 1

---

### Task 4: `rai-story-start` — add story.md artifact

**Objective:** Step 3 produces `story.md` alongside `scope.md`.

**Changes:**
- Step 3: +5 lines (create story.md using template)
- Output table: +1 line

**Files:** Modify `.claude/skills/rai-story-start/SKILL.md`

**Verification:** `wc -l` ≤ 150. Step 3 references story.md template.

**Size:** S | **Dependencies:** Task 1

---

### Task 5: `rai-story-design` — consume story.md

**Objective:** Read story.md AC as input; reference instead of generating from scratch.

**Changes:**
- Context Inputs: mention story.md
- Step 2: +2 lines (load story.md User Story)
- Step 5: +2 lines (reference story.md Gherkin AC)

**Files:** Modify `.claude/skills/rai-story-design/SKILL.md`

**Verification:** `wc -l` ≤ 150. Steps 2+5 reference story.md.

**Size:** XS | **Dependencies:** Task 1

---

### Task 6: `rai-story-plan` — AC traceability + integration verification

**Objective:** Task descriptions reference story.md AC scenarios. Verify full chain.

**Changes:**
- Step 2 "Per task" list: +1 line (AC scenario ref from story.md)

**Verification:**
- `wc -l` ≤ 150 for all 5 skills
- Chain is complete: epic-start→epic-design→story-start→story-design→story-plan
- All templates exist and are referenced

**Size:** XS | **Dependencies:** Tasks 2-5

---

## Execution Order

```
Task 1 (templates) ─────────────────────────────┐
  ├──→ Task 2 (epic-design, RISK-FIRST)         │
  ├──→ Task 3 (epic-start)      ← parallel      │
  ├──→ Task 4 (story-start)     ← parallel      │
  ├──→ Task 5 (story-design)    ← parallel      │
  └──→ Task 6 (story-plan + integration verify)  │
```

Tasks 2-5 are independent after Task 1. In practice sequential, but any order works.

**Rationale:** Task 2 first after templates because it's the riskiest (over-budget trim).

## Duration Tracking

| Task | Size | Estimated | Actual | Notes |
|------|:----:|:---------:|:------:|-------|
| 1. Templates | S | 10 min | | |
| 2. epic-design | M | 15 min | | |
| 3. epic-start | S | 5 min | | |
| 4. story-start | S | 5 min | | |
| 5. story-design | XS | 5 min | | |
| 6. story-plan + verify | XS | 5 min | | |
| **Total** | | **45 min** | | |
