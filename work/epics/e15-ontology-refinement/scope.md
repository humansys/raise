# Epic Scope: Ontology Graph Refinement

**ID:** E15
**Branch:** `epic/e15/ontology-refinement`
**Priority:** Pre-F&F (blocking — maximum Rai reliability for HumanSys team)
**Sizing:** M (22 SP estimated — 17 original + 5 S15.7)
**Depends on:** E11 (Unified Graph), E13 (Discovery), discover-describe story (all complete)

---

## Strategic Objective

Make the ontology graph the **active backbone** for design decisions, not just a query tool. RaiSE is ontology-guided software development — the graph should proactively surface constraints, domain boundaries, and architectural context before every design decision.

**Value proposition:** Without E15, Rai designs blind — ad-hoc keyword queries that miss constraints, no knowledge of bounded contexts, no awareness of which guardrails apply. E14 evidence: 14 SP of rework (60% of epic effort) directly caused by missing ontology structure. E15 eliminates this class of defects for HumanSys team and all future users.

**From PAT-175:** "Design skills should query the ontology graph for architectural context, guardrails, and domain boundaries before designing."

---

## Current State

| What Exists | Status |
|------------|--------|
| Unified graph: 810 concepts, 5122 relationships | Working |
| 15 NodeTypes (pattern, module, component, guardrail, etc.) | Working |
| 8 EdgeTypes (depends_on, learned_from, related_to, etc.) | Working |
| 14 module nodes with depends_on edges | Working |
| Keyword-based BFS query with type filtering | Working |
| `get_neighbors()` with `edge_types` parameter | **Working** (not exposed in query engine) |
| Architecture docs: system-context, system-design, domain-model | Exist but **NOT ingested** |
| Bounded contexts (7 defined in domain-model.md) | Documented but **NOT in graph** |
| Layer architecture (4 layers in system-design.md) | Documented but **NOT in graph** |
| 22 guardrail nodes (extracted from guardrails.md) | In graph but **no constraint edges** |
| 12 skills query the graph | Working but **not architecture-aware** |

## Gap Analysis

### What the graph CAN'T do that ontology-guided design needs:

1. **"Find all constraints that apply to this module"** — No constraint edges
2. **"Which bounded context owns this module?"** — No bounded_context nodes
3. **"What layer is this module in?"** — No layer nodes
4. **"Show me guardrails relevant to this scope"** — Guardrails exist but aren't linked to scopes
5. **"What domain boundaries must I respect?"** — Domain model not in graph
6. **"Follow only depends_on edges"** — Query engine doesn't expose edge_types (graph layer does)
7. **Skills don't query architecture before designing** — Design skills use ad-hoc keywords, not structured architectural context

---

## Unknowns Resolved (Design Phase)

| # | Unknown | Resolution | Evidence |
|---|---------|------------|----------|
| 1 | How to make constraint queries reliable? | **Typed queries via `edge_types`, not keyword search.** `get_neighbors()` already supports it — gap is only at query engine level. Two-stage: typed first (precision), keyword second (recall) | Research: typed queries have guaranteed recall; keyword search has ~40% false negative rate (Zep/GraphRAG studies) |
| 2 | How to map guardrails to modules? | **Category-based scope inference.** Guardrail IDs encode scope: `MUST-CODE-*` → all code, `SHOULD-CLI-*` → orchestration layer. Map categories to layers/bounded contexts | Guardrails.md: 22 guardrails with structured IDs already encoding their applicability scope |
| 3 | How to extract bounded contexts? | **Deterministic from frontmatter.** domain-model.md has explicit `bounded_contexts[].modules` list. system-design.md has `layers[].modules`. No inference needed | domain-model.md and system-design.md YAML frontmatter already has structured data |
| 4 | How to ensure query recall? | **Bidirectional typed BFS.** For "what constrains X": follow incoming `constrained_by` edges. For "what depends on X": follow both directions of `depends_on`. BFS depth=2 catches transitive constraints | Research: multi-strategy retrieval (typed + keyword) is industry standard (Microsoft GraphRAG, LlamaIndex PropertyGraph) |

---

## In Scope

### Story 1: Ingest All Architecture Docs into Graph
**Size:** S (3 SP)

