# RES-TEMPORAL-001: Temporal Decay and Pattern Scoring for Agent Memory

> **Date:** 2026-02-18
> **Status:** Complete
> **Authors:** Emilio Osorio + Rai
> **Method:** Standard research — 20 sources, triangulated claims
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

## Part 2: Reinforcement Scoring via Implicit HITL Validation

### The Insight

In RaiSE's workflow, HITL already happens at every significant step. When Rai proposes patterns at story-start and the human approves implementation that either follows or contradicts those patterns, that's an **implicit vote** on the pattern's validity. No extra ceremony needed — the signal is already in the workflow.

This is analogous to Reddit's voting system, but instead of explicit upvotes/downvotes, the votes are derived from **observed implementation outcomes**.

### RQ5: What algorithms handle +1/0/-1 scoring with small sample sizes?

**Claim: Wilson score lower bound is the optimal algorithm for this use case.**
**Confidence: HIGH** (4 sources converge, proven at Reddit/Yelp/Amazon scale)

| Algorithm | Formula | Handles Small N? | Complexity | Best For |
|-----------|---------|-----------------|------------|----------|
| **Wilson score** | `(p̂+z²/2n - z√((p̂(1-p̂)+z²/4n)/n)) / (1+z²/n)` | Yes (core strength) | Low | Binary outcomes, few observations |
| **Bayesian average** | `(C*m + Σvotes) / (C + n)` | Yes (via prior C) | Low | Star ratings, configurable prior |
| **TrueSkill** | μ - k*σ (Gaussian updates) | Yes (explicit σ) | Medium | When uncertainty matters |
| **SM-2 ease factor** | `EF' = EF + (0.1-(5-q)*(0.08+(5-q)*0.02))` | No (no sample size) | Low | Fixed-interval scheduling |
| **FSRS** | 21-parameter DSR model | Overkill | High | Millions of cards |

**Evidence:**
1. Wilson score (S13): Used by Reddit for comment ranking. "Given the ratings I have, there is a 95% chance that the real fraction of positive ratings is at least what?" Handles 1 vote vs 1000 votes correctly.
2. Reddit hot ranking (S14): Demonstrates vote + time combination in production at massive scale.
3. TrueSkill (S17): More sophisticated (tracks uncertainty explicitly) but adds Gaussian math we don't need for ~200 patterns.
4. SM-2 (S15): Proven for spaced repetition but doesn't handle sample size — a pattern with 1 evaluation and 1000 evaluations are treated the same.

**Disagreement:** TrueSkill's explicit uncertainty tracking (σ shrinks with observations) is theoretically superior to Wilson's confidence interval approach. However, Wilson is simpler, well-proven, and sufficient for our corpus size. TrueSkill would matter at 10K+ items.

**RaiSE recommendation:** Wilson score lower bound. One formula, handles small samples, proven at scale, trivial to implement.

### RQ6: How to derive the +1/0/-1 signal from HITL workflow?

**Claim: Post-implementation comparison in /story-review is the natural evaluation point.**
**Confidence: HIGH** (logical derivation from existing workflow + S19 precedent)

The signal extraction works because RaiSE's lifecycle already produces the necessary data:

```
Story lifecycle data flow:

1. /story-start → Rai loads relevant patterns → RECORD which patterns were loaded
2. /story-implement → Human approves each task (HITL) → CODE is written
3. /story-review → Rai has both: loaded patterns + actual implementation

   For each loaded pattern:
     - Compare pattern guidance vs actual code/decisions
     - Did implementation follow the pattern? → +1 (applied)
     - Was pattern irrelevant to this story? → 0 (not applicable)
     - Did implementation contradict the pattern? → -1 (contradicted)
```

**Evidence:**
1. Stanford Generative Agents (S19): LLM rates memory importance 1-10. Same approach: LLM evaluates pattern applicability.
2. Agentic RL implicit rewards (S20): Outcome-level reward inferred from agent actions, not explicit labels.
3. RLHF general framework: Human preferences derived from choosing between outputs. Our variant: human choosing an implementation that follows/contradicts a pattern.

**Key distinction from Reddit:** In Reddit, users explicitly vote. In our system, the vote is **inferred from behavior** — if you approve code that contradicts a pattern, that's an implicit -1. This is more like implicit feedback in recommender systems (S18) than explicit voting.

### RQ7: How should reinforcement combine with temporal decay?

**Claim: Multiplicative combination is better than additive for this use case.**
**Confidence: MEDIUM** (logical argument, limited direct precedent)

Two options:

