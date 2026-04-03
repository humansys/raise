# R1: Neurosymbolic Memory Architectures for AI Agents

**Date:** 2026-03-24
**Researcher:** Rai (Claude Opus 4.6)
**Searches conducted:** 14 queries across WebSearch + 8 WebFetch deep reads

## Research Question

What is the state of the art in combining symbolic knowledge representations (typed knowledge graphs with schema validation and deterministic traversal) with LLM-based agents for grounding and reasoning? What architectures exist, what are their trade-offs, and where are the gaps?

**Context:** We are building a system where an LLM agent uses a typed knowledge graph (Pydantic schemas, NetworkX, spreading activation) as its primary grounding mechanism — not vector RAG alone, but a symbolic graph with typed nodes, typed relationships, and deterministic traversal. The neural component handles extraction and query interpretation; the symbolic component handles storage, validation, and retrieval.

---

## Evidence Catalog

### Source 1: SYNAPSE — Spreading Activation for Agent Memory
- **Authors/Org:** Hanqi Jiang, Junhao Chen, Yi Pan, Ling Chen, Weihang You, Yifan Zhou, Ruidong Zhang, Andrea Sikora, Lin Zhao, Yohannes Abate, Tianming Liu
- **Year:** 2026
- **URL:** https://arxiv.org/abs/2601.02744
- **Type:** paper (arXiv, v3 Feb 2026)
- **Evidence Level:** Very High
- **Key Finding:** Models agent memory as a dynamic graph with episodic nodes (interaction turns) and semantic nodes (extracted concepts). Retrieval via spreading activation with lateral inhibition and temporal decay — not pre-computed links. Triple hybrid retrieval combines semantic similarity (λ₁=0.5), activation energy (λ₂=0.3), and PageRank (λ₃=0.2). Achieves SOTA on LoCoMo (40.5 F1 weighted) with 95% token reduction vs full-context. On low-vector-similarity subsets, SYNAPSE degrades only 7.4% while A-MEM drops 56.3% — demonstrating that graph traversal recovers from bad vector seeds. Includes uncertainty-aware rejection (confidence gating at τ=0.12).
- **Relevance to our work:** **Directly validates our spreading activation approach.** Their architecture (typed nodes, weighted edges, activation propagation with decay) closely mirrors our design. Key parameters: fan-effect dilution, lateral inhibition (top-M=7), sigmoid nonlinearity, T=3 iterations, temporal decay ρ=0.01. Their triple hybrid retrieval is a blueprint for combining our deterministic traversal with embedding-based search.

### Source 2: MAGMA — Multi-Graph Agentic Memory Architecture
- **Authors/Org:** Dongming Jiang, Yi Li, Guanpeng Li, Bingzhe Li (UT Dallas, U of Florida)
- **Year:** 2026
- **URL:** https://arxiv.org/abs/2601.03236
- **Type:** paper (arXiv, Jan 2026)
- **Evidence Level:** High
- **Key Finding:** Represents each memory item across four orthogonal graphs: semantic, temporal, causal, and entity. Retrieval formulated as policy-guided traversal over these relational views. 45.5% higher reasoning accuracy on long-context benchmarks vs prior methods, 95%+ token reduction, 40% faster query latency. Key insight: decoupling memory representation from retrieval logic enables transparent reasoning paths.
- **Relevance to our work:** Validates the multi-view graph approach. Our typed nodes and relationships could be viewed through similar orthogonal lenses. Their separation of "memory representation" from "retrieval logic" aligns with our architecture where the graph is the canonical store and different traversal strategies can be applied independently.

