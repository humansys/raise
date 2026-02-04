# Epic E11: Unified Context Architecture

> **Status:** DESIGNED — Ready for /epic-plan
> **Branch:** `feature/e11/unified-context`
> **Created:** 2026-02-03
> **Target:** F&F (Feb 9)
> **Depends on:** E2 (governance extractors), E3 (memory graph), E8 (work parsers)
> **Research:** `work/research/unified-context-architecture/` (RES-CONTEXT-001)
> **ADR:** ADR-019 (Unified Context Graph Architecture)

---

## Objective

Complete Rai's self-improvement infrastructure by unifying memory, governance, and work graphs into a single queryable context that skills can access.

**Value proposition:** Every skill invocation starts with relevant context. I don't re-discover patterns — I build on accumulated knowledge. Features complete faster, quality improves.

---

## Architecture (ADR-019)

**Decision:** Single unified NetworkX graph with multiple node types.

```
┌──────────────────────────────────────────────────────────────┐
│                    Unified Context Graph                      │
│                    (.raise/graph/unified.json)                │
│                                                              │
│  Nodes: patterns, calibration, sessions, principles,         │
│         requirements, outcomes, epics, features, skills      │
│                                                              │
│  Edges: learned_from, governed_by, applies_to,              │
│         needs_context, implements, part_of, related_to       │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    raise context query "..."
                              │
                              ▼
                    Minimum Viable Context
```

**Why unified:**
- Single query interface
- Cross-domain relationships (pattern → principle, skill → feature)
- No new dependencies (NetworkX)
- Right-sized for our scale (<1K nodes)

---

## Features

| ID | Feature | Size | Status | Description |
|----|---------|:----:|:------:|-------------|
| F11.1 | **Unified Graph Schema** | S | **Done** | Pydantic models, NetworkX wrapper, serialization |
| F11.2 | **Graph Builder** | M | **Done** | Merge governance + memory + work + skills into unified graph |
| F11.3 | **Unified Query** | S | Pending | `raise context query` with BFS + keyword matching |
| F11.4 | **Skill Integration** | S | Pending | Add "Query Context" step to 9 workflow skills |

**Total:** 4 features, ~7 SP, ~4-5 hours

---

## Feature Details

### F11.1: Unified Graph Schema

**Scope:**
- `ConceptNode` model (id, type, content, source_file, created, metadata)
- `ConceptEdge` model (source, target, type, weight, metadata)
- `UnifiedGraph` class wrapping NetworkX MultiDiGraph
- JSON serialization via `node_link_data`/`node_link_graph`

**Files:**
- `src/raise_cli/context/models.py` (new)
- `src/raise_cli/context/graph.py` (new)
- `src/raise_cli/context/__init__.py` (new)

### F11.2: Graph Builder

**Scope:**
- Load existing extractors (governance, memory, work)
- Parse skill metadata from `.claude/skills/*/SKILL.md`
- Merge all concepts into unified graph
- Infer relationships (learned_from, governed_by, applies_to, etc.)
- `raise graph build --unified` command

**Sources to merge:**
1. Governance: constitution principles, PRD requirements, vision outcomes
2. Memory: patterns, calibration, sessions
3. Work: epics, features from backlog
4. Skills: metadata from SKILL.md frontmatter

**Files:**
- `src/raise_cli/context/builder.py` (new)
- `src/raise_cli/context/extractors/` (new - skill parser)
- `src/raise_cli/cli/commands/graph.py` (extend)

### F11.3: Unified Query

**Scope:**
- `raise context query "<query>"` searches unified graph
- Keyword matching on node content
- BFS traversal from matched nodes (configurable depth)
- Filter by node type if specified
- Relevance ranking (keyword hits + recency)
- Output formats: human, json, table

**Command:**
```bash
raise context query "planning estimation" --max-depth 2 --types pattern,calibration
```

**Files:**
- `src/raise_cli/context/query.py` (new)
- `src/raise_cli/cli/commands/context.py` (extend)

### F11.4: Skill Integration

**Scope:** Add "Step 0.5: Query Context" to 9 workflow skills:

