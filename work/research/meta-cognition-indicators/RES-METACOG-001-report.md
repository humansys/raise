# RES-METACOG-001: Meta-Cognition Indicators for Agent Memory

> **Date:** 2026-02-19
> **Status:** Complete
> **Authors:** Emilio Osorio + Rai
> **Method:** Standard research — 12 sources, triangulated claims
> **Informs:** RAISE-171 (story within RAISE-168: Neurosymbolic Memory Density)

---

## Executive Summary

Meta-cognition for AI agents — "knowing what you know and what you don't" — is an active research frontier with a critical finding: **LLMs are unreliable at self-assessing their knowledge** (Nature Communications 2024, Steyvers 2025). The models tend to be overconfident and fail to recognize knowledge boundaries.

For RaiSE, this means meta-cognition must be **structural and deterministic, not LLM-introspective**. We have a knowledge graph with 19 node types and a known schema. We can measure coverage, density, and gaps against expectations — no LLM self-assessment needed.

The recommended approach has three layers:

1. **Coverage analysis** — Schema completeness: does the graph have all expected node types and minimum populations?
2. **Confidence scoring** — Edge density and structural connectivity as proxy for knowledge depth per topic.
3. **Gap detection** — Competency questions: can the graph answer specific questions about a module/story/epic? If not, that's a gap.

---

## Research Questions & Findings

### RQ1: How should an AI agent assess its own knowledge coverage?

**Claim: Structural measurement beats LLM introspection for knowledge coverage.**
**Confidence: HIGH** (4 sources converge, 2 with strong evidence against LLM self-assessment)

| Approach | Used By | Reliability | Our Feasibility |
|----------|---------|------------|-----------------|
| **Schema completeness** (expected vs actual types) | KG quality research (S4, S11) | Very High (deterministic) | Trivial — we have 19 types |
| **Population thresholds** (min nodes per type) | KG quality research (S4) | High (configurable) | Trivial — count nodes |
| **Competency questions** (can KG answer X?) | Ontology engineering (S5) | Very High (domain-grounded) | Medium — need to define CQs |
| **LLM self-assessment** (verbalized confidence) | AutoMeco (S1), MeCo (S9) | Low-Medium (overconfident) | Easy but unreliable |
| **Internal state probing** (logits, entropy) | AutoMeco (S1) | Medium-High | Impossible (API, no logit access) |

**Evidence:**
1. Nature Communications (S7): "Models consistently fail to recognize knowledge limitations, providing confident answers even when correct options were absent." → LLM introspection is unreliable.
2. Steyvers & Peters (S6): "LLMs and humans both tend to exhibit overconfidence." → Calibration is the key challenge; raw confidence is not trustworthy.
3. KG Quality Survey (S4): "Completeness = schema completeness (all properties) + population completeness (all instances)." → Structural measurement is deterministic and reliable.
4. Competency Questions (S5): "If a CQ can't be answered, that's a gap." → Domain-grounded gap detection.

**RaiSE recommendation:** Three-tier structural assessment:

**Tier 1 — Schema Completeness (always-on, deterministic):**
```
For each of the 19 node types:
  - Present? (boolean)
  - Count >= minimum threshold? (configurable)
  - Coverage ratio = present_types / expected_types
```

**Tier 2 — Population Health (always-on, deterministic):**
```
For each node type:
  - Count vs expected range [min, healthy, max_useful]
  - Staleness = age of newest node (stale if > N days)
  - Orphan rate = nodes with 0 structural edges / total nodes
```

**Tier 3 — Competency Questions (on-demand, per-context):**
```
For a given module/story/epic, can the graph answer:
  - "What patterns apply to {module}?" → pattern→module edges
  - "What decisions constrain {layer}?" → decision→layer edges
  - "What guardrails govern {bounded_context}?" → constrained_by edges

If answer is empty → gap detected
```

### RQ2: What confidence indicators are appropriate for a knowledge graph?

**Claim: Edge density and structural connectivity are better confidence proxies than LLM-generated scores.**
**Confidence: HIGH** (3 sources + internal analysis)

