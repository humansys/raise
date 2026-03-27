---
research_id: R3-RAISE-760
title: RaiSE <> Atlassian Value Map
epic: RAISE-760
date: 2026-03-27
status: complete
confidence: High
---

# R3: RaiSE <> Atlassian Value Map

## Executive Summary

RaiSE produces 21+ distinct artifact types (knowledge graph nodes, session journals, patterns, governance docs, ADRs, skills, research reports, telemetry events, work lifecycle artifacts) that currently live as local files in a git repository. When these artifacts are stored and managed in Atlassian products, three transformative capabilities emerge that neither RaiSE nor Atlassian can deliver alone:

1. **AI-governed software delivery at organization scale** -- RaiSE's deterministic governance (knowledge graph + typed patterns) becomes visible, searchable, and actionable across teams via Confluence, Jira, and Rovo, rather than locked inside individual developer workstations.
2. **Zero-code governance customization** -- governance processes become editable Confluence pages that Rovo agents read natively. Adding a new code standard or testing policy = creating a page. No deploy, no code change.
3. **Closed-loop traceability** -- from business requirement (Jira epic) through architectural decision (Confluence ADR) to code implementation (Bitbucket PR) to learned pattern (RaiSE graph), with Rovo agents providing natural-language query over the full chain.

The MVP "aha moment" is a Rovo agent that answers "what are our code standards and does this PR comply?" by querying the RaiSE knowledge graph synced from Confluence governance pages -- demonstrating the governance-dev loop in under 30 seconds.

## Artifact Mapping Matrix

### RaiSE Artifact Types --> Atlassian Product Homes

| RaiSE Artifact | Current Home | Atlassian Home | Product | Value Gained |
|---|---|---|---|---|
| **Knowledge graph nodes** (21 types: pattern, decision, guardrail, module, component, etc.) | Local JSON graph + rai-server PostgreSQL | Forge Custom Entity Store (structured data) + rai-server (relational queries) | Forge Platform | Multi-tenant persistence, per-installation isolation, no self-hosted DB for basic queries |
| **Knowledge graph edges** (11 types: governed_by, implements, depends_on, etc.) | Local JSON + rai-server | Forge Custom Entity Store | Forge Platform | Cross-entity relationship queries within Forge |
| **Session state/journal** | `.raise/rai/sessions/` JSONL files | Forge KVS (active session) + Confluence page (closed session archive) | Forge + Confluence | Team visibility into AI agent sessions; audit trail; searchable history |
| **Patterns** (learned engineering patterns) | `.raise/rai/memory/patterns.jsonl` | Confluence pages (human-readable) + Forge Entity Store (machine-queryable) | Confluence + Forge | Team-wide pattern sharing; non-developers can read/contribute patterns; Rovo can surface relevant patterns in context |
| **Governance docs** (code-standards, testing-policy, guardrails) | `.raise/governance/*.md` | Confluence pages in a Governance space | Confluence | Version history, comments, approval workflows, CQL search, Rovo reads natively, non-dev stakeholders can review/edit |
| **ADRs** (Architecture Decision Records) | `.raise/templates/architecture/adr.md` + work/epics/ | Confluence pages with structured template | Confluence | Searchable decision history, linking to Jira stories that implement them, approval workflows |
| **Epic scope/design/plan/retro** | `work/epics/{epic-id}/` directory tree | Confluence pages (scope, design, retro) + Jira epic issue (tracking) | Confluence + Jira | Project managers see progress without git access; retros become org-level learning assets |
| **Story scope/design/plan** | `.raise/artifacts/*.yaml` | Jira issue fields (scope) + Confluence child page (design) | Jira + Confluence | Full story lifecycle visible in standard PM tools; no context switching |
| **Skills** (prompt templates for AI agents) | `.raise/skills/{name}/` | Confluence pages (skill content) + Jira labels (skill metadata) | Confluence | Zero-code skill authoring; governance team edits skills as pages; Rovo reads natively (confirmed in RAISE-273) |
| **Research reports** | `work/research/` or `work/epics/{id}/research/` | Confluence pages with research template | Confluence | Searchable knowledge base; evidence catalogs become organizational memory; cross-team reuse |
| **Telemetry/metrics** | `.raise/telemetry/events.jsonl` (local, gitignored) | Forge Custom Entity Store (events) + Compass metrics (DORA) + Jira dashboards (summary) | Forge + Compass + Jira | Organizational visibility into AI-augmented dev metrics; Compass scorecards; exec dashboards |
| **Calibration data** (velocity, estimation accuracy) | `.raise/rai/memory/calibration.jsonl` | Forge Entity Store + Jira sprint data | Forge + Jira | Cross-team velocity benchmarking; estimation accuracy tracking at org level |
| **Templates** (governance, architecture, tech design) | `.raise/templates/` | Confluence templates | Confluence | Standard template library; Rovo pre-fills from context; org-wide consistency |
| **Module/architecture docs** | Generated by `rai discover` | Confluence pages + Compass component catalog | Confluence + Compass | Living architecture documentation; Compass health scorecards; dependency mapping visible in developer portal |
| **Glossary terms** | Graph nodes (type: term) | Confluence glossary | Confluence | Org-wide shared vocabulary; Rovo can define terms in context |
| **Release notes** | Graph nodes (type: release) | Confluence release pages + Jira versions | Confluence + Jira | Automated release documentation; traceability from version to stories to code |

