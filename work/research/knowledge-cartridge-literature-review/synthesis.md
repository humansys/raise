# Knowledge Cartridge Architecture — Literature Review & Market Analysis Synthesis

**Date:** 2026-03-24
**Context:** S11.9 (RAISE-704) — Knowledge Refactor ideation
**Method:** 10 parallel research agents (5 academic, 5 market), 100+ searches, 90+ sources
**Confidence:** High (triangulated across academic, industry, and market sources)

---

## 1. The Concept Is Novel — But Built on Proven Foundations

**Claim (HIGH confidence, 8+ sources):** No existing system combines all Knowledge Cartridge features: typed schema (Pydantic) + corpus provenance + domain adapter + validation gates (CQs) + HITL curation + symbolic retrieval + pluggable composition.

Each individual piece exists:

| Feature | Prior Art | Evidence Level |
|---------|-----------|----------------|
| Modular ontologies | MOMo, OBO Foundry, NeOn (20+ years) | Very High |
| Typed schemas for KG | Graphiti/Zep (Pydantic), Cognee (OWL+Pydantic) | High |
| Spreading activation retrieval | SYNAPSE (SOTA LoCoMo), Cognee SA-RAG | Very High |
| HITL ontology refinement | OntoChat, WebProtégé, Gene Ontology | Very High |
| CQ-based validation | 234 CQs formalized in literature, CQOA method | High |
| Multi-domain composition | OBO Foundry, Apollo Federation, Schema.org | Very High |
| Graph-based agent memory | Mem0, Letta, Graphiti, HippoRAG | Very High |

**The integration is the innovation.** Nobody has packaged these into a distributable, self-contained domain knowledge module.

---

## 2. Six Validated Design Principles

### P1: Orthogonality — Each cartridge owns its concepts exclusively
**Sources:** OBO Foundry (100+ ontologies), Apollo Federation, MOMo, Schema.org
**Confidence:** Very High (4+ independent validations across domains)

Each concept belongs to exactly one cartridge. Cross-cartridge references use linking (MIREOT-style: source_id + type_uri + parent_type), never duplication.

### P2: Thin Upper Schema — 5-10 shared meta-types as bridge
**Sources:** Schema.org (~10 top-level types, 45M domains), BFO/DOLCE, Data Mesh semantic layer
**Confidence:** High

A minimal shared type hierarchy (Entity, Process, Goal, Metric, Role, Artifact, Constraint) bridges domains without coupling. Keep it stable and minimal.

### P3: Federated Query Decomposition — Route, don't search everything
**Sources:** FedX, Apollo router, R1-Router, Agentic RAG patterns
**Confidence:** Very High

Every successful federated system decomposes queries into source-specific sub-queries. The agent analyzes which cartridges are relevant, generates cartridge-specific sub-queries, and composes results.

### P4: Fail-Fast Composition — Conflicts are errors, not warnings
**Sources:** Apollo Federation, dbt contracts, OWL module interface proposals
**Confidence:** High

Conflicting type definitions between cartridges should fail registration. A "draft" status can allow softer validation during development.

### P5: Separate Review Metadata from Domain Data
**Sources:** WebProtégé ChAO, Gene Ontology evidence codes, Collaborative Protégé
**Confidence:** High

Review decisions, gate results, and change history live in a separate linked structure — not embedded in the cartridge. Keeps the domain model clean.

### P6: PDCA as the Improvement Model
**Sources:** Deming-based ontology inspection, DILIGENT methodology, Ontology Maturing
**Confidence:** High

Plan (CQs + schema) → Do (extraction) → Check (gates) → Act (curation). Each cycle improves both the ontology and the extraction patterns.

---

## 3. Spreading Activation Is Validated

**Claim (HIGH confidence, 5 sources):** SA-based retrieval significantly outperforms vector RAG for relational/multi-hop queries.

| System | Result | Venue |
|--------|--------|-------|
| SYNAPSE | SOTA on LoCoMo (40.5 F1), 95% token reduction | arXiv 2026 |
| Cognee SA-RAG | 25-39% absolute improvement over naive RAG | arXiv 2025 |
| HippoRAG (PPR) | Up to 20% improvement, 10-20x cheaper | NeurIPS 2024, ICML 2025 |
| FalkorDB benchmark | 3.4x vs vector RAG; vector RAG = 0% on schema-bound queries | Industry 2024 |
| GCR | 100% faithfulness via structural constraint | ICML 2025 |

**Calibration:** For simple fact retrieval, vanilla RAG is comparable or better (GraphRAG-Bench, ICLR 2026). Consider a fast-path for trivial queries.

**Recommended parameters:** c=0.4 rescaling, T=3 iterations, τₐ=0.5 activation threshold (from Cognee SA-RAG).

---

## 4. Competitive Landscape — Whitespace Confirmed

### No one builds Knowledge Cartridges

12 competitors analyzed. The market converges from two directions:

| Direction | Players | What They Have | What They Lack |
|-----------|---------|----------------|----------------|
| **Memory layers** | Mem0 ($24M), Letta ($10M), LangMem | Conversation-derived memory, agent integration | Typed domain schemas, HITL, validation, modularity |
| **Knowledge graph platforms** | Cognee ($8.2M), Zep ($2.3M), TrustGraph | Structured KG, some Pydantic support | Distributable modules, HITL curation, composition |
| **Enterprise KG** | Interloom ($16.5M), Diffbot, Graphlit | Scale, enterprise integration | Pluggability, curation, domain packaging |

