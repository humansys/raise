---
research_id: R1-RAISE-760
title: Atlassian API Landscape 2026
epic: RAISE-760
date: 2026-03-27
status: complete
confidence: High
---

# R1: Atlassian API Landscape

## Executive Summary

Atlassian's cloud platform in March 2026 offers a broad and maturing API surface across 11+ products, with a clear strategic direction: **Forge is the only path forward** for new app development, Connect reaches end of support in December 2026, and all new extensibility features are Forge-only. The platform is mid-transition on several fronts: a new points-based rate limiting system began phased enforcement on March 2, 2026; authentication is consolidating around OAuth 2.0 (3LO) and Forge app auth (asApp/asUser); and the Teamwork Graph is emerging as a unified data layer but remains in EAP.

For RaiSE's Forge app MVP (deadline: Apr 16, 2026), the most relevant APIs are: **Jira REST API v3** (issue CRUD, JQL, agile boards/sprints), **Confluence REST API v2** (page CRUD, CQL search), **Forge platform APIs** (storage, resolver, bridge, Rovo agent/action modules), and **Rovo** (AI agent framework with native chat UI). Compass GraphQL, Bitbucket REST v2, and Admin APIs are secondary targets for post-MVP expansion. The Teamwork Graph (Cypher + GraphQL) is strategically important but too immature (EAP) for production dependency.

The biggest risks for our integration are: (1) the new points-based rate limits — our app starts in Tier 1 with a shared 65,000 points/hour global pool, which could be tight for multi-tenant usage; (2) Forge's 25-second sync timeout requiring async patterns for LLM calls; and (3) Rovo's lack of memory between conversations, requiring workarounds via Forge Storage or content properties.

## Product API Matrix

| Product | API Type | Auth Methods | Rate Limits | Maturity | Docs Quality | MVP Priority |
|---------|----------|-------------|-------------|----------|-------------|-------------|
| **Jira Software** | REST v2, v3 | OAuth 2.0 (3LO), API token, Forge (asApp/asUser) | Points-based: 65K/hr (Tier 1); burst: per-second; per-issue write limits | GA, stable | Very Good | **P0** |
| **Jira Agile** | REST `/agile/1.0/` | Same as Jira Platform | Same as Jira Platform | GA, stable | Good | **P0** |
| **Jira Service Mgmt** | REST (service-desk specific) | Same as Jira Platform + JSM scopes | Same as Jira Platform | GA, stable | Good | P2 |
| **Confluence** | REST v1 (legacy), v2 (current) | OAuth 2.0 (3LO), API token, Forge (asApp/asUser) | Points-based (same system as Jira) | v2 GA, v1 deprecated path | Good | **P0** |
| **Bitbucket Cloud** | REST v2 | OAuth 2.0, API tokens (replacing app passwords), Forge | Per-token rate limits (from Nov 2025) | GA, stable | Good | P1 |
| **Compass** | GraphQL (via Forge toolkit) | Forge app auth | Standard Forge limits | GA | Good | P2 |
| **Teamwork Graph** | Cypher + GraphQL wrapper | Forge EAP only | EAP limits | **EAP — not production-ready** | Adequate | P3 (watch) |
| **Rovo** | Forge modules (agent/action) | Forge app auth; user permission context | Forge invocation limits | GA (since Apr 2025) | Good | **P0** |
| **Automation for Jira** | No public API; rule engine | N/A (configuration UI) | N/A | GA | Limited | P2 |
| **Admin / Org** | REST (Organizations, User Mgmt, User Provisioning) | OAuth 2.0, SCIM | Standard | GA, v1 sunset Jun 2026 | Good | P2 |
| **Guard (Access)** | Admin REST sub-APIs | Org admin auth | Standard | GA | Adequate | P3 |
| **Analytics** | No public REST API | N/A | N/A | Enterprise plan only | N/A | P3 |
| **Forge Platform** | Storage KVS, Custom Entity, Resolver, Bridge, Realtime | Forge runtime | Consumption-based (Jan 2026) | GA | Very Good | **P0** |

## Detailed Findings

### Jira (Software, Service Management, Work Management)

