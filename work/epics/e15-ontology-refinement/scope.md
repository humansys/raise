# Epic Scope: Ontology Graph Refinement

**ID:** E15
**Branch:** `epic/e15/ontology-refinement`
**Priority:** Post-F&F (Feb 15+)
**Sizing:** L (21-30 SP estimated)
**Depends on:** E11 (Unified Graph), E13 (Discovery), discover-describe story

---

## Strategic Objective

Make the ontology graph the **active backbone** for design decisions, not just a query tool. RaiSE is ontology-guided software development — the graph should proactively constrain and inform all design/planning activities through progressive disclosure of architectural context.

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
4. **"Show me guardrails relevant to authentication"** — Guardrails exist but aren't linked to modules/components
5. **"What domain boundaries must I respect?"** — Domain model not in graph
6. **BFS filtered by edge type** — Can't say "follow only depends_on edges"
7. **Skills don't query architecture before designing** — Design skills use ad-hoc keywords, not structured architectural context

---

## In Scope

### Story 1: Ingest All Architecture Docs into Graph
**Size:** S (3 SP)

Extend `load_architecture()` to ingest system-context, system-design, and domain-model frontmatter — not just module docs. The builder currently filters `if type != "module": return None`. Remove this filter and add handlers for:
- `architecture_context` → system-level node with tech stack, external deps
- `architecture_design` → design node with layers, ADR references
- `architecture_domain_model` → domain model node with bounded contexts

**Value:** All architecture knowledge in the graph. Queryable. No new NodeTypes needed — use existing types with rich metadata.

### Story 2: Bounded Context and Layer Nodes
**Size:** M (5 SP)

Add `bounded_context` and `layer` to NodeType. Extract from domain-model.md and system-design.md frontmatter:
- 7 bounded_context nodes (governance, discovery, ontology, skills, experience, observability, integrations)
- 4 layer nodes (leaf, domain, integration, orchestration)
- `belongs_to` edges: module → bounded_context
- `in_layer` edges: module → layer

**Value:** "Which domain does this module belong to?" becomes a graph query. Domain boundaries are navigable.

### Story 3: Constraint Edges from Guardrails
**Size:** M (5 SP)

Guardrails already exist as nodes (22 guardrail nodes). Add `constrained_by` EdgeType and infer edges:
- Parse guardrail scope (MUST-CODE applies to all code, MUST-ARCH applies to architecture, SHOULD-CLI applies to CLI)
- Create `constrained_by` edges from modules/layers to relevant guardrails
- Parse module doc `constraints` field and create constraint nodes

**Value:** "Find all constraints for the memory module" returns both guardrails and module-specific constraints.

### Story 4: Edge-Type Filtering in Queries
**Size:** M (5 SP)

Add `edge_types: list[EdgeType]` parameter to `UnifiedQueryEngine.query()`. BFS traversal currently follows all edges — add filtering so queries can say "follow only depends_on edges" or "follow only constrained_by edges".

**Value:** Progressive disclosure by relationship type. "Show me what this module depends on" vs "show me everything related to this module."

### Story 5: Architectural Context Query Helpers
**Size:** S (3 SP)

Add convenience methods to `UnifiedQueryEngine`:
- `find_constraints_for(concept_id: str) → list[ConceptNode]`
- `find_domain_for(module_name: str) → ConceptNode | None`
- `find_layer_for(module_name: str) → ConceptNode | None`

Expose via CLI: `raise memory constraints <module>`, `raise memory domain <module>`.

**Value:** One-call architectural context for skills. No multi-hop query assembly needed.

### Story 6: Ontology-Guided Design Step for Skills
**Size:** S (3 SP)

Create a reusable "Load Architectural Context" step for design skills. Update `/story-design` and `/epic-design` to include it as Step 0:

```bash
# Query relevant architectural context
raise memory query "<topic> architecture constraints" --types module,guardrail,bounded_context,layer --limit 15
# Or use helper:
raise memory constraints <relevant-module>
raise memory domain <relevant-module>
```

Skills present "Architectural Context Loaded" section in their output, showing what the graph told them about relevant constraints, domain boundaries, and patterns.

**Value:** Ontology-guided design by default. Every design decision starts grounded in the current architecture.

---

## Out of Scope

- Semantic search / embeddings (keyword search is sufficient at our scale)
- Path query DSL (complex query composition — YAGNI for now)
- Validation module (`validate_design()` — useful but separate epic)
- Conflict detection edges (`violates`, `conflicts_with` — future)
- Cross-project ontology (V3 scope)
- Full DDD enforcement (aggregate root validation, anti-corruption layer checking)

---

## Done Criteria

- [ ] All architecture docs (system-context, system-design, domain-model) ingested into graph
- [ ] Bounded context and layer nodes exist with belongs_to/in_layer edges
- [ ] Guardrails linked to modules via constrained_by edges
- [ ] Queries can filter by edge type
- [ ] `raise memory constraints <module>` returns relevant guardrails and constraints
- [ ] `/story-design` queries architectural context before designing
- [ ] Tests pass (>90% coverage on new code)
- [ ] Dogfood: design a story using ontology-guided design step

---

## Execution Order

```
Story 1 (S) — Ingest all arch docs
    ↓
Story 2 (M) — Bounded context + layer nodes
    ↓
Story 3 (M) ──┬── Story 4 (M)    ← parallel after Story 2
              ↓
         Story 5 (S) — Query helpers
              ↓
         Story 6 (S) — Skills integration
```

**Critical path:** 1 → 2 → 3 → 5 → 6 (19 SP)
**Parallel:** Story 4 can run alongside Story 3

---

## Risks

| Risk | Mitigation |
|------|------------|
| Schema change (PAT-152) breaks cached graphs | Stories 2-3 add NodeType/EdgeType — always rebuild after |
| Over-engineering the query engine | Keep it simple — helpers, not DSL. YAGNI. |
| Guardrail-to-module mapping is ambiguous | Start with explicit scope parsing (MUST-CODE → all code modules). Refine based on dogfood. |
| Too many new edges make graph noisy | Use weight < 1.0 for inferred constraint edges. Type filtering prevents noise in queries. |

---

## References

- **PAT-175:** Ontology-guided design pattern
- **PAT-174:** Architecture docs as intentional governance
- **PAT-173:** DDD from structural data
- **E11:** Unified Graph (foundation)
- **ADR-019:** Unified graph architecture
- **ADR-020:** Extended node types
- **Research:** RES-ARCH-KNOWLEDGE-001 (architecture knowledge layer)
- **Domain Model:** `governance/architecture/domain-model.md`

---

*Created: 2026-02-08*
*Status: Scoped — pending /epic-design*
