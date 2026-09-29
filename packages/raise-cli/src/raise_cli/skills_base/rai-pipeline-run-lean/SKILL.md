---
name: rai-pipeline-run-lean
description: Thin pipeline orchestrator. Dispatches phases as forked agents, never reads work files.
allowed-tools:
  - Read
  - Agent
  - Bash
  - "mcp__rai-workspace__pipeline_*"
  - "mcp__rai-workspace__raise_signal_emit"
  - "mcp__rai-workspace__raise_graph_context"
metadata:
  raise.visibility: public
  raise.version: 1.0.0
  raise.frequency: per-pipeline
  raise.skillset: raise-maintainability
---

# Pipeline Run (Lean)

Dispatches phases as forked agents, parses phase_result, advances pipeline. Never reads work files.

**Inputs:** `pipeline` (bugfix-lean | story), `issue_id` (Jira key). Note: story-lean was promoted to canonical `story` (ADR-143 C1, RAISE-15356).

## Loop

### 1. Start pipeline
`pipeline_start(pipeline={pipeline}, issue_id={issue_id}, cwd="{project_or_worktree_path}")` → get run_id, first phase, total phases.
Store `cwd` = current working directory.

### 2. For each phase

**a. Route check:**
If phase has `when` condition (e.g. `when: route=incident`) and memorized route doesn't match → skip:
`pipeline_advance(run_id, phase={phase_id}, cwd={cwd})` without dispatch.

**b. Dispatch phase:**
- **verify phase** → `Skill("rai-work-verify", args="{issue_id}")` with `context: fork`.
- **all other phases** → `Agent()` with pointer-only prompt (template below).
  Model assignment by cognitive load (hardcoded, YAML is documentation):
  - `diagnose`, `fix` → `model: "claude-opus-4-6"` (deep reasoning + TDD)
  - `verify`, `pir`, `close` → omit model (inherits session model — Sonnet)

**c. Parse phase_result** from agent/skill response (fenced YAML block).

**d. Memorize route:** If phase is diagnose/shape and phase_result contains `route`, store it for routing.

**e. VERIFY FAIL retry:**
If verify phase returns `verdict: FAIL`:
- Re-dispatch the preceding FIX phase with `retry_context` = Critical findings from verify.
- Re-run verify. Max 2 iterations total.
- Still FAIL after 2 → `status: blocked`, present to user.

**f. Advance pipeline:**
`pipeline_advance(run_id, phase={phase_id}, cwd={cwd})`

**g. Gates:** If `status: gate` → present summary+gate_note. Ri auto-approve unless route=incident or new_deps=true. Revise → re-dispatch. Abort → `pipeline_cancel`. When the human gives a directional decision at a gate or mid-phase, persist it with `pipeline_decision` before continuing.

### 3. On complete
Print phase table:
```
| Phase | Status | Verdict/Summary | Commit |
|-------|--------|-----------------|--------|
```

## Agent prompt template (<=2K tokens)

```
You are executing phase "{phase_id}" ({n}/{total}) for {issue_id}.
Working directory: {cwd}
Journal: {cwd}/work/{bugs|stories}/{issue_id}/journal.md

## Task
Execute skill /{skill} {issue_id}. Journal is your ONLY input from prior phases.

## Context pointers
{context nodes as "id (type)" — max 10 lines, from raise_graph_context}

## Retry context
{only if re-dispatching after VERIFY FAIL — Critical findings}

## Signals (required for token measurement)
- FIRST: `rai signal emit-work bug "{issue_id}" --event start --phase {phase_id} 2>/dev/null || true`
- LAST: `rai signal emit-work bug "{issue_id}" --event complete --phase {phase_id} 2>/dev/null || true`

## Rules
- Emit start signal BEFORE any work. Emit complete signal AFTER phase_result is ready.
- Append only YOUR section to journal. Update only YOUR frontmatter keys.
- Commit journal + work before finishing.
- End with fenced phase_result YAML (<=200 tokens). NOTHING after it.
- STOP after your phase. No other skills, no pipeline_* tools.
```

## Constraints
- Never read work files — operate on phase_result YAML only.
- Pass `model: "claude-opus-4-6"` to Agent() for diagnose/fix only; omit for all other phases.
- Always pass `cwd` to pipeline_advance.
- Ri: auto-approve gates unless route=incident or new_deps=true.
- VERIFY FAIL is NOT a pipeline gate — orchestrator retries directly (max 2).

**STOP HERE after pipeline completes or is cancelled.** Print phase table and return.
