---
name: rai-story-run
description: >
  Chain the full story lifecycle (start → design → plan → implement →
  architecture review → quality review → review → close) in one
  invocation. Resumes from last completed phase using git-derived
  artifact detection. Delegation profile controls pause behavior.

license: MIT

metadata:
  raise.work_cycle: story
  raise.frequency: per-story
  raise.fase: ""
  raise.prerequisites: ""
  raise.next: ""
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "1.0.0"
  raise.visibility: public
  raise.inputs: |
    - story_id: string, required, argument (e.g. "S325.6")
    - epic_id: string, optional, argument (inferred from story_id prefix)
  raise.outputs: |
    - merge_commit: string, git
    - retrospective_md: file_path (work/epics/.../stories/s{N}.{M}-retrospective.md)
    - patterns: list, cli (via rai pattern add)
---

# Story Run

## Purpose

Execute the full story lifecycle in one invocation, pausing only at delegation gates and resuming automatically from the last completed phase.

## Mastery Levels (ShuHaRi)

- **Shu**: Show phase progress, explain each skill's output, pause at both gates
- **Ha**: Brief progress between phases, pause only when delegation says REVIEW
- **Ri**: Minimal output, AUTO delegation, gates stop only on failure

## Context

**When to use:** Starting or resuming any story. Replaces manual sequential skill invocation.

**When to skip:** Single-phase work (e.g., only running review on an already-implemented story). Individual skills remain independently invocable.

## Steps

### Step 0: Detect Phase

Resolve the epic and story paths from `story_id`. Check artifacts in **reverse order** — take the most advanced phase:

| Check | Artifact | If exists → resume at |
|:-----:|----------|----------------------|
| 5 | `stories/s{N}.{M}-retrospective.md` | **close** |
| 4 | `stories/s{N}.{M}-plan.md` | **implement** |
| 3 | `stories/s{N}.{M}-design.md` | **plan** |
| 2 | `stories/s{N}.{M}-story.md` | **design** |
| 1 | story branch exists (`story/s{N}.{M}/*`) | **start** (branch only, no artifacts) |
| 0 | (nothing) | **start** (from scratch) |

Present: "Phase detection: resuming at **{phase}** (found: {artifact})" or "Starting fresh — no artifacts found."

<verification>
Phase identified. Epic path resolved.
</verification>

### Step 1: Resolve Delegation

Load developer profile from `~/.rai/developer.yaml`. Resolve delegation level:

| Source | Resolution |
|--------|-----------|
| `delegation.overrides.rai-story-run` | Per-skill override (highest priority) |
| `delegation.default_level` | Explicit default |
| `experience_level` ShuHaRi | Shu→REVIEW, Ha→NOTIFY, Ri→AUTO |
| No profile | Default to REVIEW |

Present: "Delegation: **{level}**"

<verification>
Delegation level resolved.
</verification>

### Step 2: Execute Skill Chain

Run each skill from the detected phase forward. Between skills, show progress:

```
── Phase {N}/8: {skill_name} ──
```

**Chain order:**

| Phase | Skill | Gate after? |
|:-----:|-------|:-----------:|
| 1 | `/rai-story-start {story_id}` | — |
| 2 | `/rai-story-design {story_id}` | **POST-DESIGN** |
| 3 | `/rai-story-plan {story_id}` | — |
| 4 | `/rai-story-implement {story_id}` | **POST-IMPLEMENT** |
| 5 | `/rai-architecture-review {story_id} story` | **POST-AR** |
| 6 | `/rai-quality-review {story_id}` | **POST-QR** |
| 7 | `/rai-story-review {story_id}` | — |
| 8 | `/rai-story-close {story_id}` | — |

Each skill invocation follows its own SKILL.md completely — the orchestrator delegates, it does not override individual skill behavior.

<verification>
Each skill completes successfully before proceeding to the next.
</verification>

<if-blocked>
Skill fails → STOP immediately. Report which phase failed and why. The developer re-invokes `/rai-story-run` after fixing the issue — phase detection resumes from the last completed artifact.
</if-blocked>

### Step 3: Apply Delegation Gates

After **phase 2 (design)**, **phase 4 (implement)**, **phase 5 (AR)**, and **phase 6 (QR)**, apply the delegation gate:

| Level | Behavior |
|-------|----------|
| REVIEW | Present summary of completed phase. Wait for explicit approval before continuing. |
| NOTIFY | Present summary. Continue after 3 seconds unless user intervenes. |
| AUTO | Continue immediately. Gates still stop on test/lint/type failure or AR/QR SIMPLIFY/FAIL verdict. |

**Post-design summary:** Approach, components affected, key decisions.
**Post-implement summary:** Tasks completed, tests passing, files changed.
**Post-AR summary:** Verdict (PASS/PASS WITH QUESTIONS/SIMPLIFY), findings count, key heuristics triggered.
**Post-QR summary:** Verdict (PASS/PASS WITH RECOMMENDATIONS/FAIL), findings count, fixes applied.

If AR verdict is SIMPLIFY or QR verdict is FAIL, STOP regardless of delegation level. Fixes must be applied before proceeding.

<verification>
Gate applied. Approval received (REVIEW) or notification shown (NOTIFY/AUTO).
</verification>

### Step 4: Complete & Report

After all phases complete, present:

```markdown
## Story Run Complete: {story_id}

**Phases:** {start_phase} → close ({N} phases executed)
**Delegation:** {level}
**Artifacts:** story.md, design.md, plan.md, retrospective.md
**Result:** Merged to {parent_branch}
```

<verification>
All phases complete. Story merged and branch cleaned up.
</verification>

## Output

| Item | Destination |
|------|-------------|
| All story artifacts | `work/epics/e{N}-{name}/stories/` |
| Merge commit | Parent branch (epic or dev) |
| Patterns | `.raise/rai/memory/patterns.jsonl` |
| Calibration | Via `rai signal emit-calibration` |
| Next | Next story or `/rai-epic-close` |

## Quality Checklist

- [ ] Phase detection checked in reverse order (most advanced first)
- [ ] Delegation resolved from profile before starting chain
- [ ] Each skill invoked completely (not partially or overridden)
- [ ] Gates applied at post-design, post-implement, post-AR, and post-QR
- [ ] Failure stops immediately — no cascading to next phase
- [ ] NEVER create a state file — phase detection is git-derived only
- [ ] NEVER skip a skill in the chain (even if developer says "just close it")

## References

- Skills: `/rai-story-start`, `/rai-story-design`, `/rai-story-plan`, `/rai-story-implement`, `/rai-architecture-review`, `/rai-quality-review`, `/rai-story-review`, `/rai-story-close`
- Delegation: `~/.rai/developer.yaml`, S325.2
- BacklogHook: S325.4 (fires on `rai signal emit-work` in start/close)
- Design: `s325.6-design.md` (decisions D1-D2-D3)
