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
  raise.version: "1.2.0"
  raise.visibility: public
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

### Step 0: Verify Prerequisites & Load Context (Parallel)

Run these in parallel (all independent):

```bash
# Verify tests pass
uv run pytest --tb=no -q || {
    echo "ERROR: Tests must pass before review"
    exit 10  # GateFailedError
}

# Query retrospective patterns and calibration data
rai graph query "retrospective learnings velocity" --types pattern,calibration --limit 5
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
rai pattern add "Pattern description" \
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
rai pattern add "HITL before commits" -c "git,workflow" -t process --from F12.6

# Technical pattern
rai pattern add "capsys.readouterr() for stdout tests" -c "pytest,testing" -t technical --from F12.6
```

**Decision:**
- Pattern is project-agnostic or reusable → Add to memory
- Pattern is one-off or context-specific → Document in retrospective only

**Verification:** Patterns persisted via CLI (or explicitly skipped).

> **If you can't continue:** CLI not available → Add patterns manually to `.raise/rai/memory/patterns.jsonl`.

### Step 4.6: Evaluate Behavioral Patterns (Reinforcement Signal)

Evaluate the patterns that were loaded at story-start against what actually happened
during implementation. This is the primary signal collection point for the temporal
decay scoring system (RAISE-170).

**When to run:** After implementation is complete and the code is working.
**Source of patterns:** The behavioral section loaded at session start (`rai session context --sections behavioral`).

**Votes:**
- `1` = implementation **followed** the pattern (applied, reinforced)
- `0` = pattern **not relevant** to this story (N/A — does NOT count toward evaluations)
- `-1` = implementation **contradicted** the pattern (violated, worked against it)

**Command per pattern:**
```bash
rai pattern reinforce {pattern_id} --vote {1|0|-1} --from {story_id}
```

**Example batch (RAISE-170 patterns):**
```bash
rai pattern reinforce PAT-E-183 --vote 1 --from RAISE-170   # Grounding over speed — applied
rai pattern reinforce PAT-E-153 --vote 1 --from RAISE-170   # JSONL backward compat — applied
rai pattern reinforce PAT-E-186 --vote 1 --from RAISE-170   # Design not optional — applied
rai pattern reinforce PAT-E-150 --vote 0 --from RAISE-170   # Drift review — N/A this story
rai pattern reinforce PAT-E-151 --vote 0 --from RAISE-170   # Large renames — N/A this story
```

**Decision heuristic per pattern:**
- Did the implementation explicitly use, follow, or validate this pattern? → `1`
- Was the pattern loaded but this story simply wasn't the relevant context? → `0`
- Did the implementation go against what the pattern recommends? → `-1`

**Output interpretation:**
- `wilson≈0.XX` — current confidence score after update
- `↓ consider reviewing` — Wilson score < 0.15, pattern may need revision

**Note:** Only evaluate patterns you consciously considered during implementation.
Do NOT force votes. `0` is the right choice for most patterns in any given story.

**Verification:** All loaded behavioral patterns evaluated (or explicitly skipped with reason).

> **If you can't continue:** CLI unavailable → Document evaluations in retrospective manually.

### Step 5: Document Retrospective

Create retrospective document:
- Feature summary
- Key learnings
- Improvements applied

**Verification:** Retrospective documented.

### Step 6: Emit Calibration Telemetry

Record the calibration signal for velocity tracking:

```bash
rai signal emit-calibration {story_id} \
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
rai signal emit-calibration F9.4 -s S -e 30 -a 15
```

**Verification:** Command shows velocity and "Calibration event recorded".

> **If you can't continue:** CLI not available → Skip; telemetry is optional.

## Output

- **Artifact:** `work/epics/e{N}-{name}/stories/f{N}.{M}-{name}/retrospective.md`
- **Memory:** `.raise/rai/memory/patterns.jsonl` (patterns persisted via CLI)
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
