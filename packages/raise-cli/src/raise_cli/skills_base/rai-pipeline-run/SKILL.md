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

license: MIT
metadata:
  raise.work_cycle: utility
  raise.frequency: on-demand
  raise.adaptable: 'true'
  raise.version: "1.0.0"
  raise.visibility: public
---

# Pipeline Run

Dispatches phases as forked agents, parses each phase skill's `outcome` block, advances pipeline. Never reads work files.

**Inputs:**
- `pipeline` (bugfix | story | spike | epic | initiative, or a literal `-enterprise` variant, e.g. `bugfix-enterprise` — `pipeline_name` resolves to that exact `{name}.yaml` file, `size` never changes which file loads)
- `issue_id` (Jira key)
- `size` (XS | S | M | L, optional — governs `when: size...` phase gating per ADR-116; unset fails safe to the full phase set, so pass it whenever the caller knows it)

## Supported Pipelines

Phases and skills below match `packages/raise-cli/src/raise_cli/pipeline/pipelines_base/*.yaml` (source of truth — re-check there if a pipeline file changes).

| Pipeline | Phases | Key skills |
|---|---|---|
| bugfix | diagnose → fix → verify → review → pir¹ → close | rai-bugfix-start, rai-bugfix-fix, rai-quality-review, rai-bugfix-review, rai-bugfix-pir, rai-bugfix-close |
| story | start → design¹ → implement → verify → review → close | rai-story-start, rai-story-design, rai-story-implement, rai-quality-review, rai-story-review, rai-story-close |
| spike | start → implement → close | rai-spike-start, rai-spike-journal, rai-spike-close |
| epic | start → design² → stories² → close | rai-epic-start, epic-design-pdcv (sub-pipeline), story ×N (fan-out sub-pipeline), rai-epic-close |
| initiative | shaped → validated → delivering → concluded | rai-initiative-shaped, (deterministic, no skill), rai-initiative-delivering, (inline prompt, no skill) |

¹ `pir` (bugfix) and `design` (story) carry `when: "size != 'XS'"` — skipped when `size=XS`.
² `design`/`stories` are sub-pipeline phases (`pipeline: epic-design-pdcv` / `foreach: stories`), not single-skill dispatches — §2 Dispatch applies to the leaf phases they expand into.

`-enterprise` variants (`bugfix-enterprise`, `story-enterprise`, `spike-enterprise`, `epic-enterprise`, `initiative-enterprise`) are separate, larger phase sets gated by `size` (ADR-116) — pass that literal name as `pipeline` to select one; the Loop below is unchanged.

Note: not every phase skill emits a structured `outcome` block yet (e.g. `rai-bugfix-review`, `rai-bugfix-pir`, `rai-story-design` write only their artifact today). Treat a missing `outcome` as `verdict: PASS` and continue — only the `verify` phase's `outcome.verdict` is load-bearing (drives §2e retry).

## Loop

### 1. Start pipeline
`pipeline_start(pipeline_name={pipeline}, issue_id={issue_id}, cwd="{project_or_worktree_path}", size={size})` → get run_id, first phase, total phases.
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
  Recommended model by cognitive load (this is the orchestrator's *default suggestion*,
  not the final say — see note below):
  - `diagnose`, `fix`, `implement` → `model: "opus"` (deep reasoning + TDD)
  - `verify`, `pir`, `close`, `plan`, `research`, `design` → omit model (inherits active session model)

  **Actual model resolution is layered, not this simple rule (RAISE-13920).** The `model:`
  value this orchestrator passes to `Agent()` is only layer 5 of an 8-layer precedence
  resolved by `parse_skill_model()` in
  `packages/raise-cli/src/raise_cli/pipeline/skill_model.py`, highest to lowest:
  1. Per-skill env var `RAISE_SKILL_MODEL_<SKILL>`
  2. Global env var `RAISE_PIPELINE_MODEL`
  3. Repo config phase-path key (`.raise/skill_models.yaml` → `skills[<phase.path>]`)
  4. Repo config skill key (`.raise/skill_models.yaml` → `skills[<skill_name>]`)
  5. **Pipeline phase YAML `model:` field** ← the recommendation above lives here
  6. `SKILL.md` frontmatter `model:` field of the dispatched skill
  7. Repo config `default:` key
  8. `None` (inherits active session model)

  Layers 1-4 can silently override the recommendation above — that is intentional
  (env vars and `.raise/skill_models.yaml` exist precisely to let operators change routing
  without an MR). If a dispatched phase reports running under a different model than what
  was passed here, check those layers before treating it as drift.

