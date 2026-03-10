---
story_id: S-RELEASE-ONTOLOGY
title: Add release as first-class ontology concept
size: S
status: design-complete
modules: [governance, context]
---

# Design: S-RELEASE-ONTOLOGY

## What & Why

**Problem:** Epics are flat — there's no concept above them. We can't group E19-E22 under "V3.0 Commercial Launch" in the ontology. Releases exist in every team tool (Jira Fix Versions, GitLab Milestones) but not in our graph.

**Value:** Enables V3 planning with proper ontology. Forward-compatible with Jira Fix Version sync (E21). Enterprise teams expect roadmap artifacts.

## Architectural Context

**Modules affected:**
- `mod-governance` (domain layer) — new parser, extractor wiring
- `mod-context` (integration layer) — NodeType, builder wiring, part_of edges

**Pattern:** Follows existing governance artifact → parser → extractor → graph builder chain.

## Approach

Add `release` to the ontology following the exact pattern used for every other concept type:

```
governance/roadmap.md → roadmap parser → governance extractor → graph builder → graph
```

### Impact Radius (8 files)

| File | Change | Type |
|------|--------|------|
| `src/rai_cli/context/models.py` | Add `"release"` to `NodeType` | Modify |
| `src/rai_cli/governance/models.py` | Add `RELEASE` to `ConceptType` | Modify |
| `src/rai_cli/governance/parsers/roadmap.py` | Parse `governance/roadmap.md` | **Create** |
| `src/rai_cli/governance/extractor.py` | Wire roadmap parser into `extract_with_result()` and `_infer_concept_type()` | Modify |
| `src/rai_cli/context/builder.py` | Add `_infer_release_part_of()` for epic → release edges | Modify |
| `governance/roadmap.md` | Governance artifact with release definitions | **Create** |
| `tests/governance/parsers/test_roadmap.py` | Parser unit tests | **Create** |
| `tests/context/test_builder_release.py` | Builder integration tests for release nodes + edges | **Create** |

## Examples

### governance/roadmap.md

```markdown
# Roadmap: raise-cli

> **Status:** Active
> **Date:** 2026-02-13

---

## Releases

| ID | Release | Target | Status | Epics |
|----|---------|--------|--------|-------|
| REL-V2.0 | V2.0 Open Core | 2026-02-15 | In Progress | E18 |
| REL-V3.0 | V3.0 Commercial Launch | 2026-03-14 | Planning | E19, E20, E21, E22 |

---

## REL-V3.0: V3.0 Commercial Launch

> **Target:** 2026-03-14
> **Status:** Planning
> **Objective:** BYOK trial offering with COMMUNITY/PRO/ENTERPRISE tiers

### Epics
- E19: V3 Product Design
- E20: Shared Memory Architecture
- E21: Platform Integration
- E22: Enterprise Readiness

### Milestones
- [ ] Tier definitions formalized (E19)
- [ ] Hosted infrastructure live (E20)
- [ ] Jira/Confluence integration demo-ready (E21)
- [ ] March 14 Atlassian webinar
```

### Parser Output

```python
# extract_releases("governance/roadmap.md") returns:
[
    Concept(
        id="rel-v3.0",
        type=ConceptType.RELEASE,
        file="governance/roadmap.md",
        section="REL-V3.0: V3.0 Commercial Launch",
        lines=(10, 10),
        content="V3.0 Commercial Launch — Planning. Target: 2026-03-14",
        metadata={
            "release_id": "REL-V3.0",
            "name": "V3.0 Commercial Launch",
            "target": "2026-03-14",
            "status": "planning",
            "epics": ["E19", "E20", "E21", "E22"],
        },
    ),
]
```

### Graph Edges (part_of)

```
epic-e19 --part_of--> rel-v3.0
epic-e20 --part_of--> rel-v3.0
epic-e21 --part_of--> rel-v3.0
epic-e22 --part_of--> rel-v3.0
```

Uses existing `part_of` edge type — same as story → epic.

### Release Node in Graph

```python
ConceptNode(
    id="rel-v3.0",
    type="release",       # NEW NodeType
    content="V3.0 Commercial Launch — Planning. Target: 2026-03-14",
    source_file="governance/roadmap.md",
    created="2026-02-13T...",
    metadata={
        "release_id": "REL-V3.0",
        "name": "V3.0 Commercial Launch",
        "target": "2026-03-14",
        "status": "planning",
        "epics": ["E19", "E20", "E21", "E22"],
    },
)
```

## Key Decisions

**D1: ID format** — `rel-v3.0` (lowercase, same pattern as `epic-e18`, `story-f18-1`).

**D2: Edge direction** — `epic --part_of--> release` (same direction as `story --part_of--> epic`). Consistent hierarchy.

**D3: Epic association source** — Release metadata contains `epics` list parsed from the roadmap table. The builder matches `epic-e{N}` nodes. If the epic node doesn't exist in the graph, the edge is silently skipped (same safety pattern as `_infer_part_of`).

**D4: No new EdgeType needed** — `part_of` already exists and is semantically correct for "epic is part of release."

**D5: Parser follows backlog parser pattern** — Table parsing with regex, same structure as `extract_epics()` in `parsers/backlog.py`. Predictable, testable, no new patterns.

**D6: Release detail sections are optional** — Parser extracts from the table (minimum). Detail sections under `## REL-X.X:` are human-readable but not parsed by MVP. Future: extract milestones, objectives.

## Acceptance Criteria

**MUST:**
- [ ] `"release"` exists in `NodeType` Literal
- [ ] `RELEASE` exists in `ConceptType` Enum
- [ ] `governance/roadmap.md` parser extracts releases from table
- [ ] Extractor wires roadmap parser into `extract_with_result()`
- [ ] Builder creates `part_of` edges from epic → release nodes
- [ ] `rai memory build` produces release nodes in graph
- [ ] Tests >90% coverage on new code

**SHOULD:**
- [ ] `_infer_concept_type()` handles `roadmap` filename
- [ ] Parser handles missing/empty epics column gracefully

**MUST NOT:**
- [ ] Break existing graph build (no regressions)
- [ ] Require changes to query engine (release nodes are queryable via existing `get_concepts_by_type`)