### Source 3: HippoRAG / HippoRAG 2 — Neurobiologically Inspired Memory
- **Authors/Org:** Bernal Jiménez Gutiérrez, Yiheng Shu, Yu Gu, Michihiro Yasunaga, Yu Su (OSU NLP Group)
- **Year:** 2024 (NeurIPS 2024) / 2025 (ICML 2025)
- **URL:** https://arxiv.org/abs/2405.14831 (v1), https://arxiv.org/abs/2502.14802 (v2/HippoRAG2)
- **Type:** paper (NeurIPS 2024, ICML 2025)
- **Evidence Level:** Very High
- **Key Finding:** LLM as neocortex (processing), KG as hippocampal index (storage), Personalized PageRank for retrieval. Outperforms SOTA RAG by up to 20% on multi-hop QA. Single-step retrieval is 10-30x cheaper and 6-13x faster than iterative methods like IRCoT. HippoRAG 2 extends with deeper passage integration, achieving 7% improvement on associative memory tasks. The schemaless KG construction is key: LLM transforms corpus into KG, then PPR ranks nodes for retrieval.
- **Relevance to our work:** The hippocampal indexing theory provides theoretical grounding for our architecture. Their use of PPR as the traversal algorithm is a proven alternative/complement to spreading activation. Key difference: their KG is schemaless (emergent), ours is typed (prescribed). This is a design trade-off we should explicitly acknowledge.

### Source 4: Zep/Graphiti — Temporal Knowledge Graph for Agent Memory
- **Authors/Org:** Preston Rasmussen, Pavlo Paliychuk, Travis Beauvais, Jack Ryan, Daniel Chalef (Zep AI)
- **Year:** 2025
- **URL:** https://arxiv.org/abs/2501.13956
- **Type:** paper (arXiv, Jan 2025) + production system
- **Evidence Level:** Very High
- **Key Finding:** Three-layer KG: episode subgraph (raw input), semantic entity subgraph (extracted entities/relationships), community subgraph (clusters with summaries). Bi-temporal model with four timestamps per edge (t'_created, t'_expired, t_valid, t_invalid). Temporal invalidation via LLM comparison of new vs existing edges. Three search methods: cosine similarity, BM25, BFS. Supports Pydantic models for entity/edge type definitions — either prescribed (schema-first) or learned (emergent). Uses Neo4j. Outperforms MemGPT (94.8% vs 93.4% on DMR), 18.5% accuracy improvement and 90% latency reduction on LongMemEval.
- **Relevance to our work:** **Closest production system to our architecture.** Their Pydantic-based entity/edge types, temporal tracking, and hybrid search are directly analogous. Key differences: they use Neo4j (graph DB), we use NetworkX (in-process); they do incremental community detection via label propagation, we do spreading activation. Their bi-temporal model is more sophisticated than simple temporal decay — worth considering.

### Source 5: A-MEM — Agentic Memory (Zettelkasten-inspired)
- **Authors/Org:** Wujiang Xu, Zujie Liang, Kai Mei, Hang Gao, Juntao Tan, Yongfeng Zhang
- **Year:** 2025 (NeurIPS 2025)
- **URL:** https://arxiv.org/abs/2502.12110
- **Type:** paper (NeurIPS 2025)
- **Evidence Level:** High
- **Key Finding:** Dynamic knowledge-network inspired by Zettelkasten. Generates structured notes with contextual descriptions, keywords, tags. New memories trigger updates to existing memories. Agent-driven decision making for memory management. Accepted at NeurIPS 2025, demonstrating mainstream recognition of graph-based agent memory.
- **Relevance to our work:** The Zettelkasten analogy is useful for explaining our approach. Their dynamic linking and memory evolution align with our graph update patterns. However, their structure is less typed than ours — more emergent network than prescribed schema.

### Source 6: Microsoft GraphRAG
- **Authors/Org:** Microsoft Research (Darren Edge et al.)
- **Year:** 2024-2025
- **URL:** https://arxiv.org/abs/2404.16130, https://microsoft.github.io/graphrag/
- **Type:** paper + production system
- **Evidence Level:** Very High
- **Key Finding:** Two-stage approach: LLM extracts entity KG from source documents, then community summaries are pre-generated for clusters of related entities. Hierarchical community structure enables both local (entity-level) and global (theme-level) queries. Substantial improvements over naive RAG for comprehensiveness and diversity on global sensemaking questions. LazyGraphRAG variant reduces cost. Now integrated into Microsoft Discovery platform.
- **Relevance to our work:** Their community detection + summarization is a pattern we could adopt for our graph's higher-level abstractions. Key difference: GraphRAG is batch-oriented (index → query), while our system needs incremental updates. Their hierarchical approach (entity → community → global summary) maps to our node type hierarchy.

