# Recommendation: Ontology Extraction Pipeline for E3 — ScaleUp Agent

> Actionable recommendation for Epic E3
> Based on synthesis of 24 sources (see synthesis.md)

---

## Executive Summary

Build a **three-phase iterative pipeline** using existing tools, not a custom framework. Start with competency questions from Eduardo, use KGGen or LlamaIndex for initial extraction, canonicalize with LLM-assisted clustering, and validate with domain expert review. Represent the ontology as SKOS + property graph (not full OWL). Budget 40-60% of effort for human curation.

---

## Recommended Architecture

### Phase 1: Seed Schema (1-2 days, human-intensive)

**Goal**: Create a lightweight seed schema before any automated extraction.

**Steps**:
1. Formulate 20-30 competency questions with Eduardo
   - "What are the four decisions in Scaling Up?"
   - "What habits map to each decision area?"
   - "What tools support each habit?"
2. Extract candidate entity types and relationship types from CQs
3. Define a seed schema as a Pydantic model or JSON Schema:
   - Entity types: Concept, Framework, Tool, Habit, Decision, Metric, Role, Process
   - Relation types: `part_of`, `supports`, `measured_by`, `performed_by`, `prerequisite_of`

**Rationale**: Schema-guided extraction outperforms free-form (Claim 5). CQs are validated as specification mechanism (Claim 6). This is 10-15% of total effort.

### Phase 2: Automated Extraction (2-3 days, pipeline-intensive)

**Goal**: Extract entities and relations from corpus using LLM pipeline.

**Recommended Tool Stack** (in order of preference):

| Component | Option A (Simplest) | Option B (More Control) | Option C (Most Flexible) |
|-----------|---------------------|------------------------|--------------------------|
| Entity extraction | KGGen (`pip install kg-gen`) | LlamaIndex PropertyGraphIndex | OntoGPT/SPIRES |
| Schema guidance | KGGen entity types | LlamaIndex schema-guided mode | LinkML schema |
| Entity resolution | KGGen built-in clustering | Custom LLM-based dedup | OntoGPT grounding |
| Storage | JSON/NetworkX | Neo4j | RDFlib/Turtle |
| LLM provider | Claude via LiteLLM | Claude via LlamaIndex | Claude via OntoGPT |

**Recommended: Option A (KGGen) for first pass, Option B (LlamaIndex) if more control needed.**

**Steps**:
1. Chunk corpus into manageable segments (1000-2000 tokens per chunk)
2. Run extraction with seed schema as entity type hints
3. Apply built-in entity clustering/canonicalization
4. Export to JSON property graph for review

**Validation gates** (deterministic):
- Schema conformance: all entities have a valid type from seed schema
- Completeness: all CQs can be answered from extracted graph
- Consistency: no contradictory relations (A `part_of` B AND B `part_of` A)
- Coverage: every source document contributed at least one triple

### Phase 3: Human Curation + Refinement (3-5 days, human-intensive)

**Goal**: Domain expert validates and refines the extracted ontology.

**Steps**:
1. Present extracted ontology to Eduardo in a visual format (Streamlit app or Neo4j Browser)
2. Review cycle:
   - Mark entities as correct / incorrect / missing
   - Mark relations as correct / incorrect / missing
   - Identify missing concepts and connections
3. Update seed schema based on review feedback
4. Re-run extraction with refined schema (Phase 2 iteration)
5. Repeat until diminishing returns (typically 2-3 iterations)

**Expected effort distribution**:
- Entity validation: ~30% of curation time (easier, most entities will be correct)
- Relationship validation: ~50% of curation time (harder, many will be approximate)
- Schema refinement: ~20% of curation time (adding missed concept types)

---

## Representation Format

### Recommended: SKOS + Property Graph (JSON-LD)

**Why not full OWL?**
- We need a knowledge graph for agent context, not an inference engine
- OWL complexity is unjustified for our use case
- SKOS is sufficient for hierarchical concepts + relations
- Property graph (JSON) integrates naturally with Python/Pydantic

**Schema structure**:
```
Concept (skos:Concept)
  ├── prefLabel (string)
  ├── altLabel (list[string])      # alternative names
  ├── definition (string)
  ├── broader (list[Concept])      # parent concepts
  ├── narrower (list[Concept])     # child concepts
  ├── related (list[Concept])      # non-hierarchical relations
  └── properties (dict)            # domain-specific metadata

Relation (custom)
  ├── source (Concept)
  ├── target (Concept)
  ├── type (enum)                  # part_of, supports, etc.
  ├── evidence (list[string])      # source passages
  └── confidence (float)           # extraction confidence
```

### Storage

For the agent use case, store as:
1. **Primary**: JSON-LD files in the repository (version-controlled, human-readable)
2. **Query**: Load into NetworkX for graph traversal at runtime
3. **Optional**: Neo4j if we need visual exploration or complex queries

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| LLM hallucinated concepts | Every concept must trace to source passage (evidence field) |
| Inconsistent entity naming | Clustering/canonicalization step + manual review |
| Missing process knowledge | Supplement with explicit process modeling (state machines, decision trees) extracted separately |
| Eduardo's time availability | Pre-extract and present for validation (reduce review burden) |
| Over-engineering the pipeline | Start with KGGen (simplest), escalate only if insufficient |

---

## Effort Estimate

| Phase | Effort | Who |
|-------|--------|-----|
| 1. Seed schema + CQs | 1-2 days | Emilio + Eduardo |
| 2. Pipeline setup + first extraction | 2-3 days | Emilio (engineering) |
| 3. First review cycle | 1-2 days | Eduardo (domain) + Emilio |
| 4. Refinement iteration | 1-2 days | Emilio (pipeline) |
| 5. Second review cycle | 1 day | Eduardo + Emilio |
| 6. Final validation | 1 day | Both |
| **Total** | **7-11 days** | |

---

## Tools to Evaluate First

In order of priority:

1. **KGGen** (`pip install kg-gen`) — Simplest, NeurIPS-validated, built-in clustering. Try this first.
2. **LlamaIndex PropertyGraphIndex** — More control, schema-guided mode, modular extractors. Use if KGGen is too limited.
3. **Neo4j LLM Graph Builder** — If we want visual exploration and transcript handling. More infrastructure.
4. **OntoGPT/SPIRES** — If we need formal ontology grounding against existing vocabularies.

**Do NOT build from scratch.** All of these tools are validated and maintained.

---

## Decision Required

Before proceeding with implementation:

1. **Eduardo availability**: Can he dedicate 3-4 days for review cycles?
2. **Corpus readiness**: Are transcripts, books, and notes digitized and accessible?
3. **Representation choice**: Confirm SKOS + property graph (vs. full OWL)
4. **Tool choice**: Approve starting with KGGen, escalating if needed

---

*Recommendation confidence: HIGH (based on 7 triangulated claims from 24 sources)*
