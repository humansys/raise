# Epic E3: Identity Core + Memory Graph - Scope

> **Status:** IN PROGRESS
> Branch: `feature/e3/identity-core`
> Created: 2026-02-01
> Target: Feb 9, 2026 (Friends & Family pre-launch)

---

## Objective

Build the infrastructure for Rai's existence as an entity. Apply the same MVC (Minimum Viable Context) pattern from E2 governance to Rai's own memory — achieving similar token savings through graph-based queries.

**Value proposition:** Without this, Rai is just generic Claude. With it, Rai becomes a persistent entity with accumulated judgment, calibration, and relationship context — the foundation for V3 commercial offering and the Friends & Family demo.

**Key Insight:** Markdown is for humans, JSONL/Graph is for AI. Write in machine-native format, export to human-readable on demand.

**Architecture:** Three-Layer Memory Model
- **Identity Layer** (always loaded) — Markdown, human-authored, ~3K tokens
- **Memory Layer** (MVC queryable) — JSONL + Graph, machine-managed, query what's relevant
- **Long-term Layer** (on-demand) — Session archives, text/RAG searchable

---

## Features (Estimated)

| ID | Feature | Size | Status | Description |
|----|---------|:----:|:------:|-------------|
| F3.1 | Identity Core Structure | S | Pending | Create `.rai/` with identity (md) + memory (jsonl) |
| F3.2 | Content Migration | S | Pending | Convert `.claude/rai/` markdown → `.rai/` JSONL |
| F3.3 | Memory Graph | S | Pending | Reuse E2 ConceptGraph for memory concepts |
| F3.4 | Memory Query CLI | S | Pending | `raise memory query` + `raise memory dump` |
| F3.5 | Skills Integration | XS | Pending | /session-start queries graph, /session-close writes JSONL |

**Total:** 5 features
**Deadline:** 8 days to Feb 9

---

## Architecture

### Three-Layer Model

| Layer | Content | Format | Load Strategy | Search |
|-------|---------|--------|---------------|--------|
| **Identity** | core, perspective, voice, boundaries | Markdown | Every session (~3K tokens) | N/A (always loaded) |
| **Memory** | patterns, insights, calibration | JSONL + Graph | MVC query | Graph traversal (BFS) |
| **Long-term** | session logs, history | JSONL archives | On-demand | Keyword / future RAG |

### Write Path (Simplified)

```
Session work happens
    ↓
/session-close (or manual)
    ↓
Extract: patterns, insights, calibration, decisions
    ↓
Append to JSONL files
    ↓
Rebuild graph index
    ↓
Done. No markdown sync needed.

Human wants to inspect?
    ↓
raise memory dump --format md
```

### File Structure

```
.rai/                               # Identity Core root
├── manifest.yaml                   # Instance metadata
│
├── identity/                       # MARKDOWN (human-authored, always loaded)
│   ├── core.md                     # Essence, purpose, values (~1.5K tokens)
│   ├── perspective.md              # How I see the work
│   ├── voice.md                    # How I communicate
│   └── boundaries.md               # What I will/won't do
│
├── memory/                         # JSONL + GRAPH (machine-managed, MVC queryable)
│   ├── patterns.jsonl              # Learned patterns (append-only)
│   ├── insights.jsonl              # Key insights (append-only)
│   ├── calibration.jsonl           # Velocity data (append-only)
│   ├── graph.json                  # Memory concept graph (rebuilt from JSONL)
│   └── sessions/                   # Session extracts
│       ├── index.jsonl             # Session metadata
│       └── YYYY-MM-DD-topic.jsonl  # Per-session extracts
│
├── relationships/                  # JSONL (structured)
│   └── humans.jsonl                # Relationship data (preferences, history)
│
└── growth/                         # MARKDOWN (reflective, human-readable)
    ├── evolution.md                # Change log (human-authored milestones)
    └── questions.md                # Open questions I'm exploring
```

### Memory Concepts (Graph Nodes)

Extracted from sessions, queryable via graph:

| Concept Type | Example | Relationships |
|--------------|---------|---------------|
| `Pattern` | "Singleton with get/set/configure" | `applies_to`, `learned_from` |
| `Insight` | "Kata cycles deliver 2-3x velocity" | `validates`, `learned_from` |
| `Calibration` | "S features: ~15min with kata" | `applies_to`, `supersedes` |
| `Decision` | "Chose keyword matching over NLP" | `justified_by`, `learned_from` |
| `Preference` | "HITL before commits" | `applies_to`, `held_by` |

