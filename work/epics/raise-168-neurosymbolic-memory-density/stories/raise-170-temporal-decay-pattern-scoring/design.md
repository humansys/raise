---
id: RAISE-170
epic: RAISE-168
title: Temporal Decay and Pattern Scoring
size: M
status: design-complete
research: work/research/temporal-decay-pattern-scoring/RES-TEMPORAL-001-report.md
date: 2026-02-19
---

# Design: RAISE-170 — Temporal Decay and Pattern Scoring

## Problem & Value

All 378 patterns have equal weight regardless of age, validation history, or relevance quality.
The current scorer is a placeholder: `(hits * 10) + 5 if "2026-02" in created else 0` — literally
hardcoded to a month. Patterns from January 2026 already score 0 recency bonus.

**Value:** Higher-scored patterns surface first in queries and context bundles, making every session
more accurate. Patterns that are validated by implementation get rewarded; contradicted ones rank lower.

## Approach

**IMPORTANT:** This is grounded in RES-TEMPORAL-001 (20 sources, Stanford Generative Agents baseline).

### Composite Score Formula

```
score(pattern, query) =
    if pattern.foundational:
        keyword_relevance(pattern, query)   # no decay — always full weight
    else:
        base = w_r * recency(p) + w_k * keyword_relevance(p, query)
        base * validation_modifier(p)
```

Where:

```python
# Half-life exponential decay (RQ1 recommendation: H=30d default)
recency(p) = exp(-ln(2) / H * age_days(p))
    H = half_life_days (default: 30)
    age_days = (date.today() - p.created).days

# Normalized keyword relevance (replaces raw hit count * 10)
keyword_relevance(p, q) = keyword_hits / max(len(keywords), 1)

# Wilson score lower bound (RQ5: proven at Reddit/Yelp/Amazon scale)
# Handles small samples correctly — conservative with few evaluations
validation_modifier(p) =
    if p.evaluations == 0:
        1.0   # neutral — never evaluated, no penalty or boost
    else:
        wilson_lower_bound(p.positives, p.negatives, z=1.96)

wilson(pos, neg):
    n = pos + neg
    p̂ = pos / n
    z = 1.96
    return (p̂ + z²/2n - z * √((p̂*(1-p̂) + z²/4n) / n)) / (1 + z²/n)

# Default weights (relevance dominates, recency modulates)
w_r = 0.3, w_k = 0.7
```

### Reinforcement Signal (RQ6)

Signal is collected at `/story-review` — the natural evaluation point in the lifecycle.
Rai auto-evaluates patterns that were loaded at story-start:

```
+1 = implementation followed the pattern (applied)
 0 = pattern not relevant to this story (N/A — not counted in Wilson)
-1 = implementation contradicted the pattern
```

**DO NOT** add `+1/0/-1` prompts during implementation. Only at story-review.

### Components Affected

| File | Change |
|------|--------|
| `src/rai_cli/context/query.py` | Replace `calculate_relevance_score()` with composite scorer |
| `src/rai_cli/memory/writer.py` | Add `reinforce_pattern()` function + `PatternReinforcement` model |
| `src/rai_cli/cli/commands/memory.py` | Add `rai memory reinforce` command |
| `src/rai_cli/memory/loader.py` | Load new reinforcement fields from JSONL |
| `.claude/skills/rai-story-review` | Add pattern evaluation step |
| `tests/context/test_query.py` | New: decay, wilson, foundational exemption |
| `tests/memory/test_writer.py` | New: reinforce_pattern() |
| `tests/cli/test_memory.py` | New: reinforce command |

## Data Model

### patterns.jsonl — new fields (backward compatible)

```json
{
  "id": "PAT-E-183",
  "content": "Grounding over speed for foundational infrastructure",
  "context": ["architecture", "infrastructure"],
  "created": "2026-02-08",
  "base": true,
  "positives": 3,
  "negatives": 0,
  "evaluations": 4,
  "last_evaluated": "2026-02-19"
}
```

**Missing fields default to 0 / null.** Existing patterns.jsonl is valid without migration.

Note: `base: true` in JSONL corresponds to `foundational` exemption in scoring.
The field is already loaded as `metadata["base"]` in `loader.py`.

## Examples

### Score Calculation

