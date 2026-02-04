---
name: feature-review
description: >
  Reflect on completed features to extract learnings, identify process
  improvements, and update the framework with insights gained. Use after
  implementation is complete to close the development cycle.

license: MIT

metadata:
  raise.work_cycle: feature
  raise.frequency: per-feature
  raise.fase: "7"
  raise.prerequisites: feature-implement
  raise.next: ""
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "1.0.0"

hooks:
  PostToolUse:
    - matcher: "Write"
      hooks:
        - type: command
          command: "RAISE_SKILL_NAME=feature-review \"$CLAUDE_PROJECT_DIR\"/.claude/skills/scripts/log-artifact-created.sh"
  Stop:
    - hooks:
        - type: command
          command: "RAISE_SKILL_NAME=feature-review \"$CLAUDE_PROJECT_DIR\"/.claude/skills/scripts/log-skill-complete.sh"
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
- Progress log (`work/features/{feature}/progress.md`)
- Team feedback (if available)

**Output:**
- `work/features/{feature}/retrospective.md` - Documented retrospective

## Steps

### Step 0: Emit Feature Start (Telemetry)

Record the start of the review phase:

```bash
raise telemetry emit feature {feature_id} --event start --phase review
```

**Example:** `raise telemetry emit feature F9.4 -e start -p review`

### Step 0.5: Query Context

Load relevant process patterns and prior retrospectives from unified context:

```bash
raise context query "retrospective process patterns" --unified --types pattern,session --limit 5
```

Review returned patterns before proceeding. Prior learnings inform retrospective focus.

**Verification:** Context loaded; relevant patterns noted.

> **If context unavailable:** Run `raise graph build --unified` first, or proceed without patterns.

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

### Step 5: Document Retrospective

Create retrospective document:
- Feature summary
- Key learnings
- Improvements applied

**Verification:** Retrospective documented.

### Step 6: Emit Calibration Telemetry

Record the calibration signal for velocity tracking:

```bash
raise telemetry emit-calibration {feature_id} \
  --size {XS|S|M|L} \
  --estimated {minutes} \
  --actual {minutes}
```

**Parameters:**
- `feature_id`: Feature ID from the plan (e.g., F9.4)
- `--size`: T-shirt size from the plan
- `--estimated`: Total estimated minutes from the plan
- `--actual`: Total actual minutes from progress log

**Example:**
```bash
raise telemetry emit-calibration F9.4 -s S -e 30 -a 15
```

**Verification:** Command shows velocity and "Calibration event recorded".

> **If you can't continue:** CLI not available → Skip; telemetry is optional.

### Step 7: Emit Feature Complete (Telemetry)

Record the completion of the entire feature lifecycle:

```bash
raise telemetry emit feature {feature_id} --event complete --phase review
```

**Example:** `raise telemetry emit feature F9.4 -e complete -p review`

**Note:** This marks the feature as fully complete through all phases (design → plan → implement → review).

## Output

- **Artifact:** `work/features/{feature}/retrospective.md`
- **Telemetry:** `.rai/telemetry/signals.jsonl` (feature_lifecycle: review start/complete, calibration)
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

The retrospective completes the feature cycle and feeds learnings back into the framework, enabling organic evolution.

## References

- Heutagogical Checkpoint: `framework/reference/glossary.md`
- Kaizen: Toyota Production System
- Previous skill: `/feature-implement`
