---
name: feature-plan
description: >
  Decompose user stories into atomic executable tasks, identify dependencies,
  and create a deterministic implementation plan. Use after design spec is ready
  or for simple features that skip design.

license: MIT

metadata:
  raise.work_cycle: feature
  raise.frequency: per-feature
  raise.fase: "5"
  raise.prerequisites: project-backlog
  raise.next: feature-implement
  raise.gate: gate-plan
  raise.adaptable: "true"
  raise.version: "1.0.0"

hooks:
  PostToolUse:
    - matcher: "Write"
      hooks:
        - type: command
          command: "RAISE_SKILL_NAME=feature-plan \"$CLAUDE_PROJECT_DIR\"/.claude/skills/scripts/log-artifact-created.sh"
  Stop:
    - hooks:
        - type: command
          command: "RAISE_SKILL_NAME=feature-plan \"$CLAUDE_PROJECT_DIR\"/.claude/skills/scripts/log-skill-complete.sh"
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
- For each feature to be developed

**Inputs required:**
- User stories for the feature to implement
- Technical Design for architectural context (if complex)

**Output:**
- `work/features/{feature}/plan.md` - Implementation plan

## Steps

### Step 1: Select Story

Identify the next story to implement by priority.

**Verification:** Selected story has clear BDD/acceptance criteria.

> **If you can't continue:** Story without criteria → Complete BDD criteria first.

### Step 2: Decompose into Tasks

Divide story into atomic tasks:
- 1-4 hours of work each
- Independent when possible
- Individually verifiable

**Task structure:**
```markdown
### Task N: [Name]
- **Description:** What to do
- **Files:** Files to create/modify
- **Verification:** How to verify completion
- **Estimate:** X hours
```

**Verification:** Each task is atomic and verifiable.

> **If you can't continue:** Tasks too large → Divide until atomic.

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
- Ordered list of tasks
- Dependencies
- Verifications
- Total estimate

**Verification:** Plan documented and complete.

## Output

- **Artifact:** `work/features/{feature}/plan.md`
- **Gate:** `gates/gate-plan.md`
- **Next:** `/feature-implement`

## Plan Template

```markdown
# Implementation Plan: {Feature Name}

## Overview
- **Feature:** {feature-id}
- **Stories:** {list of story IDs}
- **Total Estimate:** X hours
- **Created:** YYYY-MM-DD

## Tasks

### Task 1: {Name}
- **Description:** ...
- **Files:** ...
- **Verification:** `pytest tests/test_X.py`
- **Estimate:** 2h
- **Dependencies:** None

### Task 2: {Name}
- **Description:** ...
- **Files:** ...
- **Verification:** `ruff check src/`
- **Estimate:** 1h
- **Dependencies:** Task 1

## Execution Order
1. Task 1 (foundation)
2. Task 2 (depends on 1)
3. Task 3, Task 4 (parallel)
5. Task 5 (integration)

## Risks
- {Risk 1}: {Mitigation}
```

## References

- Gate: `gates/gate-plan.md`
- Next skill: `/feature-implement`
