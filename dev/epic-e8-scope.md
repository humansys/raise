# Epic E8: Work Tracking Graph - Scope

> **Status:** DESIGNED
> **Branch:** `feature/e8/work-tracking-graph`
> **Created:** 2026-02-02
> **Designed:** 2026-02-02 (informed by RES-ROVO-001)
> **Target:** Feb 9, 2026 (F&F pre-launch)
> **Priority:** P0 — Foundational for alignment

---

## Problem Statement

Today's session revealed a critical gap: Rai didn't know where the backlog was, consulted stale sources, and found duplicated/desynced information. This caused wasted time and incorrect assumptions.

**Root cause:** Work tracking (projects, epics, features) is not part of the queryable governance graph.

---

## Objective

Extend the governance graph to include work tracking concepts (projects, epics, features, status). This enables:

1. **Unambiguous queries:** `raise context query "current work"` → clear answer
2. **Single source of truth:** Each level has one owner
3. **Foundation for V3:** Internal representation for Jira/Confluence integration

**Value proposition:** Without this, Rai and RaiSE Engineers lose alignment. With it, the graph becomes the canonical source for both governance AND work state.

---

## Architecture Decision: V3-Compatible Design (ADR-017)

**Decision:** Design work concepts to be compatible with Atlassian Teamwork Graph while keeping RaiSE terminology.

**Rationale:** (from RES-ROVO-001)
- Atlassian Teamwork Graph uses: Project, Work Item (Epic/Story/Task), Document
- RaiSE uses: Project, Epic, Feature — these map cleanly
- Terminology conversion happens at integration time (V3), not in internal model
- Our "Feature" (15-90 min) maps to Jira Story or Task depending on team config

**Consequences:**
- Keep `ProjectConcept`, `EpicConcept`, `FeatureConcept` names
- Add `external_id`, `external_url` fields for future sync
- Design parsers as adapters (interface-first) for future `JiraAdapter`
- Status enum includes RaiSE-specific states (DRAFT, DEFERRED)

---

## Concepts to Add

### New Concept Types

Extend `ConceptType` enum in `governance/models.py`:

```python
class ConceptType(str, Enum):
    # Existing
    REQUIREMENT = "requirement"
    OUTCOME = "outcome"
    PRINCIPLE = "principle"
    PATTERN = "pattern"
    PRACTICE = "practice"
    # NEW: Work tracking
    PROJECT = "project"
    EPIC = "epic"
    FEATURE = "feature"
```

### Work Status Enum

New shared status for work items (Jira-compatible):

```python
class WorkStatus(str, Enum):
    """Status values for work items, aligned with Jira workflows."""
    DRAFT = "draft"           # RaiSE-specific (pre-Jira)
    PENDING = "pending"       # → "To Do" in Jira
    IN_PROGRESS = "in_progress"  # → "In Progress" in Jira
    COMPLETE = "complete"     # → "Done" in Jira
    DEFERRED = "deferred"     # RaiSE-specific
```

### Node Properties (via metadata)

All work concepts use existing `Concept` model with type-specific metadata:

**Project metadata:**
```python
{
    "name": "raise-cli",
    "current_epic": "E8",  # For current_focus relationship
    "target_date": "2026-02-09",
    "epic_count": 9,
    "status": "active"
}
```

**Epic metadata:**
```python
{
    "epic_id": "E8",
    "name": "Work Tracking Graph",
    "status": "draft",
    "target_date": "2026-02-09",
    "feature_count": 4,
    "completion_percent": 0.0,
    "scope_doc": "dev/epic-e8-scope.md",
    # V3 fields (optional)
    "external_id": None,
    "external_url": None
}
```

**Feature metadata:**
```python
{
    "feature_id": "F8.1",
    "name": "Backlog Parser",
    "status": "pending",
    "size": "S",
    "story_points": 2,
    "epic_id": "E8",
    # V3 fields (optional)
    "external_id": None,
    "external_url": None
}
```

### New Relationship Types

Extend `RelationshipType` in `governance/graph/models.py`:

