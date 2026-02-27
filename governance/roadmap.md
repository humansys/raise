# Roadmap: RaiSE Framework

> **Status:** Active
> **Updated:** 2026-02-26 (SES-294)
> **Products:** rai-cli (Community), rai-server + rai-pro (Pro), Enterprise
> **Category:** AI Agentic Governance
> **Problem Brief:** `work/problem-briefs/ai-agentic-governance-2026-02-26.md`

---

## Vision

> When AI agents build your software, RaiSE ensures they follow your rules.

RaiSE is an AI Agentic Governance platform. It doesn't make AI agents more
capable — it makes them **confiable**. Governance-as-code with poka-yoke
enforcement, embedded in the developer workflow.

**Speed camera vs lane assist.** Others catch violations after the fact.
RaiSE keeps you in the lane while you drive.

---

## Product Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    ENTERPRISE                            │
│  SSO/SAML, SCIM, audit logging, RBAC, on-premise,      │
│  data residency, compliance certs, org-wide analytics   │
├─────────────────────────────────────────────────────────┤
│                    PRO (rai-server + rai-pro)            │
│  Shared memory, cross-repo visibility, governance       │
│  guardrails, pattern propagation, portfolio health,     │
│  platform integration (Jira, Confluence, Forge)         │
├─────────────────────────────────────────────────────────┤
│                    COMMUNITY (rai-cli + rai-core)        │
│  CLI, 20+ skills, local memory, knowledge graph,        │
│  multi-language discovery, governance scaffolding,       │
│  adapter protocol contracts (Apache 2.0)                │
└─────────────────────────────────────────────────────────┘
```

---

## Release Overview

| ID | Release | Product | Target | Status | Epics |
|----|---------|---------|--------|--------|-------|
| REL-2.0 | v2.0.0 Open Core | Core | 2026-02-15 | ✅ Released | E18 |
| REL-2.1 | v2.1.0 CLI Professional | Core | 2026-02-24 | ✅ Released | E247, E257, E275 |
| REL-P0.1 | Pro 0.1 Shared Memory | Pro | 2026-02-26 | ✅ Complete | E275 |
| **REL-MVP** | **Pro MVP Launch** | **Core + Pro** | **2026-03-15** | **🚀 In Progress** | **E-JIRA, E-SKILLS, E-GOV-FOUND** |
| REL-P1.1 | Pro 1.1 Governance Guardrails | Pro | 2026-Q2 | 📋 Planning | E-GOV-GUARDRAILS |
| REL-P1.2 | Pro 1.2 Portfolio Health | Pro | 2026-Q2 | 📋 Planning | E-PORT-HEALTH |
| REL-P2.0 | Pro 2.0 Pattern Propagation | Pro | 2026-Q3 | 📋 Planning | E-PATTERNS |
| REL-P2.1 | Pro 2.1 Org Intelligence | Pro | 2026-Q3 | 📋 Planning | E-ORG-INTEL |
| REL-P2.2 | Pro 2.2 Forge Integration | Pro | 2026-Q3/Q4 | 📋 Planning | E-FORGE |
| REL-3.0 | v3.0 Enterprise | Enterprise | 2026-Q4 | 📋 Planning | E-ENT |

### 🎯 MVP Launch: March 15, 2026 — Atlassian Webinar

**Audience:** Jira customers. **Demo:** RaiSE Pro with Jira + Confluence + Governance.

The MVP bundles three workstreams into one launch:

| Workstream | Epic | Status | What it delivers |
|-----------|------|--------|-----------------|
| Platform Integration | E-JIRA (RAISE-274) | 🚀 In Progress | Jira backlog sync, Confluence docs publishing |
| Skill Ecosystem | E-SKILLS (RAISE-242) | 🚀 In Progress | Skill builder, connectors for Jira/Confluence |
| Governance Foundation | E-GOV-FOUNDATION | 📋 Planning | Guardrails, scope hierarchy, compliance query |
| Shared Memory | E275 | ✅ Done | Graph sync, patterns, telemetry, query |

---

## COMMUNITY (rai-cli + rai-core)

### v2.0.0 — Open Core ✅ Released (2026-02-15)

Published to PyPI. First public release.

- Complete CLI with 20+ skills
- Local knowledge graph (JSON-based)
- Multi-language discovery (Python, TypeScript, PHP, C#, Dart)
- Memory system (patterns, calibration, sessions)
- Governance framework scaffolding
- BYOK inference (any AI agent)

### v2.1.0 — CLI Professional ✅ Released (2026-02-24)

- RAISE-247: CLI Ontology Restructuring ✅ (6 stories, 1.94x velocity)
- RAISE-257: Skill Excellence ✅ (4 stories, 3.4x velocity)
- RAISE-275: Shared Memory Backend ✅ (7 stories, rai-server package created)
- RAISE-249: Artifact Ontology & Contract Chain ✅
- Branch rename v2→dev, published to PyPI

### v2.2.0 — MVP Launch (Target: 2026-03-15)

**Coincides with REL-MVP (Atlassian webinar). Includes Core + Pro features.**

Core changes:
- E275 features exposed in CLI (graph sync commands)
- RAISE-242: Skill ecosystem (skill builder, Jira/Confluence connectors)
- Engineering health fixes (44 duplicate node warnings, Alembic env.py)

Pro features (rai-server + rai-pro):
- RAISE-274: Jira backlog integration (`rai backlog` commands)
- Confluence docs publishing (`rai docs publish`)
- Governance foundation (guardrails in graph, scope resolution, compliance query)
- Shared memory (already complete from v2.1/E275)

### v2.3.0 — Post-MVP Hardening (Target: 2026-Q2)

- RAISE-292: TDD Policy Reform (coverage as diagnostic, not gate)
- Adapter protocol refinements
- Community adapter documentation
- Provider system (context, output, scaffold providers)

---

## PRO (rai-server + rai-pro)

### Capability Stack

```
Layer 4: Organizational Learning    ← P2.1 (Q3)
Layer 3: Governance Intelligence    ← MVP (partial) + P1.1 (full guardrails)
Layer 2: Pattern Propagation        ← P2.0 (Q3, fast-follow)
Layer 1: Cross-Repo Visibility      ← MVP (partial, for governance)
Layer 0: Shared Memory              ← P0.1 ✅ DONE
     +  Platform Integration        ← MVP 🚀 (Jira + Confluence)