### Source 7: Graph Retrieval-Augmented Generation Survey (ACM TOIS)
- **Authors/Org:** Boci Peng, Yun Zhu, Yongchao Liu, Xiaohe Bo, Haizhou Shi, Chuntao Hong, Yan Zhang, Siliang Tang
- **Year:** 2024
- **URL:** https://arxiv.org/abs/2408.08921
- **Type:** survey (ACM Transactions on Information Systems)
- **Evidence Level:** Very High
- **Key Finding:** First comprehensive GraphRAG survey. Three-stage taxonomy: G-Indexing (graph construction), G-Retrieval (graph-guided search), G-Enhanced Generation (graph-informed output). Three categories: Knowledge-based (existing KGs), Index-based (self-constructed), Hybrid. GraphRAG captures relational knowledge that flat vector retrieval misses, enabling multi-hop reasoning.
- **Relevance to our work:** Provides the taxonomic framework for positioning our system. We are "Index-based" (self-constructed graph) with potential "Hybrid" extensions (if we integrate external KGs). Our three-phase architecture (extraction → storage → retrieval) maps cleanly to their G-Indexing → G-Retrieval → G-Generation.

### Source 8: Memory in the Age of AI Agents (Survey)
- **Authors/Org:** Yuyang Hu, Shichun Liu, et al. (50+ authors, multi-institutional)
- **Year:** 2025-2026
- **URL:** https://arxiv.org/abs/2512.13564
- **Type:** survey (arXiv, Dec 2025, revised Jan 2026)
- **Evidence Level:** High
- **Key Finding:** Three-dimensional taxonomy: Forms (token-level, parametric, latent), Functions (factual, experiential, working), Dynamics (formation, evolution, retrieval). Graph-based memory falls under "Planar" organization within token-level forms. Key frontier: memory automation, RL integration, multi-agent memory, trustworthiness. The field is fragmented — no consensus architecture.
- **Relevance to our work:** Positions our system within the broader taxonomy. Our knowledge graph is "Planar" form, serving "factual" function primarily, with "experiential" as secondary. The identified fragmentation validates our approach of building from first principles rather than adopting any single framework.

### Source 9: Spreading Activation for KG-RAG (Cognee)
- **Authors/Org:** Jovan Pavlović, Miklós Krész, László Hajdu (U of Primorska, Cognee Inc.)
- **Year:** 2025
- **URL:** https://arxiv.org/html/2512.15922v1
- **Type:** paper (arXiv, Dec 2025)
- **Evidence Level:** High
- **Key Finding:** Four-stage pipeline: indexing (LLM extracts entities/relations → KG with three node types), subgraph fetching (top-k entity descriptions via cosine similarity + n-hop expansion), spreading activation (breadth-first with formula: activation[target] = min(1, activation[target] + weight·activation[node]), c=0.4 rescaling), document retrieval (threshold τₐ=0.5). SA-RAG + CoT achieves 25-39% absolute gains over naive RAG on MuSiQue and 2WikiMultiHopQA.
- **Relevance to our work:** **Directly validates spreading activation on KGs for retrieval.** Their activation formula and threshold parameters are reference implementations. Three node types (entities, descriptions, chunks) parallel our typed node approach. The c=0.4 rescaling factor to prevent overactivation is an important engineering parameter.