**API Versions:**
- **REST API v3** (`/rest/api/3/`): Current recommended version for Jira Cloud. Full CRUD on issues, projects, users, fields, workflows, permissions. JQL search. Webhooks.
- **REST API v2** (`/rest/api/2/`): Legacy but still functional. Main difference: v3 uses ADF (Atlassian Document Format) for rich text fields; v2 uses wiki markup.
- **Agile API** (`/rest/agile/1.0/`): Board, sprint, backlog, epic management. Separate from platform API. Max 50 issues per backlog move operation.
- **JSM API** (`/rest/servicedeskapi/`): Service desk, queues, SLA, request types, forms (ProForma). Separate scopes required.
- **JSM Ops API** (`/rest/v2/`): Incident and operations management.

**Authentication:**
- OAuth 2.0 (3LO): Account-level grants, rotating refresh tokens. Endpoint format: `https://api.atlassian.com/ex/jira/<cloudId>/rest/api/3/<resource>`. Recommended < 50 scopes per app.
- API tokens: Basic HTTP auth (email + token). **Not affected by new points-based rate limits** (important: only Forge/Connect/OAuth apps are in scope).
- Forge: `asApp()` (service account, permission tied to manifest scopes) and `asUser()` (acting user's permissions). Use Authorize API to verify user permissions before asApp calls.

**Rate Limits (enforced from March 2, 2026):**
Three independent systems operate simultaneously:
1. **Points-based quota** (per hour): Tier 1 (default) = 65,000 points/hr shared across all tenants. Tier 2 (by request) = per-tenant pool, Standard edition: 100,000 base + 10 points/user/hr. Each API call starts at 1 point base cost + additional points per object affected. Same system for REST and GraphQL.
2. **Burst rate limits** (per second): Prevent sudden spikes. Enforced since Aug 2025.
3. **Per-issue write limits**: Prevent rapid writes to the same issue.

**Key Capabilities for RaiSE:**
- Issue CRUD, bulk operations, JQL search
- Custom field management
- Workflow transition execution
- Sprint and board management
- Webhook registration for real-time events
- Issue linking, comments, worklogs

**Gotchas:**
- v3 uses ADF for description/comment bodies — must serialize/deserialize ADF
- JQL has a 10,000 result hard limit for search
- Bulk operations have per-request limits (e.g., 50 issues for backlog moves)
- Points-based rate limits are new (Mar 2, 2026) — monitor for impact

**Documentation Quality:** Very Good. Comprehensive OpenAPI specs, interactive explorer, changelog, migration guides.

**Evidence Level:** Very High (primary sources: official docs, changelog, community announcements).

---

### Confluence

**API Versions:**
- **REST API v2** (`/wiki/api/v2/`): Current recommended. Cursor-based pagination. Discrete endpoints per content type (pages, blogposts, spaces, labels, comments, attachments). Up to 30x faster bulk retrieval vs v1.
- **REST API v1** (`/wiki/rest/api/`): Legacy. Convert content body v1 API deprecated, extended to Aug 5, 2026. Still functional but migration to v2 recommended.
- **CQL** (Confluence Query Language): Used in search endpoints. Known issue: does not index spaces with unusual mixed-case keys (e.g., "rAIse") — per PAT-E-593.

**Authentication:** Same as Jira (OAuth 2.0 3LO, API token, Forge asApp/asUser).

**Rate Limits:** Same points-based system as Jira, enforced from March 2, 2026.

**Key Capabilities for RaiSE:**
- Page CRUD with storage format (HTML-based) or ADF
- Space management
- Content properties (key-value metadata on pages — useful for agent state persistence)
- Label management
- Attachment upload/download
- Comment threading
- CQL search across spaces

**Gotchas:**
- v2 API still expanding endpoint coverage — some v1 operations may not have v2 equivalents yet
- CQL search indexing issues with non-standard space keys (PAT-E-593)
- Storage format vs. ADF: different content formats depending on API version used
- Content properties: useful for state persistence but limited visibility in UI

**Documentation Quality:** Good. v2 docs well-structured with OpenAPI specs. v1 docs still available but clearly being sunset.

**Evidence Level:** Very High (primary: official docs; confirmed by prior research RAISE-273).

---

### Bitbucket Cloud

**API Type:** REST API v2 (`/2.0/`)

**Authentication (in transition, 2025-2026):**
- **API tokens**: Replacing app passwords. Basic HTTP auth (email + token). Rate limits applied since Nov 22, 2025.
- **OAuth 2.0**: Three RFC-6749 grant flows supported + custom JWT-to-access-token flow.
- **Access tokens**: Scoped to repository, project, or workspace.
- **OAuth 1.0**: Deprecated. Ceases working after March 14, 2026.
- **App passwords**: No new creation allowed. Existing ones still work.
- **Enforcement date**: May 4, 2026 — all OAuth/token changes enforced.

**Key Capabilities for RaiSE:**
- Repository CRUD and management
- Pull request operations (create, review, merge, comments)
- Branch management and branch restrictions
- Pipeline operations (trigger, monitor, artifacts)
- Webhook management
- Code search
- Commit and diff operations

**Rate Limits:** Per-token rate limits implemented Nov 2025. Specific values not publicly documented in detail — appears to be simpler than Jira/Confluence points system.

**Gotchas:**
- Authentication landscape is actively changing — plan for OAuth 2.0 only by May 2026
- Not part of Jira/Confluence points-based system (separate rate limiting)
- Forge support for Bitbucket is less mature than for Jira/Confluence

**Documentation Quality:** Good. OpenAPI specs available. Changelog tracks changes.

**Evidence Level:** High (primary: official docs, changelog announcements).

---

### Compass

**API Type:** GraphQL via `@atlassian/forge-graphql` toolkit from Forge apps. Also has a REST API v2.

**Authentication:** Forge app auth only for GraphQL toolkit. OAuth 2.0 (3LO) for REST API.

**Key Capabilities for RaiSE:**
- Component catalog management (create, update, delete components)
- Scorecard management for software health
- Event and metric data providers
- Dependency mapping between components
- Integration with Jira for scorecard work items

**Recent Changes:**
- `createComponentScorecardJiraIssue` → `createComponentScorecardWorkItem` (deprecated Oct 1, 2025)
- GraphQL toolkit simplifies common Compass operations from Forge

**Rate Limits:** Standard Forge invocation limits apply.

**Gotchas:**
- Forge-first integration model — external integrations need Forge as the bridge
- GraphQL API requires understanding Compass's data model (components, scorecards, metrics, events)
- Each complex query limited to 100 conditions

**Documentation Quality:** Good. Dedicated developer docs section with API explorer, tutorials, changelog.

**Evidence Level:** High (primary: official developer docs).

---

### Teamwork Graph (formerly Atlas / Teams)

**API Type:** Two-layer query: Cypher queries (graph traversal language) wrapped in GraphQL.

**Authentication:** Forge EAP only. Must be in selected EAP program.

**Status:** **EAP — Early Access Program. NOT production-ready.**

**Key Capabilities (theoretical):**
- Unified data layer connecting Jira, Confluence, and external tools (Google Drive, Slack, GitHub)
- Object types representing work items, pages, files, messages, PRs across tools
- Relationship traversal between objects
- Goal and project tracking across organization
- Team and group management

**Gotchas:**
- **EAP only**: Unsupported, subject to change without notice. Must only be installed in test organizations.
- No SLA, no production guarantee
- Limited to Forge apps (no standalone API access)

**Documentation Quality:** Adequate. Developer docs exist but EAP status means incomplete coverage.

**Evidence Level:** High (primary: official EAP docs, Atlassian blog announcements from Team '25).

---

### Rovo

**API Type:** Forge modules (`rovo:agent`, `rovo:action`). Not a traditional REST/GraphQL API — it is a platform capability within Forge.

**Authentication:** Operates with the invoking user's permissions (not the app creator's). Forge app auth for action execution.

**Key Capabilities for RaiSE:**
- **Rovo Agent module**: Configurable AI agent with custom prompt, conversation starters, and actions. Native chat UI in Jira and Confluence (top nav button, `/ai` command in editor).
- **Rovo Action module**: Custom actions implemented as Forge functions. Typed inputs/outputs, can call external APIs via fetch(). Max 5MB data per action.
- **Forge Bridge Rovo API**: Programmatically open Rovo chat sidebar, initiate conversations with specific agents, pre-fill prompts.
- **Forge LLMs API** (EAP): Atlassian-hosted Claude models (Haiku/Sonnet/Opus) with streaming support. Use with caution — EAP, no SLA.
- **Forge Realtime**: Push-based streaming for long-running LLM responses.
- **Prompt from file**: `prompt: resource:key;path/to/file.txt` (since CLI v10.6.0).
- **Multiple agents per app**: Supported via `rovo:agent` array in manifest.

**Licensing:** Included in all paid Atlassian plans since April 2025. No free tier.

**Gotchas:**
- **No memory between conversations**: State lost between user queries. Must use Forge Storage or content properties for persistence (RAISE-273 R1 finding).
- Forge LLMs API is EAP — do not depend on it for production. Use external LLM via fetch() instead.
- 5MB data limit per action invocation.
- Agent operates with user's permissions — cannot access resources the user cannot see.

**Documentation Quality:** Good. Tutorials (Q&A agent, Jira analyst, hello world), module reference, bridge API docs.

**Evidence Level:** Very High (primary: official docs, tutorials; confirmed by prior research RAISE-273).

---

### Forge Platform

**API Type:** Platform runtime APIs (not REST — internal Forge SDK calls).

**Components:**
- **Storage — Key-Value Store (KVS)**: Simple key-value pairs. 240KB max per value. 1000 RPS. 20 entities. Scoped per installation. Transactions supported.
- **Storage — Custom Entity Store**: Structured data with indexes and queries. 100 conditions per complex query. Scoped per installation.
- **Storage — Secret Store**: Encrypted key-value for sensitive data (API keys, tokens).
- **Resolver**: Backend function handler for UI Kit and Custom UI apps. Optional but needed for server-side logic.
- **Custom UI**: React-based, runs in iframe. Full HTML/CSS/JS control. Isolated environment.
- **UI Kit**: React primitives that render natively within Atlassian apps. Uses same platform components as internal teams. UI Kit 2 is current version.
- **Forge Bridge**: Client-side API for communication between Custom UI/UI Kit and Forge backend. Includes product API bridges (`requestJira`, `requestConfluence`).
- **Realtime**: Push-based event streaming for long-running operations.
- **External Fetch**: HTTPS-only calls to external APIs. All domains must be pre-declared in manifest.yml.

**Runtime Limits:**
- Sync function timeout: 25 seconds (hard limit)
- Async function timeout: 900 seconds (15 minutes), configurable via `timeoutSeconds`
- Memory: 512MB default, 1GB max (configurable in manifest)
- Response payload: 5MB max (frontend)
- Environments: 3 (development, staging, production) with separate storage

**Pricing (effective Jan 1, 2026):** Consumption-based. Previous quotas on FaaS invocations, runtime, KVS storage capacity, and file capacity removed. Generous free allowance, pay for excess.

**CI/CD:** Bitbucket Pipelines reference config available. Uses `FORGE_EMAIL` and `FORGE_API_TOKEN` environment variables.

**Distribution:** No private Marketplace listings for Forge apps. Use distribution links for direct sharing. From Sep 17, 2025, only Forge apps can be listed on Marketplace.

**Evidence Level:** Very High (primary: official docs, pricing blog, platform limits docs).

---

### Automation for Jira

**API Type:** **No public API for rule management.** Automation is a rule engine configured through the Jira UI or imported/exported as JSON. Rules consist of triggers, conditions, and actions.

**Key Capabilities:**
- Triggers: Issue created, updated, transitioned, scheduled, incoming webhook, manual
- Conditions: JQL, field-based, user-based
- Actions: Edit issue, create issue, transition, send notification, create Confluence page, send web request, set entity property
- Smart values: Templating syntax for accessing issue data (`{{issue.summary}}`, `{{issue.assignee.displayName}}`)
- Web request action: Can call external REST APIs (outbound)
- Incoming webhook trigger: Can receive external events (inbound)

**Programmatic Access:** Limited. Entity properties can be set via REST API (`/rest/api/3/issue/{id}/properties/{key}`) and read by automation rules. Automation rules themselves cannot be created/modified via API.

**Gotchas:**
- No CRUD API for automation rules — UI-only configuration
- Smart values have a learning curve
- Web request action is the main integration point for external systems
- Rule execution logs available in UI but not via API

**Documentation Quality:** Limited from developer perspective. Good end-user docs on triggers, conditions, actions, smart values.

**Evidence Level:** High (primary: official support docs; secondary: community patterns).

---

### Atlassian Admin (Organization Management)

**API Type:** REST APIs — multiple sub-APIs:
- **Organizations REST API**: Org settings, users, groups
- **User Management REST API**: Account management, profile operations
- **User Provisioning REST API**: SCIM-based provisioning
- **Classification REST API**: Data classification
- **Admin Control REST API**: Authentication policies, compliance, access management
- **API Access REST API**: Token management

**Authentication:** Organization admin OAuth 2.0. SCIM API keys (with new 1-year default expiry).

**Key Changes (2025-2026):**
- New Directory, Users, and Groups REST APIs superseding v1 APIs
- **v1 APIs sunset: June 30, 2026** — migration required
- New user invitation API (available to all paid subscriptions)
- SCIM API keys: existing keys assigned expiry between May 2026 and May 2027
- API tokens: default 1-year expiry from creation. Guard admins can configure 1-365 day expiry.

**Gotchas:**
- Multiple sub-APIs with different base URLs and auth requirements
- v1 → v2 migration deadline June 2026
- Org-level auth differs from product-level auth

**Documentation Quality:** Good. Clear migration guides, changelog, dedicated admin API section.

**Evidence Level:** High (primary: official docs, changelog, community announcements).

---

### Guard (Access)

**API Type:** Subset of Admin REST APIs focused on security policies.

**Capabilities:**
- Authentication policy management (SSO, 2FA requirements)
- Data security policies (content access rules for Confluence and Jira)
- Mobile app policies (auto-created for Guard Standard + verified domain)
- Audit log management (including new event exclusion toggles for third-party app activity)
- API token expiry enforcement
- Data export/download controls

**Tiers:**
- Guard Standard: Authentication policies, mobile policies, audit logs
- Guard Premium: Data security policies, data classification, advanced controls

**Gotchas:**
- Guard features gate access to certain admin APIs
- Data security policy rules may affect Forge app content access
- Audit log changes (Nov 2025): third-party API request logs require explicit opt-in

**Documentation Quality:** Adequate. Support-focused docs more than developer-focused.

**Evidence Level:** Medium (primary: support docs, cloud changelog announcements).

---

### Analytics

**API Type:** **No public REST API.** Analytics is a product feature, not an API surface.

**Availability:** Enterprise plan only (Atlassian Analytics).

**What Exists:**
- Built-in dashboards for Jira and Confluence usage
- Active user charts for Atlassian Intelligence and Rovo (filterable by date range)
- Audit log APIs (under Admin) provide some analytics-adjacent data
- JQL and CQL can be used to build custom reports programmatically
- Third-party analytics integration toggle (admin setting, default enabled)

**Gotchas:**
- No API to extract analytics data programmatically
- Enterprise plan requirement limits accessibility
- For custom reporting, build from JQL/CQL queries + issue/page data

**Documentation Quality:** N/A for developer API (product feature docs only).

**Evidence Level:** Medium (primary: cloud changelog, support docs).

---

## Platform-Wide Authentication Summary

| Method | Scope | Use Case | Status |
|--------|-------|----------|--------|
| **Forge asApp** | App service account | Server-to-server, background jobs | GA, recommended for Forge apps |
| **Forge asUser** | Acting user context | User-initiated actions | GA, recommended for Forge apps |
| **OAuth 2.0 (3LO)** | User account grant | External integrations, 3rd party apps | GA, recommended for non-Forge |
| **API token** | User personal token | Scripts, CLI tools, basic integrations | GA, but 1-year expiry default. **Not subject to points-based rate limits** |
| **SCIM** | Org-level provisioning | User/group sync from IdP | GA, keys now expire |
| **Connect (JWT)** | App-to-Atlassian | Legacy Connect apps | **End of support Dec 2026** |
| **OAuth 1.0** | Legacy | Bitbucket legacy | **Dead after Mar 14, 2026** |
| **App passwords** | Bitbucket legacy | Scripts | **No new creation allowed** |

## Platform Timeline (Critical Dates)

| Date | Event | Impact |
|------|-------|--------|
| Apr 2025 | Rovo included in all paid plans | Rovo available at no extra cost |
| Sep 17, 2025 | Only Forge apps on Marketplace | Connect apps can no longer be newly listed |
| Nov 22, 2025 | Bitbucket API token rate limits | Rate limiting for BB token-based auth |
| Jan 1, 2026 | Forge consumption-based pricing | Pay-per-use model, free tier generous |
| Mar 2, 2026 | Points-based rate limits enforcement begins | Phased rollout for Jira/Confluence APIs |
| **Mar 14, 2026** | **OAuth 1.0 dead for Bitbucket** | Must use OAuth 2.0 |
| **Mar 30, 2026** | **Connect apps can no longer push updates** | Must migrate to Forge |
| **May 4, 2026** | **Bitbucket OAuth/token enforcement** | Auth migration complete |
| Jun 30, 2026 | Admin v1 APIs sunset | Migrate to new Directory/Users/Groups APIs |
| Aug 5, 2026 | Confluence v1 convert body API deprecated | Use v2 equivalents |
| **Dec 2026** | **Connect end of support** | "Use at own risk" — no updates, no security patches |

## Evidence Catalog

| # | Source | Type | Evidence Level | Key Finding |
|---|--------|------|---------------|-------------|
| E1 | [Jira Cloud REST API v3 Introduction](https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/) | Primary | Very High | Current recommended API version, ADF for rich text |
| E2 | [Rate Limiting - Jira Cloud](https://developer.atlassian.com/cloud/jira/platform/rate-limiting/) | Primary | Very High | Three-tier rate limiting: points-based, burst, per-issue write |
| E3 | [Evolving API Rate Limits Blog](https://www.atlassian.com/blog/platform/evolving-api-rate-limits) | Primary | Very High | Points-based model details: Tier 1 = 65K/hr global, Tier 2 = per-tenant |
| E4 | [Jira Scopes for OAuth 2.0 and Forge](https://developer.atlassian.com/cloud/jira/platform/scopes-for-oauth-2-3LO-and-forge-apps/) | Primary | Very High | Scope model, < 50 scopes recommended |
| E5 | [Confluence REST API v2](https://developer.atlassian.com/cloud/confluence/rest/v2/intro/) | Primary | Very High | Cursor-based pagination, discrete content type endpoints |
| E6 | [Confluence Cloud Changelog](https://developer.atlassian.com/cloud/confluence/changelog/) | Primary | Very High | v1 deprecation timeline, v2 expansion |
| E7 | [Bitbucket Cloud REST API](https://developer.atlassian.com/cloud/bitbucket/rest/intro/) | Primary | Very High | v2 API structure, authentication methods |
| E8 | [Bitbucket Auth Deprecation Notice](https://community.atlassian.com/forums/Bitbucket-articles/Deprecation-notice-Bitbucket-Cloud-shifts-to-API-tokens-from-app/ba-p/3040975) | Primary | High | App passwords deprecated, API tokens as replacement |
| E9 | [Compass GraphQL API Toolkit](https://developer.atlassian.com/cloud/compass/integrations/graphql-api-toolkit/) | Primary | Very High | Forge GraphQL integration for component catalog |
| E10 | [Compass REST API v2](https://developer.atlassian.com/cloud/compass/rest/v2/intro/) | Primary | High | REST alternative to GraphQL for Compass |
| E11 | [Teamwork Graph API (EAP)](https://developer.atlassian.com/platform/teamwork-graph/call-the-teamwork-graph-api/) | Primary | High | Cypher + GraphQL, EAP only, test orgs only |
| E12 | [Teamwork Graph Overview](https://www.atlassian.com/platform/teamwork-graph) | Primary | High | Unified data layer vision, cross-product relationships |
| E13 | [Rovo Agent Module](https://developer.atlassian.com/platform/forge/manifest-reference/modules/rovo-agent/) | Primary | Very High | Agent definition, prompt from file, conversation starters |
| E14 | [Rovo Action Module](https://developer.atlassian.com/platform/forge/manifest-reference/modules/rovo-action/) | Primary | Very High | Custom actions with typed I/O, 5MB data limit |
| E15 | [Forge Bridge Rovo API](https://developer.atlassian.com/platform/forge/apis-reference/ui-api-bridge/rovo/) | Primary | Very High | Programmatic chat opening, agent invocation |
| E16 | [Forge LLMs API](https://developer.atlassian.com/platform/forge/runtime-reference/forge-llms-api/) | Primary | Very High | EAP, Claude models, streaming support |
| E17 | [Forge Platform Introduction](https://developer.atlassian.com/platform/forge/introduction/the-forge-platform/) | Primary | Very High | Platform overview, hosted infrastructure |
| E18 | [Forge Platform Quotas and Limits](https://developer.atlassian.com/platform/forge/platform-quotas-and-limits/) | Primary | Very High | Consumption-based pricing, resource limits |
| E19 | [Forge KVS and Entity Store Limits](https://developer.atlassian.com/platform/forge/limits-kvs-ce/) | Primary | Very High | 240KB/value, 1000 RPS, 20 entities |
| E20 | [Forge Invocation Limits](https://developer.atlassian.com/platform/forge/limits-invocation/) | Primary | Very High | 25s sync, 900s async, 512MB-1GB memory |
| E21 | [Forge External Fetch API](https://developer.atlassian.com/platform/forge/runtime-reference/external-fetch-api/) | Primary | Very High | HTTPS only, pre-declared domains |
| E22 | [Forge Authorize API](https://developer.atlassian.com/platform/forge/runtime-reference/authorize-api/) | Primary | Very High | Permission verification for asApp calls |
| E23 | [Organizations REST API](https://developer.atlassian.com/cloud/admin/organization/rest/) | Primary | Very High | Org management, user/group operations |
| E24 | [User Management REST API](https://developer.atlassian.com/cloud/admin/user-management/rest/) | Primary | Very High | Account management, superseding v1 APIs |
| E25 | [Connect End of Support Blog](https://www.atlassian.com/blog/developer/announcing-connect-end-of-support-timeline-and-next-steps) | Primary | Very High | Timeline: Sep 2025 → Mar 2026 → Dec 2026 |
| E26 | [Forge Pricing Updates Blog](https://www.atlassian.com/blog/developer/updates-to-forge-pricing-effective-january-2026) | Primary | High | Consumption-based from Jan 2026 |
| E27 | [Jira Software Agile REST API](https://developer.atlassian.com/cloud/jira/software/rest/api-group-board/) | Primary | Very High | Board, sprint, backlog operations |
| E28 | [JSM Cloud REST API](https://developer.atlassian.com/cloud/jira/service-desk/rest/) | Primary | Very High | Service desk, queues, SLA endpoints |
| E29 | [Guard Overview](https://support.atlassian.com/security-and-access-policies/docs/understand-atlassian-guard/) | Primary | High | Security policies, authentication controls |
| E30 | [Community: 2026 Point-Based Rate Limits](https://community.developer.atlassian.com/t/2026-point-based-rate-limits/97828) | Secondary | High | Developer concerns, Atlassian responses on quota details |
| E31 | Prior research RAISE-273 (Feb 2026) | Internal | High | Forge integration viability, Rovo architecture, 24 sources |

## Implications for RaiSE

### Adapter Architecture

1. **Forge-first is mandatory.** Connect is dying (Dec 2026). All new RaiSE Atlassian integrations must be Forge apps. This aligns with our prior decision (RAISE-273).

2. **Three authentication contexts to support:**
   - `asApp` for background/system operations (webhooks, scheduled tasks)
   - `asUser` for user-initiated actions (respecting user permissions)
   - External API token for RaiSE backend → Atlassian calls (if needed outside Forge context)

3. **Adapter abstraction layer should model the points-based rate limit system.** At 65K points/hour (Tier 1), a multi-tenant app needs intelligent rate budgeting. Consider:
   - Per-operation point cost awareness in adapter layer
   - Batching strategies to reduce point consumption
   - Monitoring/alerting for quota usage
   - Planning for Tier 2 application if usage warrants it

### MVP Scope (Apr 16 deadline)

**P0 — Must have:**
- Jira adapter: Issue CRUD, JQL search, sprint operations, transitions (REST v3 + Agile API)
- Confluence adapter: Page CRUD, CQL search, content properties (REST v2)
- Rovo agent: Custom agent with governance prompt, actions calling RaiSE backend
- Forge storage: State persistence for agent conversations (workaround for no-memory limitation)

**P1 — Should have:**
- Bitbucket adapter: Repository and PR operations (REST v2)
- Webhook integration: Real-time event processing from Jira/Confluence

**P2 — Nice to have:**
- Compass integration: Component catalog sync
- JSM integration: Service request automation
- Admin API: User/group management

**P3 — Watch list:**
- Teamwork Graph: Monitor EAP progress. Strategically important for cross-product intelligence but too immature for production.
- Analytics API: None exists today. Build custom analytics from JQL/CQL data.

### Key Design Decisions Needed

1. **Rate limit strategy**: Global pool (65K/hr) vs. applying for Tier 2 per-tenant pool. This depends on expected multi-tenant usage patterns.
2. **ADF handling**: Jira v3 uses Atlassian Document Format. Need ADF serialization/deserialization in the adapter layer.
3. **Async pattern for LLM calls**: 25s sync timeout means all LLM operations must use async functions + Forge Realtime for streaming.
4. **State persistence strategy**: Forge KVS (240KB/value limit) vs. Confluence content properties for agent conversation state.
5. **External backend communication**: All domains must be pre-declared in manifest.yml. Plan the RaiSE backend URL structure accordingly.
