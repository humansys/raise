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
| `mod-context` | bc-ontology | Integration | Code analyzers, graph diffing, builder enrichment |
| `mod-memory` | bc-ontology | Integration | Build command `--diff` flag |
| `mod-cli` | bc-tooling | Orchestration | CLI integration, story-close wiring |

**Cross-domain:** Contained within bc-ontology + bc-tooling. Code analysis lives in context (ontology domain) because it feeds the knowledge graph directly.

**Key constraints from graph:**
- MUST: Type hints, Pydantic models, >90% coverage (all standard guardrails)
- Architecture: Engine/content separation, deterministic CLI + inference skill (PAT-200)
- Protocol pattern for code analyzers enables platform agnosticism (principle-platform-agnosticism)

**Key patterns informing revised design:**
- PAT-066: tree-sitter for multi-language AST (future analyzers, not S16.1)
- PAT-200: Deterministic (CLI) for structure, inference (skill) for content
- PAT-053: Unified graph query as Step 1, raw file reads as fallback

---

## Stories (4 planned — resequenced 2026-02-09)

| ID | Story | Size | Status | Description |
|----|-------|:----:|:------:|-------------|
| S16.1 | Code-Aware Graph | S | ✅ Done | Pluggable `CodeAnalyzer` Protocol + `PythonAnalyzer` (ast-based) to enrich graph with real imports/exports/components |
| S16.5 | Component ID Uniqueness | S | Done | Fix silent 10-component data loss from duplicate IDs in analyzer (comp-{stem} → comp-{module.path}) |
| S16.2 | Graph Diff Engine | M | Done | Compare old vs new unified graph via `diff_graphs()`, expose as `raise memory build --diff` |
| S16.3 | Docs Update Skill | M | Done | `/docs-update` skill — subagent compares graph vs module docs, updates frontmatter + narrative |
| S16.4 | Lifecycle Integration | S | Pending | Wire `/docs-update` into story-close as subagent, HITL gate |

**Total:** 5 stories, ~3S + 2M

**Design decisions (2026-02-09 session):**
- S16.2+S16.3 from original plan merged into single `/docs-update` skill (AI updates both frontmatter and narrative)
- New S16.1 added as prerequisite: graph must have real code data before diff is useful
- `/docs-update` compares graph vs docs directly (robust) — doesn't depend on transient diff file
- `/docs-update` runs as subagent with own context window, uses `raise memory` CLI for context
- CodeAnalyzer is a Protocol — pluggable for future TS/PHP support (parkinglotted)

---

## In Scope

**MUST:**
- Code-aware graph: `CodeAnalyzer` Protocol + `PythonAnalyzer` enriching module nodes with real imports/exports/components
- Graph diffing: compare two graph snapshots via `diff_graphs()`, produce structured change set
- `raise memory build --diff` CLI: single build, diff as side effect, persists diff
- `/docs-update` skill: AI subagent updates both frontmatter AND narrative for affected module docs
- `/docs-update` compares graph vs docs directly (robust, works without diff file)
- Story-close integration: spawns `/docs-update` as subagent with HITL gate
- HITL gate: human reviews all doc changes before commit

**SHOULD:**
- Change set includes categorized impact (frontmatter-only vs structural vs architectural)
- `/docs-update` invocable manually outside lifecycle for ad-hoc use
- `ModuleInfo` model captures entry_points for CLI commands

---

## Out of Scope (defer to parking lot)

- **Multi-language code analyzers** (TS, PHP) → Post-E16, needed for F&F devs on mixed-stack monorepos. Protocol is ready.
- **Drift detector calibration** (SES-118) → Separate item, complements but doesn't block
- **Real-time/watch-mode detection** → Post-V3, no current need
- **Cross-project coherence** → V3 scope (multi-project Rai)
- **Auto-commit without human review** → Violates HITL principle
- **High-level doc restructuring** (bounded context boundaries, layer redesign) → Human-only decisions
- **Rename discovery namespace to discover** → Cosmetic, low priority
- **Merge /discover-complete into /discover-validate** → Simplification, post-F&F

---

## Architecture (revised 2026-02-09)

### Three-Layer Design (ADR-025 evolved)

```
Code changes (gemba moves)
         │
         ▼
┌─────────────────────────┐
│ Layer 0: Code Analysis   │  Deterministic (S16.1)
│ (CodeAnalyzer Protocol)  │
│                          │
│ PythonAnalyzer (ast)     │
│ → ModuleInfo per module  │
│ → real imports, exports  │
│ → component counts       │
└────────┬─────────────────┘
         │ enriches
         ▼
┌─────────────────────────┐
│ Layer 1: Graph + Diff    │  Deterministic (S16.2)
│ (raise memory build      │
│  --diff)                 │
│                          │
│ Input: old graph +       │
│        new sources +     │
│        code analysis     │
│ Output: GraphDiff        │
│   - added/removed/mod    │
│   - affected modules     │
└────────┬─────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Layer 2: /docs-update    │  Inference (S16.3)
│ (AI subagent)            │
│                          │
│ Compares graph vs docs   │
│ Updates frontmatter +    │
│   narrative together     │
│ Uses raise memory CLI    │
│   for context            │
└────────┬─────────────────┘
         │
         ▼
    HITL review
         │
         ▼
    Commit with story
```