### Source 10: MemGPT / Letta — LLM as Operating System
- **Authors/Org:** Charles Packer, Sarah Wooders et al. (UC Berkeley → Letta Inc.)
- **Year:** 2023-2025
- **URL:** https://arxiv.org/abs/2310.08560
- **Type:** paper + production framework
- **Evidence Level:** High
- **Key Finding:** Virtual context management inspired by OS memory hierarchy. Two-tier: main context (in-context window) and external context (out-of-context storage). Agent self-manages memory via tool calls — decides what to page in/out. Now part of Letta framework. DMR benchmark: 93.4% (outperformed by Zep at 94.8%).
- **Relevance to our work:** Represents the "paging" alternative to our "graph traversal" approach. MemGPT treats memory as flat pages; we treat it as a typed graph. Their approach is simpler but loses relational structure. Zep/Graphiti outperforming MemGPT supports our hypothesis that structured graph memory > flat memory management.

### Source 11: Neurosymbolic AI for KG Reasoning (IEEE Survey)
- **Authors/Org:** Lauren Nicole DeLong, Ramon Fernández Mir, Matthew Whyte, Zonglin Ji, Jacques D. Fleuriot (U of Edinburgh)
- **Year:** 2023 (IEEE TNNLS 2024)
- **URL:** https://arxiv.org/abs/2302.07200
- **Type:** survey (IEEE Transactions on Neural Networks and Learning Systems)
- **Evidence Level:** Very High
- **Key Finding:** Three categories of neurosymbolic KG reasoning: (1) logically-informed embeddings, (2) embeddings with logical constraints, (3) rule learning. Key tension: interpretability vs performance. Rule-based inference provides explainability; embeddings provide generalization. Hybrid approaches attempt to bridge this but increase complexity.
- **Relevance to our work:** Provides theoretical grounding for our approach. Our system is primarily category (3) — rule learning via deterministic graph traversal — augmented with neural extraction. The interpretability advantage of symbolic traversal is exactly why we chose this architecture.

### Source 12: Neuro-Symbolic Architectures Taxonomy
- **Authors/Org:** Oualid Bougzime, Samir Jabbar, Christophe Cruz, Frédéric Demoly
- **Year:** 2025
- **URL:** https://arxiv.org/html/2502.11269v1
- **Type:** paper (arXiv, Feb 2025)
- **Evidence Level:** Medium
- **Key Finding:** Five NSAI architecture types: Sequential (Sym→Neuro→Sym), Nested (Sym[Neuro] or Neuro[Sym]), Cooperative (Neuro||Sym with feedback), Compiled (symbolic loss/constraints), Ensemble (Neuro→Sym←Neuro). The Ensemble pattern "consistently outperforms its counterparts across all evaluation metrics." Key limitations: scalability, complexity of maintaining efficiency, difficulty adapting without retraining.
- **Relevance to our work:** Our architecture is **Cooperative** — the LLM and KG iterate with feedback loops (LLM extracts → KG stores → KG retrieves → LLM reasons). Understanding this taxonomy helps position our design decisions and anticipate known trade-offs.

### Source 13: Graph of Thoughts (GoT)
- **Authors/Org:** Maciej Besta et al. (ETH Zürich)
- **Year:** 2023 (AAAI 2024)
- **URL:** https://arxiv.org/abs/2308.09687
- **Type:** paper (AAAI 2024)
- **Evidence Level:** High
- **Key Finding:** LLM thoughts as vertices, dependencies as edges, forming arbitrary graphs (not just chains or trees). Enables combining thoughts into synergistic outcomes and feedback loops. 62% quality improvement over Tree of Thoughts on sorting, 31% cost reduction. Extensions: Adaptive GoT (dynamic DAGs), Knowledge GoT (externalized reasoning with KGs).
- **Relevance to our work:** GoT models reasoning topology; our KG models knowledge topology. They are complementary — GoT could orchestrate multi-step queries over our knowledge graph. The Knowledge GoT (KGoT) variant is particularly relevant as it connects reasoning graphs with external knowledge structures.

