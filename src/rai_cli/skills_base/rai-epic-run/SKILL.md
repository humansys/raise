---
name: rai-epic-run
description: >
  Chain the full epic lifecycle (start → design → plan → story iterations →
  close) in one invocation. Resumes from last completed phase using
  git-derived artifact detection. Stories iterate via /rai-story-run.
  Delegation profile controls pause behavior at natural gates.

license: MIT

metadata:
  raise.work_cycle: epic
  raise.frequency: per-epic
  raise.fase: ""
  raise.prerequisites: ""
  raise.next: ""
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "1.0.0"
  raise.visibility: public
  raise.inputs: |
    - epic_id: string, required, argument (e.g. "E325")
    - epic_slug: string, optional, argument (inferred from scope or prompted)
  raise.outputs: |
    - merge_commit: string, git
    - retrospective: file_path (work/epics/e{N}-{name}/retrospective.md)
---

# Epic Run

## Purpose

Execute the full epic lifecycle in one invocation — including iterating all stories via `/rai-story-run` — pausing only at delegation gates and resuming automatically from the last completed phase.

## Mastery Levels (ShuHaRi)

- **Shu**: Show phase progress, explain each skill's output, pause at both gates
- **Ha**: Brief progress between phases, pause only when delegation says REVIEW
- **Ri**: Minimal output, AUTO delegation, gates stop only on failure

## Context

**When to use:** Starting or resuming any epic. Replaces manual sequential skill and story invocation.

**When to skip:** Single-phase work (e.g., only closing an already-completed epic). Individual skills remain independently invocable.

## Steps

### Step 0: Detect Phase

Resolve the epic path from `epic_id`. Check artifacts in **reverse order** — take the most advanced phase:

| Check | Condition | Resume at |
|:-----:|-----------|-----------|
| 4 | `### Progress Tracking` exists AND all rows Status = "Done" | **close** |
| 3 | `### Progress Tracking` exists AND any row Status != "Done" | **stories** |
| 2 | `scope.md` exists, no `### Progress Tracking` heading | **plan** |
| 1 | epic branch exists, no `scope.md` | **design** |
| 0 | (nothing) | **start** |

Present: "Phase detection: resuming at **{phase}**" with context (e.g., "3/5 stories done, 2 remaining").

<verification>
Phase identified. Epic path resolved.
</verification>

### Step 1: Resolve Delegation

Load developer profile from `~/.rai/developer.yaml`. Resolve delegation level:

| Source | Resolution |
|--------|-----------|
| `delegation.overrides.rai-epic-run` | Per-skill override (highest priority) |
| `delegation.default_level` | Explicit default |
| `experience_level` ShuHaRi | Shu→REVIEW, Ha→NOTIFY, Ri→AUTO |
| No profile | Default to REVIEW |

Present: "Delegation: **{level}**"

<verification>
Delegation level resolved.
</verification>

### Step 2: Execute Epic Skill Chain

Run each epic skill from the detected phase forward. Show `── Phase {N}/5: {skill_name} ──` between phases.

| Phase | Skill | Gate after? |
|:-----:|-------|:-----------:|
| 1 | `/rai-epic-start {epic_id}` | — |
| 2 | `/rai-epic-design {epic_id}` | **POST-DESIGN** |
| 3 | `/rai-epic-plan {epic_id}` | **POST-PLAN** |
| 4 | Story iteration (see Step 3) | — |
| 5 | `/rai-epic-close {epic_id}` | — |

Each skill invocation follows its own SKILL.md completely.

<if-blocked>
Skill fails → STOP immediately. Report which phase failed and why. Developer re-invokes `/rai-epic-run` after fixing — phase detection resumes automatically.
</if-blocked>

### Step 3: Iterate Stories

When reaching phase 4, read the `### Progress Tracking` table from `scope.md`:

1. Parse rows — columns: Story, Size, Status, Actual, Velocity, Notes
2. Filter rows where Status != "Done"
3. Execute in table order (plan already resolved dependencies)

For each pending story, show `── Story {N}/{total}: {story_id} ──` and invoke `/rai-story-run {story_id}`. After each completes, `/rai-story-close` updates scope.md. When all done, proceed to phase 5.

<verification>
All stories completed. Progress Tracking shows all "Done".
</verification>

### Step 4: Apply Delegation Gates

After **phase 2 (design)** and **phase 3 (plan)**, apply the delegation gate:

| Level | Behavior |
|-------|----------|
| REVIEW | Present summary. Wait for explicit approval. |
| NOTIFY | Present summary. Continue unless user intervenes. |
| AUTO | Continue immediately. |

**Post-design summary:** Story count, sizes, key architectural decisions.
**Post-plan summary:** Milestones, story sequence, estimated timeline.

No gate between stories — each `/rai-story-run` has its own internal gates.

<verification>
Gate applied. Approval received (REVIEW) or notification shown (NOTIFY/AUTO).
</verification>

### Step 5: Complete & Report

After all phases, present summary: phases executed, stories completed/total, delegation level, merge target. Confirm epic merged and branch cleaned up.

<verification>
All phases complete. Epic merged.
</verification>

## Output

| Item | Destination |
|------|-------------|
| All epic + story artifacts | `work/epics/e{N}-{name}/` |
| Merge commit | Development branch |
| Patterns | `.raise/rai/memory/patterns.jsonl` |
| Next | Next epic or release |

## Quality Checklist

- [ ] Phase detection checked in reverse order (most advanced first)
- [ ] `### Progress Tracking` heading used as plan presence marker
- [ ] Story iteration filters Status != "Done" (handles spikes naturally)
- [ ] Each skill and story invoked completely (not overridden)
- [ ] Gates applied only at post-design and post-plan
- [ ] Failure stops immediately — no cascading
- [ ] NEVER create a state file — phase detection is git-derived only
- [ ] NEVER skip stories or reorder them — table order is plan order

## References

- Epic skills: `/rai-epic-start`, `/rai-epic-design`, `/rai-epic-plan`, `/rai-epic-close`
- Story orchestrator: `/rai-story-run` (S325.6)
- Delegation: `~/.rai/developer.yaml`, S325.2
- BacklogHook: S325.4 (fires on `rai signal emit-work` in start/close)
- Design: `s325.7-design.md` (decisions D1-D2-D3-D4)
