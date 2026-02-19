# RES-TEMPORAL-001: Temporal Decay and Pattern Scoring for Agent Memory

> **Date:** 2026-02-18
> **Status:** Complete
> **Authors:** Emilio Osorio + Rai
> **Method:** Standard research — 12 sources, triangulated claims
> **Informs:** RAISE-170 (story within RAISE-168: Neurosymbolic Memory Density)

---

## Executive Summary

Temporal decay and pattern scoring is a solved problem in the literature, with convergence on a small set of proven approaches. The dominant model is the **three-factor weighted score** (recency + importance + relevance) from Stanford's Generative Agents (2023), which has become the de facto baseline. For RaiSE's specific constraints — JSONL append-only store, no embedding infrastructure, NetworkX graph, ~200 patterns — the optimal approach is a **lightweight composite score computed at query time** with a configurable half-life decay and explicit exemption for foundational patterns.

**Key insight:** The literature splits into two camps — *active forgetting* (FadeMem, MemoryBank) vs *relevance-first retrieval* (Mem0, A-Mem). For small corpora (<500 items), relevance-first is sufficient. For growing corpora (our trajectory), adding temporal decay as a *retrieval bias* (not deletion) is the pragmatic middle ground.

---

## Research Questions & Findings

### RQ1: What decay functions does the literature use?

**Claim: Three decay models dominate, with exponential being the pragmatic choice.**
**Confidence: HIGH** (4 primary sources converge)

| Model | Formula | Used By | Pros | Cons |
|-------|---------|---------|------|------|
| **Exponential** | `R = e^(-λt)` | FadeMem, MemoryBank, Stanford, OpenClaw | Simple, tunable via λ, well-understood | Decays too aggressively for long-lived knowledge |
| **Power-law** | `B = ln(Σ t_j^-d)` | ACT-R | More accurate to human memory | Computationally heavier, requires access history |
| **Half-life** | `score = exp(-ln(2)/H * t)` | OpenClaw #5547 | Most intuitive parameter (H = "half-life in days") | Special case of exponential |

**Evidence:**
1. FadeMem (S1): Adaptive exponential `v(t) = v(0) * exp(-λ * (t-τ)^β)` — most sophisticated, but requires dual-layer architecture
2. ACT-R (S4): Power-law `B = ln(Σ t_j^-d)` with d=0.5 — gold standard in cognitive science, heavy for our case
3. Stanford Generative Agents (S3): Exponential decay with factor 0.995 per time unit — simplest, most adopted
4. OpenClaw (S8): Half-life formulation `exp(-ln(2)/H * age)` — most intuitive parameterization

**Disagreement:** Power-law vs exponential is a real debate. Power-law better models human memory (Anderson 1990), but exponential is "good enough" for engineering and far simpler to implement. FadeMem's β parameter (0.8 for LTM, 1.2 for STM) bridges the gap by allowing sub-exponential decay for important memories.

**RaiSE recommendation:** Half-life exponential. One parameter (H = days), intuitive for users, trivial to compute. H=30 days as default (pattern loses 50% score at 30 days).

### RQ2: What reinforcement signals improve scoring?

**Claim: Three signals are consistently used — recency, importance, and access frequency.**
**Confidence: HIGH** (5 sources converge)

| Signal | How Measured | Used By | Complexity |
|--------|-------------|---------|------------|
| **Recency** | Time since creation/last access | All systems | Zero (timestamp exists) |
| **Importance** | LLM-scored or manual | Stanford, FadeMem | Medium (needs scoring mechanism) |
| **Access frequency** | Count of retrievals | ACT-R, FadeMem, MemoryBank | Low (counter field) |
| **Semantic relevance** | Embedding cosine similarity | Stanford, A-Mem, Mem0 | High (needs embeddings) |
| **Reinforcement** | Explicit human/agent boost | MemoryBank | Zero (flag or counter) |

**Evidence:**
1. Stanford (S3): `score = α*recency + β*importance + γ*relevance` — all weights = 1, min-max normalized
2. FadeMem (S1): `I(t) = α*relevance + β*frequency/(1+frequency) + γ*exp(-δ*(t-τ))` — three-factor importance
3. ACT-R (S4): `B = ln(Σ t_j^-d)` — each access adds to activation sum
4. MemoryBank (S5): S (strength) = integer, +1 on each access, t resets to 0
5. OpenClaw (S8): `finalScore = (1-w)*hybridScore + w*recencyScore` — recency as weighted modifier

