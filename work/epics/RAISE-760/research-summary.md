# RAISE-760: Research Summary & Strategic Recommendations

**Epic:** RAISE-760 — RaiSE Project Management Model
**Date:** 2026-03-27
**Status:** Complete
**Research period:** 2026-03-27 (single session, 4 parallel tracks)
**Total sources:** 85 (68 primary, 14 secondary, 3 internal)
**Overall confidence:** High

---

## 1. Why This Research

RaiSE is an Atlassian partner building an AI-augmented software engineering
framework. We have 3 weeks (deadline: Apr 16, 2026) to launch a Forge app MVP
on the Atlassian Marketplace. Before designing or building, we needed to answer
four foundational questions:

1. **What does Atlassian offer?** — Which products, APIs, and capabilities are
   available today, and what are their constraints?
2. **What tools exist?** — Can we leverage existing Python libraries and MCP
   servers instead of building from scratch?
3. **Where's the value?** — Which RaiSE artifacts gain the most from living in
   Atlassian, and what business cases does that enable?
4. **What can Forge actually do?** — What are the real constraints for building
   an app in 3 weeks?

---

## 2. Research Tracks

### R1: Atlassian API Landscape
[Full report →](https://humansys.atlassian.net/wiki/spaces/RaiSE1/pages/3143139330)

**Question:** What products and APIs are available today?

**Key findings:**
- **11 products mapped** across REST, GraphQL, and Forge-native APIs
- **Forge is the only path forward** — Connect reaches end of support Dec 2026;
  Marketplace is Forge-only since Sep 2025
- **Points-based rate limits** (65K pts/hr Tier 1) began enforcement Mar 2, 2026
- **Rovo is GA** (since Apr 2025, included in all paid plans, 5M+ MAU)
- **Teamwork Graph is EAP only** — strategically important but not production-ready
- **No public API** for Automation rule management or Analytics

**Sources:** 31 (24 primary from official Atlassian docs)
**Confidence:** High

### R2: Python Atlassian Ecosystem
[Full report →](https://humansys.atlassian.net/wiki/spaces/RaiSE1/pages/3143172097)

**Question:** What libraries and tools exist so we don't build from scratch?

**Key findings:**
- **No library warrants replacing our adapter architecture** — protocol-based,
  transport-agnostic design with ACLI for Jira and mcp-atlassian for Confluence
  is the right approach
- **mcp-atlassian** (sooperset, 4.7K stars) is the most active community project
  — already our Confluence transport
- **Atlassian's official Rovo MCP Server** (GA, OAuth 2.1) has the highest
  strategic value for the Forge app
- **atlassian-python-api** dependency in raise-pro may be vestigial — audit needed
- **Do not adopt** PyJira, pyatlassian, or atlassian-api-py

**Sources:** 22 (14 primary)
**Confidence:** High

### R3: RaiSE ↔ Atlassian Value Map
[Full report →](https://humansys.atlassian.net/wiki/spaces/RaiSE1/pages/3143237634)

**Question:** What gains value from living in Atlassian? What business cases emerge?

**Key findings:**
- **15 artifact types mapped** to Atlassian products — Confluence is dominant
  (7 of 15)
- **6 business cases identified:**
  1. Cross-team governance visibility
  2. AI-augmented project management
  3. Developer onboarding acceleration
  4. Automated compliance & audit trail (highest willingness-to-pay)
  5. Knowledge-driven executive reporting
  6. Organizational learning loop
- **No direct competitor** on Marketplace combines knowledge graph + deterministic
  governance + AI agents
- **The "aha moment":** Rovo agent answers "does this follow our standards?" in
  <30 seconds by querying the RaiSE knowledge graph
- **DORA 2025 confirms RaiSE's thesis:** AI boosts individual output but not
  organizational delivery — RaiSE solves the organizational layer

**Sources:** 19 (7 primary, rest internal + research)
**Confidence:** High

### R4: Forge Platform Deep-Dive
[Full report →](https://humansys.atlassian.net/wiki/spaces/RaiSE1/pages/3143270401)

**Question:** What can Forge actually do, and can we ship in 3 weeks?

**Key findings:**
- **3-week MVP is feasible** — Rovo agents as only UI, async queue consumers,
  KVS for state, fetch() to raise-server
- **No sandbox restrictions** — legacy sandbox fully retired Feb 2025; all npm
  packages and Node built-ins available
- **KVS value limit is 240 KiB** (not 128 KiB as older sources report)
- **Forge Bridge Rovo API graduated from EAP** — production-ready
- **Forge LLMs API remains EAP** — use external LLM via fetch()
- **Cold start ~1s** + ~1s Bridge invoke overhead
- **Distribution via link** — no Marketplace review needed for MVP

**Sources:** 35 (22 primary)
**Confidence:** High

---

## 3. Strategic Recommendations

### SR-1: Each Product Does What It Was Designed For
[Taxonomy Design →](https://humansys.atlassian.net/wiki/spaces/RaiSE1/pages/3143335938)

Jira tracks work. Confluence holds knowledge. Compass catalogs software. Forge
hosts the app. Rovo provides the AI face. Bitbucket manages code. Automation
connects them. Don't force one product to do another's job.

**Decision taken:** ADR-037 — Capabilities moved from Jira (where they were
misplaced as issue types) to Compass (software catalog with scorecards, DORA,
dependencies).

### SR-2: Validate the "Aha Moment" First
[Value Map →](https://humansys.atlassian.net/wiki/spaces/RaiSE1/pages/3143237634)

The MVP must demonstrate exactly one loop end-to-end: governance doc in
Confluence → graph sync → Rovo agent query → developer gets answer with
Confluence source link. Everything else is secondary.

**Decision taken:** RAISE-819 created as the Forge MVP construction epic,
consuming RAISE-760 designs as input.

### SR-3: Confluence is the Primary Atlassian Surface
[Confluence IA →](https://humansys.atlassian.net/wiki/spaces/RaiSE1/pages/3143598104)

7 of 15 artifact types map naturally to Confluence. Rovo reads Confluence
natively. Non-technical stakeholders already use it. Skills-as-pages enables
zero-code governance customization.

**Decision taken:** 11-section page tree designed. 10 templates specified.
Skills-as-pages model validated (from RAISE-273).

### SR-4: Keep the Knowledge Graph in raise-server, Not Forge
[Forge Deep-Dive →](https://humansys.atlassian.net/wiki/spaces/RaiSE1/pages/3143270401)

Forge Custom Entity Store has 100-condition query limit and 240KB values. The
graph already has 1,589 nodes + 33K edges for a single project — Forge limits
would break at org scale. raise-server (PostgreSQL + GIN) is already built and
validated.

**Decision taken:** ADR-035 — raise-server is the canonical knowledge store.
Forge KVS for conversation state only.

### SR-5: Rovo-Only UI for MVP
[Forge Deep-Dive →](https://humansys.atlassian.net/wiki/spaces/RaiSE1/pages/3143270401)

Zero Custom UI code. Rovo chat provides the entire UX. This eliminates ~40% of
estimated work and keeps the 3-week deadline achievable.

**Decision taken:** ADR-034 — Rovo-only UI. Custom UI panels deferred to Phase 2.

### SR-6: Position Against the DORA Gap
[Value Map →](https://humansys.atlassian.net/wiki/spaces/RaiSE1/pages/3143237634)

The 2025 DORA report confirms: AI boosts individual output but not
organizational delivery. RaiSE solves exactly this — the organizational systems
(governance, knowledge, patterns) that make AI development actually work.

**Implication:** Marketing and partner conversations should lead with DORA data.

### SR-7: Prioritize Regulated Industries
[Value Map →](https://humansys.atlassian.net/wiki/spaces/RaiSE1/pages/3143237634)

The compliance business case (BC4) has the highest willingness-to-pay. Fintech,
healthtech, and defense organizations already use Atlassian and already pay
premium for compliance tools. RaiSE's deterministic traceability (not
probabilistic AI) is a regulatory differentiator. Forge SOC2 inheritance
covers ~30% of requirements.

### SR-8: Unidirectional Sync by Design
[Workflow & Automation →](https://humansys.atlassian.net/wiki/spaces/RaiSE1/pages/3143598084)

RaiSE CLI → Jira → Automation cascades. No Jira → CLI sync needed because
developers ARE in the CLI. Jira is a projection of RaiSE state, not an input.
7 automation rules specified as the cross-product glue.

### SR-9: Plan for Teamwork Graph but Don't Block on It
[API Landscape →](https://humansys.atlassian.net/wiki/spaces/RaiSE1/pages/3143139330)

The Teamwork Graph (Cypher + GraphQL, EAP) is strategically perfect for
RaiSE — it's a cross-product knowledge graph. When it reaches GA, RaiSE's
graph could federate with it. But it's too immature for production. Monitor,
don't depend.

### SR-10: Forge-First is Mandatory
[API Landscape →](https://humansys.atlassian.net/wiki/spaces/RaiSE1/pages/3143139330)

Connect end-of-support: Dec 2026. Marketplace: Forge-only since Sep 2025.
There is no alternative. All new Atlassian integrations must be Forge apps.

**Decision taken:** ADR-036 — Async queue consumer pattern for Forge backend
calls (25s sync timeout workaround).

---

## 4. Decisions Made

| ADR | Decision | Status | Evidence |
|-----|----------|--------|----------|
| [ADR-034](../../dev/decisions/adr-034-rovo-only-ui-forge-mvp.md) | Rovo-only UI for Forge MVP | Proposed | R4 §3, R3 MVP Slice |
| [ADR-035](../../dev/decisions/adr-035-raise-server-canonical-store.md) | raise-server as canonical knowledge store | Proposed | R4 §2, E275 validation |
| [ADR-036](../../dev/decisions/adr-036-async-queue-consumer-pattern.md) | Async queue consumer for backend calls | Proposed | R4 §1, R1 rate limits |
| [ADR-037](../../dev/decisions/adr-037-capability-compass-initiative-jira.md) | Capabilities → Compass, Initiatives → Jira | Proposed | R1 Compass API, S760.2 Taxonomy |

---

## 5. What This Research Produced

| Output | Location |
|--------|----------|
| [Taxonomy Design](https://humansys.atlassian.net/wiki/spaces/RaiSE1/pages/3143335938) | Product Responsibility Matrix, issue types, components, labels, boards |
| [Workflow & Automation](https://humansys.atlassian.net/wiki/spaces/RaiSE1/pages/3143598084) | Lifecycle mapping, 7 automation rules, sync model |
| [Confluence IA](https://humansys.atlassian.net/wiki/spaces/RaiSE1/pages/3143598104) | 11-section page tree, 10 templates, skills-as-pages, 7 adapter gaps |
| [Compass Catalog](https://humansys.atlassian.net/wiki/spaces/RaiSE1/pages/3143172117) | 12 component definitions, 3 scorecards, dependency graph, DORA pipeline |
| [Bitbucket Integration](https://humansys.atlassian.net/wiki/spaces/RaiSE1/pages/3143663625) | Branch naming, smart commits, pipelines, GitHub equivalents |
| [Adapter Gap Analysis](https://humansys.atlassian.net/wiki/spaces/RaiSE1/pages/3144155138) | 30 gaps, 6 proposed implementation epics |
| [Reference Blueprint](https://humansys.atlassian.net/wiki/spaces/RaiSE1/pages/3143335958) | Consolidated partner guide |
| RAISE-819 | Forge MVP epic created in Jira with 7 stories and 3 ADRs |

---

## 6. Risks & Open Questions

### Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| 65K pts/hr rate limit insufficient | Low (single tenant MVP) | Medium | Monitor; apply for Tier 2 |
| Rovo action descriptions don't trigger correctly | Medium | Medium | Iterative prompt engineering |
| raise-server latency > 25s | Medium | Medium | Async queue consumer (ADR-036) |
| Compass requires plan upgrade | Medium | Medium | Design anyway; degrade to Jira Components if needed |
| Model too theoretical without validation | Medium | Medium | RAISE-819 runs in parallel |

### Open Questions

1. Does current Atlassian plan include Compass with scorecards?
2. Are historical Jira Component assignments preserved after Compass switch?
3. Should raise-server / raise-forge be Compass components?
4. Which Jira Automation plan tier is available?
5. Timeline for Teamwork Graph GA?

---

## 7. Next Steps

1. **Resolve open questions** (Compass plan, Automation tier) — prerequisite for implementation
2. **Begin RAISE-819** (Forge MVP) — 3-week sprint, deadline Apr 16
3. **Prioritize P1 adapter gaps** (13 gaps) — "Stabilize Backlog Adapter v2" and "Stabilize Docs Adapter v2" epics
4. **Dogfood the model** — apply Jira taxonomy to RAISE project itself
5. **Present blueprint to Fernando** — align on Forge MVP scope and architecture
