# E1133: Skill Introspection — Scope

## Objective

Make every lifecycle skill (epic and story workflows) **measurably self-improving**: informed by accumulated knowledge before generating, producing learning records as a natural byproduct of operation, and feeding those records forward to the next skill in the chain.

**Current state:** 2 of 12 lifecycle skills read the graph. 1 of 12 writes patterns. 1 of 12 evaluates them. No skill produces evaluation data about its own effectiveness. All learning is concentrated in story-review — too late, too aggregated.

**Target state:** All lifecycle skills participate in a PRIME → GENERATE → LEARN cycle via a shared introspection aspect. LEARN produces a **learning record** — the unit of measurement that enables continuous improvement. Each skill reads the previous skill's learning record and enriches it with downstream impact. This is amplify learning (Poppendieck) applied to the development process itself.

## Design Principles

1. **Measurement IS operation** — learning records are not extra work; they are what LEARN naturally produces.
2. **Pointers over duplication** — git history IS the change trace, conversation transcript IS the execution trace. Learning records index and annotate — they don't duplicate. (CC SAR E1132: MetaHarness traces exist in git already)
3. **Skills evolve, not just context** — evolving skills (MCE paradigm) yields 16.9% mean improvement over evolving only context (ACE paradigm).
4. **Simple metrics + fast eval** — one flat record per execution (~10 fields), simple composite score. AutoResearch principle.
5. **Deterministic inner loop, adaptive outer loop** — PRIME executes fixed queries with variable substitution. JIT is LLM-adaptive. Self-improvement (future) is where the bitter lesson applies. (CC SAR E1132 F14: CC loads CLAUDE.md deterministically)

## Research Basis

Three formal research investigations ground this design:

1. **SOTA Agentic Memory Patterns** — 10 sources. Key finding: industry converges on **tiered hybrid**. Post-use evaluation is the industry's biggest gap.
2. **Design Query Taxonomy** — Maps every decision point in epic-design and story-design to concrete graph queries. Identifies 3 gaps in current graph schema.
3. **Self-Improving Coding Agents SOTA** — 12+ sources. Key finding: RaiSE skills map to MCE's "skill evolution" paradigm. Raw traces are essential — but they already exist in git.

**Additional validation:** E1132 Claude Code Architecture Reconstruction — 7 design improvements validated against CC's production architecture.

## Architecture

### 3-Tier Introspection Model

```
┌─────────────────────────────────────────────────────────┐
│  TIER 0: GUARDRAILS (always in system prompt)           │
│  Loaded at session start. Zero per-skill cost.          │
│  Already exists — no changes needed.                    │
│                                                         │
│  TIER 1: PHASE PRIME (hook — before skill body)         │
│  Deterministic query: template + variable substitution. │
│  ~3-5 relevant patterns per skill. 1 CLI call.          │
│  Reads previous skill's learning record for chain.      │
│                                                         │
│  TIER 2: JIT ALIGNMENT (in-step — agent-initiated)      │
│  LLM-adaptive query at decision bifurcations.           │
│  0-N queries per skill run. Agent-controlled.           │
│  Heuristic: "multiple valid approaches + consequences   │
│  beyond this step → query graph before deciding."       │
│                                                         │
│  LEARN (hook — after skill body)                        │
│  Produces flat learning record YAML (~10 fields):       │
│  pattern votes, gap analysis, trace pointers.           │
│  Compaction-proof: reads from disk, not conversation.   │
│  Hard limit: 1200 tokens total introspection overhead.  │
└─────────────────────────────────────────────────────────┘
```

### Learning Record: The Unit of Measurement

Each skill execution produces a learning record — a flat structured YAML (~10 fields) that serves three purposes simultaneously:

