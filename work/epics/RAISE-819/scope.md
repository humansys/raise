# RAISE-819: Forge MVP — Rovo Agents + raise-server Integration — Scope

**Jira:** RAISE-819
**Labels:** atlassian, forge, pro-launch, rovo
**Branch:** release/2.4.0 (stories branch from release/2.4.0)
**Depends on:** RAISE-760 (model design), E616 (license MVP)
**Design:** [design.md](design.md)
**Research:** `../RAISE-760/research/` (R1-R4, completed 2026-03-27)

## Objective

Build a Forge app MVP that makes RaiSE a "no-brainer" for teams already on
Atlassian. Two Rovo agents (Rai Governance, Rai Dev) query the RaiSE knowledge
graph, with Confluence as the governance surface and Jira as the work tracker.
Distribute via link to first customer by Apr 16, 2026.

## Value

- **For partner teams:** AI-governed software delivery without leaving Atlassian
- **For RaiSE:** first paying PRO customers via Marketplace/distribution
- **For Atlassian partnership:** reference implementation of Forge + Rovo + knowledge graph
- **Unlocks:** compliance business case (BC4), organizational learning (BC6), executive reporting (BC5)

## Stories

### S760.1: Forge App Scaffold & raise-server Connection (S)

Forge app created with `forge create`, manifest.yml with permissions, Node.js 22,
raise-server domain declared, Secret Store for API key, hello-world Rovo agent
that responds to greetings. Deployed to development environment.

**Dependencies:** None

### S760.2: Core Forge Actions — Read Context (S)

Implement 3 read actions: `read-page` (current Confluence page content),
`read-jira-context` (current issue + story context), `query-graph`
(query raise-server `/graph/query` endpoint). Actions return structured data
that agents can interpret.

**Dependencies:** S760.1

### S760.3: Governance Sync Action (M)

Implement `sync-governance` action: reads Confluence pages from a designated
Governance space/section, parses governance docs (code-standards, guardrails,
testing-policy), transforms to graph nodes, POSTs to raise-server `/graph/sync`.
Uses async queue consumer for operations that may exceed 25s.

**Dependencies:** S760.1

### S760.4: Rai Governance Agent — Prompt & Actions (M)

Full Rai Governance agent with production prompt, conversation starters,
and action suite: read-page, query-graph, sync-governance, validate-document.
The `validate-document` action queries applicable standards from the graph and
evaluates content against them. Demonstrates the "aha moment": ask about
standards, get authoritative answer with links to Confluence source pages.

**Dependencies:** S760.2, S760.3

### S760.5: Rai Dev Agent — Prompt & Actions (S)

Rai Dev agent with developer-focused prompt, conversation starters, and actions:
read-jira-context, query-graph, report-event. Helps developers understand
architecture, find applicable patterns, and check constraints for their current
work item.

**Dependencies:** S760.2

### S760.6: KVS State Persistence & Telemetry (S)

Implement Forge KVS-based conversation state persistence (memory workaround).
Add `report-event` action that POSTs telemetry to raise-server `/agent/events`.
Session state stored per user+context, cleaned up on configurable TTL.

**Dependencies:** S760.1

### S760.7: E2E Validation & Demo (M)

End-to-end test of full governance loop: governance doc in Confluence →
sync-governance → graph populated → Rai Governance agent answers "does this
follow our standards?" correctly. Demo script for first customer presentation.
Distribution link generated.

**Dependencies:** S760.4, S760.5, S760.6

## In Scope (MUST)

- Forge app with 2 Rovo agents (Governance + Dev)
- 6-8 Forge actions connecting to raise-server
- Governance sync: Confluence → raise-server graph
- Conversation state persistence via Forge KVS
- Distribution link (not Marketplace listing)
- Deployed and demoed on our own Atlassian instance

## In Scope (SHOULD)

- Telemetry via raise-server events API
- Error handling for raise-server unavailability
- Prompt iteration based on real governance docs

## Out of Scope

- Custom UI (Jira panels, Confluence macros) → Phase 2
- Marketplace listing and review process → post-MVP
- Compass integration → Phase 2
- Bitbucket adapter → Phase 2
- Teamwork Graph integration → Phase 3 (EAP)
- Multi-tenant rate limit strategy → post single-customer validation
- Scheduled sync triggers → post-MVP (manual sync first)
- Taxonomy redesign (issue types, workflows) → separate story post-MVP
- Confluence IA restructuring → separate story post-MVP

## Done Criteria

- [ ] Forge app deployed to development environment
- [ ] 2 Rovo agents accessible in Jira and Confluence chat
- [ ] Governance sync populates raise-server graph from Confluence pages
- [ ] "Aha moment" works: agent answers governance question with graph-backed evidence
- [ ] Rai Dev agent returns relevant architecture/pattern info for a Jira issue
- [ ] Conversation state persists across actions within a session
- [ ] Distribution link generated and shared with first customer
- [ ] Demo script documented and rehearsed

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| 65K pts/hr rate limit insufficient for demo workflows | Low (single tenant) | Medium | Monitor usage; apply for Tier 2 if needed |
| Rovo action descriptions don't trigger correctly | Medium | Medium | Iterative prompt engineering; test with real queries |
| raise-server latency > 25s on graph queries | Medium | Medium | All backend calls via async queue consumer pattern |

## Research Foundation

This design is grounded in 4 completed research tracks:

- **R1:** Atlassian API Landscape — 11 products mapped, Forge-only path confirmed
- **R2:** Python Ecosystem — adapter architecture sound, Rovo MCP strategic
- **R3:** Value Map — 6 business cases, "aha moment" defined, no Marketplace competitor
- **R4:** Forge Deep-Dive — 35 sources, MVP architecture validated, 3-week feasible
