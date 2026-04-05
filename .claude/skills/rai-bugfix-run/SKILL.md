---
name: rai-bugfix-run
description: Run the full 7-phase bugfix pipeline with delegation gates. Use to orchestrate a bug fix.

allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - Agent
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

Execute the full 7-phase bugfix pipeline in one invocation, pausing at the mandatory triage gate and delegation-based gates, resuming automatically from the last completed phase.

**D5 principle:** Skills contain only judgment work. The orchestrator handles all deterministic actions (backlog transitions, Jira assignment, branch cleanup).

## Mastery Levels (ShuHaRi)

- **Shu**: Show phase progress, explain each skill's output, pause at all gates
- **Ha**: Brief progress between phases, pause only when delegation says REVIEW
- **Ri**: Minimal output, AUTO delegation (triage gate still mandatory)

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
| 5 | Code commits on bug branch after `plan.md` timestamp | **review** |
| 4 | `work/bugs/RAISE-{N}/plan.md` | **fix** |
| 3 | `work/bugs/RAISE-{N}/analysis.md` | **plan** |
| 2 | `work/bugs/RAISE-{N}/scope.md` with `^TRIAGE:` | **analyse** |
| 1 | `work/bugs/RAISE-{N}/scope.md` without TRIAGE | **triage** |
| 0 | (nothing) | **start** |

Present: "Phase detection: resuming at **{phase}** (found: {artifact})" or "Starting fresh."

### Step 1: Resolve Delegation

Load `~/.rai/developer.yaml`. Resolve delegation level:

| Source | Resolution |
|--------|-----------|
| `delegation.overrides.rai-bugfix-run` | Per-skill override (highest priority) |
| `delegation.default_level` | Explicit default |
| `experience_level` ShuHaRi | Shu→REVIEW, Ha→NOTIFY, Ri→AUTO |
| No profile | Default to REVIEW |

**Triage gate is ALWAYS mandatory regardless of delegation level.**

### Step 2: Pre-chain Setup (orchestrator responsibility)

Before forking phase 1 (start), the orchestrator handles:

```bash
# Assign bug and transition to In Progress
rai backlog update RAISE-{N} --assignee "{developer-email}" -a jira
rai backlog transition RAISE-{N} in-progress -a jira
```

These are best-effort — failures do not block the pipeline.

### Step 3: Execute Skill Chain

**Chain order:**

| Phase | Skill | Gate after? |
|:-----:|-------|:-----------:|
| 1 | `/rai-bugfix-start RAISE-{N}` | — |
| 2 | `/rai-bugfix-triage RAISE-{N}` | **MANDATORY** (triage gate) |
| 3 | `/rai-bugfix-analyse RAISE-{N}` | delegation gate |
| 4 | `/rai-bugfix-plan RAISE-{N}` | — |
| 5 | `/rai-bugfix-fix RAISE-{N}` | delegation gate |
| 6 | `/rai-bugfix-review RAISE-{N}` | — |
| 7 | `/rai-bugfix-close RAISE-{N}` | — |

**All phases fork** via Agent tool with fresh context. The orchestrator never executes skill logic directly.

#### Fork Execution

For each phase:

1. **Read** the skill's SKILL.md from `.claude/skills/rai-bugfix-{phase}/SKILL.md`
2. **Spawn** Agent tool subagent with prompt template (below)
3. **Wait** for completion
4. **Verify** output: confirm artifact exists on disk
5. **Show** completion banner
6. **Apply** gate if applicable

**Agent prompt template:**

```
Execute the following skill for bug {bug_id}.

## Skill Instructions

{full SKILL.md content}

## Bug Context

- Bug ID: {bug_id}
- Bug path: work/bugs/{bug_id}/
- Prior artifacts on disk: {list existing files}
- Bug branch: {branch name or "not yet created"}

## Your Task

1. Read CLAUDE.md for project-level context and rules
2. Read the prior artifacts listed above from disk
3. Execute every step in the Skill Instructions — no compression, no skipping
4. Write all output artifacts to the correct paths
5. When done, return a brief summary: what you did, artifacts created, and any decisions

ARGUMENTS: {bug_id}
```