| Indicator | What It Measures | Formula | Interpretation |
|-----------|-----------------|---------|----------------|
| **Structural edge ratio** | How much of the graph is "real" vs keyword noise | `structural_edges / total_edges` | Higher = more meaningful connections |
| **Module coverage depth** | How well-documented a module is | `edges_to_module / expected_edge_types` | 0 = unknown, 1.0 = fully connected |
| **Pattern validation ratio** | Patterns validated by Wilson score (from RES-TEMPORAL-001) | `evaluated_patterns / total_patterns` | Higher = more validated knowledge |
| **Session recency** | How fresh the episodic memory is | `days_since_last_session` | Lower = more current context |
| **Cross-type connectivity** | How many node types are connected to each other | `connected_type_pairs / possible_type_pairs` | Higher = richer semantic network |

**Evidence:**
1. RaiSE graph analysis (S12): 97.7% of edges are keyword-heuristic `related_to`. Only 383 edges are structural. The structural edge ratio (383/16,884 = 2.3%) is a stark indicator that the graph's apparent richness is mostly noise.
2. Hindsight (S2): Separates facts from opinions with confidence scores. Our analog: separate structural edges (high confidence) from keyword heuristic edges (low confidence).
3. KG Quality Survey (S4): "Accuracy, completeness, consistency" as quality dimensions. Our edge types map to these: `depends_on` = structural accuracy, `part_of` = completeness, absence of cycles = consistency.

**RaiSE recommendation:** Report three confidence indicators:

```
Graph Confidence Report:
  Structural density:  2.3%  (383 real edges / 16,884 total)  ← low
  Schema coverage:     89%   (17/19 types present)             ← good
  Pattern validation:  0%    (0/326 patterns evaluated)        ← none yet
```

### RQ3: How should gap detection work in practice?

**Claim: Gaps are most useful when tied to the current task context, not reported globally.**
**Confidence: MEDIUM** (logical derivation + S5, S9 precedent)

Global gap reports ("your graph is missing X") are noisy. Task-contextual gaps ("for this story about the memory module, you're missing pattern coverage") are actionable.

**Evidence:**
1. MeCo (S9): Metacognitive trigger asks "Do I know enough for THIS query?" — task-specific, not global.
2. Competency Questions (S5): CQs are scoped to a domain question, not "is the ontology complete in general?"
3. SAGE (S3): Reflection generates self-assessments relative to current task performance, not global knowledge audit.

**RaiSE recommendation:** Two modes:

**Mode 1 — Session-start health check (global, fast):**
```
$ rai memory health

Graph Health: 1,244 nodes, 16,884 edges
  Schema:     17/19 types (missing: release dates stale)
  Staleness:  Sessions fresh (last: 2d ago)
              Patterns fresh (last: 1d ago)
              Components stale (last scan: 30d ago) ⚠️
  Density:    2.3% structural (383/16,884)
  Validation: 0/326 patterns evaluated

Recommendation: Run `rai discover scan` to refresh components.
```

**Mode 2 — Story-start context check (scoped, deep):**
```
$ rai memory gaps --module mod-memory

Module: mod-memory (Memory System)
  Patterns mentioning memory:  23 found ✓
  Decisions constraining memory: 3 ADRs ✓
  Guardrails for memory code: 2 found ✓
  Dependencies documented: 2 (context, cli) ✓
  Components discovered: 45 ✓

  Gaps:
  - No `constrained_by` edges from guardrails → mod-memory
  - Calibration data: 0 entries for memory module

  Coverage: 83% (5/6 dimensions present)
```

### RQ4: What should the meta-cognition output format look like?

**Claim: Compact, actionable indicators beat verbose reports.**
**Confidence: HIGH** (consistent with RES-MEMORY-002 finding on density + our Ri-level communication)

Based on our existing compact format work (RAISE-166) and the session-start skill's manifest approach (RAISE-169):

**For session-start integration (always-on):**
```
# Graph Health
coverage: 89% (17/19 types) | density: 2.3% structural | stale: components (30d)
```
One line. Enough for Rai to flag if something needs attention.

**For `rai memory health` (on-demand detail):**
```
## Graph Health Report

| Dimension | Status | Detail |
|-----------|--------|--------|
| Schema | 89% | Missing: release (stale) |
| Population | ✓ | All types above minimum |
| Staleness | ⚠️ | Components: 30d since last scan |
| Structural density | 2.3% | 383 real / 16,884 total edges |
| Pattern validation | 0% | 0/326 evaluated |
| Orphan nodes | 12% | 149 nodes with 0 structural edges |

### Actionable Gaps
1. Run `rai discover scan` → refresh components
2. Start pattern validation via /story-review → builds Wilson scores
3. Consider pruning keyword-only `related_to` edges → improves density signal
```

