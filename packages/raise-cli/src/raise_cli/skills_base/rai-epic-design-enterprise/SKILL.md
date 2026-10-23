---
name: rai-epic-design-enterprise
description: Design epic scope, stories, and architecture. Use for work spanning 3-10 features.
model: opus

allowed-tools:
  - Read
  - Edit
  - Grep
  - Glob
  - "Bash(rai:*)"

license: MIT

metadata:
  raise.work_cycle: epic
  raise.frequency: per-epic
  raise.fase: "3"
  raise.prerequisites: project-backlog
  raise.next: epic-ux-design
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "2.3.0"
  raise.visibility: public
  raise.inputs: |
    - brief: file_path, optional, previous_skill
    - scope: file_path, required, previous_skill
  raise.outputs: |
    - scope: file_path, next_skill
    - design: file_path, optional, next_skill
  raise.aspects: introspection
  raise.introspection:
    phase: epic.design
    context_source: problem brief or strategic objective
    affected_modules: []
    max_tier1_queries: 4
    max_jit_queries: 5
    tier1_queries:
      - "patterns for {affected_modules} architecture decisions"
      - "risks and failure modes in {domain} epics"
      - "prior epic designs with similar scope ({story_count} stories)"
      - "related backlog items for {epic_key} --types backlog"
---

# Epic Design

## Purpose

Design an epic that bridges strategic objectives to executable stories, making key architectural decisions and defining bounded scope for incremental delivery.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps, create full scope document and ADRs
- **Ha/Ri**: Adjust depth based on complexity, lightweight ADRs, custom patterns

## Context

**When to use:** Starting work spanning 3-10 stories. Design is the gemba walk at epic scale — go see what exists, challenge assumptions, prevent waste.

**When to skip:** Single-story work → `/rai-story-design`. Bug fixes → issue tracker. High uncertainty → `/rai-research` first.

**Inputs:** Business objective, project backlog, constraints. Optionally: Problem Brief from `/rai-problem-shape` or Epic Brief from `/rai-epic-start`.

## Steps

### PRIME — HARD CONSTRAINT (blocks all subsequent work)

**FORBIDDEN:** You MUST NOT use grep, find, Glob, or Read to explore code UNTIL you have executed at least one `rai graph query`. Your first queries are this skill's tier1 queries (frontmatter `raise.introspection.tier1_queries`) — run them now using the `raise_graph_query` MCP tool with `cwd="{project_or_worktree_path}"`, or the CLI fallback:
```bash
rai graph query "{query}"
```
0 results is valid — the constraint lifts when the queries have run, not when they return results.

**Report:** In your final output, list every graph query you executed and its result count.

Then, before Step 1:

1. **Emit start**: Signal lifecycle start for observability.
2. **Backlog transition** — engine owned (RAISE-15034):
   Transition to design status is performed by the pipeline engine via `apply_phase_transition`.
   No skill-initiated transition call required or allowed.
   **Standalone-mode notice** (RAISE-16988): When no pipeline run is active, the tracker is **not** moved — `apply_phase_transition` requires the engine. In standalone execution, report explicitly:
> "⚠️ Tracker not updated: this skill ran standalone (no active pipeline run). Backlog status unchanged. Run the pipeline or update the tracker manually."

**Engine behavior** (RAISE-16987): The engine checks `ExecutionContext` to determine mode:
- `mode: pipeline` — `apply_phase_transition` moves the tracker. No skill call required or allowed.
- `mode: standalone` — tracker is **not** moved. Report explicitly:
  > "⚠️ Tracker not updated: this skill ran standalone (no active pipeline run). Backlog status unchanged. Run the pipeline or update the tracker manually."

  To force a transition standalone: `rai backlog transition {key} --point {workflow_point}`

### Step 1: Load Brief & Frame Objective

Check for Epic Brief (`work/epics/e{N}-{name}/brief.md`) or Problem Brief (`work/problem-briefs/*.md`). If found, use hypothesis and boundaries as starting input.

Define what this epic accomplishes:
- **Objective**: Business/user outcome (1-2 sentences, outcome-focused)
- **Value**: Why this matters, what's unlocked after completion
- **In scope (MUST/SHOULD)**: Non-negotiable vs nice-to-have deliverables
- **Out of scope**: Excluded items with rationale and deferral destination

Scoping heuristic: defer what doesn't block the objective; separate what needs its own ADRs.

> **JIT**: Before defining scope boundaries, query graph for prior designs with similar scope
> → `aspects/introspection.md § JIT Protocol`

<verification>
Objective explainable to non-technical stakeholder in 60 seconds. Scope boundaries explicit.
</verification>

### Step 2: Gemba Walk (mandatory — do not skip)

Go to the actual codebase. Read what exists before designing what's next.

1. **Read the modules** this epic will touch. Understand current state, not just the graph abstraction.

**Module Health Check** — before proposing stories, check if any touched module is a known drift hotspot:

