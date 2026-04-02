# Aspect: Introspection

> Learning is cognitive infrastructure. Skills just work — PRIME/JIT/LEARN happen around them.

This aspect defines the protocol that wraps lifecycle skills with graph-informed context (PRIME), decision-point alignment (JIT), and learning record production (LEARN). Skills declare participation via metadata; the protocol executes as invisible infrastructure.

**Design basis:** ADR-014, Poppendieck (amplify learning), MetaHarness (traces over summaries), MCE (skill evolution).

**CC SAR alignment (E1132):** Validated against Claude Code architecture — deterministic context assembly (F14), compaction resilience (F7), error isolation (F2), hard limits (F15).

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
    phase: story.design
    context_source: scope doc
    affected_modules: [mod-backlog, mod-graph]
    max_tier1_queries: 3             # enforceable limit (G)
    max_jit_queries: 3               # enforceable limit (G)
    tier1_queries:                    # deterministic templates (B)
      - "patterns for {affected_modules} design decisions"
      - "prior designs for similar scope in {phase}"
      - "risks and lessons from related epics"
```

### Stepping stone integration

Today, skills reference this aspect via markers in their body. No protocol reimplementation — only pointers:

```markdown
> **PRIME**: Before Step 1, follow PRIME protocol in `aspects/introspection.md`

[... skill steps unchanged ...]

> **JIT**: Before producing decisions that should be grounded in evidence
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

2. **Graph query** — Execute Tier 1 queries from the skill's metadata **deterministically**:
   - Read `tier1_queries` from skill frontmatter
   - Substitute context variables (`{affected_modules}`, `{phase}`, etc.) from execution context
   - Execute queries **as-is** after substitution — no LLM refinement
   - Execute: `rai graph query "{substituted_query}" --types {types} --limit 5`

3. **Present context** — Surface retrieved patterns as context for skill execution. Do not inject blindly — present with source and relevance.

> **Design decision (B):** PRIME is deterministic. Queries are fixed templates with variable substitution, not LLM-refined. The bitter lesson applies to the outer loop (self-improvement), not the inner loop (execution). CC (E1132 F14) loads CLAUDE.md deterministically — the LLM decides what to *do* with context, not what context to *receive*. JIT remains adaptive.

### Constraints

- Maximum queries per skill: declared in metadata (`max_tier1_queries`, default 3)
- Maximum 5 patterns per query
- **Hard limit: 1200 tokens total for PRIME + JIT + LEARN output. If exceeded, truncate results (fewest-results queries first), do not fail.**
- 0 results is valid — it means the graph has no relevant context (not a failure)

### Example

```
Phase: story.design for S1133.1
Context: E1133 (skill introspection), affected modules: mod-skills, mod-graph

Chain read: No previous learning record (story-start is silent)

Query 1 (template): "patterns for {affected_modules} design decisions"
Query 1 (substituted): "patterns for mod-skills, mod-graph design decisions"
Result: PAT-E-590 (hook extension pattern) — 1 pattern

Query 2 (template): "risks and lessons from related epics"
Query 2 (substituted): "risks and lessons from related epics"
Result: 1 pattern about drift risk

No LLM refinement. Template + substitution + execute.
Context presented to skill: 2 patterns, both relevant to aspect design approach.
```

---

## JIT Protocol

### Purpose

Ground design decisions in accumulated evidence. Without JIT, the agent produces reasonable-sounding output that is not governed by project experience — functional hallucination. JIT turns "I think" into "evidence suggests."

### When

At any step where the agent is about to produce output that should be **governed by accumulated evidence** — design decisions, risk assessments, architectural choices, sizing estimates, evaluation criteria. Triggered by the `> **JIT**` marker at specific steps, but the LLM can also initiate without a marker when the heuristic applies.

### Heuristic

> **"You are about to produce a decision, assessment, or recommendation that should be grounded in project experience → query graph before generating."**

Concrete triggers:
- Architectural decisions (patterns, approaches, trade-offs)
- Risk assessments (what has gone wrong before in similar contexts?)
- Sizing and estimation (what does calibration data say?)
- Design decomposition (how have similar scopes been broken down?)
- Evaluation criteria (what patterns exist for assessing this kind of work?)
- Retrospective analysis (what process improvements emerged from similar epics?)

