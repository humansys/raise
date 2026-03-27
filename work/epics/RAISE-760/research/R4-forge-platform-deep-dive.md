---
research_id: R4-RAISE-760
title: Forge Platform Deep-Dive 2026
epic: RAISE-760
date: 2026-03-27
status: complete
confidence: High
---

# R4: Forge Platform Deep-Dive

## Executive Summary

Atlassian Forge in March 2026 is a mature FaaS platform running native Node.js 20/22, with the legacy sandbox fully retired (Feb 2025). The platform provides four function types (sync/25s, async/900s, scheduled/900s, web trigger/55s), three storage tiers (KVS, Custom Entity Store, Secret Store), two UI approaches (UI Kit 2 and Custom UI), and first-class Rovo agent/action modules for AI integration. For the RaiSE MVP, the architecture is clear: **Rovo agents as the primary UI**, async functions for backend calls that may exceed 25s, Forge KVS for state persistence, and external fetch to the raise-server backend.

**Key findings that update or refine R1:**
1. **KVS value limit is 240 KiB** (not 128 KiB as some older sources report) -- confirmed from official platform quotas docs
2. **Native Node.js runtime has NO sandbox restrictions** -- fs, child_process, and all npm packages are available (isolation is at VM layer)
3. **Forge Bridge Rovo API graduated from EAP** (Nov-Dec 2025) -- programmatic agent invocation from Custom UI is now available
4. **Forge Realtime is Preview** (stable but under active development) -- suitable for MVP streaming patterns
5. **Forge LLMs API remains EAP** -- do NOT depend on it; use external LLM via fetch() as planned
6. **Cold start overhead is ~1s** per community reports, plus ~1s Bridge invoke overhead

**3-week MVP is feasible** with the architecture: Rovo Agent + Actions + fetch() to raise-server. No Custom UI needed for MVP; Rovo chat provides the entire UX. Forge KVS handles conversation state persistence. The main risk is the 65K points/hr rate limit for multi-tenant scenarios.

---

## 1. Runtime & Constraints

### 1.1 Function Types

| Type | Timeout | Use Case | Configuration |
|------|---------|----------|---------------|
| **Sync (resolver/handler)** | 25s hard limit | UI interactions, API responses | Default for all function modules |
| **Async (event consumer)** | 55s default, up to 900s (15 min) | LLM calls, bulk operations, data sync | `timeoutSeconds: 900` in manifest |
| **Scheduled trigger** | 55s default, up to 900s | Periodic sync, health checks | Intervals: `fiveMinute`, `hour`, `day`, `week` |
| **Web trigger** | 55s | Inbound webhooks from external systems | HTTPS endpoint generated via Forge CLI |

**Async Events API details:**
- Push up to 50 events per request
- Max combined payload: 200 KB
- Events can be delayed up to 15 minutes via `delayInSeconds`
- Consumer functions referenced by `consumer` module in manifest

**Evidence level:** Very High (official docs: platform-quotas-and-limits, scheduled-trigger, async-events-api)

### 1.2 Node.js Runtime

| Property | Value |
|----------|-------|
| Supported versions | `nodejs20.x`, `nodejs22.x` |
| Deprecated versions | `nodejs18.x` (deploys fail since late 2025) |
| Legacy sandbox | **Fully retired** (Feb 28, 2025 -- apps stop working) |
| Module system | CommonJS and ESM both supported |
| npm packages | **All packages work** -- no sandbox restrictions |
| Built-in Node modules | **All available** including `fs`, `child_process`, `crypto` |
| Snapshots | Enabled by default (improves cold start) |

**Critical caveat:** Without the V8 isolate sandbox, local state in Forge functions is NOT cleared between invocations. Developers MUST NOT persist customer data in global state, in memory, or on disk between invocations. This is a security responsibility, not a platform guarantee.

**Evidence level:** Very High (official docs: native-nodejs-runtime, legacy-runtime-migrating; community: Node 18 deprecation thread)

### 1.3 Memory Limits

| Resource | Limit |
|----------|-------|
| Default memory | 512 MB per invocation |
| Maximum memory | 1 GB (configurable in manifest) |
| Response payload (frontend) | 5 MB max |
| Rovo action data | 5 MB max |

**Evidence level:** Very High (official docs: platform-quotas-and-limits, limits-invocation)

### 1.4 Cold Start & Latency

- Forge uses **snapshots by default** to reduce cold start
- Legacy sandbox removal "moderately improves" invocation performance
- Community reports indicate **~1s overhead** for Forge Bridge invoke calls (the round-trip between UI and backend function)
- Geographic latency is notable for European users (Forge runs on AWS, region selection is limited)
- Invocation metrics are available via the Developer Console for monitoring