```

### Pro 0.1 — Shared Memory ✅ Complete (2026-02-26)

**Epic:** [RAISE-275](https://humansys.atlassian.net/browse/RAISE-275) — Shared Memory Backend

**What exists:**
- rai-server package (FastAPI + PostgreSQL 16 + Alembic)
- `POST /graph/sync` — Idempotent full graph upsert (nodes + edges)
- `GET /graph/query` — Full-text search with GIN indexing
- `POST/GET /agent/events` — Agent telemetry (append-only)
- `POST/GET /memory/patterns` — Shared pattern storage
- `GET /health` — Server health check
- Multi-tenancy (org_id), multi-repo (repo_id)
- Docker Compose deployment (PG 16 + server)
- API key authentication per org
- Validated: E2E with 1589 nodes + 33k edges from real graph

**Metrics:** 7 stories, 91 commits, 2950 tests across epic.

---

### MVP — Pro Launch 🎯 (Target: 2026-03-15, Atlassian Webinar)

**Epics:** E-JIRA (RAISE-274) + E-SKILLS (RAISE-242) + E-GOV-FOUNDATION + E275 ✅

**Audience:** Jira customers at Atlassian webinar. Demo must show Jira + Confluence
+ governance working together.

**Deliverables:**

**Platform Integration (E-JIRA, 🚀 in progress):**
1. `rai backlog` — Jira backlog commands (create, read, update, transition issues)
2. `rai docs publish` — Confluence docs publishing (governance docs → Confluence pages)
3. Jira → knowledge graph parser (issues flow into graph)

**Skill Ecosystem (E-SKILLS, 🚀 in progress):**
1. Skill builder tooling
2. Jira connector skill (backlog sync)
3. Confluence connector skill (docs publish)

**Governance Foundation (E-GOV-FOUNDATION):**
1. Guardrail nodes with enforcement level (MUST/SHOULD/CAN) and scope hierarchy
2. Scope resolution query — applicable guardrails for any repo/module
3. Cross-repo edge sync via `.raise/contracts.yaml` convention
4. Impact query — BFS traversal crossing repo boundaries

**Shared Memory (E275, ✅ complete):**
- Graph sync, patterns, telemetry, query — all operational

**New endpoints (governance):**
- `GET /governance/applicable?repo=X&module=Y` — Guardrails resolving scope chain
- `GET /visibility/impact?repo=X&node=Y&depth=N` — Cross-repo blast radius

**Research:** [Cross-Repo Visibility (L1)](work/research/cross-repo-visibility/),
[Governance Intelligence (L3)](work/research/governance-intelligence-multi-repo/)

**Demo scenario:** Rodo defines guardrails → syncs to server → tech lead designs
story in Jira → RaiSE agent shows applicable guardrails + cross-repo impact →
compliance check passes → docs published to Confluence automatically.

---

### Pro 1.1 — Governance Guardrails (Target: 2026-Q2, ~4 weeks after MVP)

**Epic:** E-GOV-GUARDRAILS — Poka-yoke in Skills + Waivers + Compliance

**Problem:** Guardrails exist in the graph but don't surface during developer
workflow. Tech leads still rely on memory to follow rules.

**Deliverables:**
1. Poka-yoke integration in 3 skills:
   - `/rai-story-design` — surfaces applicable guardrails + cross-repo impact
   - `/rai-story-implement` — checks MUST constraints, offers waiver for SHOULD
   - `/rai-story-close` — pre-merge compliance report
2. Waiver mechanism with expiration, traceability, and approval levels
3. Compliance check endpoint
4. Compliance report (per-repo and per-org)

**New endpoints:**
- `POST /governance/check` — Run compliance check for a repo
- `GET /governance/compliance` — Compliance report for org or repo
- `POST /governance/waiver` — Register a waiver
- `GET /governance/waivers` — List active/expired waivers

**Research:** [Governance Intelligence (L3)](work/research/governance-intelligence-multi-repo/)

**Estimated:** ~5-6 stories, ~4 weeks

**Kurigage validation:** Sofi designs API change → agent shows blast radius +
applicable guardrails. Arnulfo writes direct SQL → agent offers waiver or
refactor. Rodo sees compliance report: 🟢🟢🟡 across 3 repos.

---

### Pro 1.2 — Portfolio Health (Target: 2026-Q2, ~2 weeks after P1.1)

**Epic:** E-PORT-HEALTH — Health Scorecards for Business Visibility

**Problem:** Business owners ask "are we on track?" and get anecdotes.

**Deliverables:**
1. Health score composite (7 components, configurable weights)
2. Traffic light system (🟢🟡🔴) per repo
3. Health endpoint with trend (improving/stable/degrading)

**New endpoints:**
- `GET /analytics/health` — Health scores for org or repos
- `GET /analytics/health/{repo}/trend` — Score trend over time

**Schema:** `metric_snapshots` table for point-in-time scores.

**Research:** [Organizational Learning (L4)](work/research/organizational-learning/)

**Estimated:** ~2-3 stories, ~2 weeks

**Kurigage validation:** Jorge asks "¿cómo vamos?" → sees contabilidad 🟢 92,
erp 🟡 74, apis 🟢 95, with trend arrows.

---

### Pro 1.x — Full Governance Suite (Target: 2026-Q2 end)

**Cumulative:** MVP + P1.1 (Guardrails) + P1.2 (Health) = feature-complete governance.

**Checklist for full governance suite:**
- [ ] All governance endpoints functional and tested
- [ ] Poka-yoke integrated in 3 skills
- [ ] Compliance reporting operational
- [ ] Health scorecards operational
- [ ] Kurigage pilot validated (Rodo, Adan, Arnulfo, Sofi, Jorge)
- [ ] Pricing activated ($79/user/month Pro)

---

## POST-MVP (Pro 1.x — Fast Follow)

### Pro 2.0 — Pattern Propagation (Target: 2026-Q3)

**Layer 2 from capability stack.**

- Scope hierarchy for patterns (repo → team → org → enterprise)
- Cross-repo reinforcement (Wilson score aggregation)
- Promotion mechanism (auto repo→team, HITL team→org)
- Context bundle with inherited org patterns
- Pattern catalog endpoint

**Research:** [Pattern Propagation (L2)](work/research/pattern-propagation/)
**Estimated:** ~4-5 stories, ~3-4 weeks

---

### Pro 2.1 — Organizational Intelligence (Target: 2026-Q3)

**Layer 4 full from capability stack.**

- Risk intelligence (8 risk categories, early warning)
- Velocity & capacity metrics (throughput, cycle time, DORA partial)
- Process experiment tracking (Toyota Kata structure)
- Evidence-based improvement recommendations
- Audience-segmented dashboards (executive/architect/lead)

**Research:** [Organizational Learning (L4)](work/research/organizational-learning/)
**Critical constraint:** Goodhart's Law — velocity diagnostic only, never target.
**Estimated:** ~8-10 stories, ~6-8 weeks

---

### Pro 2.2 — Forge Integration (Target: 2026-Q3/Q4)

**Forge app + Rovo agents from walking skeleton design.**

- [RAISE-274](https://humansys.atlassian.net/browse/RAISE-274): Atlassian Forge Integration
- Rovo Rai Governance agent (compliance via chat)
- Rovo Rai Dev agent (context-aware development via chat)
- Confluence as governance content store (skills-as-pages)
- Jira workflow integration (governance in issue lifecycle)

**Research:** [Atlassian Forge Integration (RAISE-273)](work/research/atlassian-forge-integration/),
[Walking Skeleton](work/research/atlassian-forge-integration/walking-skeleton-design.md)

---

## ENTERPRISE (v3.0+)

### Enterprise Readiness (Target: 2026-Q4)

Everything in Pro, plus:

**Security & Compliance:**
- SSO/SAML authentication
- SCIM provisioning
- Comprehensive audit logging
- RBAC — role-based access control
- Compliance certifications (ISO 27001, SOC 2)

**Deployment:**
- Data residency controls
- On-premise / air-gapped option
- VPC deployment

**Enterprise Intelligence:**
- Organization-wide pattern aggregation (anonymized)
- Multi-org scope hierarchy (enterprise → org → team → repo)
- Cross-org pattern marketplace (enterprise tier only)
- Usage analytics / ROI reporting

**Support:**
- Dedicated account manager, custom SLA, professional services

---

## Timeline Summary

```
2026
 Feb         Mar              Apr       May       Jun       Q3        Q4
  │           │                │         │         │         │         │
  ├──✅───────┤                │         │         │         │         │
  │v2.1 P0.1 │                │         │         │         │         │
  │           │                │         │         │         │         │
  │     ┌─────┼──★ Mar 15 ────┤         │         │         │         │
  │     │ E-JIRA (🚀 now)    │         │         │         │         │
  │     │ E-SKILLS (🚀 now)  │         │         │         │         │
  │     │ E-GOV-FOUND        │         │         │         │         │
  │     └─────┼── MVP LAUNCH ─┤         │         │         │         │
  │           │   + Webinar    │         │         │         │         │
  │           │                ├─────────┼─────────┤         │         │
  │           │                │  P1.1 Guardrails  │         │         │
  │           │                │  P1.2 Health      │         │         │
  │           │                │         │         ├─────────┤         │
  │           │                │         │         │ P2.0-2.2│         │
  │           │                │         │         │ Patterns│         │
  │           │                │         │         │ OrgIntel│         │
  │           │                │         │         │ Forge   │         │
  │           │                │         │         │         ├─────────┤
  │           │                │         │         │         │ v3.0    │
  │           │                │         │         │         │ Enterpr.│
