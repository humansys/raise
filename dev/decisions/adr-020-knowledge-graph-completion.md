---
id: "ADR-020"
title: "Knowledge Graph Completion - Extended Node Types and Bidirectional Memory"
date: "2026-02-03"
status: "Accepted"
related_to: ["ADR-019", "ADR-011", "ADR-016"]
supersedes: []
research: "Session analysis (2026-02-03)"
---

# ADR-020: Knowledge Graph Completion

## Context

### The Problem

ADR-019 established the unified context graph with 9 node types. However, session analysis revealed:

1. **Missing governance data** — 40+ ADRs exist but skills can't query them
2. **Query/type mismatches** — Skills ask for "ADR" but type doesn't exist
3. **Read-only memory** — Skills query patterns but can't write them
4. **Generic queries** — All phases use same query, wasting context

**Concrete impact:**
```bash
# This fails today (2026-02-03):
raise context query "ADR architecture" --unified --types decision
# ValidationError: 'decision' is not a valid type
```

### Current State (E11 Complete)

**Available node types:**
- pattern, calibration, session (memory)
- principle, requirement, outcome (governance)
- epic, feature (work)
- skill (process)

**Missing node types:**
- `decision` (ADRs) — 40+ files in `dev/decisions/`
- `guardrail` (code standards) — `governance/solution/guardrails.md`
- `term` (glossary) — `framework/reference/glossary.md`

### Impact on Feature Cycle

| Skill | Queries For | Can't Find |
|-------|-------------|------------|
| /story-design | "architecture ADR" | ADRs (type doesn't exist) |
| /story-implement | "testing guardrails" | Guardrails (not extracted) |
| /story-review | calibration for comparison | Works, but not queried |

## Decision

**Extend the unified graph with three new node types and add bidirectional memory flow.**

### New Node Types

```python
# Extended NodeType literal
NodeType = Literal[
    # Existing (E11)
    "pattern", "calibration", "session",
    "principle", "requirement", "outcome",
    "epic", "feature", "skill",
    # New (E12)
    "decision",    # ADRs
    "guardrail",   # Code standards
    "term",        # Glossary entries
]
```

### Architecture Extension

```
┌──────────────────────────────────────────────────────────────┐
│                    Unified Context Graph                      │
│                    (.raise/graph/unified.json)                │
│                                                               │
│  MEMORY:        pattern, calibration, session                 │
│  GOVERNANCE:    principle, requirement, outcome               │
│  WORK:          epic, feature                                 │
│  PROCESS:       skill                                         │
│  NEW (E12):     decision, guardrail, term                     │
│                                                               │
│  New Edges:                                                   │
│  ├── supersedes     — decision → decision (ADR evolution)    │
│  ├── enforces       — guardrail → principle (compliance)     │
│  └── defines        — term → concept (terminology)           │
└──────────────────────────────────────────────────────────────┘
```

### Bidirectional Memory Flow

**Current (read-only):**
```
/session-close → patterns.jsonl → graph build → /session-start
                 (only entry point)
```

**New (bidirectional):**
```
/story-review → raise memory add-pattern → patterns.jsonl → graph
/session-close  → raise memory add-pattern → patterns.jsonl → graph
                  (multiple entry points, immediate persistence)
```

### Parser Reuse Pattern

Following PAT-038 (parser modules are reusable):

```python
# Same pattern as constitution.py, prd.py, vision.py
def extract_decisions(file_path: Path, project_root: Path) -> list[Concept]:
    """Extract ADR concepts from decision markdown files."""
    ...

def extract_guardrails(file_path: Path, project_root: Path) -> list[Concept]:
    """Extract guardrail concepts from guardrails.md."""
    ...

def extract_terms(file_path: Path, project_root: Path) -> list[Concept]:
    """Extract term concepts from glossary.md."""
    ...
```

## Consequences

### Positive

1. **Complete MVC for story cycle** — Every skill gets relevant context
2. **ADRs queryable** — `/story-design` sees prior architecture decisions
3. **Immediate learning** — Patterns persist during work, not just at session end
4. **Phase-appropriate context** — Design gets ADRs, implement gets guardrails
5. **Reuses existing infrastructure** — Same extractors, same graph, same query

### Negative

1. **Schema change** — NodeType literal must be extended (breaking if strict)
2. **Extractor maintenance** — Three new parsers to maintain
3. **Graph size increase** — ~50-100 new nodes (still <500 total)

### Neutral

1. **ADR format variance** — v1, v2, root formats need flexible parsing
2. **Guardrails structure** — May evolve; parser should be resilient
3. **Memory write deduplication** — Need to handle duplicate pattern detection

## Implementation (E12)

| Feature | Description | Size |
|---------|-------------|:----:|
| F12.1 | ADR Extractor | M |
| F12.2 | Guardrails Extractor | S |
| F12.3 | Glossary Extractor | S |
| F12.4 | Skill Query Alignment | S |
| F12.5 | Phase-Specific MVC | M |
| F12.6 | Memory Write from Skills | M |

**Total:** ~10-12 SP

## Alternatives Considered

### Alternative 1: Embed ADRs in CLAUDE.md

Include ADR summaries directly in CLAUDE.md for preload.

**Rejected because:**
- CLAUDE.md becomes bloated
- Can't query specific ADRs
- Redundant with source files
- Violates DRY principle

### Alternative 2: Separate ADR Graph

Build a separate ADR-specific graph.

**Rejected because:**
- Violates ADR-019 (unified > federated)
- Can't relate ADRs to patterns, features
- More maintenance overhead
- Fragments query interface

### Alternative 3: No Memory Write (Keep Read-Only)

Keep patterns.jsonl write-only via /session-close.

**Rejected because:**
- Learnings during features are lost if session crashes
- Delay between learning and persistence
- /story-review should capture patterns immediately
- Contradicts "continuous improvement" principle

## Validation

### Success Criteria

| Metric | Target |
|--------|--------|
| Decision nodes in graph | 40+ (all ADRs extracted) |
| Guardrail nodes | 5-10 (one per section) |
| Term nodes | 20+ (glossary entries) |
| Query latency | <100ms (unchanged) |
| Skill queries succeed | 100% (no type errors) |

### Test Cases

```bash
# ADR query works
raise context query "architecture graph" --unified --types decision
# Returns: ADR-011, ADR-019, ADR-020

# Guardrail query works
raise context query "testing coverage" --unified --types guardrail
# Returns: guardrail-testing section

# Memory write works
raise memory add-pattern "Parser modules are reusable" --context testing
# Adds to patterns.jsonl immediately
```

## References

- **ADR-019:** Unified Context Graph Architecture (foundation)
- **ADR-011:** Concept-level graph architecture (MVC design)
- **ADR-016:** Memory format (JSONL + graph)
- **PAT-038:** Parser modules are reusable (1.5x velocity on second parser)
- **Session analysis:** Memory recall assessment (2026-02-03)

---

**Status**: Proposed (2026-02-03)

**Next steps**:
1. Review and approve ADR
2. Implement F12.1 (ADR extractor)
3. Extend NodeType in models
4. Update UnifiedGraphBuilder