**Invocation rate limit:** 1,200 invocations per 60-second sliding window per app installation.

**Evidence level:** High (official docs: monitor-invocation-metrics; community: "Forge invoke is very slow", "Bridge functions geographic latency" threads)

### 1.5 External Communication

| Constraint | Detail |
|------------|--------|
| Protocol | **HTTPS only** (no HTTP, no raw TCP) |
| Allowed ports | 80, 443, 8080, 8443, 8444, 7990, 8089, 8090, 8085, 8060 |
| Domain declaration | **All external domains must be declared** in `permissions.external.fetch.backend` |
| Redirect handling | Redirected domains must also be declared |
| Major version bump | Adding new remotes triggers major version upgrade (admin re-consent required) |
| Single outbound request timeout (async) | 180s max for any single fetch in async context |

```yaml
# manifest.yml example
permissions:
  external:
    fetch:
      backend:
        - 'https://api.raise-server.example.com'
```

**Evidence level:** Very High (official docs: permissions, runtime-egress-permissions, external-fetch-api)

---

## 2. Storage Options

### 2.1 Key-Value Store (KVS)

| Property | Limit |
|----------|-------|
| Key length | 500 bytes max |
| Key format | Must match `/^(?!\s+/` (no leading whitespace) |
| Value size | **240 KiB** per persisted value |
| Object depth | 31 levels max |
| Read throughput | 12 MB/s per key |
| Write throughput | 1 MB/s per key |
| Query throughput | 24 MB/s per index value |
| Scope | Per app installation (automatic namespace isolation) |
| Consistency | `get()` is **strictly consistent**; `query()` is **eventually consistent** |
| Transactions | Supported (conditional writes with filters) |

**When to use KVS:**
- Simple key-value lookups (conversation state, user preferences, config)
- Data not tied to a specific Atlassian entity
- Global or tenant-scoped application state
- Data needing complex queries (use Custom Entity Store variant)

**Package migration:** As of March 2025, all new features are in `@forge/kvs` package only. Legacy `@forge/api` storage module receives no further updates.

**Evidence level:** Very High (official docs: limits-kvs-ce, platform-quotas-and-limits, storage-api-basic)

### 2.2 Custom Entity Store

The Custom Entity Store extends KVS with structured data, indexes, and complex queries.

**Key features:**
- Define entities with typed properties in manifest
- Create indexes for efficient querying
- Complex queries with `WhereConditions` (beginsWith, contains, greaterThan, etc.)
- **Max 100 conditions per complex query**
- Cursor-based pagination for large result sets
- Sort support (ASC/DESC)

```javascript
// Example: Query employees over 30, sorted descending
import kvs, { WhereConditions, Sort } from "@forge/kvs";

const results = await kvs
  .entity('employee')
  .query()
  .index('by-age')
  .where(WhereConditions.greaterThan(30))
  .sort(Sort.DESC)
  .getMany();
```

**Consistency model:**
- `entity().get()` -- strictly consistent (current data)
- `entity().query()` -- **eventually consistent** (may return slightly stale data)

**When to use Custom Entity Store:**
- Structured data with relationships (agent session history, pattern catalog)
- Data requiring filtered queries or sorting
- Data needing indexes for efficient retrieval

**Evidence level:** Very High (official docs: storage-api-custom-entities, storage-api-query-complex)

### 2.3 Secret Store

- Encrypted key-value storage for sensitive data (API keys, tokens, credentials)
- Set via Forge CLI: `forge variables:set --encrypt SECRET_NAME`
- Accessed at runtime via `@forge/kvs` or environment variables
- Scoped per environment (dev, staging, production)

**For RaiSE MVP:** Store the raise-server API key (`rsk_...`) in Secret Store.

**Evidence level:** Very High (official docs: storage-api-secret)

### 2.4 Entity Properties (Atlassian Product Storage)

An alternative to Forge Storage -- data stored directly on Atlassian entities (issues, pages, users) via REST API.

| Dimension | Forge Storage | Entity Properties |
|-----------|--------------|-------------------|
| Performance | **2x+ faster** read/write | Slower |
| Scope | App-scoped (isolated) | Entity-scoped (visible to other apps) |
| Query support | Complex queries, indexes | Limited (REST API filtering) |
| Visibility | Not visible in Atlassian UI | Accessible via REST API |
| Best for | App state, session data | Issue/page metadata, cross-app data |

**For RaiSE MVP:** Use Forge KVS for agent conversation state. Use content properties only if data needs to be visible to other integrations or the REST API.

**Evidence level:** High (community: "Entity Properties or Forge Storage? A Performance Battle")

### 2.5 Storage Migration Patterns