### Dual-Write Architecture

The mapping follows the pattern established in RAISE-273 and E275:

```
Developer workstation (CLI, local graph)
       |
       | rai graph sync (push)
       v
rai-server (PostgreSQL, canonical store)
       |
       | Forge actions (pull/push)
       v
Atlassian Cloud (Confluence pages, Jira issues, Forge storage)
       |
       | Rovo agents (read)
       v
Team members (natural language queries over governance + code knowledge)
```

**Key architectural principle**: RaiSE backend remains the canonical knowledge layer (deterministic graph queries, validation logic). Atlassian products are the visibility and collaboration layer. This avoids duplicating logic in Forge (25s timeout constraint) while leveraging Atlassian's UI, search, and permission model.

## Business Cases

### BC1: Cross-Team Governance Visibility

**Description**: Engineering leadership currently has no visibility into whether teams follow governance standards (code quality, testing policy, architectural guidelines) unless they read individual repositories. With RaiSE governance artifacts published to Confluence and enforced via Rovo agents, compliance becomes visible at the organization level.

**Who benefits**: Engineering Directors, CTOs, Compliance Officers, Team Leads

**Prerequisites**: Governance docs in Confluence, RaiSE graph synced to rai-server, Rovo agent with governance actions

**Atlassian features leveraged**:
- Confluence: Page versioning (who changed the standard, when), CQL search, space-level permissions
- Jira: Custom fields for governance compliance status, JQL queries for compliance reporting
- Rovo: Natural-language queries ("which teams have updated their testing policy this quarter?")
- Compass: Health scorecards tracking governance adoption per component

**Evidence level**: High (Compass scorecards are GA, Rovo agents are GA, Confluence templates are proven)

### BC2: AI-Augmented Project Management

**Description**: RaiSE's work lifecycle (epic -> story -> task -> pattern) generates structured data that, when synced to Jira, enables AI-powered project management. Rovo agents can answer "what's blocking this epic?", "what patterns did we learn from the last 3 sprints?", "which stories have design docs but no implementation plan?".

**Who benefits**: Project Managers, Scrum Masters, Engineering Managers

**Prerequisites**: Epic/story lifecycle data synced to Jira, patterns synced to Confluence, Rovo agent with PM actions

**Atlassian features leveraged**:
- Jira: Issue types, links, sprints, JQL for structured queries
- Confluence: Design docs, retros as searchable pages
- Rovo: Context-aware queries spanning Jira issues and Confluence pages
- Jira Automation: Rules triggered by RaiSE lifecycle events (e.g., auto-create retro page when story transitions to "Done")