```

---

## Milestones & Dates

| Milestone | Target | Status |
|-----------|--------|--------|
| v2.0.0 published to PyPI | 2026-02-15 | ✅ |
| v2.1.0 published to PyPI | 2026-02-24 | ✅ |
| rai-server E2E validated (P0.1) | 2026-02-26 | ✅ |
| Jira integration in progress (E-JIRA) | 2026-02-26 | 🚀 |
| **★ MVP Launch + Atlassian Webinar** | **2026-03-15** | **🎯 Target** |
| P1.1 Governance Guardrails (poka-yoke + waivers) | 2026-Q2 | 📋 |
| P1.2 Portfolio Health (scorecards) | 2026-Q2 | 📋 |
| P2.0 Pattern Propagation | 2026-Q3 | 📋 |
| P2.1 Organizational Intelligence | 2026-Q3 | 📋 |
| P2.2 Forge Integration (Rovo agents) | 2026-Q3/Q4 | 📋 |
| Enterprise v3.0 | 2026-Q4 | 📋 |

---

## Research Base

All roadmap decisions grounded in formal research (SES-294, 2026-02-26):

| Research | Key Finding | Confluence |
|----------|-------------|-----------|
| [L1: Cross-Repo Visibility](work/research/cross-repo-visibility/) | Schema supports cross-repo edges; gap is population + traversal | [Page](https://humansys.atlassian.net/wiki/spaces/RaiSE1/pages/3084648458) |
| [L2: Pattern Propagation](work/research/pattern-propagation/) | Scope hierarchy + Wilson aggregation + SECI model | [Page](https://humansys.atlassian.net/wiki/spaces/RaiSE1/pages/3082715148) |
| [L3: Governance Intelligence](work/research/governance-intelligence-multi-repo/) | Poka-yoke in skills, MUST/SHOULD/CAN, waivers, compliance | [Page](https://humansys.atlassian.net/wiki/spaces/RaiSE1/pages/3084451849) |
| [L4: Organizational Learning](work/research/organizational-learning/) | Health scorecards, Goodhart safeguards, experiment tracking | [Page](https://humansys.atlassian.net/wiki/spaces/RaiSE1/pages/3084779523) |
| [Forge Integration](work/research/atlassian-forge-integration/) | Three-layer architecture, Rovo agents, walking skeleton | [Page](https://humansys.atlassian.net/wiki/spaces/RaiSE1/pages/3078160385) |
| [Shared Memory Architecture](work/research/shared-memory-architecture/) | PostgreSQL + JSONB, multi-tenancy, scoping | [Page](https://humansys.atlassian.net/wiki/spaces/RaiSE1/pages/3078619137) |

---

## Pricing Reference

| Tier | Price | Audience | Available |
|------|-------|----------|-----------|
| COMMUNITY | Free (BYOK) | Solo devs, OSS | ✅ Now (v2.1.0) |
| PRO | $79/user/month (BYOK) | Teams 5-200 | Pro 1.0 (2026-Q2) |
| ENTERPRISE | $149/user/month + custom | 200+ devs, regulated | v3.0 (2026-Q4) |

See `governance/tiers.md` for full tier definitions and feature matrix.

---

*Updated: 2026-02-26 (SES-294)*
*Previous: 2026-02-13 (SES-234)*
*Next update: After E-GOV-FOUNDATION epic design*