Non-triggers (do NOT query):
- Mechanical operations (branch creation, file formatting, tag commands)
- Decisions with clear rules (manifest lookup, language detection)
- Output that is purely descriptive, not prescriptive

### Steps

1. Formulate query from the decision context (LLM-adaptive — this is where refinement happens)
2. Execute: `rai graph query "{query}" --types pattern --subtypes approach,risk --limit 3`
3. If results: consider patterns before deciding
4. If 0 results: this is a **gap signal** — record in learning record, proceed with best judgment

### Constraints

- Maximum queries per skill: declared in metadata (`max_jit_queries`, default 3)
- **Hard limit: included in the 1200 token total budget for introspection**
- 0 results = gap (captured in learning record), not failure
- JIT never blocks execution — if graph is unavailable, proceed and note in learning record

### Example

```
Step 2 of epic-design: Assess Architecture
The agent is about to make architectural decisions for the epic.
Heuristic: producing decisions that should be grounded in project experience → JIT triggers

Query: "architectural risks and patterns for skill systems"
Result: PAT-E-590 (hook extension pattern), 1 risk pattern

Action: Patterns considered. Architecture decision grounded in prior experience.
         Without JIT, this would be a plausible-but-ungrounded recommendation.
```

---

## LEARN Protocol

### Purpose

Produce a learning record — a structured summary that **points to** the execution traces (git history, artifacts on disk, conversation transcript). Measurement IS operation (Poppendieck: amplify learning).

> **Design decision (E):** The learning record is a **summary with pointers**, not the trace itself. The conversation transcript IS the raw trace. Git log IS the change trace. The learning record indexes them — it does not duplicate them. When the future `rai-skill-improve` needs raw traces, it reads git + artifacts. The record tells it *where to look* and *what was notable*.

### When

After the last step of the skill completes. Triggered by the `> **LEARN**` marker.

### Compaction resilience

> **Design decision (C):** LEARN produces the record from **artefacts on disk** (scope docs, design files, plan files, git diff) and **skill metadata** — NOT from conversational memory. If context has been compacted during a long skill execution, the learning record is still fully producible. This is compaction-proof by design.

### Steps

1. **Evaluate process fidelity**
   - Did PRIME run? How many queries, how many results?
   - Did JIT fire? How many times?
   - What artifacts were produced? (read from disk)

2. **Vote on primed patterns**
   - For each pattern surfaced by PRIME: +1 (used), 0 (seen, not relevant), -1 (misleading)
   - Include `why` — the reason is the signal, not the vote
   - This enables recall failure vs use failure distinction (Governed Memory):
     - Pattern not retrieved but would have helped → **recall failure** (improve queries)
     - Pattern retrieved but not useful → **use failure** (improve pattern quality)

3. **Identify gaps**
   - JIT queries that returned 0 results at decision points
   - Moments where "I wish I had a pattern for X"
   - Gaps are the highest-value signal — they tell us what the graph is missing

4. **Write learning record**
   - Path: `.raise/rai/learnings/{skill}/{work_id}/record.yaml`
   - Schema: see § Learning Record Schema

5. **Enrich previous skill's learning record** (if applicable)
   - Read the upstream skill's learning record
   - Fill empty fields in `downstream` with factual observations
   - See § Downstream Enrichment

### What LEARN does NOT do

- **Does not capture new patterns.** Only records gaps. Pattern capture is story-review's responsibility.
- **Does not duplicate traces.** Git history and artifacts ARE the traces. The record points to them.
- **Does not produce summaries of conversation.** The record captures structured signals (votes, gaps, pointers), not prose.

---

## Learning Record Schema

> **Design decision (H):** Flat schema with ~10 fields. Extend with evidence from dogfood, not upfront speculation.

