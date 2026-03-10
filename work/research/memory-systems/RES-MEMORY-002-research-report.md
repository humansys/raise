# RES-MEMORY-002: High-Density Neurosymbolic Memory for LLM Context

> **Date:** 2026-02-18
> **Status:** Complete
> **Authors:** Emilio Osorio + Rai
> **Method:** Systematic research — 4 parallel research questions, 50+ sources, triangulated claims
> **Audience:** RaiSE engineers, technical leads, anyone evaluating the memory architecture

---

## Executive Summary

RaiSE promises **neurosymbolic memory with high semantic density** — a Minimum Viable Context (MVC) that delivers maximum semantic impact to an LLM with minimum tokens. This research investigates the state of the art across four dimensions to validate our architecture, identify gaps, and inform the roadmap.

**Key findings:**

1. **RaiSE's memory architecture is already neurosymbolic and well-aligned with SOTA.** The knowledge graph (1,244 nodes, 16,884 edges, 10+ relation types) implements the hybrid neural+symbolic pattern that every successful memory system converges on.

2. **The bottleneck is serialization, not architecture.** We have rich relational knowledge but serialize it as isolated nodes in decorated markdown. The graph's structure — its core advantage — never reaches the LLM context.

3. **The biggest compression gain comes from removing irrelevant content, not shortening relevant content.** Empirically, removing distractors *improves* LLM performance by up to 21.4% (LongLLMLingua). There is an optimal context size — more is worse.

4. **Format choice causes up to 40% performance variation.** Claude excels with hierarchical formats (YAML, Markdown-KV). Key repetition (JSON arrays) is the single largest source of token waste. The correct metric is accuracy-per-token, not minimum tokens.

5. **Six gaps identified**, ranging from quick fixes (hours) to research frontiers (epic-scale).

---

## Research Questions & Methodology

Four parallel research agents (Claude Opus, ~60K tokens each) investigated:

| RQ | Focus | Sources | Catalog |
|----|-------|---------|---------|
| **RQ1** | Neurosymbolic memory foundations | 12 papers (NeurIPS, ICML, NAACL) + 4 foundational works | [RES-MEMORY-002-neurosymbolic-foundations.md](RES-MEMORY-002-neurosymbolic-foundations.md) |
| **RQ2** | Semantic compression & information density | 15 peer-reviewed papers + 4 surveys | [RES-MEMORY-002-semantic-compression.md](RES-MEMORY-002-semantic-compression.md) |
| **RQ3** | Memory system implementations | 11 systems surveyed + 5 benchmarks | [RES-MEMORY-002-implementations-survey.md](RES-MEMORY-002-implementations-survey.md) |
| **RQ4** | Serialization formats for LLM context | 10 academic papers + 8 practitioner benchmarks | [RES-MEMORY-002-serialization-formats.md](RES-MEMORY-002-serialization-formats.md) |

**Epistemological standards applied:** Claims triangulated across 3+ sources where possible. Evidence levels rated (Very High → Low). Contrary evidence noted explicitly. Gaps in literature acknowledged.

---

## Key Findings

### 1. First Principles of Neurosymbolic Memory (RQ1)

Seven independent lines of evidence (cognitive science, neuroscience, AI engineering, knowledge representation, hallucination research, neurosymbolic theory, agent memory research) converge on **8 properties** a neurosymbolic memory must have:

| Property | Description | Key Evidence |
|----------|-------------|--------------|
| **Dual Representation** | Both embeddings (fuzzy retrieval) and graph (precise reasoning) | HippoRAG +20% on multi-hop QA (NeurIPS 2024) |
| **Composability** | Facts link to form reasoning chains | GraphRAG community summaries (Microsoft 2024) |
| **Selective Encoding** | Prioritize novel/high-value information | Titans surprise-driven learning (Google 2024) |
| **Graceful Forgetting** | Decay, consolidate, prune old memories | CLS theory (McClelland 1995), Titans weight decay |
| **Hierarchical Organization** | Multiple abstraction levels co-exist | MemGPT main/archival (2023), M+ GPU/CPU banks |
| **Partial-Cue Retrieval** | Retrieve from incomplete queries | Kanerva SDM (1988), HippoRAG PageRank |
| **Writability at Inference** | Update memory during interaction | MemGPT self-edit, A-Mem evolution (NeurIPS 2025) |
| **Grounding** | Structured memory constrains generation | 61% hallucination reduction via KG (NAACL 2024) |

### 2. Semantic Compression Principles (RQ2)

