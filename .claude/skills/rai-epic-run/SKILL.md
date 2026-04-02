---
name: rai-epic-run
description: >
  Execute epic lifecycle phases (start → design → AR → plan → close),
  pausing at story iteration for human-driven /rai-story-run execution.
  Resumes from last completed phase. Delegation profile controls pause
  behavior at natural gates.
disable-model-invocation: true

license: MIT

metadata:
  raise.work_cycle: epic
  raise.frequency: per-epic
  raise.fase: ""
  raise.prerequisites: ""
  raise.next: ""
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "2.0.0"
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

Execute the epic lifecycle phases (start → design → AR → plan → close), pausing at delegation gates and at story iteration for human-driven `/rai-story-run` execution. Resumes automatically from the last completed phase.

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
| 1 | epic directory exists, no `scope.md` | **design** |
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

Run each epic skill from the detected phase forward. Show `── Phase {N}/6: {skill_name} ──` between phases.

| Phase | Skill | Gate after? |
|:-----:|-------|:-----------:|
| 1 | `/rai-epic-start {epic_id}` | — |
| 2 | `/rai-epic-design {epic_id}` | **POST-DESIGN** |
| 3 | `/rai-architecture-review {epic_id} epic` | **POST-AR** |
| 4 | `/rai-epic-plan {epic_id}` | **POST-PLAN** |
| 5 | Story iteration (see Step 3) | — |
| 6 | `/rai-epic-close {epic_id}` | — |

**Full execution rule:** For each phase, you MUST:
1. Load the skill's SKILL.md (read the file, don't rely on memory)
2. Execute every step in the skill's SKILL.md sequentially — no compression, no skipping
3. Produce all artifacts the skill specifies
4. Only then move to the next phase

The orchestrator delegates — it does not summarize, compress, or shortcut individual skill behavior. A skill invoked through the orchestrator must produce the same output as when invoked standalone.

<if-blocked>
Skill fails → STOP immediately. Report which phase failed and why. Developer re-invokes `/rai-epic-run` after fixing — phase detection resumes automatically.
</if-blocked>

### Step 3: Hand Off Stories

When reaching phase 5 (story iteration), read the `### Progress Tracking` table from `scope.md`:

1. Parse rows — columns: Story, Size, Status, Actual, Velocity, Notes
2. Filter rows where Status != "Done"
3. Present in table order (plan already resolved dependencies)

> **Quality rule — epic-run NEVER executes story-run.**
> Each `/rai-story-run` must run in a fresh session/context so it can
> fork its heavy phases via Agent tool with full context budget.
> Running story-run inside epic-run would accumulate context across
> stories, degrading quality in later stories — the exact problem
> Checkpoint & Fork (ADR-043) was designed to eliminate.
> We never operate at known lower quality levels.

**Present the pending stories and STOP:**

```markdown
## Stories Ready for Execution

| # | Story | Size | Status |
|:-:|-------|:----:|--------|
| 1 | S{N}.1 — {name} | S | Pending |
| 2 | S{N}.2 — {name} | M | Pending |

**Next:** Run each story independently with `/rai-story-run {story_id}`
**Resume:** Re-invoke `/rai-epic-run {epic_id}` when all stories are Done → resumes at close
```

**STOP here.** Do not proceed to phase 6. Do not invoke story-run.
The developer runs each story in a separate session with fresh context.
When all stories are Done, re-invoking `/rai-epic-run` detects phase=close and proceeds.

<verification>
Pending stories presented. Execution paused for human-driven story iteration.
</verification>

### Step 4: Apply Delegation Gates

After **phase 2 (design)**, **phase 3 (AR)**, and **phase 4 (plan)**, apply the delegation gate:

| Level | Behavior |
|-------|----------|
| REVIEW | Present summary. Wait for explicit approval. |
| NOTIFY | Present summary. Continue unless user intervenes. |
| AUTO | Continue immediately. AR SIMPLIFY verdict stops regardless. |

**Post-design summary:** Story count, sizes, key architectural decisions.
**Post-AR summary:** Verdict (PASS/PASS WITH QUESTIONS/SIMPLIFY), proportionality findings, systemic heuristics (H13-H16).
**Post-plan summary:** Milestones, story sequence, estimated timeline.

If AR verdict is SIMPLIFY, STOP regardless of delegation level. Design must be revised before planning.

Story iteration is a mandatory STOP — stories run in separate sessions (see Step 3).

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
- [ ] Each skill's SKILL.md was loaded (read from file) before execution
- [ ] Every step in each skill executed — no compression or shortcuts
- [ ] Gates applied at post-design, post-AR, and post-plan
- [ ] Failure stops immediately — no cascading
- [ ] NEVER create a state file — phase detection is git-derived only
- [ ] NEVER skip stories or reorder them — table order is plan order
- [ ] NEVER compress a skill's steps into a summary — execute each step fully
- [ ] NEVER invoke story-run from epic-run — present list and STOP (ADR-043 quality rule)
- [ ] Stories run in separate sessions with fresh context

## References

- Epic skills: `/rai-epic-start`, `/rai-epic-design`, `/rai-architecture-review`, `/rai-epic-plan`, `/rai-epic-close`
- Story orchestrator: `/rai-story-run` (S325.6)
- Delegation: `~/.rai/developer.yaml`, S325.2
- BacklogHook: S325.4 (fires on `rai signal emit-work` in start/close)
- Design: `s325.7-design.md` (decisions D1-D2-D3-D4)
- F5 constraint & checkpoint protocol: E353 (ADR-043), S353.2, S353.3
