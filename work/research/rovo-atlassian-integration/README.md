# Research: Rovo AI & Atlassian Integration Strategy

> **ID**: RES-ROVO-001
> **Date**: 2026-02-02
> **Decision Informed**: E8 Work Tracking Graph design; V3 integration strategy
> **Confidence**: HIGH (10 primary sources, 2 secondary)

---

## Executive Summary (5 min read)

Atlassian's AI strategy centers on **Teamwork Graph** — a unified knowledge graph connecting all Atlassian products and 100+ external tools. External AI tools integrate via **MCP (Model Context Protocol)**, with Atlassian providing an official Remote MCP Server.

**Key insight for RaiSE**: Our Work Tracking Graph (E8) should align with Teamwork Graph's object model. This isn't just V3 preparation — it's ensuring our internal representation can seamlessly map to/from Atlassian's canonical model.

**Recommendation**: Proceed with E8 using Teamwork Graph-compatible concepts. Design parsers as adapters that could eventually become bidirectional.

---

## Quick Reference

| RaiSE Term | Jira Default | Alternative | Notes |
|------------|--------------|-------------|-------|
| Project | Project | — | Direct map |
| Epic | Epic | Story | Configurable per-team |
| Feature | Story | Task | Our Features are 15-90 min |
| Governance Doc | Confluence Page | — | Spec sync |

**Decision:** Keep RaiSE terminology, configure mapping during onboarding. Our "Feature" has methodology meaning (design→plan→implement cycle) that shouldn't be lost.

---

## Contents

1. [Full Report](./rovo-integration-report.md) — Detailed findings (20 min)
2. [Evidence Catalog](./sources/evidence-catalog.md) — All sources with ratings
3. [Integration Strategy](./integration-strategy-draft.md) — V3 architecture draft

---

## Key Findings

### 1. Teamwork Graph is the Canonical Layer

Atlassian has built a **unified data model** where everything — Jira issues, Confluence pages, Slack messages, GitHub PRs — becomes an "object" in the graph. This is the source of truth for all AI features.

**Object Types** (relevant to RaiSE):
- `Work Item` — Issues, tasks, stories, epics
- `Document` — Pages, docs, specifications
- `Project` — Containers for work
- `User` — People in the system

**Relationship Types**:
- `Canonical` — Direct structural (parent-child, contains)
- `Activity` — User actions (created, updated)
- `Logical` — Aggregated views
- `Inferred` — AI-derived connections

### 2. MCP is the Integration Protocol

The **Model Context Protocol** (developed by Anthropic) is how external AI tools connect to Atlassian:

```
Claude/RaiSE ←→ MCP Client ←→ Remote MCP Server ←→ Teamwork Graph
                              (mcp.atlassian.com)
```

- **OAuth 2.1** for authentication
- **Read + Write** operations supported
- Respects existing **permissions**
- Anthropic is **first partner**

### 3. Rovo Dev is a Competitor/Complement

Rovo Dev provides AI coding assistance tightly integrated with Jira:
- Code Planner (Jira → technical plan)
- Code Generator (work item → code)
- Code Reviewer (PR → acceptance criteria check)
- CLI that reads local repos + Jira context

**Positioning for RaiSE**: We're not competing with Rovo Dev — we're complementing it. RaiSE provides **governance** and **methodology**; Rovo Dev provides **Jira-native execution**. Integration lets teams use both.

### 4. Forge is the Future, Connect is Deprecated

- **Connect apps**: Deprecated March 31, 2026
- **Forge apps**: The supported platform going forward
- **Implication**: Any custom Atlassian integration should use Forge

---

## Recommendations for E8

Based on this research, here are specific design recommendations:

### Concept Naming

| E8 Concept | Recommendation | Rationale |
|------------|----------------|-----------|
| `ProjectConcept` | Keep | Maps directly to Teamwork Graph "Project" |
| `EpicConcept` | Keep | Maps to Jira Epic (Work Item subtype) |
| `FeatureConcept` | Keep | Maps to Jira Story/Task (Work Item) |
| `has_epic` | Consider `contains` | More generic, matches Teamwork Graph |
| `has_feature` | Consider `parent_of` | Aligns with Teamwork Graph hierarchy |

### Status Values

Align with Jira workflow states:
```python
class WorkStatus(str, Enum):
    DRAFT = "draft"           # RaiSE-specific (pre-Jira)
    PENDING = "pending"       # → "To Do" in Jira
    IN_PROGRESS = "in_progress"  # → "In Progress" in Jira
    COMPLETE = "complete"     # → "Done" in Jira
    DEFERRED = "deferred"     # RaiSE-specific
```

