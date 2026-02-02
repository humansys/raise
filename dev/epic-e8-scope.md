# Epic E8: Work Tracking Graph - Scope

> **Status:** DRAFT
> **Branch:** TBD (`feature/e8/work-tracking-graph`)
> **Created:** 2026-02-02
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

## Concepts to Add

### New Node Types

| Concept | Source | Example |
|---------|--------|---------|
| `Project` | `governance/projects/*/backlog.md` | raise-cli |
| `Epic` | `dev/epic-*-scope.md` | E8 Work Tracking Graph |
| `Feature` | Inside epic scope docs | F8.1 Epic Parser |

### New Relationships

| Relationship | From | To | Example |
|--------------|------|----|---------|
| `has_epic` | Project | Epic | raise-cli → E8 |
| `has_feature` | Epic | Feature | E8 → F8.1 |
| `blocks` | Feature | Feature | F8.1 → F8.3 |
| `implements` | Feature | Requirement | F8.1 → REQ-RF-05 |
| `current_focus` | Project | Epic | raise-cli → E8 |

### Node Properties

**Epic:**
```python
class EpicConcept(Concept):
    status: Literal["DRAFT", "IN_PROGRESS", "COMPLETE"]
    target_date: date | None
    feature_count: int
    completion_percent: float
```

**Feature:**
```python
class FeatureConcept(Concept):
    status: Literal["PENDING", "IN_PROGRESS", "COMPLETE", "DEFERRED"]
    size: Literal["XS", "S", "M", "L", "XL"] | None
    story_points: int | None
```

---

## Features

| ID | Feature | Size | Description |
|----|---------|:----:|-------------|
| F8.1 | **Backlog Parser** | S | Parse `governance/projects/*/backlog.md` → Project + Epic index |
| F8.2 | **Epic Parser** | S | Parse `dev/epic-*-scope.md` → Epic + Features |
| F8.3 | **Graph Extension** | S | Add work concepts to ConceptGraph, relationships |
| F8.4 | **Work Queries** | S | `raise context query "current epic"`, `"E8 features"` |

**Total:** 4 features, ~4-6 hours with kata cycle

---

## Architecture

### Parser Flow

```
governance/projects/raise-cli/backlog.md
    ↓ BacklogParser
Project(id="raise-cli", epics=[...])

dev/epic-e8-scope.md
    ↓ EpicParser
Epic(id="E8", features=[F8.1, F8.2, ...], status="DRAFT")
```

### Extended Graph

```
┌─────────────────────────────────────────────────┐
│              ConceptGraph                        │
├─────────────────────────────────────────────────┤
│  Governance Layer (existing)                     │
│  ├── Requirements (PRD)                          │
│  ├── Principles (Constitution)                   │
│  └── Outcomes (Vision)                           │
├─────────────────────────────────────────────────┤
│  Work Layer (NEW)                                │
│  ├── Projects (backlog.md)                       │
│  ├── Epics (epic-*-scope.md)                     │
│  └── Features (inside epic scopes)               │
├─────────────────────────────────────────────────┤
│  Relationships                                   │
│  ├── governed_by, implements (existing)          │
│  └── has_epic, has_feature, blocks (NEW)         │
└─────────────────────────────────────────────────┘
```

### Query Examples

```bash
# Current focus
$ raise context query "current work"
Project: raise-cli
Current Epic: E8 Work Tracking Graph (DRAFT)
Target: Feb 9, 2026

# Epic details
$ raise context query "E8" --strategy relationship_traversal
Epic: E8 Work Tracking Graph
Status: DRAFT
Features:
  - F8.1 Backlog Parser [PENDING]
  - F8.2 Epic Parser [PENDING]
  - F8.3 Graph Extension [PENDING]
  - F8.4 Work Queries [PENDING]

# What implements a requirement
$ raise context query "REQ-RF-05" --edge-types implements
Requirement: REQ-RF-05 (Context Generation)
Implemented by:
  - F4.1 Governance Loader [COMPLETE]
  - F4.2 CLAUDE.md Generator [COMPLETE via skill]
```

---

## File Changes Required

### New Files

```
src/raise_cli/governance/parsers/
├── backlog.py          # NEW: Parse project backlog
└── epic.py             # NEW: Parse epic scope docs

src/raise_cli/governance/
└── models.py           # EXTEND: Add EpicConcept, FeatureConcept, ProjectConcept
```

### Modified Files

```
src/raise_cli/governance/graph/
├── builder.py          # EXTEND: Build work layer
├── relationships.py    # EXTEND: New relationship types
└── models.py           # EXTEND: New edge types

src/raise_cli/governance/
└── extractor.py        # EXTEND: Extract work concepts
```

---

## Backlog Format (Simplified)

To make parsing reliable, backlog.md should follow this structure:

```markdown
# Backlog: {project-name}

## Epics

| ID | Epic | Status | Scope |
|----|------|--------|-------|
| E1 | Core Foundation | COMPLETE | `dev/epic-e1-scope.md` |
| E8 | Work Tracking Graph | DRAFT | `dev/epic-e8-scope.md` |

## Current Focus

Epic: E8
Target: 2026-02-09
```

**Parser extracts:**
- Project ID from filename
- Epic index from table
- Current focus from section

---

## Epic Scope Format (Simplified)

Epic scope docs should have parseable feature table:

```markdown
## Features

| ID | Feature | Size | Status | Description |
|----|---------|:----:|:------:|-------------|
| F8.1 | Backlog Parser | S | PENDING | Parse backlog.md |
```

**Parser extracts:**
- Epic ID from filename
- Features from table
- Status, target from frontmatter or headers

---

## In Scope

**MUST:**
- [ ] BacklogParser extracts projects and epic index
- [ ] EpicParser extracts epic details and features
- [ ] Graph includes work concepts with relationships
- [ ] `raise context query "E8"` returns epic with features
- [ ] `raise context query "current work"` returns focus

**SHOULD:**
- [ ] `--type epic` filter for queries
- [ ] Status filtering (`--status IN_PROGRESS`)
- [ ] Feature dependencies (blocks relationship)

---

## Out of Scope

- Jira/Confluence integration (V3)
- Bidirectional sync (V3)
- Team/assignee tracking (V3)
- Sprint management (V3)
- Burndown/velocity charts (Telemetry epic)

---

## Done Criteria

- [ ] `raise graph build` includes work concepts
- [ ] `raise context query "current epic"` returns correct answer
- [ ] No more "where is the backlog?" confusion
- [ ] Existing governance queries still work
- [ ] Tests: >90% coverage on new parsers

---

## Dependencies

```
E2 Governance Toolkit ← COMPLETE (infrastructure exists)
    ↓
E8 Work Tracking Graph ← THIS EPIC
    ↓
E7 Onboarding (can use graph for status)
    ↓
E9 Telemetry (queries graph for metrics)
```

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Query "current work" accuracy | 100% |
| Parse existing epic scopes | All 4 (E1, E2, E3, E7) |
| No regression on governance queries | All existing tests pass |

---

## Future: V3 Integration Point

This epic creates the **internal canonical representation** that V3 will use for external integrations:

```
Jira ←→ Gateway ←→ Work Graph ←→ Rai
Confluence ←→ Gateway ←→ Governance Graph ←→ Rai
```

The parsers we build now become **adapters** in V3:
- `BacklogParser` → `JiraEpicAdapter`
- `EpicParser` → `JiraIssueAdapter`

---

*Draft created: 2026-02-02*
*Status: Ready for review*