Extend `load_architecture()` to ingest all architecture docs — not just module docs. The builder currently filters `if type != "module": return None`. Remove this filter and add handlers for:
- `architecture_context` → node with tech stack, external deps, governed_by references
- `architecture_design` → node with layers listing, ADR references, guardrails reference
- `architecture_domain_model` → node with bounded contexts listing, communication patterns

**Implementation:** Extend `_parse_architecture_doc()` with a type-dispatch pattern. Each architecture doc type gets its own node ID scheme and content extraction.

**Value:** All architecture knowledge in the graph. Queryable. Foundation for Stories 2-3.

### Story 2: Bounded Context and Layer Nodes
**Size:** S (3 SP) — *revised down from M (5 SP) after discovering structured frontmatter*

Add `bounded_context` and `layer` to NodeType. Add `belongs_to` and `in_layer` to EdgeType. Extract from domain-model.md and system-design.md frontmatter:
- 7 bounded_context nodes + 1 shared_kernel (governance, discovery, ontology, skills, experience, observability, integrations, shared_kernel)
- 4 layer nodes (leaf, domain, integration, orchestration)
- `belongs_to` edges: module → bounded_context (from `bounded_contexts[].modules`)
- `in_layer` edges: module → layer (from `layers[].modules`)

**Implementation:** New `_extract_bounded_contexts()` and `_extract_layers()` methods in builder, called after `load_architecture()` produces the domain model and design nodes.

**Value:** "Which domain does this module belong to?" and "What layer is this module in?" become single graph queries. Domain boundaries are navigable.

### Story 3: Constraint Edges from Guardrails
**Size:** S (3 SP) — *revised down from M (5 SP) after resolving guardrail mapping unknown*

Guardrails already exist as nodes (22 nodes with structured IDs). Add `constrained_by` EdgeType and create edges using category-based scope inference:

| Guardrail Category | Applies To | Mapping |
|-------------------|-----------|---------|
| `MUST-CODE-*` | All bounded contexts | Universal code quality |
| `MUST-TEST-*` | All bounded contexts | Universal testing |
| `MUST-SEC-*` | All bounded contexts | Universal security |
| `MUST-ARCH-*` | Ontology, Skills BCs | Architecture-specific |
| `MUST-DEV-*` | All bounded contexts | Development workflow |
| `SHOULD-CLI-*` | Orchestration layer | CLI-specific |
| `SHOULD-INF-*` | All bounded contexts | Methodology |
| `SHOULD-CODE-*` | All bounded contexts | Code quality suggestions |
| `SHOULD-TEST-*` | All bounded contexts | Testing suggestions |
| `SHOULD-DEV-*` | All bounded contexts | Dev workflow suggestions |
| `SHOULD-SEC-*` | All bounded contexts | Security suggestions |

Additionally: parse module doc `constraints` field and create module-specific constraint edges.

**Implementation:** New `_infer_constrained_by()` method in builder. Parse guardrail node IDs to extract category prefix, map to bounded contexts/layers via lookup table.

**Value:** "Find all constraints for the memory module" returns guardrails + module-specific constraints.

### Story 4: Edge-Type Filtering in Query Engine
**Size:** XS (2 SP) — *revised down from M (5 SP) after discovering `get_neighbors()` already supports it*

Expose `edge_types` parameter in `UnifiedQueryEngine.query()`:
- Add `edge_types: list[EdgeType] | None = None` to `UnifiedQuery` model
- Pass through to `_concept_lookup()` → `graph.get_neighbors()`
- Add `--edge-types` CLI option to `raise memory query`

**Implementation:** ~20 lines of code change. The graph-level capability already exists in `UnifiedGraph.get_neighbors()`. This story bridges the gap to the query engine and CLI.

**Value:** "Show me what this module depends on" (follows only `depends_on`) vs "show me everything related" (follows all edges). Progressive disclosure by relationship type.

### Story 5: Architectural Context Query Helpers
**Size:** S (3 SP)

Add convenience methods to `UnifiedQueryEngine`:
- `find_constraints_for(module_name: str) → list[ConceptNode]` — follows `constrained_by` edges from module's bounded context
- `find_domain_for(module_name: str) → ConceptNode | None` — follows `belongs_to` edge
- `find_layer_for(module_name: str) → ConceptNode | None` — follows `in_layer` edge
- `get_architectural_context(module_name: str) → ArchitecturalContext` — single-call combining all three