- Use the Async Events API + queue consumer pattern for bulk data migrations
- `timeoutSeconds: 900` gives 15 minutes for migration functions
- Transaction support enables atomic updates during migration
- Cursor-based pagination for iterating large datasets

**Evidence level:** High (official docs: sql-migration-guide)

---

## 3. UI Options

### 3.1 UI Kit 2 vs Custom UI

| Dimension | UI Kit 2 | Custom UI |
|-----------|----------|-----------|
| Rendering | **Native** (same components as Atlassian) | **iframe** (isolated environment) |
| Framework | `@forge/react` components | Any framework (React, Vue, vanilla) |
| Styling | Atlassian Design System (automatic) | Full HTML/CSS/JS control |
| DOM access | No direct DOM access | Full browser DOM |
| Performance | Better (no iframe overhead) | Additional iframe overhead |
| Resources | Images only | HTML, CSS, JS, images, fonts |
| Portals/Refs | Not supported | Fully supported |
| Bridge API | Direct access to product APIs | Via `@forge/bridge` package |
| Learning curve | Lower (fewer choices) | Higher (more flexibility) |
| Best for | Standard UI patterns, quick builds | Complex custom interfaces |

**For RaiSE MVP:** Neither is needed initially. Rovo chat provides the primary UX. If a Jira issue panel or Confluence panel is added later, UI Kit 2 is preferred for speed and native look.

**Evidence level:** Very High (official docs: ui-kit/compare, ui-kit/overview, user-interface)

### 3.2 Available Extension Points

**Jira modules:**
- `jira:issuePanel` -- Panel in issue view (UI Kit or Custom UI)
- `jira:issueContext` -- Collapsible panel on right side of issue (replaces deprecated issueGlance)
- `jira:projectPage` -- Full page within project navigation
- `jira:globalPage` -- Full page in global navigation
- `jira:dashboardGadget` -- Dashboard widget
- `jira:customField` -- Custom field types
- `jira:workflowValidator` / `jira:workflowCondition` / `jira:workflowPostFunction`

**Confluence modules:**
- `confluence:contentAction` -- Action menu item on pages
- `confluence:contextMenu` -- Editor context menu
- `confluence:globalPage` -- Full page
- `confluence:homepageFeed` -- Homepage feed item
- `confluence:contentByLineItem` -- Byline item under page title
- `confluence:macro` -- Custom macro in editor

**Cross-product modules:**
- `rovo:agent` -- AI agent with chat interface
- `rovo:action` -- Agent capability (function)
- `trigger:` -- Product event triggers (issue created, page updated, etc.)
- `scheduledTrigger` -- Periodic execution
- `webtrigger` -- Inbound webhooks
- `function` -- Backend function handlers

**Evidence level:** Very High (official docs: modules index, jira modules, confluence modules)

### 3.3 Bridge API

The Forge Bridge provides client-side APIs for communication between UI and backend:

- `invoke()` -- Call resolver functions from UI
- `requestJira()` / `requestConfluence()` -- Direct product API calls from UI
- `rovo.open()` -- Programmatically open Rovo chat sidebar (graduated from EAP)
- `getContext()` -- Get current product context (issue key, page ID, etc.)
- `showFlag()` -- Display notification flags

**Evidence level:** Very High (official docs: ui-api-bridge, forge-bridge-rovo)

---

## 4. Rovo Integration

### 4.1 Agent Module

The `rovo:agent` module defines an AI agent that integrates into Jira and Confluence workflows.

**Manifest structure:**
```yaml
modules:
  rovo:agent:
    - key: rai-governance       # Unique identifier
      name: "Rai Governance"    # Display name in Rovo chat
      description: "..."        # Shown in agent selector
      icon: resource:res;icons/rai.svg  # Optional custom icon
      prompt: |                 # System prompt (or resource:key;path/to/file.txt)
        You are Rai, a governance copilot...
      conversationStarters:     # Suggested prompts shown to user
        - "Review this document"
        - "Create a Lean Business Case"
      actions:                  # References to action module keys
        - read-governance-doc
        - validate-document
        - graph-sync
      followUpPrompt: "..."     # Optional prompt appended after action results
```

**Key capabilities:**
- **Prompt from file:** `prompt: resource:key;path/to/prompt.txt` (since CLI v10.6.0)
- **Multiple agents per app:** Define multiple entries in `rovo:agent` array
- **Conversation starters:** Up to N predefined prompts shown to users
- **Action chaining:** Agent decides when to invoke which actions based on prompt + user request
- **Context awareness:** Agent has access to the current page/issue context

**Evidence level:** Very High (official docs: rovo-agent module, tutorials)

### 4.2 Action Module

Actions are the capabilities agents can invoke, implemented as Forge functions.

