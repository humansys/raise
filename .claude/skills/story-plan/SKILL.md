---
name: story-plan
description: >
  Decompose user stories into atomic executable tasks, identify dependencies,
  and create a deterministic implementation plan. Use after design spec is ready
  or for simple stories that skip design.

license: MIT

metadata:
  raise.work_cycle: story
  raise.frequency: per-story
  raise.fase: "5"
  raise.prerequisites: project-backlog
  raise.next: story-implement
  raise.gate: gate-plan
  raise.adaptable: "true"
  raise.version: "1.0.0"

hooks:
  PostToolUse:
    - matcher: "Write"
      hooks:
        - type: command
          command: "RAISE_SKILL_NAME=story-plan \"$CLAUDE_PROJECT_DIR\"/.raise/scripts/log-artifact-created.sh"
  Stop:
    - hooks:
        - type: command
          command: "RAISE_SKILL_NAME=story-plan \"$CLAUDE_PROJECT_DIR\"/.raise/scripts/log-skill-complete.sh"
---

# Plan: Implementation Planning

## Purpose

Decompose user stories into atomic executable tasks, identify dependencies, and create a deterministic implementation plan that guides development.

## Mastery Levels (ShuHaRi)

**Shu (守)**: Decompose each story into atomic tasks with full verification criteria.

**Ha (破)**: Adjust granularity based on complexity; parallelize when possible.

**Ri (離)**: Create custom planning patterns for specific stacks or contexts.

## Context

**When to use:**
- After having prioritized stories in the backlog
- Before starting feature implementation
- For each story to be developed

**Inputs required:**
- User stories for the feature to implement
- Technical Design for architectural context (if complex)

**Output:**
- Implementation plan: `work/epics/e{N}-{name}/stories/f{N}.{M}-{name}/plan.md`

## Steps

### Step 0: Emit Feature Start (Telemetry)

Record the start of the plan phase:

```bash
uv run raise memory emit-work story {story_id} --event start --phase plan
```

**Example:** `raise memory emit-work story S15.1 -e start -p plan`

### Step 0.1: Verify Prerequisites (Deterministic)

Check design document for complex features:

```bash
ls work/epics/e*/stories/{story_id}/design.md 2>/dev/null || echo "INFO: No design"
```

**Decision:**
- design.md exists → Load and reference
- design.md missing + Simple feature → Continue (design optional)
- design.md missing + Moderate/Complex → Suggest `/story-design` first

**Skip condition:** Simple features (per complexity matrix in /story-design).

**Verification:** Design loaded OR simple feature confirmed.

> **If you can't continue:** Complex feature without design → Run `/story-design` first.

### Step 0.5: Query Context

Load relevant patterns and calibration from unified context:

```bash
uv run raise memory query "planning estimation calibration" --types pattern,calibration --limit 5
```

Review returned patterns before proceeding. Key patterns inform task structure and sizing.

**Verification:** Context loaded; relevant patterns noted.

> **If context unavailable:** Run `raise memory build` first, or proceed without patterns.

### Step 1: Select Story

Identify the next story to implement by priority.

**Verification:** Selected story has clear BDD/acceptance criteria.

> **If you can't continue:** Story without criteria → Complete BDD criteria first.

### Step 2: Decompose into Tasks

Divide story into atomic tasks:
- Independent when possible
- Individually verifiable
- One commit per task

**Task granularity guidance:**

| Feature Size | Recommended Tasks | Rationale |
|--------------|-------------------|-----------|
| XS (1-2 SP) | 1-2 tasks | Single-pass implementation |
| S (3-5 SP) | 2-3 tasks | Avoid over-decomposition |
| M (5-8 SP) | 3-5 tasks | Balance granularity and overhead |
| L (8+ SP) | 5-8 tasks | Consider splitting the feature |

**T-shirt sizing guide:**

| Size | Scope | Typical Duration* |
|------|-------|-------------------|
| XS | Single function/method, trivial change | <15 min |
| S | Single component, straightforward logic | 15-30 min |
| M | Multiple files, moderate complexity | 30-60 min |
| L | Cross-cutting, significant complexity | 1-2 hours |

