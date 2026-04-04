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

Resolve the bug path from `bug_id`. Check artifacts in **reverse order** — take the most advanced phase:

| Check | Artifact | If exists → resume at |
|:-----:|----------|----------------------|
| 6 | `work/bugs/RAISE-{N}/retro.md` | **close** |
| 5 | Code commits on bug branch after `plan.md` timestamp | **review** |
| 4 | `work/bugs/RAISE-{N}/plan.md` | **fix** |
| 3 | `work/bugs/RAISE-{N}/analysis.md` | **plan** |
| 2 | `work/bugs/RAISE-{N}/scope.md` with TRIAGE block | **analyse** |
| 1 | `work/bugs/RAISE-{N}/scope.md` without TRIAGE block | **triage** |
| 0 | (nothing) | **start** |

To detect TRIAGE block, grep for `^TRIAGE:` in `scope.md`.

To detect code commits after plan (check 5): compare `git log --oneline bug/raise-{N}/*` commit timestamps against `plan.md` mtime, or check for commits with `fix(RAISE-{N})` message prefix.

Present: "Phase detection: resuming at **{phase}** (found: {artifact})" or "Starting fresh — no artifacts found."

<verification>
Phase identified. Bug path resolved.
</verification>

### Step 1: Resolve Delegation

Load developer profile from `~/.rai/developer.yaml`. Resolve delegation level:

| Source | Resolution |
|--------|-----------|
| `delegation.overrides.rai-bugfix-run` | Per-skill override (highest priority) |
| `delegation.default_level` | Explicit default |
| `experience_level` ShuHaRi | Shu→REVIEW, Ha→NOTIFY, Ri→AUTO |
| No profile | Default to REVIEW |

**Important:** Triage gate is ALWAYS mandatory regardless of delegation level. Even AUTO delegation pauses at triage.

Present: "Delegation: **{level}** (triage gate always mandatory)"

<verification>
Delegation level resolved. Triage gate confirmed mandatory.
</verification>

### Step 2: Execute Skill Chain

Run each skill from the detected phase forward.

**Phase banner (before starting):**

```
── Phase {N}/7: {skill_name} ──
```

**Completion banner (after finishing each phase):**

```markdown
### ✔ Phase {N}/7 — {skill_name}

| | File | Status |
|---|---|---|
| + | `path/to/new-file.md` | created |
| ~ | `path/to/modified-file.py` | modified |

**Commits:** 1 (`abc1234`) · **Tests:** {count} passed
```

**Chain order:**

| Phase | Skill | Execution | Gate after? |
|:-----:|-------|:---------:|:-----------:|
| 1 | `/rai-bugfix-start RAISE-{N}` | **fork** | — |
| 2 | `/rai-bugfix-triage RAISE-{N}` | **fork** | **MANDATORY** (triage gate) |
| 3 | `/rai-bugfix-analyse RAISE-{N}` | **fork** | delegation gate |
| 4 | `/rai-bugfix-plan RAISE-{N}` | **fork** | — |
| 5 | `/rai-bugfix-fix RAISE-{N}` | **fork** | delegation gate |
| 6 | `/rai-bugfix-review RAISE-{N}` | **fork** | — |
| 7 | `/rai-bugfix-close RAISE-{N}` | **fork** | — |

**All phases fork.** The orchestrator is a pure coordinator — it never executes skill logic directly. This keeps the orchestrator context minimal and prevents context saturation that degrades quality in later phases.

#### Fork Execution

Each fork phase runs in a **fresh-context subagent** via the Agent tool.

**For each fork phase:**

1. **Read** the skill's SKILL.md from `.claude/skills/rai-bugfix-{phase}/SKILL.md`
2. **Spawn** an Agent tool subagent with:
   - `subagent_type: "general-purpose"`
   - `prompt`: the agent prompt template below, filled with skill content and bug context
3. **Wait** for agent completion
4. **Verify** output:
   - Artifact-producing phases (start, triage, analyse, plan, review): confirm file exists on disk
   - Fix phase: confirm test gates pass
   - Close: confirm MR URL from agent return value
5. **Show** completion banner in main thread
6. **Apply** gate if applicable (in main thread)

**Agent prompt template:**

```
Execute the following skill for bug {bug_id}.

## Skill Instructions

{paste the full SKILL.md content here}

## Bug Context

- Bug ID: {bug_id}
- Bug path: work/bugs/{bug_id}/
- Prior artifacts on disk: {list each file that exists, e.g. scope.md, analysis.md}
- Bug branch: bug/raise-{N}/{slug} (or "not yet created" for start phase)

## Your Task

1. Read CLAUDE.md for project-level context and rules
2. Read the prior artifacts listed above from disk
3. Execute every step in the Skill Instructions — no compression, no skipping
4. Write all output artifacts to the correct paths
5. When done, return a brief summary: what you did, artifacts created, and any decisions

ARGUMENTS: {bug_id}
```

**Critical rules for fork execution:**
- The subagent gets the SKILL.md as its prompt — it executes the full skill naturally in fresh context
- Do NOT pass conversation history or prior phase results to the subagent — only disk artifacts and SKILL.md
- The orchestrator stays thin — it only reads summaries and checks for artifacts between forks
- A skill invoked through fork must produce the same output as when invoked standalone

**Close phase (phase 7) guardrails — MANDATORY in close agent prompt:**

Add to the close agent prompt, in addition to the SKILL.md:

