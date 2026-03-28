# Jira & Confluence Standards

> **Status:** Draft
> **Owner:** Emilio Osorio
> **Applies to:** RAISE project (humansys.atlassian.net)
> **Why:** The knowledge graph loads work items from Jira and governance from Confluence (RAISE-651). Consistent metadata = reliable graph nodes. These standards are the specification for JiraWorkAdapter and ConfluenceGovernanceAdapter.

---

## 1. Jira Issue Hierarchy

```
Capability
  └── Epic
        └── Story | Task | Bug
              └── Sub-task
```

| Level | Issue Type | When to Use | Example |
|-------|-----------|-------------|---------|
| **Capability** | Capability | Groups 3+ related epics into a strategic theme. SAFe construct for Easy Agile Story Maps | "RaiSE PRO", "Knowledge Graph & Discovery" |
| **Epic** | Epic | Body of work with multiple stories. Has scope, design, plan artifacts | "raise-server license MVP" |
| **Story** | Story | Delivers user/developer-observable value | "Add uv lock resolution gate to pre-commit" |
| **Task** | Task | Technical work with no direct user value (CI, config, infra) | "Remove readme-renderer dev dependency" |
| **Bug** | Bug | Defect — something that worked and broke, or never worked as specified | "graph build crashes on duplicate node IDs" |
| **Sub-task** | Sub-task | Breakdown within a single issue. Use 'Sub-task' NOT 'Subtask' (API case-sensitive) | Implementation step within a story |

### Rules

- Every Story, Task, and Bug **must** have an Epic Link
- Every Epic **must** be linked to a Capability via "Parent to Child relations" link type
- Capabilities are strategic groupings — they don't have a lifecycle (stay in Backlog)
- Epics marked `delivery` are client projects pending migration to their own Jira project (RAISE-649)

---

## 2. Summary Conventions

### Format

```
{concise description} — {context qualifier if needed}
```

### Rules

- **No key prefixes** in summaries — the Jira key IS the identifier. Wrong: "E349: Adapter Validation". Right: "Adapter Integration Validation"
- **No issue type in summary** — don't write "Epic: ..." or "Bug: ..."
- **English preferred** for summaries (codebase is English). Spanish acceptable for client-facing delivery items
- **Max 80 characters** — details go in description, not summary
- **Action-oriented** for stories/tasks: starts with verb or noun describing the deliverable
- **Problem-oriented** for bugs: describes what's broken, not the fix

### Examples

| Type | Good | Bad |
|------|------|-----|
| Epic | `raise-server license MVP` | `E616: raise-server license MVP` |
| Story | `Add dependency risk checklist to /rai-story-design` | `S583.2: checklist` |
| Bug | `graph build crashes on duplicate node IDs` | `Bug: fix graph` |
| Task | `Remove readme-renderer dev dependency` | `Task: cleanup deps` |

---

## 3. Label Taxonomy

Labels use **semantic prefixes** to enable reliable filtering and graph node enrichment.

### Prefix Categories

| Prefix | Purpose | Examples | Applied To |
|--------|---------|----------|------------|
| (none) | Functional domain | `graph`, `skills`, `session`, `adapters`, `gates`, `cli`, `mcp`, `docs` | All issue types |
| (none) | Technology | `confluence`, `forge`, `server` | All issue types |
| `tier:` | Product tier | `tier:pro`, `tier:oss` | Epics, Stories |
| `milestone:` | Target release/date | `milestone:mvp-apr16`, `milestone:v2.3` | Epics |
| `owner:` | Assigned team member (when not Emilio) | `owner:fernando`, `owner:aquiles` | Epics, Stories |
| `nature:` | Work nature | `nature:delivery`, `nature:maintenance`, `nature:foundational` | Epics |

### Anti-patterns (do NOT use)

| Bad Label | Why | Instead |
|-----------|-----|---------|
| `epic` | Redundant with issue type | Remove |
| `bug` | Redundant with issue type | Remove |
| `raise-pro` + `pro` + `pro-launch` | Multiple labels for same concept | Use `tier:pro` + specific milestone label |
| `raise-commons` | Redundant — everything in RAISE project is raise-commons | Remove |
| `capability` | Redundant with issue type | Remove |

### Required Labels

| Issue Type | Required Labels | Optional Labels |
|-----------|----------------|-----------------|
| Capability | (none needed — issue type is sufficient) | |
| Epic | At least 1 functional domain | `tier:`, `milestone:`, `nature:`, `owner:` |
| Story | Inherits from parent epic (or explicit) | domain if different from epic |
| Bug | At least 1 functional domain | `pipeline` if CI-related |
| Task | At least 1 functional domain | |

---

## 4. Description Standards

### Epic Description Template

```markdown
## Brief
One paragraph: what and why.

## Context
- Predecessor/related work
- Stakeholder
- Business driver

## Scope
- Bullet list of deliverables

## Out of Scope
- Explicit exclusions

## Stories (if known)
- S1: ...
- S2: ...

## Dependencies
- RAISE-XXX (why)

## Success Criteria
- Observable outcomes

## Owner
Name

## Evidence (if applicable)
- Links to Confluence research, problem briefs, ADRs
```

