# ADR-014: Skill Introspection Aspect — 3-Tier Model with Learning Chain

**Status:** Proposed
**Date:** 2026-03-31 (updated 2026-04-01)
**Epic:** E1133 (Skill Introspection)
**Revised:** 2026-04-01 — CC SAR alignment (E1132 findings B,D,E,F,H)

## Context

RaiSE lifecycle skills generate outputs that shape architecture, code, and process — but only 2 of 12 consult the knowledge graph before generating, only 1 captures learnings, and no skill measures its own effectiveness. All evaluation concentrates in story-review, too late for granular attribution.

Three research investigations inform this decision:
1. **Agentic Memory SOTA** (10 frameworks) — industry converges on tiered hybrid retrieval. Post-use evaluation is the biggest gap.
2. **Self-Improving Agents SOTA** (12+ sources) — MetaHarness proves raw traces are essential (15+ point advantage over summaries). MCE proves skill evolution (bi-level optimization) yields 16.9% improvement over context-only evolution.
3. **MetaHarness gemba walk** — the outer loop is trivially simple; the traces are the hard part. Without rich traces, no self-improvement paradigm works.

**Additional input (2026-04-01):** E1132 Claude Code Architecture Reconstruction validated 7 design improvements against CC's production architecture (deterministic context assembly, compaction resilience, error isolation, hard limits).

Three architectural decisions require resolution:
1. **Retrieval model:** Automatic vs explicit vs hybrid
2. **Integration mechanism:** Per-skill steps vs shared cross-cutting concern
3. **Measurement model:** Separate evaluation phase vs measurement-as-operation

## Decision

### 1. Adopt a 3-tier retrieval model with deterministic priming

```
Tier 0: GUARDRAILS — always in system prompt (exists)
Tier 1: PHASE PRIME — deterministic queries before skill (template + variable substitution)
Tier 2: JIT ALIGNMENT — agent-initiated at decision bifurcations (LLM-adaptive)
LEARN — evaluate + capture + measure (produces learning record)
```

Tier 1 is **deterministic, not LLM-refined**. Queries are fixed templates with variable substitution from execution context. The bitter lesson (Sutton 2019) applies to the outer loop (self-improvement), not the inner loop (execution). CC (E1132 F14) loads CLAUDE.md deterministically — 6 tiers, always the same. The LLM decides what to *do* with context, not what context to *receive*.

JIT (Tier 2) remains LLM-adaptive — that's where the agent formulates queries at decision bifurcations.

### 2. Implement introspection as a shared aspect

A single file (`aspects/introspection.md`) defines the PRIME/JIT/LEARN protocol. Skills declare participation via metadata without implementing the protocol.

### 3. LEARN produces learning records — summary with pointers

LEARN produces a **flat structured summary** (~10 fields) that points to execution traces (git history, artifacts on disk, conversation transcript). The learning record indexes traces — it does not duplicate them. When the future `rai-skill-improve` needs raw traces, it reads git + artifacts. The record tells it *where to look* and *what was notable*.

Learning records form a **chain**: each skill reads the previous skill's learning record (informing its prime) and enriches earlier records with downstream impact (closing the feedback loop). Enrichment is **best-effort** — failure never blocks execution.

## Rationale

### Why deterministic prime (not LLM-refined)

| Approach | Pros | Cons |
|----------|------|------|
| Rigid template (original v1) | Reproducible, evaluable | May miss nuanced queries |
| LLM-refined (original v1 "guided") | Adaptable | Non-deterministic, harder to debug, bitter lesson misapplied to inner loop |
| **Deterministic + variable substitution (adopted v2)** | Reproducible, debuggeable, CC-aligned | Less adaptive for edge cases |

**Evidence:** CC (E1132 F14) loads all 6 tiers of CLAUDE.md deterministically. No LLM decides what context to load. MCE's skill evolution discovers improvements to queries via the outer loop — not by letting the inner loop guess.

### Why flat schema with pointers (not rich traces)

| Approach | Pros | Cons |
|----------|------|------|
| Rich nested YAML (original v1) | Self-contained | Over-engineered, duplicates git, 30+ fields |
| Votes only (+1/0/-1) | Minimal | MetaHarness -15 points without traces |
| **Flat summary + pointers (adopted v2)** | Lean, indexes existing traces | Requires reading git for raw data |

**Evidence:** MetaHarness shows traces > summaries for the outer loop. But git history and conversation transcripts already ARE the raw traces. The learning record's job is to index and annotate them, not duplicate them. CC's atom store (E1132 F8) manages all app state in 35 lines — complexity must earn its place.

