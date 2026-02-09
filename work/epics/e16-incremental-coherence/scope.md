# Epic E16: Incremental Coherence - Scope

> **Status:** IN PROGRESS
> Branch: `epic/e16/incremental-coherence`
> Created: 2026-02-08
> Target: Post-F&F

---

## Objective

Prevent architecture documentation and graph drift through small-batch updates integrated into the story lifecycle, with full discovery as a validation safety net.

**Value proposition:** Every story leaves the architecture map accurate. Drift never accumulates. Future sessions always work from truth, not stale snapshots.

---

## Architectural Context

**Modules affected:**

| Module | Domain | Layer | Role in Epic |
|--------|--------|-------|--------------|
| `mod-context` | bc-ontology | Integration | Graph diffing, change set generation |
| `mod-discovery` | bc-discovery | Domain | Validation via full discovery rerun |
| `mod-memory` | bc-ontology | Integration | Build command enhancement |
| `mod-cli` | bc-tooling | Orchestration | New commands, story-close integration |

**Cross-domain:** Epic spans bc-ontology and bc-discovery — justified because coherence requires comparing graph (ontology) against code reality (discovery).

**Key constraints from graph:**
- MUST: Type hints, Pydantic models, >90% coverage (all standard guardrails)
- Architecture: Engine/content separation, deterministic CLI + inference skill (PAT-200)

---

## Stories (4 planned — resequenced 2026-02-09)

| ID | Story | Size | Status | Description |
|----|-------|:----:|:------:|-------------|
| S16.1 | Code-Aware Graph | S | In Progress | Pluggable `CodeAnalyzer` Protocol + `PythonAnalyzer` (ast-based) to enrich graph with real imports/exports/components |
| S16.2 | Graph Diff Engine | M | Pending | Compare old vs new unified graph via `diff_graphs()`, expose as `raise memory build --diff` |
| S16.3 | Docs Update Skill | M | Pending | `/docs-update` skill — subagent compares graph vs module docs, updates frontmatter + narrative |
| S16.4 | Lifecycle Integration | S | Pending | Wire `/docs-update` into story-close as subagent, HITL gate |

**Total:** 4 stories, ~2S + 2M

**Design decisions (2026-02-09 session):**
- S16.2+S16.3 from original plan merged into single `/docs-update` skill (AI updates both frontmatter and narrative)
- New S16.1 added as prerequisite: graph must have real code data before diff is useful
- `/docs-update` compares graph vs docs directly (robust) — doesn't depend on transient diff file
- `/docs-update` runs as subagent with own context window, uses `raise memory` CLI for context
- CodeAnalyzer is a Protocol — pluggable for future TS/PHP support (parkinglotted)

---

## In Scope

**MUST:**
- Graph diffing: compare two graph snapshots, produce structured change set
- Deterministic frontmatter update for module docs (depends_on, depended_by, entry_points, public_api, components)
- Story-close integration point (Step 1.75, after existing structural drift check)
- HITL gate: human reviews all doc changes before commit
- Full discovery as validation audit (verify incremental state)

**SHOULD:**
- AI subagent for narrative section regeneration (high-level docs, module purpose updates)
- Change set includes categorized impact (frontmatter-only vs structural vs architectural)
- `raise coherence check` CLI command for ad-hoc use outside lifecycle

---

## Out of Scope (defer to parking lot)

- **Drift detector calibration** (SES-118) → Separate item, complements but doesn't block
- **Real-time/watch-mode detection** → Post-V3, no current need
- **Cross-project coherence** → V3 scope (multi-project Rai)
- **Auto-commit without human review** → Violates HITL principle
- **High-level doc restructuring** (bounded context boundaries, layer redesign) → Human-only decisions

---

## Architecture

### Two-Layer Design (ADR-025)

```
Story work changes code
         │
         ▼
┌─────────────────────────┐
│   Layer 1: CLI          │  Deterministic
│   (raise memory build   │
│    --diff)              │
│                         │
│   Input: old graph +    │
│          new sources    │
│   Output: GraphDiff     │
│     - added nodes/edges │
│     - removed           │
│     - modified          │
│     - impact category   │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│   Frontmatter-only?     │──yes──▶ Auto-update module docs
│                         │         (deterministic, no review)
└────────┬────────────────┘
         │ no (structural changes)
         ▼
┌─────────────────────────┐
│   Layer 2: Skill        │  Inference
│   (subagent)            │
│                         │
│   Input: GraphDiff +    │
│          affected docs  │
│   Output: Updated docs  │
│          (human reviews) │
└────────┬────────────────┘
         │
         ▼
    HITL review
         │
         ▼
    Commit with story
```