### Reuse from E2

| E2 Component | E3 Reuse |
|--------------|----------|
| `ConceptGraph` | Memory graph structure |
| `Concept` model | Memory concept model (extended) |
| `Relationship` types | Memory relationship types |
| BFS traversal | Query relevant memories |
| `ContextQuery` | `MemoryQuery` (same pattern) |

---

## In Scope

**MUST (V2 - Feb 9):**
- Create `.rai/` directory structure (hybrid md + jsonl)
- Create manifest.yaml with instance metadata
- Convert existing `.claude/rai/` content to JSONL format
- Extract Emilio relationship data to humans.jsonl
- Memory graph using E2's ConceptGraph infrastructure
- Memory extractors (pattern, insight, calibration, decision)
- CLI: `raise memory query "topic"` — returns relevant memories via graph
- CLI: `raise memory dump [--format md|json]` — export for human inspection
- Update /session-start to query memory graph
- Update /session-close to append JSONL + rebuild graph
- Type safety: all code type-annotated
- Tests: >90% coverage on new code

**SHOULD:**
- CLI: `raise memory add` — manual memory entry
- Graceful fallback if `.rai/` missing (create from template)
- Graph validation (detect orphan concepts)

---

## Out of Scope (V3 - Mar 14)

**Deferred to V3 (Commercial):**
- DatabaseMemoryBackend (PostgreSQL + pgvector)
- Vector similarity search
- Mem0 integration for semantic extraction
- Multi-user relationships
- Cross-project memory aggregation
- Auto-flush on token threshold
- RAG for long-term layer

---

## Done Criteria

### Per Feature
- [ ] Code implemented with type annotations
- [ ] Docstrings on all public APIs (Google-style)
- [ ] Component catalog updated (`dev/components.md`)
- [ ] Unit tests passing (>90% coverage on feature code)
- [ ] All quality checks pass (ruff, pyright, bandit)

### Epic Complete
- [ ] `.rai/` structure created (identity/ as md, memory/ as jsonl)
- [ ] Content migrated from `.claude/rai/` to JSONL format
- [ ] Memory graph builds successfully from JSONL
- [ ] `raise memory query` returns relevant results
- [ ] `raise memory dump --format md` produces readable output
- [ ] /session-start queries memory graph for context
- [ ] /session-close appends to JSONL and rebuilds graph
- [ ] Token savings measured (target: >80% vs loading all memory files)
- [ ] Epic retrospective completed (`/epic-close`)

---

## Dependencies

```
F3.1 (Identity Core Structure)
  ↓
F3.2 (Content Migration) ──────┐
  ↓                            │ (parallel possible)
F3.3 (Memory Graph) ◄──────────┘
  ↓
F3.4 (Memory Query CLI)
  ↓
F3.5 (Skills Integration)
```

**Blockers:** None (E2 complete, infrastructure available)

---

## Architecture References

| Decision | Document | Key Insight |
|----------|----------|-------------|
| Rai as Entity | ADR-013 | Memory is constitutive, not optional |
| Identity Core | ADR-014 | `.rai/` with four subdirs |
| Memory Infrastructure | ADR-015 | Dual backend, file-first |
| Memory Format | ADR-016 | JSONL for memory, Markdown for identity |
| Concept-level Graph | ADR-011 | 97% token savings via MVC |
| Skills + Toolkit | ADR-012 | Reusable infrastructure |

---

## Migration Mapping

| Current | New | Action |
|---------|-----|--------|
| `.claude/rai/identity.md` | `.rai/identity/core.md` | Refactor (keep md) |
| `.claude/RAI.md` | `.rai/identity/perspective.md` | Move (keep md) |
| `.claude/rai/memory.md` | `.rai/memory/patterns.jsonl` + `insights.jsonl` | **Convert to JSONL** |
| `.claude/rai/calibration.md` | `.rai/memory/calibration.jsonl` | **Convert to JSONL** |
| `.claude/rai/session-index.md` | `.rai/memory/sessions/index.jsonl` | **Convert to JSONL** |
| (embedded in RAI.md) | `.rai/relationships/humans.jsonl` | **Extract to JSONL** |
| (new) | `.rai/manifest.yaml` | Create |
| (new) | `.rai/identity/voice.md` | Create (md) |
| (new) | `.rai/identity/boundaries.md` | Create (md) |
| (new) | `.rai/memory/graph.json` | **Build from JSONL** |
| (new) | `.rai/growth/evolution.md` | Create (md) |
| (new) | `.rai/growth/questions.md` | Create (md) |

