# RAISE-819: Forge MVP — Rovo Agents + raise-server Integration — Design

## Gemba (Current State)

### raise-server (exists, E275 + E616)

FastAPI app with PostgreSQL 16, SQLAlchemy 2.0 async, Alembic migrations.

**Endpoints available:**
- `POST /api/v1/graph/sync` — idempotent full graph upsert (nodes + edges)
- `GET /api/v1/graph/query` — GIN full-text search (`?q=...&limit=N`)
- `POST /api/v1/agent/events` — store agent telemetry
- `GET /api/v1/agent/events` — list agent events
- `POST /api/v1/memory/patterns` — store shared pattern
- `GET /api/v1/memory/patterns` — list patterns
- `GET /health` — server status + DB check

**Auth:** API key per org (`Bearer rsk_...`), hash stored in DB.
**License:** E616 added org/member/license management.

### Adapter Layer (raise-cli)

Protocol-based, transport-agnostic:
- `AcliJiraAdapter` — ACLI subprocess, production
- `McpConfluenceAdapter` — mcp-atlassian via McpBridge, production
- Pydantic models for all I/O (`IssueRef`, `IssueDetail`, `PageContent`, etc.)

### Forge/Rovo (does not exist yet)

No Forge app. No Rovo agents. This epic creates them.

## Target Architecture

```
User (Jira / Confluence)
  │
  ▼
Rovo Chat (native UI — zero custom UI code)
  │
  ├── Rai Governance Agent
  │     prompt: governance-prompt.txt
  │     actions: read-page, query-graph, sync-governance, validate-document
  │
  └── Rai Dev Agent
        prompt: dev-prompt.txt
        actions: read-jira-context, query-graph, report-event
  │
  ▼
Forge Actions (sync handlers, < 25s)
  │
  ├── Simple queries → direct response
  └── Complex work → Async Events API → Queue Consumer (up to 900s)
  │
  ▼
fetch() ──→ raise-server (HTTPS)
  │           POST /graph/sync
  │           GET  /graph/query
  │           POST /agent/events
  │           POST /memory/patterns
  │
  ▼
Forge KVS (conversation state, session data)
```

### Key Architectural Principles

1. **RaiSE backend = canonical knowledge layer.** Deterministic graph queries and
   validation logic stay in raise-server. Forge is the distribution/collaboration layer.

2. **Rovo = friendly face, not reasoning engine.** Rovo's 5M+ MAU provides
   distribution. The intelligence lives in the knowledge graph.

3. **Zero Custom UI for MVP.** Rovo chat is the entire UX. No issuePanel,
   no Confluence macro. This eliminates UI code and keeps scope to 3 weeks.

4. **Async by default for backend calls.** The 25s sync timeout is hard.
   Any action that calls raise-server should be prepared to use the async
   queue consumer pattern if response time is unpredictable.

## Forge App Structure

```
raise-forge/                     # New package in monorepo
├── manifest.yml                 # Forge manifest (modules, permissions, resources)
├── package.json                 # Node.js 22, @forge/kvs, @forge/api
├── src/
│   ├── agents/
│   │   ├── governance-prompt.txt  # Rai Governance system prompt
│   │   └── dev-prompt.txt         # Rai Dev system prompt
│   ├── actions/
│   │   ├── read-page.js           # Read current Confluence page
│   │   ├── read-jira-context.js   # Read current Jira issue
│   │   ├── query-graph.js         # Query raise-server graph
│   │   ├── sync-governance.js     # Sync Confluence → graph
│   │   ├── validate-document.js   # Validate against standards
│   │   └── report-event.js        # Send telemetry event
│   ├── lib/
│   │   ├── raise-client.js        # raise-server HTTP client
│   │   ├── state.js               # KVS state management
│   │   └── confluence.js          # Confluence API helpers
│   └── index.js                   # Function exports
└── tests/
    └── *.test.js                  # Jest unit tests
```