**For `rai memory gaps --module X` (scoped):**
Competency-question-based checklist per module, as shown in RQ3.

---

## Synthesis: Three Indicators for RaiSE

The meta-cognition system has three complementary indicators, each serving a different purpose:

### 1. Coverage (Schema Completeness)

**What:** Does the graph have all expected node types with healthy populations?

**How:** Declarative schema expectations per lifecycle phase:

```yaml
# Expected graph schema
schema_expectations:
  post_init:
    required: [project, principle]
    optional: [pattern, session]
  post_onboard:
    required: [project, principle, module, architecture, component]
    optional: [pattern, session, calibration, skill]
  post_discovery:
    required: [project, principle, module, architecture, component, bounded_context, layer]
    minimum_counts:
      component: 10
      module: 3
  mature:
    required: [all 19 types]
    minimum_counts:
      pattern: 50
      session: 20
      component: 50
      decision: 5
```

**Output:** `coverage: 89% (17/19 types)` + list of missing/underrepresented types.

**Complexity:** S — count nodes by type, compare against expectations.

### 2. Confidence (Structural Density)

**What:** How much of the graph's connectivity is meaningful (structural edges) vs noise (keyword heuristic)?

**How:**
```python
structural_types = {'learned_from', 'governed_by', 'implements', 'part_of',
                    'depends_on', 'belongs_to', 'in_layer', 'constrained_by',
                    'applies_to', 'needs_context'}
structural_edges = count(e for e in edges if e.type in structural_types)
density = structural_edges / total_edges
```

**Additional signals:**
- Orphan rate: nodes with 0 structural edges
- Cross-type connectivity: how many node-type pairs have structural connections
- Pattern validation ratio: from Wilson scores (RES-TEMPORAL-001)

**Output:** `density: 2.3% structural | orphans: 12% | validation: 0%`

**Complexity:** S — edge type counting. The hard part is defining what "healthy" density looks like (needs calibration from real usage).

### 3. Gaps (Competency Questions)

**What:** For a given context (module, story, epic), what knowledge is missing?

**How:** Predefined CQ templates per context type:

```yaml
# Competency questions for module context
module_cqs:
  - "What patterns apply to {module}?"
    check: patterns with context matching module keywords
    minimum: 1
  - "What decisions constrain {module}?"
    check: ADR nodes connected to module
    minimum: 0  # not all modules have ADRs
  - "What guardrails govern {module}?"
    check: guardrail → module constrained_by edges
    minimum: 1
  - "What are {module}'s dependencies?"
    check: depends_on edges from module
    minimum: 0  # leaf modules have none
  - "What components exist in {module}?"
    check: component nodes with source matching module path
    minimum: 1
```

**Output:** `coverage: 83% (5/6 CQs answered) | gaps: no guardrail edges`

**Complexity:** M — need CQ definitions per context type, query logic, gap reporting.

---

## Implementation Implications

### Phase 1: `rai memory health` command (S story)

```bash
$ rai memory health

# Output:
Graph Health: 1,244 nodes, 16,884 edges
  Schema coverage:      89% (17/19 types present)
  Structural density:   2.3% (383/16,884 edges)
  Staleness:           Components: 30d ⚠️
  Pattern validation:   0% (0/326 evaluated)
  Orphan nodes:         149 (12%)
```

**Code changes:**
| File | Change | Size |
|------|--------|------|
| `cli/commands/memory.py` | Add `health` subcommand | S |
| `context/health.py` | New module: schema expectations, density calc, staleness | M |
| `context/models.py` | Add `HealthReport` Pydantic model | XS |
| Tests | Health check logic, edge cases | S |

### Phase 2: Session-start integration (XS addition)

Add one line to context bundle output:
```
# Graph Health
coverage: 89% | density: 2.3% | stale: components (30d)
```

Rai reads this and flags issues proactively.

### Phase 3: `rai memory gaps --module X` (M story)

Scoped CQ-based gap detection. Requires:
- CQ template definitions (YAML)
- Query execution against graph
- Gap reporting with recommendations