```bash
# Replace MOD_TOKEN with module name fragments (e.g. "auth", "pipeline", "graph")
cat governance/drift-hotspots.json 2>/dev/null | python3 -c "
import json, sys
MOD_TOKENS = ['MOD_TOKEN']  # replace with actual module name fragments
data = json.load(sys.stdin)
hits = [m for m in data.get('ranked_modules', []) if any(t in m.get('id', '') for t in MOD_TOKENS)]
for m in hits[:5]: print(f'{m[\"id\"]}: rank {m[\"rank\"]}, signals {m[\"signal_count\"]}')
" 2>/dev/null || echo "(hotspots.json not available — skip)"
```

If a module appears in the top-10 ranked list: flag it in this epic's scope.md §Risks section with the signal count. See `governance/drift-catalog.md` for signal definitions. Graceful degradation: if `hotspots.json` is absent, skip silently.

2. **Search for existing implementations**: grep for similar functionality, patterns, components. Before proposing new stories, verify they won't duplicate what exists.
3. **Check established patterns**: how does the codebase already solve similar problems? Follow existing patterns rather than inventing new ones.
4. **Map the real dependencies**: what actually imports what? What breaks if you change X?

Use `raise_graph_context` MCP tool with module_id="mod-{name}", `cwd="{project_or_worktree_path}"`.
If MCP tools are not available, fall back to: `rai graph context mod-{name} --format json`

```bash
grep -r "similar_pattern" packages/  # real code
```

| Finding | Action |
|---------|--------|
| Similar component exists | Reuse or extend — do NOT propose a duplicate story |
| Established pattern found | Follow it — consistency > novelty |
| Over-engineered existing code | Consider a simplification story instead of building on top |

<verification>
Actual code read. No duplicate components will be proposed. Existing patterns identified.
</verification>

### Step 3: Assess Architecture & ADRs

Create ADRs when: multiple valid approaches with significant impact, new technology adoption, decisions other epics depend on. Skip when patterns are established or details are easily changed.

> **JIT**: Before making architectural decisions, query graph for patterns and known risks
> → `aspects/introspection.md § JIT Protocol`

If significant uncertainty: `/rai-research` (timebox 2-4 hours), then create ADRs.
ADR template: `.raise/templates/architecture/adr.md`. One decision per ADR.

Publish each ADR to local path and docs adapter:

Use `raise_docs_write` MCP tool with doc_type="adr", title="ADR-YYYY-MM-DD-{slug}: {Decision Title}", content="[ADR content following .raise/templates/architecture/adr.md structure]", output_path="governance/adrs/adr-YYYY-MM-DD-{slug}.md", cwd="{project_or_worktree_path}".
**Verify result:** If `result.status != "ok"`, stop immediately with error:
  `ADR write failed: {result.error}. Cannot continue without docs sync in connected mode.`
If MCP tools are not available, fall back to:
```bash
rai docs write adr \
  --title "ADR-{NNN}: {Decision Title}" \
  --stdin \
  --output-path governance/adrs/adr-YYYY-MM-DD-{slug}.md << 'EOF'
[ADR content following .raise/templates/architecture/adr.md structure]
EOF
```
**If exit code != 0, stop immediately** — do not proceed to scope creation.

**Capability-registry check (RAISE-14654):** if the ADR names a canonical, single-implementation
mechanism (a function/service/endpoint that all callers must use — the same shape as an existing
`governance/capability-registry.yaml` card), add or update that card in the same MR. This is how a
decision becomes discoverable at design time instead of only living in ADR prose — the root cause
found in RAISE-14654 was ADRs naming canonical mechanisms that never got promoted into the registry.
Skip silently when the ADR doesn't name such a mechanism (most don't).

<verification>
Technical direction clear enough to define stories. ADRs created for significant decisions.
</verification>

### Step 4: Break Down Stories (MVP mentality)

Decompose epic into 3-10 independently deliverable stories. Apply lean principles:

- **KISS**: Each story does one thing well. If explanation takes >2 sentences, split it.
- **YAGNI**: Only stories that serve the stated objective. "Nice to have" goes to parking lot.
- **DRY**: Check gemba findings — if a story duplicates existing functionality, remove or reframe as extension.
- **Everything is an MVP**: Each story delivers the simplest version that proves value. Gold-plating goes to follow-up epics.

**Per story:** ID (S{N}.{seq}), name, 1-line description, T-shirt size (XS/S/M/L), dependencies.

> **JIT**: Before finalizing decomposition, query graph for sizing patterns in similar epics
> → `aspects/introspection.md § JIT Protocol`

Target: each story delivers demonstrable value, 1-5 days duration. No dependency cycles. External blockers identified.

**Waste check**: For each proposed story, ask: "What happens if we don't build this?" If the epic still achieves its objective, the story is not essential — defer it.

<verification>
Each story passes "independently deliverable" test. Dependency graph is acyclic. No story duplicates existing functionality.
</verification>

