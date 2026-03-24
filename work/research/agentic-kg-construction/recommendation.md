# Recommendation: KG Architecture for E3 ScaleUp Agent

> Research Date: 2026-03-18
> Decision Context: Epic E3 — ScaleUp Agent
> Confidence: HIGH (based on 28 sources, 7 triangulated claims)

---

## TL;DR

**Recommended approach: Custom lightweight pipeline with schema-guided extraction + dual-index retrieval.**

Not GraphRAG (too expensive, overkill for corpus size). Not pure RAG (insufficient for relational methodology queries). A lean 3-agent pipeline extracting into a typed property graph, with vector index alongside for chunk retrieval.

---

## Decision Matrix

| Approach | Fit for E3 | Cost | Quality | Extensibility | Risk |
|----------|-----------|------|---------|---------------|------|
| Microsoft GraphRAG | Low | Very High | High for global queries | Medium | High (cost, complexity) |
| LightRAG | Medium | Low | High for mixed queries | Low (monolithic) | Low |
| KAG (Ant Group) | Medium-High | Medium | Very High | Medium | Medium (Java/SPG stack) |
| Custom Agentic Pipeline | High | Medium | High (with schema) | High (pluggable) | Medium (build effort) |
| Neo4j + LLM Builder | Medium | Low | Medium | Medium | Low |

---

## Recommended Architecture

### Phase 1: Foundation (Story 1-2)

#### 1.1 Define ScaleUp Ontology (Pydantic Models)

Design 15-25 concept types and 8-12 relation types as Pydantic models:

```
Concepts: Principle, Practice, Tool, Framework, Metric, Habit, Role,
          Meeting, Decision, Process, Strategy, Barrier, Outcome
Relations: ENABLES, REQUIRES, MEASURES, PART_OF, APPLIES_TO,
           CONFLICTS_WITH, PRECEDES, REFINES
```

