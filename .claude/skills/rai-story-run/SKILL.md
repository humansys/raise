---
name: rai-story-run
description: >
  Chain the full story lifecycle (start → design → plan → implement →
  architecture review → quality review → review → close) in one
  invocation. Resumes from last completed phase using git-derived
  artifact detection. Delegation profile controls pause behavior.
disable-model-invocation: true

license: MIT

metadata:
  raise.work_cycle: story
  raise.frequency: per-story
  raise.fase: ""
  raise.prerequisites: ""
  raise.next: ""
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "2.1.0"
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

### Step 0: Detect Phase & Story Type

Resolve the epic and story paths from `story_id`. Check artifacts in **reverse order** — take the most advanced phase:

| Check | Artifact | If exists → resume at |
|:-----:|----------|----------------------|
| 5 | `stories/s{N}.{M}-retrospective.md` | **close** |
| 4 | `stories/s{N}.{M}-plan.md` | **implement** |
| 3 | `stories/s{N}.{M}-design.md` | **plan** |
| 2 | `stories/s{N}.{M}-story.md` | **design** |
| 1 | story branch exists (`story/s{N}.{M}/*`) | **start** (branch only, no artifacts) |
| 0 | (nothing) | **start** (from scratch) |

**Detect story type** from the `type` field in `stories/s{N}.{M}-story.md` frontmatter:

| Type | Meaning | Phases skipped |
|------|---------|----------------|
| `code` (default) | Produces source code | None — full 8-phase chain |
| `docs` | Documentation, guardrails, governance artifacts | AR (phase 5), QR (phase 6) |
| `analysis` | Research, audit, assessment — no deliverable code | AR (phase 5), QR (phase 6) |

If `type` is missing or unrecognized, default to `code`.

Present: "Phase detection: resuming at **{phase}** (found: {artifact}), type: **{type}**" or "Starting fresh — no artifacts found."

<verification>
Phase identified. Epic path resolved. Story type detected.
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

Run each skill from the detected phase forward.

**Phase banner (before starting):**

```
── Phase {N}/8: {skill_name} ──
```

**Completion banner (after finishing each phase):**

Use a markdown heading + table so that file paths are clickable in the terminal:

```markdown
### ✔ Phase {N}/8 — {skill_name}

| | File | Status |
|---|---|---|
| + | `path/to/new-file.md` | created |
| ~ | `path/to/modified-file.py` | modified |

**Commits:** 1 (`abc1234`) · **Tests:** 3463 passed
```

Rules for the completion banner:
- Use markdown table (NOT ASCII box-drawing) so file paths are clickable
- File paths in backticks, relative to project root
- `+` for created, `~` for modified, `-` for deleted
- Only list files the skill actually touched (not inherited from prior phases)
- Commits and tests on a single summary line below the table
- For gate phases (design, implement, AR, QR), add verdict/summary on a separate line
- If phase produced no file changes (e.g., close is just merge), show merge commit hash instead of file table

**Chain order:**

| Phase | Skill | Execution | Gate after? | Skip for docs/analysis? |
|:-----:|-------|:---------:|:-----------:|:-----------------------:|
| 1 | `/rai-story-start {story_id}` | **fork** | — | no |
| 2 | `/rai-story-design {story_id}` | **fork** | POST-DESIGN | no |
| 3 | `/rai-story-plan {story_id}` | **fork** | — | no |
| 4 | `/rai-story-implement {story_id}` | **fork** | POST-IMPLEMENT | no |
| 5 | `/rai-architecture-review {story_id} story` | **fork** | POST-AR | **yes** |
| 6 | `/rai-quality-review {story_id}` | **fork** | POST-QR | **yes** |
| 7 | `/rai-story-review {story_id}` | **fork** | — | no |
| 8 | `/rai-story-close {story_id}` | **fork** | — | no |

**Story type skipping:** When `type` is `docs` or `analysis`, skip phases 5 (AR) and 6 (QR) entirely. Present: "Skipping phase {N} ({skill_name}) — story type is **{type}**, no code to review." Then continue to the next applicable phase.

**All phases fork.** The orchestrator is a pure coordinator — it never executes skill logic directly. This keeps the terminal output clean (subagent output is contained) and the orchestrator context minimal.

#### Fork phases (all 8)

Each fork phase runs in a **fresh-context subagent** via the Agent tool. This eliminates context saturation that degrades quality in later phases.

**For each fork phase:**