Expose via CLI:
- `raise memory constraints <module>` — all applicable guardrails and constraints
- `raise memory domain <module>` — bounded context info
- `raise memory context <module>` — full architectural context (domain + layer + constraints + dependencies)

**Implementation:** New `ArchitecturalContext` Pydantic model. Helper methods use typed BFS (edge_types parameter from Story 4). CLI commands format output via OutputConsole.

**Value:** One-call architectural context for skills. Reliable, structured, deterministic.

### Story 6: Ontology-Guided Design Step for Skills
**Size:** S (3 SP)

Create a reusable "Load Architectural Context" step for design skills. Update `/story-design`, `/epic-design`, and `/story-plan` to include it:

```bash
# Step 0: Load Architectural Context
raise memory context <relevant-module>
# Returns: bounded context, layer, constraints, dependencies, guardrails
```

Skills present "Architectural Context" section in their output, showing:
- Bounded context and domain vocabulary
- Layer position and dependency direction rules
- Applicable guardrails (MUST and SHOULD)
- Module-specific constraints
- Related modules in same domain

**Implementation:** Update 3 skill SKILL.md files. Add the step with instructions for how to identify the relevant module(s) and how to use the context in design decisions.

**Value:** Ontology-guided design by default. Every design decision starts grounded in the current architecture. Eliminates the class of errors that cost 14 SP in E14.

---

## Out of Scope

| Item | Rationale |
|------|-----------|
| Semantic search / embeddings | Keyword + typed queries sufficient at our scale (<1K nodes) |
| Path query DSL | Complex query composition — YAGNI |
| Validation module (`validate_design()`) | Useful but separate epic |
| Conflict detection edges (`violates`, `conflicts_with`) | Future |
| Cross-project ontology | V3 scope |
| Full DDD enforcement (aggregate root validation) | Over-engineering |
| Community detection / PageRank | Optimization for larger graphs |
| LLM-based synonym expansion | Adds inference cost; typed queries provide better recall |

---

## Architecture Decision: ADR-023

**Decision:** Extend the ontology graph with bounded context, layer, and constraint structure using typed queries as the primary retrieval mechanism for architectural context.

See `dev/decisions/adr-023-ontology-graph-extension.md` for full decision record.

**Key choices:**
1. Add `bounded_context` and `layer` NodeTypes (schema change, PAT-152)
2. Add `belongs_to`, `in_layer`, `constrained_by` EdgeTypes
3. **Typed queries (edge_types filter) as primary for constraint discovery** — not keyword search
4. Category-based guardrail scope inference — deterministic, not AI-inferred

---

## Done Criteria

### Per Story
- [ ] Code implemented with type annotations
- [ ] Docstrings on all public APIs (Google-style)
- [ ] Unit tests passing (>90% coverage on new code)
- [ ] All quality checks pass (ruff, pyright, bandit)

### Epic Complete
- [ ] All architecture docs ingested into graph
- [ ] Bounded context and layer nodes with belongs_to/in_layer edges
- [ ] Guardrails linked to bounded contexts/layers via constrained_by edges
- [ ] Query engine exposes edge_types filtering
- [ ] `raise memory context <module>` returns full architectural context
- [ ] `/story-design` queries architectural context before designing
- [ ] Tests pass (>90% coverage)
- [ ] **Dogfood: design a real story using ontology-guided design step**
- [ ] Graph rebuilt and verified: new node/edge counts correct
- [ ] Epic retrospective completed
- [ ] Merged to v2

---

## Execution Order

```
Story 1 (S, 3 SP) — Ingest all arch docs
    ↓
Story 2 (S, 3 SP) — Bounded context + layer nodes
    ↓
Story 3 (S, 3 SP) ──┬── Story 4 (XS, 2 SP)    ← parallel after Story 2
                     ↓
              Story 5 (S, 3 SP) — Query helpers
                     ↓
              Story 6 (S, 3 SP) — Skills integration
```

**Critical path:** 1 → 2 → 3 → 5 → 6 (15 SP)
**Parallel:** Story 4 can run alongside Story 3

---

## Risks