| Principle | Implication |
|-----------|------------|
| **Compression is the dual of prediction** | Tokens the model can predict carry zero information. The incompressible residual is the true content. |
| **Task relevance dominates compression ratio** | Removing irrelevant content (10-20x gain) > compressing relevant content (3-5x gain). |
| **Optimal context size exists (not maximum)** | "Lost in the Middle" (TACL 2024): 15-20pp accuracy drop from position alone. More context hurts. |
| **Natural language is 3-20x redundant** | Lexical ~3-5x, semantic ~5-10x, task-relevance ~10-20x. These stack. |
| **Hard ceiling ~20-30x for general compression** | Multiple methods converge. Task-specific can exceed (RECOMP: 95% reduction for factoid QA). |
| **Format is a compression lever** | Structured representations encode more per token than prose for LLM reasoning. |
| **Compression methods are complementary** | Filter by relevance → compress tokens → encode densely. Three layers. |

**The MVC Inequality:**
```
K(answer) ≤ |MVC(task, context)| ≤ |compressed(context)| ≤ |context|
```
The gap between MVC and compressed(context) — the "task-relevance gap" — is where the biggest wins are.

### 3. State of Practice (RQ3)

**11 systems surveyed:** MemGPT/Letta, Zep/Graphiti, Mem0, GraphRAG, LangMem, Cognee, LlamaIndex, MemOS, A-Mem, OpenAI Memory, Supermemory.

**Consensus patterns:**
- **Hybrid storage is the consensus** — vectors + graphs + structured stores. No single paradigm suffices.
- **Compress at write, not read** — Zep and Mem0 invest in extraction/dedup at ingest. 90%+ latency reduction.
- **Temporal awareness separates leaders** — Zep's bi-temporal model is the most sophisticated.
- **Every high-performing system is neurosymbolic** — pure vector or pure symbolic both fail.
- **Active curation beats passive storage** — extract, deduplicate, merge, prune.

**Sobering reality:** MemoryBench found **no advanced system consistently beats naive RAG baselines**. LongMemEval shows 30% accuracy drop for commercial systems on sustained interactions. The field is immature despite rapid commercialization.

### 4. Serialization Format Evidence (RQ4)

| Finding | Evidence Level | Impact |
|---------|---------------|--------|
| Format choice causes up to **40% performance variation** | High (He et al., arXiv 2411.10541) | Not marginal — format is a first-class design decision |
| **Claude excels with hierarchical formats** (JSON/YAML) | Medium-High (Preprints.org 202506.1937) | Model-specific optimization matters |
| **Key repetition is the single biggest waste** | Very High (multiple studies) | Declare fields once (headers), not per record |
| **Markdown-KV is top performer for entity descriptions** | High (ImprovingAgents, 11-format benchmark) | 60.7% accuracy, 16pp ahead of CSV |
| **Accuracy-per-token is the correct metric** | High (triangulated) | Markdown-KV: 2.7x more tokens than CSV but far better accuracy |
| **TOON: 40-75% fewer tokens than JSON** | Medium (creator benchmarks, needs replication) | Promising but unproven at scale |
| **Output format restrictions hurt reasoning by 10-15%** | High (Tam et al., arXiv 2408.02442) | Let LLM reason freely, extract structure in second pass |

---

## Current State Assessment: RaiSE Memory

### What We Already Do Right

| SOTA Practice | RaiSE Implementation | Status |
|---------------|---------------------|--------|
| **Compress at write** | `/rai-session-close` extracts patterns, deduplicates, persists | Implemented |
| **Cognitive memory taxonomy** | Semantic (patterns, terms), Episodic (sessions, stories), Procedural (skills) | Implemented |
| **Graph structure** | NetworkX directed multigraph, 1,244 nodes, 16,884 edges, 10+ relation types | Implemented |
| **Hierarchical organization** | Project → epic → story → task; modules → bounded contexts → layers | Implemented |
| **Selective encoding** | `foundational` and `always_on` flags for behavioral primes | Partial |
| **Provenance/traceability** | `created`, `learned_from`, edge types | Partial |

### What We're Missing

| Gap | Description | Severity |
|-----|-------------|----------|
| **A. Dense serialization** | Query output is 30-40% decoration. No compact format. | High — directly wastes context tokens |
| **B. Edge-aware results** | Query returns isolated nodes. Graph structure never reaches LLM. | High — defeats the purpose of having a graph |
| **C. Task-relevance filtering** | Context bundle loads fixed sections regardless of task type | Medium — ~220 tokens of potentially irrelevant primes |
| **D. Truncation transparency** | `--limit` clips silently. LLM doesn't know more exists. | Low — easy fix, high trust impact |
| **E. Temporal decay** | All patterns have equal weight regardless of age or validation | Medium — will degrade as pattern count grows |
| **F. Meta-cognition** | No coverage indicators, confidence scoring, or gap detection | Low (now) — differentiator long-term |

