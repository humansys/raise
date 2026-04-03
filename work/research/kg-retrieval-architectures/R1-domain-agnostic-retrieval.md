# R1: Domain-Agnostic Knowledge Graph Retrieval Architectures

> Research date: 2026-03-20
> Status: Complete
> Methodology: Web search + targeted page fetches, triangulated across academic, industry, and open-source sources

---

## Evidence Catalog

### E1: Ontology-Based Data Access (OBDA) / Virtual Knowledge Graph Pattern

**Claim:** The OBDA/VKG pattern uses a three-layer architecture (data sources → mappings → ontology) where a domain ontology provides a "universal vocabulary" and user queries against the ontology are rewritten into queries against underlying data sources. The ontology acts as a semantic mediator — users never see the storage layer.

**Sources:**
- [Ontopic: What is a Virtual Knowledge Graph](https://ontopic.ai/en/tech-notes/what-is-a-virtual-knowledge-graph/)
- [MIT Press: Virtual Knowledge Graphs — An Overview of Systems and Use Cases](https://direct.mit.edu/dint/article/1/3/201/9978/Virtual-Knowledge-Graphs-An-Overview-of-Systems)
- [ScienceDirect: Ontology-based data federation and query optimization](https://www.sciencedirect.com/science/article/pii/S0950705125012572)

**Confidence:** Very High — well-established pattern with 10+ years of research (Ontop system), multiple production deployments, peer-reviewed.

**Relevance:** High. The core insight — ontology as semantic mediator between query interface and storage — maps directly to our need. However, the full OBDA stack (R2RML mappings, SPARQL rewriting to SQL) is over-engineered for our scale. The *pattern* is right; the *implementation* should be lighter.

---

### E2: Schema-Driven Extraction with Ontology as Domain Registry (TrustGraph, LlamaIndex)

**Claim:** TrustGraph uses OWL ontology definitions as a "domain registry" that constrains extraction — only entities matching ontology types are extracted, relationships must use ontology-defined properties, and invalid structures are rejected. LlamaIndex PropertyGraphIndex uses `SchemaLLMPathExtractor` with Pydantic-defined entity types and relation types to guide extraction and retrieval.

**Sources:**
- [TrustGraph: Ontology RAG](https://trustgraph.ai/guides/key-concepts/ontology-rag/)
- [LlamaIndex: PropertyGraphIndex Guide](https://www.llamaindex.ai/blog/introducing-the-property-graph-index-a-powerful-new-way-to-build-knowledge-graphs-with-llms)
- [Neo4j: Customizing Property Graph Index in LlamaIndex](https://neo4j.com/blog/developer/property-graph-index-llamaindex/)

**Confidence:** High — both are production systems with published documentation and source code.

**Relevance:** Very High. LlamaIndex's approach of using Pydantic models to define domain schemas that guide both extraction and retrieval is almost exactly what we're building. The `SchemaLLMPathExtractor` pattern — where the schema is data, not code — is directly applicable.

---

### E3: Microsoft GraphRAG — Knowledge Model + Factory Pattern for Pluggability

**Claim:** GraphRAG uses a "Knowledge Model" abstraction as "an abstraction over the underlying data storage technology, providing a common interface for the GraphRAG system to interact with." Domain-agnostic indexing workflows support domain-specific customizations through pluggable implementations. Seven subsystems use factory patterns for registration: language models, input readers, cache, logging, storage, vector stores, and pipelines/workflows.

**Sources:**
- [GraphRAG Architecture](https://microsoft.github.io/graphrag/index/architecture/)
- [GraphRAG GitHub](https://github.com/microsoft/graphrag)
- [DeepWiki: GraphRAG System Architecture](https://deepwiki.com/microsoft/graphrag/1.2-system-architecture)

**Confidence:** Very High — open source, well-documented, from Microsoft Research.

**Relevance:** Medium. GraphRAG solves a different problem (unstructured text → community-based retrieval with LLM calls), but its architectural patterns are instructive: Knowledge Model as storage abstraction, factory-based registration, and workflow-as-pipeline are applicable. The community detection / hierarchical Leiden algorithm is NOT relevant to our symbolic retrieval constraint.

---

### E4: Cognee — Graph Database Adapter Pattern with Abstract Interface

**Claim:** Cognee implements a `GraphDBInterface` ABC (abstract base class) with a plugin registry (`supported_databases` dict + `use_graph_adapter()` function). Adapters must subclass `GraphDBInterface` implementing all CRUD and utility methods. Core adapters (Kuzu) are in the main repo; community adapters (NetworkX, FalkorDB, Neo4j, etc.) live in a separate `cognee-community` repository.

**Sources:**
- [Cognee GitHub: GraphDBInterface](https://github.com/topoteretes/cognee)
- [Cognee: Graph Database Integration Guide](https://docs.cognee.ai/contributing/adding-providers/graph-db/graph-database-integration)
- [ArcadeDB adapter issue showing the pattern](https://github.com/topoteretes/cognee/issues/2239)

**Confidence:** High — open source, can verify in code.

**Relevance:** Medium. This is about *storage* adapter pluggability (different backends behind same interface), not *domain* pluggability. But the registration pattern (dict registry + factory function) is a proven lightweight approach.

---

### E5: Wikidata — Unified Item Model for Domain Coexistence

**Claim:** Wikidata uses a single, domain-agnostic data model where all knowledge is represented as Items (Q-ids) with Statements composed of Property-Value pairs and Qualifiers. Domains coexist not through separate schemas but through a flat, universal model where domain specificity emerges from the properties used. Property constraints (subject type, allowed values) are advisory, not enforced — enabling maximum flexibility but requiring community governance.

**Sources:**
- [Wikidata Data Model](https://www.wikidata.org/wiki/Wikidata:Data_model)
- [Wikidata Help: Properties](https://www.wikidata.org/wiki/Help:Properties)
- [Wikidata Help: Statements](https://www.wikidata.org/wiki/Help:Statements)

**Confidence:** Very High — directly observable in Wikidata's public infrastructure.

**Relevance:** High. Wikidata proves that a single property-graph model CAN host multiple domains without separate schemas. The key insight: domain semantics are encoded in *which properties are used*, not in *separate type hierarchies*. For our scale, this suggests that a unified node model with domain-specific metadata fields may be simpler than separate Pydantic classes per domain.

---

### E6: Apache Jena — Federated SPARQL with Ontology Mapping

**Claim:** Apache Jena's ARQ engine supports SPARQL 1.1 federated queries via the SERVICE keyword, allowing queries to span multiple SPARQL endpoints. Academic work (Makris et al., 2010) demonstrates ontology mapping + SPARQL rewriting where formal mappings between overlapping ontologies enable query translation across federated RDF sources through an ontology-based mediator.

**Sources:**
- [Apache Jena: ARQ Federated Query](https://jena.apache.org/documentation/query/service.html)
- [Springer: Ontology Mapping and SPARQL Rewriting for Querying Federated RDF Data Sources](https://link.springer.com/chapter/10.1007/978-3-642-16949-6_32)
- [ACM: Ontology Mapping and SPARQL Rewriting](https://dl.acm.org/doi/10.5555/1926129.1926173)

**Confidence:** High — peer-reviewed academic work + production Apache project.

**Relevance:** Low-Medium. The federation pattern (SERVICE keyword routing to different endpoints) is overkill for our single-process, hundreds-of-nodes scenario. But the ontology mapping concept — formal rules that translate between domain vocabularies — is useful if we ever need to query across domains with different terminology.

---

### E7: Over-Abstraction and Semantic Loss in Multi-Domain KGs

**Claim:** Over-abstraction in knowledge graph construction leads to loss of "secondary information" when prioritizing structural clarity. Query languages face "differing semantic spaces during conversion" leading to "semantic loss or fidelity risks." The core tension: abstraction gains interoperability but loses domain-specific nuances essential for accurate reasoning.

**Sources:**
- [Frontiers: Practices, opportunities and challenges in the fusion of knowledge graphs](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2025.1590632/full)
- [ACM: Knowledge Graphs comprehensive survey](https://dl.acm.org/doi/fullHtml/10.1145/3447772)
- [ArXiv: Neural-Symbolic Reasoning over Knowledge Graphs](https://arxiv.org/html/2412.10390v1)

**Confidence:** High — multiple independent academic sources identify the same failure mode.

**Relevance:** Very High. This is the central risk of our design. If we abstract too aggressively (e.g., all nodes become generic `KGNode` with `metadata: dict`), we lose the ability to write domain-specific queries that leverage typed fields. If we don't abstract enough (separate query engines per domain), we duplicate logic.

---

### E8: LlamaIndex Multi-Retriever Composition Pattern

**Claim:** LlamaIndex PropertyGraphIndex supports composing multiple retrievers (`LLMSynonymRetriever`, `VectorContextRetriever`, `TextToCypherRetriever`, `CypherTemplateRetriever`) through a `PGRetriever` abstraction. Retrievers execute in parallel with results aggregated before synthesis. Each retriever implements one strategy; composition happens at the orchestration layer.

**Sources:**
- [LlamaIndex: PropertyGraphIndex Guide](https://developers.llamaindex.ai/python/framework/module_guides/indexing/lpg_index_guide/)
- [LlamaIndex: Property Graph Index Customization](https://www.llamaindex.ai/blog/customizing-property-graph-index-in-llamaindex)

**Confidence:** Very High — documented API, open source code.

**Relevance:** Very High. This is the "Strategy pattern for retrieval" we need. Each domain can contribute retrieval strategies (specialized traversals, domain-aware scoring) that are composed at the query layer. The domain doesn't own the query engine; it contributes strategies to a shared engine.

---

## Architectural Patterns

### Pattern 1: Schema-Mediated Query (OBDA-lite)

**Description:** A shared ontology/schema sits between the query interface and the graph storage. Queries are expressed against the schema vocabulary. The system translates schema-level queries into graph traversals using mappings.

**How it works:**
1. Each domain registers a schema (entity types, relationship types, attribute names)
2. Query interface accepts schema-level terms ("find all principles related to this practice")
3. Mappings translate schema terms to concrete graph structures
4. Results are returned in schema-level vocabulary

**Pros:**
- Clean separation of concerns
- Domain experts can define schemas in their language
- Query interface stays domain-agnostic

**Cons:**
- Mapping maintenance overhead
- Can lose domain richness if schema is too abstract
- Requires upfront schema design

**When to use:** When domains have fundamentally different vocabularies but need a shared query interface. Good for 3+ domains.

**Real systems:** Ontop VKG, Apache Jena with ontology mapping.

---

### Pattern 2: Domain-Contributed Retrieval Strategies (Strategy Composition)

**Description:** The retrieval engine defines a `RetrievalStrategy` interface. Each domain contributes one or more strategy implementations that know how to find relevant nodes given domain-specific semantics. The engine composes strategies at query time.

**How it works:**
1. Core engine defines `Protocol: retrieve(query_context) -> list[ScoredNode]`
2. Each domain registers strategies: "keyword match on content", "traverse edge type X", "score by recency"
3. Query dispatches to all relevant strategies, merges results
4. Domain-specific scoring/filtering happens inside the strategy

**Pros:**
- Domains retain full semantic richness
- New domains add strategies without changing core
- Composition is flexible (AND/OR/weighted merge)
- No mapping layer to maintain

**Cons:**
- Strategies can duplicate logic (every domain does "keyword search")
- Harder to optimize globally
- Result merging requires normalization

**When to use:** When domains have specialized traversal patterns and the common query operations are few. Best for our scale.

**Real systems:** LlamaIndex PGRetriever, GraphRAG query modes (local/global/drift).

---

### Pattern 3: Unified Model with Domain Metadata (Wikidata Pattern)

**Description:** All nodes share a single base model. Domain specificity is encoded in metadata fields and property types, not in separate schemas. Queries operate on the universal model, with domain-specific filters as parameters.

**How it works:**
1. Single `KGNode` model with: id, type, content, metadata: dict
2. Domain information lives in `node.type` and `node.metadata` keys
3. Queries filter by type and metadata keys
4. No separate schema per domain — convention over configuration

**Pros:**
- Simplest implementation
- No registration ceremony
- Easy to query across domains
- Works naturally with NetworkX property graph

**Cons:**
- No compile-time validation of domain attributes
- Easy to introduce inconsistencies
- Domain-specific queries require knowing metadata key names
- Loses Pydantic validation benefits

**When to use:** When domains are few, nodes are simple, and cross-domain queries are common. Wikidata scale (millions of editors) requires this; our scale may not.

**Real systems:** Wikidata, schema.org knowledge graphs.

---

### Pattern 4: Domain Registry with Schema-Typed Nodes (Configuration-Driven)

**Description:** Domains are registered via configuration files (YAML/TOML) that declare their schema (Pydantic model), node types, edge types, and retrieval hints. The core engine uses this registry to validate nodes, dispatch queries, and compose results.

**How it works:**
1. Each domain has a `domain.yaml` declaring: name, schema reference, node types, edge types, retrieval strategies
2. At startup, the registry loads all domain configs and imports schema models
3. Query interface accepts domain-agnostic queries; the registry routes to appropriate domain handlers
4. Validation uses the registered Pydantic model; retrieval uses the declared strategy

**Pros:**
- Type safety preserved (Pydantic models per domain)
- New domains added by config, not code changes to core
- Explicit contract between domain and engine
- Testable: each domain's config can be validated independently

**Cons:**
- Configuration can become complex
- Dynamic import of schema models adds a failure mode
- Must balance config expressiveness vs simplicity

**When to use:** When you want the benefits of typed schemas but the extensibility of plugin registration. Best for our exact constraints.

**Real systems:** This is what we're already building in `domain.py` + `DomainManifest`. TrustGraph's ontology loading is similar.

---

## Real System Analysis

### System 1: Microsoft GraphRAG

**How it solves domain pluggability:** Knowledge Model abstraction + factory pattern. The Knowledge Model provides storage-agnostic interfaces. Factories registered by string name allow swapping implementations for 7 subsystems. Domain-specific behavior is injected via workflow customization, not schema registration.

**Key takeaway:** Factory pattern for subsystem pluggability is lightweight and proven. But GraphRAG's approach is LLM-heavy (community summaries, entity extraction via LLM) — not applicable to our symbolic-only constraint.

### System 2: LlamaIndex PropertyGraphIndex

**How it solves domain pluggability:** Schema definition via Pydantic + composable retrievers. `SchemaLLMPathExtractor` takes entity types and relation types as lists. Retrieval strategies are independent objects composed by `PGRetriever`. Domain knowledge is encoded in the schema definition and extraction configuration, not in the retrieval engine.

**Key takeaway:** The separation "domain defines what to extract (schema) + engine defines how to query (retrievers)" is exactly the right split. The strategy composition pattern (multiple retrievers running in parallel, results merged) is the cleanest approach for our needs.

### System 3: Wikidata

**How it solves domain pluggability:** No domain boundaries at all. Every piece of knowledge is an Item with Statements. Domain specificity emerges from property usage patterns. The query language (SPARQL) is fully domain-agnostic; domain expertise is in knowing which properties to query.

**Key takeaway:** At small scale, the "no domain boundaries" approach is tempting but loses type safety. The real lesson is: domain semantics should be in the *data* (properties, types), not in the *query engine*.

### System 4: Ontop (OBDA/VKG)

**How it solves domain pluggability:** Ontology as semantic layer + R2RML mappings + SPARQL-to-SQL rewriting. Users query the ontology; the system rewrites queries into SQL against underlying databases. Multiple data sources can have different schemas; the ontology provides the unified view.

**Key takeaway:** The mediator pattern (query against abstract vocabulary, translate to concrete storage) is sound but the full OBDA machinery is overkill for NetworkX at hundreds of nodes.

---

## Recommended Pattern for Our Constraints

**Recommendation: Pattern 4 (Domain Registry) + Pattern 2 (Strategy Composition)**

Given our constraints (small-scale, symbolic, Pydantic+NetworkX, <100ms latency, no LLM in retrieval path):

### Architecture

```
┌─────────────────────────────────────────────┐
│              Query Interface                 │
│  query(context: str, domain: str | None,     │
│         strategy: str = "auto")              │
├─────────────────────────────────────────────┤
│           Strategy Compositor                │
│  Dispatches to registered strategies,        │
│  merges + deduplicates results               │
├─────────────────────────────────────────────┤
│         Domain Registry                      │
│  loads domain.yaml → DomainManifest          │
│  imports Pydantic schema models              │
│  registers retrieval strategies per domain   │
├──────────┬──────────┬───────────────────────┤
│ Domain A │ Domain B │ Domain C              │
│ schema   │ schema   │ schema                │
│ nodes    │ nodes    │ nodes                 │
│ strats   │ strats   │ strats                │
├──────────┴──────────┴───────────────────────┤
│         NetworkX MultiDiGraph               │
│  (shared graph, nodes carry domain tag)      │
└─────────────────────────────────────────────┘
```

### Key Design Decisions

1. **Single graph, multiple domains.** All nodes live in one NetworkX MultiDiGraph. Each node carries a `domain: str` attribute. Cross-domain edges are allowed.

2. **Domain registry via YAML** (already implemented in `domain.py`). Extend `DomainManifest` to declare retrieval strategies and edge types.

3. **Typed nodes via Pydantic** (already implemented). Each domain's schema model provides compile-time validation + runtime serialization. The base model defines the fields the retrieval engine needs (id, type, content, domain); domain models add specific fields.

4. **Retrieval strategies as Protocol implementations:**
   ```python
   class RetrievalStrategy(Protocol):
       def retrieve(self, graph: nx.MultiDiGraph, context: QueryContext) -> list[ScoredNode]: ...
   ```
   Built-in strategies: keyword_search, type_filter, bfs_neighbors, subgraph_by_edge_type.
   Domains can register additional strategies.

5. **Strategy composition at query time.** The compositor runs all applicable strategies, normalizes scores, deduplicates, and returns top-k.

### Why This Fits

- **Small scale:** No need for query federation, SPARQL rewriting, or distributed engines. NetworkX traversal is O(neighbors) and will be <1ms at our scale.
- **Symbolic only:** Strategies are graph traversals and text matching. No embeddings, no LLM calls.
- **Pydantic native:** Domain schemas are already Pydantic models. The registry already does dynamic import. Just extend to cover retrieval hints.
- **Extensible:** New domain = new directory + domain.yaml + Pydantic model + optional custom strategies. Zero changes to core.

---

## Anti-Patterns to Avoid

### 1. The "God Query" Anti-Pattern
**What:** A single query function with dozens of parameters trying to handle every domain's needs.
**Why it fails:** Parameters multiply with each domain. Callers need to know which parameters apply to which domain.
**Instead:** Use the Strategy pattern — each domain contributes focused, single-purpose retrieval strategies.

### 2. The "Abstract Everything" Anti-Pattern
**What:** Creating an abstract `DomainNode` base class with only `id` and `metadata: dict`, losing all typed fields.
**Why it fails:** Queries become string-key lookups into untyped dicts. No IDE support. Validation happens at runtime only if you remember to add it. This is the "over-abstraction causes semantic loss" finding from E7.
**Instead:** Keep typed Pydantic models per domain. The shared interface is a Protocol/ABC with common fields; domain models extend it with typed fields.

### 3. The "Separate Engine Per Domain" Anti-Pattern
**What:** Each domain gets its own query engine with its own traversal logic, result formatting, etc.
**Why it fails:** Massive code duplication. Cross-domain queries require custom glue. Every bug fix must be applied N times.
**Instead:** Shared engine + domain-contributed strategies. The engine owns traversal mechanics; domains own semantic interpretation.

### 4. The "Premature Federation" Anti-Pattern
**What:** Building a federated query system (separate graphs per domain, query routing, result merging) when all data fits in one graph.
**Why it fails:** Federation adds latency, complexity, and consistency challenges. At hundreds of nodes, it's all-pain-no-gain.
**Instead:** Single NetworkX graph with domain tags on nodes. Federate only if you outgrow single-process (millions of nodes).

### 5. The "Schema-Free Cowboy" Anti-Pattern
**What:** No domain registration. Anyone can add any node with any attributes. "We'll figure out the schema later."
**Why it fails:** Query interface can't make assumptions about what fields exist. Garbage data accumulates. Wikidata survives this via community governance at scale; small teams can't.
**Instead:** Explicit domain registration with Pydantic validation at ingestion time.

---

## Gap Analysis vs Current Implementation

Our current codebase (`domain.py`, `models.py`) already implements the Domain Registry pattern:
- `DomainManifest` declares schema, corpus, thresholds, required types
- `discover_domains()` scans for domain.yaml files
- `_resolve_schema()` does dynamic import of Pydantic models
- `GateConfig` configures validation gates per domain

**What's missing for retrieval:**
1. No `RetrievalStrategy` protocol or strategy registry
2. No strategy composition / result merging
3. `DomainManifest` doesn't declare edge types or retrieval hints
4. No domain-agnostic query interface that dispatches to strategies
5. Current query methods (keyword_search, concept_lookup in the graph module) are hardcoded, not pluggable

**Recommended next steps:**
1. Define `RetrievalStrategy` Protocol
2. Implement 3-4 built-in strategies (keyword, type_filter, bfs_neighbors, edge_type_traverse)
3. Extend `DomainManifest` with `edge_types` and `retrieval_strategies` fields
4. Build a `QueryEngine` that loads domains, discovers strategies, and composes results
5. Wire into existing CLI

---

*Research methodology: ddgr + WebSearch + WebFetch across academic papers, official documentation, and open-source repositories. All claims triangulated against 2+ sources. No sources were fabricated.*
