---
name: rai-story-implement
description: >
  Execute the implementation plan task by task, verifying each step, and
  producing quality code that passes validation gates. Use after planning
  is complete.

license: MIT

metadata:
  raise.work_cycle: story
  raise.frequency: per-story
  raise.fase: "6"
  raise.prerequisites: story-plan
  raise.next: story-review
  raise.gate: gate-code
  raise.adaptable: "true"
  raise.version: "2.0.0"
  raise.visibility: public
---

# Implement: Development Workflow

## Purpose

Execute the implementation plan task by task with TDD, producing verified code that passes all gates.

## Mastery Levels (ShuHaRi)

- **Shu**: Execute tasks strictly in order, verify each before proceeding
- **Ha**: Adjust plan based on discoveries during implementation
- **Ri**: Parallelize independent tasks, create stack-specific patterns

## Context

**When to use:** After `/rai-story-plan` has produced a plan document.

**Prerequisite:** Plan must exist at `work/epics/e{N}-{name}/stories/{story_id}/plan.md`. Run `/rai-story-plan` first if missing.

**Inputs:** Implementation plan, project guardrails (from graph context).

## Steps

### Step 1: Load Plan & Context

Load the implementation plan and query relevant patterns:

```bash
rai graph query "testing coverage type annotations" --types pattern,guardrail --limit 5
```

If a design document exists, restate the design intent in 2-3 sentences and confirm with the human before proceeding. One unvalidated assumption can waste an entire task cycle.

### Step 2: Execute Task

For the next uncompleted task in plan order:

1. **RED** — Write a failing test that defines expected behavior
2. **GREEN** — Write minimal code to make the test pass
3. **REFACTOR** — Clean up while keeping tests green

Follow project rules, guardrails, and established patterns.

### Step 3: Verify Task

Run the verification defined in the plan:
- Unit tests (`pytest`)
- Linting (`ruff check`)
- Type checking (`pyright`)

If verification fails: fix and re-verify (max 3 attempts before escalating).

### Step 4: Commit & Checkpoint

1. Commit the completed task
2. Update progress log (`work/epics/.../stories/{story_id}/progress.md`)
3. Present to the human: what was completed, files changed, verification results
4. Wait for acknowledgment before continuing

### Step 5: Iterate or Finalize

| Condition | Action |
|-----------|--------|
| More tasks remain | Return to Step 2 |
| All tasks complete | Run full gate check, present summary |
| Task blocked | Document blocker, escalate to human |

## Output

| Item | Destination |
|------|-------------|
| Implemented code | Per project architecture |
| Progress log | `work/epics/.../stories/{story_id}/progress.md` |
| Next | `/rai-story-review` |

## Quality Checklist

- [ ] Plan loaded and design intent confirmed (if design exists)
- [ ] TDD cycle followed for each task (RED → GREEN → REFACTOR)
- [ ] Each task committed individually (not batched at story end)
- [ ] All verifications pass (tests, lint, types)
- [ ] Progress log updated with actuals
- [ ] Human acknowledged each task before proceeding
- [ ] NEVER skip a failing test — fix it or escalate
- [ ] NEVER accumulate errors — stop on defect (Jidoka)

## References

- Gate: `gates/gate-code.md`
- Next skill: `/rai-story-review`
- Progress template: `references/progress-template.md`