### Step 5: Define Done & Risks

**Done:** All stories complete + epic-specific measurable criteria + architecture docs updated + retrospective completed.

**Risks:** Top 3 with likelihood/impact/mitigation.

> **JIT**: Before assessing risks, query graph for known risks from related epics
> → `aspects/introspection.md § JIT Protocol`

<verification>
Done criteria are measurable. Top risks have mitigations.
</verification>

### Step 6: Write Artifacts & Parking Lot

Create TWO documents via CLI:

1. `scope.md` (WHAT + WHY): objective, stories, boundaries, done criteria:

Use `raise_docs_write` MCP tool with doc_type="epic-scope", title="E{N}: {epic-name} scope", content="[scope content following templates/scope.md]", output_path="work/epics/e{N}-{name}/scope.md", cwd="{project_or_worktree_path}".
**Verify result:** If `result.status != "ok"`, stop immediately with error:
  `Epic scope write failed: {result.error}. Cannot continue without docs sync in connected mode.`
If MCP tools are not available, fall back to:
```bash
rai docs write epic-scope \
  --title "E{N}: {epic-name} scope" \
  --stdin \
  --output-path work/epics/e{N}-{name}/scope.md << 'EOF'
[scope content following templates/scope.md]
EOF
```
**If exit code != 0, stop immediately** — do not proceed to design creation.

2. `design.md` (HOW): gemba findings, target components, key contracts:

Use `raise_docs_write` MCP tool with doc_type="epic-design", title="E{N}: {epic-name} design", content="[design content following templates/design.md]", output_path="work/epics/e{N}-{name}/design.md", cwd="{project_or_worktree_path}".
**Verify result:** If `result.status != "ok"`, stop immediately with error:
  `Epic design write failed: {result.error}. Cannot continue without docs sync in connected mode.`
If MCP tools are not available, fall back to:
```bash
rai docs write epic-design \
  --title "E{N}: {epic-name} design" \
  --stdin \
  --output-path work/epics/e{N}-{name}/design.md << 'EOF'
[design content following templates/design.md]
EOF
```
**If exit code != 0, stop immediately** — do not proceed to Jira update.

Both documents are required. For simple epics, `design.md` is short (gemba findings + approach), not absent.

3. Update Jira description with the full scope (replaces the 1-line set at creation time):

Use the `raise_backlog_update` MCP tool with issue_key="{JIRA_KEY}", custom_fields='{"description": "{objective 1-2 sentences}\n\nStories: {S{N}.1 — title} | {S{N}.2 — title} | {S{N}.3 — title}\n\nDone when: {key done criteria — comma-separated}"}'.
If MCP tools are not available, fall back to:
```bash
rai backlog update {JIRA_KEY} \
  -F "description={objective 1-2 sentences}

Stories: {S{N}.1 — title} | {S{N}.2 — title} | {S{N}.3 — title}

Done when: {key done criteria — comma-separated}"
```

Capture deferred items in `dev/parking-lot.md` (Edit tool) with origin, priority, and promotion conditions.

<verification>
Scope document reviewable in <10 minutes. Parking lot updated.
</verification>

## Output

| Item | Destination |
|------|-------------|
| Scope document | `work/epics/e{N}-{name}/scope.md` |
| Design document | `work/epics/e{N}-{name}/design.md` (if architecture) |
| ADRs | `governance/adrs/adr-YYYY-MM-DD-{slug}.md` (local) + docs adapter (type: adr) |
| Parking lot | `dev/parking-lot.md` |
| Next | `/rai-epic-ux-design` (it may skip straight to `/rai-epic-plan` for infrastructure epics) |

**STOP HERE.** Return your summary to the orchestrator. Do NOT invoke any further skill.

## Quality Checklist

- [ ] Epic Brief consumed as input (if exists from `/rai-epic-start`)
- [ ] Gemba walk done — actual code read, no duplicate components proposed
- [ ] Objective is outcome-focused, not implementation-focused
- [ ] Scope boundaries explicit (in/out documented)
- [ ] Lean principles applied: KISS, DRY, YAGNI, MVP mentality
- [ ] Waste check: every story is essential for the objective
- [ ] Stories independently deliverable (3-10 range)
- [ ] Dependencies mapped with no cycles
- [ ] Done criteria are measurable
- [ ] Both scope.md and design.md produced (design.md is never optional)
- [ ] NEVER time-box epics — scope-based, not duration-based
- [ ] NEVER over-specify stories — save details for `/rai-story-design`

## References

- Brief template: `rai-epic-start/templates/brief.md`
- Scope template: `templates/scope.md`
- Design template: `templates/design.md`
- ADR template: `.raise/templates/architecture/adr.md`
- Next: `/rai-epic-ux-design` (it may hand off directly to `/rai-epic-plan` when interaction design is not needed)
- Story design: `/rai-story-design`
- Close: `/rai-epic-close`
