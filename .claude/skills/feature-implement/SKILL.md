---
name: feature-implement
description: >
  Execute the implementation plan task by task, verifying each step, and
  producing quality code that passes validation gates. Use after planning
  is complete.

license: MIT

metadata:
  raise.work_cycle: feature
  raise.frequency: per-feature
  raise.fase: "6"
  raise.prerequisites: feature-plan
  raise.next: feature-review
  raise.gate: gate-code
  raise.adaptable: "true"
  raise.version: "1.0.0"

hooks:
  PostToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: "RAISE_SKILL_NAME=feature-implement \"$CLAUDE_PROJECT_DIR\"/.claude/skills/scripts/log-artifact-created.sh"
  Stop:
    - hooks:
        - type: command
          command: "RAISE_SKILL_NAME=feature-implement \"$CLAUDE_PROJECT_DIR\"/.claude/skills/scripts/log-skill-complete.sh"
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
- For each feature being developed
- Repeated for each task in the plan

**Inputs required:**
- Implementation plan: `work/epics/e{N}-{name}/features/f{N}.{M}-{name}/plan.md`
- Project rules and guardrails context

**Output:**
- Implemented and verified code
- Progress log: `work/epics/e{N}-{name}/features/f{N}.{M}-{name}/progress.md`

## Steps

### Step 0: Emit Feature Start (Telemetry)

Record the start of the implement phase:

```bash
uv run raise telemetry emit-work feature {feature_id} --event start --phase implement
```

**Example:** `raise telemetry emit-work feature F9.4 -e start -p implement`

### Step 0.1: Verify Prerequisites (REQUIRED - No Skip)

Implementation plan is mandatory:

```bash
PLAN="work/epics/e{N}-{name}/features/{feature_id}/plan.md"
if [ ! -f "$PLAN" ]; then
    echo "ERROR: Plan not found: $PLAN"
    echo "Run /feature-plan first"
    exit 4  # ArtifactNotFoundError
fi
```

**No skip:** Planning provides task decomposition and verification criteria.

**Verification:** Plan exists and is readable.

> **If you can't continue:** Run `/feature-plan`. No exceptions.

### Step 0.5: Query Context

Load relevant codebase patterns from unified context:

```bash
uv run raise context query "testing coverage type annotations security" --types pattern,guardrail --limit 5
```

Review returned patterns and guardrails before proceeding. Key patterns inform implementation approach; guardrails ensure code standards compliance.

**What this returns:**
- Codebase patterns for implementation
- Active guardrails (MUST/SHOULD code standards from `guardrails.md`)

**Verification:** Context loaded; relevant patterns noted.

> **If context unavailable:** Run `raise graph build --unified` first, or proceed without patterns.

### Step 1: Load Plan and Context

Load the implementation plan and obtain applicable rules context.

**Verification:** Plan loaded and context available.

> **If you can't continue:** Plan not found → Prerequisite check (Step 0.1) should have caught this.

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

Update progress log (`work/epics/e{N}-{name}/features/{feature}/progress.md`):
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
uv run raise telemetry emit-work feature {feature_id} --event complete --phase implement
```

**Example:** `raise telemetry emit-work feature F9.4 -e complete -p implement`

## Output

- **Artifact:** Implemented code
- **Location:** Per project architecture
- **Telemetry:** `.raise/rai/telemetry/signals.jsonl` (feature_lifecycle: implement start/complete)
- **Gate:** `gates/gate-code.md`
- **Next:** `/feature-review`

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
- Next skill: `/feature-review`
