# Aspect: Introspection

> Learning is cognitive infrastructure. Skills just work — PRIME/JIT/LEARN happen around them.

This aspect defines the protocol that wraps lifecycle skills with graph-informed context (PRIME), decision-point alignment (JIT), and learning record production (LEARN). Skills declare participation via metadata; the protocol executes as invisible infrastructure.

**Design basis:** ADR-014, Poppendieck (amplify learning), MetaHarness (traces over summaries), MCE (skill evolution).

---

## Participation

### Which skills participate

Only skills with **cognitive work** — decisions, design, evaluation. Mechanical skills (branch creation, cleanup) are **silent nodes**: their absence of a learning record is signal that no cognitive decisions occurred.

| Skill | Phase | Participates | Rationale |
|-------|-------|:---:|-----------|
| rai-epic-start | epic.start | — | Mechanical: directory + scope init |
| rai-epic-design | epic.design | Yes | Designs scope, architecture, stories |
| rai-epic-plan | epic.plan | Yes | Sequences, estimates, identifies risks |
| rai-epic-close | epic.close | Yes | Retrospective, metrics, pattern synthesis |
| rai-story-start | story.start | — | Mechanical: branch + scope commit |
| rai-story-design | story.design | Yes | Designs approach, examples, AC |
| rai-story-plan | story.plan | Yes | Decomposes into executable tasks |
| rai-story-implement | story.implement | Yes | TDD execution, architectural decisions |
| rai-story-review | story.review | Yes | Retrospective, pattern capture, learning aggregation |
| rai-story-close | story.close | — | Mechanical: merge + cleanup |

### How skills declare participation

In the skill's `SKILL.md` frontmatter:

```yaml
metadata:
  raise.aspects: introspection
  raise.introspection:
    phase: story.design           # lifecycle phase identifier
    context_source: scope doc     # primary input the skill works from
    affected_modules: [mod-backlog, mod-graph]  # graph modules to query
    tier1_queries:                 # suggested queries (LLM refines)
      - "patterns for {affected_modules} design decisions"
      - "prior designs for similar scope in {phase}"
      - "risks and lessons from related epics"
```

### Stepping stone integration

Today, skills reference this aspect via markers in their body. No protocol reimplementation — only pointers:

```markdown
> **PRIME**: Before Step 1, follow PRIME protocol in `aspects/introspection.md`

[... skill steps unchanged ...]

> **JIT**: If multiple valid approaches with consequences beyond this step
> → query graph per `aspects/introspection.md § JIT Protocol`

> **LEARN**: After completing, follow LEARN protocol in `aspects/introspection.md`
```

When rai-agent arrives, it reads the metadata and composes the wrapper automatically. The markers become unnecessary.

---

## PRIME Protocol

### Purpose

Load relevant context from the knowledge graph before the skill body executes. Informed generation, not blind generation.

### When

Before the first step of the skill. Triggered by the `> **PRIME**` marker.

### Steps

1. **Chain read** — Check if the previous skill in the chain produced a learning record. If it exists, read it for downstream context (see § Chain Mapping).

2. **Graph query** — Execute Tier 1 queries from the skill's metadata:
   - Read `tier1_queries` from skill frontmatter
   - Refine each query using execution context (epic scope, story scope, current work)
   - The LLM adapts the suggested query — guidance, not template (bitter lesson)
   - Execute: `rai graph query "{refined_query}" --types {types} --limit 5`

3. **Present context** — Surface retrieved patterns as context for skill execution. Do not inject blindly — present with source and relevance.

### Constraints

- Maximum 3 Tier 1 queries per skill execution
- Maximum 5 patterns per query
- Time budget: <3s total for all queries
- 0 results is valid — it means the graph has no relevant context (not a failure)

### Example