**Manifest structure:**
```yaml
modules:
  action:
    - key: validate-document
      name: Validate document against governance standards
      function: validateDocumentFn
      actionVerb: GET            # GET, CREATE, UPDATE, TRIGGER
      description: |
        Validates a governance document against RaiSE standards
        and knowledge graph constraints
      inputs:
        pageId:
          title: Page ID
          type: string
          required: true
          description: "The Confluence page ID to validate"
        documentType:
          title: Document Type
          type: string
          required: false
          description: "The type of governance document (LBC, ADR, etc.)"
```

**Action verbs:** `GET`, `CREATE`, `UPDATE`, `TRIGGER` -- help the agent understand the action's nature.

**Input types:** `string`, `number`, `boolean`, `object`, `array`

**Return value:** Any string or JSON object. The agent interprets and transforms it into natural language for the user.

**Cross-app availability:** Adding `read:chat:rovo` scope to permissions makes actions available to customer-built agents.

**Evidence level:** Very High (official docs: rovo-action module, tutorials)

### 4.3 Bridge API for Rovo

The Forge Bridge Rovo API enables programmatic agent invocation from Custom UI or UI Kit apps.

```javascript
import { rovo } from '@forge/bridge';

// Open Rovo chat with a specific Forge agent
await rovo.open({
  type: 'forge',
  agentName: 'Rai Governance',
  agentKey: 'rai-governance',
  prompt: 'Review this Lean Business Case'
});

// Open with the default Rovo agent
await rovo.open({
  type: 'default',
  prompt: 'Help me with this page'
});
```

**Payload types:**
- `ForgeAgentPayload`: `type: 'forge'`, `agentName`, `agentKey`, optional `prompt`
- `AtlassianAgentPayload`: `type: 'atlassian'`, `agentName`, optional `prompt`
- `DefaultAgentPayload`: `type: 'default'`, optional `prompt`

**Status:** Graduated from EAP (Nov-Dec 2025). Now available for production use.

**For RaiSE MVP:** Not needed initially (users invoke agent directly from Rovo chat). Useful post-MVP for a `jira:issuePanel` that opens Rai in context.

**Evidence level:** High (official docs: forge-bridge-rovo; community: EAP announcement thread)

### 4.4 Multi-Agent Patterns

Forge supports multiple agents per app via multiple entries in the `rovo:agent` array. Each agent has its own prompt, conversation starters, and action set.

**RaiSE pattern:**
```yaml
modules:
  rovo:agent:
    - key: rai-governance
      name: "Rai Governance"
      prompt: resource:prompts;governance-prompt.txt
      actions: [read-page, validate-doc, graph-sync, report-event]
    - key: rai-dev
      name: "Rai Dev"
      prompt: resource:prompts;dev-prompt.txt
      actions: [query-constraints, get-adrs, report-event]
```

**Shared actions:** Both agents can reference the same action keys. Actions are defined once and shared.

**Agent selection:** Users select which agent to talk to from the Rovo agent picker in the chat sidebar.

**Evidence level:** High (official docs: rovo-agent, extend-atlassian-products-with-a-forge-rovo-agent)

### 4.5 Memory Workarounds

Rovo has **no built-in memory between conversations**. Each conversation starts fresh.

**Workaround pattern using Forge KVS:**
```javascript
// In action handler: persist conversation state
import kvs from '@forge/kvs';

export const handler = async (payload, context) => {
  const userId = context.accountId;
  const stateKey = `session:${userId}:${payload.contextId}`;

  // Read prior state
  const priorState = await kvs.get(stateKey);

  // Do work...
  const result = await processWithContext(payload, priorState);

  // Persist updated state
  await kvs.set(stateKey, {
    ...priorState,
    lastAction: 'validate-doc',
    lastResult: result.summary,
    timestamp: Date.now()
  });

  return result;
};
```

**Alternative:** Confluence content properties -- useful when state should be visible via REST API or tied to a specific page.

**Evidence level:** High (prior research RAISE-273; official docs: Forge KVS)

---

## 5. External Communication

### 5.1 fetch() API

Forge provides a global `fetch()` function for HTTPS calls to external services.

**Constraints:**
- HTTPS only (no HTTP)
- All domains pre-declared in manifest `permissions.external.fetch.backend`
- Adding new domains triggers major version bump (admin re-consent)
- Single request timeout: 180s in async context
- Supports standard request/response patterns

