# Research: Unified Context Architecture for AI Agents

> **Status:** Complete
> **Date:** 2026-02-03
> **Decision:** Informs E11 design
> **Research ID:** RES-CONTEXT-001

---

## Research Question

How do professional teams implement unified knowledge graphs for AI context? What architecture patterns and libraries can we leverage for E11?

---

## Executive Summary

**Key Finding:** The industry has converged on **hybrid graph architectures** that combine multiple retrieval methods (semantic, keyword, graph traversal) into unified query interfaces. The pattern is clear: don't choose between approaches — compose them.

**Recommendation:** Use **NetworkX** as our graph foundation (lightweight, no dependencies, JSON-serializable) with a **unified schema** that treats all concepts (patterns, principles, skills, work items) as nodes in a single graph. Add semantic search later if needed.

**Confidence:** HIGH (triangulated across 5+ major sources, production-proven patterns)

---

## Key Findings

### 1. GraphRAG is the Dominant Pattern (2024-2026)

Microsoft's GraphRAG and derivatives have become the standard for combining knowledge graphs with LLM context:

| Approach | How It Works | When It Wins |
|----------|--------------|--------------|
| **Traditional RAG** | Vector similarity on chunks | Simple Q&A, single-hop |
| **GraphRAG** | Graph traversal + vector | Multi-hop reasoning, relationships |
| **Hybrid** | Both + keyword (BM25) | Best overall precision |

**Key insight:** GraphRAG shows **20-35% improvement** in retrieval precision over traditional RAG for relationship-aware queries.