```
Phase: story.design for S1133.1
Context: E1133 (skill introspection), affected modules: mod-skills, mod-graph

Chain read: No previous learning record (story-start is silent)

Query 1 (suggested): "patterns for {affected_modules} design decisions"
Query 1 (refined):   "patterns for cross-cutting concerns in skill architecture"
Result: PAT-E-590 (hook extension pattern) — 1 pattern

Query 2 (suggested): "risks and lessons from related epics"
Query 2 (refined):   "lessons from skill modification epics"
Result: 1 pattern about drift risk

Context presented to skill: 2 patterns, both relevant to aspect design approach.
```

---

## JIT Protocol

### Purpose

Query the graph at decision bifurcations during skill execution. Agent-initiated, not scheduled.

### When

During skill steps where a decision bifurcation occurs. Triggered by the `> **JIT**` marker at specific steps, but the LLM can also initiate without a marker when the heuristic applies.

### Heuristic

> **"Multiple valid approaches exist AND consequences extend beyond this step → query graph before deciding."**

Concrete triggers:
- Choosing between architectural patterns (e.g., wrapper vs reference)
- Selecting a data model when multiple schemas could work
- Deciding integration strategy when upstream/downstream contracts are unclear
- Risk assessment when similar risks may have been encountered before

Non-triggers (do NOT query):
- Naming decisions
- Formatting choices
- Single obvious approach
- Decisions fully contained within the current step

### Steps

1. Formulate query from the decision context
2. Execute: `rai graph query "{query}" --types approach,risk --limit 3`
3. If results: consider patterns before deciding
4. If 0 results: this is a **gap signal** — record in learning record, proceed with best judgment

### Constraints

- Maximum 3 JIT queries per skill execution
- Time budget: <2s per query
- 0 results = gap (captured in learning record), not failure
- JIT never blocks execution — if graph is unavailable, proceed and note in learning record

### Example

```
Step 3 of story-design: Describe Approach
Decision: Aspect as reference vs aspect as wrapper
Heuristic: Two valid approaches, consequences affect all 10 skills → JIT triggers

Query: "patterns for aspect-oriented design in skill systems, wrapper vs reference"
Result: 0 patterns

Action: Gap recorded. Proceeded with exploration of both options.
         Pattern candidate deferred to story-review for capture after validation.
```

---

## LEARN Protocol

### Purpose

Produce a learning record — the structured trace of what happened during skill execution. Measurement IS operation (Poppendieck: amplify learning).

### When

After the last step of the skill completes. Triggered by the `> **LEARN**` marker.

### Steps

1. **Evaluate process fidelity**
   - Did PRIME run? What queries, what results?
   - Did JIT fire? At what triggers? Results or gaps?
   - What artifacts were produced?

2. **Vote on primed patterns**
   - For each pattern surfaced by PRIME: +1 (used), 0 (seen, not relevant), -1 (misleading)
   - Include `why` — the reason is the trace, not the vote
   - This enables recall failure vs use failure distinction (Governed Memory):
     - Pattern not retrieved but would have helped → **recall failure** (improve queries)
     - Pattern retrieved but not useful → **use failure** (improve pattern quality)

3. **Identify gaps**
   - Decisions made without graph context
   - JIT queries that returned 0 results
   - Moments where "I wish I had a pattern for X"
   - Gaps are the highest-value signal — they tell us what the graph is missing

4. **Write learning record**
   - Path: `.raise/rai/learnings/{skill}/{work_id}/record.yaml`
   - Schema: see § Learning Record Schema

5. **Enrich previous skill's learning record** (if applicable)
   - Read the upstream skill's learning record
   - Fill the `downstream_impact` fields with factual observations
   - See § Downstream Enrichment

### What LEARN does NOT do

- **Does not capture new patterns.** Only records gaps. Pattern capture is story-review's responsibility, after implementation validates the approach. Rationale: triple gate (New + Generalizable + Actionable) requires evidence from execution.

- **Does not evaluate output quality.** Acceptance is implicit in the chain: if the next skill executes, the previous output was accepted. No ceremony for what can be inferred. Rationale: LEARN captures what it knows at execution time (Poppendieck: eliminate waste).