**Evidence level**: High (Jira API is GA, Rovo can query Jira+Confluence, Automation webhooks proven)

### BC3: Developer Onboarding Acceleration

**Description**: New developers joining a team currently need to read scattered markdown files, understand implicit conventions, and learn from oral tradition. With RaiSE's knowledge graph (architecture, components, patterns, glossary, decisions) published to Confluence and queryable via Rovo, onboarding becomes self-service.

**Who benefits**: New hires, team transfers, contractors, open-source contributors

**Prerequisites**: Knowledge graph synced to Confluence pages, Rovo agent with graph query actions

**Atlassian features leveraged**:
- Confluence: Architecture docs, glossary, ADRs as structured pages
- Compass: Component catalog with ownership, dependencies, health status
- Rovo: "How does the payment module work?", "What was the rationale for choosing PostgreSQL?", "Show me the testing patterns for this project"

**Evidence level**: High (Rovo search across products is GA; Atlassian reports early adopters save 1-2 hrs/week from AI-surfaced context -- Deviniti 2026 statistics)

### BC4: Automated Compliance and Audit Trail

**Description**: For regulated industries (fintech, healthtech, defense), RaiSE's deterministic governance validation + Atlassian's audit trail creates a compliance system where every code change traces back to a requirement, was validated against standards, and has a documented decision chain.

**Who benefits**: Compliance Officers, Auditors, Risk Managers, CISOs

**Prerequisites**: Full artifact chain in Atlassian (requirement -> ADR -> story -> PR -> pattern), RaiSE governance validation via graph

**Atlassian features leveraged**:
- Jira: Issue linking (requirement -> story -> subtask), custom fields for compliance metadata
- Confluence: Page history (who approved the standard), content properties (machine-readable metadata)
- Bitbucket: PR <-> Jira issue links, code review audit trail
- Guard: Data classification, audit log management
- Forge: SOC2 inheritance (30% of requirements covered by staying within Forge boundary -- per Atlassian docs)

**Evidence level**: Medium-High (Forge SOC2 claim from Atlassian blog; Jira traceability is well-established; full chain requires all integrations working)

### BC5: Knowledge-Driven Executive Reporting

**Description**: RaiSE telemetry (session events, skill usage, pattern accumulation, estimation accuracy) combined with Jira/Confluence data enables executive dashboards showing: team velocity trends, AI augmentation impact, governance compliance rates, knowledge growth over time.

**Who benefits**: CTOs, VP Engineering, Board-level reporting

**Prerequisites**: Telemetry synced to Forge Entity Store, Jira dashboards or Compass metrics configured

**Atlassian features leveraged**:
- Jira: Dashboards, gadgets, JQL-based reporting
- Compass: DORA metrics, custom scorecards
- Confluence: Executive summary pages auto-generated from data
- Rovo: Natural-language reporting queries

**Evidence level**: Medium (Compass DORA is GA; Jira dashboards are mature; custom metric ingestion via Forge is documented but not widely proven at scale)

### BC6: Organizational Learning Loop

**Description**: RaiSE patterns (learned engineering insights, PAT-E-*) are currently per-project. When published to Confluence and indexed in the knowledge graph, they become organizational assets. Teams can learn from other teams' mistakes without direct communication.

**Who benefits**: All engineering teams, especially in organizations with 5+ teams

**Prerequisites**: Pattern sync to Confluence + rai-server, cross-project graph queries

**Atlassian features leveraged**:
- Confluence: Pattern catalog pages, labels for categorization, CQL for discovery
- Rovo: "What patterns have other teams found for retry logic?", "Show me all architecture patterns from the last quarter"
- Jira: Link patterns to the stories that discovered them (traceability)

**Evidence level**: High (rai-server pattern API exists per E275; Confluence page creation is trivial; cross-project queries require multi-tenant rai-server)

## Competitive Analysis

### Existing Marketplace Landscape