### Code Analysis Models (S16.1)

```python
class ModuleInfo(BaseModel):
    """Language-agnostic module analysis result."""
    name: str
    language: str
    source_path: str
    imports: list[str]
    exports: list[str]
    component_count: int
    entry_points: list[str]

class CodeAnalyzer(Protocol):
    """Pluggable per-language analyzer."""
    def detect(self, project_root: Path) -> bool: ...
    def analyze_modules(self, project_root: Path) -> list[ModuleInfo]: ...
```

### Graph Diff Data Model (S16.2)

```python
class NodeChange(BaseModel):
    node_id: str
    change_type: Literal["added", "removed", "modified"]
    old_value: ConceptNode | None
    new_value: ConceptNode | None
    changed_fields: list[str]

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
    summary: str
```

### Lifecycle Integration (S16.4)

```
story-close (existing):
  Step 1:   Verify feature ready
  Step 1.5: Check structural drift (existing)
  Step 1.75: COHERENCE CHECK (NEW)           ◄━━━━
             │
             ├─ spawn /docs-update subagent
             │    ├─ runs raise memory build --diff
             │    ├─ compares graph vs module docs
             │    ├─ updates affected docs (frontmatter + narrative)
             │    └─ returns summary of changes
             │
             ├─ HITL: human reviews doc changes
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
- [ ] `raise memory build` produces graph with real code data (imports, exports, component counts)
- [ ] `raise memory build --diff` produces accurate change sets on real raise-commons data
- [ ] `/docs-update` skill updates module docs (frontmatter + narrative) from graph state
- [ ] `/docs-update` works both manually and as subagent from story-close
- [ ] Story-close spawns `/docs-update` subagent with HITL gate
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

- **PythonAnalyzer import patterns** (Medium likelihood, Medium impact): Real codebases have conditional imports, TYPE_CHECKING blocks, relative imports. Mitigation: test against actual raise-commons modules.
- **Graph diff noise** (Medium likelihood, High impact): False positives in diff trigger unnecessary doc rewrites. Mitigation: conservative change detection, HITL gate.
- **`/docs-update` subagent quality** (Medium likelihood, Medium impact): AI-generated doc sections may need editing. Mitigation: compares graph vs docs directly (grounded in data), HITL review.
- **Story-close latency** (Low likelihood, Low impact): Subagent adds time. Mitigation: skip when no changes detected.

### Key Patterns Informing Design

- **PAT-066:** tree-sitter for multi-language AST (future analyzers)
- **PAT-196:** Architecture docs are the map — stale docs cause wrong paths
- **PAT-200:** Deterministic (CLI) for structure, inference (skill) for content
- **PAT-202/203:** Templates-as-contract — doc structure IS the contract
- **PAT-174:** Architecture docs are intentional governance — deviating is drift

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
| 1.5 | S16.5: Component ID Uniqueness | S | S16.1 | Prereq | Fix duplicate IDs causing 10 silent component drops in graph |
| 2 | S16.2: Graph Diff Engine | M | S16.5 | M1 | Pure `diff_graphs()` + `raise memory build --diff` CLI. Foundation for downstream. |
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
| S16.1: Code-Aware Graph | S | ✅ Done | 30 min | 1.5x velocity |
| S16.5: Component ID Uniqueness | S | Done | - | ✅ 345/345 unique, 1.5x velocity |
| S16.2: Graph Diff Engine | M | ✅ Done | 35 min | 1.71x velocity, 8 design decisions, 39 tests |
| S16.3: Docs Update Skill | M | ✅ Done | 120 min | 0.75x velocity, trigger A/B improvement, 15 modules synced |
| S16.4: Lifecycle Integration | S | Pending | - | |

**Milestone Progress:**
- [ ] Prereq: Code-Aware Graph (S16.1 + discovery refresh)
- [ ] M1: Graph Diff (+ S16.2)
- [x] M2: Docs Update (+ S16.3)
- [ ] M3: Epic Complete (+ S16.4, retrospective, merge)

---

*Epic tracking — update per story completion*
*Created: 2026-02-08*
*Plan added: 2026-02-08*
*Design revised: 2026-02-09 (resequenced stories, code-aware graph prerequisite, merged S16.2+S16.3 into /docs-update)*