1. **Read** the skill's SKILL.md from `src/raise_cli/skills_base/rai-{skill-name}/SKILL.md`
2. **Spawn** an Agent tool subagent with:
   - `subagent_type: "general-purpose"`
   - `prompt`: the agent prompt template below, filled with skill content and story context
3. **Wait** for agent completion
4. **Verify** output:
   - Artifact-producing phases (start, design, plan, implement, review): confirm file exists on disk
   - Verdict phases (AR, QR): read verdict from agent return value
   - Close: confirm merge commit from agent return value
5. **Show** completion banner in main thread
6. **Apply** delegation gate if applicable (in main thread)

**Agent prompt template:**

```
Execute the following skill for story {story_id}.

## Skill Instructions

{paste the full SKILL.md content here}

## Story Context

- Story ID: {story_id}
- Epic: {epic_id}
- Epic path: work/epics/{epic_slug}/
- Stories path: work/epics/{epic_slug}/stories/
- Prior artifacts on disk: {list each file that exists for this story, e.g. s353.2-story.md, s353.2-design.md}

## Your Task

1. Read CLAUDE.md for project-level context and rules
2. Read the prior artifacts listed above from disk
3. Execute every step in the Skill Instructions — no compression, no skipping
4. Write all output artifacts to the correct paths
5. When done, return a brief summary: what you did, artifacts created, and any verdicts or decisions

ARGUMENTS: {story_id}
```

**Critical rules for fork execution:**
- The subagent gets the SKILL.md as its prompt — it executes the full skill naturally in fresh context
- Do NOT pass conversation history or prior phase results to the subagent — only disk artifacts and SKILL.md
- The orchestrator stays thin — it only reads summaries and checks for artifacts between forks
- A skill invoked through fork must produce the same output as when invoked standalone

<verification>
Each skill's SKILL.md was loaded and all its steps executed before proceeding.
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

For `docs`/`analysis` stories, phases 5 and 6 are skipped, so their delegation gates don't apply.

<verification>
Gate applied. Approval received (REVIEW) or notification shown (NOTIFY/AUTO).
</verification>

### Step 4: Complete & Report

After all phases complete, present:

```markdown
## Story Run Complete: {story_id}

**Phases:** {start_phase} → close ({N} phases executed)
**Delegation:** {level}
**Type:** {code|docs|analysis}
**Result:** Merged to `{parent_branch}` (`{merge_commit_hash}`)

### Artifacts
| Phase | File | Op |
|-------|------|:--:|
| start | `work/epics/.../stories/s{N}.{M}-story.md` | + |
| start | `work/epics/.../stories/s{N}.{M}-scope.md` | + |
| design | `work/epics/.../stories/s{N}.{M}-design.md` | + |
| plan | `work/epics/.../stories/s{N}.{M}-plan.md` | + |
| implement | `src/path/to/file.py` | ~ |
| implement | `tests/path/to/test.py` | ~ |
| review | `work/epics/.../stories/s{N}.{M}-retrospective.md` | + |

### Metrics
| Metric | Value |
|--------|-------|
| Tests | {count} passed |
| Commits | {total_count} across {phases_count} phases |
| Patterns | {PAT-IDs or "none"} |
| Jira | {ticket} → {status} |
```

File paths MUST use backticks so they are clickable in the terminal. Use actual paths, not placeholders — the table above is a template.

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
- [ ] Story type detected from frontmatter (`code`/`docs`/`analysis`)
- [ ] Delegation resolved from profile before starting chain
- [ ] All applicable phases spawn Agent tool subagent with full SKILL.md as prompt
- [ ] AR and QR skipped for `docs`/`analysis` stories (with message)
- [ ] Each subagent gets fresh context — no conversation history passed
- [ ] Artifact-producing forks verified by checking file on disk
- [ ] AR/QR verdicts read from agent return value
- [ ] Gates applied at post-design, post-implement, post-AR, and post-QR (in main thread)
- [ ] Failure stops immediately — no cascading to next phase
- [ ] NEVER create a state file — phase detection is git-derived only
- [ ] NEVER skip a skill in the chain unless story type allows it
- [ ] NEVER pass conversation context to forked subagent — only disk artifacts + SKILL.md

## References

- Skills: `/rai-story-start`, `/rai-story-design`, `/rai-story-plan`, `/rai-story-implement`, `/rai-architecture-review`, `/rai-quality-review`, `/rai-story-review`, `/rai-story-close`
- Delegation: `~/.rai/developer.yaml`, S325.2
- BacklogHook: S325.4 (fires on `rai signal emit-work` in start/close)
- Design: `s325.6-design.md` (decisions D1-D2-D3)
