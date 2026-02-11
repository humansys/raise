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
  raise.version: "1.0.0"
---

# Implement: Development Workflow

## Purpose

Execute the implementation plan task by task, verifying each step, and producing quality code that passes validation gates.

## Mastery Levels (ShuHaRi)

**Shu (守)**: Execute tasks in order, verify each one before proceeding.

**Ha (破)**: Adjust plan based on discoveries during implementation.

**Ri (離)**: Create implementation patterns for specific stacks.

## Context

**When to use:**
- After having an implementation plan
- For each story being developed
- Repeated for each task in the plan

**Inputs required:**
- Implementation plan: `work/epics/e{N}-{name}/stories/f{N}.{M}-{name}/plan.md`
- Project rules and guardrails context

**Output:**
- Implemented and verified code
- Progress log: `work/epics/e{N}-{name}/stories/f{N}.{M}-{name}/progress.md`

## Steps

### Step 0: Emit Feature Start (Telemetry)

Record the start of the implement phase:

```bash
rai memory emit-work story {story_id} --event start --phase implement
```

**Example:** `rai memory emit-work story S15.1 -e start -p implement`

### Step 0.1: Verify Prerequisites (REQUIRED - No Skip)

Implementation plan is mandatory:

```bash
PLAN="work/epics/e{N}-{name}/stories/{story_id}/plan.md"
if [ ! -f "$PLAN" ]; then
    echo "ERROR: Plan not found: $PLAN"
    echo "Run /rai-story-plan first"
    exit 4  # ArtifactNotFoundError
fi
```

**No skip:** Planning provides task decomposition and verification criteria.

**Verification:** Plan exists and is readable.

> **If you can't continue:** Run `/rai-story-plan`. No exceptions.

### Step 0.5: Query Context

Load relevant codebase patterns from unified context:

```bash
rai memory query "testing coverage type annotations security" --types pattern,guardrail --limit 5
```

Review returned patterns and guardrails before proceeding. Key patterns inform implementation approach; guardrails ensure code standards compliance.

**What this returns:**
- Codebase patterns for implementation
- Active guardrails (MUST/SHOULD code standards from `guardrails.md`)

**Verification:** Context loaded; relevant patterns noted.

> **If context unavailable:** Run `rai memory build` first, or proceed without patterns.

### Step 1: Load Plan and Context

Load the implementation plan and obtain applicable rules context.

**Verification:** Plan loaded and context available.

> **If you can't continue:** Plan not found → Prerequisite check (Step 0.1) should have caught this.

### Step 1.5: Design Comprehension Check (If Design Exists)

If a design document exists for this story, restate the design intent to the user in 2-3 plain-language sentences before implementing. This catches misinterpretation before it cascades through tasks.

**Present to user:**
> "Based on the design, I understand we're building [X] that does [Y] by [Z]. Correct?"

**Focus on:** Key concepts, data flow, what's explicitly NOT in scope.

**Why:** One unvalidated assumption can waste an entire task cycle (PAT-167). A 30-second check saves hundreds of tokens.

**Verification:** User confirms understanding or corrects it.

> **If you can't continue:** Misalignment detected → Clarify before proceeding.

### Step 2: Identify Next Task

Select the next uncompleted task according to plan order.

**Timestamp tracking:** Capture start time for accurate measurement.

**Verification:** Task identified with its dependencies resolved.

> **If you can't continue:** Dependencies unresolved → Resolve dependencies first.

### Step 3: Execute Task

Implement the code for the task following:
- Project rules and guardrails
- Established patterns
- Required tests

**Verification:** Code implemented and compiles/runs.

> **If you can't continue:** Implementation error → Document blocker and escalate.

### Step 4: Verify Task

Execute verification defined in the plan:
- Unit tests
- Linting
- Type checking

**Verification:** All verifications pass.

> **If you can't continue:** Verification fails → Fix and re-verify (max 3 attempts).

### Step 5: Log Progress

Update progress log (`work/epics/e{N}-{name}/stories/{feature}/progress.md`):
- Task completed
- Actual time vs estimated
- Notes or discoveries

**Verification:** Progress logged with accurate time.

### Step 6: HITL Checkpoint

**IMPORTANT:** Pause after each task for human review unless explicitly told "autonomous mode".

Present:
- What was completed
- Files created/modified
- Verification results
- "Ready for next task?"

**Rationale:** Slow is smooth, smooth is fast. HITL builds trust and catches issues early.

**Verification:** Human acknowledged task completion.

> **If you can't continue:** No response → Wait. Don't rush ahead.

### Step 7: Iterate or Finalize

If more tasks → return to Step 2.
If all tasks completed → execute code gate.

**Verification:** All plan tasks completed.

> **If you can't continue:** Tasks blocked → Document and escalate.

### Step 8: Emit Feature Complete (Telemetry)

Record the completion of the implement phase:

```bash
rai memory emit-work story {story_id} --event complete --phase implement
```

**Example:** `rai memory emit-work story S15.1 -e complete -p implement`

## Output

- **Artifact:** Implemented code
- **Location:** Per project architecture
- **Telemetry:** `.raise/rai/personal/telemetry/signals.jsonl` (feature_lifecycle: implement start/complete)
- **Gate:** `gates/gate-code.md`
- **Next:** `/rai-story-review`

## Progress Template

```markdown
# Progress: {Feature Name}

## Status
- **Started:** YYYY-MM-DD HH:MM
- **Current Task:** N of M
- **Status:** In Progress / Complete / Blocked

## Completed Tasks

### Task 1: {Name}
- **Started:** HH:MM
- **Completed:** HH:MM
- **Duration:** X min (estimated: Y min)
- **Notes:** ...

### Task 2: {Name}
- **Started:** HH:MM
- **Completed:** HH:MM
- **Duration:** X min (estimated: Y min)
- **Notes:** ...

## Blockers
- {None / Description of blocker}

## Discoveries
- {Learnings during implementation}
```

## Notes

### Resumability

Progress is persisted in `progress.md`, allowing implementation to resume if interrupted.

### Attempt Limits

Maximum 3 attempts per failed verification before escalating.

### Jidoka

If you detect a defect or guardrail violation: **STOP**. Do not accumulate errors.

Cycle: **Detect → Stop → Correct → Continue**

## References

- Gate: `gates/gate-code.md`
- Next skill: `/rai-story-review`