```python
RelationshipType = Literal[
    # Existing
    "implements",
    "governed_by",
    "depends_on",
    "related_to",
    "validates",
    # NEW: Work hierarchy
    "contains",      # Project contains Epic, Epic contains Feature
    "blocks",        # Feature blocks Feature (dependency)
    "current_focus", # Project's current epic
]
```

**Note:** Using `contains` instead of `has_epic`/`has_feature` — more generic, aligns with Teamwork Graph's `parent_of` semantic.

---

## Features

| ID | Feature | Size | SP | Description |
|----|---------|:----:|:--:|-------------|
| F8.1 | **Backlog Parser** | S | 2 | Parse `governance/projects/*/backlog.md` → Project + Epic index |
| F8.2 | **Epic Parser** | S | 2 | Parse `dev/epic-*-scope.md` → Epic + Features |
| F8.3 | **Graph Extension** | S | 2 | Add work concepts to ConceptGraph, relationships |
| F8.4 | **Work Queries** | S | 2 | `raise context query "current epic"`, `"E8 features"` |

**Total:** 4 features, 8 SP, ~4-6 hours with kata cycle

---

## Architecture

### Parser Interface (Adapter Pattern)

Design for future extensibility:

```python
# governance/parsers/base.py
from abc import ABC, abstractmethod
from pathlib import Path
from raise_cli.governance.models import Concept

class WorkItemParser(ABC):
    """Base interface for work item parsers.

    Designed as adapter pattern for future Jira/GitHub integration.
    """

    @abstractmethod
    def extract_projects(self, root: Path) -> list[Concept]:
        """Extract project concepts from source."""
        ...

    @abstractmethod
    def extract_epics(self, root: Path) -> list[Concept]:
        """Extract epic concepts from source."""
        ...

    @abstractmethod
    def extract_features(self, epic_path: Path) -> list[Concept]:
        """Extract feature concepts from epic source."""
        ...
```

### Local Markdown Parsers

```python
# governance/parsers/backlog.py
class BacklogParser(WorkItemParser):
    """Parse local markdown backlog files."""

    def extract_projects(self, root: Path) -> list[Concept]:
        """Parse governance/projects/*/backlog.md → Project concepts."""
        ...

    def extract_epics(self, root: Path) -> list[Concept]:
        """Extract epic index from backlog.md tables."""
        ...

# governance/parsers/epic.py
class EpicScopeParser(WorkItemParser):
    """Parse local epic scope documents."""

    def extract_features(self, epic_path: Path) -> list[Concept]:
        """Parse dev/epic-*-scope.md → Feature concepts."""
        ...
```

### Extended Graph

```
┌─────────────────────────────────────────────────────────────┐
│                      ConceptGraph                            │
├─────────────────────────────────────────────────────────────┤
│  Governance Layer (existing E2)                              │
│  ├── Requirements (PRD)     → req-rf-01, req-rf-02, ...     │
│  ├── Principles (Constitution) → principle-§1, ...          │
│  └── Outcomes (Vision)       → outcome-context-gen, ...     │
├─────────────────────────────────────────────────────────────┤
│  Work Layer (NEW E8)                                         │
│  ├── Projects (backlog.md)   → project-raise-cli            │
│  ├── Epics (epic-*-scope.md) → epic-e8, epic-e7, ...        │
│  └── Features (inside epics) → feature-f8.1, feature-f8.2   │
├─────────────────────────────────────────────────────────────┤
│  Relationships                                               │
│  ├── implements, governed_by, depends_on, related_to (E2)   │
│  └── contains, blocks, current_focus (NEW E8)               │
└─────────────────────────────────────────────────────────────┘
```

### Relationship Inference

Extend `governance/graph/relationships.py`:

