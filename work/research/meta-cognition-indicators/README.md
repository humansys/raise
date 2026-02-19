# RES-METACOG-001: Meta-Cognition Indicators for Agent Memory

> 15-min overview for decision-makers

## What

How can Rai know what it knows, what it doesn't know, and where its knowledge has gaps — without relying on LLM introspection (which is unreliable)?

## Why

Currently, the graph has 1,244 nodes and 16,884 edges but no way to assess its own quality. The validation command checks 3 of 19 node types. 97.7% of edges are keyword noise. Neither Rai nor the human can see what's missing.

## Key Finding

**LLM self-assessment is unreliable** (Nature 2024, Steyvers 2025). Models are overconfident and fail to recognize knowledge boundaries. Meta-cognition must be **structural and deterministic**.

## Three Indicators

### 1. Coverage (Schema Completeness)
Does the graph have all expected node types with healthy populations?
```
coverage: 89% (17/19 types) | missing: release (stale)
```

### 2. Confidence (Structural Density)
How much connectivity is meaningful vs keyword noise?
```
density: 2.3% structural (383/16,884) | orphans: 12% | validation: 0%
```

### 3. Gaps (Competency Questions)
For a given context, what knowledge is missing?
```
$ rai memory gaps --module mod-memory
coverage: 83% (5/6 CQs answered) | gaps: no guardrail edges
```

## Decision

Implement as phased CLI commands:
1. `rai memory health` — global health report (S story)
2. Session-start integration — one-line health in context bundle (XS)
3. `rai memory gaps --module X` — scoped CQ-based gaps (M story)

**Confidence: HIGH** (12 sources, 4 RQs triangulated)

## Navigation

- [Full Report](RES-METACOG-001-report.md) — 4 RQs with evidence
- [Evidence Catalog](sources/evidence-catalog.md) — 12 sources
- [Foundation Research](../memory-systems/RES-MEMORY-002-research-report.md) — 50+ sources
- [Related: Temporal Decay Research](../temporal-decay-pattern-scoring/README.md) — Wilson scores feed into confidence indicator
