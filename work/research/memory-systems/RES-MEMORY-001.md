# Research: AI Memory Systems for F3.3 Memory Graph

> **ID:** RES-MEMORY-001
> **Date:** 2026-02-02
> **Status:** Complete
> **Researchers:** Rai (5 parallel subagents) + Emilio (direction)

---

## Research Questions

1. **RQ1:** How does OpenClaw structure memory for AI agents?
2. **RQ2:** How do Mem0 and Zep structure their knowledge graphs?
3. **RQ3:** How do Cognee and LangGraph handle memory?
4. **RQ4:** Can our E2 ConceptGraph be reused for memory?
5. **RQ5:** What does Context Engineering research recommend?

---

## Executive Summary

**Decision: BUILD on E2, don't adopt external system**

No existing open-source system supports our constraints (pure JSONL, file-based, no external DB, git-friendly). However, we can borrow proven patterns from the research.

**Key insight:** Start embarrassingly simple. Memory is judgment, not just storage.

---

## Findings by Source

### OpenClaw / Cline Memory Bank

**Architecture:** Markdown hierarchy, not graph
- Reads ALL files at session start (no selective retrieval)
- Strict dependency hierarchy (foundation → derived docs)
- Plan Mode gate — won't work until Memory Bank verified complete
- Two-tier: short-term (activeContext) vs long-term (patterns)

**File Structure:**
```
memory-bank/
├── projectBrief.md      # Foundation (source of truth)
├── productContext.md    # Why project exists
├── systemPatterns.md    # Architecture, design patterns
├── techContext.md       # Technologies, constraints
├── activeContext.md     # Current focus, recent changes
└── progress.md          # What works, what's left
```

**Key Pattern:** Complete context at session start, explicit update discipline.

