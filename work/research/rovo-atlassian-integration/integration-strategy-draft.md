# Integration Strategy Draft: RaiSE ↔ Atlassian

> **Status**: DRAFT
> **Version**: 0.1
> **Date**: 2026-02-02
> **Promotes to**: ADR-017 (when finalized)

---

## Context

RaiSE needs to integrate with the Atlassian ecosystem for V3 (hosted Rai). The Mar 14, 2026 Rovo AI webinar is a key milestone. This document outlines the integration strategy based on RES-ROVO-001 research.

---

## Strategic Positioning

### What RaiSE Brings to Atlassian Users

| Capability | RaiSE | Native Atlassian | Gap Filled |
|------------|-------|------------------|------------|
| Governance as Code | Full methodology | Basic templates | Structured governance |
| AI Calibration | Accumulated patterns | Generic | Context-aware AI |
| Quality Gates | Validation-first | Manual review | Automated governance |
| Work Tracking | Epic/Feature specs | Jira issues | Spec-driven development |

### Positioning: Complement, Not Compete

```
Rovo Dev: "AI that executes Jira work items"
RaiSE:    "AI that ensures work items are well-governed"

Together: "Governed AI execution"
```

---

## Integration Layers

### Layer 1: MCP Integration (V3 MVP)

**Approach**: Use Atlassian's Remote MCP Server to connect RaiSE/Rai to Jira and Confluence.

```
Rai (Claude) ←→ MCP ←→ Atlassian Cloud
                       ├── Jira (work items)
                       └── Confluence (governance docs)
```

**Capabilities**:
- Read Jira issues, epics, sprints
- Read Confluence pages (governance docs)
- Create/update issues (with governance context)
- Create/update pages (spec→page sync)

**Authentication**: OAuth 2.1 (user context)

**Implementation**:
1. Configure MCP server connection in Rai
2. Build skills that use MCP tools
3. Map Jira entities to RaiSE concepts

### Layer 2: Work Graph Sync (V3.1)

**Approach**: Bidirectional sync between RaiSE Work Graph and Teamwork Graph.

```
RaiSE Work Graph              Teamwork Graph
├── Project ────────────────→ Project
├── Epic ───────────────────→ Epic (Work Item)
├── Feature ────────────────→ Story/Task (Work Item)
└── Governance Doc ─────────→ Document (Confluence)
```

**Sync Rules**:
- **Create**: New epic in RaiSE → create Jira epic
- **Update**: Status change in Jira → update RaiSE
- **Link**: Feature implemented → link to Confluence spec

**Conflict Resolution**:
- Governance (specs, requirements): RaiSE authoritative
- Execution (status, assignee): Jira authoritative
- Alert on structural conflicts (deleted epic, moved feature)

### Layer 3: Forge App (V3.2 - Future)

**Approach**: Build a Forge app for deeper Atlassian integration.

**Use Cases**:
- Governance panel in Jira issue view
- RaiSE validation in Jira workflow
- Spec preview in Confluence

**Why Forge over Connect**:
- Connect deprecated March 2026
- Forge is the future platform
- Better security model (sandboxed)

---

## Entity Mapping

### Terminology Decision

**Decision:** Keep RaiSE terminology, map to Jira during onboarding.

**Rationale:**
- RaiSE "Feature" implies design→plan→implement cycle (methodology meaning)
- Jira terminology varies by team anyway
- Our Features are 15-90 min (closer to Jira Tasks), our Epics are 3-5 hours (closer to Jira Stories)
- Conversion is configurable per-project during onboarding

### Default Mapping (Configurable)

| RaiSE | Jira Default | Alternative | Notes |
|-------|--------------|-------------|-------|
| `Project` | Project | — | Direct map via project key |
| `Epic` | Epic | Story | For teams with flat hierarchy |
| `Feature` | Story | Task | Depends on team's Jira structure |
| `Task` (future) | Sub-task | Task | Child of Feature |

### Onboarding Configuration

```yaml
# .raise/integrations/jira.yaml (V3)
jira:
  project_key: "RAISE"
  mapping:
    epic: "Epic"           # or "Story" for flat teams
    feature: "Story"       # or "Task" for granular teams
    task: "Sub-task"       # or "Task"
  custom_fields:
    raise_id: "customfield_10100"
    spec_link: "customfield_10101"
```

### Status Mapping

| RaiSE Status | Jira Status | Direction |
|--------------|-------------|-----------|
| `DRAFT` | (not in Jira) | RaiSE only |
| `PENDING` | To Do | Sync both ways |
| `IN_PROGRESS` | In Progress | Sync both ways |
| `COMPLETE` | Done | Sync both ways |
| `DEFERRED` | (custom status) | RaiSE → Jira |

