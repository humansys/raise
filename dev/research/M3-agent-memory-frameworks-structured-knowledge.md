# M3: Agent Memory Frameworks — Structured Knowledge Analysis

> **Date:** 2026-03-24
> **Research type:** Market landscape analysis
> **Confidence:** High (primary sources: GitHub repos, official docs, arxiv papers, funding announcements)

---

## Framework Profiles

### Mem0
- **Company/Maintainer:** Mem0 Inc. (YC S24)
- **Architecture:** Hybrid vector + graph. Core is vector-based memory extraction from conversations. Mem0g variant adds a directed labeled graph (entities as nodes, relationships as edges) on top. Supports Neo4j, Memgraph, Neptune, Kuzu as graph backends.
- **Schema Support:** **Weak.** No custom entity types, no Pydantic schema validation, no ontology support. Entity types (Person, Location, Event) are implicitly extracted by LLM. You can only influence extraction via `custom_prompt` strings — no formal schema definition.
- **Domain Pluggability:** **None.** No mechanism to add domain-specific knowledge modules or typed knowledge structures. Memories are flat text strings with LLM-inferred categories.
- **HITL Capabilities:** **None documented.** No human review, approval, or curation workflows.
- **Retrieval Method:** Hybrid — vector similarity + graph traversal (in Mem0g). BM25 keyword search available.
- **License:** Apache 2.0
- **Funding/Traction:** $24M Series A (Oct 2025, led by Basis Set Ventures). YC S24. ~50.9k GitHub stars. Strong brand recognition — the "default" memory layer.
- **Gap vs Knowledge Cartridges:** No schema validation, no domain ontologies, no typed knowledge, no HITL curation. Pure LLM-driven extraction with no structural guarantees.

---

### Zep / Graphiti
- **Company/Maintainer:** Zep AI (YC W24)
- **Architecture:** Temporal knowledge graph (Graphiti engine). Three-tier subgraph: episodic, semantic entity, community. Bi-temporal model tracking when events occurred AND when they were ingested. Built on Neo4j, FalkorDB, Kuzu, or Neptune.
- **Schema Support:** **Strong — the strongest in the market.** Custom entity and edge types defined via **Pydantic models**. Prescribed ontology (developer-defined upfront) or learned ontology (emergent from data). Extraction validates against Pydantic model, populates typed attributes. Constraints: max 10 entity types, 10 edge types, 10 fields per type.
- **Domain Pluggability:** **Moderate.** You can define domain-specific entity types (e.g., `AirTravelPreferences(EntityModel)`) with typed fields. Ontology can be set project-wide or per-user/per-graph. However, limited to 10+10 types — not designed for rich domain ontologies.
- **HITL Capabilities:** **None documented.** No human review or curation workflows.
- **Retrieval Method:** Hybrid — semantic embeddings + BM25 keyword + direct graph traversal. No LLM calls during retrieval. P95 latency ~300ms.
- **License:** Open-source (Graphiti), commercial cloud (Zep Cloud)
- **Funding/Traction:** $500K seed (2024). $1M revenue by mid-2024 with 5 employees. ~24.2k GitHub stars for Graphiti. Published arxiv paper. Strong technical credibility.
- **Gap vs Knowledge Cartridges:** Closest competitor for structured knowledge. Has Pydantic schemas and typed entities. But: limited to 10 types, no OWL/RDF ontology support, no HITL curation, no domain module composition, no schema versioning.

---

### Letta (formerly MemGPT)
- **Company/Maintainer:** Letta Inc. (UC Berkeley spinout)
- **Architecture:** LLM-as-Operating-System paradigm. Agents manage their own context window with structured "memory blocks" — named string sections (persona, human, custom labels) that agents read/write via tools (memory_replace, memory_insert, memory_rethink). Archival storage for overflow. All state persisted to database.
- **Schema Support:** **Minimal.** Memory blocks are label+string pairs. No Pydantic validation, no typed fields, no schema enforcement. Agents edit free-text blocks. Pydantic is used for tool definitions, not memory structure.
- **Domain Pluggability:** **Limited.** Custom block labels possible but blocks are just strings. No mechanism for domain-specific knowledge types or modules.
- **HITL Capabilities:** **None documented.** Memory is agent-managed; no human review gates.
- **Retrieval Method:** In-context (always visible blocks) + archival search (vector similarity for overflow storage).
- **License:** Apache 2.0
- **Funding/Traction:** $10M seed at $70M valuation (Sep 2024, led by Felicis). $1.4M revenue by mid-2025. ~21.7k GitHub stars. Strong research pedigree (MemGPT paper).
- **Gap vs Knowledge Cartridges:** Elegant OS metaphor but no structured knowledge. Memory blocks are untyped strings. No schema, no validation, no domain ontologies, no HITL.

