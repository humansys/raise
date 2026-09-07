---
name: rai-epic-plan
description: Sequence epic stories into milestones and dependencies. Use after epic design, and consume epic UX design when present.
model: sonnet

allowed-tools:
  - Read
  - Grep
  - Glob
  - "Bash(rai:*)"

license: MIT

metadata:
  raise.work_cycle: epic
  raise.frequency: per-epic
  raise.fase: "4"
  raise.prerequisites: epic-design
  raise.next: story-start
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "2.4.0"
  raise.visibility: public
  raise.inputs: |
    - scope: file_path, required, previous_skill
    - ux_design: file_path, optional, previous_skill
  raise.outputs: |
    - scope: file_path, next_skill
  raise.aspects: introspection
  raise.introspection:
    phase: epic.plan
    context_source: scope doc from epic-design plus ux-design artifact when present
    affected_modules: []
    max_tier1_queries: 4
    max_jit_queries: 3
    tier1_queries:
      - "sequencing patterns for {strategy} ordering"
      - "estimation patterns for {size} epics"
      - "milestone patterns for multi-story epics"
      - "related backlog items for {epic_key} --types backlog"
---

# Epic Plan

## Purpose

Transform the story list from `/rai-epic-design`, plus any `ux-design.md` artifact, into a sequenced implementation plan with milestones, parallel work streams, and progress tracking.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps, create sequenced plan with walking skeleton + MVP milestones
- **Ha**: Adjust milestone granularity based on epic size, skip timeline for small epics
- **Ri**: Domain-specific sequencing patterns, team velocity models

## Context

**When to use:** After `/rai-epic-design` has produced a scope document with stories. If the epic is user-facing and `ux-design.md` exists, consume it before sequencing. Run this before the first story starts.

**When to skip:** Very small epics (2-3 stories) with obvious linear sequence. Emergency fixes.

**Inputs:** Epic scope document (`work/epics/e{N}-{name}/scope.md`), calibration data (if available).

## Steps

### PRIME — HARD CONSTRAINT (blocks all subsequent work)

**FORBIDDEN:** You MUST NOT use grep, find, Glob, or Read to explore code UNTIL you have executed at least one `rai graph query`. Your first queries are this skill's tier1 queries (frontmatter `raise.introspection.tier1_queries`) — run them now using the `raise_graph_query` MCP tool with `cwd="{project_or_worktree_path}"`, or the CLI fallback:
```bash
rai graph query "{query}"
```
0 results is valid — the constraint lifts when the queries have run, not when they return results.

**Report:** In your final output, list every graph query you executed and its result count.

Then, before Step 1:

1. **Chain read**: Read `work/epics/e{N}-{name}/design.md` if present, carrying forward its scope and architectural decisions. If `ux-design.md` exists in the same directory, read it too and carry forward workflow/trust-boundary constraints. If neither is present (legacy epic predating these artifacts), note and continue — fall back to `scope.md`.
2. **Emit start**: Signal lifecycle start for observability.

### Step 1: Review Epic Scope

Load and understand the epic scope document:
- Story list with sizes and dependencies
- Done criteria and risks
- Architectural decisions that affect sequencing
- UX workflow, surfaces, and trust boundaries from `ux-design.md` if it exists

<verification>
Can explain epic scope and story dependencies in 60 seconds.
</verification>

<if-blocked>
Epic design incomplete → run `/rai-epic-design` first.
Epic qualifies for UX design but `ux-design.md` is missing → run `/rai-epic-ux-design` before sequencing.
</if-blocked>

### Step 2: Sequence & Rationalize

Order stories using these strategies (in priority order):

| Strategy | When | Rationale |
|----------|------|-----------|
| **Risk-first** | High uncertainty features | Tackle unknowns early while energy is high and time for pivots remains |
| **Walking skeleton** | Architecture unproven | Build minimal E2E path first to prove architecture |
| **Quick wins** | Need momentum | Early deliverable value, validate tooling |
| **Dependency-driven** | Hard blockers exist | Unblock others on critical path |

For each story, document: position, rationale, dependencies (hard/soft/external), what it enables.

> **JIT**: Before choosing sequencing strategy, query graph for ordering patterns and calibration data
> → `aspects/introspection.md § JIT Protocol`

**Identify parallel opportunities:** Stories with no mutual dependencies, different codebase areas, or independent concerns can run concurrently.

<verification>
Every story has sequencing rationale. Critical path identified. Parallel opportunities documented.
</verification>

### Step 3: Define Milestones

Create 2-4 intermediate checkpoints:

