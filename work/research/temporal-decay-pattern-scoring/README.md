# RES-TEMPORAL-001: Temporal Decay and Pattern Scoring

> 15-min overview for decision-makers

## What

How to make recently-learned and frequently-relevant patterns rank higher than stale ones in RaiSE's memory retrieval, without losing foundational knowledge.

## Why

Currently all 200+ patterns score equally regardless of age. The scoring function is `keyword_hits * 10 + 5 (if created this month)` — a hardcoded month string, not real temporal logic. As patterns grow, signal-to-noise degrades.

## Key Finding

The literature converges on a **three-factor model** (recency + importance + relevance). For our constraints (JSONL, no embeddings, <500 patterns), a **two-factor half-life decay** is sufficient:

```
score = w_r * exp(-ln(2)/H * age_days) + w_k * (keyword_hits / total_keywords)
```

Foundational patterns are exempt from decay (score always = relevance only).

## Decision

Implement half-life exponential decay (H=30 days default) as a retrieval-time score modifier. No schema changes needed. ~S-M story.

## Navigation

- [Full Report](RES-TEMPORAL-001-report.md)
- [Evidence Catalog](sources/evidence-catalog.md) — 12 sources
- [Foundation Research](../memory-systems/RES-MEMORY-002-research-report.md) — 50+ sources