## Key Contracts

### Forge → raise-server

All calls use `fetch()` with Bearer auth from Secret Store.

```
// Graph query
GET https://api.raise-server.example.com/api/v1/graph/query
  ?q=code-standards+guardrails
  &limit=20
Headers: Authorization: Bearer rsk_...
Response: { results: [...], total: N, query: "..." }

// Graph sync
POST https://api.raise-server.example.com/api/v1/graph/sync
Body: { project_id: "...", nodes: [...], edges: [...] }
Headers: Authorization: Bearer rsk_...
Response: { synced_nodes: N, synced_edges: N }

// Telemetry
POST https://api.raise-server.example.com/api/v1/agent/events
Body: { agent_id: "rai-governance", event_type: "action_invoked", payload: {...} }
Headers: Authorization: Bearer rsk_...
```

### Forge KVS State Schema

```javascript
// Key pattern: state:{accountId}:{contextAri}
{
  lastAction: "query-graph",
  lastQuery: "code standards for Python",
  lastResultSummary: "Found 3 applicable standards...",
  governanceSyncTimestamp: "2026-03-27T10:00:00Z",
  sessionStart: "2026-03-27T09:45:00Z"
}
```

**Constraints:** 240 KiB max per value. Strictly consistent on `get()`.

### Manifest Key Sections

```yaml
modules:
  rovo:agent:
    - key: rai-governance
      name: "Rai Governance"
      description: "AI governance copilot backed by RaiSE knowledge graph"
      prompt: resource:prompts;agents/governance-prompt.txt
      conversationStarters:
        - "What are our code standards?"
        - "Does this page follow our testing policy?"
        - "Sync governance docs from this space"
      actions:
        - read-page
        - query-graph
        - sync-governance
        - validate-document

    - key: rai-dev
      name: "Rai Dev"
      description: "Developer assistant with architecture and pattern knowledge"
      prompt: resource:prompts;agents/dev-prompt.txt
      conversationStarters:
        - "What patterns apply to this story?"
        - "Show me the architecture for this component"
        - "What ADRs affect this area?"
      actions:
        - read-jira-context
        - query-graph
        - report-event

  action:
    - key: read-page
      function: readPageFn
      actionVerb: GET
      # ... (typed inputs: pageId)

    - key: query-graph
      function: queryGraphFn
      actionVerb: GET
      # ... (typed inputs: query, limit)

    - key: sync-governance
      function: syncGovernanceFn
      actionVerb: TRIGGER
      # ... (typed inputs: spaceKey, parentPageId)

    - key: validate-document
      function: validateDocumentFn
      actionVerb: GET
      # ... (typed inputs: pageId, documentType)

    - key: read-jira-context
      function: readJiraContextFn
      actionVerb: GET
      # ... (typed inputs: issueKey)

    - key: report-event
      function: reportEventFn
      actionVerb: CREATE
      # ... (typed inputs: eventType, payload)

permissions:
  scopes:
    - read:jira-work
    - write:jira-work
    - read:confluence-content.all
    - write:confluence-content.all
    - read:confluence-props
    - write:confluence-props
    - storage:app
    - read:chat:rovo
  external:
    fetch:
      backend:
        - 'https://api.raise-server.example.com'

app:
  runtime:
    name: nodejs22.x
```

## Governance Sync Flow (Core Innovation)

```
1. User asks Rai Governance: "Sync governance docs from RaiSE1 space"
2. Agent invokes sync-governance action with spaceKey="RaiSE1"
3. Action (async consumer, 900s timeout):
   a. GET /wiki/api/v2/spaces/RaiSE1/pages (label: governance)
   b. For each governance page:
      - Parse markdown/storage format
      - Extract: standards, guardrails, rules, policies
      - Transform to graph nodes (type: guardrail, standard, policy)
      - Create edges (governed_by, implements)
   c. POST /api/v1/graph/sync with all nodes + edges
4. Return summary: "Synced 15 governance docs → 47 graph nodes, 82 edges"
5. Agent presents result to user
```