```python
# query.py — after this story
from math import exp, log, sqrt

H = 30  # half-life days
w_r, w_k = 0.3, 0.7

def calculate_relevance_score(
    content: str,
    keywords: list[str],
    created: str,
    metadata: dict[str, Any],
) -> float:
    # Foundational patterns: no decay
    if metadata.get("base"):
        hits = sum(1 for kw in keywords if kw.lower() in content.lower())
        return hits / max(len(keywords), 1)

    # Recency component
    from datetime import date
    try:
        created_date = date.fromisoformat(created[:10])
        age_days = (date.today() - created_date).days
    except ValueError:
        age_days = 0
    recency = exp(-log(2) / H * age_days)

    # Keyword relevance (normalized)
    hits = sum(1 for kw in keywords if kw.lower() in content.lower())
    relevance = hits / max(len(keywords), 1)

    base = w_r * recency + w_k * relevance

    # Wilson validation modifier
    evaluations = metadata.get("evaluations", 0)
    if evaluations == 0:
        return round(base, 4)

    positives = metadata.get("positives", 0)
    negatives = metadata.get("negatives", 0)
    modifier = _wilson_lower_bound(positives, negatives)
    return round(base * modifier, 4)
```

### CLI Reinforcement

```bash
# At story-review — Rai evaluates patterns loaded at story-start
rai memory reinforce PAT-E-183 +1 --from RAISE-170   # applied
rai memory reinforce PAT-E-151  0 --from RAISE-170   # N/A (no update)
rai memory reinforce PAT-E-094 -1 --from RAISE-170   # contradicted

# Output
✓ PAT-E-183: positives=4, evaluations=5, wilson≈0.52
✓ PAT-E-094: negatives=1, evaluations=1, wilson≈0.03 ↓ consider reviewing
```

### Score Examples (concrete)

```
PAT-E-001 (created 2026-01-31, 19 days old, 0 evaluations, 2/3 kw hits):
    recency = exp(-ln(2)/30 * 19) = 0.642
    relevance = 2/3 = 0.667
    base = 0.3 * 0.642 + 0.7 * 0.667 = 0.659
    modifier = 1.0 (no evaluations)
    score = 0.659

PAT-E-183 (base=true, 2/3 kw hits):
    foundational → score = 2/3 = 0.667 (no decay)

PAT-E-094 (90 days old, 10 evaluations: 3 pos / 7 neg, 2/3 kw hits):
    recency = exp(-ln(2)/30 * 90) = 0.125
    relevance = 2/3 = 0.667
    base = 0.3 * 0.125 + 0.7 * 0.667 = 0.505
    wilson(3, 7) ≈ 0.10
    score = 0.505 * 0.10 = 0.050  ← ranked very low, signal to review
```

## Acceptance Criteria

**MUST:**
- [ ] `calculate_relevance_score()` uses half-life exponential decay (H=30, configurable via `SCORING_HALF_LIFE_DAYS` env var or default constant)
- [ ] `base: true` patterns are exempt from decay (score = keyword_relevance only)
- [ ] `rai memory reinforce PAT-E-XXX +1|0|-1 --from STORY-ID` updates JSONL and prints summary
- [ ] Patterns with `evaluations == 0` get `validation_modifier = 1.0` (no penalty for new patterns)
- [ ] Query results are ordered by composite score descending
- [ ] `0` vote (N/A) does NOT increment `evaluations` or `positives`/`negatives`
- [ ] All tests pass, coverage ≥ 90%, pyright + ruff pass

**SHOULD:**
- [ ] `/story-review` skill includes auto-evaluation step with `rai memory reinforce` calls
- [ ] `rai memory reinforce` output flags patterns with low Wilson score (< 0.15) for review

**MUST NOT:**
- [ ] Remove or break the `concept_lookup` strategy (RAISE-166 feature)
- [ ] Modify patterns.jsonl schema in a backward-incompatible way
- [ ] Add active deletion or archival of patterns (deferred to parking lot)

## Configuration

```python
# constants in query.py (no external config needed for v1)
SCORING_HALF_LIFE_DAYS: int = 30
SCORING_W_RECENCY: float = 0.3
SCORING_W_RELEVANCE: float = 0.7
SCORING_WILSON_Z: float = 1.96
SCORING_LOW_WILSON_THRESHOLD: float = 0.15  # flag for review
```

## Out of Scope (explicit)

- Pattern deletion or archival (deferred — score < 0.1 threshold, parking lot)
- Access frequency tracking (`reference_count`) — defer, adds write-on-read complexity
- Semantic similarity / embeddings — out of epic scope (RAISE-168 explicitly excludes)
- `rai memory health` dashboard command — deferred to RAISE-171 or new story
- Bi-temporal model (Zep-style) — out of epic scope
