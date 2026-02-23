# Implementation Plan: S247.6 — Update all skills and generated docs

## Overview
- **Story:** S247.6
- **Size:** M
- **Tasks:** 5
- **Derived from:** design.md § Gemba (stale ref inventory)
- **Created:** 2026-02-23

## Strategy

Batch replacements by command family. Each task = one batch + grep verification.
No TDD — this is documentation-only (no testable behavior).

## Tasks

### Task 1: Replace `rai memory emit-*` → `rai signal emit-*` in skills

**Objective:** Update all telemetry command references across 14 skill files.

**Replacements:**
- `rai memory emit-work` → `rai signal emit-work`
- `rai memory emit-calibration` → `rai signal emit-calibration`
- `rai memory add-calibration` → `rai signal emit-calibration`

**Files:** rai-story-implement, rai-story-design, rai-story-plan, rai-story-start, rai-story-review, rai-story-close, rai-epic-design, rai-epic-plan, rai-epic-start, rai-epic-close, rai-session-close

**Verification:**
```bash
grep -rn "rai memory emit\|rai memory add-calibration" src/rai_cli/skills_base/ | grep -v __pycache__ | wc -l
# Expected: 0
```

**Size:** M
**Dependencies:** None

### Task 2: Replace `rai memory build/query/context` → `rai graph *` in skills

**Objective:** Update all graph command references across 13 skill files.

**Replacements:**
- `rai memory build` → `rai graph build`
- `rai memory query` → `rai graph query`
- `rai memory context` → `rai graph context`

**Files:** rai-discover-validate, rai-discover-document, rai-docs-update, rai-epic-design, rai-epic-plan, rai-project-create, rai-project-onboard, rai-research, rai-session-start, rai-story-design, rai-story-implement, rai-story-plan, rai-welcome

**Verification:**
```bash
grep -rn "rai memory build\|rai memory query\|rai memory context" src/rai_cli/skills_base/ | grep -v __pycache__ | wc -l
# Expected: 0
```

**Size:** M
**Dependencies:** None (parallel with T1)

### Task 3: Replace `rai memory add-pattern/reinforce` → `rai pattern *` in skills

**Objective:** Update pattern management references.

**Replacements:**
- `rai memory add-pattern` → `rai pattern add`
- `rai memory reinforce` → `rai pattern reinforce`

**Files:** rai-story-review (primary — has examples)

**Also fix generic text:**
- `rai memory commands` → `rai graph/pattern/signal commands` (rai-docs-update)
- `rai memory build` in prose → `rai graph build` (project-create, project-onboard descriptions)

**Verification:**
```bash
grep -rn "rai memory" src/rai_cli/skills_base/ | grep -v __pycache__ | wc -l
# Expected: 0
```

**Size:** S
**Dependencies:** After T1+T2 (T3 catches any stragglers)

### Task 4: Update CLAUDE.md CLI Quick Reference

**Objective:** Replace stale CLI Quick Reference entries with new commands.

**Replacements in § CLI Quick Reference:**
- `rai memory build` → `rai graph build`
- `rai memory query` → `rai graph query`
- `rai memory add-pattern` → `rai pattern add`
- `rai memory emit-work` → `rai signal emit-work`
- `rai memory context` → `rai graph context`

**Replacements in § Common Mistakes:**
- `rai memory build` → `rai graph build`
- `rai memory add-pattern` → `rai pattern add`

**Verification:**
```bash
grep -n "rai memory" CLAUDE.md | wc -l
# Expected: 0
```

**Size:** S
**Dependencies:** None (parallel with T1-T3)

### Task 5: Propagate + verification gate

**Objective:** Run `rai init` to propagate updated skills to `.claude/skills/` and `.agent/skills/`, then run the full verification gate.

**Steps:**
1. `rai init` (propagates skills_base → .claude/skills/ + .agent/skills/)
2. Run verification gate from scope.md:
```bash
grep -r "rai memory" src/rai_cli/skills_base/ && exit 1
grep -r "rai memory" CLAUDE.md && exit 1
grep -r "rai publish" src/rai_cli/skills_base/ && exit 1
```
3. Commit all changes

**Size:** S
**Dependencies:** T1, T2, T3, T4

## Execution Order

```
T1 (signal refs) ──┐
T2 (graph refs)  ──┼── T3 (pattern + stragglers) ── T5 (propagate + gate)
T4 (CLAUDE.md)   ──┘
```

T1, T2, T4 are parallel. T3 catches stragglers after T1+T2. T5 is final.

## Traceability

| AC Scenario | Task(s) | Design § |
|-------------|---------|----------|
| "Stale `rai memory` references replaced" | T1, T2, T3 | Gemba → Command Mapping |
| "Stale `rai publish` references replaced" | T5 (verify only) | Gemba → already clean |
| "Stale `rai base` references replaced" | T5 (verify only) | Gemba → already clean |
| "CLAUDE.md CLI Quick Reference updated" | T4 | Target Interfaces → CLAUDE.md target |
| "Verification gate passes" | T5 | Constraints → scope.md gate |

## Risks
- PAT-E-151 (rename long tail): Grep after EACH batch, not just at the end
- Generic prose refs: `rai memory` in descriptive text (not code blocks) — T3 catches these

## Duration Tracking

| Task | Size | Actual | Notes |
|------|------|--------|-------|
| T1 | M | -- | ~20 signal refs across 11 files |
| T2 | M | -- | ~25 graph refs across 13 files |
| T3 | S | -- | ~10 pattern refs + stragglers |
| T4 | S | -- | 8 refs in CLAUDE.md |
| T5 | S | -- | rai init + verification gate |
