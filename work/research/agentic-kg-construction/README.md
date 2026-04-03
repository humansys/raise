# Research: Agentic KG Construction Architectures

> **Status**: Complete
> **Date**: 2026-03-18
> **Researcher**: Rai (Claude Opus 4.6)
> **Decision Context**: Epic E3 — ScaleUp Agent

## Research Question

What agentic architectures are validated for building knowledge graphs from scratch, and how do they compare with GraphRAG and traditional RAG approaches?

## Files

| File | Purpose |
|------|---------|
| [sources/evidence-catalog.md](sources/evidence-catalog.md) | Full evidence catalog (28 sources) |
| [synthesis.md](synthesis.md) | Triangulated claims, patterns, gaps |
| [recommendation.md](recommendation.md) | Actionable architecture recommendation |

## Key Findings (Summary)

1. **Full GraphRAG is overkill** for E3's corpus size (~10-50 documents). Cost 3-5x baseline; ICLR'26 benchmark shows it underperforms vanilla RAG on many tasks.

2. **Multi-agent KG construction works** (KARMA, NeurIPS'25 spotlight: 83.1% correctness with 9 agents). But 3 agents suffice for smaller corpora.

3. **Schema-guided extraction is non-negotiable** for domain KGs. Every validated system that works well uses ontology constraints.

4. **Hybrid KG + vector retrieval** outperforms either alone (94%+ relevancy in domain QA benchmarks).

5. **Cost-efficient alternatives exist**: LightRAG (0.16% of GraphRAG query cost), LazyGraphRAG (0.1% indexing cost), KAG Lightweight (89% token reduction).

## Recommendation

Custom lightweight pipeline: Pydantic ontology + 3-agent extraction (extractor, validator, curator) + dual-index retrieval (property graph + vector store). See [recommendation.md](recommendation.md) for full architecture.

## Reproducibility

### Search Queries Used
1. "Microsoft GraphRAG architecture entity relation extraction pipeline evaluation 2024 2025"
2. "agentic knowledge graph construction multi-agent LLM pipeline 2024 2025"
3. "LightRAG NanoGraphRAG alternative GraphRAG comparison benchmark 2025"
4. "structured retrieval knowledge graph vs vector RAG accuracy domain-specific QA benchmark 2024 2025"
5. "LLM agent graph refinement conflict resolution schema evolution knowledge graph 2024 2025"
6. "GraphRAG limitations cost token usage production experience Reddit engineering blog 2025"
7. "neuro-symbolic retrieval LLM knowledge graph hybrid architecture 2024 2025"
8. "DSPy knowledge extraction module knowledge graph construction pipeline 2025"
9. "Neo4j LLM knowledge graph builder integration production 2025"
10. "GraphRAG-Bench ICLR 2026 when to use graphs in RAG benchmark results"
11. "FinReflectKG agentic knowledge graph construction reflection iterative extraction 2025"
12. "LlamaIndex knowledge graph index PropertyGraphIndex 2025 evaluation"
13. "LazyGraphRAG Microsoft 2025 cost efficient graph retrieval"
14. "KARMA multi-agent knowledge graph enrichment NeurIPS 2025 nine agents architecture"
15. "E2GraphRAG efficient graph RAG streamlining cost reduction 2025"
16. "KAG knowledge augmented generation framework Ant Group 2024 2025 evaluation"
17. "ontology learning LLM automated schema induction comparison approaches RAG 2025"
18. "Graphiti real-time knowledge graph AI agents Zep 2025"

### Key URLs
- Microsoft GraphRAG: https://github.com/microsoft/graphrag
- GraphRAG-Bench: https://github.com/GraphRAG-Bench/GraphRAG-Benchmark
- KARMA: https://arxiv.org/abs/2502.06472
- KAG/OpenSPG: https://github.com/OpenSPG/KAG
- LightRAG: https://arxiv.org/html/2410.05779v1
- LazyGraphRAG: https://www.microsoft.com/en-us/research/blog/lazygraphrag-setting-a-new-standard-for-quality-and-cost/
- Graphiti/Zep: https://github.com/getzep/graphiti
- E2GraphRAG: https://github.com/YiboZhao624/E-2GraphRAG
- FinReflectKG: https://arxiv.org/abs/2508.17906
- Neo4j LLM Graph Builder: https://github.com/neo4j-labs/llm-graph-builder
- DSPy: https://dspy.ai/

### Evidence Quality Distribution
- Very High: 3 sources (KARMA NeurIPS'25, GraphRAG-Bench ICLR'26, KAG production)
- High: 13 sources
- Medium: 9 sources
- Low: 3 sources (community/anecdotal)