**Option A — Additive (Reddit-style):**
```
final_score = w_t * temporal_decay + w_r * relevance + w_v * validation_score
```
Problem: A pattern can score high from relevance alone even if it's been contradicted multiple times.

**Option B — Multiplicative (recommended):**
```
final_score = temporal_decay * relevance * validation_modifier

where:
  validation_modifier = wilson_lower_bound(positives, negatives)
                        if evaluations > 0
                      = 1.0  (neutral)
                        if never evaluated
```
Advantage: A contradicted pattern (low Wilson score) pulls the entire score down regardless of relevance. A validated pattern gets a boost. An unevaluated pattern is neutral (modifier = 1.0).

**Evidence:**
1. Reddit hot ranking (S14) uses additive (log(votes) + time), but Reddit items don't have a "validity" dimension.
2. FSRS (S16) uses multiplicative interactions between D, S, R — precedent for multiplicative combination of independent memory properties.
3. FadeMem (S1) uses multiplicative: `I(t) = α*rel + β*freq + γ*recency` but decay is applied multiplicatively to the base strength.

### The Validation Signal Semantics

| Signal | Meaning | Wilson Input | Example |
|--------|---------|-------------|---------|
| **+1** (applied) | Implementation followed pattern guidance | positive vote | "TDD always" → tests written first |
| **0** (N/A) | Pattern was loaded but not relevant to this story | skip (not counted) | "Renames have long tail" loaded for a new feature story |
| **-1** (contradicted) | Implementation actively went against pattern | negative vote | "Simple first" → complex abstraction chosen |

**Critical: -1 is not "bad"**

A -1 doesn't mean the pattern is wrong. It means:
- The context changed and the pattern doesn't apply universally
- The pattern was correctly overridden for good reasons
- OR the pattern is genuinely wrong and should be deprecated

The human should see patterns trending negative and decide: update the pattern, add context constraints, or deprecate it.

### Wilson Score for Patterns — Concrete Example

```
Pattern: PAT-E-183 "Grounding over speed"
  Applied in: RAISE-165, RAISE-169, RAISE-170 (+3)
  Contradicted in: (none)

  Wilson lower bound (z=1.96):
    p̂ = 3/3 = 1.0, n = 3
    score = (1.0 + 1.92/6 - 1.96*√((1.0*0+0.96/12)/3)) / (1 + 3.84/3)
    score ≈ 0.44

  Note: Only 0.44 despite 100% positive — Wilson is conservative
  with small samples. After 10 positive evaluations: ~0.74.
  After 30: ~0.88. Confidence grows with data.

Pattern: PAT-E-094 "Velocity compounds across epics"
  Applied in: RAISE-166 (+1)
  Contradicted in: RAISE-171, RAISE-172 (-2)

  Wilson lower bound:
    p̂ = 1/3 = 0.33, n = 3
    score ≈ 0.06

  This pattern would rank very low — signal to review it.
```

---

## Synthesis: Composite Score Formula for RaiSE

Based on triangulated evidence from 20 sources, the recommended formula is:

```
score(pattern, query) =
    if pattern.foundational:
        keyword_relevance(pattern, query)  # no decay, always full weight
    else:
        base = w_r * recency(pattern) + w_k * keyword_relevance(pattern, query)
        base * validation_modifier(pattern)
```

Where:
```
recency(p) = exp(-ln(2) / H * age_days(p))
    H = half_life_days (default: 30)
    age_days = (now - p.created).days

keyword_relevance(p, q) = keyword_hits / total_keywords
    (normalized to [0, 1])

validation_modifier(p) =
    if p.evaluations == 0:
        1.0  # neutral — never evaluated, no penalty or boost
    else:
        wilson_lower_bound(p.positives, p.negatives, z=1.96)
        # range [0, 1], conservative with small samples
```

Wilson lower bound formula:
```
wilson(pos, neg) =
    n = pos + neg
    p̂ = pos / n
    z = 1.96  # 95% confidence
    (p̂ + z²/2n - z * √((p̂*(1-p̂) + z²/4n) / n)) / (1 + z²/n)
```

Default weights: `w_r = 0.3, w_k = 0.7` (relevance dominates, recency modulates)

### Why This Formula

1. **Half-life exponential** (not raw exponential): One intuitive parameter. "A pattern loses half its recency score every 30 days." Users can tune H without understanding λ.
2. **Foundational exemption** (not slow-decay): Binary is simpler than continuous importance scoring. Our `foundational` flag already exists.
3. **Wilson score as multiplicative modifier** (not additive): A contradicted pattern can't compensate with high relevance. A validated pattern gets a boost. An unevaluated pattern is unaffected.
4. **Wilson handles small samples**: A pattern with 1 evaluation isn't over-penalized or over-rewarded. Confidence grows naturally with data.
5. **Keyword relevance preserved as primary** (not replaced): Our query engine works. Decay and validation should modulate, not replace.
6. **No access frequency yet**: Adds write-on-read complexity to JSONL. Defer until validated that recency + validation is insufficient.
7. **No embeddings**: Explicitly out of epic scope. Keyword matching is our retrieval mechanism.