**Close phase guardrails — add to close agent prompt:**

```
## Scope Constraints (CRITICAL — close is MR-only)
- ONLY: push branch, create MR, delete local branch
- NEVER edit source code, skill files, config, or governance docs
- NEVER create "fix" or "refactor" commits
- If something looks wrong, return it as a finding — do not act on it
```

**Completion banner (after each phase):**

```markdown
### ✔ Phase {N}/7 — {skill_name}

| | File | Status |
|---|---|---|
| + | `path/to/file.md` | created |
| ~ | `path/to/file.py` | modified |

**Commits:** {count} (`{hash}`) · **Tests:** {count} passed
```

<verification>
Each skill's SKILL.md loaded and all steps executed.
</verification>

<if-blocked>
Skill fails → STOP immediately. Report which phase failed and why. Re-invoke `/rai-bugfix-run` after fixing — phase detection resumes from last artifact.
</if-blocked>

### Step 4: Apply Gates

#### Triage Gate (MANDATORY — always applies)

After phase 2 (triage), present classification using **anti-anchoring design** (D3): show reproduction context BEFORE AI classification.

```
── Triage Gate (MANDATORY) ──

Bug: RAISE-{N} — {summary}

Reproduction:
  WHAT: {from scope.md}
  WHERE: {from scope.md}

AI Classification:
  Bug Type:  {value}
  Severity:  {value}
  Origin:    {value}
  Qualifier: {value}

▸ Confirm classification? [y/edit/reject]
```

| Response | Action |
|----------|--------|
| **y** | Continue to analyse |
| **edit** | Human corrects values → re-run MCP update → continue |
| **reject** | STOP — re-evaluate |

Log overrides in session journal:
```bash
rai session journal add "TRIAGE OVERRIDE: RAISE-{N} — {original} → {corrected}" --type decision
```

#### Delegation Gates (after analyse and fix)

| Level | Behavior |
|-------|----------|
| REVIEW | Present summary. Wait for approval. |
| NOTIFY | Present summary. Continue after 3s. |
| AUTO | Continue immediately. Stop on gate failure. |

### Step 5: Post-chain Cleanup (orchestrator responsibility)

After all phases complete, the orchestrator handles:

```bash
# Transition Jira to Done
rai backlog transition RAISE-{N} done -a jira
```

### Step 6: Complete & Report

```markdown
## Bugfix Run Complete: RAISE-{N}

**Phases:** {start_phase} → close ({N} phases executed)
**Delegation:** {level}
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
| Triage override | {yes/no} |
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
- [ ] Delegation resolved before starting chain
- [ ] Pre-chain: Jira assigned + In Progress (orchestrator, not skill)
- [ ] Triage gate ALWAYS mandatory (even AUTO delegation)
- [ ] Anti-anchoring: reproduction shown BEFORE classification
- [ ] All 7 phases fork via Agent tool with fresh context
- [ ] Each subagent gets only SKILL.md + disk artifacts (no conversation history)
- [ ] Close agent prompt includes scope constraints
- [ ] Post-chain: Jira transitioned to Done (orchestrator, not skill)
- [ ] Failure stops immediately — no cascading
- [ ] NEVER skip the triage gate
- [ ] NEVER pass conversation context to subagents

## References

- Skills: `/rai-bugfix-start`, `-triage`, `-analyse`, `-plan`, `-fix`, `-review`, `-close`
- Pattern: `/rai-story-run` (fork pattern, delegation gates)
- Design: `work/epics/e1286-bugfix-pipeline-orchestration/design.md` (D1-D5)
- Delegation: `~/.rai/developer.yaml`