**Closest competitors:**
1. **Cognee** — Pydantic DataPoint + OWL ontologies + pluggable resolvers. Most technically similar. Gap: no HITL curation, no "cartridge" packaging, no module composition.
2. **Zep/Graphiti** — Pydantic schemas + temporal KG + hybrid retrieval. Gap: limited to 10 types, no modularity, no HITL.
3. **TrustGraph** — OWL-first, versioned "Context Cores." Philosophically most aligned. Gap: 1.5k stars, no Pydantic, low traction.

### Strategic Positioning: "npm for domain knowledge"

Knowledge Cartridges are **complementary** to memory layers, not competitive. Any agent framework (LangGraph, CrewAI, etc.) could consume cartridges. The value is in the **domain knowledge packaging**, not the memory infrastructure.

### Risk: Cognee or Zep could add cartridge-like packaging

Both have the technical foundation. Speed to market matters. Our moat is **ontology quality + HITL curation + domain coverage**, not infrastructure.

---

## 5. Market Opportunity

### Funding validates the category

$60M+ invested in agent memory/knowledge in 18 months (was $0 before 2024). Mem0 $24M, Interloom $16.5M, Letta $10M, Cognee $8.2M, Zep $2.3M.

### TAM

| Market | 2025 | 2030 | CAGR |
|--------|------|------|------|
| Semantic Layer + KG for Agentic AI | $1.73B | $4.93B | 23.3% |
| Knowledge Graph market | $1.07B | $6.94B | 36.6% |
| AI Agent market | $7.84B | $52.62B | 46.3% |

### KG adoption bottleneck = our opportunity

KG adoption stalled at ~27% despite massive interest. **The bottleneck is building domain models.** Pre-packaged domain cartridges attack this directly.

### Verticals that already monetize ontologies

The ontology itself is rarely the product — value accrues to the **enrichment layer**:
- Lightcast (HR/Skills): $105M revenue on open ESCO/O*NET base
- MSCI ESG: $344M run rate on sustainability taxonomy
- Wolters Kluwer Health: €1.58B on medical knowledge

**Recommended first vertical: HR/Skills** — proven model, low regulatory barriers, open-base + proprietary-enrichment aligns with cartridge model.

---

## 6. Novel Contributions (What We Can Claim)

Based on the literature review, these are genuinely novel:

1. **Knowledge Cartridge as a formal concept** — self-contained, distributable, schema-validated domain knowledge module with its own adapter, gates, and corpus provenance. No precedent in this combination.

2. **Domain adapter pattern for typed traversal** — a pluggable interpreter that maps query semantics to typed graph traversal strategies. No existing system does this.

3. **Query failures as gap signals** — using downstream retrieval failures to detect ontology gaps and trigger extraction→curation cycles. No mature methodology exists.

4. **Pydantic-as-SHACL** — using Pydantic models as the constraint language for ontology validation (instead of RDF shapes). Emerging pattern, not yet established.

5. **HITL curation integrated with symbolic retrieval** — no agent memory framework has built-in expert curation workflows.

---

## 7. Key Tensions to Resolve in S11.9

### T1: NetworkX vs. Graph DB
No competitive system uses NetworkX as primary store. All use Neo4j or equivalent. Our scale (hundreds of nodes per cartridge) may not need a DB, but we need a scaling plan.

**Recommendation:** Start with NetworkX, design for pluggable backend. Validate at 10K nodes.

### T2: Prescribed vs. Emergent Schemas
Literature is split: Graphiti/Cognee support both prescribed (typed) and emergent (learned) schemas. Our cartridges are prescribed-first.

**Recommendation:** Prescribed core types + extension mechanism for emergent additions. Follow R2 evidence.

### T3: Where Does the Cartridge Runtime Live?
This is the S11.9 question. Options:
- **raise-core**: protocols only (DomainAdapter, SchemaRef, GateResult)
- **raise-cli**: runtime (engine, gates, discovery, CLI commands)
- **New package**: dedicated `raise-knowledge` or `raise-cartridge`

**Recommendation:** Based on market positioning ("npm for domain knowledge"), the cartridge runtime deserves clear identity. At minimum, protocols in raise-core + runtime in raise-cli. A future dedicated package is possible if the concept grows.

### T4: Hybrid Retrieval
Evidence strongly supports adding a vector similarity signal to complement symbolic retrieval (HybridRAG, SYNAPSE triple hybrid).

**Recommendation:** Architecture should allow optional vector signal in composite scoring. Don't require it — symbolic-only is valid for structured domains.

---

## 8. References by Axis

### Academic Research (93 sources total)
- **R1** Neurosymbolic Memory: 18 sources (SYNAPSE, HippoRAG, Graphiti, GraphRAG, etc.)
- **R2** Modular Ontologies: 20 sources (MOMo, OBO Foundry, MIREOT, Apollo Federation, etc.)
- **R3** HITL Ontology: 19 sources (OntoChat, WebProtégé, OOPS!, Gene Ontology, etc.)
- **R4** Schema-Mediated Retrieval: 19 sources (GraphRAG-Bench, GCR, SubgraphRAG, HippoRAG, etc.)
- **R5** Multi-Domain Composition: 17 sources (OBO Foundry, Apollo Federation, Wikidata, FedX, etc.)

### Market Research (5 reports)
- **M1** Direct Competitors: 12 companies profiled
- **M2** KG Platform Evolution: 11 platforms profiled
- **M3** Agent Memory Frameworks: 10 frameworks profiled
- **M4** Vertical Ontology Markets: 6 verticals analyzed
- **M5** Funding & Market Signals: $60M+ tracked, TAM estimates

Full evidence catalogs at `dev/research/R{1-5}-*.md` and `dev/research/M{1-5}-*.md`.