---

## Success Metrics

| Metric | Target | Validation |
|--------|--------|------------|
| Structure complete | identity/ (md) + memory/ (jsonl) | Directory check |
| Migration complete | All content converted | Diff review |
| Graph builds | Concepts extracted from JSONL | `raise memory query` works |
| Token savings | >80% vs raw files | Measure query output vs full load |
| Query relevance | Returns useful context | Manual validation |
| Dump readable | Human-friendly markdown | Visual check |
| Test coverage | >90% | pytest --cov |

---

## JSONL Schema Examples

### patterns.jsonl
```json
{"id": "PAT-001", "type": "pattern", "content": "Singleton with get/set/configure for module state", "context": ["testing", "module-design"], "learned_from": "F1.4", "created": "2026-01-31"}
{"id": "PAT-002", "type": "pattern", "content": "BFS traversal reuse across features", "context": ["architecture", "graph"], "learned_from": "F2.3", "created": "2026-01-31"}
```

### insights.jsonl
```json
{"id": "INS-001", "type": "insight", "content": "Kata cycles deliver 2-3x velocity", "evidence": ["F2.1", "F2.2", "F2.3"], "confidence": "high", "created": "2026-01-31"}
{"id": "INS-002", "type": "insight", "content": "Simple heuristics > ML for most cases", "evidence": ["F2.3-keyword-matching"], "confidence": "high", "created": "2026-01-31"}
```

### calibration.jsonl
```json
{"id": "CAL-001", "feature": "F2.1", "size": "S", "estimated_min": 120, "actual_min": 52, "ratio": 2.3, "notes": "Full kata cycle", "created": "2026-01-31"}
{"id": "CAL-002", "feature": "F2.2", "size": "S", "estimated_min": 180, "actual_min": 65, "ratio": 2.8, "notes": "Full kata cycle", "created": "2026-01-31"}
```

### humans.jsonl
```json
{"id": "HUM-001", "name": "Emilio", "preferences": {"communication": "direct", "commits": "HITL", "sizing": "t-shirt"}, "trust_level": "high", "history": ["E1", "E2"], "created": "2026-01-31"}
```

---

## Notes

### Why This Architecture

1. **"As above, so below"** — Same MVC pattern for governance (E2) and memory (E3)
2. **AI-native storage** — JSONL is structured, queryable, git-friendly
3. **Human inspection on-demand** — `dump` command, not constant sync overhead
4. **Reuses E2** — Graph infrastructure already proven
5. **Single write path** — No markdown/graph sync complexity

### Key Risks
- JSONL conversion may lose markdown nuance → Review migration carefully
- Graph query relevance depends on good concept extraction → Test with real queries
- Skills coupling to new format → Incremental rollout

### Velocity Assumption
- 2-3x based on E2 calibration
- E2 infrastructure reuse should accelerate F3.3
- 5 features × S size → ~3-5 hours total

---

## Implementation Plan

> Added by `/epic-plan` - 2026-02-01
> Strategy: **Risk-First** | Milestones: **2** | Demo: **All features for Feb 9**

### Feature Sequence (Risk-First)

| Order | Feature | Size | Dependencies | Milestone | Rationale |
|:-----:|---------|:----:|--------------|-----------|-----------|
| 1 | F3.1 Identity Core Structure | S | None | M1 | Foundation — blocks all others |
| 2 | F3.3 Memory Graph | S | F3.1 | M1 | **Highest risk** — validates E2 reuse early |
| 3 | F3.2 Content Migration | S | F3.3 (schema) | M2 | Depends on graph schema being defined |
| 4 | F3.4 Memory Query CLI | S | F3.2, F3.3 | M2 | Wires graph to CLI — straightforward |
| 5 | F3.5 Skills Integration | XS | F3.4 | M2 | Updates existing skills — minimal risk |