```javascript
// In a Forge function
const response = await fetch('https://api.raise-server.example.com/api/v1/graph/query?q=ADR-003', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${apiKey}`,
    'Content-Type': 'application/json'
  }
});
const data = await response.json();
```

### 5.2 Webhook Handling

**Inbound (Web Triggers):**
- Forge generates a unique HTTPS URL via CLI
- External systems (raise-server, CI/CD) can POST to this URL
- Handler receives method, headers, body, queryParameters
- 55s timeout
- Response: statusCode + headers + body

**Outbound (Product Events):**
- Subscribe to Atlassian product events in manifest (issue created, page updated, etc.)
- Event triggers invoke Forge functions
- Use Async Events API for chaining long-running work

### 5.3 Forge Realtime

**Status:** Preview (stable, under active development)

Push-based event streaming for long-running operations. Primary use case: streaming LLM responses to the UI.

**Pattern:**
1. UI sends request to resolver
2. Resolver pushes work to async queue consumer
3. Queue consumer runs up to 15 minutes
4. Consumer publishes results via Forge Realtime
5. UI subscribes to channel and receives incremental updates

This avoids storage-polling latency and keeps the UI responsive during LLM calls.

**For RaiSE MVP:** Useful if we need to show streaming progress from raise-server LLM calls. However, since Rovo handles its own streaming UX, this may not be needed for the Rovo-only MVP. Reserve for Custom UI panels post-MVP.

**Evidence level:** High (official docs: forge-realtime, llm-long-running-process-with-forge-realtime)

### 5.4 Connection to raise-server

**Manifest configuration:**
```yaml
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
        - 'https://*.raise-server.example.com'  # wildcard supported
```

**Authentication from Forge to raise-server:**
- API key stored in Forge Secret Store
- Retrieved at runtime: `const apiKey = process.env.RAISE_API_KEY;`
- Passed as Bearer token in Authorization header

---

## 6. Development & Deployment

### 6.1 CLI Tooling

| Command | Purpose |
|---------|---------|
| `forge create` | Scaffold new app from template |
| `forge deploy` | Bundle and deploy to Forge platform |
| `forge deploy -e staging` | Deploy to specific environment |
| `forge tunnel` | Local development with live Atlassian site |
| `forge install` | Install app on Atlassian site |
| `forge logs` | View runtime logs (dev/staging only) |
| `forge variables:set` | Set environment variables |
| `forge variables:set --encrypt` | Set encrypted secrets |
| `forge environments` | Manage contributor environments |
| `forge webtrigger` | Get web trigger URLs |

**Forge MCP Server:** Atlassian provides a Forge MCP server for AI-assisted development (documented at `forge-mcp`).

### 6.2 Environment Management

| Environment | Tunnel | Logs | Deploy | Purpose |
|-------------|--------|------|--------|---------|
| Development | Yes | Yes | Yes | Local development, per-contributor |
| Staging | **No** | Yes | Yes | Pre-production testing |
| Production | **No** | **No** | Yes | Live users |

- Each environment has **separate storage** (KVS, entities, secrets)
- Multiple development environments for team collaboration
- Default development environment set on first deploy

### 6.3 Testing Strategies

**Unit testing:**
- Jest is the community standard for Forge apps
- Mock `@forge/bridge`, `@forge/kvs`, and `@forge/api` imports
- Test action handlers as pure functions with mocked dependencies

**Integration testing:**
- Use `forge tunnel` to test against live Atlassian site
- Mock external APIs (raise-server) with local test servers
- Test KVS operations in development environment

**E2E testing:**
- Deploy to development environment
- Manually test via Rovo chat or product UI
- No official Forge E2E testing framework exists
- Community uses Playwright/Cypress for Custom UI testing

**For RaiSE MVP:** Unit tests for action handlers + manual E2E via `forge tunnel`. Keep it simple.

**Evidence level:** High (community: testing threads; official docs: tunneling, building-integrations)

### 6.4 CI/CD

**Bitbucket Pipelines:** Official reference configuration available. Uses `FORGE_EMAIL` and `FORGE_API_TOKEN` environment variables.

**GitHub Actions:** Not officially documented but feasible:
```yaml
# .github/workflows/deploy.yml (conceptual)
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
      - run: npm ci
      - run: npx @forge/cli deploy -e staging --non-interactive
        env:
          FORGE_EMAIL: ${{ secrets.FORGE_EMAIL }}
          FORGE_API_TOKEN: ${{ secrets.FORGE_API_TOKEN }}
