---
story_id: "S249.2"
title: "story-plan v1.1 — SDLD Task Blueprints"
epic_ref: "RAISE-249"
complexity: "moderate"
status: "draft"
---

# Design: story-plan v1.1 — SDLD Task Blueprints

## 1. What & Why

**Problem:** story-plan v1.0 produces generic tasks ("Description + Files + TDD Cycle") that leave the implementer to make design decisions: which function to write, what signature, what test to create, which AC it satisfies. The grounding detail from story-design's Contract 4 (Gemba, Target Interfaces) is lost in translation.

**Value:** SDLD Task Blueprints make implementation mechanical — each task contains the exact test to write (RED), the exact function to implement (GREEN), the file paths, and which AC scenario it satisfies. Zero design decisions during story-implement.

## 2. Approach

Restructure Step 2 (Decompose into Tasks) to produce RED/GREEN paired tasks that consume Contract 4 directly. Add a Traceability Table linking tasks to AC scenarios. Add a depth heuristic so XS/S stories get lighter blueprints.

**Components affected:**
- `.claude/skills/rai-story-plan/SKILL.md` — modify (restructure Step 2, update template, add traceability)

## 3. Gemba: Current State

| File | Current Interface | What Changes | What Stays |
|------|------------------|--------------|------------|
| `rai-story-plan/SKILL.md` | Step 2: generic task structure (Description, Files, TDD Cycle one-liner, Verification, Size, Dependencies) | RED/GREEN paired sections with signatures + test specs; depth heuristic; traceability table | Steps 0-0.6 (prereqs, context loading), Step 3 (dependencies), Step 4 (ordering), Step 5 (verification), Steps 6-7 (document + telemetry), Final Integration Test pattern |

**Surprises from Gemba:**
- Step 0.1 checks for `design.md` — good, already gates on Contract 4 for moderate/complex
- Plan Template at bottom duplicates the task structure from Step 2 — both must be updated in sync
- `Context` section says "Inputs: User stories + Technical Design" — needs updating to reference Contract 4 explicitly
- Version is `1.0.0` in frontmatter

## 4. Target Interfaces

This is a skill content change (markdown, not code), so "interfaces" = the blueprint format that story-implement consumes.

### Current Task Format (v1.0)
```markdown
### Task N: [Name]
- **Description:** What to do
- **Files:** Files to create/modify
- **TDD Cycle:** RED (write failing test) → GREEN (implement) → REFACTOR
- **Verification:** How to verify completion (test command)
- **Size:** XS/S/M/L
- **Dependencies:** None / Task N
```

### Target Task Format (v1.1 — SDLD Blueprint)
```markdown
### Task N: [descriptive name]

**Objective:** [one sentence — what this task delivers]

**RED — Write Failing Test:**
- **File:** `tests/path/to/test_file.ext`
- **Test function:** `test_descriptive_name`
- **Setup:** [Given — from Gherkin scenario]
- **Action:** [When — from Gherkin scenario]
- **Assertion:** [Then — from Gherkin scenario]
\```
// Test sketch in project language
// Given
[setup]
// When
result = function_under_test(args)
// Then
assert result == expected
\```

**GREEN — Implement:**
- **File:** `src/path/to/module.ext`
- **Function/Class:** [signature from design § Target Interfaces]
\```
// Signature from Contract 4, in project language
function_under_test(param: Type): ReturnType
\```
- **Integration:** [how this connects — from design § Integration Points]

**Verification:**
\```bash
{test_runner} tests/path/to/test_file.ext::test_name -v
\```

**Size:** S
**Dependencies:** None
**AC Reference:** Scenario "name" from story.md / design.md § AC
```

### Depth Heuristic (New)

| Story Size | Blueprint Depth | RED Section | GREEN Section |
|------------|----------------|-------------|---------------|
| XS (1-2 SP) | Lightweight | Test name + assertion only | Function name + file only |
| S (3-5 SP) | Standard | Test sketch (Given/When/Then) | Signature + file + integration |
| M (5-8 SP) | Full SDLD | Full test code sketch | Full signature + imports + integration |
| L (8+ SP) | Full SDLD | Same as M | Same as M (consider splitting story) |

### Traceability Table (New)

```markdown
## Traceability
| AC Scenario | Task(s) | Design § |
|-------------|---------|----------|
| "happy path export" | T1, T2 | Target Interfaces → exportSession |
| "error on missing session" | T3 | Target Interfaces → exportSession (error path) |
```

### Integration Points
- story-implement consumes RED section → writes the exact test shown
- story-implement consumes GREEN section → implements the exact function shown
- story-implement runs Verification command → confirms task done
- Traceability table → enables story-review to verify all ACs are covered

## 5. Acceptance Criteria

- **MUST:** Task format includes RED (test) and GREEN (implement) as separate paired sections
- **MUST:** RED section includes test file, test function name, Given/When/Then, and code sketch (M+ stories)
- **MUST:** GREEN section includes implementation file, function signature from Contract 4, and integration point
- **MUST:** Each task references which AC scenario it satisfies
- **MUST:** Traceability table maps every AC scenario to at least one task
- **MUST:** Depth heuristic adapts blueprint detail to story size (XS/S/M/L)
- **MUST:** All code examples use platform-agnostic patterns (5+ languages) per PAT-E-400
- **SHOULD:** Plan Template section updated to match new format
- **SHOULD:** Context/Inputs section references Contract 4 explicitly
- **MUST NOT:** Change Steps 0-0.6 (prerequisites and context loading)
- **MUST NOT:** Change Steps 3-5 (dependencies, ordering, verification logic)
- **MUST NOT:** Remove the Final Integration Test task pattern

## 6. Constraints

- Pure markdown change — no CLI code
- Must be consumable by story-implement without modification to that skill
- Self-test: produce a sample Contract 5 artifact from S249.1's self-test-contract4.md to verify the format works end-to-end

---

*Design grounded in: Gemba of rai-story-plan/SKILL.md v1.0.0, Contract 5 spec from epic design.md, S249.1 self-test-contract4.md as input reference*