### The "Reddit for Patterns" Analogy

| Reddit | RaiSE Patterns |
|--------|---------------|
| Upvote | Pattern applied in implementation (+1) |
| Downvote | Pattern contradicted in implementation (-1) |
| No vote | Pattern not relevant to story (0, not counted) |
| Wilson lower bound | Same formula — conservative with few votes |
| Hot = votes + time | Score = (relevance + recency) * validation |
| Pinned post | Foundational pattern (exempt from decay) |

### Comparison to Current Implementation

| Aspect | Current | Proposed |
|--------|---------|----------|
| Recency | `+5` if created in "2026-02" (hardcoded!) | Continuous exponential decay |
| Keyword | `hits * 10` (raw count) | `hits / total` (normalized) |
| Foundational | Not considered in scoring | Exempt from decay |
| Validation | None | Wilson score from implicit HITL |
| Score range | Unbounded integer | [0, 1] normalized |
| Configurability | None | H (half-life), z (confidence) |

### Signal Collection Point

```
/story-review (existing step in lifecycle)
    ↓
Rai auto-evaluates for each pattern loaded at story-start:
    +1  = implementation followed pattern
     0  = pattern not relevant (skip, don't count)
    -1  = implementation contradicted pattern
    ↓
rai memory reinforce PAT-E-183 +1 --from RAISE-170
rai memory reinforce PAT-E-151  0 --from RAISE-170
    ↓
patterns.jsonl updated: positives++, negatives++, evaluations++
```

### Pattern Health Dashboard (Future)

Patterns trending negative become visible:
```
$ rai memory health patterns

Pattern                          Evals  +   -   Wilson  Trend
PAT-E-183 Grounding over speed     12  11   1   0.64    ↑ stable
PAT-E-094 Velocity compounds        5   2   3   0.09    ↓ review needed
PAT-E-151 Renames long tail         8   7   1   0.53    ↑ stable
PAT-E-042 [deprecated by data]      6   0   6   0.00    ✗ deprecate?
```

---

## Implementation Implications

### Data Model Changes

```python
# patterns.jsonl — minimal additions for reinforcement tracking
{
    "id": "PAT-E-183",
    "content": "Grounding over speed for foundational infrastructure",
    "context": ["architecture", "infrastructure"],
    "created": "2026-02-18",
    "base": true,
    # NEW fields for reinforcement:
    "positives": 3,        # times applied (+1)
    "negatives": 0,        # times contradicted (-1)
    "evaluations": 4,      # total evaluations (positives + negatives, excludes 0s)
    "last_evaluated": "2026-02-18"  # most recent evaluation date
}
```

Backward compatible: missing fields default to 0. Existing patterns.jsonl unaffected until first evaluation.

### Code Changes (Estimated)

| File | Change | Size |
|------|--------|------|
| `context/query.py` | Replace `calculate_relevance_score()` with composite scorer | M |
| `context/models.py` | Add `ScoringConfig` Pydantic model (half_life, weights, z) | S |
| `memory/writer.py` | Add `reinforce_pattern()` function (+1/0/-1 update) | S |
| `memory/models.py` | Add reinforcement fields to pattern model | XS |
| `cli/commands/memory.py` | Add `rai memory reinforce` CLI command | S |
| `session/bundle.py` | Use scoring for behavioral prime ordering | S |
| Skill: story-review | Add pattern evaluation step (auto-eval) | S |
| Tests | Score calc, decay, Wilson, foundational exemption, reinforcement | M |

Estimated: M story (with skill integration)

### Configuration

```yaml
# .raise/manifest.yaml or similar
scoring:
  half_life_days: 30
  weights:
    recency: 0.3
    relevance: 0.7
  wilson_z: 1.96          # 95% confidence (rarely needs changing)
  foundational_exempt: true
  min_evaluations: 0       # Wilson applies from first evaluation
```

---

## Recommendation

**Decision:** Implement a three-layer composite score: half-life temporal decay + keyword relevance + Wilson score validation modifier. Signal collection via auto-evaluation in `/story-review`.

**Confidence:** HIGH