**RaiSE recommendation:** Two signals feasible now (recency + manual importance), one addable later (access frequency):
- **Recency**: Already have `created` field. Add `last_accessed` on query.
- **Importance**: Already have `foundational` flag (boolean). Extend to numeric (0-10) or use `base: true` as importance=10.
- **Access frequency**: Add `access_count` field, increment on retrieval. Cheap, defer to v2 if needed.
- **Semantic relevance**: Skip — requires embeddings, out of scope (epic explicitly excludes).

### RQ3: How to balance recency vs foundational permanence?

**Claim: Exemption mechanism for permanent memories is the universal pattern.**
**Confidence: HIGH** (3 sources + 1 practitioner)

| Approach | Used By | Mechanism |
|----------|---------|-----------|
| **Pinned/exempt** | OpenClaw (S8) | `pinnedPaths` config — exempt from decay |
| **Slow-decay layer** | FadeMem (S1) | LTM β=0.8 (sub-exponential) vs STM β=1.2 |
| **Importance floor** | Stanford (S3) | High importance score overrides low recency |
| **Foundational flag** | RaiSE (current) | `foundational: true` in metadata |

**Evidence:**
1. OpenClaw (S8): "pinnedPaths: Exempts key files from age penalties" — exact analog to our `foundational` flag
2. FadeMem (S1): Different decay shapes per layer — β<1 means sub-linear decay for important memories
3. Stanford (S3): Weighted sum means high importance compensates for low recency
4. RaiSE (S12): Already has `foundational: true` metadata on base patterns

**RaiSE recommendation:** Keep `foundational` flag as decay exemption. Foundational patterns get score = 1.0 always (no decay). This is the simplest and most robust approach, validated across multiple systems.

### RQ4: What pruning/archival thresholds prevent unbounded growth?

**Claim: Active pruning is recommended but not critical for small corpora (<500 items).**
**Confidence: MEDIUM** (3 sources, some disagreement)

| Strategy | Used By | Trigger |
|----------|---------|---------|
| **Score threshold** | FadeMem (S1) | Memory drops below θ_demote = 0.3 → archive |
| **Max age** | OpenClaw (S8) | `maxAgeDays` floor prevents extreme penalties |
| **Deduplication** | Mem0 (S6) | LLM-based semantic merge at write time |
| **No pruning** | A-Mem (S7), Mem0 | Rely on relevance retrieval to surface best |

**Evidence:**
1. FadeMem (S1): Dual threshold with hysteresis (θ_promote=0.7, θ_demote=0.3) — prevents oscillation
2. Mem0 (S6): No explicit deletion — "forgets" by not retrieving irrelevant. Works at scale with vector search.
3. A-Mem (S7): No forgetting — memories evolve, never deleted. Valid for factual knowledge that remains true.

**Disagreement:** Mem0 and A-Mem argue against active pruning, preferring retrieval filtering. FadeMem shows active pruning improves storage efficiency (55% vs 100%). The difference is corpus size — at 10K+ memories, pruning becomes necessary; at <500, retrieval filtering suffices.

**RaiSE recommendation:** Phase approach:
1. **Now (RAISE-170):** Score-based retrieval ordering only. No deletion. Low-scoring patterns simply rank lower.
2. **Later (parking lot):** When patterns.jsonl exceeds ~500 entries, add archival (move low-score patterns to `patterns-archive.jsonl`). Threshold: score < 0.1 AND not foundational AND age > 90 days.

---

## Synthesis: Composite Score Formula for RaiSE

Based on triangulated evidence, the recommended formula is:

```
score(pattern, query) =
    if pattern.foundational:
        keyword_relevance(pattern, query)  # no decay, always full weight
    else:
        w_r * recency(pattern) + w_k * keyword_relevance(pattern, query)
```

Where:
```
recency(p) = exp(-ln(2) / H * age_days(p))
    H = half_life_days (default: 30)
    age_days = (now - p.created).days

keyword_relevance(p, q) = keyword_hits / total_keywords
    (normalized to [0, 1])
```

Default weights: `w_r = 0.3, w_k = 0.7` (relevance dominates, recency modulates)

### Why This Formula

1. **Half-life exponential** (not raw exponential): One intuitive parameter. "A pattern loses half its recency score every 30 days." Users can tune H without understanding λ.
2. **Foundational exemption** (not slow-decay): Binary is simpler than continuous importance scoring. Our `foundational` flag already exists.
3. **Keyword relevance preserved as primary** (not replaced): Our query engine works. Decay should modulate, not replace.
4. **No access frequency yet**: Adds write-on-read complexity to JSONL. Defer until validated that recency alone is insufficient.
5. **No embeddings**: Explicitly out of epic scope. Keyword matching is our retrieval mechanism.