```python
def infer_work_relationships(concepts: list[Concept]) -> list[Relationship]:
    """Infer relationships between work concepts."""
    relationships = []

    projects = [c for c in concepts if c.type == ConceptType.PROJECT]
    epics = [c for c in concepts if c.type == ConceptType.EPIC]
    features = [c for c in concepts if c.type == ConceptType.FEATURE]

    # 1. Project contains Epic (from backlog.md table)
    for project in projects:
        for epic in epics:
            if epic.metadata.get("project_id") == project.metadata.get("name"):
                relationships.append(Relationship(
                    source=project.id,
                    target=epic.id,
                    type="contains",
                    metadata={"confidence": 1.0, "method": "explicit"}
                ))

    # 2. Epic contains Feature (from epic scope Features table)
    for epic in epics:
        epic_id = epic.metadata.get("epic_id")
        for feature in features:
            if feature.metadata.get("epic_id") == epic_id:
                relationships.append(Relationship(
                    source=epic.id,
                    target=feature.id,
                    type="contains",
                    metadata={"confidence": 1.0, "method": "explicit"}
                ))

    # 3. current_focus (from backlog "Current Focus" section)
    for project in projects:
        current_epic_id = project.metadata.get("current_epic")
        if current_epic_id:
            epic = next((e for e in epics if e.metadata.get("epic_id") == current_epic_id), None)
            if epic:
                relationships.append(Relationship(
                    source=project.id,
                    target=epic.id,
                    type="current_focus",
                    metadata={"confidence": 1.0, "method": "explicit"}
                ))

    # 4. Feature implements Requirement (keyword matching)
    requirements = [c for c in concepts if c.type == ConceptType.REQUIREMENT]
    for feature in features:
        for req in requirements:
            # Match F8.1 description to RF-XX keywords
            ...

    return relationships
```

---

## Query Examples

```bash
# Current focus
$ raise context query "current work"
Project: raise-cli
Current Epic: E8 Work Tracking Graph (DRAFT)
Target: Feb 9, 2026
Next: F8.1 Backlog Parser

# Epic details (relationship traversal)
$ raise context query "E8" --strategy relationship_traversal
Epic: E8 Work Tracking Graph
Status: DRAFT | Target: Feb 9, 2026
Features:
  - F8.1 Backlog Parser [PENDING] (S)
  - F8.2 Epic Parser [PENDING] (S)
  - F8.3 Graph Extension [PENDING] (S)
  - F8.4 Work Queries [PENDING] (S)
Completion: 0/4 (0%)

# Feature lookup
$ raise context query "F8.1"
Feature: F8.1 Backlog Parser
Epic: E8 Work Tracking Graph
Status: PENDING | Size: S | SP: 2
Description: Parse governance/projects/*/backlog.md → Project + Epic index

# What implements a requirement
$ raise context query "RF-05" --edge-types implements
Requirement: RF-05 (Golden Context Generation)
Implemented by:
  - F4.1 Governance Loader [COMPLETE]
  - F4.2 CLAUDE.md Generator [COMPLETE via skill]
```

---

## File Changes Required

### New Files

```
src/raise_cli/governance/parsers/
├── base.py             # NEW: WorkItemParser interface
├── backlog.py          # NEW: BacklogParser
└── epic.py             # NEW: EpicScopeParser
```

### Modified Files

```
src/raise_cli/governance/
├── models.py           # EXTEND: ConceptType (PROJECT, EPIC, FEATURE)
├── extractor.py        # EXTEND: extract_work_concepts()

src/raise_cli/governance/graph/
├── models.py           # EXTEND: RelationshipType (contains, blocks, current_focus)
├── builder.py          # EXTEND: build_work_layer()
└── relationships.py    # EXTEND: infer_work_relationships()

src/raise_cli/governance/query/
└── strategies.py       # EXTEND: work-aware query strategies
```

---

## Backlog Format Requirements

For reliable parsing, backlog.md should follow this structure:

```markdown
# Backlog: {project-name}

> **Status**: Active
> **Date**: YYYY-MM-DD

## 1. Epics Overview

| ID | Epic | Status | Scope Doc | Priority |
|----|------|--------|-----------|----------|
| E1 | Core Foundation | ✅ Complete | `dev/epic-e1-scope.md` | — |
| E8 | Work Tracking Graph | 📋 DRAFT | `dev/epic-e8-scope.md` | P0 |

**F&F Scope (Feb 9):** E8 → E7 → E9
```