### Graph Diff Data Model

```python
class NodeChange(BaseModel):
    node_id: str
    change_type: Literal["added", "removed", "modified"]
    old_value: ConceptNode | None
    new_value: ConceptNode | None
    changed_fields: list[str]  # For modified: which fields changed

class EdgeChange(BaseModel):
    source: str
    target: str
    edge_type: str
    change_type: Literal["added", "removed", "modified"]

class GraphDiff(BaseModel):
    node_changes: list[NodeChange]
    edge_changes: list[EdgeChange]
    impact: Literal["none", "frontmatter", "structural", "architectural"]
    affected_modules: list[str]
    summary: str  # Human-readable one-liner
```

### Lifecycle Integration

```
story-close (existing):
  Step 1:   Verify feature ready
  Step 1.5: Check structural drift (existing)
  Step 1.75: COHERENCE CHECK (NEW)           ◄━━━━
             │
             ├─ rebuild graph
             ├─ diff against previous
             ├─ if frontmatter changes: auto-update docs
             ├─ if structural changes: flag for subagent
             ├─ human reviews changes
             └─ commit doc updates with story
  Step 2:   Identify parent branch
  ...
```

---

## Done Criteria

### Per Story
- [ ] Code implemented with type annotations
- [ ] Pydantic models for all data structures
- [ ] Unit tests passing (>90% coverage)
- [ ] All quality checks pass (ruff, pyright, bandit)

### Epic Complete
- [ ] Graph diff produces accurate change sets on real raise-commons data
- [ ] Module doc frontmatter auto-updates correctly from code changes
- [ ] Story-close coherence step triggers on structural changes
- [ ] Full discovery validates incremental state (no regression)
- [ ] Architecture docs updated for new modules/capabilities
- [ ] Epic retrospective done
- [ ] Merged to v2

---

## Dependencies

```
S16.1 Code-Aware Graph (prerequisite)
  │
  ├──▶ [Discovery refresh — re-run discover + update docs with real data]
  │
  └──▶ S16.2 Graph Diff Engine (foundation)
              │
              └──▶ S16.3 Docs Update Skill (/docs-update)
                          │
                          └──▶ S16.4 Lifecycle Integration
```

Sequential chain: each story depends on the previous.
Discovery refresh between S16.1 and S16.2 is an activity, not a story.

**External blockers:** None.

---

## Architecture References

| Decision | Document | Key Insight |
|----------|----------|-------------|
| Graph diffing + AI doc regen | ADR-025 | Two-layer: deterministic CLI + inference skill |
| Unified context graph | ADR-019 | Single graph, NetworkX, node_link_data format |
| Ontology graph extension | ADR-023 | Structural nodes (BCs, layers) in graph |

---

## Notes

### Why This Epic

- PAT-196 keeps recurring: stale docs → wrong paths in new sessions
- PAT-152: schema changes invalidate graph silently
- Current drift detection (383 false positives) is unusable
- Prevention > detection: small batches at story-close vs periodic big-bang audit
- Graph diff is foundational infrastructure — enables future tooling beyond docs

### Key Risks

- **Graph diff accuracy** (Medium likelihood, High impact): False positives in diff could trigger unnecessary doc rewrites. Mitigation: conservative change detection, HITL gate.
- **Subagent quality** (Medium likelihood, Medium impact): AI-generated doc sections may need significant editing. Mitigation: start with frontmatter-only (S16.2), add AI layer (S16.3) incrementally.
- **Story-close latency** (Low likelihood, Low impact): Extra step adds time. Mitigation: skip when no structural changes detected.

### Key Patterns Informing Design

- **PAT-196:** Architecture docs are the map — stale docs cause wrong paths
- **PAT-200:** Deterministic (CLI) for structure, inference (skill) for content
- **PAT-202/203:** Templates-as-contract — doc structure IS the contract
- **PAT-174:** Architecture docs are intentional governance — deviating is drift
- **PAT-191:** Simplest architecture is discovered, not designed upfront