### Serialization Overhead Analysis

**Current query output (`--format human`):**
```
Per-concept overhead: ~25 tokens (###, **Source:**, **Created:**, blank lines, ---)
Global overhead: ~30 tokens (title, query metadata, footer)
Semantic content ratio: ~60-70%
```

**Current context bundle (~600 tokens):**
```
Structural overhead: ~100 tokens (headers, separators, labels)
Fixed primes (governance + identity + behavioral): ~220 tokens
Semantic content: ~280 tokens
Effective density: ~47%
```

**MCP tool definitions tax (measured):**
```
47 Atlassian + Context7 tools: ~13,500 tokens
Built-in tools: ~5,000-7,000 tokens
Total tool tax: ~20,000 tokens before any conversation
```

---

## Proposed Epic Scope

### Vision

Transform RaiSE's memory serialization from human-readable markdown to **semantically dense, edge-aware, task-relevant context** that maximizes accuracy-per-token for Claude's comprehension.

### Stories (by priority)

| # | Story | Size | Description |
|---|-------|------|-------------|
| 1 | **Compact query format** | S | `--format compact`: header-based, one fact per line, ~20 tokens/result vs ~80 today |
| 2 | **Fix concept_lookup + edge serialization** | S | Fix broken BFS, serialize 1-hop edges in compact format |
| 3 | **Truncation indicator** | XS | `[+N more — use --limit to see more]` footer |
| 4 | **Task-relevant context bundle** | M | Parametrize bundle sections by session type / story phase |
| 5 | **Temporal decay & pattern scoring** | M | Recency, reinforcement count, frequency-based scoring for pattern retrieval |
| 6 | **Meta-cognition indicators** | L | Coverage analysis, confidence scoring, gap detection |

Stories 1-3 are the quick hits (RAISE-166 scope). Stories 4-6 are follow-up.

### Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Tokens per query result (compact) | ~80 | ~20-30 |
| Semantic content ratio (query) | ~65% | ~85%+ |
| Edge visibility in results | 0% (nodes only) | 1-hop edges included |
| Context bundle effective density | ~47% | ~70%+ |
| Truncation transparency | Silent | Always visible |

### Non-Goals (This Epic)

- Changing the graph architecture (NetworkX → Neo4j, etc.)
- Adding vector embeddings / similarity search
- Implementing bi-temporal model (Zep-style)
- Building benchmark infrastructure

---

## References

### Evidence Catalogs (This Research)

1. [RQ1: Neurosymbolic Memory Foundations](RES-MEMORY-002-neurosymbolic-foundations.md) — 12 SOTA papers + 6 foundational works
2. [RQ2: Semantic Compression & Information Density](RES-MEMORY-002-semantic-compression.md) — 15 peer-reviewed papers + 4 surveys
3. [RQ3: Memory System Implementations Survey](RES-MEMORY-002-implementations-survey.md) — 11 systems + 5 benchmarks
4. [RQ4: Serialization Formats for LLM Context](RES-MEMORY-002-serialization-formats.md) — 10 academic papers + 8 practitioner benchmarks

### Key Papers (Most Cited Across RQs)

- HippoRAG — Gutierrez et al., NeurIPS 2024 ([arXiv:2405.14831](https://arxiv.org/abs/2405.14831))
- Language Modeling Is Compression — Deletang et al., ICLR 2024 ([arXiv:2309.10668](https://arxiv.org/abs/2309.10668))
- Lost in the Middle — Liu et al., TACL 2024 ([arXiv:2307.03172](https://arxiv.org/abs/2307.03172))
- A-Mem — Xu et al., NeurIPS 2025 ([arXiv:2502.12110](https://arxiv.org/abs/2502.12110))
- Prompt Compression Survey — Li et al., NAACL 2025 ([ACL Anthology](https://aclanthology.org/2025.naacl-long.368/))
- GraphRAG — Edge et al., Microsoft Research 2024 ([arXiv:2404.16130](https://arxiv.org/abs/2404.16130))
- LLMLingua-2 — Pan et al., ACL 2024 ([arXiv:2403.12968](https://arxiv.org/abs/2403.12968))
- Does Prompt Formatting Impact LLM Performance? — He et al. ([arXiv:2411.10541](https://arxiv.org/abs/2411.10541))
- Mem0 — ([arXiv:2504.19413](https://arxiv.org/abs/2504.19413))
- Zep/Graphiti — ([arXiv:2501.13956](https://arxiv.org/abs/2501.13956))

---

*Research completed 2026-02-18. This document serves as the research foundation for the Neurosymbolic Memory Density epic.*
