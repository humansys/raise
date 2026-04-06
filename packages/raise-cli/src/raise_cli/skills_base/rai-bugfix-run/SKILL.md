---
name: rai-bugfix-run
description: Run the full 7-phase bugfix pipeline with 3 HITL gates. Use to orchestrate a bug fix.

allowed-tools:
  - Read
  - Edit
  - Write
  - Grep
  - Glob
  - Bash
  - Skill

license: MIT

metadata:
  raise.work_cycle: bugfix
  raise.frequency: per-bug
  raise.fase: ""
  raise.prerequisites: ""
  raise.next: ""
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: 2.4.0
  raise.visibility: internal
  raise.skillset: raise-maintainability
  raise.inputs: |
    - bug_id: string, required, argument (e.g. "RAISE-251")
  raise.outputs: |
    - mr_url: string, git
    - retro_md: file_path (work/bugs/RAISE-{N}/retro.md)
    - patterns: list, cli (via rai pattern add)
---

# Bugfix Run

## Purpose

Execute the full 7-phase bugfix pipeline inline (no subagents), pausing at 3 fixed HITL gates where human judgment prevents cascading errors.

**Design principles:**
- **D5:** Skills contain only judgment work. Orchestrator handles deterministic actions.
- **D6:** Inline execution, no subagents. Skills are short enough (<600w) for high compliance without context isolation. 3 fixed HITL gates replace delegation levels.

## Mastery Levels (ShuHaRi)

- **Shu**: Explain each phase output, pause at all 3 gates with full context
- **Ha**: Brief progress between phases, gates still mandatory
- **Ri**: Minimal output, gates still mandatory (gates are never skippable)

## Context

**When to use:** Starting or resuming any tracked bug fix. Replaces manual sequential skill invocation.

**When to skip:** Single-phase work (e.g., only running review on an already-fixed bug). Individual skills remain independently invocable.

**Inputs:** Bug ID (e.g., RAISE-251).

## Steps

### Step 0: Detect Phase

Check artifacts in **reverse order** — take the most advanced phase:

| Check | Artifact | If exists → resume at |
|:-----:|----------|----------------------|
| 6 | `work/bugs/RAISE-{N}/retro.md` | **close** |
| 5 | Code commits on bug branch after `plan.md` | **review** |
| 4 | `work/bugs/RAISE-{N}/plan.md` | **fix** |
| 3 | `work/bugs/RAISE-{N}/analysis.md` | **plan** |
| 2 | `work/bugs/RAISE-{N}/scope.md` with `^TRIAGE:` | **analyse** |
| 1 | `work/bugs/RAISE-{N}/scope.md` without TRIAGE | **triage** |
| 0 | (nothing) | **start** |

Present: "Phase detection: resuming at **{phase}**" or "Starting fresh."

**Abbreviation rule:** If resuming at **analyse** or later (scope+triage pre-exist from a prior session), GATE 1 is skipped — the scope was already validated when it was created. GATE 2 and GATE 3 are always mandatory.

### Step 0.5: Already-Resolved Check

Before creating a worktree or starting work, verify the bug isn't already fixed:

1. Check Jira comments for resolution evidence: `rai backlog get-comments RAISE-{N} -a jira`
2. Search release branch for fix commits: `git log release/{version} --grep="RAISE-{N}" --oneline`
3. If evidence of prior fix found, present to user:

```
── Already-Resolved Check ──

RAISE-{N} may already be fixed:
  {evidence: Jira comment / commit / code change}

▸ Continue with bugfix pipeline? [y/close]
```

If user says **close** → transition Jira to Done, skip entire pipeline. This prevents wasting a worktree on resolved bugs.

### Step 1: Pre-chain Setup (orchestrator responsibility)

Before starting, handle Jira assignment (best-effort, non-blocking):

```bash
rai backlog update RAISE-{N} --assignee "{developer-email}" -a jira
rai backlog transition RAISE-{N} in-progress -a jira
```

Query the graph for relevant context (single query, non-blocking):

```bash
rai graph query "bugs patterns {component or keywords from bug summary}" --types pattern --limit 5
```

If graph returns results, present them as context before starting phase 1. If graph is unavailable (e.g., worktree without index), note and continue — graph context is enrichment, not a gate.

### Step 2: Execute Skill Chain

Execute each phase inline by reading the SKILL.md and following its steps directly. No subagents.

**Chain order:**

| Phase | Skill | Then |
|:-----:|-------|:----:|
| 1 | `/rai-bugfix-start` | → **GATE 1** |
| 2 | `/rai-bugfix-triage` | ↓ |
| 3 | `/rai-bugfix-analyse` | → **GATE 2** |
| 4 | `/rai-bugfix-plan` | ↓ |
| 5 | `/rai-bugfix-fix` | → **GATE 3** |
| 6 | `/rai-bugfix-review` | ↓ |
| 7 | `/rai-bugfix-close` | done |

**Per phase:**

1. Read `.claude/skills/rai-bugfix-{phase}/SKILL.md`
2. Execute every step — no compression, no skipping
3. Show completion banner
4. If gate follows → present gate, wait for human

**Completion banner:**

