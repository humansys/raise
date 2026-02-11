---
name: rai-story-review
description: >
  Reflect on completed stories to extract learnings, identify process
  improvements, and update the framework with insights gained. Use after
  implementation is complete to close the development cycle.

license: MIT

metadata:
  raise.work_cycle: story
  raise.frequency: per-story
  raise.fase: "7"
  raise.prerequisites: story-implement
  raise.next: story-close
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "1.1.0"
---

# Review: Retrospective & Learning

## Purpose

Reflect on the completed feature to extract learnings, identify process improvements, and update the framework with insights gained.

## Mastery Levels (ShuHaRi)

**Shu (守)**: Follow standard retrospective questions faithfully.

**Ha (破)**: Adapt questions to team context and project specifics.

**Ri (離)**: Create custom review patterns for specific domains or contexts.

## Context

**When to use:**
- After completing a feature
- Before starting the next feature
- As closure for the development cycle

**Inputs required:**
- Completed feature
- Progress log: `work/epics/e{N}-{name}/stories/f{N}.{M}-{name}/progress.md`
- Team feedback (if available)

**Output:**
- Retrospective: `work/epics/e{N}-{name}/stories/f{N}.{M}-{name}/retrospective.md`

## Steps

### Step 0: Emit Feature Start (Telemetry)

Record the start of the review phase:

```bash
rai memory emit-work story {story_id} --event start --phase review
```

**Example:** `rai memory emit-work story S15.1 -e start -p review`

### Step 0.1: Verify Prerequisites & Load Context (Parallel)

Run these in parallel (all independent):

```bash
# Verify tests pass
uv run pytest --tb=no -q || {
    echo "ERROR: Tests must pass before review"
    exit 10  # GateFailedError
}

# Query retrospective patterns and calibration data
rai memory query "retrospective learnings velocity" --types pattern,calibration --limit 5
```

**From tests:**
- Tests pass → Continue with review
- Tests fail → Fix tests first, then review

**From memory query:**
- Process patterns from prior retrospectives
- Calibration data (feature completion times for velocity comparison)

**Verification:** All tests passing; patterns noted.

> **If you can't continue:** Fix failing tests. Review requires green tests.

### Step 1: Gather Data

Review the feature development:
- Actual time vs estimated
- Blockers encountered
- Deviations from plan

**Verification:** Feature data collected.

> **If you can't continue:** No data → Reconstruct timeline from commits/PRs.

### Step 2: Heutagogical Checkpoint

Answer the four questions:
1. What did you learn?
2. What would you change about the process?
3. Are there improvements for the framework?
4. What are you more capable of now?

**Verification:** All four questions answered with specific examples.

> **If you can't continue:** Vague answers → Be more specific with concrete examples.

### Step 3: Identify Process Improvements

List concrete improvements:
- To skills/katas
- To guardrails
- To templates

**Verification:** Improvements identified with owner.

> **If you can't continue:** No improvements → Celebrate the process and continue.

### Step 4: Update Framework

If improvements identified:
- Update relevant skills
- Create or modify guardrails
- Document decisions (ADRs if significant)

**Verification:** Improvements applied to framework.

> **If you can't continue:** Complex improvement → Create issue for future.

### Step 4.5: Persist Patterns to Memory

For learnings worth preserving across sessions, add to memory via CLI:

```bash
rai memory add-pattern "Pattern description" \
  -c "context,keywords" \
  -t process \
  --from {story_id}
```

**Pattern types:**
- `process` — How to work (workflow, collaboration)
- `technical` — Code techniques, gotchas, APIs
- `architecture` — Design decisions, module patterns
- `codebase` — Project-specific conventions

**Examples:**
```bash
# Process pattern
rai memory add-pattern "HITL before commits" -c "git,workflow" -t process --from F12.6

# Technical pattern
rai memory add-pattern "capsys.readouterr() for stdout tests" -c "pytest,testing" -t technical --from F12.6
```

**Decision:**
- Pattern is project-agnostic or reusable → Add to memory
- Pattern is one-off or context-specific → Document in retrospective only

**Verification:** Patterns persisted via CLI (or explicitly skipped).

> **If you can't continue:** CLI not available → Add patterns manually to `.raise/rai/memory/patterns.jsonl`.

### Step 5: Document Retrospective

Create retrospective document:
- Feature summary
- Key learnings
- Improvements applied

**Verification:** Retrospective documented.

### Step 6: Emit Calibration Telemetry

Record the calibration signal for velocity tracking:

```bash
rai memory emit-calibration {story_id} \
  --size {XS|S|M|L} \
  --estimated {minutes} \
  --actual {minutes}
```

**Parameters:**
- `story_id`: Feature ID from the plan (e.g., F9.4)
- `--size`: T-shirt size from the plan
- `--estimated`: Total estimated minutes from the plan
- `--actual`: Total actual minutes from progress log

**Example:**
```bash
rai memory emit-calibration F9.4 -s S -e 30 -a 15
```

**Verification:** Command shows velocity and "Calibration event recorded".

> **If you can't continue:** CLI not available → Skip; telemetry is optional.

### Step 7: Emit Feature Complete (Telemetry)

Record the completion of the entire story lifecycle:

```bash
rai memory emit-work story {story_id} --event complete --phase review
```

**Example:** `rai memory emit-work story S15.1 -e complete -p review`

**Note:** This marks the feature as fully complete through all phases (design → plan → implement → review).

## Output

- **Artifact:** `work/epics/e{N}-{name}/stories/f{N}.{M}-{name}/retrospective.md`
- **Memory:** `.raise/rai/memory/patterns.jsonl` (patterns persisted via CLI)
- **Telemetry:** `.raise/rai/personal/telemetry/signals.jsonl` (feature_lifecycle: review start/complete, calibration)
- **Gate:** None
- **Next:** Next feature or continuous improvement

## Retrospective Template

```markdown
# Retrospective: {Feature Name}

## Summary
- **Feature:** {feature-id}
- **Started:** YYYY-MM-DD
- **Completed:** YYYY-MM-DD
- **Estimated:** X hours
- **Actual:** Y hours

## What Went Well
- {Positive aspects}

## What Could Improve
- {Areas for improvement}

## Heutagogical Checkpoint

### What did you learn?
- {Specific learnings}

### What would you change about the process?
- {Process improvements}

### Are there improvements for the framework?
- {Framework enhancements}

### What are you more capable of now?
- {Capability growth}

## Improvements Applied
- {List of changes made to framework}

## Action Items
- [ ] {Future improvements to implement}
```

## Notes

### Kaizen

This skill implements the Kaizen principle of continuous improvement. Each retrospective should produce at least one concrete improvement.

### Closing the Loop

The retrospective completes the story cycle and feeds learnings back into the framework, enabling organic evolution.

## References

- Heutagogical Checkpoint: `framework/reference/glossary.md`
- Kaizen: Toyota Production System
- Previous skill: `/rai-story-implement`