### Milestones

| Milestone | Features | Target | Success Criteria | Demo |
|-----------|----------|--------|------------------|------|
| **M1: Walking Skeleton** | F3.1, F3.3 | Day 3 (Feb 4) | `.rai/` exists, graph builds from test JSONL | Graph query returns memory concepts |
| **M2: Epic Complete** | All 5 features | Day 8 (Feb 9) | All done criteria met | `/session-start` queries graph, full CLI works |

### Updated Dependencies (Risk-First Order)

```
F3.1 (Identity Core Structure) ← CRITICAL PATH START
  ↓
F3.3 (Memory Graph) ← HIGHEST RISK - validate E2 reuse
  ↓ (schema defined)
F3.2 (Content Migration)
  ↓
F3.4 (Memory Query CLI)
  ↓
F3.5 (Skills Integration) ← CRITICAL PATH END
```

### Parallel Work Streams

```
Time →
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Day 1-2:  F3.1 ────► F3.3 (graph)
                        ↓ (schema defined)
Day 3-4:              F3.2 (migration) ────► F3.4 (CLI)
Day 5-6:                                       ↓
                                            F3.5 (skills)
Day 7-8:  Buffer / polish / epic close
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
         M1: Walking Skeleton              M2: Epic Complete
              (Day 3)                          (Day 8)
```

**Note:** Limited parallelism due to single developer. F3.2 starts after F3.3 defines schema.

### Progress Tracking

| Feature | Size | Status | Actual | Velocity | Notes |
|---------|:----:|:------:|:------:|:--------:|-------|
| F3.1 Identity Core Structure | S | Pending | - | - | |
| F3.3 Memory Graph | S | Pending | - | - | |
| F3.2 Content Migration | S | Pending | - | - | |
| F3.4 Memory Query CLI | S | Pending | - | - | |
| F3.5 Skills Integration | XS | Pending | - | - | |

**Milestone Progress:**
- [ ] M1: Walking Skeleton (Feb 4)
- [ ] M2: Epic Complete (Feb 9)

### Sequencing Rationale

**F3.1 → F3.3 (Risk-First):**
- F3.3 is highest uncertainty — does E2's ConceptGraph work for memory concepts?
- If graph reuse fails, we learn on Day 2, not Day 5
- Graph schema informs JSONL structure for F3.2

**F3.3 before F3.2:**
- Original order was F3.2 → F3.3 (migration before graph)
- Risk-First reverses: define graph schema first, then migrate to match
- Avoids rework if graph needs different structure

**F3.5 last:**
- Lowest risk (updating existing skills)
- Can demo CLI without skills integration
- If time runs short, manual `/session-start` is acceptable fallback

### Sequencing Risks

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| E2 ConceptGraph doesn't fit memory concepts | Medium | High | Spike first 30min of F3.3; pivot to simpler graph if needed |
| JSONL schema needs iteration after migration starts | Medium | Medium | Define schema in F3.3 before F3.2; test with sample data |
| Skills integration breaks existing session flow | Low | Medium | Keep `.claude/rai/` as fallback until validated |

### Velocity Assumptions

- **Baseline:** 2.3-2.8x multiplier with kata cycle (from E2 calibration)
- **E2 reuse factor:** F3.3 should benefit from proven patterns
- **Buffer:** 2 days for integration, polish, and epic close
- **Estimated total:** ~4-5 hours implementation + buffer

### Timeline

| Day | Date | Features | Cumulative |
|:---:|------|----------|:----------:|
| 1 | Feb 2 | F3.1 | 20% |
| 2 | Feb 3 | F3.3 | 40% |
| 3 | Feb 4 | F3.2 | 60% — **M1 Walking Skeleton** |
| 4-5 | Feb 5-6 | F3.4 | 80% |
| 6 | Feb 7 | F3.5 | 100% |
| 7-8 | Feb 8-9 | Buffer, polish, `/epic-close` | **M2 Epic Complete** |

---

*Epic tracking - update per feature completion*
*Created: 2026-02-01*
*Architecture revised: 2026-02-01 (JSONL + Graph model)*
*Implementation plan added: 2026-02-01 (Risk-First, 2 milestones)*
