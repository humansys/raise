---
name: rai-pipeline-run
description: Thin pipeline orchestrator. Dispatches phases as forked agents, never reads work files.
allowed-tools:
  - Read
  - Agent
  - Bash
  - "mcp__rai-workspace__pipeline_*"
  - "mcp__rai-workspace__raise_signal_emit"
  - "mcp__rai-workspace__raise_graph_context"
---

# Pipeline Run

Dispatches phases as forked agents, parses phase_result, advances pipeline. Never reads work files.

**Inputs:** `pipeline` (bugfix | story | spike | epic | initiative), `issue_id` (Jira key).

## Supported Pipelines

| Pipeline | Phases | Key skills |
|---|---|---|
| bugfix | start → diagnose → fix → verify → close | rai-bugfix-start, rai-bugfix-fix, rai-quality-review, rai-bugfix-close |
| story | start → implement → verify → close | rai-story-start, rai-story-implement, rai-quality-review, rai-story-close |
| spike | start → research → close | rai-spike-start, rai-spike-journal, rai-spike-close |
| epic | start → close | rai-epic-start, rai-epic-close |
| initiative | start → design → close | rai-epic-start (initiative mode), rai-epic-design, rai-epic-close |

## Loop

### 1. Start pipeline
`pipeline_start(pipeline={pipeline}, issue_id={issue_id}, cwd="{project_or_worktree_path}")` → get run_id, first phase, total phases.
Store `cwd` = current working directory.
Store `advance_token` from the response. **Never** include it in subagent prompts.
Derive `work_type`: `bugfix` → `bug`; `story` → `story`; all others → use pipeline name verbatim.

### 2. For each phase

**a. Route check:**
If phase has `when` condition (e.g. `when: route=incident`) and memorized route doesn't match → skip:
`pipeline_advance(run_id, phase={phase_id}, cwd={cwd}, advance_token={advance_token})` without dispatch.

**b. Dispatch phase:**
- **verify phase** → `Agent()` with Opción A verify directive (see §Opción A Directives). No model override.
- **implement phase (Opción A)** → `Agent()` with Opción A implement directive (see §Opción A Directives).
- **all other phases** → `Agent()` with pointer-only prompt (template below).
  Model assignment by cognitive load:
  - `diagnose`, `fix`, `implement` → `model: "opus"` (deep reasoning + TDD)
  - `verify`, `pir`, `close`, `plan`, `research`, `design` → omit model (inherits active session model)

**c. Parse phase_result** from agent/skill response (fenced YAML block).

**d. Memorize route:** If phase is diagnose/shape and phase_result contains `route`, store it for routing.

**e. VERIFY FAIL retry:**
If verify phase returns `verdict: FAIL`:
- Re-dispatch the preceding FIX/IMPLEMENT phase with `retry_context` = Critical findings from verify.
- Re-run verify. Max 2 iterations total.
- Still FAIL after 2 → `status: blocked`, present to user.

**f. Advance pipeline:**
`pipeline_advance(run_id, phase={phase_id}, cwd={cwd}, advance_token={advance_token})`

**g. Gates:** If `status: gate` → present summary+gate_note. Ri auto-approve unless route=incident or new_deps=true. Revise → re-dispatch. Abort → `pipeline_cancel`. When the human gives a directional decision at a gate or mid-phase, persist it with `pipeline_decision` before continuing.

### 3. On complete
Print phase table:
```
| Phase | Status | Verdict/Summary | Commit |
|-------|--------|-----------------|--------|
```

## Opción A Directive Prompts

When a pipeline uses enterprise skills (`rai-story-implement`, `rai-quality-review`) for implement or verify phases, inject the following directive context into the Agent() prompt.

### implement phase directive

```
## Opción A Directive — Implement Phase

You are executing the implement phase in Opción A mode (AI-only implementation).

Rules:
- Follow TDD strictly: RED → GREEN → REFACTOR for every task.
- Use `raise_task_complete` after completing each task (not just at story end).
- Emit start signal BEFORE any work: `rai signal emit-work story "{issue_id}" --event start --phase implement`
- Emit complete signal AFTER phase_result is ready: `rai signal emit-work story "{issue_id}" --event complete --phase implement`
- Append only YOUR section to the journal. Update only YOUR frontmatter keys.
- Commit journal + work after each task.
- End with fenced phase_result YAML (<=200 tokens). NOTHING after it.
- STOP after your phase. No other skills, no pipeline_* tools.

Attribution (auto-injected by orchestrator):
  pipeline: {pipeline}
  phase: implement
  skill: rai-story-implement
  issue_id: {issue_id}
```

### verify phase directive

```
## Opción A Directive — Verify Phase

You are executing the verify phase in Opción A mode (AR checklist + attestation).

Rules:
- Run the full AR (Architecture Review) checklist against the implementation.
- Attest each item: pass / fail / not-applicable.
- If any item fails: emit verdict=fail in phase_result with Critical findings listed.
- Emit start signal BEFORE any work: `rai signal emit-work story "{issue_id}" --event start --phase verify`
- Emit complete signal AFTER phase_result is ready: `rai signal emit-work story "{issue_id}" --event complete --phase verify`
- End with fenced phase_result YAML (<=200 tokens). NOTHING after it.
- STOP after your phase. No other skills, no pipeline_* tools.

Attribution (auto-injected by orchestrator):
  pipeline: {pipeline}
  phase: verify
  skill: rai-quality-review
  issue_id: {issue_id}
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
- FIRST: `rai signal emit-work {work_type} "{issue_id}" --event start --phase {phase_id} 2>/dev/null || true`
- LAST: `rai signal emit-work {work_type} "{issue_id}" --event complete --phase {phase_id} 2>/dev/null || true`

## Rules
- Emit start signal BEFORE any work. Emit complete signal AFTER phase_result is ready.
- Append only YOUR section to journal. Update only YOUR frontmatter keys.
- Commit journal + work before finishing.
- End with fenced phase_result YAML (<=200 tokens). NOTHING after it.
- STOP after your phase. No other skills, no pipeline_* tools.
```

## Constraints
- Never read work files — operate on phase_result YAML only.
- Pass `model: "opus"` to Agent() for diagnose/fix/implement only; omit for all other phases.
- Always pass `cwd` and `advance_token` to pipeline_advance. Never put advance_token in subagent prompts.
- Ri: auto-approve gates unless route=incident or new_deps=true.
- VERIFY FAIL is NOT a pipeline gate — orchestrator retries directly (max 2).

**STOP HERE after pipeline completes or is cancelled.** Print phase table and return.