### Source 14: Pydantic for Knowledge Graph Construction
- **Authors/Org:** Various (LangChain, Pydantic AI ecosystem)
- **Year:** 2024-2025
- **URL:** https://dev.to/jhagerer/knowledge-graph-extraction-in-pydantic-32on, https://www.latent.space/p/pydantic
- **Type:** blog + docs
- **Evidence Level:** Medium
- **Key Finding:** Pydantic schemas define ontology (entity categories, attributes, relationships) as data models. LLM structured output with Pydantic ensures type safety and validation at extraction time. Triplet pattern (subject, predicate, object) maps naturally to Pydantic models. pydantic-graph library provides async graph/state machine primitives. Samuel Colvin (Pydantic creator) has discussed "Agent Engineering with Pydantic + Graphs" explicitly.
- **Relevance to our work:** **Validates our technology choices.** Pydantic for schema validation + graph structure is an emerging pattern with ecosystem support. Our approach of typed Pydantic models for nodes and relationships is well-aligned with the direction the ecosystem is moving.

### Source 15: KAG — Knowledge Augmented Generation (Ant Group)
- **Authors/Org:** Ant Group / OpenSPG
- **Year:** 2025
- **URL:** https://dl.acm.org/doi/10.1145/3701716.3715240
- **Type:** paper (WWW 2025 Companion)
- **Evidence Level:** Medium
- **Key Finding:** Three-phase approach: (1) indexing — extraction + semantic reasoning, (2) reasoning — questions transformed into Logical Forms, (3) retrieval — semantic relationship prediction. Establishes semantic relationships between keywords. The Logical Form transformation is notable — it bridges natural language queries to structured graph queries.
- **Relevance to our work:** The query→LogicalForm transformation is relevant to our query interpretation layer. Instead of embedding-only retrieval, translating queries into graph traversal operations (as KAG does) aligns with our deterministic traversal philosophy.

### Source 16: LlamaIndex PropertyGraph Index
- **Authors/Org:** LlamaIndex (Jerry Liu et al.)
- **Year:** 2024-2025
- **URL:** https://www.llamaindex.ai/blog/introducing-the-property-graph-index-a-powerful-new-way-to-build-knowledge-graphs-with-llms
- **Type:** docs + production framework
- **Evidence Level:** Medium
- **Key Finding:** Modular property graph with multiple retrieval strategies: LLMSynonymRetriever (keyword expansion), VectorContextRetriever (embedding similarity), TextToCypherRetriever (natural language → graph query), CypherTemplateRetriever (parameterized queries). Strategies can be composed for hybrid search. Designed for Neo4j, Memgraph, or other graph DBs.
- **Relevance to our work:** Their multi-retriever composition pattern is relevant. However, their dependency on graph databases (Neo4j/Memgraph) contrasts with our lightweight NetworkX approach. The TextToCypher pattern (NL → structured query) is analogous to our LLM-interpreted graph traversal.

### Source 17: CrewAI / Microsoft Agent Framework Memory Systems
- **Authors/Org:** CrewAI Inc., Microsoft
- **Year:** 2025
- **URL:** https://www.datacamp.com/tutorial/crewai-vs-langgraph-vs-autogen
- **Type:** docs + production frameworks
- **Evidence Level:** Medium
- **Key Finding:** CrewAI implements four memory layers: short-term (task context), long-term (cross-session insights), entity (people/concepts), contextual (integration layer). Microsoft Agent Framework (AutoGen + Semantic Kernel merger, GA May 2025) adds graph-based workflows for multi-agent orchestration with Azure AI Search integration. Neither provides true graph-structured memory — they use vector stores with metadata tagging.
- **Relevance to our work:** Demonstrates the industry gap: major agent frameworks still treat memory as vector stores with metadata, not as typed knowledge graphs. This validates our differentiation. Their "entity memory" concept is the closest to our approach but lacks typed relationships and deterministic traversal.

