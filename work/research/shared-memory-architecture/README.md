# Research: Shared Memory Architecture

**Date:** 2026-02-25
**Session:** SES-281
**Decision informs:** Backend architecture for RaiSE Pro, RAISE-274 coordination

## Contents

- [Report](./shared-memory-architecture-report.md) — Synthesized findings and recommendations
- [Evidence Catalog](./sources/evidence-catalog.md) — All sources with ratings

## Research Questions

1. **Storage backend**: What DB for a knowledge graph scaling from NetworkX/JSON to shared server?
2. **Multi-repo shared graph**: How to architect personal vs shared vs org scopes across repos?
3. **Graph search algorithms**: What algorithms work for governance traceability, impact analysis, and relevance scoring?

## Key Decisions

| Dimension | Decision | Confidence |
|-----------|----------|-----------|
| Storage | PostgreSQL with nodes/edges + JSONB | HIGH |
| Multi-tenancy | scope + repo_id + org_id per node (Graphiti pattern) | VERY HIGH |
| Scopes | PERSONAL → PROJECT → ORG (data flows UP, never DOWN) | VERY HIGH |
| Server role | API for read/write (not harvest), local filesystem as offline fallback | HIGH |
| Query engine | NetworkX stays for in-memory scoring/traversal | HIGH |
| Next algorithm | Personalized PageRank (~10 lines) | HIGH |
| Open-core cut | Free=local+git, Pro=server+cross-repo+curation | HIGH |
| Dead ends | Embeddings, GNNs, LLM-dependent traversal at our scale | HIGH |