- **Does not produce summaries.** The learning record IS the trace. Summaries lose information — MetaHarness Table 3 shows raw traces outperform summaries by 15+ points.

---

## Learning Record Schema

```yaml
# .raise/rai/learnings/{skill}/{work_id}/record.yaml

skill: rai-story-design           # skill that produced this record
version: "2.4.0"                  # skill version at execution time
work_id: S1133.1                  # story or epic work ID
timestamp: 2026-04-01T11:30:00    # ISO 8601

process_fidelity:
  tier1_primed: true              # did PRIME execute?
  tier1_queries:                  # what was queried (the trace)
    - query: "patterns for cross-cutting concerns in skill architecture"
      types: [approach, risk]     # graph query types filter
      results: 1                  # number of patterns returned
      useful: true                # was the result used in the work?
    - query: "prior story designs for docs/protocol stories"
      results: 0                  # 0 results = no gap signal from query itself
  jit_queries:                    # JIT queries during execution
    - query: "patterns for aspect-oriented design"
      trigger: "Step 3 — two valid approaches with structural consequences"
      results: 0
      gap: true                   # 0 results at a decision point = gap signal
  artifacts_produced:             # what the skill created
    - s1133.1-design.md
    - s1133.1-design.yaml

pattern_metrics:
  primed:                         # evaluation of patterns from PRIME
    - id: PAT-E-590               # pattern identifier
      vote: 1                     # +1 used, 0 not relevant, -1 misleading
      why: "hook extension pattern directly informed stepping stone design"
  gaps:                           # what the graph was missing
    - "No patterns for aspect-oriented composition in skill systems"
    - "No prior designs for protocol/docs-type stories"

downstream_impact:                # filled by the NEXT skill in the chain
  next_skill: rai-story-plan      # which skill fills these
  plan_derivable: null            # could story-plan derive tasks from this design?
  tasks_clear: null               # were the tasks clear and executable?
  design_gaps_found: null         # did implementation reveal design gaps?
```

### Schema rules

1. **All fields present, nulls explicit.** A null downstream_impact field means "not yet filled" — distinct from "not applicable."
2. **`why` is mandatory on votes.** The reason is the trace. A vote without `why` is noise.
3. **`gap: true` only on JIT queries with 0 results at decision points.** Tier 1 queries with 0 results are normal (the topic may not have patterns yet).
4. **Timestamps are UTC ISO 8601.**
5. **One record per skill execution.** If a skill runs twice for the same work_id (rework), the second record overwrites the first.

---

## Chain Mapping

The learning chain defines how records flow between skills. Each participating skill reads the previous skill's record (informing its PRIME) and enriches it with downstream observations.

### Epic chain

```
epic-design ──record──→ epic-plan ──record──→ epic-close
                ↑                     ↑              │
                │                     │              │
                └─ epic-plan reads:   └─ epic-close  └─ reads all records,
                   design_coherent?      reads:         produces aggregate
                   scope_clear?          plan_held?
                                         estimates_accurate?
```

| Upstream | Downstream | What downstream reads | What downstream enriches |
|----------|------------|----------------------|------------------------|
| epic-design | epic-plan | gaps, approach decisions | `design_coherent`, `scope_clear` |
| epic-plan | epic-close | sizing, risk predictions | `plan_held`, `estimates_accurate` |

### Story chain

```
story-design ──record──→ story-plan ──record──→ story-implement ──record──→ story-review
                 ↑                      ↑               │                       │
                 │                      │               │                       │
                 └─ story-plan reads:   │               └─ enriches             └─ reads all,
                    plan_derivable?     └─ implement        story-design:           aggregates,
                    tasks_clear?           reads:           design_gaps_found       captures patterns
                                           tasks_executable?
                                           estimate_accurate?
```

