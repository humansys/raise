---
id: F11.3
title: Unified Context Query
epic: E11
size: S
sp: 2
status: design
created: 2026-02-03
---

# F11.3: Unified Context Query

## Problem

Skills need to query accumulated context (patterns, calibration, governance, work) at invocation time. Currently `raise context query` only queries the governance graph. There's no way to query the unified graph that F11.2 builds.

## Value

**For Rai:** Every skill starts with relevant context — patterns learned, principles that govern, calibration data for estimates. No re-discovery.

**For RaiSE Engineers:** One command to retrieve cross-domain context. Validates the unified graph investment.

## Approach

Extend the existing `raise context query` command to support `--unified` flag, querying the unified graph instead of governance-only graph.

**Components affected:**
- `src/raise_cli/context/query.py` — **CREATE** — UnifiedContextQuery engine
- `src/raise_cli/cli/commands/context.py` — **MODIFY** — Add `--unified` flag

**Pattern reuse:**
- Copy engine pattern from `governance/query/engine.py`
- Reuse `estimate_tokens` from `governance/query/formatters.py`
- Use existing `UnifiedGraph.get_neighbors()` for BFS

## Examples

### CLI Usage

```bash
# Query unified graph for planning-related context
raise context query "planning estimation" --unified

# Filter by node types
raise context query "planning" --unified --types pattern,calibration

# Limit traversal depth
raise context query "PAT-001" --unified --max-depth 2

# JSON output for programmatic use
raise context query "story-plan" --unified --format json
```

### Expected Output (Human Format)

```
Querying unified context graph for: planning estimation
Strategy: keyword_search

# Unified Context Results

**Query:** `planning estimation`
**Concepts:** 5 | **Tokens:** ~320 | **Depth:** 1

---

## PAT-042: Kata-optimized estimation
**Type:** pattern | **Source:** .rai/memory/patterns.jsonl

Apply 0.5x multiplier to estimates when using full kata cycle.
Learned from F2.1-F2.3 where velocity was 2-3.5x estimates.

---

## CAL-007: F2.1 Concept Extraction
**Type:** calibration | **Source:** .rai/memory/calibration.jsonl

Size: S | Est: 180m | Actual: 52m | Velocity: 3.5x

---

## /story-plan
**Type:** skill | **Source:** .claude/skills/story-plan/SKILL.md

Decompose user stories into atomic executable tasks.
**Needs context:** pattern, calibration, feature

---

**Query Metadata:**
- Execution time: 8.32ms
- Token estimate: ~320
- Concepts by type: pattern=2, calibration=2, skill=1
```

### Expected Output (JSON Format)

```json
{
  "concepts": [
    {
      "id": "PAT-042",
      "type": "pattern",
      "content": "Apply 0.5x multiplier to estimates...",
      "source_file": ".rai/memory/patterns.jsonl",
      "created": "2026-02-01",
      "metadata": {"sub_type": "process"}
    }
  ],
  "metadata": {
    "query": "planning estimation",
    "total_concepts": 5,
    "token_estimate": 320,
    "execution_time_ms": 8.32,
    "types_found": {"pattern": 2, "calibration": 2, "skill": 1}
  }
}
```

### Query Module API

```python
from raise_cli.context.query import UnifiedQueryEngine, UnifiedQuery

# Load engine from graph file
engine = UnifiedQueryEngine.from_file(Path(".raise/graph/unified.json"))

# Keyword search
result = engine.query(UnifiedQuery(
    query="planning estimation",
    strategy="keyword_search",
    max_depth=1,
))

# Direct concept lookup with BFS
result = engine.query(UnifiedQuery(
    query="PAT-042",
    strategy="concept_lookup",
    max_depth=2,
    types=["pattern", "calibration"],
))

# Access results
for concept in result.concepts:
    print(f"{concept.id}: {concept.content[:50]}...")

print(f"Tokens: ~{result.metadata.token_estimate}")
```

## Acceptance Criteria

### MUST

- [ ] `raise context query "<query>" --unified` queries unified graph
- [ ] Keyword search matches against node content (case-insensitive)
- [ ] `--types` flag filters by node type (comma-separated)
- [ ] `--max-depth` controls BFS traversal depth (default 1)
- [ ] `--format json` outputs JSON for programmatic use
- [ ] Returns token estimate in metadata

### SHOULD

- [ ] Relevance ranking considers keyword frequency + recency
- [ ] Human output groups by node type
- [ ] Shows "Needs context" from skill metadata

### MUST NOT

- [ ] Break existing `raise context query` (governance) behavior
- [ ] Require graph rebuild on every query (load from file)
- [ ] Include concepts with no keyword matches in keyword_search

## Technical Notes

**Query strategies (subset of governance query):**

| Strategy | Behavior |
|----------|----------|
| `keyword_search` | Match keywords in node content, return top N |
| `concept_lookup` | Direct ID lookup + BFS neighbors |

**Relevance scoring (simple first):**
```
score = keyword_hits * 10 + recency_bonus
recency_bonus = 5 if created within 7 days else 0
```

**Graph file location:** `.raise/graph/unified.json` (from F11.2)

## Out of Scope

- Vector embeddings / semantic search (add later if keyword insufficient)
- New query strategies beyond keyword_search and concept_lookup
- Auto-rebuild graph if stale (manual `raise graph build --unified`)

## References

- Epic: `dev/epic-e11-scope.md`
- ADR: `dev/decisions/adr-019-unified-context-graph.md`
- Pattern reuse: `src/raise_cli/governance/query/`
- Graph class: `src/raise_cli/context/graph.py`