## Validate-Document Flow (The "Aha Moment")

```
1. User on a Confluence page asks: "Does this follow our standards?"
2. Agent invokes read-page to get current page content
3. Agent invokes query-graph with relevant terms from the page
4. Agent invokes validate-document with pageId + documentType
5. validate-document action:
   a. GET page content from Confluence API
   b. GET applicable standards from raise-server graph
   c. Compare content against standards (structural check)
   d. Return: { compliant: [...], violations: [...], suggestions: [...] }
6. Agent presents findings with links to source governance pages
```

## Decisions

### ADR-034: Rovo-Only UI for Forge MVP

**Context:** We need a Forge app UI in 3 weeks. Options: Custom UI (React in
iframe), UI Kit 2 (native components), or Rovo agents only (chat interface).

**Decision:** Rovo agents as the only UI. No Custom UI, no UI Kit panels.

**Consequences:**
- ✅ Zero UI code to write, test, maintain
- ✅ Native Jira/Confluence integration via chat
- ✅ Users already familiar with Rovo chat
- ⚠️ No visual dashboards or data tables in MVP
- ⚠️ Limited to conversational interaction patterns

**Alternatives rejected:**
- Custom UI: too much code for 3 weeks, iframe overhead
- UI Kit 2: faster than Custom UI but still requires React components

### ADR-035: raise-server as Canonical Knowledge Store (not Forge Storage)

**Context:** Graph data (1,589 nodes + 33K edges for single project) needs
a store. Options: Forge Custom Entity Store or raise-server PostgreSQL.

**Decision:** raise-server PostgreSQL remains the canonical store. Forge KVS
for conversation state only.

**Consequences:**
- ✅ PostgreSQL + GIN handles complex graph queries at scale
- ✅ raise-server already built and validated (E275)
- ✅ No Forge Entity Store 100-condition or 240KB limits
- ⚠️ External dependency (raise-server must be available)
- ⚠️ Additional latency (Forge → external fetch → raise-server)

**Alternatives rejected:**
- Forge Custom Entity Store: 100 conditions per query, 240KB values, would
  hit limits at org scale. Good for session state, not for knowledge graphs.

### ADR-036: Async Queue Consumer Pattern for Backend Calls

**Context:** Forge sync functions have a 25s hard timeout. raise-server
graph sync operations may take longer.

**Decision:** Use Async Events API + queue consumer (900s timeout) for all
raise-server calls that involve data sync or LLM processing.

**Consequences:**
- ✅ 15-minute timeout accommodates large graph syncs
- ✅ Up to 50 events per request for batch processing
- ⚠️ More complex than direct sync calls
- ⚠️ Results not immediately available (need KVS state + polling or Realtime)

**Alternatives rejected:**
- Direct sync calls only: would fail on graph sync operations > 25s
- Forge Realtime: Preview status, adds complexity. Reserve for post-MVP streaming.

## Component Impact

| Component | Impact | Changes |
|-----------|--------|---------|
| raise-forge (NEW) | New package | Entire Forge app |
| raise-server | None | No changes — existing APIs are sufficient |
| raise-cli | None | No changes — CLI adapters unaffected |
| raise-core | None | Graph models consumed by raise-server |

## Testing Strategy

- **Unit:** Jest + mocked `@forge/kvs`, `@forge/api`. Test action handlers as pure functions.
- **Integration:** `forge tunnel` against dev Atlassian site + local raise-server.
- **E2E:** Manual governance loop on our own instance. Demo script as acceptance test.

## Deployment

- Environment: development (tunnel) → staging (deploy) → production (deploy)
- Distribution: link (no Marketplace review)
- CI/CD: GitHub Actions with `FORGE_EMAIL` + `FORGE_API_TOKEN` (post-MVP)
- Secret Store: raise-server API key