The Atlassian Marketplace has **no direct competitor** to RaiSE's combined offering. Existing apps address fragments of the value proposition:

| Category | Existing Apps | What They Do | What RaiSE Adds |
|---|---|---|---|
| **DORA Metrics** | Software Development Optimization, Faros AI | Measure deployment frequency, lead time, MTTR, change failure rate | RaiSE adds AI-augmented development metrics (session productivity, pattern accumulation, governance compliance) that DORA doesn't measure |
| **Documentation** | Scroll Versions, Comala Document Control | Document lifecycle, version control, approval workflows | RaiSE generates documentation from code analysis (rai discover), keeps it synchronized, and makes it queryable via knowledge graph |
| **Architecture** | draw.io, Gliffy, LucidChart | Diagramming | RaiSE provides living architecture docs that update from code changes, with ADR traceability and impact analysis |
| **Compliance** | Various GRC apps | Checklist-based compliance tracking | RaiSE validates compliance deterministically via knowledge graph (not checklists), with AI agents that explain violations |
| **Knowledge Management** | Confluence itself, Guru, Notion | Static knowledge bases | RaiSE's knowledge is structured (typed graph), versioned, and actively maintained by AI agents during development |
| **AI/Rovo Agents** | Various Rovo-powered apps (emerging) | Task-specific AI assistance | RaiSE agents are governance-aware: they don't just help write code, they ensure code meets standards while being written |

### What RaiSE + Atlassian Does That Neither Can Alone

1. **Deterministic governance via AI agents**: Atlassian has Rovo (AI) but no governance engine. RaiSE has governance but no team-wide UI. Together: Rovo agents backed by RaiSE's deterministic knowledge graph enforce standards with explanations, not just rules.

2. **Living architecture documentation**: Confluence has pages. RaiSE has code analysis. Together: architecture docs that auto-update when code changes, with graph relationships linking components to standards to decisions.

3. **Neuro-symbolic knowledge management**: Atlassian has search (keyword + AI). RaiSE has a typed knowledge graph (nodes, edges, types). Together: structured knowledge queries ("what depends on the payment module and violates the new security standard?") that neither keyword search nor pure AI can answer reliably.

4. **AI session transparency**: No Atlassian product or Marketplace app tracks what AI agents actually did during development. RaiSE's session journals + telemetry provide this accountability layer, visible in Confluence.

### The "No-Brainer" Value Proposition

> **If your team already uses Jira + Confluence + Rovo, RaiSE turns your Atlassian stack into an AI-governed software development platform -- no new tools to learn, no new UIs to adopt. Your governance lives in Confluence pages. Your work tracking lives in Jira issues. Your AI agent (Rovo) knows both. RaiSE provides the intelligence layer that connects them with deterministic, traceable, auditable reasoning.**

The pitch is not "replace your tools" but "make your existing tools smarter":
- Confluence becomes a **living governance system**, not a documentation graveyard
- Jira becomes an **AI-augmented work tracker** that understands architecture, not just status
- Rovo becomes a **governance-aware copilot**, not just a chat assistant

## MVP Value Slice

### The "Aha Moment"

A developer asks the Rovo agent: "Does this code follow our standards?" The agent:
1. Queries the RaiSE knowledge graph for applicable guardrails and code standards
2. Evaluates the code against those standards (via RaiSE backend)
3. Returns a structured answer with specific violations and the rationale from the governance docs
4. Links to the relevant Confluence page where the standard is defined

This takes <30 seconds and demonstrates the full governance-dev loop.

### Day-1 Features (Forge MVP, Apr 16 deadline)

| Feature | Atlassian Products | RaiSE Backend | User Story |
|---|---|---|---|
| **Rai Governance Agent** | Rovo agent module | Graph query API | "As a developer, I can ask the Rovo agent about our code standards and get authoritative answers from the knowledge graph" |
| **Governance Sync** | Confluence pages -> Forge action | Graph sync API | "As a governance lead, I edit code standards in Confluence and they're automatically indexed in the RaiSE knowledge graph" |
| **Pattern Viewer** | Confluence pages (read-only display) | Pattern API | "As a team lead, I can browse engineering patterns learned by AI agents across our projects in Confluence" |
| **Session Summary** | Confluence page (auto-generated) | Session/event API | "As a team lead, I can see what the AI agent worked on in each session, with decisions and artifacts listed" |

