# Evidence Catalog: Agentic KG Construction Architectures

> Research Date: 2026-03-18
> Researcher: Rai (Claude Opus 4.6)
> Total Sources: 28

---

## Source Index

| # | Source | Type | Evidence | Key Finding |
|---|--------|------|----------|-------------|
| 1 | MS GraphRAG Paper & Repo | Primary | High | Community-based summarization for global queries; 3-5x cost vs baseline RAG |
| 2 | GraphRAG-Bench (ICLR'26) | Primary | Very High | GraphRAG underperforms vanilla RAG on many tasks; only wins on multi-hop + relational |
| 3 | LightRAG (HKU, 2024) | Primary | High | 0.16% of GraphRAG's token cost per query; competitive quality |
| 4 | LazyGraphRAG (MS Research) | Primary | High | 0.1% indexing cost of GraphRAG; defers LLM use to query time |
| 5 | E2GraphRAG (2025) | Primary | High | 10x faster indexing than GraphRAG, 100x faster retrieval than LightRAG |
| 6 | KARMA (NeurIPS'25) | Primary | Very High | 9-agent framework; 83.1% correctness; 18.6% conflict reduction |
| 7 | FinReflectKG (ACM ICAIF) | Primary | High | Reflection-agent mode best balance; 64.8% compliance; critic-corrector loop |
| 8 | KAG / OpenSPG (Ant Group) | Primary | Very High | 19.6-33.5% F1 improvement on multi-hop QA; 89% token cost reduction in lightweight mode |
| 9 | Graphiti / Zep (2025) | Primary | High | Temporal KG for agents; P95 300ms retrieval; no LLM calls at retrieval time |
| 10 | DSPy KG Construction (2025) | Primary | Medium | DSPy outperforms baseline prompts on entity/relation extraction F1; <$0.10 per run |
| 11 | Neo4j LLM Graph Builder | Secondary | Medium | Production tool; multi-model support; community summarization feature |
| 12 | LlamaIndex PropertyGraphIndex | Secondary | Medium | Modular KG construction + retrieval; property graph upgrade from triples |
| 13 | DO-RAG (2025) | Primary | High | KG-enhanced RAG: 94%+ answer relevancy; up to 33.38% over baseline |
| 14 | Ontology Learning Comparison | Primary | High | DB-derived ontologies match text-derived ones at lower cost; ontology-guided KGs beat vector RAG |
| 15 | LLM-empowered KGC Survey (ICAIS'25) | Secondary | High | Comprehensive taxonomy: closed IE, open IE, schema-guided, schema-free |
| 16 | Neuro-Symbolic Design Patterns | Secondary | Medium | 6 design patterns for LLM + symbolic systems; dual-mode validation |
| 17 | Graph Survey (OpenReview) | Secondary | High | Taxonomy of Graph-RAG approaches with evaluation framework |
| 18 | LOGOS Schema Induction | Primary | High | End-to-end grounded theory; outperforms 4 competing workflows |
| 19 | RIGOR Ontology Learning | Primary | Medium | RAG-enhanced ontology: DB schema + domain ontologies + growing core |
| 20 | BioKGBench (2024) | Primary | Medium | Domain-constrained KG QA benchmark; biomedical discovery focus |
| 21 | GraphRAG Cost Discussion (GitHub) | Tertiary | Medium | Community reports: $7 for 32K-word book; production scaling issues |
| 22 | NashTech GraphRAG Production Report | Secondary | Medium | 50K PDF ingestion failure; days instead of hours; write lock contention |
| 23 | Weaviate GraphRAG Blog | Secondary | Medium | Practical comparison of RAG vs GraphRAG use cases |
| 24 | FalkorDB VectorRAG vs GraphRAG | Secondary | Medium | March 2025 technical challenges analysis for enterprise |
| 25 | "You Probably Don't Need GraphRAG" | Tertiary | Low | Practitioner perspective on overuse; cost-benefit skepticism |
| 26 | Amazon Neuro-Symbolic (2025) | Secondary | Medium | Applied to Vulcan robots and Rufus assistant; production validation |
| 27 | Graphs Meet AI Agents Survey | Secondary | High | Taxonomy of graph + agent integration patterns |
| 28 | NeOn-GPT / LLMs4Life (2024-25) | Primary | Medium | End-to-end ontology construction with adaptive refinement |

---

## Detailed Evidence

### S1: Microsoft GraphRAG

- **URL**: https://github.com/microsoft/graphrag / https://www.microsoft.com/en-us/research/project/graphrag/
- **Type**: Primary (original implementation + paper)
- **Evidence Level**: High
- **Date**: April 2024 (initial); ongoing updates through 2025
- **Key Findings**:
  - Two-stage pipeline: (1) entity/relation extraction + summarization from chunks, (2) community detection + hierarchical summarization
  - LLM used for all reasoning: entity extraction, relationship extraction, entity summarization, community summarization
  - Strong on "global" queries requiring cross-document synthesis
  - Indexing cost 3-5x baseline RAG; query cost 610K tokens per query in original implementation
  - Now integrated into Microsoft Discovery (Azure) with LazyGraphRAG
- **Relevance**: Baseline architecture to compare against; sets the standard but also the cost ceiling

### S2: GraphRAG-Bench (ICLR 2026)

- **URL**: https://arxiv.org/abs/2506.05690 / https://github.com/GraphRAG-Bench/GraphRAG-Benchmark
- **Type**: Primary (peer-reviewed benchmark)
- **Evidence Level**: Very High (ICLR acceptance; systematic evaluation)
- **Date**: June 2025 (arXiv), accepted ICLR 2026
- **Key Findings**:
  - GraphRAG frequently underperforms vanilla RAG on many real-world tasks
  - Graph structures provide measurable benefits only for: multi-hop reasoning, entity relationship queries, complex cross-document synthesis
  - Tasks of increasing difficulty: fact retrieval, complex reasoning, contextual summarization, creative generation
  - Graph advantage increases with query complexity; diminishes for simple factual retrieval
- **Relevance**: Critical for deciding when to invest in graph construction vs. simpler approaches

### S3: LightRAG

- **URL**: https://arxiv.org/html/2410.05779v1
- **Type**: Primary (paper + implementation)
- **Evidence Level**: High
- **Date**: October 2024
- **Key Findings**:
  - Combines knowledge graphs with vector retrieval
  - 100 tokens per query vs 610K for GraphRAG
  - Outperforms GraphRAG on Agriculture, CS, Legal datasets (millions of tokens)
  - 20-30ms faster response times than baseline RAG
  - Merges neighboring subgraphs for multi-hop reasoning
- **Relevance**: Potential lightweight alternative for E3; cost-effective for iterative development

### S4: LazyGraphRAG

- **URL**: https://www.microsoft.com/en-us/research/blog/lazygraphrag-setting-a-new-standard-for-quality-and-cost/
- **Type**: Primary (Microsoft Research)
- **Evidence Level**: High
- **Date**: November 2024
- **Key Findings**:
  - Indexing cost = vector RAG cost (0.1% of full GraphRAG)
  - Defers LLM use to query time (no up-front summarization)
  - Combines best-first and breadth-first search in iterative deepening
  - At 4% of GraphRAG global search cost, outperforms all competing methods
  - Integrated into Microsoft Discovery (June 2025)
- **Relevance**: Shows that lazy/deferred approaches can match full GraphRAG quality at fraction of cost

### S5: E2GraphRAG

- **URL**: https://arxiv.org/abs/2505.24226
- **Type**: Primary (paper + code)
- **Evidence Level**: High
- **Date**: May 2025
- **Key Findings**:
  - 10x faster indexing than GraphRAG
  - 100x faster retrieval than LightRAG
  - Uses SpaCy for entity graph (not LLM), LLM only for summary tree
  - Adaptive retrieval strategy: auto-selects local vs global mode
  - Bidirectional entity-chunk indexes for fast lookup
- **Relevance**: Demonstrates hybrid SpaCy+LLM approach; relevant cost/quality trade-off

### S6: KARMA (NeurIPS 2025 Spotlight)

- **URL**: https://arxiv.org/abs/2502.06472 / https://openreview.net/forum?id=k0wyi4cOGy
- **Type**: Primary (peer-reviewed, NeurIPS spotlight)
- **Evidence Level**: Very High
- **Date**: February 2025
- **Key Findings**:
  - 9 collaborative agents: entity discovery, relation extraction, schema alignment, conflict resolution
  - Schema-guided extraction ensures ontological consistency
  - Tested on 1,200 PubMed articles across 3 domains
  - 38,230 new entities identified; 83.1% LLM-verified correctness
  - 18.6% reduction in conflict edges through multi-layer assessment
  - Conflict Resolution Agents use LLM-based debate mechanisms
- **Relevance**: Most validated multi-agent KG architecture; directly applicable pattern for E3

### S7: FinReflectKG

- **URL**: https://arxiv.org/abs/2508.17906 / https://dl.acm.org/doi/10.1145/3768292.3770363
- **Type**: Primary (ACM conference paper)
- **Evidence Level**: High
- **Date**: August 2025
- **Key Findings**:
  - Three extraction modes: single-pass, multi-pass, reflection-agent
  - Reflection-agent mode: 64.8% compliance score (best); critic-corrector loop
  - Iterative refinement catches schema violations AND discovers missed triples
  - Produces denser yet cleaner graphs than single-pass
  - Comprehensive evaluation: rule-based + statistical + LLM-as-Judge
- **Relevance**: Validates reflection/iterative refinement pattern for KG quality

### S8: KAG / OpenSPG (Ant Group)

- **URL**: https://arxiv.org/abs/2409.13731 / https://github.com/OpenSPG/KAG
- **Type**: Primary (paper + production system)
- **Evidence Level**: Very High (production-validated at Ant Group scale)
- **Date**: September 2024 (paper), January 2025 (updates)
- **Key Findings**:
  - Bidirectional LLM-KG enhancement across 5 aspects
  - Logical-form-guided hybrid reasoning engine
  - Mutual indexing between KG and original chunks
  - 19.6% improvement on 2wiki, 33.5% on hotpotQA (F1)
  - Production: E-Government (91.6% precision), E-Health (1.8M entities, 5M relationships)
  - Lightweight Build mode: 89% reduction in token costs
  - SPG (Semantic-enhanced Programmable Graph) as foundation
- **Relevance**: Best production evidence for hybrid KG+RAG; schema-guided approach matches E3 needs

### S9: Graphiti / Zep

- **URL**: https://github.com/getzep/graphiti / https://arxiv.org/abs/2501.13956
- **Type**: Primary (paper + open-source framework)
- **Evidence Level**: High
- **Date**: January 2025
- **Key Findings**:
  - Temporal knowledge graph for agent memory
  - Real-time incremental updates without batch recomputation
  - Hybrid search: semantic embeddings + BM25 + graph traversal
  - No LLM calls during retrieval (P95 latency: 300ms)
  - Supports both prescribed and learned ontology
  - 18.5% accuracy improvement over MemGPT; 90% latency reduction
- **Relevance**: Directly relevant for agent memory layer; temporal awareness critical for methodology evolution

### S10: DSPy for KG Construction

- **URL**: https://arxiv.org/abs/2506.19773 / https://github.com/chrisammon3000/dspy-neo4j-knowledge-graph
- **Type**: Primary (empirical study)
- **Evidence Level**: Medium (limited scale evaluation)
- **Date**: June 2025
- **Key Findings**:
  - DSPy, APE, TextGrad all outperform baseline prompts for entity/relation/triple extraction
  - Cost: <$0.10 per pipeline run with Gemini Flash
  - Pipeline runs in under a minute
  - Generates Cypher statements for Neo4j graph creation
- **Relevance**: Cost-effective extraction module; could be component in larger pipeline

### S11: Neo4j LLM Graph Builder

- **URL**: https://neo4j.com/labs/genai-ecosystem/llm-graph-builder/ / https://github.com/neo4j-labs/llm-graph-builder
- **Type**: Secondary (production tool, not peer-reviewed)
- **Evidence Level**: Medium
- **Date**: January 2025 (latest release)
- **Key Findings**:
  - Supports multiple LLMs (GPT-5.x, Claude 4.5, Gemini 2.5, etc.)
  - Community summarization via clustering (GraphRAG-style)
  - Token tracking per user
  - Handles PDFs, web pages, YouTube transcripts, images
  - Docker Compose deployment; React + FastAPI
- **Relevance**: Ready-made tool; could accelerate initial KG construction for E3

### S12: LlamaIndex PropertyGraphIndex

- **URL**: https://docs.llamaindex.ai/en/stable/examples/property_graph/property_graph_basic/
- **Type**: Secondary (framework documentation)
- **Evidence Level**: Medium
- **Date**: 2024-2025
- **Key Findings**:
  - Upgrade from triples to proper property graphs (labels, properties)
  - Modular: pluggable KG constructors and retrievers
  - Concurrent querying techniques
  - Neo4j integration available
- **Relevance**: Framework option for rapid prototyping; modular design aligns with RaiSE architecture

### S13: DO-RAG

- **URL**: https://arxiv.org/html/2505.17058v1
- **Type**: Primary (paper)
- **Evidence Level**: High
- **Date**: May 2025
- **Key Findings**:
  - Domain-specific QA framework using KG-enhanced RAG
  - Near-perfect recall and 94%+ answer relevancy in domain-specific contexts
  - Up to 33.38% improvement over baseline frameworks
  - Dual-pathway: entity paths + contextual evidence
- **Relevance**: Validates that KG-enhanced retrieval is superior for domain-specific QA (which is E3's exact use case)

### S14: Ontology Learning Comparison

- **URL**: https://arxiv.org/abs/2511.05991
- **Type**: Primary (paper)
- **Evidence Level**: High
- **Date**: November 2025
- **Key Findings**:
  - DB-derived ontologies match text-derived ones at lower cost and better maintainability
  - Ontology-guided KGs with chunk info achieve competitive performance with SOTA
  - Substantially outperform vector retrieval baselines
  - Schema stability from structured sources reduces maintenance
- **Relevance**: Informs ontology sourcing strategy; suggests starting with structured schema is viable

### S15: LLM-empowered KGC Survey

- **URL**: https://arxiv.org/html/2510.20345v1
- **Type**: Secondary (survey, ICAIS 2025)
- **Evidence Level**: High
- **Date**: October 2025
- **Key Findings**:
  - Comprehensive taxonomy: closed IE, open IE, schema-guided, schema-free
  - Schema-guided approaches consistently outperform schema-free for domain KGs
  - LLMs excel at entity/relation extraction but struggle with complex ontological reasoning
  - NeOn-GPT and LLMs4Life advance end-to-end ontology construction
- **Relevance**: Survey validates schema-guided approach for domain-specific KG construction

### S16: Neuro-Symbolic Design Patterns

- **URL**: https://journals.sagepub.com/doi/10.1177/29498732251377499
- **Type**: Secondary (design patterns paper)
- **Evidence Level**: Medium
- **Date**: 2025
- **Key Findings**:
  - 6 design patterns for LLM + symbolic systems
  - Dual-mode validation: LLM generates, symbolic system validates
  - Enterprise pipelines use KG as factual basis to enforce logical consistency
  - Layered approach: auditable and trustworthy
- **Relevance**: Design pattern guidance for E3's neuro-symbolic architecture

### S17: Graph RAG Survey (OpenReview)

- **URL**: https://openreview.net/pdf?id=9FJiOMuZkr
- **Type**: Secondary (survey)
- **Evidence Level**: High
- **Date**: 2025
- **Key Findings**:
  - Taxonomy of Graph-RAG approaches
  - Evaluation framework for comparing approaches
  - Identifies gaps in current benchmarks
- **Relevance**: Comprehensive overview for positioning E3's approach

### S18: LOGOS Schema Induction

- **URL**: https://arxiv.org/pdf/2509.24294
- **Type**: Primary (paper)
- **Evidence Level**: High
- **Date**: September 2025
- **Key Findings**:
  - LLM-driven end-to-end grounded theory development
  - Outperforms 4 competing workflows on 5 diverse datasets
  - Integrates schema induction with evidence grounding
- **Relevance**: Schema induction approach applicable to Scaling Up methodology ontology

### S19: RIGOR Ontology Learning

- **URL**: https://arxiv.org/pdf/2506.01232
- **Type**: Primary (paper)
- **Evidence Level**: Medium
- **Date**: June 2025
- **Key Findings**:
  - RAG-enhanced ontology: combines DB schema + domain ontologies + growing core
  - Delta ontology fragments with provenance tags
  - Judge-LLM refines before merging
- **Relevance**: Incremental ontology building pattern; applicable to growing ScaleUp ontology

### S20: BioKGBench

- **URL**: Referenced in multiple sources
- **Type**: Primary (benchmark)
- **Evidence Level**: Medium
- **Date**: 2024
- **Key Findings**:
  - Domain-constrained KG QA benchmark
  - Shifts from encyclopedic to domain-specific evaluation
- **Relevance**: Benchmark design patterns for evaluating E3's KG quality

### S21-25: Community/Production Evidence

- **Sources**: GitHub discussions, engineering blogs, practitioner posts
- **Evidence Level**: Low-Medium (anecdotal but valuable for practical insights)
- **Key Findings**:
  - GraphRAG production cost: ~$7 per 32K-word book
  - NashTech: 50K PDF ingestion failed at scale (days instead of hours)
  - Write lock contention, rate limit saturation at scale
  - Community consensus: GraphRAG over-engineered for most use cases

### S26: Amazon Neuro-Symbolic Production

- **URL**: Referenced in search results
- **Type**: Secondary
- **Evidence Level**: Medium
- **Date**: 2025
- **Key Findings**:
  - Applied to Vulcan warehouse robots and Rufus shopping assistant
  - Enhances accuracy and decision-making in production
- **Relevance**: Production validation of neuro-symbolic approaches at scale

### S27: Graphs Meet AI Agents Survey

- **URL**: https://arxiv.org/html/2506.18019v1
- **Type**: Secondary (survey)
- **Evidence Level**: High
- **Date**: June 2025
- **Key Findings**:
  - Taxonomy of graph + agent integration patterns
  - Dynamic graph evolution as key challenge for agent memory
- **Relevance**: Framework for understanding where E3 fits in the landscape

### S28: NeOn-GPT / LLMs4Life

- **URL**: Referenced in survey S15
- **Type**: Primary (papers)
- **Evidence Level**: Medium
- **Date**: 2024-2025
- **Key Findings**:
  - End-to-end ontology construction with ontology reuse
  - Adaptive refinement workflows
  - Prompt-driven for accessibility
- **Relevance**: Ontology construction patterns for ScaleUp methodology