| Upstream | Downstream | What downstream reads | What downstream enriches |
|----------|------------|----------------------|------------------------|
| story-design | story-plan | gaps, approach, examples | `plan_derivable`, `tasks_clear` |
| story-plan | story-implement | task breakdown, estimates | `tasks_executable`, `estimate_accurate` |
| story-design | story-implement | (skip-read) design decisions | `design_gaps_found`, `ac_testable_rate` |
| story-implement | story-review | execution gaps, rework signals | (story-review reads, does not enrich — it's the chain end) |

### Downstream enrichment mechanics

To enrich an upstream learning record:

1. Locate the upstream record: `.raise/rai/learnings/{upstream_skill}/{work_id}/record.yaml`
2. Read the `downstream_impact` section
3. Fill null fields with factual observations (not opinions)
4. Write the updated record back

Example — story-plan enriches story-design's record:
```yaml
# Before (written by story-design LEARN):
downstream_impact:
  next_skill: rai-story-plan
  plan_derivable: null
  tasks_clear: null

# After (enriched by story-plan PRIME):
downstream_impact:
  next_skill: rai-story-plan
  plan_derivable: true
  tasks_clear: true
```

**Rules:**
- Only fill null fields — never overwrite existing values
- Only write factual observations: "I could/couldn't derive tasks" not "the design was good/bad"
- If the upstream record doesn't exist (silent node or execution gap), skip enrichment silently

---

## Evaluation Semantics

When a primed pattern is not useful, the learning record helps distinguish two failure modes (from Governed Memory, arxiv 2603.17787):

### Recall failure (system gap)

The graph had a relevant pattern, but PRIME didn't retrieve it. The queries missed it.

**Signal:** Gap in learning record ("no patterns for X") + pattern later found manually or by JIT.
**Action:** Improve Tier 1 query templates for that phase.

### Use failure (pattern quality gap)

PRIME retrieved the pattern, but it wasn't useful (-1 or 0 vote).

**Signal:** Pattern voted 0 or -1 with `why` explaining irrelevance.
**Action:** Pattern needs refinement, re-contextualization, or retirement.

### Neither (genuine novelty)

No relevant pattern exists in the graph. The gap is real.

**Signal:** JIT query with 0 results + no pattern found manually.
**Action:** Candidate for new pattern capture in story-review (after validation).

---

## Downstream Impact Fields by Phase

### Epic lifecycle

| Phase | downstream_impact fields |
|-------|------------------------|
| epic.design | `design_coherent`: bool, `scope_clear`: bool, `stories_derivable`: bool |
| epic.plan | `plan_held`: bool, `estimates_accurate`: bool, `risk_predictions_useful`: bool |

### Story lifecycle

| Phase | downstream_impact fields |
|-------|------------------------|
| story.design | `plan_derivable`: bool, `tasks_clear`: bool, `design_gaps_found`: str or null, `ac_testable_rate`: float or null |
| story.plan | `tasks_executable`: bool, `estimate_accurate`: bool, `blocked_by_missing_task`: bool |
| story.implement | `rework_needed`: bool, `rework_type`: str or null (minor/major), `patterns_applied`: int |

---

## Token Budget

The introspection aspect adds tokens to each skill execution:

| Component | Estimated tokens | Notes |
|-----------|-----------------|-------|
| PRIME (queries + results) | 200-400 | 3 queries × ~5 patterns × ~25 tokens each |
| JIT (0-3 queries) | 0-300 | Only at decision bifurcations |
| LEARN (record production) | 200-400 | Structured YAML, not prose |
| **Total overhead** | **400-1100** | Target: <1200 tokens |

Chain reads (previous skill's learning record) are included in PRIME budget.

---

## References

- ADR-014: `governance/adrs/v2/adr-014-skill-introspection-aspect.md`
- Epic scope: `work/epics/e1133-skill-introspection/scope.md`
- Research: `work/research/skill-memory-integration/`
- Governed Memory: arxiv 2603.17787 (recall failure vs use failure)
- MetaHarness: arxiv 2603.28052 (traces over summaries)
- MCE: arxiv 2601.21557 (skill evolution, bi-level optimization)
- Poppendieck: Amplify Learning — measurement IS operation
- Bitter Lesson: Sutton 2019 — guidance over rigid templates