| Milestone | Typical scope | Purpose |
|-----------|---------------|---------|
| **M1: Walking Skeleton** | 1-3 stories (smallest E2E) | Prove architecture, enable integration |
| **M2: Core MVP** | 50-70% of stories | Demonstrate value, gather feedback |
| **M3: Feature Complete** | 100% planned stories | Ready for polish |
| **M4: Epic Complete** | Done criteria met | Ready for `/rai-epic-close` |

Per milestone: stories included, success criteria (verifiable), demo capability.

> **JIT**: Before defining milestones, query graph for calibration patterns and checkpoint strategies
> → `aspects/introspection.md § JIT Protocol`

**Integration checkpoint:** For epics with multiple components (client/server, CLI/API, frontend/backend), schedule an **E2E integration milestone** before the final story. This checkpoint runs real infrastructure (docker compose, actual DB) and verifies cross-story contracts (auth headers, payload schemas, parameter limits). Unit tests with mocks cannot catch these mismatches — only real E2E validates the seams between stories.

<verification>
At least 2 milestones defined with clear success criteria. Multi-component epics include E2E integration checkpoint.
</verification>

### Step 4: Setup Tracking

Add progress tracking to epic scope using `templates/plan-section.md`:
- Story sequence table with status/actual/velocity columns
- Milestone checklist with target dates
- Velocity assumptions from calibration data (if available)

<verification>
Tracking table added to epic scope document.
</verification>

### Step 5: Update Scope Document

Append the implementation plan section to `work/epics/e{N}-{name}/scope.md` via CLI (preserves existing content + publishes to Confluence):

Use `raise_docs_write` MCP tool with doc_type="epic-scope", title="E{N}: {epic-name} scope + plan", content="existing work/epics/e{N}-{name}/scope.md contents plus ## Implementation Plan, ## Milestones, and ### Sequencing Risks sections", output_path="work/epics/e{N}-{name}/scope.md", cwd="{project_or_worktree_path}".
If MCP tools are not available, fall back to:
```bash
rai docs write epic-scope \
  --title "E{N}: {epic-name} scope + plan" \
  --stdin \
  --output-path work/epics/e{N}-{name}/scope.md << EOF
$(cat work/epics/e{N}-{name}/scope.md)

## Implementation Plan
{story sequence with rationale}

## Milestones
{milestones with success criteria}

{parallel work streams if any}

{progress tracking table}

### Sequencing Risks
{top 3 risks}
EOF
```

Note: unquoted heredoc so `$(cat ...)` expands the existing scope content.

Present plan to human for review before starting first story.

<verification>
Scope document updated. Plan reviewable in <5 minutes. Human acknowledges.
</verification>

## Output

| Item | Destination |
|------|-------------|
| Implementation plan | Appended to `work/epics/e{N}-{name}/scope.md` |
| Plan template | `templates/plan-section.md` |
| Next | `/rai-story-design` for first story in sequence |

Backlog transition to implement status is engine-owned (RAISE-15034):
Engine performs the transition via `apply_phase_transition` at phase completion.
No skill-initiated transition call required or allowed.
**Standalone-mode notice** (RAISE-16988): When no pipeline run is active, the tracker is **not** moved — `apply_phase_transition` requires the engine. In standalone execution, report explicitly:
> "⚠️ Tracker not updated: this skill ran standalone (no active pipeline run). Backlog status unchanged. Run the pipeline or update the tracker manually."

**Engine behavior** (RAISE-16987): The engine checks `ExecutionContext` to determine mode:
- `mode: pipeline` — `apply_phase_transition` moves the tracker. No skill call required or allowed.
- `mode: standalone` — tracker is **not** moved. Report explicitly:
  > "⚠️ Tracker not updated: this skill ran standalone (no active pipeline run). Backlog status unchanged. Run the pipeline or update the tracker manually."

  To force a transition standalone: `rai backlog transition {key} --point {workflow_point}`

**STOP HERE.** Return your summary to the orchestrator. Do NOT invoke any further skill.

## Quality Checklist

- [ ] All stories sequenced with rationale
- [ ] Critical path identified
- [ ] At least 2 milestones (walking skeleton + MVP minimum)
- [ ] Dependencies verified — no cycles, blockers identified
- [ ] Parallel opportunities documented (or explained why sequential)
- [ ] Progress tracking in scope document
- [ ] NEVER over-plan — plans are hypotheses, not commitments
- [ ] NEVER sequence by size alone — use risk-first as default
- [ ] Multi-component epics include E2E integration checkpoint

## References

- Plan template: `templates/plan-section.md`
- Previous: `/rai-epic-design` (produces scope input) + `/rai-epic-ux-design` when the epic is user-facing
- Next: `/rai-story-design` for first story
- Close: `/rai-epic-close`
- Calibration: `.raise/rai/memory/calibration.jsonl`