### Phase 4: Pattern validation integration (from RES-TEMPORAL-001)

Once Wilson score reinforcement is implemented, the validation ratio becomes a real indicator. Until then, it shows 0%.

---

## Recommendation

**Decision:** Implement meta-cognition as three deterministic structural indicators (coverage, confidence, gaps), NOT as LLM self-assessment. Phase 1 (`rai memory health`) is an S-sized story that delivers immediate value.

**Confidence:** HIGH

**Rationale:**
- LLM introspection is unreliable for knowledge boundary detection (S6, S7 — Nature + Sage, very high evidence)
- Structural measurement is deterministic and reproducible (S4, S11 — KG quality research)
- Competency questions provide domain-grounded gap detection (S5 — multiple peer-reviewed sources)
- Our graph already has the schema and data to support all three indicators (S12 — internal analysis)
- Phased approach allows incremental delivery without architectural changes

**Trade-offs:**
- We skip LLM-based confidence scoring (too unreliable without logit access)
- We skip Hindsight's per-memory confidence model (requires graph restructuring)
- Schema expectations need manual definition per lifecycle phase (but this is a feature — it makes expectations explicit)

**Risks:**
- "Healthy" density thresholds need calibration — we don't know yet what 2.3% means qualitatively → mitigate by tracking over time and establishing baselines
- Competency questions may produce false gaps (module has no ADRs because none are needed, not because one is missing) → mitigate with `minimum: 0` for optional dimensions
- Keyword `related_to` edges dominate — if we report only 2.3% structural density, it may look alarming → contextualize in output ("structural edges carry more weight than keyword associations")

---

## Quality Checklist

- [x] Research question is specific and falsifiable
- [x] 12 sources consulted (standard depth)
- [x] Evidence catalog created with levels
- [x] Major claims triangulated (3+ sources per RQ)
- [x] Confidence level explicitly stated
- [x] Contrary evidence acknowledged (LLM introspection vs structural measurement)
- [x] Recommendation is actionable
- [x] Governance linkage: informs RAISE-171 design

---

## References

### Evidence Catalog
- [Full Catalog](sources/evidence-catalog.md) — 12 sources with ratings

### Key Sources
- [AutoMeco — LLM Meta-Cognition](https://arxiv.org/abs/2506.08410) — Intrinsic meta-cognition via lenses (S1)
- [Hindsight — Confidence Scoring](https://arxiv.org/abs/2512.12818) — Four-network memory with opinion confidence (S2)
- [SAGE — Self-Evolving Agents](https://arxiv.org/abs/2409.00872) — Reflection-based gap detection (S3)
- [KG Quality Management Survey](https://www.wict.pku.edu.cn/docs/20240422164533167415.pdf) — Completeness, accuracy, consistency (S4)
- [Competency Questions Survey](https://link.springer.com/chapter/10.1007/978-3-031-47262-6_3) — CQ-based ontology evaluation (S5)
- [Metacognition in LLMs](https://journals.sagepub.com/doi/10.1177/09637214251391158) — Overconfidence warning (S6)
- [LLMs Lack Metacognition — Nature](https://www.nature.com/articles/s41467-024-55628-6) — Medical reasoning failures (S7)
- [Uncertainty Quantification Survey](https://arxiv.org/abs/2503.15850) — UQ methods for LLMs (S8)
- [MeCo — Metacognitive Tool Trigger](https://arxiv.org/abs/2502.12961) — Self-assessment for tool use (S9)
- [Self-Improving Agents](https://arxiv.org/abs/2506.05109) — Metacognitive learning requirements (S10)
- [KG Completeness SLR](https://hal.science/hal-03621495v1/file/Knowledge_Graph_Completeness_A_Systematic_Literature_Review.pdf) — Seven completeness types (S11)

### Related Research
- [RES-TEMPORAL-001](../temporal-decay-pattern-scoring/RES-TEMPORAL-001-report.md) — Temporal decay + Wilson score (pattern validation feeds into confidence indicator)
- [RES-MEMORY-002](../memory-systems/RES-MEMORY-002-research-report.md) — Foundation research identifying Gap F (meta-cognition)

---

*Research completed 2026-02-19. This document informs the design of RAISE-171.*