### Source 18: MemoryScope / ReMe (Alibaba/ModelScope)
- **Authors/Org:** Alibaba / ModelScope
- **Year:** 2024-2025
- **URL:** https://github.com/modelscope/ReMe
- **Type:** production framework
- **Evidence Level:** Low
- **Key Finding:** MemoryScope (Sep 2024) evolved into ReMe (Sep 2025). Personalized, time-aware memory storage. Includes success pattern recognition and failure analysis learning. MCP protocol support added mid-2025. Integrates task memory and personal memory.
- **Relevance to our work:** Their "success pattern recognition" aligns with our pattern memory concept. However, ReMe appears to be primarily vector-based with metadata enrichment rather than true graph structure.

---

## Synthesized Claims

### Claim 1: Graph-structured memory significantly outperforms flat vector memory for multi-hop and temporal reasoning tasks.
- **Confidence:** HIGH
- **Supporting sources:** [1] SYNAPSE, [2] MAGMA, [3] HippoRAG, [4] Zep/Graphiti, [9] SA-RAG
- **Contrary evidence:** Source [8] (Memory survey) notes that "simple retrieval baselines have been shown to outperform more complex memory structures on both LoCoMo and LongMemEval" for certain question types. The advantage of graph structure is most pronounced for multi-hop, temporal, and associative queries — for simple factual recall, vector similarity is often sufficient.

### Claim 2: Spreading activation is a validated and effective retrieval mechanism for knowledge-graph-based agent memory.
- **Confidence:** HIGH
- **Supporting sources:** [1] SYNAPSE (SOTA on LoCoMo), [3] HippoRAG (PPR variant, NeurIPS+ICML), [9] Cognee SA-RAG (25-39% gains over naive RAG)
- **Contrary evidence:** None found directly contradicting. However, [4] Zep achieves competitive results with simpler BFS+BM25+cosine combination, suggesting spreading activation may not always be necessary — simpler hybrid search can suffice for many use cases.

### Claim 3: Typed schemas (Pydantic models) for knowledge graph nodes and edges are an emerging production pattern, not just a research idea.
- **Confidence:** HIGH
- **Supporting sources:** [4] Graphiti explicitly uses Pydantic for entity/edge type definitions, [14] Pydantic ecosystem movement toward KG construction, [16] LlamaIndex PropertyGraph
- **Contrary evidence:** Most research systems ([1], [2], [3], [5]) use ad-hoc or schemaless representations. Typed schemas add rigidity that may limit emergent knowledge capture. The field is split between "prescribed" (typed) and "learned" (emergent) schemas.

### Claim 4: Temporal awareness (invalidation, bi-temporal tracking, decay) is essential for agent memory in production.
- **Confidence:** HIGH
- **Supporting sources:** [1] SYNAPSE (temporal decay ρ=0.01), [4] Zep (bi-temporal with 4 timestamps per edge), [2] MAGMA (separate temporal graph)
- **Contrary evidence:** None. Every competitive system includes some form of temporal modeling. The question is how sophisticated — simple decay vs bi-temporal tracking.

### Claim 5: The neurosymbolic architecture for agent memory is "Cooperative" — LLM and KG iterate with feedback loops, not a one-shot pipeline.
- **Confidence:** HIGH
- **Supporting sources:** [12] NSAI taxonomy (Cooperative pattern), [1] SYNAPSE (LLM extracts, graph stores, activation retrieves, LLM reasons), [4] Zep (LLM extracts entities, KG stores with temporal tracking, hybrid search retrieves)
- **Contrary evidence:** [6] Microsoft GraphRAG is more "Sequential" (batch index, then query). For some use cases, batch processing is sufficient and simpler.

### Claim 6: In-process graph libraries (NetworkX) are underrepresented in the literature relative to graph databases (Neo4j).
- **Confidence:** MEDIUM
- **Supporting sources:** [4] Zep uses Neo4j, [16] LlamaIndex targets Neo4j/Memgraph, [6] GraphRAG uses its own graph store. NetworkX appears primarily in tutorial/blog content, not in benchmark-winning systems.
- **Contrary evidence:** [3] HippoRAG uses in-memory graph structures for PPR computation. The SYNAPSE paper [1] does not specify Neo4j dependency. For smaller-scale agent memory (not enterprise knowledge bases), in-process graphs may be sufficient — the literature simply hasn't benchmarked this trade-off.

