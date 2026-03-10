---
id: "ADR-016"
title: "Memory Format: JSONL + Graph (Not Markdown)"
date: "2026-02-01"
status: "Accepted"
related_to: ["ADR-014", "ADR-015", "ADR-011"]
supersedes: []
---

# ADR-016: Memory Format: JSONL + Graph (Not Markdown)

## Context

### The Question

ADR-014 defined the Identity Core structure with four subdirectories. ADR-015 defined dual-backend memory infrastructure. But neither specified the **file format** for the memory layer.

Options:
- **A) Markdown everywhere** — Human-readable, current approach
- **B) JSONL for memory, Markdown for identity** — Machine-native for memory, human-native for identity
- **C) Database only** — Skip files entirely

### The Insight

During E3 design, we realized:

> "Markdown is for humans, JSONL/Graph is for AI. We've been doing it backwards."

Current approach (markdown memory) requires:
1. AI parses unstructured markdown
2. AI extracts patterns from prose
3. AI struggles with consistency

Proposed approach (JSONL + Graph):
1. AI writes structured JSONL
2. AI queries graph directly
3. Human exports to markdown on demand

### The Parallel

This mirrors E2's governance approach:
- Governance: Markdown files → Extract concepts → Build graph → Query graph
- Memory: Sessions happen → Extract learnings → Append JSONL → Build graph → Query graph

Same MVC pattern, 97% token savings proven in E2.

## Decision

**Use JSONL for memory layer, Markdown for identity layer.**

### Format by Layer

| Layer | Format | Rationale |
|-------|--------|-----------|
| **Identity** | Markdown | Human-authored, philosophical, rarely changes |
| **Memory** | JSONL + Graph | Machine-managed, frequently updated, queryable |
| **Relationships** | JSONL | Structured preferences, history |
| **Growth** | Markdown | Reflective, human milestones |

### Write Path

```
Session work happens
    ↓
/session-close (or manual)
    ↓
Extract: patterns, insights, calibration
    ↓
Append to JSONL files
    ↓
Rebuild graph index
    ↓
Done. No markdown sync.

Human inspection?
    ↓
rai memory dump --format md
```

### File Structure

```
.rai/
├── identity/           # MARKDOWN (human-authored)
│   ├── core.md
│   ├── perspective.md
│   ├── voice.md
│   └── boundaries.md
│
├── memory/             # JSONL + GRAPH (machine-managed)
│   ├── patterns.jsonl
│   ├── insights.jsonl
│   ├── calibration.jsonl
│   ├── graph.json      # Built from JSONL
│   └── sessions/
│       └── *.jsonl
│
├── relationships/      # JSONL (structured)
│   └── humans.jsonl
│
└── growth/             # MARKDOWN (reflective)
    ├── evolution.md
    └── questions.md
```

### JSONL Schema

```json
// patterns.jsonl
{"id": "PAT-001", "type": "pattern", "content": "...", "context": ["testing"], "learned_from": "F1.4", "created": "2026-01-31"}

// insights.jsonl
{"id": "INS-001", "type": "insight", "content": "...", "evidence": ["F2.1"], "confidence": "high", "created": "2026-01-31"}

// calibration.jsonl
{"id": "CAL-001", "feature": "F2.1", "size": "S", "estimated_min": 120, "actual_min": 52, "ratio": 2.3, "created": "2026-01-31"}
```

## Consequences

### Positive

1. **Single write path** — No markdown/graph sync complexity
2. **AI-native format** — JSONL is structured, queryable
3. **Git-friendly** — JSONL diffs well, append-only
4. **Reuses E2** — Same graph infrastructure
5. **Token efficient** — Query graph, not parse prose
6. **Human inspection on-demand** — `dump` command exports readable format

### Negative

1. **Less immediately readable** — Must run `dump` for human view
2. **Migration effort** — Convert existing markdown to JSONL
3. **Schema evolution** — JSONL needs versioning strategy

### Neutral

1. **Identity stays markdown** — Best of both worlds
2. **Growth stays markdown** — Reflective content is human-authored

## Validation

### Token Savings Test

Same as E2 governance:
- Load full markdown memory: ~15,000 tokens
- Query graph for relevant context: ~500-1,500 tokens
- Savings: >80% (target)

### Write Path Test

```bash
# Session close appends to JSONL
rai memory add pattern "New pattern" --context testing

# Verify append
tail -1 .rai/memory/patterns.jsonl

# Rebuild graph
rai memory rebuild

# Query works
rai memory query "testing patterns"
```

## Implementation

Part of E3 (Identity Core + Memory Graph):
- F3.1: Create structure with correct formats
- F3.2: Migrate markdown → JSONL
- F3.3: Build graph from JSONL
- F3.4: CLI commands for query/dump

## Alternatives Considered

### Alternative 1: Markdown Everywhere

**Rejected because:**
- Requires constant parsing
- Sync complexity between formats
- Not optimized for AI consumption

### Alternative 2: Database Only

**Rejected because:**
- Loses file inspectability
- Requires setup for open source
- Overkill for single-user local

### Alternative 3: JSON (not JSONL)

**Rejected because:**
- JSONL is append-friendly (no read-modify-write)
- JSONL diffs better in git
- JSONL handles large datasets without loading all

## References

- **ADR-014**: Identity Core Structure
- **ADR-015**: Memory Infrastructure
- **ADR-011**: Concept-level Graph (97% savings)
- **E3 Scope**: `dev/epic-e3-scope.md`

---

**Status**: Accepted (2026-02-01)

**Approved by**: Emilio Osorio, Rai

**Impact**:
- Memory files use JSONL format
- Graph built from JSONL (same as E2)
- `rai memory dump` for human inspection
- Migration converts existing markdown