**c. Parse outcome** from agent/skill response (fenced `outcome:` YAML block — `verdict`/`route`/`blocked_reason`, see phase skills' own contract, e.g. `.claude/skills/rai-bugfix-fix/SKILL.md`). If the phase's skill doesn't emit one (see table note above), treat as `verdict: PASS`.

**d. Memorize route:** If phase is diagnose/shape and `outcome` contains `route`, store it for routing.

**e. VERIFY FAIL retry:**
If verify phase returns `outcome.verdict: FAIL`:
- Re-dispatch the preceding FIX/IMPLEMENT phase with `retry_context` = `outcome.blocked_reason` (critical findings) from verify.
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
- Emit complete signal AFTER outcome is ready: `rai signal emit-work story "{issue_id}" --event complete --phase implement`
- Read only the artifacts your own skill declares as inputs (e.g. design.md) — prior-phase state lives in those artifacts and in pipeline engine state, not in a shared journal.
- Commit work after each task.
- End with fenced `outcome` YAML (`verdict`/`route`/`blocked_reason`, <=200 tokens). NOTHING after it.
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
- If any item fails: emit `verdict: FAIL` in `outcome` with critical findings in `blocked_reason`.
- Emit start signal BEFORE any work: `rai signal emit-work story "{issue_id}" --event start --phase verify`
- Emit complete signal AFTER outcome is ready: `rai signal emit-work story "{issue_id}" --event complete --phase verify`
- End with fenced `outcome` YAML (`verdict`/`route`/`blocked_reason`, <=200 tokens). NOTHING after it.
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

## Task
Execute skill /{skill} {issue_id}. Read only the inputs your own skill declares (e.g. scope.md, analysis.md, plan.md) — prior-phase artifacts are each skill's own concern; the orchestrator does not read or write them, and there is no shared journal file.

## Context pointers
{context nodes as "id (type)" — max 10 lines, from raise_graph_context}

## Retry context
{only if re-dispatching after VERIFY FAIL — outcome.blocked_reason / critical findings}

## Signals (required for token measurement)
- FIRST: `rai signal emit-work {work_type} "{issue_id}" --event start --phase {phase_id} 2>/dev/null || true`
- LAST: `rai signal emit-work {work_type} "{issue_id}" --event complete --phase {phase_id} 2>/dev/null || true`

## Rules
- Emit start signal BEFORE any work. Emit complete signal AFTER outcome is ready.
- Commit your work (and artifact) before finishing.
- End with fenced `outcome` YAML (`verdict`/`route`/`blocked_reason`, <=200 tokens). NOTHING after it.
- STOP after your phase. No other skills, no pipeline_* tools.
```

## Constraints
- Never read work files — operate on `outcome` YAML only (pipeline engine state, via `pipeline_status`, is the canonical source of phase progress, not a journal file).
- Pass `model: "opus"` to Agent() for diagnose/fix/implement as the recommended default (layer 5
  of 8 — see §Dispatch phase); omit for all other phases. Env vars and `.raise/skill_models.yaml`
  (layers 1-4, higher precedence) may override this at runtime — that is by design, not drift.
- Always pass `cwd` and `advance_token` to pipeline_advance. Never put advance_token in subagent prompts.
- Always pass `size` in step 1 when known — omitting it fails safe to the full phase set (ADR-116), defeating the lean/default pipelines' purpose.
- Ri: auto-approve gates unless route=incident or new_deps=true.
- VERIFY FAIL is NOT a pipeline gate — orchestrator retries directly (max 2).

**STOP HERE after pipeline completes or is cancelled.** Print phase table and return.