### Claim 7: Hallucination in KG construction (LLM-extracted triples) is a recognized open problem.
- **Confidence:** HIGH
- **Supporting sources:** [4] Zep uses "reflexion" technique to minimize extraction hallucinations, [14] multiple sources note LLM-extracted "hallucinated triples," [11] neurosymbolic survey discusses grounding challenges
- **Contrary evidence:** None contradicting the problem — only proposed mitigations (reflection, multi-pass verification, schema constraints). Typed schemas (our approach) are one mitigation but not complete.

### Claim 8: No existing system combines all of: typed Pydantic schemas + in-process graph (NetworkX) + spreading activation + deterministic traversal as a primary architecture.
- **Confidence:** HIGH
- **Supporting sources:** Surveyed all 18 sources — no system combines all four. Graphiti has Pydantic + graph but uses Neo4j + BFS (not spreading activation). SYNAPSE has spreading activation + graph but no typed schemas. HippoRAG has PPR + graph but schemaless.
- **Contrary evidence:** None found. This represents a genuine architectural gap/opportunity.

---

## Gaps Identified

### Gap 1: NetworkX-scale benchmarking
No benchmarks evaluate graph-based agent memory with in-process graphs (NetworkX, igraph) vs graph databases (Neo4j). All competitive systems assume a graph DB. For small-to-medium agent memory (hundreds to low thousands of nodes), the overhead of a graph DB may be unnecessary, but there is no evidence either way.

### Gap 2: Schema rigidity vs emergent knowledge
The literature is split between prescribed schemas (Graphiti) and schemaless/emergent graphs (HippoRAG, SYNAPSE). No system explores a hybrid where core types are prescribed but the graph can extend with emergent types. This is precisely our design — worth validating.

### Gap 3: Validation at ingestion boundary
While Pydantic extraction is discussed, no system benchmarks the impact of schema validation at the extraction boundary on downstream retrieval quality. Does rejecting ill-formed triples improve retrieval accuracy? No evidence found.

### Gap 4: Spreading activation + typed schemas
SYNAPSE proves spreading activation works; Graphiti proves typed schemas work. Nobody has combined them. The interaction effects are unknown — does type-aware activation propagation (e.g., different decay rates per relationship type) improve retrieval?

### Gap 5: Multi-agent shared knowledge graphs
Source [8] identifies multi-agent memory as a frontier. No system benchmarks multiple agents reading/writing the same typed knowledge graph concurrently.

### Gap 6: Cost-performance at small scale
Most benchmarks focus on large-scale scenarios (1M+ tokens, hundreds of sessions). For a developer tool / personal agent with moderate memory needs, the optimal architecture may differ. No benchmarks exist for this regime.

---

## Relevance to Knowledge Cartridge Architecture

### What the literature validates in our design:

1. **Spreading activation works.** SYNAPSE (Source 1) and Cognee SA-RAG (Source 9) prove this with specific parameters we can reference. Key numbers: c=0.4 rescaling, τₐ=0.5 activation threshold, T=3 iterations, ρ=0.01 temporal decay.

2. **Typed schemas are production-ready.** Graphiti (Source 4) uses Pydantic for entity/edge types in production. The ecosystem (Source 14) is moving this direction.

3. **Hybrid retrieval is essential.** Every competitive system combines multiple retrieval strategies. SYNAPSE's triple hybrid (semantic + activation + PageRank) is the reference design. Zep's triple (cosine + BM25 + BFS) is the simpler alternative.

4. **Temporal modeling is table stakes.** Every competitive system tracks time. Zep's bi-temporal model is the most sophisticated; SYNAPSE's exponential decay is the simplest effective approach.

5. **The cooperative neurosymbolic pattern is correct.** LLM extracts → graph stores → graph retrieves → LLM reasons. This is the dominant architecture across all competitive systems.