```

**Evidence level:** High (official docs: set-up-cicd; inferred for GitHub Actions)

### 6.5 Marketplace & Distribution

| Distribution Method | Use Case | Notes |
|---------------------|----------|-------|
| **Distribution link** | Direct sharing with specific customers | No review required, immediate |
| **Marketplace listing** | Public distribution | Review process required |
| **Forge CLI install** | Development/testing | Direct install via CLI |

- Since Sep 2025, **only Forge apps** can be newly listed on Marketplace
- No private Marketplace listings for Forge apps
- Marketplace revenue share changes effective Jan 2026
- New Developer Terms effective Dec 2025 / Jan 2026

**For RaiSE MVP:** Use distribution link for Coppel. No Marketplace listing needed initially.

**Evidence level:** Very High (official docs: listing-forge-apps, runs-on-atlassian)

---

## 7. Known Gotchas

### 7.1 Runtime Gotchas

| Gotcha | Impact | Mitigation |
|--------|--------|------------|
| **25s sync timeout is hard** | LLM calls will timeout | Use async functions (900s) + queue pattern |
| **Global state persists between invocations** | Data leak risk | Never store customer data in module-level variables |
| **~1s Bridge invoke overhead** | UI feels sluggish | Minimize round-trips; batch data in single calls |
| **1,200 invocations/minute rate limit** | High-traffic apps throttled | Design for minimal invocations per user action |
| **100 log lines per runtime minute** | Hard to debug complex flows | Use structured logging, external log aggregation |
| **No production logs** | Cannot debug production issues | Reproduce in staging; use external telemetry (raise-server events) |

### 7.2 Storage Gotchas

| Gotcha | Impact | Mitigation |
|--------|--------|------------|
| **240 KiB value limit** | Cannot store large documents | Chunk data or store references; keep values lean |
| **Eventually consistent queries** | Stale data on reads after writes | Use `get()` for critical reads; `query()` for listings |
| **100 conditions per complex query** | Cannot build arbitrarily complex filters | Design data model for index-aligned queries |
| **@forge/api storage is frozen** | No new features since Mar 2025 | Migrate to `@forge/kvs` package |

### 7.3 Rovo Gotchas

| Gotcha | Impact | Mitigation |
|--------|--------|------------|
| **No conversation memory** | Context lost between sessions | Persist state in Forge KVS per user+context |
| **5 MB action data limit** | Cannot process large documents in single action | Chunk processing; summarize before returning |
| **Agent uses user's permissions** | Cannot access resources user cannot see | Use `asApp()` for system operations with explicit permission checks |
| **Prompt engineering is iterative** | Not plug-and-play | Use `prompt: resource:key;file.txt` for file-based prompt management |
| **Action descriptions drive invocation** | Agent decides when to call actions based on description | Invest in clear, specific action descriptions |

### 7.4 External Communication Gotchas

| Gotcha | Impact | Mitigation |
|--------|--------|------------|
| **Adding new domains = major version bump** | Admin re-consent required | Plan all domains upfront in manifest |
| **HTTPS only** | Cannot call HTTP services | Ensure raise-server has valid TLS cert |
| **Redirect domains must be declared** | Unexpected failures on redirects | Declare all possible redirect targets |
| **180s single request timeout (async)** | Very long LLM calls may fail | Implement timeout and retry in action handler |

### 7.5 Deployment Gotchas

| Gotcha | Impact | Mitigation |
|--------|--------|------------|
| **No tunnel for staging** | Must redeploy for every change | Test thoroughly in dev first |
| **No logs for production** | Blind debugging | Use raise-server telemetry events for observability |
| **Separate storage per environment** | Data isolation | Plan seed data strategy per environment |
| **npm packages pre-Apr 2024 may be incompatible** | Build failures | Pin recent package versions |

**Evidence level:** High (aggregated from official docs, community threads, prior research RAISE-273)

---

## 8. MVP Architecture Recommendation

### 8.1 Architecture Pattern

```
User (Jira/Confluence)
    |
    v
Rovo Chat (native UI -- zero custom UI code)
    |
    v
Rovo Agent: "Rai Governance" / "Rai Dev"
    |  (prompt + conversation starters)
    v
Forge Actions (sync handlers, < 25s)
    |
    |-- Simple queries: direct response
    |-- Complex work: push to async queue
    |
    v
Async Queue Consumer (up to 900s)
    |
    v
fetch() --> raise-server (HTTPS)
    |        |-- POST /graph/sync
    |        |-- GET  /graph/query
    |        |-- POST /agent/events
    |        |-- POST /memory/patterns
    |
    v
Forge KVS (conversation state, session data)
```

### 8.2 Forge Modules for MVP

```yaml
# manifest.yml structure
modules:
  # Two AI agents
  rovo:agent:
    - key: rai-governance
    - key: rai-dev

  # Shared actions (6-8 core actions)
  action:
    - key: read-page             # Read current Confluence page
    - key: read-jira-context     # Read current Jira issue + story context
    - key: find-skill-page       # Find governance skill definition in Confluence
    - key: validate-document     # Validate doc against graph constraints
    - key: update-page           # Write content to Confluence page
    - key: graph-sync            # Sync content to raise-server graph
    - key: query-constraints     # Query applicable ADRs/standards from graph
    - key: report-event          # Send telemetry to raise-server

  # Backend functions
  function:
    - key: readPageFn
    - key: readJiraContextFn
    - key: findSkillPageFn
    - key: validateDocFn
    - key: updatePageFn
    - key: graphSyncFn
    - key: queryConstraintsFn
    - key: reportEventFn

  # Inbound webhook (optional, for raise-server callbacks)
  webtrigger:
    - key: raise-server-webhook

  # Periodic graph sync (optional, post-MVP)
  # scheduledTrigger:
  #   - key: periodic-sync
  #     interval: hour

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
  id: ari:cloud:ecosystem::app/<app-id>