### Phase 2 (Post-MVP, Q2 2026)

| Feature | Products | Value |
|---|---|---|
| **Rai Dev Agent** | Rovo + Jira + Bitbucket | AI coding assistant that knows your architecture, standards, and patterns |
| **Architecture Sync** | Compass + Confluence | Component catalog and architecture docs auto-updated from code discovery |
| **Compliance Dashboard** | Jira dashboard + Forge | Cross-team governance compliance visibility for engineering leadership |
| **Sprint Intelligence** | Jira + Rovo | AI-powered sprint planning using calibration data and historical patterns |

### Phase 3 (H2 2026)

| Feature | Products | Value |
|---|---|---|
| **Teamwork Graph Integration** | Teamwork Graph (post-EAP) | Cross-product knowledge traversal (Jira issue -> Confluence doc -> Bitbucket PR -> RaiSE pattern) |
| **Multi-Tenant Graph** | rai-server + Forge | Organization-wide knowledge graph spanning all teams and projects |
| **Executive Analytics** | Compass + Jira + custom dashboards | Board-level reporting on AI-augmented engineering metrics |
| **JSM Integration** | JSM + Rovo | Incident response informed by architecture knowledge and pattern history |

### MVP Architecture (from RAISE-273, validated by E275)

```
[Confluence Pages]                    [Jira Issues]
  (Governance docs,                    (Epics, Stories,
   Skills, Patterns)                    Sprints, Status)
        |                                    |
        | Forge Action: sync_governance      | Forge Action: sync_work
        v                                    v
[rai-server API]  <--- Forge fetch() ---> [Forge App]
  /graph/sync                               |
  /graph/query                         [Rovo Agent]
  /memory/patterns                      (Rai Governance)
  /agent/events                              |
        ^                                    v
        |                              [Developer Chat]
  [RaiSE CLI]                          "Does this follow
   rai graph build                      our standards?"
   rai graph sync
```

**Technical constraints addressed**:
- Forge 25s sync timeout: Governance sync uses async Forge functions (900s timeout)
- Rovo no-memory: Active session state persisted in Forge KVS (240KB/value)
- Rate limits: Graph queries go to rai-server (not Atlassian API), minimizing point consumption
- External fetch: rai-server domain pre-declared in manifest.yml

## Evidence Catalog