### Where we are novel (and unvalidated):

1. **NetworkX as primary store** — no competitive system uses this. We need to prove it scales to our requirements or have a migration path to a graph DB.

2. **Typed schemas + spreading activation** — nobody has combined these. This is our unique contribution and our biggest risk.

3. **In-process, single-agent focus** — the literature assumes server-based graph DBs and multi-user scenarios. Our lightweight, embedded approach is unexplored territory.

### Recommended architectural decisions based on evidence:

| Decision | Recommendation | Evidence |
|----------|---------------|----------|
| Retrieval strategy | Triple hybrid: embedding + spreading activation + structural importance | Sources 1, 4, 9 |
| Activation parameters | Start with SYNAPSE defaults: T=3 iterations, lateral inhibition M=7, temporal decay ρ=0.01 | Source 1 |
| Temporal model | Start with exponential decay; consider bi-temporal if invalidation becomes important | Sources 1, 4 |
| Schema approach | Prescribed core types (Pydantic) with extension mechanism for emergent types | Sources 4, 14 |
| Extraction validation | Reflexion/multi-pass verification for LLM-extracted triples; reject malformed | Sources 4, 7 |
| Confidence gating | Implement uncertainty-aware rejection (SYNAPSE τ_gate=0.12 pattern) | Source 1 |
| Benchmark targets | LoCoMo and LongMemEval are the standard; target LoCoMo F1 > 35 as minimum | Sources 1, 2, 4, 8 |

---

## Sources

- [SYNAPSE: Empowering LLM Agents with Episodic-Semantic Memory via Spreading Activation](https://arxiv.org/abs/2601.02744)
- [MAGMA: A Multi-Graph based Agentic Memory Architecture for AI Agents](https://arxiv.org/abs/2601.03236)
- [HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models](https://arxiv.org/abs/2405.14831)
- [From RAG to Memory: Non-Parametric Continual Learning for LLMs (HippoRAG 2)](https://arxiv.org/abs/2502.14802)
- [Zep: A Temporal Knowledge Graph Architecture for Agent Memory](https://arxiv.org/abs/2501.13956)
- [A-MEM: Agentic Memory for LLM Agents](https://arxiv.org/abs/2502.12110)
- [Microsoft GraphRAG](https://arxiv.org/abs/2404.16130)
- [Graph Retrieval-Augmented Generation: A Survey (ACM TOIS)](https://arxiv.org/abs/2408.08921)
- [Memory in the Age of AI Agents: A Survey](https://arxiv.org/abs/2512.13564)
- [Leveraging Spreading Activation for KG-RAG Systems](https://arxiv.org/html/2512.15922v1)
- [MemGPT: Towards LLMs as Operating Systems](https://arxiv.org/abs/2310.08560)
- [Neurosymbolic AI for Reasoning over Knowledge Graphs: A Survey (IEEE TNNLS)](https://arxiv.org/abs/2302.07200)
- [Unlocking the Potential of Generative AI through Neuro-Symbolic Architectures](https://arxiv.org/html/2502.11269v1)
- [Graph of Thoughts: Solving Elaborate Problems with LLMs](https://arxiv.org/abs/2308.09687)
- [KAG: Knowledge Augmented Generation (WWW 2025)](https://dl.acm.org/doi/10.1145/3701716.3715240)
- [LlamaIndex PropertyGraph Index](https://www.llamaindex.ai/blog/introducing-the-property-graph-index-a-powerful-new-way-to-build-knowledge-graphs-with-llms)
- [Graphiti GitHub (Zep AI)](https://github.com/getzep/graphiti)
- [Awesome-GraphRAG Paper List](https://github.com/DEEP-PolyU/Awesome-GraphRAG)
- [Awesome-GraphMemory Survey](https://github.com/DEEP-PolyU/Awesome-GraphMemory)
- [Agent-Memory-Paper-List](https://github.com/Shichun-Liu/Agent-Memory-Paper-List)