### Metadata Fields

| RaiSE Field | Jira Field | Type |
|-------------|------------|------|
| `id` | Custom field (RaiSE ID) | Text |
| `name` | Summary | Text |
| `description` | Description (ADF) | Rich text |
| `size` | Story Points | Number |
| `target_date` | Due Date | Date |
| `spec_url` | Custom field (Spec Link) | URL |

---

## Governance Document Sync

### Confluence Page Structure

```
[Governance Space]
├── Constitution (framework/reference/constitution.md)
├── Guardrails (governance/solution/guardrails.md)
├── [Project: raise-cli]
│   ├── Vision
│   ├── Epics/
│   │   ├── E8 Work Tracking Graph
│   │   └── ...
│   └── Features/
│       ├── F8.1 Backlog Parser
│       └── ...
```

### Sync Behavior

1. **Initial Import**: Markdown → Confluence (ADF conversion)
2. **Updates**: RaiSE → Confluence (authoritative)
3. **Read-back**: Confluence → RaiSE (for comments, links)

### ADF Conversion

Atlassian Document Format for rich content:
```json
{
  "type": "doc",
  "content": [
    {
      "type": "heading",
      "attrs": {"level": 1},
      "content": [{"type": "text", "text": "Epic E8: Work Tracking Graph"}]
    },
    {
      "type": "paragraph",
      "content": [{"type": "text", "text": "..."}]
    }
  ]
}
```

Tools exist for Markdown → ADF conversion.

---

## Security Model

### Principle: Least Privilege

- RaiSE requests only necessary scopes
- Read-only by default; write requires explicit grant
- No admin access needed

### Data Flow

```
User authenticates → OAuth 2.1 → User's permissions apply
                                       │
                                       ▼
                              Only data user can see
```

### Sensitive Data Handling

- No secrets stored in Jira/Confluence
- Governance docs are generally non-sensitive
- Work status is shared context

---

## Implementation Phases

### Phase 1: MCP Read (V3 MVP - Mar 14)
- [ ] Configure Atlassian MCP server
- [ ] Skill: Read Jira epic/feature status
- [ ] Skill: Read Confluence governance docs
- [ ] Demo: Rai understands Jira context

### Phase 2: MCP Write (V3.1 - Apr)
- [ ] Skill: Create Jira issue from story spec
- [ ] Skill: Update Confluence page from spec
- [ ] Skill: Comment on Jira issue (governance notes)

### Phase 3: Bidirectional Sync (V3.2 - Q2)
- [ ] Webhook listener for Jira changes
- [ ] Sync engine for conflict resolution
- [ ] UI for sync status/conflicts

### Phase 4: Forge App (V3.3 - Q3)
- [ ] Governance panel in Jira
- [ ] Validation workflow integration
- [ ] Confluence macro for spec embedding

---

## E8 Design Implications

Based on this strategy, E8 should:

1. **Use Teamwork Graph-compatible names**
   - Keep: Project, Epic, Feature (generic enough)
   - Relationships: Use `parent_of`, `contains` style

2. **Include integration-ready fields**
   ```python
   class WorkConcept(Concept):
       # ... core fields ...
       external_id: str | None = None    # Jira key when synced
       external_url: str | None = None   # Link to Jira/Confluence
       sync_status: SyncStatus | None = None  # synced/pending/conflict
   ```

3. **Design parsers as adapters**
   - Common interface for all sources
   - `BacklogParser` today → `JiraAdapter` tomorrow

4. **Status enum that maps**
   - Include DRAFT (RaiSE-only)
   - Standard statuses map to Jira To Do/In Progress/Done

---

## Open Questions

1. **Custom fields in Jira** — Do we need a "RaiSE ID" custom field, or use labels?
2. **Confluence space structure** — One space per project, or shared governance space?
3. **Sync frequency** — Real-time (webhooks) or periodic (polling)?
4. **Conflict UI** — Where does user resolve sync conflicts?

---

## Decision Record

| Decision | Option Chosen | Rationale |
|----------|---------------|-----------|
| Integration protocol | MCP | Official Atlassian support, Anthropic partnership |
| Sync direction | Bidirectional | RaiSE for gov, Jira for execution |
| App platform | Forge (future) | Connect deprecated 2026 |
| Auth model | OAuth 2.1 | MCP standard, user context |

---

*Draft: 2026-02-02*
*Review: Pending*
*Promotes to: ADR-017 when accepted*
