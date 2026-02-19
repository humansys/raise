# RES-TEMPORAL-001: Temporal Decay and Pattern Scoring

> 15-min overview for decision-makers

## What

How to make recently-learned, frequently-validated patterns rank higher than stale or contradicted ones in RaiSE's memory retrieval.

## Why

Currently all 200+ patterns score equally regardless of age or validation history. The scoring function is `keyword_hits * 10 + 5 (if created this month)` — a hardcoded month string, not real temporal logic. As patterns grow, signal-to-noise degrades.

## Key Findings

### Part 1: Temporal Decay
The literature converges on a **three-factor model** (recency + importance + relevance). For our constraints (JSONL, no embeddings, <500 patterns), a **two-factor half-life decay** is sufficient.

### Part 2: Reinforcement via Implicit HITL ("Reddit for Patterns")
The existing HITL workflow already produces validation signals. When Rai loads patterns at story-start and the implementation follows/contradicts them, that's an implicit vote. **Wilson score lower bound** (Reddit's comment ranking algorithm) handles this optimally with small sample sizes.

## Formula

```
score = (0.3 * recency + 0.7 * relevance) * validation_modifier

recency      = exp(-ln(2)/30 * age_days)     # half-life 30 days
relevance    = keyword_hits / total_keywords  # normalized [0,1]
validation   = wilson_lower_bound(pos, neg)   # [0,1], conservative
               or 1.0 if never evaluated      # neutral default
```

Foundational patterns exempt from decay (score = relevance only).

## Decision

Implement composite score with Wilson-based validation modifier in `calculate_relevance_score()`. Signal collection in `/story-review` via Rai auto-evaluation. **Confidence: HIGH** (20 sources, 7 RQs triangulated).

## Navigation

- [Full Report](RES-TEMPORAL-001-report.md) — 7 RQs with evidence
- [Evidence Catalog — Temporal](sources/evidence-catalog.md) — 12 sources
- [Evidence Catalog — Reinforcement](sources/evidence-catalog-reinforcement.md) — 8 sources
- [Foundation Research](../memory-systems/RES-MEMORY-002-research-report.md) — 50+ sources