| Skill | Query Focus |
|-------|-------------|
| `/session-start` | Session type + current epic |
| `/session-close` | Session patterns (for extraction hints) |
| `/feature-design` | Architecture patterns, ADRs |
| `/feature-plan` | Planning patterns, calibration |
| `/feature-implement` | Codebase patterns, guardrails |
| `/feature-review` | Process patterns, retrospectives |
| `/epic-design` | Architecture decisions, prior epics |
| `/epic-plan` | Sequencing patterns, calibration |
| `/research` | Prior research, methodology |

**Files:**
- `.claude/skills/*/SKILL.md` (9 files)

---

## In Scope (F&F)

**MUST:**
- [x] ADR-019 documenting architecture decision
- [x] Unified graph schema (Pydantic + NetworkX) — F11.1 ✓
- [ ] Graph builder merging 4 sources
- [ ] Unified query command
- [ ] Skill integration (9 skills)

**SHOULD:**
- [ ] `--types` filter on query
- [ ] Relevance scoring with recency
- [ ] Graph validation on build

---

## Out of Scope

- Vector embeddings / semantic search (add later if keyword insufficient)
- Auto-rebuild on file changes (manual `raise graph build` for now)
- GraphRAG-style community detection (overkill for our scale)
- External database backend (NetworkX in-memory is sufficient)

---

## Dependencies

```
F11.1 (Schema)
   ↓
F11.2 (Builder) ─────► F11.3 (Query)
                          ↓
                       F11.4 (Skills)
```

**External:**
- E2 extractors (governance parsing) ✓ exists
- E3 memory loader (JSONL parsing) ✓ exists
- E8 work parsers (backlog, epic parsing) ✓ exists

**Critical path:** F11.1 → F11.2 → F11.3 → F11.4

---

## Done Criteria

### Per Feature
- [ ] Code implemented with type annotations
- [ ] Docstrings on all public APIs (Google-style)
- [ ] Unit tests passing (>90% coverage)
- [ ] All quality checks pass (ruff, pyright, bandit)

### Epic Complete
- [ ] Unified graph builds successfully
- [ ] Query returns relevant results for planning context
- [ ] 9 skills have "Query Context" step
- [ ] **Validation:** `/feature-plan` surfaces relevant patterns
- [ ] ADR-019 created ✓
- [ ] Component catalog updated

---

## Success Metrics

| Metric | Target | Validation |
|--------|--------|------------|
| Concepts in graph | >50 | `raise graph build --unified && jq '.nodes | length'` |
| Query latency | <100ms | Benchmark |
| Relevant results per skill | >2 | Manual check |
| Skills integrated | 9 | Count SKILL.md files with query step |

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| Existing extractors don't output compatible format | Medium | Medium | Adapter layer in builder |
| Query returns too much noise | Low | Medium | Type filtering, relevance cutoff |
| Skill changes break existing behavior | Low | Medium | Query is additive, doesn't change core logic |
| Build too slow | Low | Low | Our scale is small; optimize later if needed |

---

## The Learning Loop (Complete with E11)