**Parser extracts:**
- Project ID from filename (`governance/projects/{id}/backlog.md`)
- Epic index from "Epics Overview" table
- Current focus from "F&F Scope" line or explicit "Current Focus" section
- Target date from frontmatter or context

---

## Epic Scope Format Requirements

Epic scope docs should have parseable feature table:

```markdown
# Epic E{N}: {Name} - Scope

> **Status:** DRAFT | IN PROGRESS | COMPLETE
> **Target:** YYYY-MM-DD

## Features

| ID | Feature | Size | SP | Description |
|----|---------|:----:|:--:|-------------|
| F8.1 | Backlog Parser | S | 2 | Parse backlog.md |
```

**Parser extracts:**
- Epic ID from filename (`dev/epic-{id}-scope.md`)
- Epic name from H1 heading
- Status from frontmatter
- Target date from frontmatter
- Features from "Features" table

---

## In Scope

**MUST:**
- [ ] `ConceptType` extended with PROJECT, EPIC, FEATURE
- [ ] `WorkStatus` enum with Jira-compatible values
- [ ] `BacklogParser` extracts projects and epic index
- [ ] `EpicScopeParser` extracts epic details and features
- [ ] Graph includes work concepts with `contains` relationships
- [ ] `raise context query "E8"` returns epic with features
- [ ] `raise context query "current work"` returns project focus

**SHOULD:**
- [ ] `--type epic` filter for queries
- [ ] Status filtering (`--status in_progress`)
- [ ] Feature `blocks` relationships (from dependency sections)
- [ ] Feature `implements` requirement (keyword inference)

---

## Out of Scope (V3 / Post-MVP)

| Item | Reason | Destination |
|------|--------|-------------|
| Jira/Confluence integration | V3 scope | Post Feb-15 |
| Bidirectional sync | V3 scope | Post Feb-15 |
| Team/assignee tracking | V3 scope | Post Feb-15 |
| Sprint management | V3 scope | Post Feb-15 |
| Burndown/velocity charts | E9 Telemetry | E9 |

---

## Done Criteria

### Per Feature

- [ ] Code implemented with type annotations
- [ ] Docstrings on all public APIs (Google-style)
- [ ] Component catalog updated (`dev/components.md`)
- [ ] Unit tests passing (>90% coverage on feature code)
- [ ] All quality checks pass (ruff, pyright, bandit)

### Epic Complete

- [ ] `raise graph build` includes work concepts
- [ ] `raise context query "current epic"` returns correct answer
- [ ] `raise context query "E8 features"` returns feature list
- [ ] No more "where is the backlog?" confusion
- [ ] Existing governance queries still work (no regression)
- [ ] Tests: >90% coverage on new parsers
- [ ] ADR-017 created (V3-compatible design)
- [ ] Epic merged to v2

---

## Dependencies

```
E2 Governance Toolkit ← COMPLETE (infrastructure exists)
    ↓ (provides ConceptGraph, parsers pattern, query engine)
E8 Work Tracking Graph ← THIS EPIC
    ↓ (enables work-aware queries)
E7 Onboarding (can use graph for status)
    ↓
E9 Telemetry (queries graph for metrics)
```

**Internal dependencies:**
```
F8.1 (Backlog Parser) ──┐
                        ├──► F8.3 (Graph Extension)
F8.2 (Epic Parser) ─────┘           │
                                    ▼
                            F8.4 (Work Queries)
```

**External blockers:** None

---

## Success Metrics

| Metric | Target | Validation |
|--------|--------|------------|
| Query "current work" accuracy | 100% | Manual test |
| Parse existing epic scopes | All 6 (E1, E2, E3, E7, E8, E9) | Automated test |
| Parse backlog.md | All projects | Automated test |
| No regression on governance queries | All existing tests pass | CI |
| Test coverage | >90% on new code | pytest --cov |