```
## Scope Constraints (CRITICAL — close is MR-only)
- ONLY: push branch, create MR, delete local branch, transition Jira, emit signals
- NEVER edit source code, skill files, config files, or governance docs
- NEVER create "fix" or "refactor" commits — report issues, do not repair them
- NEVER delete directories, worktrees, or files outside the bug branch
- NEVER revert or modify commits already on the dev branch
- If something looks wrong, return it as a finding in your summary — do not act on it
```

<verification>
Each skill's SKILL.md was loaded and all its steps executed before proceeding.
</verification>

<if-blocked>
Skill fails → STOP immediately. Report which phase failed and why. The developer re-invokes `/rai-bugfix-run` after fixing the issue — phase detection resumes from the last completed artifact.
</if-blocked>

### Step 3: Apply Gates

#### Triage Gate (MANDATORY — always applies)

After **phase 2 (triage)**, present the classification for human **active verification**. This gate uses anti-anchoring design (D3): show reproduction context BEFORE AI classification to prevent anchoring bias.

```
── Triage Gate (MANDATORY) ──

Bug: RAISE-{N} — {summary from Jira or scope.md}

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
| **y** (confirm) | Continue to analyse |
| **edit** | Human selects correct values via conversation → re-run triage MCP update with corrected values → continue |
| **reject** | STOP. Bug returns to triage for re-evaluation |

Log override rate: if human edits classification, record in session journal:

```bash
rai session journal add "TRIAGE OVERRIDE: RAISE-{N} — AI said {original}, human changed to {corrected}" --type decision
```

#### Delegation Gates (after analyse and fix)

After **phase 3 (analyse)** and **phase 5 (fix)**, apply the delegation gate:

| Level | Behavior |
|-------|----------|
| REVIEW | Present summary. Wait for explicit approval before continuing. |
| NOTIFY | Present summary. Continue after 3 seconds unless user intervenes. |
| AUTO | Continue immediately. Gates still stop on test/lint/type failure. |

**Post-analyse summary:** Root cause, fix approach, analysis method used.
**Post-fix summary:** Tasks completed, tests passing, files changed, bug no longer reproduces.

<verification>
Gates applied. Triage approved (or edited). Delegation gates resolved.
</verification>

### Step 4: Complete & Report

After all phases complete, present:

```markdown
## Bugfix Run Complete: RAISE-{N}

**Phases:** {start_phase} → close ({N} phases executed)
**Delegation:** {level}
**Result:** MR created targeting `{dev_branch}` ({mr_url})

### Artifacts
| Phase | File | Op |
|-------|------|:--:|
| start | `work/bugs/RAISE-{N}/scope.md` | + |
| triage | `.raise/artifacts/RAISE-{N}-triage.yaml` | + |
| analyse | `work/bugs/RAISE-{N}/analysis.md` | + |
| plan | `work/bugs/RAISE-{N}/plan.md` | + |
| fix | `src/path/to/file.py` | ~ |
| fix | `tests/path/to/test.py` | + |
| review | `work/bugs/RAISE-{N}/retro.md` | + |

### Classification
{Bug Type} / {Severity} / {Origin} / {Qualifier}
{override: yes/no}

### Metrics
| Metric | Value |
|--------|-------|
| Tests | {count} passed |
| Commits | {total} across 7 phases |
| Patterns | {PAT-IDs or "none"} |
| Jira | RAISE-{N} → Done |
| Triage override | {yes: original→corrected / no} |
```

File paths MUST use backticks so they are clickable in the terminal. Use actual paths, not placeholders.

<verification>
All phases complete. MR created. Bug branch cleaned up.
</verification>

## Output

| Item | Destination |
|------|-------------|
| All bug artifacts | `work/bugs/RAISE-{N}/` |
| Typed triage artifact | `.raise/artifacts/RAISE-{N}-triage.yaml` |
| Merge request | GitLab MR: bug branch → `{dev_branch}` |
| Patterns | `.raise/rai/memory/patterns.jsonl` |
| Calibration | Via `rai signal emit-calibration` |
| Next | Next bug or epic work |

## Quality Checklist

- [ ] Phase detection checked in reverse order (most advanced first)
- [ ] Delegation resolved from profile before starting chain
- [ ] Triage gate is ALWAYS mandatory (even with AUTO delegation)
- [ ] Anti-anchoring: reproduction shown BEFORE AI classification in triage gate
- [ ] Triage override rate logged to session journal
- [ ] All 7 phases spawn Agent tool subagent with full SKILL.md as prompt
- [ ] Each subagent gets fresh context — no conversation history passed
- [ ] Artifact-producing forks verified by checking file on disk
- [ ] Delegation gates applied at post-analyse and post-fix (in main thread)
- [ ] Close agent prompt includes scope constraints guardrails
- [ ] Failure stops immediately — no cascading to next phase
- [ ] NEVER create a state file — phase detection is artifact-derived only
- [ ] NEVER skip the triage gate — it is the highest-leverage checkpoint
- [ ] NEVER pass conversation context to forked subagent — only disk artifacts + SKILL.md

## References

- Skills: `/rai-bugfix-start`, `/rai-bugfix-triage`, `/rai-bugfix-analyse`, `/rai-bugfix-plan`, `/rai-bugfix-fix`, `/rai-bugfix-review`, `/rai-bugfix-close`
- Pattern: `/rai-story-run` (fork pattern, delegation gates)
- Design: `work/epics/e1286-bugfix-pipeline-orchestration/design.md` (D1-D4)
- Evidence: AgentIF (NeurIPS 2025), Agentless (FSE '25), Kim et al. (Google/MIT)
- Delegation: `~/.rai/developer.yaml`