---

## Implementation Plan

> Added by `/epic-plan` — 2026-02-08

### Sequencing Strategy (revised 2026-02-09)

**Prerequisite-first.** S16.1 (code-aware graph) must come first — without real code data in the graph, the diff engine would be blind to code changes. After S16.1, a discovery refresh grounds the docs in real data. Then S16.2 (diff engine) becomes meaningful, S16.3 (docs-update skill) consumes the diff, and S16.4 wires it into the lifecycle.

### Story Sequence

| Order | Story | Size | Dependencies | Milestone | Rationale |
|:-----:|-------|:----:|:-------------|-----------|-----------|
| 1 | S16.1: Code-Aware Graph | S | None | Prereq | Graph must have real code data (imports, exports) before diff is useful |
| — | Discovery refresh | — | S16.1 | Prereq | Re-run discover + update module docs with enriched graph data |
| 2 | S16.2: Graph Diff Engine | M | S16.1 | M1 | Pure `diff_graphs()` + `raise memory build --diff` CLI. Foundation for downstream. |
| 3 | S16.3: Docs Update Skill | M | S16.2 | M2 | `/docs-update` — subagent compares graph vs docs, updates both frontmatter + narrative |
| 4 | S16.4: Lifecycle Integration | S | S16.3 | M3 | Wire `/docs-update` into story-close as subagent with HITL gate |

### Milestones

| Milestone | Stories | Success Criteria | Demo |
|-----------|---------|------------------|------|
| **Prereq: Code-Aware Graph** | S16.1 + discovery refresh | `raise memory build` produces graph with real imports/exports; module docs refreshed | Run build, query mod-context, show real depends_on from code |
| **M1: Graph Diff** | + S16.2 | `raise memory build --diff` produces accurate change set | Make a code change, run build --diff, show detected changes |
| **M2: Docs Update** | + S16.3 | `/docs-update` skill updates affected module docs (frontmatter + narrative) | Run /docs-update, show updated module doc |
| **M3: Epic Complete** | + S16.4 | story-close spawns /docs-update subagent, HITL review, commit | Full story-close flow with coherence step |

### Sequencing Rationale

**S16.1 first:** Without real code data in the graph, the diff is blind. This is S-sized (Python ast + Protocol + builder integration) but enables everything else.

**Discovery refresh after S16.1:** Not a story — an activity. Re-run discover with the enriched graph to ground all module docs in real data before we start diffing.

**S16.2 second:** Now that the graph has real data, diff becomes meaningful. Pure function `diff_graphs(old, new)` + CLI integration. Highest uncertainty (comparison algorithm, noise filtering).

**S16.3 third:** `/docs-update` skill. Compares graph vs docs directly (robust, no diff dependency). Runs as subagent with own context. Can also be invoked manually outside lifecycle.

**S16.4 last:** Wiring. story-close spawns `/docs-update` subagent. HITL gate for review. Low risk once components exist.

### Sequencing Risks

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| PythonAnalyzer misses import patterns | Medium | Medium | Test against real raise-commons modules; handle relative/absolute/conditional imports |
| Diff is too noisy (false changes) | Medium | High | Conservative matching: ignore metadata-only changes, HITL gate |
| `/docs-update` subagent quality | Medium | Medium | Compares graph vs docs directly — grounded in data, not guessing |
| Graph format changes break diff | Low | Medium | Pin GraphDiff model with tests against real unified.json snapshots |

### Progress Tracking

| Story | Size | Status | Actual | Notes |
|-------|:----:|:------:|:------:|-------|
| S16.1: Code-Aware Graph | S | In Progress | - | Branch: story/s16.1/graph-diff-engine |
| S16.2: Graph Diff Engine | M | Pending | - | |
| S16.3: Docs Update Skill | M | Pending | - | |
| S16.4: Lifecycle Integration | S | Pending | - | |

**Milestone Progress:**
- [ ] Prereq: Code-Aware Graph (S16.1 + discovery refresh)
- [ ] M1: Graph Diff (+ S16.2)
- [ ] M2: Docs Update (+ S16.3)
- [ ] M3: Epic Complete (+ S16.4, retrospective, merge)

---

*Epic tracking — update per story completion*
*Created: 2026-02-08*
*Plan added: 2026-02-08*