1. **Pattern evaluation** (was the primed context useful?)
2. **Gap identification** (what's missing from the graph?)
3. **Trace indexing** (pointers to git commits, artifacts, branches)

```yaml
# .raise/rai/learnings/{skill}/{work_id}/record.yaml
skill: rai-story-design
work_id: S1133.4
version: "2.4.0"
timestamp: 2026-04-01T09:15:00
primed_patterns: [PAT-E-590]
tier1_queries: 2
tier1_results: 3
jit_queries: 1
pattern_votes:
  PAT-E-590: {vote: 1, why: "directly applied"}
gaps:
  - "No patterns for 'aspect cross-cutting concern'"
artifacts: [design.md, examples]
commit: abc123
branch: story/s1133.4/story-lifecycle
downstream: {}
```

### The Learning Chain

Skills read AND write learning records — measurement flows naturally through the lifecycle:

```
epic-design → learning record → epic-plan reads "design gaps? sizing?"
                                    → learning record → [story cycle]

story-design → learning record → story-plan reads "AC testable? approach clear?"
                                     → learning record → story-implement reads "tasks?"
                                                             → enriches story-design record
                                                             → learning record → story-review
```

Downstream enrichment is **best-effort** — if upstream record is missing, corrupted, or locked: log warning, continue. Nulls are valid signal.

### Introspection as Aspect

Defined once in `aspects/introspection.md`, referenced by all lifecycle skills. Skills declare participation:

```yaml
metadata:
  raise.aspects: introspection
  raise.introspection:
    phase: story.design
    context_source: scope doc
    affected_modules: [mod-backlog, mod-graph]
    max_tier1_queries: 3
    max_jit_queries: 3
    tier1_queries:
      - "patterns for {affected_modules} design decisions"
```

### Why tiered hybrid (not fully automatic)

| Approach | Verdict | Reason |
|----------|---------|--------|
| Fully automatic (CrewAI-style) | Rejected | Token bloat, noise, no evaluation capability |
| Fully agent-controlled (Letta-style) | Rejected | Inconsistent — agent may skip retrieval |
| **Tiered hybrid** | **Adopted** | Deterministic prime + agent JIT + mandatory learning record |

## In Scope

### S1: Introspection Aspect Definition
Define `aspects/introspection.md` — the shared PRIME/JIT/LEARN protocol. Includes:
- Deterministic Tier 1 query templates with variable substitution
- Tier 2 JIT heuristic with concrete trigger examples
- LEARN protocol that produces flat learning record YAML
- Learning record schema (~10 fields, pointers not traces)
- Evaluation semantics (recall failure vs use failure)
- Downstream enrichment protocol (best-effort, failure never blocks)
- Hard token limit: 1200 tokens total introspection overhead

### S2: Graph Schema Enhancements
Close identified gaps in the knowledge graph:
- Pattern type taxonomy: add `approach` and `risk` to existing types
- Story outcome metadata
- Context tag standardization
- Learning records stored in `.raise/rai/learnings/`

### S3: Epic Lifecycle Integration
Add introspection aspect to epic-design, epic-plan, epic-close:
- Declare phase metadata including `max_tier1_queries`, `max_jit_queries`
- Add deterministic Tier 1 query templates
- Add Tier 2 JIT instruction to relevant steps
- Add LEARN section that produces flat learning record

### S4: Story Lifecycle Integration
Add introspection aspect to story-design, story-plan, story-implement, story-close:
- Declare phase metadata with query limits
- Add deterministic Tier 1 query templates
- Add LEARN section with compaction-resilient record production
- Each skill reads previous skill's learning record and enriches downstream (best-effort)

### S5: Story-Review Refactor
Simplify story-review now that evaluation is distributed:
- Remove "evaluate all patterns" responsibility
- Keep: retrospective, calibration telemetry, meta-pattern synthesis
- Add: aggregate learning summary across all skill executions
- Produce: learning metrics (acceptance rate, gap rate, pattern utility)

### S6: Validation & Dogfood
Run 1 complete epic cycle (2-3 stories) with introspection active. Measure:
- Learning chain completeness
- Pattern utility (primed patterns voted +1 vs 0 vs -1)
- JIT query appropriateness
- Downstream attribution
- **Actual** token overhead (validate against 1200 hard limit)
- Schema sufficiency (do we need more fields? Evidence-based extension)

## Out of Scope

- Automatic skill evolution loop (rai-skill-improve) — future, enabled by traces
- Automatic aspect weaving by rai-agent runtime — future
- Pattern lifecycle management — separate epic
- Changes to non-lifecycle skills
- Background LEARN (future — when PostToolUse hooks exist)
- LLM-refined priming (rejected per CC SAR: inner loop = deterministic)

## Stories

| ID | Story | Size | Deps | Description |
|----|-------|------|------|-------------|
| S1133.1 | Introspection aspect definition | M | — | `aspects/introspection.md` with PRIME/JIT/LEARN, flat schema, hard limits |
| S1133.2 | Graph schema + learning infrastructure | S | — | Pattern types, story metadata, `.raise/rai/learnings/` ✓ |
| S1133.3 | Epic lifecycle integration | M | S1133.1 | Integrate aspect into epic-design, epic-plan, epic-close ✓ |
| S1133.4 | Story lifecycle integration | M | S1133.1 | Integrate aspect into story-design, story-plan, story-implement, story-review ✓ |
| S1133.5 | Story-review refactor | S | S1133.4 | Aggregate learning records, learning metrics |
| S1133.6 | Validation & dogfood | M | S1133.3, S1133.4, S1133.5 | 1 epic cycle, measure real overhead |

Dependency graph:
```
S1133.1 ──→ S1133.3 ──┐
    │                  ├──→ S1133.6
    └──→ S1133.4 ──→ S1133.5 ──┘

S1133.2 (parallel — no deps)
```

## Estimation

| Story | Size | Estimated effort | Rationale |
|-------|------|-----------------|-----------|
| S1133.1 | M | 4-6h | Protocol design, flat schema, query guidance |
| S1133.2 | S | 2-3h | Additive schema changes, directory structure |
| S1133.3 | M | 4-6h | 3 skills, deterministic query templates |
| S1133.4 | M | 5-7h | 4 skills, learning chain, downstream enrichment |
| S1133.5 | S | 2-3h | Simplification + aggregation |
| S1133.6 | M | 4-6h | Real usage, +50% buffer (PAT-E-592) |
| **Total** | | **21-31h** | |

## Done Criteria

- [x] `aspects/introspection.md` defines complete PRIME/JIT/LEARN protocol
- [x] Learning record schema is flat (~10 fields) with pointers to traces
- [ ] All 7 cognitive lifecycle skills reference introspection aspect
- [ ] Each skill produces a learning record in `.raise/rai/learnings/{skill}/{work_id}/`
- [ ] Learning chain works: each skill reads previous skill's learning record
- [ ] Downstream enrichment is best-effort with failure logging
- [x] PRIME is deterministic (template + variable substitution, no LLM refinement)
- [ ] Token overhead measured and within 1200 hard limit
- [x] Metadata includes `max_tier1_queries` and `max_jit_queries`
- [ ] At least 1 epic cycle completed with full learning chain
- [ ] Schema extended only with evidence from dogfood

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Token bloat from priming + learning record | Medium | High | Hard limit 1200. Truncate, don't fail |
| LLM ignores JIT heuristic | Medium | Medium | Concrete trigger examples. Validate in dogfood |
| Learning records become noise | Low | High | Require `why` on votes. Gaps are factual |
| Deterministic queries miss nuanced context | Medium | Low | JIT compensates. Outer loop improves queries later |
| Downstream enrichment fails silently | Medium | Low | Best-effort + warning log. Nulls are valid signal |
| Modifying 7 skills creates merge conflicts | Medium | Low | Sequential stories on separate branches |

## Strategic Context

```
E1133 (now)              → Flat learning records: measurement as operation
                            Records + git traces accumulate

Post-E1133 (manual)      → rai-skill-improve: reads records + git traces,
                            proposes skill edits. Human reviews.
                            Simple scoring: gap rate + pattern utility + downstream

With rai-agent (future)  → Event-driven: skill.execution.complete →
                            store record. threshold(10) → trigger improvement.
                            Background LEARN via PostToolUse hooks.
```

## Changes Log

| Version | Date | Changes |
|---------|------|---------|
| v1 | 2026-03-31 | Initial scope — LLM-refined priming, nested schema |
| v2 | 2026-04-01 | CC SAR alignment: deterministic PRIME, flat schema, hard limits, pointers not traces, best-effort enrichment, enforceable metadata limits |

## References

- Research: `work/research/skill-memory-integration/`
- ADR-014: Skill Introspection Aspect
- **E1132: Claude Code Architecture Reconstruction** — SAR validation
- Patterns: PAT-E-592 (dogfood +50% buffer), PAT-E-590 (hook extension pattern)
- Key papers: MetaHarness, MCE, ACE