```
┌─────────────────────────────────────────────────────────────┐
│                    THE COMPLETE LOOP                         │
│                                                             │
│  /session-start                                             │
│      ↓ query unified context (E11)                          │
│      ↓ load patterns, calibration, work context             │
│                                                             │
│  [WORK SESSION - using skills]                              │
│      ↓ each skill queries context first (E11)               │
│      ↓ telemetry signals emitted (E9)                       │
│                                                             │
│  /session-close                                             │
│      ↓ extract learnings                                    │
│      ↓ update memory (E3)                                   │
│      ↓ emit session signal (E9)                             │
│                                                             │
│  ────────────────────────────────────────────────────────   │
│  Next session: patterns available via unified query (E11)   │
│                I'm smarter than before                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Research Foundation

From RES-CONTEXT-001:
- **Microsoft GraphRAG**: Hierarchical communities, proven at scale
- **Neo4j**: 20-35% precision improvement with graph retrieval
- **Graphiti/Zep**: Temporal/episodic memory pattern
- **NetworkX**: Sufficient for <10K nodes, no dependencies

**Pattern learned:** PAT-048 — Unified graph > federated for small-scale systems.

---

---

## Implementation Plan

> Added by `/epic-plan` — 2026-02-03

### Feature Sequence

| Order | Feature | Size | Est. | Dependencies | Milestone | Rationale |
|:-----:|---------|:----:|:----:|--------------|-----------|-----------|
| 1 | F11.1 Unified Graph Schema | S | 45m | None | M1 | Foundation — all features depend on schema |
| 2 | F11.2 Graph Builder | M | 90m | F11.1 | M2 | Integration risk — merge 4 sources |
| 3 | F11.3 Unified Query | S | 45m | F11.1, F11.2 | M3 | Enables skill integration |
| 4 | F11.4 Skill Integration | S | 60m | F11.3 | M4 | Final integration — 9 skills |

**Total estimated:** ~4 hours (with kata cycle velocity)

### Milestones

| Milestone | Features | Target | Success Criteria | Demo |
|-----------|----------|--------|------------------|------|
| **M1: Schema Ready** | F11.1 | Hour 1 | Models pass pyright, tests pass | `UnifiedGraph` can add/serialize nodes |
| **M2: Graph Builds** | F11.2 | Hour 2.5 | All 4 sources merged into graph | `raise graph build --unified` produces JSON |
| **M3: Queryable** | F11.3 | Hour 3.5 | Query returns relevant context | `raise context query "planning"` works |
| **M4: Complete** | F11.4 | Hour 4.5 | Skills use unified context | `/feature-plan` shows queried patterns |

### Parallel Work Streams

```
Time →
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Stream 1: F11.1 ─► F11.2 ─► F11.3 ─► F11.4 (critical path, linear)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Note:** Linear dependency chain — no parallel opportunities. Each feature depends on the previous.

### Progress Tracking

| Feature | Size | Status | Actual | Velocity | Notes |
|---------|:----:|:------:|:------:|:--------:|-------|
| F11.1 Schema | S | **Done** | ~57m | 1.1x | 33 tests, 100% coverage |
| F11.2 Builder | M | **Done** | ~80m | 1.1x | 40 tests, 151 nodes, 255 edges |
| F11.3 Query | S | Pending | -- | -- | |
| F11.4 Skills | S | Pending | -- | -- | |

**Milestone Progress:**
- [x] M1: Schema Ready ✓
- [x] M2: Graph Builds ✓
- [ ] M3: Queryable
- [ ] M4: Complete

### Sequencing Rationale

**F11.1 first (Foundation):**
- All other features import the schema
- Low risk — Pydantic + NetworkX well understood
- Quick win — models are straightforward

**F11.2 second (Risk-First per PAT-020):**
- Highest risk: integrating 4 different extractors
- If adapters needed, better to discover early
- Validates architecture decision (ADR-019)

**F11.3 third (Enable integration):**
- Query is the user-facing interface
- Similar to existing memory query (pattern reuse)
- Must work before skills can use it

**F11.4 last (Integration):**
- Depends on query working
- Low risk — text edits to skill files
- Can validate the complete loop

### Velocity Assumptions

| Metric | Value | Source |
|--------|-------|--------|
| **Baseline velocity** | 1.5-2x | E9 calibration (similar infrastructure work) |
| **S feature actual** | 30-60 min | Recent calibration |
| **M feature actual** | 60-120 min | Recent calibration |
| **Buffer** | 20% | Integration, unexpected adapters |

### Sequencing Risks

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| Extractor output formats incompatible | Medium | Medium | Adapter layer in F11.2, fail fast |
| NetworkX serialization edge cases | Low | Low | Test with real data early |
| Skill edits cause regressions | Low | Medium | Each skill is independent, test one first |

---

*Plan created: 2026-02-03*
*Next: `/feature-plan` for F11.1*

---

*Epic scope - unified context architecture*
*Created: 2026-02-03*
*Designed: 2026-02-03*
*Planned: 2026-02-03*
*Research: RES-CONTEXT-001*
*ADR: ADR-019*
*Contributors: Emilio Osorio, Rai*