---

## Architecture References

| Decision | Document | Key Insight |
|----------|----------|-------------|
| Concept-level graph | ADR-011 | 97% token savings via MVC |
| Skills + Toolkit | ADR-012 | Parsers as toolkit, skills orchestrate |
| V3-compatible design | ADR-017 (new) | Teamwork Graph alignment, adapter pattern |
| Atlassian research | RES-ROVO-001 | MCP integration, terminology mapping |

---

## Notes

### Why This Epic (Problem Validation)

2026-02-02 session revealed:
- Rai couldn't answer "where is the backlog?"
- Consulted stale `.claude/` files instead of current `governance/`
- Ishikawa analysis: root cause = work state not in graph

**Before E8:**
```
User: "What's the current epic?"
Rai: *searches files, finds conflicting info, guesses wrong*
```

**After E8:**
```
User: "What's the current epic?"
Rai: *queries graph* → "E8 Work Tracking Graph (DRAFT), target Feb 9"
```

### Key Risks

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| Backlog format varies | Medium | Medium | Document required format, parser is lenient |
| Epic scope format varies | Medium | Medium | Parse what exists, warn on missing fields |
| Too many relationships | Low | Low | Start with `contains` only, add others if needed |
| Parser complexity | Low | Medium | Follow existing prd.py pattern |

### Velocity Assumption

- **Baseline:** 2-3x multiplier with kata cycle (E2, E3 calibration)
- **Reuse factor:** Parsers follow established pattern (prd.py, vision.py)
- **Estimated:** 4-6 hours total
- **Buffer:** 2 hours for integration/polish

---

## V3 Integration Point

This epic creates the **internal canonical representation** that V3 will use:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  BacklogParser  │     │   JiraAdapter   │     │  GitHubAdapter  │
│   (local md)    │     │     (V3)        │     │    (future)     │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                    ┌─────────────────────┐
                    │   ConceptGraph      │
                    │  (unified model)    │
                    └─────────────────────┘
                                 ▼
                    ┌─────────────────────┐
                    │   Query Engine      │
                    │  (Rai, CLI, MCP)    │
                    └─────────────────────┘
```

**Terminology mapping (onboarding config):**

| RaiSE | Jira Default | Alternative |
|-------|--------------|-------------|
| Project | Project | — |
| Epic | Epic | Story |
| Feature | Story | Task |

---

## Implementation Plan

> Added by `/epic-plan` — 2026-02-02
> Strategy: **Parallel Parsers → Integration** | Milestones: **2** | Target: Feb 9

### Feature Sequence

| Order | Feature | Size | SP | Dependencies | Milestone | Rationale |
|:-----:|---------|:----:|:--:|--------------|-----------|-----------|
| 1 | F8.1 Backlog Parser | S | 2 | None | M1 | Foundation — can parallel with F8.2 |
| 1 | F8.2 Epic Parser | S | 2 | None | M1 | Foundation — can parallel with F8.1 |
| 2 | F8.3 Graph Extension | S | 2 | F8.1, F8.2 | M1 | Integration — needs both parsers |
| 3 | F8.4 Work Queries | S | 2 | F8.3 | M2 | User-facing — validates E2E |

**Sequencing strategy:** Parallel foundation, then integration.

- F8.1 and F8.2 are **independent** — both follow prd.py pattern, no shared state
- F8.3 **integrates** both parsers into graph — natural merge point
- F8.4 **validates** the whole stack — proves "current work" query works

### Milestones

| Milestone | Features | Target | Success Criteria | Demo |
|-----------|----------|--------|------------------|------|
| **M1: Graph with Work** | F8.1, F8.2, F8.3 | Day 1-2 | `raise graph build` includes work concepts | Graph shows Project → Epic → Feature hierarchy |
| **M2: Epic Complete** | F8.4 | Day 2-3 | `raise context query "current work"` returns E8 | Query returns current epic with features |

### Parallel Work Streams

```
Time →
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Stream 1: F8.1 (Backlog Parser) ──┐
                                  ├──► F8.3 (Graph) ──► F8.4 (Queries)