```

### 8.3 Three-Week Sprint Plan

| Week | Focus | Deliverables |
|------|-------|-------------|
| **Week 1** | Forge app scaffold + core actions | Hello world agent, read-page action, fetch to raise-server working, KVS state persistence |
| **Week 2** | Agent prompts + action suite | Both agents with full prompts, all 6-8 actions implemented, validate-document flow end-to-end |
| **Week 3** | E2E testing + polish + demo prep | Full governance workflow (Ana creates LBC), review workflow (Rodo reviews), error handling, demo script |

### 8.4 Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| UI approach | Rovo chat only (no Custom UI) | Zero UI code; Rovo provides native UX; 3-week constraint |
| LLM provider | raise-server (external) | Forge LLMs is EAP; we control our own LLM stack |
| State persistence | Forge KVS | Faster than entity properties; simple key-value fits session state |
| Node.js version | 22.x | Latest supported; best performance |
| Async pattern | Queue consumer for graph-sync | graph-sync and validate may exceed 25s |
| Distribution | Distribution link | No Marketplace review delay; direct to Coppel |

### 8.5 Risk Summary for MVP

| Risk | Severity | Likelihood | Mitigation |
|------|----------|------------|------------|
| 65K pts/hr rate limit (Tier 1) | Medium | Low (single tenant MVP) | Monitor; apply for Tier 2 if needed |
| Action descriptions don't trigger correctly | Medium | Medium | Invest in prompt engineering; test iteratively |
| Forge platform outage | High | Low | No mitigation (platform dependency) |
| raise-server latency > 25s | Medium | Medium | All backend calls via async queue consumer |
| Rovo memory workaround insufficient | Medium | Medium | Design lean state; test with real workflows |

---

## Evidence Catalog

| # | Source | Type | Evidence Level | Key Finding |
|---|--------|------|---------------|-------------|
| E1 | [Forge Platform Quotas and Limits](https://developer.atlassian.com/platform/forge/platform-quotas-and-limits/) | Primary | Very High | 25s sync, 900s async, 240KiB KVS value, 1200 inv/min |
| E2 | [Native Node.js Runtime](https://developer.atlassian.com/platform/forge/runtime-reference/native-nodejs-runtime/) | Primary | Very High | Node 20/22, all npm packages, fs/child_process available |
| E3 | [Legacy Runtime Migration](https://developer.atlassian.com/platform/forge/runtime-reference/legacy-runtime-migrating/) | Primary | Very High | Legacy died Feb 2025; sandbox fully removed |
| E4 | [KVS and Custom Entity Store Limits](https://developer.atlassian.com/platform/forge/limits-kvs-ce/) | Primary | Very High | 240KiB value, 500-byte key, 100 conditions per query |
| E5 | [Custom Entity Store API](https://developer.atlassian.com/platform/forge/storage-reference/storage-api-custom-entities/) | Primary | Very High | Query with WhereConditions, indexes, cursor pagination |
| E6 | [KVS Transactions](https://developer.atlassian.com/platform/forge/storage-reference/transactions/) | Primary | Very High | Atomic conditional writes |
| E7 | [Rovo Agent Module](https://developer.atlassian.com/platform/forge/manifest-reference/modules/rovo-agent/) | Primary | Very High | Agent definition, prompt from file, conversation starters |
| E8 | [Rovo Action Module](https://developer.atlassian.com/platform/forge/manifest-reference/modules/rovo-action/) | Primary | Very High | Typed inputs, actionVerb, 5MB data limit |
| E9 | [Forge Bridge Rovo API](https://developer.atlassian.com/platform/forge/apis-reference/ui-api-bridge/rovo/) | Primary | Very High | Programmatic agent invocation from UI |
| E10 | [Rovo Bridge EAP Announcement](https://community.developer.atlassian.com/t/early-access-program-forge-bridge-rovo-api/97251) | Primary | High | EAP Nov-Dec 2025; now available |
| E11 | [Forge Permissions](https://developer.atlassian.com/platform/forge/manifest-reference/permissions/) | Primary | Very High | Domain allowlist, scope management, major version rules |
| E12 | [Runtime Egress Permissions](https://developer.atlassian.com/platform/forge/runtime-egress-permissions/) | Primary | Very High | HTTPS only, pre-declared domains, redirect handling |
| E13 | [Forge Realtime (Preview)](https://developer.atlassian.com/platform/forge/realtime/) | Primary | High | Push-based streaming, preview status |
| E14 | [LLM Long-Running with Realtime](https://developer.atlassian.com/platform/forge/llm-long-running-process-with-forge-realtime/) | Primary | High | Queue consumer + Realtime publish pattern |
| E15 | [Forge LLMs API (EAP)](https://developer.atlassian.com/platform/forge/runtime-reference/forge-llms-api/) | Primary | High | EAP, Claude models, streaming; NOT for production |
| E16 | [Forge LLM Limits](https://developer.atlassian.com/platform/forge/limits-llm/) | Primary | High | EAP quotas for Forge-hosted LLMs |
| E17 | [Forge Environments](https://developer.atlassian.com/platform/forge/environments-and-versions/) | Primary | Very High | Dev/staging/prod; separate storage; tunnel constraints |
| E18 | [Forge CI/CD Setup](https://developer.atlassian.com/platform/forge/set-up-cicd/) | Primary | High | Bitbucket Pipelines reference; FORGE_EMAIL/FORGE_API_TOKEN |
| E19 | [Forge Tunneling](https://developer.atlassian.com/platform/forge/tunneling/) | Primary | Very High | Cloudflare-based; dev only; hot-reload for Custom UI |
| E20 | [UI Kit vs Custom UI Comparison](https://developer.atlassian.com/platform/forge/ui-kit-2/compare/) | Primary | Very High | Native vs iframe, performance vs flexibility |
| E21 | [Jira Modules Index](https://developer.atlassian.com/platform/forge/manifest-reference/modules/index-jira/) | Primary | Very High | issuePanel, issueContext, projectPage, customField, etc. |
| E22 | [Forge Modules Overview](https://developer.atlassian.com/platform/forge/modules/) | Primary | Very High | Complete module catalog |
| E23 | [Scheduled Trigger](https://developer.atlassian.com/platform/forge/manifest-reference/modules/scheduled-trigger/) | Primary | Very High | fiveMinute/hour/day/week intervals, configurable timeout |
| E24 | [Web Trigger](https://developer.atlassian.com/platform/forge/runtime-reference/web-trigger/) | Primary | Very High | Inbound HTTPS, request/response format |
| E25 | [Async Events API](https://developer.atlassian.com/platform/forge/runtime-reference/async-events-api/) | Primary | Very High | 50 events/request, 200KB payload, delayInSeconds |
| E26 | [Runs on Atlassian Roadmap 2026](https://community.developer.atlassian.com/t/please-help-us-shape-the-runs-on-atlassian-roadmap-for-2026-and-beyond/99630) | Secondary | High | 1000+ RoA listings; 2026 roadmap in planning |
| E27 | [Entity Properties vs Forge Storage Performance](https://community.atlassian.com/forums/Jira-articles/Entity-Properties-or-Forge-Storage-A-Performance-Battle-for/ba-p/2795677) | Secondary | High | Forge Storage 2x+ faster than entity properties |
| E28 | [Forge Invoke Performance](https://community.developer.atlassian.com/t/forge-invoke-is-very-slow/68746) | Secondary | Medium | ~1s overhead for Bridge invoke calls |
| E29 | [Bridge Geographic Latency](https://community.developer.atlassian.com/t/forge-bridge-functions-are-very-slow-geographic-latency-in-europe/76604) | Secondary | Medium | Notable latency for European users |
| E30 | [Node 18 Runtime Deprecated](https://community.developer.atlassian.com/t/node-18-runtime-is-no-longer-supported-on-forge/94301) | Secondary | High | Node 18 deploys fail |
| E31 | [RFC-117: Forge LLMs](https://community.developer.atlassian.com/t/rfc-117-forge-llms/96506) | Secondary | High | Community feedback on Forge LLMs; EAP concerns |
| E32 | [Listing Forge Apps on Marketplace](https://developer.atlassian.com/platform/marketplace/listing-forge-apps/) | Primary | Very High | Distribution link for direct sharing |
| E33 | [Marketplace Revenue Share 2026](https://community.developer.atlassian.com/t/marketplace-revenue-share-updates-2026/91727) | Secondary | High | Revenue share changes effective Jan 2026 |
| E34 | Prior research RAISE-273 (Feb 2026) | Internal | High | Architecture validated; Rovo + backend pattern confirmed |
| E35 | R1-RAISE-760 (Mar 2026) | Internal | Very High | API landscape, rate limits, authentication summary |