**Source:** [Neo4j GraphRAG Patterns](https://neo4j.com/nodes-2025/agenda/enhancing-retrieval-augmented-generation-with-graphrag-patterns-in-neo4j/)

### 2. Dual-Channel Retrieval is Standard

Modern systems use multiple retrieval channels merged into unified results:

```
Query
  ├─► Vector similarity (semantic)
  ├─► Keyword search (BM25)
  └─► Graph traversal (relationships)
      │
      └─► Merge & Rank ─► Unified Context
```

**Why:** Each channel catches what others miss:
- Vector: semantic similarity even with different words
- Keyword: exact matches, technical terms
- Graph: relationships, multi-hop connections

**Source:** [Nature - KG-RAG Research](https://www.nature.com/articles/s41598-025-21222-z)

### 3. Graphiti: Temporal Knowledge Graphs for Agents

Zep's Graphiti is specifically designed for AI agent memory with:

- **Bi-temporal model**: Event time (when it happened) + Ingestion time (when learned)
- **Episodic memory**: Raw events as ground truth
- **Real-time updates**: No batch recomputation needed
- **Hybrid search**: Semantic + BM25 + graph traversal at 300ms P95

**Architecture:**
```
Episode Subgraph (raw events, timestamped)
    ↓ extraction
Entity Subgraph (deduplicated, facts with validity periods)
    ↓ query
Hybrid Search (semantic + keyword + traversal)
```

**Relevance to us:** Their episodic → semantic extraction is similar to our sessions → patterns flow.

**Source:** [Graphiti GitHub](https://github.com/getzep/graphiti), [Zep Paper](https://arxiv.org/abs/2501.13956)

### 4. NetworkX for Lightweight Local Graphs

For in-memory knowledge graphs without external databases:

- **No dependencies** beyond Python stdlib
- **Dict-of-dicts** structure enables fast lookups
- **Any Python object** as node/edge attributes
- **JSON serializable** with `node_link_data()`
- **Scales to thousands of nodes** in memory

**When to use NetworkX vs Neo4j:**
- NetworkX: Local, <10K nodes, no infrastructure
- Neo4j: Distributed, complex queries, >100K nodes

**Source:** [Simple In-Memory Knowledge Graphs](https://safjan.com/simple-inmemory-knowledge-graphs-for-quick-graph-querying/)

### 5. Federated vs Unified: Industry Leans Unified

Two patterns exist for combining multiple knowledge sources:

| Pattern | How | Pros | Cons |
|---------|-----|------|------|
| **Federated** | Query multiple graphs, merge results | Separation of concerns | Complex merging, inconsistent |
| **Unified** | Single graph, multiple node types | Simple queries, cross-domain links | Schema complexity |

**Industry trend:** Unified graphs with **ontology layer** for consistency.

> "A global semantic layer resolves inconsistencies across domains, delivering AI-ready, context-rich data."
> — [Actian: Federated Knowledge Graphs](https://www.actian.com/blog/data-intelligence/why-federated-knowledge-graphs-are-the-missing-link-in-your-ai-strategy/)

**Relevance:** Our patterns, principles, skills, and work items are small enough for unified graph.

### 6. LlamaIndex Property Graph Pattern

LlamaIndex's Property Graph Index supports multiple retrievers composed together:

- **LLMSynonymRetriever**: Expand query to keywords/synonyms
- **VectorContextRetriever**: Vector similarity + connected paths
- **TextToCypherRetriever**: Natural language → graph query
- **Custom retrievers**: Subclass for specific needs

**Key pattern:** Retrievers are **composable** — run multiple, merge results.

**Source:** [LlamaIndex Property Graph](https://www.llamaindex.ai/blog/introducing-the-property-graph-index-a-powerful-new-way-to-build-knowledge-graphs-with-llms)

---

## Architecture Recommendation for E11

Based on research, here's the recommended architecture:

### Option A: Simple Unified Graph (Recommended for F&F)

```
Single NetworkX MultiDiGraph
├── Node Types:
│   ├── pattern (PAT-*)
│   ├── calibration (CAL-*)
│   ├── session (SES-*)
│   ├── principle (§N)
│   ├── requirement (RF-*)
│   ├── outcome (OUT-*)
│   ├── epic (E*)
│   ├── feature (F*.*)
│   └── skill (/skill-name)
│
├── Edge Types:
│   ├── learned_from (pattern → session)
│   ├── governed_by (requirement → principle)
│   ├── applies_to (pattern → skill)
│   ├── needs_context (skill → node types)
│   ├── implements (feature → requirement)
│   └── related_to (generic semantic link)
│
└── Query Interface:
    raise context query "planning F11.1"
    → BFS from matching nodes
    → Filter by relevance
    → Return MVC
```

**Why this works:**
1. NetworkX handles our scale easily (<1K nodes)
2. Single graph enables cross-domain relationships
3. JSON serialization for persistence
4. No external dependencies
5. Can add vector search later if needed

### Option B: Hybrid with Embeddings (Post-F&F)

Add semantic search layer:
```
Query
  ├─► Keyword match (current)
  ├─► Embedding similarity (new)
  └─► Graph traversal (current)
      │
      └─► Merge ─► MVC
```

Only if keyword matching proves insufficient.

---

## Libraries Comparison

| Library | Use Case | Dependencies | Our Fit |
|---------|----------|--------------|---------|
| **NetworkX** | In-memory graph | None | ✅ Perfect |
| **Graphiti** | Temporal agent memory | Neo4j, OpenAI | ⚠️ Overkill |
| **LlamaIndex** | RAG pipelines | Heavy | ⚠️ Overkill |
| **Microsoft GraphRAG** | Document understanding | Azure, LLMs | ❌ Wrong scale |
| **kglab** | RDF/semantic web | RDFLib, etc. | ❌ Wrong paradigm |

**Recommendation:** NetworkX is sufficient for our needs. We already use it transitively.

---

## Implementation Implications

### For E11 Design

1. **Single graph file**: `.raise/graph/unified.json`
2. **Node schema**: Type + ID + content + metadata + embeddings (optional)
3. **Edge schema**: Type + source + target + metadata
4. **Query**: BFS from seed nodes, filter by type/relevance
5. **Build**: Merge existing builders (governance, memory, work)

### Schema Sketch

```python
from pydantic import BaseModel
from typing import Literal

class ConceptNode(BaseModel):
    id: str  # PAT-001, §2, F11.1, /story-plan
    type: Literal["pattern", "calibration", "session", "principle",
                  "requirement", "outcome", "epic", "feature", "skill"]
    content: str  # The actual text/description
    source_file: str | None  # Where it came from
    created: str  # ISO timestamp
    metadata: dict  # Type-specific attributes

class ConceptEdge(BaseModel):
    source: str  # Node ID
    target: str  # Node ID
    type: Literal["learned_from", "governed_by", "applies_to",
                  "needs_context", "implements", "related_to"]
    weight: float = 1.0
    metadata: dict = {}
```

### Migration Path

1. **F11.1**: Build governance graph (already have extractor)
2. **F11.2**: Index skills into graph
3. **F11.3**: Merge memory graph into unified
4. **F11.4**: Unified query command
5. **F11.5**: Skill integration

---

## Evidence Catalog

| Source | Type | Level | Key Finding |
|--------|------|-------|-------------|
| [Microsoft GraphRAG](https://github.com/microsoft/graphrag) | Primary | Very High | Hierarchical communities, LLM extraction |
| [Neo4j GraphRAG](https://neo4j.com/blog/news/graphrag-python-package/) | Primary | High | 20-35% precision improvement |
| [Graphiti/Zep](https://github.com/getzep/graphiti) | Primary | High | Bi-temporal, episodic memory |
| [Nature KG-RAG](https://www.nature.com/articles/s41598-025-21222-z) | Primary | Very High | Dual-channel retrieval |
| [LlamaIndex Property Graph](https://www.llamaindex.ai/blog/introducing-the-property-graph-index-a-powerful-new-way-to-build-knowledge-graphs-with-llms) | Primary | High | Composable retrievers |
| [NetworkX Tutorial](https://networkx.org/documentation/stable/tutorial.html) | Primary | Very High | In-memory graph API |
| [Actian Federated KG](https://www.actian.com/blog/data-intelligence/why-federated-knowledge-graphs-are-the-missing-link-in-your-ai-strategy/) | Secondary | Medium | Unified > federated trend |
| [Ultimate RAG Blueprint](https://langwatch.ai/blog/the-ultimate-rag-blueprint-everything-you-need-to-know-about-rag-in-2025-2026) | Secondary | Medium | Industry convergence |

---

## Conclusion

The research strongly supports a **single unified graph** approach using **NetworkX**:

1. **Proven pattern**: Industry uses unified graphs with multiple node types
2. **Right scale**: NetworkX handles our size without infrastructure
3. **Extensible**: Can add embeddings/hybrid search later
4. **No new dependencies**: NetworkX is already in our dependency tree
5. **Cross-domain links**: Patterns can connect to principles, skills to features

**Recommendation:** Proceed with unified NetworkX graph for E11. Start simple (keyword + BFS), add sophistication only if needed.

---

## Next Steps

1. Create ADR-019 documenting unified graph decision
2. Update E11 scope with this architecture
3. Design unified schema (Pydantic models)
4. Plan migration from separate graphs

---

*Research completed: 2026-02-03*
*Researcher: Rai*
*Reviewed by: Emilio Osorio*
