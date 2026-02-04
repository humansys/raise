# ADR-017: V3-Compatible Work Graph Design

## Status

**Accepted** — 2026-02-02

## Context

E8 Work Tracking Graph will extend the governance graph to include work items (projects, epics, features). This creates the internal representation that V3 will use for external integrations with Atlassian ecosystem (Jira, Confluence, Rovo).

Research (RES-ROVO-001) revealed:
- Atlassian's **Teamwork Graph** is the canonical data layer for all AI features
- **MCP (Model Context Protocol)** is the integration mechanism for external tools
- Teamwork Graph uses standardized object types: Project, Work Item, Document
- RaiSE terminology (Epic, Feature) maps cleanly but at different granularity

**Key insight:** Our "Feature" (15-90 minutes) is smaller than typical Jira "Story" (1-5 days). This is intentional — our Feature represents a design→plan→implement cycle, not just a work item.

## Decision

**Design work concepts to be compatible with Atlassian Teamwork Graph while keeping RaiSE terminology. Mapping happens at integration time (V3), not in the internal model.**

### Terminology Preservation

| RaiSE Term | Internal Model | Jira Mapping (configurable) |
|------------|----------------|----------------------------|
| Project | `ConceptType.PROJECT` | Project |
| Epic | `ConceptType.EPIC` | Epic or Story |
| Feature | `ConceptType.FEATURE` | Story or Task |

### Adapter Pattern for Parsers

Design parsers as adapters that can be swapped for different data sources:

```
WorkItemParser (interface)
    ├── BacklogParser (local markdown) ← E8
    ├── JiraAdapter (V3)
    └── GitHubAdapter (future)
```

### V3-Ready Fields in Metadata

Include optional fields for future sync:

```python
{
    "external_id": None,     # Jira key when synced (e.g., "RAISE-123")
    "external_url": None,    # Link to external system
    "sync_status": None      # For bidirectional sync
}
```

### Status Values (Jira-Compatible)

```python
class WorkStatus(str, Enum):
    DRAFT = "draft"           # RaiSE-specific (pre-Jira)
    PENDING = "pending"       # → "To Do"
    IN_PROGRESS = "in_progress"  # → "In Progress"
    COMPLETE = "complete"     # → "Done"
    DEFERRED = "deferred"     # RaiSE-specific
```

### Relationship Types (Teamwork Graph aligned)

Use `contains` instead of `has_epic`/`has_feature`:
- More generic, matches Teamwork Graph's `parent_of` semantic
- Works for any hierarchy level

## Alternatives Considered

### Option A: Rename to Jira Terminology

Rename Epic→Epic, Feature→Story internally.

**Rejected:** Our "Feature" has methodology meaning (design→plan→implement cycle). Losing this semantic would confuse RaiSE users and documentation.

### Option B: No V3 Preparation

Build E8 without considering Atlassian compatibility.

**Rejected:** Would require rework when adding V3 integration. Small upfront investment (adapter pattern, status enum, metadata fields) saves significant refactoring later.

### Option C: Full Jira Model Now

Implement complete Jira entity model (Sprint, Board, Component, etc.).

**Rejected:** YAGNI. Start with minimal mapping (Project, Epic, Feature), extend when needed for V3.

## Consequences

### Positive

- **Smooth V3 path:** Internal model maps directly to Teamwork Graph concepts
- **Terminology preserved:** RaiSE methodology semantics maintained
- **Adapter pattern:** Easy to add JiraAdapter without changing core graph
- **Onboarding flexibility:** Teams configure mapping per their Jira workflow

### Negative

- **Slight complexity:** Parser interface adds abstraction layer
- **Documentation needed:** Must explain RaiSE↔Jira mapping to users

### Neutral

- Status enum covers both RaiSE-specific and Jira-standard states
- Optional V3 fields add minimal overhead to metadata

## Implementation Notes

### E8 Deliverables

1. `WorkStatus` enum in `governance/models.py`
2. `WorkItemParser` interface in `governance/parsers/base.py`
3. `BacklogParser` and `EpicScopeParser` implementing interface
4. Extended `RelationshipType` with `contains`, `blocks`, `current_focus`
5. V3 fields in metadata (optional, None by default)

### V3 Deliverables (Post Feb-15)

1. `JiraAdapter` implementing `WorkItemParser`
2. MCP integration for read/write operations
3. Onboarding wizard for terminology mapping config
4. Bidirectional sync with conflict resolution

## References

- [RES-ROVO-001](../../work/research/rovo-atlassian-integration/README.md) — Atlassian integration research
- [Teamwork Graph Docs](https://developer.atlassian.com/platform/teamwork-graph/) — Object types and relationships
- [Atlassian MCP Server](https://github.com/atlassian/atlassian-mcp-server) — Integration mechanism
- [ADR-011](./adr-011-concept-level-graph-architecture.md) — Concept-level graph foundation
- [ADR-012](./adr-012-skills-toolkit-architecture.md) — Skills + Toolkit pattern

---

*Decision by: Emilio + Rai*
*Date: 2026-02-02*
*Epic: E8 Work Tracking Graph*