### Comparison to Current Implementation

| Aspect | Current | Proposed |
|--------|---------|----------|
| Recency | `+5` if created in "2026-02" (hardcoded!) | Continuous exponential decay |
| Keyword | `hits * 10` (raw count) | `hits / total` (normalized) |
| Foundational | Not considered in scoring | Exempt from decay |
| Score range | Unbounded integer | [0, 1] normalized |
| Configurability | None | H (half-life) configurable |

---

## Implementation Implications

### Data Model Changes

```python
# patterns.jsonl — no schema change needed for v1
# Existing fields sufficient: id, content, context, created, base

# Future addition (v2, if needed):
# "last_accessed": "2026-02-18"
# "access_count": 3
```

### Code Changes (Estimated)

| File | Change | Size |
|------|--------|------|
| `context/query.py` | Replace `calculate_relevance_score()` with composite scorer | M |
| `context/models.py` | Add `ScoringConfig` Pydantic model (half_life, weights) | S |
| `session/bundle.py` | Use scoring for behavioral prime ordering | S |
| Tests | Score calculation, decay curve, foundational exemption | M |

Estimated: S-M story (as scoped in epic)

### Configuration

```yaml
# .raise/manifest.yaml or similar
scoring:
  half_life_days: 30
  weights:
    recency: 0.3
    relevance: 0.7
  foundational_exempt: true
```

---

## Recommendation

**Decision:** Implement half-life exponential decay with foundational exemption as a retrieval-time score modifier in `calculate_relevance_score()`.

**Confidence:** HIGH

**Rationale:**
- Three-factor model (Stanford) is the gold standard, but we only need two factors (recency + relevance) given our constraints (no embeddings, <500 patterns)
- Half-life parameterization (OpenClaw) is the most intuitive
- Foundational exemption is validated across all systems that handle permanent knowledge
- Post-processing approach (score at query time, not at write time) matches our append-only JSONL architecture

**Trade-offs:**
- We accept keyword matching over semantic similarity (scope constraint)
- We accept no access frequency tracking in v1 (simplicity)
- We accept no active pruning in v1 (corpus size doesn't warrant it)

**Risks:**
- Half-life of 30 days may be too aggressive for process patterns that are referenced monthly → mitigated by making H configurable
- Normalization to [0,1] may lose granularity for keyword matching → mitigated by testing with real pattern corpus

---

## Quality Checklist

- [x] Research question is specific and falsifiable
- [x] 12 sources consulted (standard depth)
- [x] Evidence catalog created with levels
- [x] Major claims triangulated (3+ sources per RQ)
- [x] Confidence level explicitly stated
- [x] Contrary evidence acknowledged (power-law vs exponential, pruning vs no-pruning)
- [x] Recommendation is actionable
- [x] Governance linkage: informs RAISE-170 design

---

## References

- [Evidence Catalog](sources/evidence-catalog.md) — 12 sources with ratings
- [RES-MEMORY-002](../memory-systems/RES-MEMORY-002-research-report.md) — Foundation research (50+ sources)
- [FadeMem](https://arxiv.org/abs/2601.18642) — Biologically-inspired forgetting
- [Zep/Graphiti](https://arxiv.org/abs/2501.13956) — Bi-temporal knowledge graph
- [Stanford Generative Agents](https://dl.acm.org/doi/fullHtml/10.1145/3586183.3606763) — Three-factor retrieval
- [ACT-R Tutorial Unit 4](https://huxianyin.github.io/blog/2020/11/09/tutorialUnit4) — Base-level learning equation
- [MemoryBank](https://arxiv.org/abs/2305.10250) — Ebbinghaus curve for LLMs
- [Mem0](https://arxiv.org/abs/2504.19413) — Production memory architecture
- [A-Mem](https://arxiv.org/abs/2502.12110) — Agentic memory evolution
- [OpenClaw #5547](https://github.com/openclaw/openclaw/issues/5547) — Pragmatic half-life decay
- [Memory in the Age of AI Agents](https://arxiv.org/abs/2512.13564) — Survey paper
- [Agent Memory Paper List](https://github.com/Shichun-Liu/Agent-Memory-Paper-List) — Comprehensive bibliography

---

*Research completed 2026-02-18. This document informs the design of RAISE-170.*