*Duration tracked for calibration, not commitment. AI-assisted velocity varies.

**Task structure:**
```markdown
### Task N: [Name]
- **Description:** What to do
- **Files:** Files to create/modify
- **TDD Cycle:** RED (write failing test) → GREEN (implement) → REFACTOR
- **Verification:** How to verify completion (test command)
- **Size:** XS/S/M/L
- **Dependencies:** None / Task N
```

**TDD Guidance (RED/GREEN cycles):**
- **RED:** Write a failing test first that defines expected behavior
- **GREEN:** Write minimal code to make the test pass
- **REFACTOR:** Clean up while keeping tests green
- For infrastructure/setup tasks, TDD cycle may be optional

**Verification:** Each task is atomic and verifiable.

> **If you can't continue:** Tasks too large → Divide until atomic. But avoid over-decomposition for simple features.

**Required final task:** Always include a manual integration test task as the last task:
```markdown
### Task N (Final): Manual Integration Test
- **Description:** Validate story works end-to-end with running software
- **Verification:** Demo the story working (not just unit tests passing)
- **Size:** XS
- **Dependencies:** All previous tasks
```

This validates the implementation with real usage before marking the story complete.

### Step 3: Identify Dependencies

Map dependencies between tasks:
- Sequential vs parallel
- External dependencies
- Potential blockers

**Verification:** Dependency graph has no cycles.

> **If you can't continue:** Circular dependencies → Refactor tasks to break cycles.

### Step 4: Order Execution

Define optimal execution order:
- Respect dependencies
- Maximize parallelism
- Quick wins first
- Risk-first approach (riskiest tasks early)

**Verification:** Execution order defined.

> **If you can't continue:** Ambiguous order → Prioritize by risk.

### Step 5: Define Verification Per Task

For each task, define:
- Completion criteria
- Verification command (test, lint, etc.)
- Rollback if fails

**Verification:** Each task has verification criteria.

> **If you can't continue:** Verification unclear → Add specific test for the task.

### Step 6: Document Plan

Create plan document with:
- Ordered list of tasks with T-shirt sizes
- Dependencies
- Verifications
- Duration tracking table (filled during implementation)

**Verification:** Plan documented and complete.

### Step 7: Emit Feature Complete (Telemetry)

Record the completion of the plan phase:

```bash
uv run raise memory emit-work story {story_id} --event complete --phase plan
```

**Example:** `raise memory emit-work story S15.1 -e complete -p plan`

## Output

- **Artifact:** `work/epics/e{N}-{name}/stories/f{N}.{M}-{name}/plan.md`
- **Telemetry:** `.raise/rai/telemetry/signals.jsonl` (feature_lifecycle: plan start/complete)
- **Gate:** `gates/gate-plan.md`
- **Next:** `/story-implement`

## Plan Template

```markdown
# Implementation Plan: {Feature Name}

## Overview
- **Feature:** {feature-id}
- **Story Points:** N SP
- **Feature Size:** XS/S/M/L
- **Created:** YYYY-MM-DD

## Tasks

### Task 1: {Name}
- **Description:** ...
- **Files:** ...
- **TDD Cycle:** RED → GREEN → REFACTOR
- **Verification:** `pytest tests/test_X.py`
- **Size:** S
- **Dependencies:** None

### Task 2: {Name}
- **Description:** ...
- **Files:** ...
- **TDD Cycle:** RED → GREEN → REFACTOR
- **Verification:** `ruff check src/`
- **Size:** XS
- **Dependencies:** Task 1

### Task N (Final): Manual Integration Test
- **Description:** Validate story works end-to-end with running software
- **Verification:** Demo the story working interactively
- **Size:** XS
- **Dependencies:** All previous tasks

## Execution Order
1. Task 1 (foundation)
2. Task 2 (depends on 1)
3. Task 3, Task 4 (parallel)
4. Task N - Manual Integration Test (final validation)

## Risks
- {Risk 1}: {Mitigation}

## Duration Tracking
| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | S | -- | (filled during implementation) |
| 2 | XS | -- | |
| N | XS | -- | Integration test |
```

## References

- Gate: `gates/gate-plan.md`
- Next skill: `/story-implement`