**Sources:**
- [Cline Memory Bank Documentation](https://docs.cline.bot/prompting/cline-memory-bank)
- [Memory Bank System | DeepWiki](https://deepwiki.com/cline/prompts/3.1-memory-bank-system)

---

### MAGMA Research (State of the Art)

**Architecture:** 4 orthogonal graphs for different query types

| Graph Type | Edges | Query Type |
|------------|-------|------------|
| Semantic | Conceptual similarity | "What patterns exist?" |
| Temporal | Chronological order | "When did X happen?" |
| Causal | Logical entailment | "Why did X happen?" |
| Entity | Event-to-entity links | "What about person X?" |

**Performance:**
- 95% token reduction vs full context
- 40% faster retrieval
- Query-adaptive traversal (why → causal, when → temporal)

**Key Pattern:** Different query types need different graph traversal strategies.

**Sources:**
- [MAGMA Paper - arXiv 2601.03236](https://arxiv.org/abs/2601.03236)

---

### Mem0

**Architecture:** Dual-store hybrid (vector + graph + history)

| Store | Purpose | Backend Options |
|-------|---------|-----------------|
| Vector | Embeddings | Qdrant, Chroma, FAISS, LanceDB |
| Graph | Relationships | Neo4j, Memgraph, **Kuzu** (embedded) |
| History | Conversations | SQLite |

**Node Types:** Dynamic entity extraction via LLM (people, locations, objects, concepts)

**Relationship Model:** Triplets `(source_entity, relation_label, destination_entity)`
- Labels dynamically generated: `lives_in`, `prefers`, `owns`, `works_at`
- Temporal reasoning: relationships marked invalid, not deleted

**Retrieval:**
1. Vector similarity search
2. Graph enrichment (parallel)
- Two modes: Entity-centric, Semantic triplet

**Performance:** 7-14k tokens/conversation (very efficient)

**Key Pattern:** Triplets with dynamic LLM extraction, conflict resolution via invalidation.

**Sources:**
- [Mem0 GitHub](https://github.com/mem0ai/mem0)
- [Mem0 Graph Memory Docs](https://docs.mem0.ai/open-source/features/graph-memory)
- [Mem0 Research Paper](https://arxiv.org/html/2504.19413v1)

---

### Zep / Graphiti

**Architecture:** Property graph with bi-temporal model

**Bi-temporal Edge Model (key insight):**
| Timestamp | Meaning |
|-----------|---------|
| `t_created` | When fact entered system |
| `t_expired` | When fact left system |
| `t_valid` | When fact was actually true |
| `t_invalid` | When fact stopped being true |

This handles "knowledge that changes" elegantly. Old facts marked invalid, not deleted.

**Node Types:**
- EntityNode (extracted entities)
- EpisodeNode (source provenance)
- Communities (semantic groupings)

**Edge Types:**
- Semantic edges (entity relationships)
- Episodic edges (provenance to source)

**Retrieval:** Hybrid (semantic + BM25 + graph distance), no LLM needed

**Performance:** P95 latency 300ms, but higher token usage (600k/conv)

**Key Pattern:** Full provenance via episodic edges, bi-temporal for evolving knowledge.

**Sources:**
- [Graphiti GitHub](https://github.com/getzep/graphiti)
- [Zep Paper - arXiv 2501.13956](https://arxiv.org/abs/2501.13956)
- [Kuzu DB Configuration](https://help.getzep.com/graphiti/configuration/kuzu-db-configuration)

---

### Cognee

**Architecture:** Hybrid graph-vector with file-based defaults

| Component | Default | Purpose |
|-----------|---------|---------|
| Graph | Kuzu (embedded) | Knowledge structure |
| Vectors | LanceDB (file-based) | Semantic search |
| Metadata | SQLite | Tracking |

**ECL Pipeline:** Extract → Cognify → Load (like ETL for knowledge)

**Node Types:**
- TextDocument (sources)
- DocumentChunk (all info links here)
- Entity (extracted)
- EntityType (classification)

**Key Principle:** Strict provenance — all derived nodes link to source chunks.

**Performance:** 92.5% accuracy vs traditional RAG's 60%

**Requirement:** Needs LLM for "cognify" step

**Key Pattern:** Zero-config local setup, strict provenance.

**Sources:**
- [Cognee GitHub](https://github.com/topoteretes/cognee)
- [Cognee + Kuzu Blog](https://blog.kuzudb.com/post/cognee-kuzu-relational-data-to-knowledge-graph/)

---

### LangGraph Memory

**Important:** NOT a knowledge graph — it's a state machine framework.

- Checkpointers for persistence (SQLite file-based option)
- Thread-based conversation isolation
- State = TypedDict passed between nodes
- No semantic retrieval, purely checkpoint recovery

**Fit for our use case:** Low (wrong paradigm)

**Sources:**
- [LangGraph GitHub](https://github.com/langchain-ai/langgraph)
- [langgraph-checkpoint-sqlite PyPI](https://pypi.org/project/langgraph-checkpoint-sqlite/)

---

### Context Engineering Guide

**Core Definition:** "The delicate art and science of filling the context window with just the right information for the next step."

**CELL Structure:**
```
CELL = [INSTRUCTIONS] + [EXAMPLES] + [MEMORY/STATE] + [CURRENT INPUT]
```

**Three-tier Memory:**
| Tier | Content | Strategy |
|------|---------|----------|
| Short-term | Recent turns | Windowing |
| Working | Active task state | Key-Value |
| Long-term | Persistent patterns | External storage |

**Token Budget ("40-40-20"):**
- ~40% system instructions
- ~40% contextual information
- ~20% response generation space

**MEM1 Research Findings (Singapore-MIT, NeurIPS 2025):**
- 3.5x performance improvement
- 3.7x reduction in memory usage
- Key insight: **Memory consolidation should be part of reasoning, not separate**
- "What to remember" is itself a reasoning task

**Cognitive Tools Pattern (IBM Zurich):**
- Structured prompt templates as "cognitive tools"
- Distinct operations: understanding, recalling, examining, backtracking
- Compartmentalization prevents confusion, creates auditable processes

**Key Patterns:**
1. Memory as reasoning (MEM1)
2. Recency weighting (newer = more relevant)
3. Consolidation cycles (periodic prune/merge)
4. Cognitive tools structure (explicit, auditable operations)

**Sources:**
- [Context Engineering Guide](https://github.com/davidkimai/Context-Engineering)
- [MEM1 Paper - arXiv:2506.15841](https://arxiv.org/abs/2506.15841)
- [MEM1 Project Site](https://mit-mi.github.io/mem1-site/)

---

### E2 ConceptGraph Review

**Reuse Assessment:** 70% reuse, 30% new code

| Component | Reuse Level | Action |
|-----------|-------------|--------|
| `ConceptGraph` class | 95% | Add JSONL loading |
| `Relationship` model | 100% | Use as-is |
| `traverse_bfs()` | 100% | Use as-is |
| Query engine pattern | 80% | Generalize |
| Relationship inference | 20% | New memory rules |

**Gaps to Fill:**
- JSONL support (currently single JSON)
- Incremental updates (currently full rebuild)
- Temporal queries ("what did I learn this week?")
- Memory-specific concept and relationship types

**Location:** `src/raise_cli/governance/graph/`

---

## Fit Assessment

| System | File-Based | JSONL | Simple Queries | No External DB | Fit |
|--------|------------|-------|----------------|----------------|-----|
| Cline | Yes (md) | No | N/A (no graph) | Yes | Pattern source |
| Mem0 | Via Kuzu | No | Via LLM | Kuzu ok | Medium |
| Zep | Via Kuzu | No | Cypher | Kuzu ok | Medium |
| Cognee | Yes | No | Cypher | Yes | Medium |
| LangGraph | Yes | No | N/A | Yes | Wrong paradigm |
| **Our E2** | Yes | **Yes** | BFS | Yes | **Best** |

**Conclusion:** No existing system fits our constraints. Build on E2.

---

## Patterns to Adopt

| Pattern | Source | How to Apply |
|---------|--------|--------------|
| **Triplets** | Mem0, Zep | `{subject, relation, object}` in JSONL |
| **Bi-temporal** | Zep | `valid_from`, `valid_until` on facts |
| **Provenance** | Zep, Cognee | Link all facts to source session |
| **Two-tier memory** | Cline | Short-term active vs long-term patterns |
| **Plan Mode gate** | Cline | Verify memory completeness before work |
| **Query dimensions** | MAGMA | Consider semantic, temporal, causal, entity |
| **Memory as reasoning** | MEM1 | Extraction involves judgment |
| **Cognitive tools** | Context Eng | Explicit, auditable memory operations |
| **Recency weighting** | Context Eng | Newer memories rank higher |
| **Consolidation** | MEM1 | Periodic prune/merge cycles |

---

## Recommendations for F3.3

### Architecture

```
.rai/memory/
├── patterns.jsonl      # Learned patterns (append-only)
├── calibration.jsonl   # Velocity data (append-only)
├── sessions/
│   └── index.jsonl     # Session metadata
└── graph.json          # Built from JSONL (rebuilt on query)
```

### JSONL Schema (Refined)

```jsonl
{"type": "pattern", "id": "PAT-027", "content": "...", "context": ["testing"], "learned_from": "SES-012", "created": "2026-02-02", "valid_from": "2026-02-02"}
{"type": "insight", "id": "INS-005", "content": "...", "validates": ["PAT-027"], "confidence": 0.9, "source_session": "SES-012", "created": "2026-02-02"}
{"type": "calibration", "id": "CAL-011", "feature": "F3.3", "size": "S", "estimated_min": 60, "actual_min": null, "created": "2026-02-02"}
```

### Concept Types

| Type | Description | Relationships |
|------|-------------|---------------|
| `Pattern` | Learned pattern | `learned_from`, `applies_to` |
| `Insight` | Key insight | `validates`, `learned_from` |
| `Calibration` | Velocity data | `for_feature` |
| `Session` | Session record | `contains` |
| `Preference` | Human preference | `held_by` |

### Relationship Types

| Type | Meaning | Example |
|------|---------|---------|
| `learned_from` | Provenance to session | Pattern → Session |
| `validates` | Evidence relationship | Insight → Pattern |
| `applies_to` | Domain scope | Pattern → Context |
| `references` | Mention relationship | Any → Any |
| `supersedes` | Replaces old fact | New → Old |

### Retrieval Strategy (Simple First)

1. **Keyword match** on query terms
2. **BFS expand** from matched concepts
3. **Recency weight** (newer = higher score)
4. **Return top N** by relevance × recency

### Token Budget

| Component | Budget | Notes |
|-----------|--------|-------|
| Identity Core | ~3K | Always loaded |
| Memory Query Result | ~1-2K | MVC, only relevant |
| Session Context | ~2-5K | Variable |
| Response Reserve | ~2-3K | Model thinking room |
| **Total typical** | **8-12K** | >80% savings target |

---

## Open Questions (for future research)

1. When should consolidation happen? (Session close? Daily? Weekly?)
2. How to handle contradicting patterns? (Zep's invalidation model?)
3. Should we add vector search for V3? (LanceDB integration?)
4. How to measure retrieval quality? (Precision/recall metrics?)

---

## Related Research

- [RES-OPENCLAW-001](../openclaw-architecture/) — OpenClaw architecture patterns (2026-02-01)
- [RES-PERSONA-001](../agent-personas/) — Agent personas not needed for katas (2026-01-31)

---

*Research completed: 2026-02-02*
*Method: 5 parallel subagents + synthesis*
*Key learning: Start simple, memory is judgment not storage*