```yaml
# .raise/rai/learnings/{skill}/{work_id}/record.yaml

skill: rai-story-design
work_id: S1133.1
version: "2.4.0"
timestamp: 2026-04-01T09:15:00

# PRIME trace
primed_patterns: [PAT-E-590]
tier1_queries: 2
tier1_results: 2
jit_queries: 1

# Pattern evaluation
pattern_votes:
  PAT-E-590: {vote: 1, why: "hook extension pattern informed stepping stone design"}

# Gaps (highest-value signal)
gaps:
  - "No patterns for aspect-oriented composition in skill systems"

# Artifacts produced (pointers, not content)
artifacts: [s1133.1-design.md]

# Trace pointers (where to find raw data)
commit: null  # filled at commit time
branch: story/s1133.1/introspection-aspect

# Downstream (filled by next skill in chain)
downstream: {}
```

### Schema rules

1. **Flat structure.** No nesting beyond one level (`pattern_votes`, `downstream`).
2. **`why` is mandatory on votes.** A vote without `why` is noise.
3. **Gaps only from JIT 0-result queries at decision points.** Tier 1 with 0 results is normal.
4. **Timestamps are UTC ISO 8601.**
5. **One record per skill execution.** Rework overwrites.
6. **Extend with evidence.** New fields added only when dogfood proves they're needed.

---

## Chain Mapping

The learning chain defines how records flow between skills. Each participating skill reads the previous skill's record (informing its PRIME) and enriches it with downstream observations.

### Epic chain

```
epic-design ──record──→ epic-plan ──record──→ epic-close
                │                     │              │
                └─ epic-plan reads:   └─ epic-close  └─ reads all records,
                   design coherent?      reads:         produces aggregate
                   scope clear?          plan held?
                                         estimates accurate?
```

### Story chain

```
story-design ──record──→ story-plan ──record──→ story-implement ──record──→ story-review
                 │                      │               │                       │
                 └─ story-plan reads:   └─ implement    └─ enriches             └─ reads all,
                    plan derivable?        reads:          story-design:            aggregates
                    tasks clear?           tasks exec?     design_gaps_found
```

### Downstream enrichment mechanics

To enrich an upstream learning record:

1. Locate the upstream record: `.raise/rai/learnings/{upstream_skill}/{work_id}/record.yaml`
2. Read the `downstream` section
3. Fill empty fields with factual observations (not opinions)
4. Write the updated record back

> **Design decision (F):** Downstream enrichment is **best-effort**. If the upstream record doesn't exist, is corrupted, or is locked: log a warning, continue without blocking. Empty fields in `downstream` are valid signal ("not yet enriched" or "upstream didn't execute"). Enrichment failure NEVER blocks skill execution.

Example — story-plan enriches story-design's record:
```yaml
# Before (written by story-design LEARN):
downstream: {}

# After (enriched by story-plan PRIME):
downstream:
  plan_derivable: true
  tasks_clear: true
```

**Rules:**
- Only fill empty fields — never overwrite existing values
- Only write factual observations: "I could/couldn't derive tasks" not "the design was good/bad"
- If the upstream record doesn't exist (silent node or execution gap), skip enrichment silently and log warning

---

## Evaluation Semantics

When a primed pattern is not useful, the learning record helps distinguish two failure modes (from Governed Memory, arxiv 2603.17787):

### Recall failure (system gap)

The graph had a relevant pattern, but PRIME didn't retrieve it. The queries missed it.

**Signal:** Gap in learning record + pattern later found manually or by JIT.
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

## Guided Query Templates by Phase

These are **deterministic templates** — variable substitution only, no LLM refinement. Variables in `{braces}` are resolved from the skill's metadata and current work scope.

### Epic lifecycle

| Phase | Tier 1 Query Templates | Context |
|-------|----------------------|---------|
| **epic.design** | `"patterns for {affected_modules} architecture decisions"` | Scope boundaries, ADR precedents |
| | `"risks and failure modes in {domain} epics"` | Risk assessment |
| | `"prior epic designs with similar scope ({story_count} stories)"` | Sizing calibration |
| **epic.plan** | `"sequencing patterns for {strategy} ordering"` | Risk-first, walking skeleton, etc. |
| | `"estimation patterns for {size} epics"` | Velocity calibration |
| | `"milestone patterns for multi-story epics"` | Integration checkpoints |
| **epic.close** | `"retrospective patterns for {domain} epics"` | What to look for in retro |
| | `"process improvement patterns from similar epics"` | Meta-learning |