| Risk | L | I | Mitigation |
|------|:-:|:-:|------------|
| Schema change (PAT-152) breaks cached graphs | H | M | Always rebuild after adding NodeType/EdgeType. One rebuild at end, not per-story |
| Over-engineering the query engine | M | H | Helpers only, not DSL. YAGNI. |
| Guardrail category mapping too coarse | M | L | Start with category prefix. Refine based on dogfood. Universal guardrails (MUST-*) apply everywhere — correct by default |
| Too many constraint edges add noise | L | M | Typed queries filter by edge type — constraint edges only appear when asked for |
| Time pressure (2 days to F&F) | M | H | Stories revised down (24→17 SP). At 3x velocity, 17 SP ≈ 6 SP effort. Achievable in 2 focused days |

---

## References

- **PAT-175:** Ontology-guided design pattern
- **PAT-174:** Architecture docs as intentional governance
- **PAT-173:** DDD from structural data
- **PAT-062:** Query keywords must match actual node content
- **PAT-125:** Ontology reflects user mental model
- **PAT-127:** Graph consolidation removes N×maintenance
- **E11:** Unified Graph (foundation)
- **E14 evidence:** 14 SP rework from missing ontology — 5,200 dead lines, 315 files renamed, session scattered across 4 systems
- **ADR-019:** Unified graph architecture
- **ADR-020:** Extended node types
- **ADR-023:** Ontology graph extension (this epic)
- **Research:** RES-ARCH-KNOWLEDGE-001 (architecture knowledge layer)
- **Research:** Microsoft GraphRAG, LlamaIndex PropertyGraph, Zep/Graphiti (reliable retrieval patterns)
- **Domain Model:** `governance/architecture/domain-model.md`

---

## Implementation Plan

> Added by `/epic-plan` — 2026-02-08

### Story Sequence

| Order | Story | Size | SP | Dependencies | Milestone | Rationale |
|:-----:|-------|:----:|:--:|--------------|-----------|-----------|
| 1 | S15.1 Ingest All Arch Docs | S | 3 | None | M1 | Foundation — removes `type != "module"` filter, enables all downstream |
| 2 | S15.2 Bounded Context + Layer Nodes | S | 3 | S15.1 | M1 | Adds structural nodes S3 and S5 depend on |
| 3 | S15.3 Constraint Edges | S | 3 | S15.2 | M2 | Creates `constrained_by` edges linking guardrails to bounded contexts |
| 3‖ | S15.4 Edge-Type Filtering | XS | 2 | None (graph layer ready) | M2 | Parallel with S3. Exposes existing `get_neighbors()` edge_types in query engine |
| 4 | S15.5 Query Helpers | S | 3 | S15.3, S15.4 | M3 | `find_constraints_for()`, `get_architectural_context()`, CLI commands |
| 5 | S15.6 Skills Integration | S | 3 | S15.5 | M4 | Updates `/story-design`, `/epic-design`, `/story-plan` with architectural context step |
| — | ~~S15.4b Foundational Pattern Surfacing~~ | XS | — | — | — | **Superseded by S15.7** |
| 6 | S15.7 Deterministic Session Protocol | M | 5 | S15.4 | M5 | Session-state, CLI context bundle, coaching persistence, foundational patterns, platform agnosticism |

### Milestones

| Milestone | Stories | Target | Success Criteria | Demo |
|-----------|---------|--------|------------------|------|
| **M1: Architecture in Graph** | S15.1, S15.2 | Day 1 | `raise memory query "ontology" --types bounded_context` returns nodes. 8 BC + 4 layer nodes + belongs_to/in_layer edges | Query bounded contexts and layers |
| **M2: Constraint-Aware Graph** | +S15.3, S15.4 | Day 1 | `raise memory query mod-memory --strategy concept_lookup --edge-types constrained_by` returns guardrails. ~200 constraint edges | Query constraints for any module |
| **M3: One-Call Context** | +S15.5 | Day 2 | `raise memory context memory` returns full architectural context (domain, layer, constraints, dependencies) in <100ms | CLI command returns structured context |
| **M4: Skills Integration** | +S15.6 | Day 2 | `/story-design` queries architectural context before designing. Dogfood with real story design. | Design a story using ontology-guided context |
| **M5: Session Protocol** | +S15.7 | Day 3+ | `raise session start` outputs context bundle. Session-state.yaml written/read. Coaching persists. No CLAUDE.local.md dependency. Retro complete. | Full session lifecycle with new protocol |