### Metadata Fields

Include fields that map to Jira:
```python
class FeatureConcept(Concept):
    # Core (RaiSE)
    id: str           # "F8.1"
    name: str
    status: WorkStatus

    # Jira-compatible
    size: str | None          # → Story Points (custom field)
    assignee: str | None      # → Assignee
    target_date: date | None  # → Due Date

    # Integration (V3)
    jira_key: str | None      # "RAISE-123" when synced
    external_id: str | None   # Teamwork Graph object ID
```

### Parser Design

Design parsers as **adapters** from the start:
```
                    ┌─────────────────────┐
                    │   Adapter Interface │
                    └─────────────────────┘
                              ▲
              ┌───────────────┼───────────────┐
              │               │               │
    ┌─────────────────┐ ┌─────────────┐ ┌───────────────┐
    │ BacklogParser   │ │ JiraAdapter │ │ GitHubAdapter │
    │ (local md)      │ │ (V3)        │ │ (future)      │
    └─────────────────┘ └─────────────┘ └───────────────┘
```

---

## V3 Integration Architecture (Draft)

```
┌─────────────────────────────────────────────────────────────┐
│                     RaiSE V3 Architecture                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐ │
│  │   Rai CLI    │     │   Rovo Dev   │     │  Other AI    │ │
│  │  (RaiSE)     │     │ (Atlassian)  │     │   Tools      │ │
│  └──────┬───────┘     └──────┬───────┘     └──────┬───────┘ │
│         │                    │                    │          │
│         ▼                    ▼                    ▼          │
│  ┌─────────────────────────────────────────────────────────┐│
│  │              MCP Protocol Layer                          ││
│  │  - OAuth 2.1 auth                                        ││
│  │  - Read/write operations                                 ││
│  │  - Permission-aware                                      ││
│  └─────────────────────────────────────────────────────────┘│
│         │                    │                    │          │
│         ▼                    ▼                    ▼          │
│  ┌─────────────────────────────────────────────────────────┐│
│  │              Teamwork Graph (Atlassian)                  ││
│  │  - Work Items (Epics, Stories, Tasks)                    ││
│  │  - Documents (Confluence pages)                          ││
│  │  - Projects, Users, Relationships                        ││
│  └─────────────────────────────────────────────────────────┘│
│         │                    │                                │
│         ▼                    ▼                                │
│  ┌──────────────┐     ┌──────────────┐                       │
│  │    Jira      │     │  Confluence  │                       │
│  └──────────────┘     └──────────────┘                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘

                    ┌─────────────────────┐
                    │   RaiSE Work Graph  │
                    │   (Local Source of  │
                    │    Truth for Gov)   │
                    └─────────────────────┘
                              ▲
                              │ Bidirectional Sync
                              ▼
                    ┌─────────────────────┐
                    │   Teamwork Graph    │
                    │   (Jira/Confluence) │
                    └─────────────────────┘
```

### Sync Strategy

1. **RaiSE as Source of Truth for Governance**
   - Constitution, guardrails, principles → Confluence pages
   - Epic scopes, story designs → Confluence + Jira epics

2. **Jira as Source of Truth for Execution**
   - Sprint status, assignees → synced from Jira
   - Comments, activity → read from Jira via MCP

3. **Conflict Resolution**
   - Governance changes: RaiSE wins (Confluence updated)
   - Execution status: Jira wins (RaiSE updated)
   - Manual review for structural conflicts

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Teamwork Graph API stays in EAP | Medium | High | Use MCP as primary; Graph API as optimization |
| MCP capabilities change | Low | Medium | Abstract integration behind adapter |
| Rovo Dev dominates space | Medium | Medium | Position as complement, not competitor |
| Custom object types not supported | Medium | Low | Use standard types + metadata |

---

## Next Steps

1. **E8 Implementation** — Use recommendations above for concept naming and structure
2. **ADR Draft** — Document integration strategy decisions (ADR-017?)
3. **MCP Exploration** — Try Atlassian MCP server with Claude to validate patterns
4. **V3 Roadmap** — Schedule integration features for post-Feb 15 launch

---

## References

- [Atlassian Rovo](https://www.atlassian.com/software/rovo)
- [Rovo Dev](https://www.atlassian.com/software/rovo-dev)
- [Teamwork Graph Developer Docs](https://developer.atlassian.com/platform/teamwork-graph/)
- [Atlassian MCP Server](https://github.com/atlassian/atlassian-mcp-server)
- [MCP Protocol](https://modelcontextprotocol.io/)

---

*Research completed: 2026-02-02*
*Informs: E8 Work Tracking Graph, V3 Integration Strategy*