```markdown
### ✔ Phase {N}/7 — {skill_name}

| | File | Status |
|---|---|---|
| + | `path/to/file.md` | created |
| ~ | `path/to/file.py` | modified |

**Commits:** {count} (`{hash}`)
```

<verification>
Each phase's steps fully executed before proceeding.
</verification>

<if-blocked>
Phase fails → STOP immediately. Report which phase and why. Re-invoke `/rai-bugfix-run` after fixing — phase detection resumes from last artifact.
</if-blocked>

### Step 3: HITL Gates

#### GATE 1: Scope Confirmation (after start + triage)

After phases 1-2, present for human verification:

```
── GATE 1: Scope & Classification ──

Bug: RAISE-{N} — {summary}

Reproduction:
  WHAT: {from scope.md}
  WHERE: {from scope.md}
  Reproduces: {yes/no}

Classification:
  Bug Type:  {value}
  Severity:  {value}
  Origin:    {value}
  Qualifier: {value}

▸ Is this the right problem with the right classification? [y/edit/reject]
```

| Response | Action |
|----------|--------|
| **y** | Continue to analyse |
| **edit** | Human corrects scope or classification → update artifacts + MCP → continue |
| **reject** | STOP — re-evaluate problem definition |

#### GATE 2: Analysis & Strategy (after analyse)

After phase 3, present root cause and **multiple fix approaches** with trade-offs. This is the highest-value gate — it caught an over-engineered strategy in the 2026-04-05 session (code fallback vs. simple gitignore fix). Always present at least 2 options.

```
── GATE 2: Root Cause & Strategy ──

Root cause: {from analysis.md}
Method: {5 Whys / Ishikawa / Direct}
Evidence: {key evidence supporting root cause}

Fix approaches:
  A: {simplest approach} — {trade-off}
  B: {recommended approach} — {trade-off}
  C: {most thorough approach} — {trade-off}  (if applicable)

Recommended: {A/B/C} because {reasoning}

▸ Which approach? [a/b/c/adjust/reject]
```

| Response | Action |
|----------|--------|
| **a/b/c** | Continue to plan + fix with selected approach |
| **adjust** | Human refines strategy → update analysis.md → continue |
| **reject** | STOP — re-analyse with different hypotheses |

**Bias toward simplicity:** If the simplest approach (A) fully addresses the root cause, recommend it. Code changes are not always the answer — configuration, documentation, or process fixes may be simpler and more durable.

#### GATE 3: Fix Verification (after fix)

After phase 5, present fix results:

```
── GATE 3: Fix Verification ──

Tasks completed: {N}/{total}
Tests: {count} passed
Bug reproduces: {no — verified}

Files changed:
  {list of modified files}

▸ Does the fix look correct? [y/reject]
```

| Response | Action |
|----------|--------|
| **y** | Continue to review + close |
| **reject** | STOP — human reviews code, identifies issues |

### Step 4: Post-chain Cleanup (orchestrator responsibility)

After all phases complete:

```bash
rai backlog transition RAISE-{N} done -a jira
```

### Step 5: Complete & Report

```markdown
## Bugfix Run Complete: RAISE-{N}

**Phases:** {start_phase} → close ({N} phases executed)
**Result:** MR created targeting `{dev_branch}` ({mr_url})

### Artifacts
| Phase | File | Op |
|-------|------|:--:|
| start | `work/bugs/RAISE-{N}/scope.md` | + |
| triage | `work/bugs/RAISE-{N}/scope.md` | ~ |
| analyse | `work/bugs/RAISE-{N}/analysis.md` | + |
| plan | `work/bugs/RAISE-{N}/plan.md` | + |
| fix | `src/path/to/file.py` | ~ |
| review | `work/bugs/RAISE-{N}/retro.md` | + |

### Classification
{Bug Type} / {Severity} / {Origin} / {Qualifier}

### Metrics
| Metric | Value |
|--------|-------|
| Tests | {count} passed |
| Commits | {total} across 7 phases |
| Patterns | {PAT-IDs or "none"} |
| Jira | RAISE-{N} → Done |
```

## Output

| Item | Destination |
|------|-------------|
| All bug artifacts | `work/bugs/RAISE-{N}/` |
| Merge request | GitLab MR: bug branch → `{dev_branch}` |
| Patterns | `.raise/rai/memory/patterns.jsonl` |
| Next | Next bug or epic work |

## Quality Checklist

- [ ] Phase detection checked in reverse order
- [ ] Already-resolved check run before creating worktree (Step 0.5)
- [ ] Pre-chain: Jira assigned + In Progress (orchestrator, not skill)
- [ ] All 7 phases executed inline (no subagents)
- [ ] GATE 1 presented after start+triage (skip only if resuming at analyse+)
- [ ] GATE 2 presents multiple fix approaches with trade-offs (bias toward simplest)
- [ ] GATE 3 (fix verification) presented after fix
- [ ] GATE 2 and GATE 3 are always mandatory — never skippable
- [ ] Post-chain: Jira transitioned to Done (orchestrator, not skill)
- [ ] Failure stops immediately — no cascading

## References

- Skills: `/rai-bugfix-start`, `-triage`, `-analyse`, `-plan`, `-fix`, `-review`, `-close`
- Design: `work/epics/e1286-bugfix-pipeline-orchestration/design.md` (D1-D6)
