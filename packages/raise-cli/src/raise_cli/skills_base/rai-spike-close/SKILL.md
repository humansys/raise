---
name: rai-spike-close
description: Capture spike decision and close with minimal retrospective. Use after research or prototype complete.
model: opus

allowed-tools:
  - Read
  - Edit
  - Write
  - Grep
  - Glob
  - "Bash(rai:*)"
  - "Bash(git:*)"

license: MIT

metadata:
  raise.work_cycle: spike
  raise.frequency: per-spike
  raise.fase: "3"
  raise.prerequisites: rai-spike-start
  raise.next: ""
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "1.0.0"
  raise.visibility: public
  raise.inputs: |
    - scope_path: file_path, required, previous_skill
  raise.outputs: |
    - decision: string, terminal
raise.mastery:
  shu: "Explain decision options and retrospective value"
  ha: "Present only the decision and key learning"
  ri: "Tool call → one-line confirmation → done"
---

# Spike Close

## Purpose

Capture the spike's decision and a minimal retrospective. Update the scope
artifact, transition Jira to done, and commit.

## Mastery Levels (ShuHaRi)

- **Shu**: Explain decision options and retrospective value
- **Ha**: Present only the decision and key learning
- **Ri**: Minimal — decision captured, Jira done, committed

## Context

**When to use:** After research or prototype work is complete.

**When to skip:** Spike was cancelled (transition Jira to Cancelled manually).

**Inputs:** Spike scope artifact (`work/spikes/SP-{slug}/scope.md`), research
outputs (evidence catalog, prototype, etc.).

## Steps

### Pipeline Context Check (RAISE-10715)

Before executing any step, verify this skill was invoked via the pipeline engine:

1. Check if `Run ID:` appears in the context above (injected by `pipeline/prompt.py`)
2. If **present**: continue silently — pipeline is orchestrating
3. If **absent**: **STOP and present HITL gate:**

> **Standalone execution detected.** This skill is running outside the pipeline engine.
> Prior phases (research) may have been skipped.
>
> Options:
> 1. Continue anyway (acknowledge that prior phases were skipped)
> 2. Abort and investigate why the pipeline engine is not orchestrating

Wait for the user's explicit choice before proceeding. This gate fires even in Ri mode — standalone execution is a signal of broken infrastructure, not a routine gate.

### Step 1: Determine decision

Review the spike's outputs and determine the decision:

| Decision | Meaning |
|----------|---------|
| **go** | Sufficient evidence/validation — proceed to implementation (create epic/story) |
| **no-go** | Hypothesis invalidated or approach not viable — document why |
| **needs-more-data** | Inconclusive — document what's missing, may spawn follow-up spike |

### Step 2: Update scope artifact

Read `work/spikes/SP-{slug}/scope.md` and update the `## Decision` section:

```markdown
## Decision

**Verdict:** {go|no-go|needs-more-data}

{2-3 sentences explaining the rationale. Reference evidence catalog or prototype findings.}

**Next action:** {What happens next — epic key, follow-up spike, or "archived"}

## Retrospective

{1 paragraph — what we learned, what surprised us, what we'd do differently.
This is NOT the full story retrospective template — keep it brief.}
```

### Step 3: Commit

```bash
git add work/spikes/SP-{slug}/
git commit -m "spike(SP-{slug}): close — {verdict}

Decision: {verdict}
{1-line rationale}

Jira: {KEY}

Co-Authored-By: Rai <rai@humansys.ai>"
```

### Step 4: Present

```
## Spike SP-{slug} — Closed
**Decision:** {verdict}
**Rationale:** {1-line}
**Next:** {action}
```

**STOP HERE.** Return your summary to the orchestrator. Do NOT invoke any further skill.

## Output

| Item | Destination |
|------|-------------|
| Updated scope | `work/spikes/SP-{slug}/scope.md` |
| Close commit | On current branch |

## Quality Checklist

- [ ] Decision is one of: go, no-go, needs-more-data
- [ ] Rationale references actual findings (not generic)
- [ ] Retrospective is 1 paragraph (not the full story template)
- [ ] Next action is specific (epic key, follow-up spike, or "archived")

## References

- Previous: `/rai-spike-start`, `/rai-research`
- Pipeline: `spike.yaml`

## Backlog tracker

**Engine behavior** (RAISE-16987): The engine checks `ExecutionContext` to determine mode:
- `mode: pipeline` — engine active; `apply_phase_transition` moves the tracker. No skill call required.
- `mode: standalone` — no active run; tracker is **not** moved automatically.

If standalone (`mode == standalone` via `ExecutionContext`):
```bash
rai backlog transition {key} --point after:spike:close
```