### Why hard token limit (not target)

| Approach | Pros | Cons |
|----------|------|------|
| Soft target (original v1) | Flexible | No enforcement, creeps over time |
| **Hard limit with truncation (adopted v2)** | Predictable, CC-aligned | May lose some context |

**Evidence:** CC (E1132 F15) uses 92 compile-time + 53 runtime hardcoded limits. "Target" becomes "suggestion" becomes "ignored." Hard limit 1200 tokens with truncation strategy (drop fewest-match queries first) ensures predictable overhead.

### Why learning chain (not aggregated review)

| Approach | Pros | Cons |
|----------|------|------|
| Aggregate at story-review | Single collection point | Too late, loses attribution |
| Per-skill isolated | Simple | No downstream signal |
| **Chain (adopted)** | Natural flow, downstream attribution | Depends on execution order |

**Evidence:** Governed Memory (arxiv 2603.17787) identifies the diagnostic distinction between "recall failure" and "use failure." Only per-skill, immediate evaluation can make this distinction. Downstream enrichment is best-effort (E1132 F2: error isolation pattern).

### Why this enables self-improvement

The learning chain produces the exact data that self-improvement loops need:

| Paradigm | What it needs | Learning record provides |
|----------|--------------|------------------------|
| **MetaHarness** | Source code + scores + execution traces | Skill version + record + trace pointers (git, artifacts) |
| **MCE** | Skill directories + execution trajectories + metrics | Complete — records + git traces are MCE-compatible |
| **ACE** | Execution feedback for reflection | Pattern votes + gaps + downstream |
| **AutoResearch** | Single scalar metric + fast eval | Composite score derivable from record |

## Alternatives Considered

### A. Opt-out injection (RAISE-1009)
Inject graph context before every skill at runtime. Rejected: token bloat, no evaluation, no measurement.

### B. Context-only evolution (ACE-style)
Evolve patterns/context but not skills themselves. Rejected: MCE shows 16.9% improvement from evolving skills, not just context.

### C. Full MetaHarness outer loop now
Build automated skill improvement immediately. Deferred: need traces first.

### D. Separate observability epic
Build measurement infrastructure as a separate concern. Rejected: measurement-as-operation is simpler.

### E. LLM-refined priming (original v1)
Let the LLM reformulate Tier 1 queries. Revised: bitter lesson applies to outer loop, not inner loop. CC validates deterministic context assembly. JIT remains adaptive.

## Consequences

### Positive
- Every skill execution produces measurable data (learning record)
- Downstream attribution closes the feedback loop
- Learning records lean enough for any future self-improvement paradigm
- Skills generate informed by accumulated knowledge (prime + JIT)
- Deterministic PRIME is reproducible and debuggeable
- Hard limits prevent token creep
- Flat schema is easy to parse and extend

### Negative
- Each skill file needs modification (aspect reference + phase metadata)
- Deterministic PRIME may miss nuanced queries (mitigated by JIT)
- Downstream enrichment can fail silently (mitigated by best-effort + logging)

### Neutral
- RAISE-1009 subsumed — update to reference this ADR
- Story-review role simplifies
- Graph schema extended (additive, no breaking changes)

## Compliance

- Guardrail: Inference Economy — Tier 1 is deterministic CLI calls, Tier 2 bounded by metadata limits
- Guardrail: Simple First — flat schema, one aspect file, hard limits
- ADR-011: Graph queries remain concept-level
- ADR-036: Graph backend unchanged; records stored in filesystem

## Changes Log

| Version | Date | Changes |
|---------|------|---------|
| v1 | 2026-03-31 | Initial ADR — guided (LLM-refined) priming, rich nested schema |
| v2 | 2026-04-01 | CC SAR alignment: deterministic PRIME (B), hard token cap (D), flat schema (H), pointers not traces (E), best-effort enrichment (F) |

## References

- Research: `work/research/skill-memory-integration/`
- MetaHarness: arxiv 2603.28052
- MCE: arxiv 2601.21557
- ACE: arxiv 2510.04618
- Governed Memory: arxiv 2603.17787
- Self-Evolving Agents Survey: arxiv 2507.21046
- AutoResearch: github.com/karpathy/autoresearch
- Bitter Lesson: Sutton 2019
- Anthropic: Effective harnesses for long-running agents
- **E1132: Claude Code Architecture Reconstruction** — findings F2, F7, F8, F14, F15