| ID | Source | Type | Evidence Level | Key Finding |
|---|---|---|---|---|
| E1 | R1-RAISE-760 (this epic) | Internal research | Very High | Atlassian API landscape: Forge-only path, points-based rate limits, Rovo GA |
| E2 | R2-RAISE-760 (this epic) | Internal research | Very High | Python ecosystem: adapter architecture sound, Rovo MCP for Forge |
| E3 | RAISE-273 research | Internal research | Very High | Three-layer architecture validated: Confluence (content) + RaiSE (knowledge) + Forge (UI) |
| E4 | E275 implementation | Internal (shipped code) | Very High | rai-server exists with graph/sync, graph/query, patterns, events APIs |
| E5 | raise-core graph models | Internal (code) | Very High | 21 node types, 11 edge types define the full artifact ontology |
| E6 | raise-cli adapter protocols | Internal (code) | Very High | Protocol-based architecture supports pluggable Atlassian adapters |
| E7 | .raise/governance/ artifacts | Internal (code) | Very High | Governance docs (code-standards, guardrails) are structured markdown |
| E8 | .raise/telemetry/ | Internal (code) | Very High | Local JSONL telemetry for skill lifecycle events |
| E9 | .raise/templates/ | Internal (code) | Very High | 10+ templates for governance, architecture, tech design |
| E10 | Atlassian Rovo features page | Official (atlassian.com) | Very High | Rovo: 5M+ MAUs, included in all paid plans, agent+action modules |
| E11 | Atlassian Compass features | Official (atlassian.com) | Very High | Software catalog, health scorecards, DORA metrics, Forge extensibility |
| E12 | Atlassian Forge platform docs | Official (developer.atlassian.com) | Very High | Custom Entity Store, KVS, async functions, SOC2 inheritance |
| E13 | Deviniti Atlassian AI statistics 2026 | Third-party research | High | Rovo 5M MAU, 1-2 hrs/week saved, 2.4M automations |
| E14 | DORA 2025 report | Google/DORA | Very High | AI amplifies but does not automatically improve delivery; organizational systems matter |
| E15 | Atlassian Marketplace survey | Direct observation | High | No direct competitor combining knowledge graph + governance + AI agents |
| E16 | Forge security blog | Official (atlassian.com) | High | Forge boundary covers 30% of SOC2 requirements |
| E17 | Forge pricing blog | Official (atlassian.com) | Very High | Consumption-based from Jan 2026, generous free tier |
| E18 | Rovo Dev announcement | Official (atlassian.com) | High | Rovo Dev targets 84% of developer time spent outside coding |
| E19 | Atlassian Forge transition timeline | Official (atlassian.com) | Very High | Connect end-of-support Dec 2026, Forge-only for new apps since Sep 2025 |

## Recommendations

### R1: Validate the "Aha Moment" First

The MVP should demonstrate exactly one loop end-to-end: governance doc in Confluence -> graph sync -> Rovo agent query -> developer gets answer. Everything else is secondary. This is the demo that makes the value proposition tangible.

### R2: Confluence is the Primary Atlassian Surface

Of all Atlassian products, Confluence provides the highest leverage for RaiSE:
- 7 of 15 artifact types map naturally to Confluence pages
- Rovo reads Confluence pages natively (no custom indexing needed)
- Non-technical stakeholders already use Confluence
- Skills-as-pages (RAISE-273 design) enables zero-code governance customization

Jira is the secondary surface (work tracking), and Compass is tertiary (component catalog, post-MVP).

### R3: Keep the Knowledge Graph in rai-server, Not Forge

Forge Custom Entity Store is useful for per-installation state (session data, cached queries) but should not replace rai-server as the canonical graph store:
- rai-server supports relational queries (PostgreSQL + GIN full-text search)
- Forge Entity Store has 100-condition query limits and 240KB value limits
- The graph currently holds 1,589 nodes + 33K edges for a single project -- this would quickly hit Forge limits at org scale
- rai-server is already built and validated (E275)

### R4: Leverage Rovo's Distribution, Not Its Reasoning

Rovo's value to RaiSE is distribution (5M+ MAU, native Jira/Confluence integration, zero-install for end users), not reasoning. The deterministic governance reasoning stays in RaiSE's knowledge graph. Rovo is the friendly face that makes it accessible.

### R5: Position Against the DORA Gap

The 2025 DORA report confirms: AI boosts individual output but not organizational delivery. This is RaiSE's exact thesis -- that organizational systems (governance, knowledge, patterns) determine whether AI improves outcomes. Position RaiSE+Atlassian as "the organizational system that makes AI development actually work" -- backed by DORA data.

### R6: Prioritize Regulated Industries

The compliance business case (BC4) has the highest willingness-to-pay. Fintech, healthtech, and defense organizations already use Atlassian and already pay premium for compliance tools. RaiSE's deterministic traceability (not probabilistic AI) is a regulatory differentiator.

### R7: Plan for Teamwork Graph (But Don't Block on It)

The Teamwork Graph (EAP) is strategically perfect for RaiSE -- it's literally a cross-product knowledge graph. When it reaches GA, RaiSE's graph could federate with it. But it's too immature for the Apr 16 deadline or even Q2 2026 plans. Monitor, don't depend.
