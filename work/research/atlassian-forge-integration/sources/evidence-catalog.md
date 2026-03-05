# Evidence Catalog: Atlassian Forge Integration for Governance Sidebar

**Research:** RAISE-273
**Date:** 2026-02-24
**Depth:** Standard
**Sources consulted:** 24

---

## Source Index

| # | Source | Type | Evidence Level | Key Finding |
|---|--------|------|---------------|-------------|
| S1 | [Forge Confluence Modules Reference](https://developer.atlassian.com/platform/forge/manifest-reference/modules/index-confluence/) | Primary (official docs) | Very High | Lists all available Confluence UI modules — NO sidebar panel module exists |
| S2 | [Community: Sidebar Panel Request](https://community.developer.atlassian.com/t/sidebar-panel-for-confluence-content-pages-like-native-comments-sidebar/98227) | Secondary (community) | Medium | Developer confirms no sidebar module; no Atlassian staff response |
| S3 | [Rovo Agent Module](https://developer.atlassian.com/platform/forge/manifest-reference/modules/rovo-agent/) | Primary (official docs) | Very High | Rovo Agents have native chat sidebar in Confluence top nav |
| S4 | [Rovo Action Module](https://developer.atlassian.com/platform/forge/manifest-reference/modules/rovo-action/) | Primary (official docs) | Very High | Custom actions with typed inputs, can call external APIs via remote endpoints |
| S5 | [Forge LLMs API](https://developer.atlassian.com/platform/forge/runtime-reference/forge-llms-api/) | Primary (official docs) | Very High | Atlassian-hosted Claude models (Haiku/Sonnet/Opus), streaming support. EAP status. |
| S6 | [Forge Realtime + LLM Streaming](https://developer.atlassian.com/platform/forge/llm-long-running-process-with-forge-realtime/) | Primary (official docs) | Very High | Push-based streaming architecture for long-running LLM responses |
| S7 | [Forge Invocation Limits](https://developer.atlassian.com/platform/forge/limits-invocation/) | Primary (official docs) | Very High | 25s default, 900s async; 512MB-1GB memory; 5MB response limit |
| S8 | [Forge External Fetch / Egress](https://developer.atlassian.com/platform/forge/runtime-reference/external-fetch-api/) | Primary (official docs) | Very High | External HTTPS calls allowed, must declare domains in manifest |
| S9 | [Forge Egress Permissions](https://developer.atlassian.com/platform/forge/runtime-egress-permissions/) | Primary (official docs) | Very High | All external domains must be pre-declared; HTTPS only |
| S10 | [Q&A Rovo Agent for Confluence Tutorial](https://developer.atlassian.com/platform/forge/build-a-q-and-a-rovo-agent-for-confluence/) | Primary (official tutorial) | High | Working example: agent reads Confluence pages, generates Q&A, stores as content properties |
| S11 | [External APIs + Rovo: What Actually Works](https://community.atlassian.com/forums/Atlassian-AI-Rovo-articles/External-APIs-Rovo-Agents-What-Actually-Works/ba-p/3096718) | Secondary (practitioner) | High | Universal fetch + API docs in prompt > hardcoded endpoints. No memory between interactions. |
| S12 | [Confluence REST API v2](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/) | Primary (official docs) | Very High | Full CRUD on pages via REST API, storage format for content |
| S13 | [Content Byline Item Module](https://developer.atlassian.com/platform/forge/manifest-reference/modules/confluence-content-byline-item/) | Primary (official docs) | Very High | Byline entry opens popup or modal — NOT a persistent sidebar |
| S14 | [Rovo Pricing/Licensing](https://support.atlassian.com/rovo/kb/understand-rovo-billing-and-managing-costs-in-atlassian-cloud/) | Primary (official docs) | Very High | Rovo included in all paid plans from April 2025. No free tier. |
| S15 | [Rovo Agent Permissions](https://support.atlassian.com/rovo/docs/rovo-agent-permissions-and-governance/) | Primary (official docs) | Very High | Agent operates with user's permissions, not creator's |
| S16 | [Forge App Distribution](https://developer.atlassian.com/platform/forge/distribute-your-apps/) | Primary (official docs) | Very High | No private Marketplace listings for Forge; use distribution links |
| S17 | [Rovo Writing/Reviewing Content](https://support.atlassian.com/rovo/docs/writing-and-reviewing-content-with-rovo-agents/) | Primary (official docs) | High | Rovo can edit pages, create content, invoked via /ai command in editor |
| S18 | [Forge Custom UI](https://developer.atlassian.com/platform/forge/custom-ui/) | Primary (official docs) | Very High | React-based Custom UI in iframes, full HTML/CSS/JS control |
| S19 | [Forge Storage KV Limits](https://developer.atlassian.com/platform/forge/limits-kvs-ce/) | Primary (official docs) | Very High | 240KB/value, 1000 RPS, 20 entities, scoped per installation |
| S20 | [Forge Environments](https://developer.atlassian.com/platform/forge/environments-and-versions/) | Primary (official docs) | Very High | 3 environments (dev/staging/prod), separate storage, auto-created |
| S21 | [Forge CI/CD Setup](https://developer.atlassian.com/platform/forge/set-up-cicd/) | Primary (official docs) | Very High | Bitbucket Pipelines reference config, FORGE_EMAIL/API_TOKEN for CI |
| S22 | [Prompt from File Resource](https://developer.atlassian.com/platform/forge/manifest-reference/modules/rovo-agent/) | Primary (official docs) | Very High | `prompt: resource:key;path/to/file.txt` supported since CLI v10.6.0 |
| S23 | [Rovo Agents Coming to Forge](https://community.developer.atlassian.com/t/rovo-agents-are-coming-to-forge/79626) | Secondary (community) | High | Confirmed rovo:agent array supports multiple agents per app |
| S24 | [Community: Custom Rovo Skill Resolution](https://community.developer.atlassian.com/t/custom-rovo-skill-is-not-available-in-studio-agents-or-rovo-chat/98639) | Secondary (community) | High | Custom skills work — require complete input/output definitions and outputContext |

---

## Evidence by Capability

### C1: Sidebar Panel in Confluence

| Claim | Evidence | Confidence | Sources |
|-------|----------|------------|---------|
| No native sidebar panel module exists in Forge | Module reference lists all available modules; sidebar is absent | HIGH | S1, S2 |
| Rovo Agents provide a native chat sidebar in top nav | Agents accessible via Chat button in top navigation | HIGH | S3, S17 |
| ContentBylineItem opens popup/modal, not persistent sidebar | Documentation states popup or modal viewport | HIGH | S13 |
| ContentAction opens modal dialog only | Documentation confirms modal only | HIGH | S1 |

**Synthesis:** Building a custom sidebar from scratch is NOT possible with current Forge modules. However, **Rovo Agents already provide a chat sidebar** accessible from Confluence's top navigation and the `/ai` command in the editor. This is the path of least resistance.

### C2: Chat Interface

| Claim | Evidence | Confidence | Sources |
|-------|----------|------------|---------|
| Rovo provides native conversational chat | Agent module includes conversation starters, natural language interaction | HIGH | S3, S10 |
| Custom UI supports React-based interfaces in iframes | Full HTML/CSS/JS via Custom UI module | HIGH | S18 |
| Forge LLMs API supports streaming responses | stream() method available, Realtime for push-based delivery | HIGH | S5, S6 |

**Synthesis:** Two paths — (a) Rovo Agent's built-in chat (fastest, most native), or (b) Custom UI with React chat component (more control, more effort). Rovo is clearly preferred for the use case.

### C3: Page Read/Write

| Claim | Evidence | Confidence | Sources |
|-------|----------|------------|---------|
| Forge apps can read page content via Confluence REST API v2 | requestConfluence available from @forge/bridge | HIGH | S12, S10 |
| Forge apps can write/update page content | PUT to /wiki/api/v2/pages/{id} with storage format | HIGH | S12 |
| Rovo agents can edit pages directly | "edit page" action appends content after confirmation | HIGH | S17 |
| Rovo agents can create new pages | "Publish new page" action available | HIGH | S17 |

**Synthesis:** Full CRUD on Confluence pages is well-supported. Both via direct API calls and via Rovo's built-in page actions.

### C4: Approval Workflows

| Claim | Evidence | Confidence | Sources |
|-------|----------|------------|---------|
| Confluence Cloud has basic content statuses (Draft, In Progress, Ready for Review) | Native feature, no API for custom statuses | MEDIUM | S12 |
| No native Forge module for approval workflows | No approval-specific module in Forge | HIGH | S1 |
| Marketplace apps (AURA, Workflows for Confluence) handle approvals | Multiple Forge-based approval apps exist | HIGH | (marketplace search) |
| Confluence Automation can trigger on status changes | Page status + automation rules | MEDIUM | (community) |

**Synthesis:** Approval workflows require either (a) leveraging native Confluence content statuses + automation, (b) using a Marketplace app, or (c) building custom workflow logic in Forge. For MVP, content statuses + page labels + Rovo agent guidance is sufficient.

### C5: External API Connectivity

| Claim | Evidence | Confidence | Sources |
|-------|----------|------------|---------|
| Forge can call external HTTPS APIs | fetch API with declared domains in manifest | HIGH | S8, S9 |
| All external domains must be pre-declared in manifest.yml | Strict egress control | HIGH | S9 |
| HTTP (non-HTTPS) is NOT supported | HTTPS only for external calls | HIGH | S8 |
| Rovo actions can use remote endpoints | rovo:action supports endpoint pointing to remote | HIGH | S4 |
| Universal fetch pattern works best for external APIs | Single fetch function + API docs in prompt | HIGH | S11 |

**Synthesis:** External API connectivity is fully supported but requires HTTPS and pre-declared domains. The architecture would be: Rovo Agent -> Rovo Action -> Forge Function -> fetch() -> RaiSE Backend API.

### C6: Runtime Constraints

| Claim | Evidence | Confidence | Sources |
|-------|----------|------------|---------|
| Default timeout: 25 seconds | Hard limit for synchronous functions | HIGH | S7 |
| Async/scheduled: up to 900 seconds (15 min) | Configurable via timeoutSeconds | HIGH | S7 |
| Memory: 512MB default, 1GB max | Configurable in manifest | HIGH | S7 |
| Response payload: 5MB max (frontend) | Hard limit | HIGH | S7 |
| Rovo action data: 5MB limit | Dependency size constraint | HIGH | S11 |
| No memory between Rovo interactions | State lost between queries | HIGH | S11 |

**Synthesis:** The 25s sync limit is the main constraint for LLM calls. Solution: use async functions + Forge Realtime for streaming, or leverage Rovo's built-in LLM (which handles this internally). The **no-memory-between-interactions** is a significant limitation for complex multi-turn governance workflows.

### C7: Licensing & Distribution

| Claim | Evidence | Confidence | Sources |
|-------|----------|------------|---------|
| Rovo included in all paid Atlassian plans from April 2025 | No additional cost | HIGH | S14 |
| No free tier for Rovo | Business email domain required | HIGH | S14 |
| Forge apps can't have private Marketplace listings | Must use distribution links for private sharing | HIGH | S16 |
| Forge consumption-based pricing from Jan 2026 | Pay for what you use, generous free allowance | MEDIUM | S7 |

**Synthesis:** Coppel already has Confluence Cloud (paid) = Rovo available at no extra cost. Our Forge app distribution via link (not Marketplace) for initial engagement.

---

## Contrary Evidence & Risks

| Risk | Evidence | Severity | Mitigation |
|------|----------|----------|------------|
| No persistent sidebar — Rovo chat is in top nav, not page-adjacent | S2, S3 | Medium | Rovo chat IS contextual to page when invoked via /ai in editor |
| No memory between Rovo interactions | S11 | High | Store state in Confluence content properties or Forge storage |
| Forge LLMs API is EAP (experimental) | S5 | Medium | Can use external LLM via fetch as fallback |
| 25s timeout for sync functions | S7 | Medium | Use async + Realtime pattern for long operations |
| 5MB data limit per action | S11 | Low | Governance documents are typically small |
| Significant iteration required for external API integration | S11 | Medium | Budget extra time for prompt engineering |
