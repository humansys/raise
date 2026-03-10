# RQ3: Memory System Implementations for LLMs -- Evidence Catalog

> **ID:** RES-MEMORY-002
> **Date:** 2026-02-18
> **Status:** Complete
> **Scope:** State of practice survey -- active memory systems for LLMs (2024-2026)
> **Method:** Web search + documentation review + benchmark cross-referencing

---

## Executive Summary

The LLM memory landscape in 2024-2025 has coalesced around a few dominant architectural patterns: (1) virtual context management (MemGPT/Letta), (2) temporal knowledge graphs (Zep/Graphiti), (3) hybrid triple-store architectures (Mem0), (4) hierarchical community graphs (GraphRAG), and (5) agentic self-organizing memory (A-Mem). A key finding is that **no advanced memory system consistently outperforms naive RAG baselines** on the MemoryBench benchmark, suggesting the field is still immature despite rapid commercialization. The most promising results come from hybrid approaches that combine graph structure with vector similarity and temporal indexing.

---

## Systems Surveyed

### 1. MemGPT / Letta

- **Organization:** UC Berkeley (research), Letta Inc. (commercial)
- **Architecture:** Two-tier virtual context management inspired by OS memory hierarchy. "Main context" (in-context, RAM-like) contains core memory blocks (persona, human) that the agent can directly write to via function calls. "External context" (disk-like) includes archival memory (vector DB) and recall memory (conversation history). The agent uses function calls (tool use) to move data between tiers.
- **Memory Format:** Core memory is natural language text in named blocks (persona block, human block). Archival memory is stored in a vector database as text passages. Recall memory stores raw conversation history.
- **Compression Approach:** The agent itself decides what to compress, summarize, or evict from main context. When the context window fills, the agent must explicitly choose what to archive. No automatic summarization -- the LLM makes all memory management decisions via tool calls.
- **Retrieval Strategy:** Embedding similarity search over archival memory. Keyword/date filtering over recall memory. The agent decides when to search and what queries to use.
- **Metrics Reported:** DMR (Deep Memory Retrieval) benchmark: 93.4%. The original paper demonstrated multi-session conversation coherence and document QA over large corpora. LongMemEval results show significant accuracy drops for sustained interactions.
- **Open Source:** Yes. https://github.com/cpacker/MemGPT / https://github.com/letta-ai/letta
- **Source:** [MemGPT paper (arXiv 2310.08560)](https://arxiv.org/abs/2310.08560), [Letta docs](https://docs.letta.com/concepts/memgpt/), [Memory management guide](https://docs.letta.com/advanced/memory-management/)
- **Evidence Level:** Very High (peer-reviewed paper + open-source implementation + benchmarks)
- **Key Insight:** The "OS metaphor" is powerful -- treating the LLM as a processor with limited registers (context window) that must manage its own memory hierarchy via system calls. The agent's ability to self-manage memory is both the strength (flexibility) and weakness (requires many LLM calls for memory operations, adding latency and cost). As of 2025, Letta has rearchitected its agent loop drawing from ReAct and Claude Code patterns, suggesting the original pure-MemGPT loop had practical limitations.

---

### 2. Zep / Graphiti

- **Organization:** Zep AI (commercial + open-source)
- **Architecture:** Temporal knowledge graph-based memory layer. Core component is Graphiti -- a temporally-aware knowledge graph engine. Multi-subgraph hierarchy: (a) Episode Subgraph records episodic memory (raw events/messages), (b) Semantic Entity Subgraph contains extracted entities and facts with high-dimensional embeddings, (c) Community Subgraph groups related entities. Implements a bi-temporal model: timeline T (chronological event ordering) and timeline T' (data ingestion ordering).
- **Memory Format:** Neo4j-backed labeled property graph with temporal annotations. Entities are nodes with embeddings. Facts are edges with timestamps. Episodes are nodes linked to the entities/facts they produced.
- **Compression Approach:** Graphiti does NOT rely on LLM summarization at retrieval time. Instead, it incrementally extracts and deduplicates facts during ingestion. Contradictions and updates are resolved at write time, keeping the graph clean. This is a "compress at write, not at read" philosophy.
- **Retrieval Strategy:** Hybrid: semantic embedding similarity + BM25 keyword matching + direct graph traversal. No LLM calls during retrieval. P95 latency: 300ms.
- **Metrics Reported:** DMR benchmark: 94.8% (vs MemGPT 93.4%). LongMemEval: up to 18.5% accuracy improvement over baselines. 90% latency reduction vs baseline. These are self-reported in their January 2025 paper.
- **Open Source:** Graphiti is open-source (MIT): https://github.com/getzep/graphiti. Zep (the full platform) is commercial with an open-source community edition.
- **Source:** [Zep paper (arXiv 2501.13956)](https://arxiv.org/abs/2501.13956), [Graphiti blog](https://blog.getzep.com/graphiti-knowledge-graphs-for-agents/), [Neo4j case study](https://neo4j.com/blog/developer/graphiti-knowledge-graph-memory/)
- **Evidence Level:** High (arXiv paper + open-source core + benchmark results, but benchmarks are self-reported)
- **Key Insight:** The bi-temporal model is the standout innovation. Most memory systems conflate "when something happened" with "when we learned about it." Zep's separation enables point-in-time queries and proper handling of contradictions/updates. The "compress at write" philosophy avoids the latency penalty of LLM-based retrieval summarization. This is the most sophisticated temporal handling of any system surveyed.

---

### 3. Mem0

- **Organization:** Mem0 AI (YC-backed, $24M Series A as of Oct 2025)
- **Architecture:** Hybrid triple-store: vector database + graph database + key-value store, working in concert. On message ingestion: an Entity Extractor identifies entities as graph nodes, a Relations Generator infers labeled edges, a Conflict Detector flags contradictions, and an LLM-powered Update Resolver decides add/merge/invalidate/skip. Supports four memory types: episodic, semantic, procedural, associative.
- **Memory Format:** Memories stored as natural language facts in vector store, entities and relationships in graph store (Neo4j/Neptune), and structured key-value pairs for fast lookup. Each memory has metadata: user_id, timestamp, confidence, source.
- **Compression Approach:** Active curation during ingestion. The system extracts, deduplicates, and consolidates memories rather than storing raw conversations. Contradictory information triggers conflict resolution. This reduces stored data significantly vs raw conversation logs.
- **Retrieval Strategy:** Hybrid: graph traversal for relational queries + vector similarity for semantic queries + key-value lookup for exact facts. Prioritizes by importance, relevance, and recency.
- **Metrics Reported:** LoCoMo benchmark: 66.9% (vs OpenAI Memory 52.9%). 91% lower P95 latency vs OpenAI. 90% token cost reduction. 26% relative improvement in LLM-as-Judge metric. 41K GitHub stars, 14M downloads, 186M API calls/quarter (Q3 2025).
- **Open Source:** Yes (core). https://github.com/mem0ai/mem0. Commercial platform also available.
- **Source:** [Mem0 paper (arXiv 2504.19413)](https://arxiv.org/abs/2504.19413), [Mem0 research page](https://mem0.ai/research), [AWS integration blog](https://aws.amazon.com/blogs/database/build-persistent-memory-for-agentic-ai-applications-with-mem0-open-source-amazon-elasticache-for-valkey-and-amazon-neptune-analytics/)
- **Evidence Level:** High (arXiv paper + open-source + production usage at scale, but benchmark comparisons are self-reported)
- **Key Insight:** The triple-store hybrid is the most commercially successful approach. The insight that different memory types need different storage backends (vectors for semantic similarity, graphs for relationships, KV for fast facts) is pragmatic and well-validated by adoption numbers. The active curation approach (extract-deduplicate-consolidate) rather than raw storage is a clear pattern across successful systems.

---

### 4. Microsoft GraphRAG

- **Organization:** Microsoft Research
- **Architecture:** Knowledge graph construction + hierarchical community detection + summarization. Pipeline: (1) Slice corpus into TextUnits, (2) Extract entities, relationships, and claims using LLM, (3) Build knowledge graph, (4) Apply Leiden community detection for hierarchical clustering, (5) Generate bottom-up community summaries at each level. Two query modes: "local search" (entity-centric) and "global search" (community-summary-based).
- **Memory Format:** Knowledge graph with entities (nodes), relationships (edges), and claims. Community summaries are natural language. Stored in various backends (Parquet files, databases).
- **Compression Approach:** Hierarchical community summaries replace raw graph data. Dynamic community selection (2024 update) reduces token cost by 77% by eliminating irrelevant community reports during global search. If token budget is limited, lower-level community summaries substitute for detailed descriptions.
- **Retrieval Strategy:** Local search: entity-centric retrieval via embedding similarity, then graph traversal to related entities. Global search: map-reduce over community summaries, rated and filtered for relevance. LazyGraphRAG (2024): deferred summarization that only generates summaries when needed.
- **Metrics Reported:** Global search dramatically outperforms naive RAG on questions requiring holistic dataset understanding. 77% average token cost reduction with dynamic community selection (2024). Specific accuracy numbers are task-dependent; the paper focuses on qualitative improvements in "sensemaking" queries.
- **Open Source:** Yes. https://github.com/microsoft/graphrag
- **Source:** [GraphRAG paper (arXiv 2404.16130)](https://arxiv.org/html/2404.16130v1), [Microsoft Research blog](https://www.microsoft.com/en-us/research/blog/graphrag-unlocking-llm-discovery-on-narrative-private-data/), [Dynamic community selection blog](https://www.microsoft.com/en-us/research/blog/graphrag-improving-global-search-via-dynamic-community-selection/)
- **Evidence Level:** Very High (Microsoft Research paper + open-source + active development + multiple follow-up papers)
- **Key Insight:** GraphRAG is designed for corpus understanding, not conversational memory per se. Its contribution is the insight that **community structure in a knowledge graph enables answering questions that no single document can answer**. The Leiden hierarchical clustering creates multi-resolution summaries that serve different query granularities. The 77% token reduction via dynamic community selection shows that intelligent filtering matters more than brute-force inclusion. However, the indexing cost is very high (many LLM calls to extract entities and generate summaries).

---

### 5. LangMem (LangChain)

- **Organization:** LangChain Inc.
- **Architecture:** Two-layer architecture separating stateless core operations from stateful integrations. Core API Layer provides stateless functions: memory extraction, prompt optimization, thread summarization, message compression. Stateful Integration Layer builds on LangGraph's BaseStore for persistence.
- **Memory Format:** Three memory types with distinct formats: (a) Semantic memory -- extracted facts stored as key-value documents with namespaces (typically keyed by user_id), (b) Episodic memory -- few-shot examples distilled from longer interactions, (c) Procedural memory -- updated instructions written directly into the agent's system prompt.
- **Compression Approach:** `summarize_messages` for short-term context compression. `create_memory_manager` for extracting and consolidating long-term memories from conversations. Prompt optimization rewrites system prompts based on accumulated feedback.
- **Retrieval Strategy:** Semantic search over stored memories via LangGraph's BaseStore. Namespace-scoped retrieval prevents cross-user contamination. Agent can also use explicit memory search tools.
- **Metrics Reported:** No published benchmark numbers. LangMem is positioned as infrastructure/SDK rather than a benchmarked system. The focus is on developer experience and composability.
- **Open Source:** Yes. https://github.com/langchain-ai/langmem
- **Source:** [LangMem docs](https://langchain-ai.github.io/langmem/), [LangMem blog post](https://blog.langchain.com/langmem-sdk-launch/), [Conceptual guide](https://langchain-ai.github.io/langmem/concepts/conceptual_guide/)
- **Evidence Level:** Medium (open-source SDK, well-documented, but no benchmarks or academic validation)
- **Key Insight:** LangMem's distinction between semantic, episodic, and procedural memory is theoretically grounded in cognitive science (Tulving's memory taxonomy). The procedural memory concept -- where the agent's system prompt evolves over time based on interactions -- is unique among the systems surveyed. This is "learning" rather than just "remembering." The two-layer stateless/stateful separation is good engineering for composability but adds complexity.

---

### 6. Cognee

- **Organization:** Topoteretes (open-source company)
- **Architecture:** Extract-Cognify-Load pipeline. Ingests files, APIs, and databases. Chunks content, enriches entities and relationships, adds temporal context, writes both graph structures and embeddings. The "Memify" post-processing pipeline keeps the knowledge graph fresh by cleaning stale nodes, adding associations, and reweighting important memories without full rebuild.
- **Memory Format:** Hybrid knowledge graph + vector embeddings. Supports multiple graph backends: NetworkX (development), Neo4j, FalkorDB (production). Uses LanceDB for vector storage. Entities and relationships form the graph; embeddings enable semantic search.
- **Compression Approach:** Memify pipeline: prunes stale nodes, merges duplicate entities, adds inferred associations, reweights based on importance. Continuous improvement without costly full rebuilds.
- **Retrieval Strategy:** Hybrid: semantic similarity (vector search) + structural context (graph traversal). Combined approach reduces hallucinations by relying on verified, contextually enriched information.
- **Metrics Reported:** No published benchmark comparisons found. Marketing claims focus on hallucination reduction and contextual enrichment rather than specific accuracy numbers.
- **Open Source:** Yes. https://github.com/topoteretes/cognee
- **Source:** [GitHub repo](https://github.com/topoteretes/cognee), [Cognee blog](https://www.cognee.ai/blog/fundamentals/llm-memory-cognitive-architectures-with-ai), [LanceDB case study](https://lancedb.com/blog/case-study-cognee/)
- **Evidence Level:** Medium (open-source, documented architecture, but no benchmark validation)
- **Key Insight:** The "Memify" continuous refinement pipeline is distinctive -- most systems either do full reindexing or only append. Cognee's approach of incremental graph maintenance (prune stale, merge duplicates, reweight) is operationally practical. The multi-backend flexibility (swap NetworkX for FalkorDB without code changes) is good engineering for the development-to-production transition.

---

### 7. LlamaIndex Property Graph Index + Memory Blocks

- **Organization:** LlamaIndex (Run LLC)
- **Architecture:** Two distinct but complementary features: (a) Property Graph Index -- labeled property graph construction from text using LLM extraction, with entity/relationship extraction and storage in graph databases. (b) Memory API -- flexible plug-and-play memory blocks: StaticMemoryBlock (fixed context), FactExtractionMemoryBlock (dynamic fact extraction from conversations), VectorMemoryBlock (semantic search over past interactions).
- **Memory Format:** Property graphs stored in Neo4j or in-memory. Memory blocks stored as documents in LlamaIndex's storage abstractions. Facts extracted as structured tuples.
- **Compression Approach:** Property Graph Index supports hierarchical community detection similar to GraphRAG. Memory blocks handle short-term compression via summarization. FactExtractionMemoryBlock distills conversations into facts.
- **Retrieval Strategy:** Graph traversal + embedding similarity for Property Graph Index. Memory blocks inject relevant context into the agent's prompt. Text2Cypher for structured graph queries with retry/self-correction.
- **Metrics Reported:** No published memory-specific benchmarks. Focus is on RAG accuracy improvements from property graphs.
- **Open Source:** Yes. https://github.com/run-llama/llama_index
- **Source:** [Property Graph Index blog](https://www.llamaindex.ai/blog/introducing-the-property-graph-index-a-powerful-new-way-to-build-knowledge-graphs-with-llms), [Memory docs](https://docs.langchain.com/oss/python/langgraph/memory)
- **Evidence Level:** Medium (open-source, well-documented, but no memory-specific benchmarks)
- **Key Insight:** LlamaIndex's contribution is more framework than system -- it provides building blocks rather than an opinionated memory architecture. The FactExtractionMemoryBlock is essentially the same pattern as Mem0's extraction pipeline, but exposed as a composable block. The Text2Cypher with self-correction is a practical approach to making graph databases accessible to agents.

---

### 8. MemOS (MemTensor)

- **Organization:** MemTensor
- **Architecture:** Three-layer memory operating system: (a) Interface Layer for API access, (b) Operation Layer for memory CRUD and reasoning, (c) Infrastructure Layer for storage. Core abstraction is the MemCube -- a standardized memory unit that enables tracking, fusion, and migration of heterogeneous memory types. Three memory types: parametric (model weights), activation (in-context), and plaintext (external).
- **Memory Format:** MemCube: a standardized abstraction wrapping heterogeneous memory (knowledge base docs, graph structures, embeddings, model parameters). Each MemCube has metadata for tracking lineage and enabling migration.
- **Compression Approach:** Memory governance framework with fusion operations that merge multiple MemCubes. Plaintext memories are compressed via knowledge graph extraction and summarization.
- **Retrieval Strategy:** Multi-modal retrieval combining knowledge base search, graph traversal, and web search (BochaAI integration). NebulaGraph for graph storage.
- **Metrics Reported:** LoCoMo benchmark: 159% improvement in temporal reasoning over OpenAI global memory. 38.97% overall accuracy gain. 60.95% reduction in token overhead. Claims to rank first across all categories in MemoryBench, outperforming Mem0, LangMem, Zep, and OpenAI-Memory.
- **Open Source:** Yes. https://github.com/MemTensor/MemOS
- **Source:** [MemOS paper (arXiv 2505.22101)](https://arxiv.org/abs/2505.22101), [MemOS v2 paper (arXiv 2507.03724)](https://arxiv.org/pdf/2507.03724), [GitHub](https://github.com/MemTensor/MemOS)
- **Evidence Level:** Medium-High (arXiv papers + open-source + benchmark results, but relatively new and claims need independent verification)
- **Key Insight:** The MemCube abstraction treating memory as a first-class resource with metadata, lineage tracking, and migration capabilities is the most OS-like approach since MemGPT. The unification of parametric (weights), activation (context), and plaintext (external) memory under one framework is theoretically appealing but adds significant complexity. The claimed benchmark results are impressive but need independent verification.

---

### 9. A-Mem (Agentic Memory)

- **Organization:** AGI Research (academic, NeurIPS 2025)
- **Architecture:** Zettelkasten-inspired self-organizing memory. When a new memory is added, the system: (1) generates a structured note with contextual descriptions, keywords, tags, and embeddings; (2) analyzes historical memories for relevant connections; (3) establishes links where meaningful similarities exist; (4) triggers updates to existing memories when new information refines understanding. The memory network continuously evolves.
- **Memory Format:** Structured notes (Zettelkasten "zettels") with multiple attributes: content, context, keywords, tags, embeddings, and inter-note links. Stored as a linked graph of notes.
- **Compression Approach:** Dynamic reorganization -- as new memories integrate, they can trigger updates to contextual representations and attributes of existing memories. This "memory evolution" keeps the network coherent without explicit compression.
- **Retrieval Strategy:** Multi-attribute search combining keyword matching, tag filtering, embedding similarity, and graph link traversal across the note network.
- **Metrics Reported:** Doubles performance on complex multi-hop reasoning tasks vs baselines. Cost-effective despite multiple LLM calls during memory processing. Specific numbers available in the NeurIPS 2025 paper.
- **Open Source:** Yes. https://github.com/agiresearch/A-mem
- **Source:** [A-Mem paper (arXiv 2502.12110)](https://arxiv.org/abs/2502.12110), [NeurIPS 2025 poster](https://neurips.cc/virtual/2025/poster/119020)
- **Evidence Level:** High (NeurIPS 2025 acceptance + open-source + benchmark comparisons)
- **Key Insight:** The Zettelkasten metaphor is elegant -- each memory is a "note" that links to related notes, and the act of adding a new note can update existing ones. This mirrors how human knowledge management works (new learning recontextualizes old knowledge). The key innovation is that memory operations themselves are agentic -- the LLM decides how to organize, link, and update memories rather than following fixed rules.

---

### 10. OpenAI ChatGPT Memory

- **Organization:** OpenAI
- **Architecture:** Dual system: (a) "Saved Memories" -- explicit user-requested facts stored as a notepad of key-value pairs, (b) "Chat History" -- implicit insights gathered from past conversations. As of April 2025, the system references all past conversations. Memory extraction is automatic. Free users get a lightweight version for short-term cross-conversation continuity.
- **Memory Format:** Saved memories are natural language facts (similar to custom instructions). Chat history is indexed conversation data. Internal format is not publicly documented.
- **Compression Approach:** Not publicly documented. Saved memories are concise extracted facts. Chat history processing is opaque.
- **Retrieval Strategy:** Not publicly documented. The system selects relevant memories and chat history to include in context for each new conversation. Selection criteria are opaque.
- **Metrics Reported:** LoCoMo benchmark: 52.9% (used as baseline by Mem0). No official benchmarks published by OpenAI.
- **Open Source:** No. Proprietary.
- **Source:** [OpenAI memory announcement](https://openai.com/index/memory-and-new-controls-for-chatgpt/), [Memory FAQ](https://help.openai.com/en/articles/8590148-memory-faq), [Reverse engineering analysis](https://embracethered.com/blog/posts/2025/chatgpt-how-does-chat-history-memory-preferences-work/)
- **Evidence Level:** Low-Medium (product exists and is widely used, but architecture is opaque and only external benchmarks exist)
- **Key Insight:** OpenAI's approach is the simplest conceptually -- extract facts, store them, inject relevant ones into context. The April 2025 upgrade to reference all past conversations is significant but raises privacy concerns. The 52.9% LoCoMo score (used as baseline by competitors) suggests the simple approach has significant limitations for complex memory tasks. The separation of "saved memories" (explicit) from "chat history" (implicit) mirrors the declarative/procedural distinction but in a much simpler form.

---

### 11. Supermemory

- **Organization:** Supermemory AI
- **Architecture:** Memory and context infrastructure for AI agents. Combines short-term and long-term memory with a hybrid search mode. Includes AST-aware code chunking for code-heavy use cases.
- **Memory Format:** Not fully publicly documented. Uses graph-based memory evolution (not just vector storage).
- **Compression Approach:** Hybrid search mode combines multiple retrieval strategies. AST-aware code chunking improves recall for code by 28 points.
- **Retrieval Strategy:** Hybrid search combining multiple strategies. Claims to be up to 10x faster than Zep in recall speed.
- **Metrics Reported:** Claims state-of-the-art on LongMemEval and LoCoMo benchmarks. 10-15% LLM context improvement with hybrid search. 28-point recall improvement with AST-aware code chunking.
- **Open Source:** Partially. https://github.com/supermemoryai
- **Source:** [Supermemory research](https://supermemory.ai/research), [Product page](https://supermemory.ai/)
- **Evidence Level:** Low-Medium (marketing claims, limited independent verification, no academic paper)
- **Key Insight:** The AST-aware code chunking is a practical innovation for developer-facing memory systems. Code is not prose, and chunking it by syntax tree structure rather than token count preserves semantic units. Worth investigating for code-heavy agent systems.

---

## Comparison Matrix

| System | Memory Type | Format | Compression | Retrieval | Key Metric | Open Source |
|--------|-----------|--------|-------------|-----------|------------|-------------|
| **MemGPT/Letta** | Virtual context (2-tier) | NL text blocks + vector DB | Agent-driven eviction | Embedding similarity | DMR 93.4% | Yes |
| **Zep/Graphiti** | Temporal knowledge graph | Neo4j property graph | Compress at write (dedup) | Hybrid (embed+BM25+graph) | DMR 94.8%, LongMemEval +18.5% | Graphiti: Yes |
| **Mem0** | Hybrid triple-store | Graph + vector + KV | Active curation on ingest | Graph + vector + KV lookup | LoCoMo 66.9%, 91% less latency | Yes (core) |
| **GraphRAG** | Community knowledge graph | KG + community summaries | Hierarchical Leiden clustering | Map-reduce over summaries | 77% token reduction (dynamic) | Yes |
| **LangMem** | Semantic/episodic/procedural | Documents + prompts | Message summarization | Semantic search (BaseStore) | No benchmarks | Yes |
| **Cognee** | Hybrid KG + vector | Multi-backend graph + embeddings | Memify pipeline (prune/merge) | Semantic + graph traversal | No benchmarks | Yes |
| **LlamaIndex** | Property graph + memory blocks | Property graph + documents | Fact extraction + summarization | Graph + embedding + Text2Cypher | No benchmarks | Yes |
| **MemOS** | Unified (parametric+activation+plaintext) | MemCube abstraction | Fusion operations | Multi-modal (KB+graph+web) | LoCoMo +159% temporal, +38.97% overall | Yes |
| **A-Mem** | Zettelkasten notes | Linked structured notes | Dynamic reorganization | Multi-attribute + graph links | 2x multi-hop reasoning | Yes |
| **OpenAI Memory** | Fact extraction + chat history | NL facts (opaque) | Not documented | Not documented | LoCoMo 52.9% (baseline) | No |
| **Supermemory** | Hybrid (graph evolution) | Not documented | Hybrid search + AST chunking | Hybrid (10x faster than Zep claimed) | SOTA on LongMemEval (claimed) | Partial |

---

## Patterns Across Systems

### P1: Hybrid Storage is the Consensus
Every high-performing system (Zep, Mem0, MemOS) combines multiple storage backends. The pattern is: **vectors for semantic similarity + graphs for relationships + structured stores for fast facts**. No single storage paradigm is sufficient.

### P2: Compress at Write, Not at Read
The best-performing systems (Zep, Mem0) extract, deduplicate, and consolidate at ingestion time rather than trying to compress at retrieval time. This front-loads the LLM cost but dramatically reduces retrieval latency and token usage.

### P3: Temporal Awareness is a Differentiator
Systems that track when facts were learned and when they were true (bi-temporal models like Zep) outperform those that don't. Knowledge evolves -- a user's address changes, preferences shift. Without temporal indexing, contradictions accumulate.

### P4: Agent-Driven Memory Management Has Limits
MemGPT's approach of letting the agent manage its own memory is elegant but costly (many LLM calls) and unreliable (the agent might not manage well). The trend is toward more structured, system-level memory management with the agent as a consumer rather than manager.

### P5: The Three Memory Types Keep Recurring
Nearly every system distinguishes some variant of: (a) facts/knowledge (semantic), (b) experiences/episodes (episodic), (c) skills/instructions (procedural). This maps to Tulving's cognitive science taxonomy and appears to be a genuine structural requirement.

### P6: Graph Structure Enables Multi-Hop Reasoning
Systems with explicit graph structure (Zep, Mem0, A-Mem) consistently outperform flat-vector systems on multi-hop reasoning tasks. The graph enables traversal across relationships that embedding similarity alone cannot capture.

### P7: Community Detection Enables Global Queries
GraphRAG's Leiden community clustering enables answering questions that span the entire dataset -- something no single-document retrieval can do. This is a distinct capability from entity-level retrieval.

---

## Anti-Patterns

### AP1: Raw Conversation Storage
Storing complete conversation history and hoping retrieval will find the right snippets. This fails because: conversations are noisy, relevant information is buried in casual language, and token costs scale linearly with history length. Every successful system does some form of extraction/distillation.

### AP2: Pure Vector Similarity for Complex Queries
Relying solely on embedding similarity retrieval fails for temporal queries ("what did I say last Tuesday?"), relational queries ("who works with Alice?"), and negation queries ("what did I NOT want?"). Embeddings capture semantic meaning but lose structure.

### AP3: Fixed Memory Schemas
Systems with rigid memory formats struggle with diverse use cases. A-Mem's success demonstrates that letting the memory organization emerge from the data (agentic organization) outperforms fixed schemas, especially for novel domains.

### AP4: Ignoring Contradictions
Systems that simply append new memories without checking for contradictions with existing ones accumulate stale and conflicting information. Active conflict detection and resolution (Mem0, Zep) is essential for long-running agents.

### AP5: Batch-Only Indexing
Systems that require full reindexing (like early GraphRAG) cannot keep up with real-time conversational data. Incremental update capability (Graphiti, Cognee's Memify) is necessary for production agent systems.

### AP6: Over-Engineering Memory Without Validating Basics
MemoryBench's finding that "none of the advanced memory-based LLMsys can consistently outperform RAG baselines" is a sobering reality check. Complex memory architectures must demonstrate clear advantages over simple retrieval before adding complexity.

---

## Metrics & Benchmarks

### Established Benchmarks

| Benchmark | Focus | Scale | Key Finding |
|-----------|-------|-------|-------------|
| **DMR (Deep Memory Retrieval)** | Recall of specific facts from conversations | Hundreds of items | Zep (94.8%) > MemGPT (93.4%) |
| **LongMemEval** (ICLR 2025) | 5 memory abilities across extended interactions | 500 questions, 115K-1.5M tokens | 30% accuracy drop for commercial systems on sustained interactions |
| **LoCoMo** | Long-context memory with temporal reasoning | Multi-turn conversations | MemOS (+159% temporal) > Mem0 (66.9%) > OpenAI (52.9%) |
| **MemoryBench** | Memory + continual learning | Multi-domain tasks | No advanced system consistently beats naive RAG |
| **MemoryAgentBench** | Multi-turn incremental memory | Converted long-context datasets | Evaluates incremental information processing |

### Evaluation Dimensions
1. **Information Extraction** -- Can the system identify and store relevant facts?
2. **Multi-Hop Reasoning** -- Can it connect facts across different interactions?
3. **Temporal Reasoning** -- Can it handle time-dependent queries?
4. **Knowledge Updates** -- Can it handle contradictions and evolving information?
5. **Abstention** -- Can it correctly say "I don't know" when information was never provided?
6. **Token Efficiency** -- How many tokens does it consume per query?
7. **Latency** -- How fast is retrieval?
8. **Cost** -- How many LLM calls are needed for memory operations?

### Notable Metrics Gap
There is no standardized benchmark that all systems report on. DMR, LongMemEval, LoCoMo, and MemoryBench each measure different things. Cross-system comparison requires running evaluations yourself. This is a significant gap in the field.

---

## Neurosymbolic Approaches

The following systems qualify as hybrid neurosymbolic (combining embeddings with structured knowledge):

| System | Neural Component | Symbolic Component | Integration |
|--------|-----------------|-------------------|-------------|
| **Zep/Graphiti** | Entity embeddings, semantic search | Temporal knowledge graph, bi-temporal logic | Write-time: LLM extracts symbols. Read-time: graph traversal + embedding similarity |
| **Mem0** | Vector embeddings per memory | Graph DB with typed entities and relations | Parallel retrieval from graph + vector + KV, then fusion |
| **GraphRAG** | Entity/relationship extraction via LLM | Leiden community hierarchy, map-reduce reasoning | LLM extraction builds symbolic structure; retrieval uses both |
| **Cognee** | Vector embeddings (LanceDB) | Knowledge graph (multi-backend) | Dual-path retrieval combining semantic + structural |
| **A-Mem** | Note embeddings | Zettelkasten link structure, keyword/tag indices | Agent decides how to link and organize; retrieval uses all channels |
| **MemOS** | MemCube embeddings | Knowledge base + graph structure | MemCube abstraction unifies all modalities |

**Key observation:** Every high-performing system is neurosymbolic. Pure neural (vector-only) and pure symbolic (rule-only) approaches both have clear limitations. The integration point varies -- some combine at write time (Zep), some at read time (Mem0), some at both (GraphRAG).

---

## Synthesis

### Key Lessons from the State of Practice

1. **Memory is not retrieval.** The field has evolved beyond "store and retrieve" to "extract, curate, organize, and serve." The best systems (Zep, Mem0) invest heavily in write-time processing to make read-time cheap and fast.

2. **The hybrid consensus is real.** Vectors + graphs + structured storage is not over-engineering; it's the minimum viable architecture for handling the full range of memory queries (semantic, relational, temporal, exact).

3. **Temporal awareness is table stakes.** Any system without temporal indexing will fail on real-world tasks where facts change over time. This is especially critical for enterprise/business agents where information evolves.

4. **Benchmarks show the field is immature.** MemoryBench's finding that naive RAG competes with advanced systems, and LongMemEval's 30% accuracy drop for commercial systems, suggest that memory technology is still early. Marketing claims significantly outpace empirical reality.

5. **The OS metaphor has legs.** MemGPT, MemOS, and Letta all draw from operating system concepts (memory hierarchy, paging, context management). This is more than analogy -- the resource management problem is structurally similar.

6. **Cognitive science taxonomy works.** The episodic/semantic/procedural distinction from cognitive psychology maps well to agent needs. Systems that explicitly model these types (LangMem, Mem0) offer clearer developer mental models.

7. **Active curation beats passive storage.** Systems that extract, deduplicate, merge, and prune (Mem0, Zep, Cognee) outperform those that simply accumulate. Memory management IS the hard problem.

8. **Cost is a real constraint.** GraphRAG's indexing cost, MemGPT's per-operation LLM calls, and A-Mem's multi-call note generation are all significant. The 77% token reduction from GraphRAG's dynamic community selection and Mem0's 90% token cost reduction demonstrate that efficiency optimization is a first-class concern.

9. **No single winner.** Different use cases favor different systems. Conversational agents benefit from Zep's temporal model. Knowledge-heavy applications benefit from GraphRAG's community structure. Developer tools benefit from LangMem's composability. The "best" system depends on the use case.

10. **The gap between research and production is wide.** Academic systems (A-Mem, MemOS) report impressive benchmarks but lack production validation. Commercial systems (Zep, Mem0) have production usage but self-report benchmarks. Independent evaluation infrastructure is desperately needed.

---

## Relevance to RaiSE Memory System

Based on this survey, the RaiSE session memory optimization (RAISE-165) should consider:

- **Pattern P2 (compress at write):** Extract and consolidate during session close, not during retrieval. This aligns with the existing `/rai-session-close` pattern.
- **Pattern P5 (three memory types):** The existing `.raise/rai/memory/` structure should distinguish facts (semantic), session experiences (episodic), and learned patterns (procedural -- which is already done via patterns.jsonl).
- **Pattern P3 (temporal awareness):** Timestamps on memories are essential. The existing pattern IDs provide ordering but not temporal context.
- **Anti-pattern AP6:** Before adding complexity, verify that simple retrieval over existing memories is insufficient. The MemoryBench result is a cautionary tale.

---

*Research completed 2026-02-18. Sources verified against documentation and repos where possible. Evidence levels reflect author assessment of source reliability and reproducibility.*