**Why Pydantic**: Aligns with RaiSE conventions (Critical Rule #10). Schema IS the ontology contract. Validation at extraction boundaries.

**Evidence**: Schema-guided extraction outperforms schema-free (Claim 3, HIGH confidence). Even minimal schemas improve quality dramatically.

#### 1.2 Build 3-Agent Extraction Pipeline

Three agents, not nine (KARMA's 9 agents is for 1,200+ documents; ScaleUp corpus is ~10-50):

1. **Extractor Agent**: Schema-guided entity + relation extraction from transcript chunks. Uses DSPy-style typed signatures for structured output.

2. **Validator Agent**: Checks extracted triples against ontology constraints. Detects duplicates, schema violations, contradictions. Reports confidence scores.

3. **Curator Agent**: Resolves conflicts flagged by Validator. Merges duplicate entities. Evolves schema when consistent gaps appear (proposes new concept types).

**Evidence**: KARMA (Claim 2) validates multi-agent approach. FinReflectKG (Claim 5) validates reflection/validation loop. But 3 agents sufficient for corpus size.

#### 1.3 Dual-Index Storage

- **Property Graph**: Neo4j or in-memory property graph (networkx + typed nodes). Stores concepts, relationships, provenance.
- **Vector Index**: Embedded transcript chunks with links to graph entities. Standard RaiSE memory adapter pattern.

**Evidence**: Claim 4 (HIGH confidence) — hybrid outperforms either alone. KAG's mutual indexing pattern (S8) is the reference architecture.

### Phase 2: Retrieval + Agent (Story 3-4)

#### 2.1 Neuro-Symbolic Query Engine

Query pipeline:
1. Parse user question -> extract intent + entities
2. **Graph path**: Traverse KG for structured relationships (ENABLES, REQUIRES, etc.)
3. **Vector path**: Retrieve relevant transcript chunks by semantic similarity
4. **Merge**: Combine structured knowledge + source evidence for response generation

**Evidence**: DO-RAG achieves 94%+ relevancy with this pattern (S13). Graphiti's hybrid search (semantic + keyword + graph) at P95 300ms (S9).

#### 2.2 Conversational Agent via Claude SDK

Use RaiAgentRuntime (from S2.3) with tool-use for:
- `query_graph(concept, relation_type)` — structured graph traversal
- `search_chunks(query)` — vector similarity search
- `get_context(concept)` — full context: graph neighbors + source chunks
- `suggest_application(situation)` — methodology application advice

### Phase 3: Evolution (Story 5+)

#### 3.1 Pluggable Ontology Architecture

Design the ontology layer to be swappable:
- Ontology as a Pydantic model package (one per methodology)
- Extraction pipeline parameterized by ontology
- Graph schema derived from Pydantic models
- Future: EOS, 4DX, OKR ontologies plug into same infrastructure

**Evidence**: No direct evidence for hot-swappable ontologies (Gap 3), but KARMA's schema-guided pattern (S6) and KAG's SPG framework (S8) both parameterize on schema. The pattern is sound even if not benchmarked.

#### 3.2 Incremental Graph Updates

When new content arrives (new transcripts, Eduardo's adaptations):
- Graphiti-style incremental updates (S9) — no full recomputation
- Temporal tracking of methodology evolution
- Provenance preservation

---

## What NOT to Do

1. **Don't use full Microsoft GraphRAG**. Indexing cost is 3-5x baseline, query cost 610K tokens. E3's corpus doesn't justify it. LazyGraphRAG or LightRAG patterns are sufficient.

2. **Don't skip the ontology**. Schema-free extraction produces noisy, inconsistent graphs (Claim 3). Even 15 concept types dramatically improve quality.

3. **Don't over-agent the pipeline**. KARMA's 9 agents are for 1,200+ documents. 3 agents suffice for 10-50 transcripts. Add agents only when specific quality problems emerge.

4. **Don't index everything up front**. LazyGraphRAG pattern (S4) shows deferring LLM work to query time produces comparable quality. Build the structural graph (entities, relations) at index time; generate summaries on demand.

5. **Don't build without evaluation**. Define QA test cases BEFORE building the KG. Use methodology questions Eduardo would actually ask. GraphRAG-Bench (S2) pattern: fact retrieval, complex reasoning, contextual summarization.

---

## Integration with RaiSE

### Existing Assets to Leverage

- **RaiAgentRuntime + ClaudeRuntime** (S2.3): Agent execution layer already built
- **Pydantic models convention**: Ontology fits naturally as typed models
- **Memory adapter pattern**: Dual-index retrieval can extend existing adapter protocol
- **Graph build command** (`rai graph build`): Existing graph infrastructure to extend

### New Components Needed

1. **ScaleUp ontology module**: Pydantic models for methodology concepts/relations
2. **Extraction pipeline**: 3-agent pipeline (extractor, validator, curator)
3. **Graph storage adapter**: Property graph store (Neo4j or lightweight alternative)
4. **Retrieval engine**: Hybrid KG + vector query merger
5. **Agent tools**: Claude tool definitions for graph queries

### Estimated Complexity

| Component | Size | Risk | Dependencies |
|-----------|------|------|-------------|
| Ontology models | S | Low | None |
| Extraction pipeline | M | Medium | Ontology, Claude SDK |
| Graph storage | S-M | Low | Neo4j or networkx |
| Retrieval engine | M | Medium | Graph storage, vector store |
| Agent tools | S | Low | RaiAgentRuntime |
| Evaluation harness | S | Low | Test cases from Eduardo |

---

## Open Questions for Emilio

1. **Corpus size**: How many transcripts/documents? If <20, single-pass extraction with post-hoc validation may be sufficient (skip multi-agent overhead).

2. **Graph backend**: Neo4j (production-grade, community support) vs. networkx + JSON (lightweight, no external dependency)? Depends on whether this becomes a hosted service.

3. **Ontology starting point**: Does Eduardo have an existing framework/structure for Scaling Up concepts? Starting from his mental model is faster than extracting from scratch.

4. **Evaluation criteria**: What questions should the agent answer correctly? Need 20-30 test cases before building.

5. **Pluggable ontologies timeline**: Is the multi-methodology vision for E3 or a future epic? This affects how much abstraction to build now.