**Rationale:**
- Three-factor model (Stanford) is the gold standard. We implement all three factors but adapted to our constraints:
  - Recency = half-life exponential (not LLM-scored importance)
  - Relevance = keyword matching (not embedding cosine similarity)
  - Validation = Wilson score from implicit HITL (not explicit user rating)
- Wilson score (Reddit) handles small sample sizes — critical because most patterns will have <10 evaluations
- Multiplicative combination ensures contradicted patterns rank low regardless of relevance
- Signal collection is free — it's implicit in the HITL workflow that already exists
- Foundational exemption is validated across all systems that handle permanent knowledge

**Trade-offs:**
- We accept keyword matching over semantic similarity (scope constraint)
- We accept no access frequency tracking in v1 (simplicity)
- We accept no active pruning in v1 (corpus size doesn't warrant it)
- Wilson score is conservative with few evaluations — a pattern needs ~10+ votes to have a strong effect. This is a feature, not a bug.

**Risks:**
- Half-life of 30 days may be too aggressive for process patterns referenced monthly → mitigated by making H configurable
- Rai's auto-evaluation of +1/0/-1 may be inaccurate → mitigated by the human seeing evaluations in story-review (can correct)
- Normalization to [0,1] may lose granularity for keyword matching → mitigated by testing with real pattern corpus
- Patterns with only -1 evaluations get Wilson ≈ 0, which with multiplicative combination makes them invisible → this is intentional, but should flag for human review rather than silently disappear

---

## Quality Checklist

- [x] Research question is specific and falsifiable
- [x] 20 sources consulted (standard depth + reinforcement extension)
- [x] Evidence catalogs created with levels (2 files)
- [x] Major claims triangulated (3+ sources per RQ, 7 RQs)
- [x] Confidence level explicitly stated
- [x] Contrary evidence acknowledged (power-law vs exponential, pruning vs no-pruning, Wilson vs TrueSkill)
- [x] Recommendation is actionable
- [x] Governance linkage: informs RAISE-170 design

---

## References

### Evidence Catalogs
- [Temporal Decay Catalog](sources/evidence-catalog.md) — 12 sources (S1-S12)
- [Reinforcement Scoring Catalog](sources/evidence-catalog-reinforcement.md) — 8 sources (S13-S20)
- [RES-MEMORY-002](../memory-systems/RES-MEMORY-002-research-report.md) — Foundation research (50+ sources)

### Key Sources — Temporal Decay
- [FadeMem](https://arxiv.org/abs/2601.18642) — Biologically-inspired forgetting (S1)
- [Zep/Graphiti](https://arxiv.org/abs/2501.13956) — Bi-temporal knowledge graph (S2)
- [Stanford Generative Agents](https://dl.acm.org/doi/fullHtml/10.1145/3586183.3606763) — Three-factor retrieval (S3)
- [ACT-R Tutorial Unit 4](https://huxianyin.github.io/blog/2020/11/09/tutorialUnit4) — Base-level learning equation (S4)
- [MemoryBank](https://arxiv.org/abs/2305.10250) — Ebbinghaus curve for LLMs (S5)
- [Mem0](https://arxiv.org/abs/2504.19413) — Production memory architecture (S6)
- [A-Mem](https://arxiv.org/abs/2502.12110) — Agentic memory evolution (S7)
- [OpenClaw #5547](https://github.com/openclaw/openclaw/issues/5547) — Pragmatic half-life decay (S8)

### Key Sources — Reinforcement Scoring
- [Wilson Score — Evan Miller](https://www.evanmiller.org/how-not-to-sort-by-average-rating.html) — "How Not To Sort By Average Rating" (S13)
- [Reddit Ranking Algorithms](https://medium.com/hacking-and-gonzo/how-reddit-ranking-algorithms-work-ef111e33d0d9) — Hot, Best, Controversial (S14)
- [SM-2 Algorithm](https://tegaru.app/en/blog/sm2-algorithm-explained) — Spaced repetition with quality ratings (S15)
- [FSRS Algorithm](https://github.com/open-spaced-repetition/fsrs4anki/wiki/The-Algorithm) — State of the art spaced repetition (S16)
- [TrueSkill](https://trueskill.org/) — Bayesian skill estimation (S17)
- [Agentic RL Implicit Rewards](https://arxiv.org/abs/2509.19199) — Credit assignment from implicit signals (S20)

### Surveys
- [Memory in the Age of AI Agents](https://arxiv.org/abs/2512.13564) — Survey paper
- [Agent Memory Paper List](https://github.com/Shichun-Liu/Agent-Memory-Paper-List) — Comprehensive bibliography

---

*Research completed 2026-02-18. This document informs the design of RAISE-170.*