### Parallel Work Streams

```
Day 1 (Graph Structure):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Stream 1: S15.1 (arch docs) ──► S15.2 (BCs + layers) ──► M1
                                        │
Day 1-2 (Constraint Layer):             ↓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Stream 1:                        S15.3 (constraint edges) ─┐
                                                           ├──► M2
Stream 2:                        S15.4 (edge-type filter)──┘

Day 2 (Query + Skills):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Stream 1: S15.5 (query helpers + CLI) ──► M3
                    ↓
          S15.6 (skills integration) ──► M4
```

**Merge points:**
- After S15.2: Graph has structural nodes → split into S15.3 (builder) + S15.4 (query engine)
- Before S15.5: Both constraint edges AND edge-type filtering must be ready
- S15.6 is sequential — updates skills that call S15.5 helpers

### Progress Tracking

| Story | Size | SP | Status | Actual | Velocity | Notes |
|-------|:----:|:--:|:------:|:------:|:--------:|-------|
| S15.1 Ingest Arch Docs | S | 3 | ✅ Done | 42 min | 2.14x | 3 arch nodes, type-dispatch pattern |
| S15.2 BC + Layer Nodes | S | 3 | ✅ Done | 25 min | 2.4x | 10 BC + 4 layer nodes, 26 edges, PAT-182 |
| S15.3 Constraint Edges | S | 3 | ✅ Done | 18 min | 3.3x | 195 constrained_by edges, PAT-185 |
| S15.4 Edge-Type Filter | XS | 2 | ✅ Done | 12 min | 2.5x | edge_types in query engine + CLI, PAT-186 |
| S15.5 Query Helpers | S | 3 | Pending | — | — | |
| S15.6 Skills Integration | S | 3 | Pending | — | — | |
| ~~S15.4b Foundational Patterns~~ | XS | — | Superseded | — | — | Absorbed into S15.7 |
| S15.7 Session Protocol | M | 5 | ✅ Done | 55 min | 4.1x | 136 tests, ADR-024, PAT-189 |
| S15.8 Minimal Agent Config | M | 5 | ✅ Done | — | — | Rich context bundle, shrink CLAUDE.md + CLAUDE.local.md |

**Milestone Progress:**
- [x] M1: Architecture in Graph (Day 1)
- [x] M2: Constraint-Aware Graph (Day 1-2) — S15.3 + S15.4 done
- [ ] M3: One-Call Context (Day 2)
- [ ] M4: Skills Integration (Day 2)
- [x] M5: Session Protocol (Day 3+) — S15.7 ✓
- [x] M6: Self-Sustaining Sessions — S15.8 ✓ (CLAUDE.md + CLAUDE.local.md minimal, context bundle complete)

### Velocity Assumptions

- **Baseline:** 3x multiplier with full kata cycle (PAT-082, PAT-094)
- **All stories S/XS:** Full kata cycle yields ~3x (PAT-082). 17 SP at 3x ≈ ~6 SP effective effort
- **Day 1:** S15.1 + S15.2 are builder changes in same module (context/builder.py) — momentum carries
- **Day 2:** S15.3 + S15.4 parallel, then S15.5 + S15.6 are consumer code (query + skills)
- **Buffer:** S15.4 already partially implemented → extra time for dogfood validation

### Sequencing Risks

| Risk | L | I | Mitigation |
|------|:-:|:-:|------------|
| S15.1 arch doc parsing more complex than expected | M | M | Frontmatter is already structured YAML — same parsing as module docs |
| S15.3 guardrail category mapping creates too many edges | L | L | Start with bounded contexts only, add module-level later if needed |
| S15.5 ArchitecturalContext model design requires iteration | M | M | Start with flat model (domain, layer, constraints list), don't over-abstract |
| Rebuild graph breaks existing queries | M | H | Run full test suite after schema change. Keep existing node types untouched |

---

*Plan created: 2026-02-08*
*Created: 2026-02-08*
*Designed: 2026-02-08 (unknowns resolved, stories revised, ADR-023 created)*
*Planned: 2026-02-08 (sequenced, milestones defined, 2-day timeline)*
*Status: Planned — ready for /story-start S15.1*