### Story Description

- **Acceptance criteria** clearly stated
- **Context** linking to parent epic
- **Technical notes** if non-obvious implementation

### Bug Description

- **Steps to reproduce**
- **Expected behavior**
- **Actual behavior**
- **Environment** (version, OS if relevant)

---

## 5. Priority Usage

Priority is meaningful only if differentiated. Currently almost everything is Major — this must change.

| Priority | When to Use | SLA Expectation |
|----------|------------|-----------------|
| **Critical** | Data loss, security vulnerability, complete feature broken in production | Fix in current sprint |
| **High** | Significant functionality broken, blocks other work, client-facing issue | Next sprint |
| **Major** | Standard work — default for planned stories and epics | Planned per roadmap |
| **Minor** | Nice-to-have, polish, low-impact improvements | When convenient |
| **Trivial** | Cosmetic, typo, non-functional | Opportunistic |

### Rules

- Bugs should rarely be Major — triage to actual severity
- Epics inherit priority from business urgency, not default
- Stories inherit from epic unless overridden

---

## 6. Workflow Conventions

### Status Transitions

| From | To | When |
|------|----|------|
| Backlog | Selected for Development | Prioritized for next sprint/milestone |
| Selected for Development | In Progress | Work actively started (branch created, story started) |
| In Progress | Done | All acceptance criteria met, code merged, tests passing |
| Any | Done (cancelled) | Superseded, stale, or no longer relevant — add closing comment with reason |

### Rules

- **Don't start In Progress without a plan** — stories should have `/rai-story-plan` before implementation
- **Rolling epics** (maintenance, security) stay In Progress indefinitely — that's OK
- **Add closing comment** when transitioning to Done if the issue wasn't completed normally (cancelled, superseded, duplicate)

---

## 7. Confluence Space Structure

### Primary Space: RaiSE1

```
RaiSE Documentation (RaiSE1)
├── Product
│   ├── PRD
│   ├── Vision
│   ├── Roadmap
│   └── Problem Briefs
├── Architecture
│   ├── ADRs
│   ├── Technical Architecture (per epic)
│   └── Domain Model
├── Research
│   ├── Evidence Catalogs
│   └── Spike Reports
├── Epics
│   ├── {Epic Key} — {Epic Name}
│   │   ├── Scope
│   │   ├── Design
│   │   ├── Plan
│   │   └── Retrospective
│   └── ...
├── Releases
│   └── v{X.Y.Z} Release Notes
└── Operations
    ├── Runbooks
    └── Onboarding
```

### Page Naming Convention

```
{Context} — {Artifact Type}
```

Examples:
- `E3: ScaleUp Knowledge Integration — Technical Architecture`
- `Pluggable Domains — Requirements Brief`
- `v2.2.4 — Release Notes`

### Rules

- Every epic with Confluence artifacts links to them from the Jira epic description (Evidence section)
- Research pages include date and author in metadata block
- ADRs follow `ADR-{NNN}: {Title}` naming

---

## 8. Graph Integration Contract

When RAISE-651 (Graph Data Abstraction) loads from Jira, the JiraWorkAdapter will map:

| Jira Field | GraphNode Field | Notes |
|------------|----------------|-------|
| `key` | `id` | Prefixed: `epic-RAISE-XXX`, `story-RAISE-XXX` |
| `summary` | `content` | |
| `issuetype.name` | `type` | Lowercase: `epic`, `story`, `task`, `bug` |
| `status.name` | `metadata.status` | Normalized to: `backlog`, `selected`, `in_progress`, `done` |
| `labels` | `metadata.labels` | Array |
| `labels` (domain) | `metadata.domain` | First non-prefixed label |
| `labels` (tier:) | `metadata.tier` | `pro` or `oss` |
| `labels` (milestone:) | `metadata.milestone` | Target milestone |
| `priority.name` | `metadata.priority` | Lowercase |
| `Epic Link` | edge `BELONGS_TO` | Story→Epic relationship |
| `Parent to Child relations` | edge `BELONGS_TO` | Epic→Capability relationship |
| `Relates` link | edge `RELATED_TO` | Cross-epic dependencies |
| `description` | `metadata.description` | Truncated to first 500 chars for graph |
| `created` | `created` | ISO timestamp |
| `updated` | `metadata.updated` | ISO timestamp |

### Node ID Convention

```
{type}-{key}
```

Examples: `epic-RAISE-651`, `story-RAISE-584`, `bug-RAISE-648`, `capability-RAISE-644`

This replaces the old `epic-e8`, `story-f8-1` IDs from filesystem scope.md parsing.

---

## 9. Enforcement

- **Session start** (`/rai-session-start`): surface issues without required labels as signals
- **Story close** (`/rai-story-close`): verify new issues created during story have required metadata
- **Graph build** (`rai graph build`): warn on issues missing required fields for graph nodes
- **Backlog reviews**: periodic cleanup using this document as checklist

---

*Created: 2026-03-22*
*Applies to: RAISE project on humansys.atlassian.net*
*Related: RAISE-651 (Graph Data Abstraction), `.raise/jira.yaml` (instance config)*