Stream 2: F8.2 (Epic Parser) ─────┘
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                                  M1: Graph with Work    M2: Epic Complete
                                       (Day 1-2)              (Day 2-3)
```

**Merge point:** F8.3 waits for both F8.1 and F8.2 to complete.

**Note:** With single developer, "parallel" means low context-switch cost — can interleave or do sequentially without blocking.

### Progress Tracking

| Feature | Size | SP | Status | Actual | Velocity | Notes |
|---------|:----:|:--:|:------:|:------:|:--------:|-------|
| F8.1 Backlog Parser | S | 2 | ✅ Complete | ~45 min | 1.0x | 34 tests, 93% coverage |
| F8.2 Epic Parser | S | 2 | ✅ Complete | ~20 min | 1.5x | 27 tests, 89% coverage |
| F8.3 Graph Extension | S | 2 | Pending | — | — | |
| F8.4 Work Queries | S | 2 | Pending | — | — | |

**Milestone Progress:**
- [ ] M1: Graph with Work (target: Day 2) — F8.1 ✓, F8.2 ✓, F8.3 remaining
- [ ] M2: Epic Complete (target: Day 3)

### Sequencing Rationale

**F8.1 + F8.2 (Parallel, First):**
- Both follow established parser pattern (prd.py, vision.py)
- No dependencies between them
- Low risk — well-understood problem
- Produce concepts needed by F8.3

**F8.3 (After F8.1 + F8.2):**
- Needs work concepts to add to graph
- Medium risk — extends existing infrastructure
- Natural integration point
- Validates parser output

**F8.4 (Last):**
- Needs complete graph with work layer
- Low risk — extends existing query engine
- User-facing validation — proves epic objective met
- Demo-able result

### Sequencing Risks

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| Backlog format parsing issues | Medium | Low | Lenient parser, document format requirements |
| Epic scope format varies across E1-E9 | Medium | Low | Test against all existing scopes |
| Graph extension breaks existing queries | Low | High | Run full test suite after F8.3 |
| Query strategy needs new patterns | Low | Medium | Extend existing strategies, don't rewrite |

### Velocity Assumptions

**Calibration data (S features with kata cycle):**
- F2.1 Concept Extraction: 52 min (3.5x)
- F2.2 Graph Builder: 65 min (2.8x)
- F2.3 MVC Query Engine: 90 min (2.1x)
- F3.3 Memory Graph: 60 min (1.0x)

**Average:** ~67 min per S feature

**E8 Estimate:**
- 4 features × ~60 min = ~4 hours implementation
- + 1 hour buffer = ~5 hours total
- **Timeline:** 2-3 sessions (comfortable for Feb 9)

### Implementation Notes

**F8.1 Backlog Parser:**
- Input: `governance/projects/*/backlog.md`
- Output: `Concept(type=PROJECT)` + `Concept(type=EPIC)` for index
- Pattern: Follow `prd.py` — regex for tables, state machine for sections
- Test with: `raise-cli/backlog.md`

**F8.2 Epic Parser:**
- Input: `dev/epic-*-scope.md`
- Output: `Concept(type=EPIC)` (full) + `Concept(type=FEATURE)` from tables
- Pattern: Follow `prd.py` — regex for frontmatter, tables
- Test with: All 6 existing epic scopes (E1, E2, E3, E7, E8, E9)

**F8.3 Graph Extension:**
- Extend `ConceptType` enum
- Add `WorkStatus` enum
- Extend `RelationshipType` with `contains`, `blocks`, `current_focus`
- Add `infer_work_relationships()` to relationships.py
- Update `builder.py` to call work extractors

**F8.4 Work Queries:**
- Test existing strategies with work concepts
- May need work-specific query formatting
- Key test: `raise context query "current work"` → returns E8

---

*Epic planned: 2026-02-02*
*Informed by: RES-ROVO-001, calibration data*
*Next: `/feature-design` for F8.1 or F8.2 (can start either)*
