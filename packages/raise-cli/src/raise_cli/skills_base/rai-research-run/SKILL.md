---
name: rai-research-run
description: Adaptive research pipeline orchestrator. Dispatches phases as forked agents, routes by depth.
allowed-tools:
  - Read
  - Agent
  - Bash
  - Skill
  - "mcp__rai-workspace__pipeline_*"
  - "mcp__rai-workspace__raise_signal_emit"
metadata:
  raise.work_cycle: research
  raise.frequency: per-research
  raise.version: "1.0.0"
  raise.visibility: public
---

# Research Run

## Purpose

Orchestrate the adaptive research pipeline. Dispatches phases as forked agents, routes phases by depth (quick/standard/deep), and handles phase transitions. Never reads work files directly — operates on phase_result YAML only.

## Inputs

- `question`: the research question (string)
- `depth`: optional override (quick|standard|deep) — if omitted, Frame phase determines it
- `topic`: optional slug for the work directory — if omitted, derived from question

## Steps

### Step 1: Start Pipeline

If MCP pipeline tools are available:
```
pipeline_start(pipeline=research, issue_id={topic}, cwd="{cwd}")
```

If not available, track state manually via journal.

### Step 2: Phase Loop

Execute phases in order. For each phase:

**a. Route check:**
Read the phase's `when` condition from the pipeline definition. Evaluate against the memorized route (depth). If condition fails → skip, advance to next phase.

| Phase | Condition | Runs when |
|-------|-----------|-----------|
| frame | always | always |
| scope | `route != 'quick'` | standard, deep |
| search | always | always |
| evidence | `route != 'quick'` | standard, deep |
| verify | `route == 'deep'` | deep only |
| critic | `route == 'deep'` | deep only |
| synthesize | always | always |

**b. Dispatch phase:**
Use fresh agents (not forks) to enable model override per phase:

```
Agent({
  subagent_type: "general-purpose",
  model: "{model_for_phase}",
  name: "research-{phase_id}",
  prompt: "Execute skill /rai-research-{phase_id} for topic '{topic}'.
    Working directory: {cwd}
    Journal: {cwd}/work/research/{topic}/journal.md

    Read the skill SKILL.md and follow all steps.
    Append your section to the journal before finishing.
    End with fenced phase_result YAML block. NOTHING after it.
    STOP after your phase.

    {full context: question, depth, prior phase artifacts}"
})
```

Model assignment (validated by A/B experiment — see work/research/observability-dashboards-raise-server-v2):
- `frame`, `scope`, `search`, `evidence` → `model: "sonnet"` (mechanical, 53% cheaper)
- `verify`, `critic` → `model: "opus"` (adversarial reasoning)
- `synthesize` → `model: "fable"` (cross-source synthesis, best quality in testing)

**c. Parse phase_result** from agent response.

**d. Memorize route:** If phase is `frame` and phase_result contains `route`, store it for routing subsequent phases.

**e. Advance pipeline:**
If MCP available: `pipeline_advance(run_id, phase={phase_id}, cwd={cwd})`

**f. Gate:** If synthesize phase completes and has HITL gate → present summary to user.

### Step 3: On Complete

Print phase table:

```markdown
## Research Pipeline Complete: {topic}

| Phase | Status | Key Metric |
|-------|--------|------------|
| frame | done | depth={route} |
| scope | {done|skipped} | {angle_count} angles |
| search | done | {source_count} sources |
| evidence | {done|skipped} | {claim_count} claims |
| verify | {done|skipped} | {survived}/{verified} survived |
| critic | {done|skipped} | verdict={verdict} |
| synthesize | done | confidence={confidence} |

**Report:** `work/research/{topic}/{topic}-report.md`
**Recommendation:** {one-line from synthesize phase_result}
```

## Constraints

- Never read work files — operate on phase_result YAML only
- Fork agents for phases; orchestrator stays thin
- Route is determined once (frame phase) and applied to all subsequent phases
- Max 1 re-search loop in critic phase (handled by critic skill internally)
- Failure in any phase → STOP, report which phase and why