---

### Cognee
- **Company/Maintainer:** Cognee (Berlin, Germany)
- **Architecture:** Knowledge graph + vector hybrid with cognitive science inspiration. Pipeline: classify → permissions → chunk → LLM entity/relationship extraction → summarize → embed + graph commit. "Memify" step prunes/strengthens graph over time. Two-layer: session memory (short-term) + permanent memory (long-term graph).
- **Schema Support:** **Strong.** Uses **Pydantic `DataPoint` models** as the fundamental unit. Custom entity types with typed fields, `index_fields` metadata. **Full OWL/RDF ontology support** via RDFLib — supports RDF/XML, Turtle, N-Triples, JSON-LD. Schema validation with `ontology_valid` flag on each node. Fuzzy matching at configurable threshold (default 0.80).
- **Domain Pluggability:** **The strongest in the market.** Pluggable `BaseOntologyResolver` interface. Bring your own OWL ontology file. Supports domain vocabularies (SNOMED CT for healthcare, FIBO for finance, schema.org, MeSH, GeoSPARQL). Ontology enrichment adds inherited relationships automatically (e.g., ElectricCar subclass of Car).
- **HITL Capabilities:** **Indirect.** Documentation emphasizes "manually curated, focused ontologies" and iterative expansion. No built-in approval workflows, but design encourages human curation of ontology files before deployment.
- **Retrieval Method:** Hybrid — vector similarity + graph traversal + time filters. Triplet-based (subject-predicate-object) retrieval. Multiple graph backends (Kuzu, Neo4j, FalkorDB, Neptune, Memgraph).
- **License:** Apache 2.0
- **Funding/Traction:** €7.5M seed (Feb 2026, led by Pebblebed). ~14.6k GitHub stars. 70+ companies in production (including Bayer). 1M+ pipelines/month.
- **Gap vs Knowledge Cartridges:** Closest to the Knowledge Cartridge vision. Has Pydantic models, OWL ontologies, domain pluggability. Missing: HITL curation workflows, schema versioning, module composition (can't compose multiple ontology modules cleanly), no "cartridge" packaging concept.

---

### LangMem (LangChain)
- **Company/Maintainer:** LangChain Inc.
- **Architecture:** SDK for long-term memory in LangGraph agents. Three memory types: semantic (facts/profiles), episodic (past experiences as few-shot examples), procedural (prompt instructions that evolve). Background memory manager for async extraction/consolidation.
- **Schema Support:** **Moderate.** Supports **Pydantic BaseModel** for structured memory types. Define schemas like `UserProfile`, `PreferenceMemory`, `Fact` with typed fields. Uses `trustcall` for type-safe memory consolidation. Profiles update in-place; collections grow unbounded.
- **Domain Pluggability:** **Moderate.** Custom Pydantic schemas per domain. Flexible namespace structures for segmentation (per-user, per-team, per-app). Custom extraction instructions. But no ontology support, no relationship modeling, no graph structure.
- **HITL Capabilities:** **Partial.** Profiles are "easy to present to a user for manual editing." Feedback integration via `user_score` in trajectory evaluation. No formal approval workflows.
- **Retrieval Method:** Direct access + semantic search + metadata filtering via LangGraph's BaseStore.
- **License:** MIT (LangMem SDK)
- **Funding/Traction:** Part of LangChain ecosystem ($235M+ total funding). Not separately funded. GitHub stars for langmem repo moderate.
- **Gap vs Knowledge Cartridges:** Has Pydantic schemas and basic HITL (editable profiles). But flat memory — no knowledge graph, no relationships, no ontology, no domain module composition. Memory is document-like, not graph-like.

---

### TrustGraph
- **Company/Maintainer:** TrustGraph AI
- **Architecture:** "Context development platform" — graph-native infrastructure with OWL ontology-driven extraction. Multi-component: Cassandra (storage), Qdrant (vectors), Pulsar (messaging). Portable "Context Cores" bundle ontology + graph + embeddings + policies into versioned, deployable artifacts.
- **Schema Support:** **Very strong.** OWL ontologies define the semantic vocabulary. Every entity has a typed class, every relationship has a typed property. Ontology-based extraction processor guides LLM extraction to match domain constraints. Reified agent behavior (interactions, reasoning chains) also typed per ontological schema.
- **Domain Pluggability:** **Strong.** Custom OWL ontologies define domain vocabulary. Context Cores are portable, versioned knowledge bundles that can be shipped between projects. "Treat context like code: build, test, version, promote, roll back."
- **HITL Capabilities:** **Limited.** Workbench provides runtime adjustment of prompts and parameters. No formal curation/approval workflows.
- **Retrieval Method:** Semantic retrieval reasoning over structured knowledge — understands entities, relationships, and intent. Not just vector similarity.
- **License:** Apache 2.0
- **Funding/Traction:** ~1.5k GitHub stars. Early stage. No disclosed funding. Technically sophisticated but low adoption.
- **Gap vs Knowledge Cartridges:** Very aligned philosophically — ontology-first, versioned context bundles. Missing: Pydantic integration (uses OWL directly), HITL curation workflows, broader ecosystem integration. Low traction risk.

---

### WhyHow AI (Knowledge Graph Studio)
- **Company/Maintainer:** WhyHow AI
- **Architecture:** API-first knowledge graph platform on MongoDB. Triple-based (head-relation-tail) with typed nodes (name, label, properties). Rule-based entity resolution. SDK in Python (FastAPI backend).
- **Schema Support:** **Moderate.** Schema collection for defining node labels, properties, and relations. Supports "highly schema-constrained graphs." But not Pydantic-native — schema is MongoDB document-based.
- **Domain Pluggability:** **Moderate.** Schema definitions allow domain-specific node/relation types. Original SDK supported small ontologies for extraction guidance (now deprecated in favor of Studio).
- **HITL Capabilities:** **None documented.**
- **Retrieval Method:** Graph queries over triples.
- **License:** MIT
- **Funding/Traction:** ~899 GitHub stars. Low activity (38 commits). Appears to be winding down or pivoting.
- **Gap vs Knowledge Cartridges:** Interesting schema-constrained graph approach but low traction, uncertain future. No HITL, no ontology support, no versioning.

---

### ReMe (formerly MemoryScope, Alibaba/ModelScope)
- **Company/Maintainer:** Alibaba / ModelScope / AgentScope
- **Architecture:** File-based + vector memory. Memories stored as editable Markdown files. Hybrid retrieval (70% vector, 30% BM25). Part of CoPaw agent workstation. Layers: long-term (MEMORY.md), session (daily journals), raw dialogue (JSONL), tool result cache.
- **Schema Support:** **Minimal.** Markdown-based schema with predefined sections (Goal, Constraints, Progress, Key Decisions, Next Steps). No Pydantic, no typed entities, no formal ontology.
- **Domain Pluggability:** **None.** Fixed section structure. No mechanism for domain-specific knowledge types.
- **HITL Capabilities:** **Best in class for simplicity.** "Memory as files, files as memory" — memories are plain Markdown files humans can directly read and edit. Design explicitly contrasts with opaque databases. Not a workflow, but transparency-first.
- **Retrieval Method:** Hybrid vector + BM25 keyword search.
- **License:** Apache 2.0
- **Funding/Traction:** ~2.4k GitHub stars. Backed by Alibaba ecosystem. Part of AgentScope/CoPaw.
- **Gap vs Knowledge Cartridges:** Interesting HITL philosophy (files as memory) but no structured knowledge, no schema, no graph, no ontology.

---

### Graphlit
- **Company/Maintainer:** Graphlit Inc.
- **Architecture:** "Context layer for AI agents." Cloud platform for real-time data sync across Slack, GitHub, Jira, etc. Knowledge graph with entity extraction, entity linking, temporal awareness. Five layers: ingestion → knowledge graph → time-aware memory → semantic retrieval → context assembly.
- **Schema Support:** **Unknown.** Marketing describes "knowledge fabric" with entities, relationships, and temporal context, but no documentation on custom schemas or ontologies found.
- **Domain Pluggability:** **Unknown.** Platform-level data integration rather than domain ontology.
- **HITL Capabilities:** **Unknown.** No documentation found.
- **Retrieval Method:** Semantic retrieval over structured knowledge — entity-aware, relationship-aware, intent-aware.
- **License:** Proprietary cloud platform (some MIT GitHub repos for SDKs).
- **Funding/Traction:** No disclosed funding. Active marketing and content production. Unclear adoption.
- **Gap vs Knowledge Cartridges:** Unclear differentiation due to limited technical documentation. Appears more like an integration platform than a knowledge architecture.

---

### PlugMem (Microsoft Research)
- **Company/Maintainer:** Microsoft Research
- **Architecture:** Research prototype. Transforms raw agent interactions into **propositional knowledge** (facts) and **prescriptive knowledge** (reusable skills). Organizes into a structured memory graph. Task-agnostic plug-and-play module.
- **Schema Support:** **Structured but not schema-defined.** Knowledge units are typed (facts vs skills) but there's no developer-defined schema or Pydantic models. Structure is LLM-derived.
- **Domain Pluggability:** **By design — task-agnostic.** Single memory module works across benchmarks without task-specific modification. But no mechanism for explicit domain knowledge injection.
- **HITL Capabilities:** **None documented.**
- **Retrieval Method:** Intent-based routing — high-level concepts and inferred intents surface relevant knowledge units.
- **License:** Research paper (March 2026). No production release.
- **Funding/Traction:** Microsoft Research backing. Academic paper, not a product.
- **Gap vs Knowledge Cartridges:** Interesting factual decomposition approach but research-only. No schema, no ontology, no HITL, no production path.

---

## Capability Matrix

| Framework | Architecture | Pydantic Schema | OWL/RDF Ontology | Domain Pluggable | HITL Curation | Typed Entities | Retrieval | License | GitHub Stars | Funding |
|-----------|-------------|----------------|-----------------|-----------------|---------------|---------------|-----------|---------|-------------|---------|
| **Mem0** | Vector+Graph | No | No | No | No | Implicit (LLM) | Vector+Graph | Apache 2.0 | 50.9k | $24M Series A |
| **Zep/Graphiti** | Temporal KG | **Yes** | No | Moderate (10 types) | No | **Yes (Pydantic)** | Hybrid (no LLM) | OSS+Cloud | 24.2k | $500K seed |
| **Letta** | OS paradigm | No | No | No | No | No (strings) | In-context+Archive | Apache 2.0 | 21.7k | $10M seed |
| **Cognee** | KG+Vector | **Yes (DataPoint)** | **Yes (OWL/RDF)** | **Strong** | Indirect | **Yes** | Hybrid+Triplets | Apache 2.0 | 14.6k | €7.5M seed |
| **LangMem** | Flat store | **Yes** | No | Moderate | Partial (edit) | Partial | Semantic+Filter | MIT | Low | LangChain ecosystem |
| **TrustGraph** | Ontology KG | No (OWL native) | **Yes (OWL)** | **Strong** | Limited | **Yes** | Semantic+Graph | Apache 2.0 | 1.5k | Undisclosed |
| **WhyHow** | Triple store | No (MongoDB) | No | Moderate | No | Partial | Graph queries | MIT | 899 | Undisclosed |
| **ReMe** | File+Vector | No | No | No | **Yes (files)** | No | Hybrid V+BM25 | Apache 2.0 | 2.4k | Alibaba |
| **Graphlit** | Cloud KG | Unknown | Unknown | Unknown | Unknown | Unknown | Semantic | Proprietary | N/A | Undisclosed |
| **PlugMem** | Memory graph | No | No | Task-agnostic | No | Typed (fact/skill) | Intent routing | Research | N/A | Microsoft Research |

---

## Key Findings

### 1. The Whitespace Is Real

**No framework combines all four capabilities:**
1. Schema-validated knowledge (Pydantic/typed)
2. Pluggable domain ontologies (bring your own domain model)
3. HITL curation (human review/approval of knowledge)
4. Composable knowledge modules (multiple domains, versioned)

### 2. Who Comes Closest?

**Cognee** is the clear leader in structured knowledge:
- Pydantic DataPoint models for entity definition
- Full OWL/RDF ontology support with pluggable resolvers
- Schema validation with `ontology_valid` flags
- 70+ production deployments, real traction

**Zep/Graphiti** is second:
- Pydantic entity/edge types (prescribed ontology)
- Temporal awareness is a unique strength
- But limited to 10 types, no OWL support

**TrustGraph** is philosophically aligned:
- OWL ontology-first architecture
- Versioned Context Cores (portable knowledge bundles)
- But very low traction, no Pydantic integration

### 3. Universal Gaps (Whitespace for Knowledge Cartridges)

| Capability | Market Status |
|-----------|--------------|
| **Schema-validated knowledge** | Cognee and Graphiti have it. Others don't. |
| **Pluggable domain ontologies** | Cognee supports OWL. TrustGraph supports OWL. Nobody else. |
| **HITL curation workflows** | Nobody has formal approval/review workflows. ReMe has file-based transparency. LangMem has editable profiles. |
| **Composable knowledge modules** | Nobody. No framework supports composing multiple domain knowledge modules. |
| **Schema versioning** | Nobody. No framework versions knowledge schemas. |
| **Domain module packaging** | TrustGraph's Context Cores come closest (versioned bundles). Nobody else. |
| **Validation at boundaries** | Cognee's `ontology_valid` flag is the only schema validation. |

### 4. Market Dynamics

- **Mem0** has the brand and funding but is architecturally simple — pure LLM extraction, no structure
- **Zep/Graphiti** has the best temporal model and strong technical credibility but is a tiny team
- **Letta** has the best research pedigree but memory blocks are just strings
- **Cognee** is the dark horse — richest knowledge architecture, growing fast, but less well-known
- **LangMem** benefits from LangChain distribution but is shallow architecturally
- **The market is converging on "memory = vector store + maybe graph"** — almost nobody is doing schema-first knowledge

### 5. Implication for Knowledge Cartridges

The Knowledge Cartridge concept (domain-specific, schema-validated, HITL-curated, composable knowledge modules) sits in clear whitespace. The closest competitors (Cognee, Graphiti) address parts of it but none combine:

- **Pydantic-first schema definition** (Cognee and Graphiti have this)
- **Domain ontology pluggability** (Cognee has OWL, but not Pydantic-native composition)
- **HITL curation workflows** (nobody has this)
- **Module composition** (nobody has this)
- **Schema versioning** (nobody has this)
- **Retrieval shaped by schema** (schema-mediated retrieval — see R4 research)

The gap is not in "better vector search" or "better graph" — it's in **governance of knowledge**: who decides what the agent knows, how knowledge is validated, how domain expertise is packaged and composed.

---

## Sources

- [Mem0 GitHub](https://github.com/mem0ai/mem0) | [Mem0 Series A](https://mem0.ai/series-a) | [Mem0 Paper](https://arxiv.org/abs/2504.19413)
- [Graphiti GitHub](https://github.com/getzep/graphiti) | [Zep Paper](https://arxiv.org/abs/2501.13956) | [Graphiti Custom Types](https://help.getzep.com/graphiti/core-concepts/custom-entity-and-edge-types)
- [Letta GitHub](https://github.com/letta-ai/letta) | [Letta Docs](https://docs.letta.com/concepts/memgpt/)
- [Cognee GitHub](https://github.com/topoteretes/cognee) | [Cognee Ontology Blog](https://www.cognee.ai/blog/deep-dives/grounding-ai-memory) | [Cognee Architecture](https://www.cognee.ai/blog/fundamentals/how-cognee-builds-ai-memory) | [Cognee Funding](https://www.eu-startups.com/2026/02/german-ai-infrastructure-startup-cognee-lands-e7-5-million-to-scale-enterprise-grade-memory-technology/)
- [LangMem GitHub](https://github.com/langchain-ai/langmem) | [LangMem Concepts](https://langchain-ai.github.io/langmem/concepts/conceptual_guide/)
- [TrustGraph GitHub](https://github.com/trustgraph-ai/trustgraph) | [TrustGraph Ontologies](https://trustgraph.ai/guides/key-concepts/ontologies-and-context-graphs/)
- [WhyHow Knowledge Graph Studio](https://github.com/whyhow-ai/knowledge-graph-studio)
- [ReMe GitHub](https://github.com/modelscope/ReMe)
- [Graphlit](https://www.graphlit.com/) | [Graphlit Survey](https://www.graphlit.com/blog/survey-of-ai-agent-memory-frameworks)
- [PlugMem (Microsoft Research)](https://www.microsoft.com/en-us/research/blog/from-raw-interaction-to-reusable-knowledge-rethinking-memory-for-ai-agents/)
- [Neo4j Graphiti Blog](https://neo4j.com/blog/developer/graphiti-knowledge-graph-memory/)
- [Vectorize Framework Comparison](https://vectorize.io/articles/best-ai-agent-memory-systems)
