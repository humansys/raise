# Synthesis: Agentic KG Construction Architectures

> Research Date: 2026-03-18
> Sources: 28 (see evidence-catalog.md)

---

## Triangulated Claims

### Claim 1: GraphRAG is effective but over-engineered for most use cases

**Confidence: HIGH** (5 sources: S1, S2, S3, S4, S21-25)

- GraphRAG-Bench (ICLR'26, S2) shows GraphRAG underperforms vanilla RAG on many real-world tasks
- Graph advantage only materializes for: multi-hop reasoning, relational queries, cross-document synthesis
- Cost: 610K tokens/query (S1), ~$7 per 32K-word book (S21), 3-5x indexing cost over baseline (S1)
- LazyGraphRAG achieves comparable quality at 0.1% indexing cost (S4)
- LightRAG achieves competitive quality at 0.16% query cost (S3)
- Production failures at scale: NashTech 50K PDF ingestion (S22)

**Contrary evidence**: GraphRAG's community summarization is uniquely strong for "global" queries requiring cross-corpus synthesis (S1). For the specific use case of methodology Q&A with relational reasoning, the graph structure adds real value.

**Implication for E3**: Full GraphRAG is overkill. A lighter graph-based approach (LightRAG, LazyGraphRAG, or custom) would be more appropriate for the ScaleUp corpus size.

---

### Claim 2: Multi-agent architectures for KG construction are validated and effective

**Confidence: HIGH** (4 sources: S6, S7, S8, S15)

- KARMA (NeurIPS'25 spotlight, S6): 9 agents achieving 83.1% correctness across 3 domains
- FinReflectKG (S7): reflection-agent mode produces denser, cleaner graphs than single-pass
- KAG (S8): production-validated at Ant Group with 91.6% precision in government domain
- Survey (S15): schema-guided extraction consistently outperforms schema-free

**Key validated agent roles:**
1. **Schema Proposer** - suggests how new information fits the ontology
2. **Schema Critic/Validator** - reviews proposals against existing rules
3. **Entity Extractor** - identifies entities from text chunks
4. **Relation Extractor** - identifies relationships between entities
5. **Conflict Resolver** - resolves contradictions via LLM debate
6. **Schema Aligner** - ensures extracted data matches ontological constraints

**Contrary evidence**: Multi-agent systems add complexity. DSPy single-pipeline extraction (<$0.10/run, S10) may be sufficient for smaller corpora.

**Implication for E3**: Start with 3-agent architecture (extractor + validator + curator) rather than KARMA's 9. Scale agents as complexity demands.

---

### Claim 3: Schema-guided extraction significantly outperforms schema-free for domain KGs

**Confidence: HIGH** (5 sources: S6, S7, S8, S14, S15)

- KARMA's schema-guided approach: 83.1% correctness (S6)
- KAG's SPG framework: semantic-enhanced programmable graph with schema constraints (S8)
- FinReflectKG: schema violations caught by reflection loop improve quality (S7)
- Ontology comparison (S14): ontology-guided KGs with chunk info outperform vector baselines
- Survey (S15): schema-guided consistently beats schema-free for domain KGs

**Practical pattern**: Define ontology first (even if minimal), then extract. Iterate ontology as extraction reveals gaps.

**Contrary evidence**: LKD-KGC (S15) shows schema-free approaches can bootstrap initial ontologies via clustering, which can then guide subsequent extraction.

**Implication for E3**: Design the Scaling Up ontology first (concepts, relationships, constraints), then use it to guide extraction from transcripts. This aligns with RaiSE's existing pattern of structured models.

---

### Claim 4: Hybrid KG + vector retrieval outperforms either alone for domain-specific QA

**Confidence: HIGH** (5 sources: S3, S8, S9, S13, S14)

- DO-RAG (S13): 94%+ answer relevancy, 33.38% improvement over baselines
- KAG (S8): mutual indexing between KG and chunks; 19.6-33.5% F1 improvement
- LightRAG (S3): combines KG with vector retrieval; outperforms pure GraphRAG
- Graphiti (S9): hybrid search (semantic + BM25 + graph traversal) at P95 300ms
- Ontology comparison (S14): ontology-guided KGs with chunk info beat both pure KG and pure vector

**Mechanism**: KG provides structural/relational reasoning; vectors provide semantic similarity; chunks provide source evidence. Each addresses different failure modes.

**Implication for E3**: Build a dual-index system: KG for structured methodology concepts/relationships + vector index for transcript chunks. Query combines both.

---

### Claim 5: Reflection/iterative refinement significantly improves KG quality

**Confidence: MEDIUM** (3 sources: S7, S6, S19)

- FinReflectKG (S7): reflection-agent mode achieves best compliance score (64.8%) and catches schema violations
- KARMA (S6): multi-layer assessment reduces conflict edges by 18.6%
- RIGOR (S19): judge-LLM refines delta ontology fragments before merging

**Pattern**: Extract -> Validate -> Reflect -> Re-extract. The critic-corrector loop discovers both errors AND missed valid triples.

**Contrary evidence**: Reflection adds cost. For small corpora, single-pass with post-hoc validation may be sufficient.

**Implication for E3**: Include a validation/reflection step but keep it lightweight. A single critic agent reviewing extraction batches rather than per-triple reflection.

---

### Claim 6: Temporal awareness matters for evolving knowledge bases

**Confidence: MEDIUM** (2 sources: S9, S27)

- Graphiti (S9): tracks how facts change over time; provenance to source data
- Graphs Meet AI Agents survey (S27): dynamic graph evolution as key challenge for agent memory

**Implication for E3**: If the ScaleUp methodology evolves (new editions, Eduardo's adaptations), temporal tracking prevents stale knowledge. Worth considering for phase 2.

---

### Claim 7: Cost-efficient alternatives to full GraphRAG are production-ready

**Confidence: HIGH** (4 sources: S3, S4, S5, S8)

| Approach | Indexing Cost (vs GraphRAG) | Query Cost (vs GraphRAG) | Quality |
|----------|---------------------------|-------------------------|---------|
| LazyGraphRAG | 0.1% | 4% | Comparable or better |
| LightRAG | ~similar to vector RAG | 0.16% | SOTA on multiple datasets |
| E2GraphRAG | 10x faster | 100x faster than LightRAG | Competitive |
| KAG Lightweight | 89% reduction | Comparable | Production-validated |

**Implication for E3**: No need to build the expensive version first. Start with LightRAG or custom lightweight pipeline.

---

## Identified Patterns

### Pattern A: The 4-Layer KG Construction Pipeline

Recurring across multiple sources (S6, S7, S8, S11, S14):

1. **Document Layer**: Parse, chunk, embed (standard RAG preprocessing)
2. **Extraction Layer**: Entity + relation extraction (schema-guided)
3. **Validation Layer**: Schema compliance, conflict detection, deduplication
4. **Graph Layer**: Store in property graph with provenance links back to chunks

### Pattern B: Schema-First, Extract-Second

Strongest results come from defining the ontology before extraction (S6, S8, S14, S15). Even a minimal schema (10-20 concept types, 5-10 relation types) dramatically improves extraction quality.

### Pattern C: Dual-Index Architecture

Best-performing systems maintain two indexes (S3, S8, S9, S13):
- **Knowledge Graph**: structured entities, relationships, constraints
- **Vector Store**: embedded text chunks with provenance

Queries route through both and merge results.

### Pattern D: Deferred LLM Usage

LazyGraphRAG (S4) and E2GraphRAG (S5) show that deferring expensive LLM calls to query time (rather than indexing time) produces comparable quality at dramatically lower cost.

---

## Gaps in Evidence

1. **Small corpus effectiveness**: Most evaluations use large corpora (thousands of documents). ScaleUp transcripts may be 10-50 documents. Limited evidence on whether graph approaches add value at this scale.

2. **Management methodology ontologies**: No direct evidence of KGs built for business methodology domains (Scaling Up, OKRs, EOS, etc.). Closest analogs are financial KGs (S7) and biomedical KGs (S6).

3. **Pluggable ontology switching**: No validated system for hot-swapping ontologies on the same graph infrastructure. KARMA (S6) and KAG (S8) use fixed schemas per domain.

4. **Claude SDK integration**: No evidence of agentic KG construction built on Claude's tool-use SDK specifically. KARMA uses general LLM APIs.

5. **Evaluation of conversational agents over KGs**: Most benchmarks test Q&A, not multi-turn conversational interaction with methodology knowledge.