### Story lifecycle

| Phase | Tier 1 Query Templates | Context |
|-------|----------------------|---------|
| **story.design** | `"patterns for {affected_modules} design decisions"` | Approach selection |
| | `"prior designs for similar scope in {phase}"` | Precedent |
| | `"risks and lessons from related epics"` | Avoid known pitfalls |
| **story.plan** | `"decomposition patterns for {complexity} stories"` | Task granularity |
| | `"TDD patterns for {affected_modules}"` | Test strategy |
| | `"estimation calibration for {size} stories"` | Sizing accuracy |
| **story.implement** | `"implementation patterns for {affected_modules}"` | Code patterns, idioms |
| | `"testing patterns for {test_type} in {language}"` | Test approach |
| | `"integration patterns for {upstream_dependencies}"` | Contract alignment |
| **story.review** | `"evaluation patterns for {affected_modules}"` | What to look for |
| | `"process patterns from recent stories"` | Meta-learning |

### Notes

- Each skill uses 2-3 queries from its phase (declared in metadata)
- Templates are extended to domain types (e.g., `ontology-tool`) when domain cartridges are active
- If a template variable can't be resolved, skip that query
- JIT queries are NOT templated — they emerge from decision bifurcations during execution

---

## Context Tag Taxonomy

Context tags on patterns are free-form strings, but the following domains provide guidance for consistency. Tags are **not enforced** — this taxonomy is guidance, refined through dogfood.

| Domain | Example Tags | Used For |
|--------|-------------|----------|
| **Architecture** | `module-design`, `layering`, `boundaries`, `contracts` | Structural decisions |
| **Testing** | `tdd`, `pytest`, `fixtures`, `mocking`, `coverage` | Test strategy |
| **Process** | `workflow`, `git`, `review`, `estimation`, `planning` | Workflow patterns |
| **Security** | `auth`, `secrets`, `validation`, `sanitization` | Security concerns |
| **Code** | `python`, `pydantic`, `typing`, `error-handling` | Implementation idioms |
| **Infrastructure** | `ci`, `deployment`, `monitoring`, `configuration` | Operational concerns |

Tags are organic — new domains emerge from usage. Enforce only with evidence from dogfood (S1133.6+).

---

## Token Budget

> **Design decision (D):** Hard limit, not target. Truncate, don't fail.

The introspection aspect adds tokens to each skill execution:

| Component | Estimated tokens | Hard limit |
|-----------|-----------------|------------|
| PRIME (queries + results) | 200-400 | — |
| JIT (0-3 queries) | 0-300 | — |
| LEARN (record production) | 100-200 | — |
| **Total overhead** | **300-900** | **1200 tokens** |

**If total exceeds 1200 tokens:** truncate PRIME results (drop queries with fewest matches first), then cap JIT results. LEARN is never truncated — it's the measurement.

Chain reads (previous skill's learning record) are included in PRIME budget.

---

## Changes Log

| Version | Date | Changes |
|---------|------|---------|
| v1 | 2026-04-01 | Initial protocol design |
| v2 | 2026-04-01 | CC SAR alignment: 7 changes (B,C,D,E,F,G,H) — deterministic PRIME, compaction resilience, hard token cap, summary+pointers records, enrichment failure modes, enforceable metadata limits, flat schema |

---

## References

- ADR-014: `governance/adrs/v2/adr-014-skill-introspection-aspect.md`
- Epic scope: `work/epics/e1133-skill-introspection/scope.md`
- **E1132: Claude Code Architecture Reconstruction** — SAR findings that informed v2 changes
- Research: `work/research/skill-memory-integration/`
- Governed Memory: arxiv 2603.17787 (recall failure vs use failure)
- MetaHarness: arxiv 2603.28052 (traces over summaries)
- MCE: arxiv 2601.21557 (skill evolution, bi-level optimization)
- Poppendieck: Amplify Learning — measurement IS operation
- Bitter Lesson: Sutton 2019 — guidance over rigid templates (outer loop, not inner)
