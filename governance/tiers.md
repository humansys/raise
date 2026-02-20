---
type: governance
subtype: tiers
name: "V3 Commercial Tiers"
status: current
version: "1.0"
release: REL-V3.0
date: 2026-02-13
pricing_model: per-user
tiers:
  - id: COMMUNITY
    price: "Free"
    model: "Open Source, BYOK"
    audience: "Solo developers, OSS contributors, students"
  - id: PRO
    price: "$79/user/month"
    model: "Paid SaaS, BYOK"
    audience: "Development teams (5-200 developers)"
  - id: ENTERPRISE
    price: "$149/user/month + custom"
    model: "Custom contract"
    audience: "Regulated industries, 200+ developers"
---
# Commercial Tiers: COMMUNITY / PRO / ENTERPRISE

> **Release:** REL-V3.0 (March 14, 2026)
> **Pricing model:** Per-user/month
> **Trial model:** COMMUNITY is the trial — free forever, upgrade when your team needs shared intelligence

---

## Overview

RaiSE offers three tiers designed around a natural progression: individual developer adopts for free, team upgrades for shared intelligence, enterprise adds security and compliance.

**Rai framing:** Each project has one Rai — a persistent AI partner that accumulates judgment across sessions. Technically, each developer runs their own Rai instance that syncs to a shared project memory (like git: one repo, many clones). COMMUNITY Rai is local-only. PRO Rai syncs across the team. Enterprise Rai adds governance controls.

**BYOK (Bring Your Own Key):** All tiers use the customer's own inference API key. RaiSE never handles inference — the customer's data stays with their provider. This is a structural advantage for regulated industries and a cost transparency win for everyone.

---

## Tier Definitions

### COMMUNITY (Free, Open Source)

**Who:** Solo developers, OSS contributors, students, individual practitioners.

**Model:** Free forever. BYOK — works with Claude Code, Cursor, any capable AI agent.

**Boundary:** Local only. Git-based. Everything lives in your repo.

**Features:**

- `rai` CLI — all commands, no artificial limits
- All 20 skills (session, epic, story, discovery, meta)
- Memory system — personal patterns, calibration, session history
- Multi-language discovery (Python, TypeScript/TSX, PHP, Svelte)
- Governance framework scaffolding (`rai init`, onboarding)
- Knowledge graph (local JSON-based)
- Local telemetry (velocity tracking, signal analysis)
- BYOK inference — customer's own API key, always
- **Adapter extension contracts (ADR-033, ADR-034)** — `GovernanceSchemaProvider`,
  `GovernanceParser`, `DocumentationTarget`, and `ProjectManagementAdapter` Protocol
  definitions are Apache 2.0–licensed. The community can build adapters (Notion, Obsidian,
  Azure DevOps, GitHub Issues) against these contracts without any dependency on raise-pro.

**Value proposition:** *"Ship reliable software at AI speed. Solo."*

**Role in funnel:** COMMUNITY is the adoption engine. A developer tries RaiSE, internalizes the methodology, and brings it to their team. Bottom-up enterprise entry — the most defensible growth model in developer tools.

---

### PRO ($79/user/month, BYOK)

**Who:** Development teams in corporate context. 5-200 developers.

**Model:** Paid SaaS. Customer brings own Claude API key (inference stays theirs). Humansys hosts the knowledge graph and memory persistence layer.

**Boundary:** Hosted intelligence layer. Shared memory. External tool integrations.

**Features (everything in COMMUNITY, plus):**

**Shared Memory — the core differentiator:**

- Project-level memory — patterns, decisions, architecture understanding shared across team
- Team awareness — "Daniel worked on auth yesterday, found 3 edge cases"
- Cross-session persistence — Rai remembers across machines, sessions, developers
- Conflict resolution — when two Rai instances learn contradicting patterns
- Privacy gradient — calibration stays personal, architecture insights are shared

**Platform Integration (raise-pro adapters — ADR-033, ADR-034):**

- `rai backlog` — Platform-agnostic backlog commands backed by `ProjectManagementAdapter`
  - Create/read/update/transition issues
  - JQL search abstracted behind CLI
  - Story lifecycle synced to Jira (story-start creates issue, story-close transitions)
  - First implementation: `raise-jira-adapter` (raise-pro). Community may build `raise-linear-adapter`, etc.
- `rai docs publish` — Publishes governance docs to Confluence via `DocumentationTarget`
  - Destination resolved from org config (`.raise/adapters/confluence-governance.yaml`)
  - Org-specific space mapping, page hierarchy, and templates
- `rai memory build` with `JiraBacklogParser` — Jira issues flow into the knowledge graph
- `rai search` — Unified search across Jira + Confluence (via Rovo)
- Compass catalog — Component registry sync (beta)
- Token-efficient CLI wrappers (~200 tokens vs ~8,000 raw MCP per operation)

**Hosted Knowledge Graph:**

- PostgreSQL on Supabase (our scale doesn't need a graph DB)
- Sync protocol: local-first, cloud-backed — works offline, syncs when connected
- Row-level security for multi-tenancy
- pgvector ready for future semantic search

**Value proposition:** *"Your team's Rai gets smarter with every session. Shared intelligence that compounds."*

**Pricing justification:** $79/user/mo is less than GitLab Ultimate ($99) and delivers more process value than any single tool in the stack. The methodology + persistent intelligence + integrations justify premium positioning. At 50 developers, that's $47,400/year — trivial against the cost of one production incident from missed governance.

---

### ENTERPRISE ($149/user/month + custom)

**Who:** Regulated industries, large enterprises. 200+ developers. Procurement process.

**Model:** Custom contracts. On-premise option. Dedicated support.

**Boundary:** Security, compliance, and deployment control on top of PRO capabilities.

**Features (everything in PRO, plus):**

**Security & Compliance:**

- SSO/SAML authentication
- SCIM provisioning (automated user management)
- Comprehensive audit logging
- Compliance certifications (ISO 27001 priority for LatAm, SOC 2 for US)
- Data training opt-out guarantee (contractual)
- RBAC — role-based access control

**Deployment:**

- Data residency controls (choose your region)
- On-premise / air-gapped option (critical for banking per CNBV regulations)
- VPC deployment option

**Support:**

- Dedicated account manager
- Custom SLA (99.95%+ uptime)
- Priority support (24/7)
- Professional services / implementation support (Jumpstart program)

**Enterprise Intelligence:**

- Organization-wide pattern aggregation (anonymized)
- Usage analytics / ROI reporting
- Model governance controls (approve which models developers use)
- IP indemnification

**Value proposition:** *"RaiSE for the enterprise. Security, compliance, and governance built in — not bolted on."*

**Pricing justification:** $149/user/mo aligns with enterprise developer tooling expectations. Regulated industries (banking, telecom) routinely pay this for tools that meet compliance requirements. The on-premise option and compliance certifications justify the premium over PRO.

---

## Feature Comparison Matrix

| Feature                             | COMMUNITY | PRO | ENTERPRISE |
| ----------------------------------- | :-------: | :-: | :--------: |
| **Core**                      |          |    |            |
| CLI (all commands)                  |    ✓    | ✓ |     ✓     |
| All 20 skills                       |    ✓    | ✓ |     ✓     |
| BYOK inference                      |    ✓    | ✓ |     ✓     |
| Governance scaffolding              |    ✓    | ✓ |     ✓     |
| **Memory**                    |          |    |            |
| Personal memory (local)             |    ✓    | ✓ |     ✓     |
| Local knowledge graph               |    ✓    | ✓ |     ✓     |
| Local telemetry                     |    ✓    | ✓ |     ✓     |
| Shared project memory               |    —    | ✓ |     ✓     |
| Cross-session persistence           |    —    | ✓ |     ✓     |
| Team awareness                      |    —    | ✓ |     ✓     |
| Hosted knowledge graph              |    —    | ✓ |     ✓     |
| Org-wide pattern aggregation        |    —    | — |     ✓     |
| **Discovery**                 |          |    |            |
| Multi-language discovery            |    ✓    | ✓ |     ✓     |
| **Extensibility (ADR-033/034)**|          |    |            |
| Adapter Protocol contracts (Apache 2.0)    |    ✓    | ✓ |     ✓     |
| Community adapter support           |    ✓    | ✓ |     ✓     |
| raise-pro adapters (Jira, Confluence)|   —    | ✓ |     ✓     |
| Custom org governance schemas       |    —    | ✓ |     ✓     |
| **Platform Integration**      |          |    |            |
| Jira integration (`rai backlog`)    |    —    | ✓ |     ✓     |
| Confluence publishing (`rai docs`)  |    —    | ✓ |     ✓     |
| Jira → knowledge graph parser       |    —    | ✓ |     ✓     |
| Unified search (Rovo)               |    —    | ✓ |     ✓     |
| Compass catalog sync                |    —    | ✓ |     ✓     |
| **Security & Compliance**     |          |    |            |
| SSO/SAML                            |    —    | — |     ✓     |
| SCIM provisioning                   |    —    | — |     ✓     |
| Audit logging                       |    —    | — |     ✓     |
| RBAC                                |    —    | — |     ✓     |
| Compliance certs (ISO 27001, SOC 2) |    —    | — |     ✓     |
| Data training opt-out               |    —    | — |     ✓     |
| **Deployment**                |          |    |            |
| Local (git-based)                   |    ✓    | ✓ |     ✓     |
| Cloud-hosted (Supabase)             |    —    | ✓ |     ✓     |
| Data residency controls             |    —    | — |     ✓     |
| On-premise / air-gapped             |    —    | — |     ✓     |
| VPC deployment                      |    —    | — |     ✓     |
| **Support**                   |          |    |            |
| Community (GitHub Issues)           |    ✓    | ✓ |     ✓     |
| Priority support                    |    —    | ✓ |     ✓     |
| Dedicated account manager           |    —    | — |     ✓     |
| Custom SLA                          |    —    | — |     ✓     |
| Professional services               |    —    | — |     ✓     |

---

## Pricing Strategy

### Model: Per-User, Value-Based

| Tier       | Price           | Billing           | Minimum |
| ---------- | --------------- | ----------------- | ------- |
| COMMUNITY  | Free            | —                | —      |
| PRO        | $79/user/month  | Annual or monthly | 5 users |
| ENTERPRISE | $149/user/month | Annual contract   | Custom  |

**Annual discount:** 2 months free on annual billing (effective $65.83/user/mo PRO, $124.17/user/mo ENTERPRISE).

### Why Value-Based, Not Competitive

RaiSE isn't autocomplete — it's a methodology + governance + persistent AI partner. The right comparison is the cost of NOT having it:

| Problem Cost                                    | Monthly per Developer         |
| ----------------------------------------------- | ----------------------------- |
| 1 production incident from skipped governance   | $5,000-50,000 (one event)     |
| 5-10 hrs/week wasted on process overhead        | $2,000-6,000/mo               |
| Developer onboarding (3-6 months to productive) | $8,000-15,000/mo unproductive |
| Knowledge loss when someone leaves              | Incalculable                  |
| Rework from bad architecture decisions          | $3,000-10,000/mo              |

If RaiSE saves 20% of that waste, the value is $2,000-5,000/user/month. Charging $79 captures ~2-4% of value delivered.

### ARR Projections

| Scenario   | Deals | Avg Devs |  Avg Price  |  ARR |
| ---------- | :---: | :------: | :---------: | ---: |
| Seed proof |   3   |    50    | $79 | $142K |      |
| Series A   |  10  |    50    | $79 | $474K |      |
| Growth     |  50  |   100   |    mixed    | $3M+ |

---

## Design Partner Program

First customers are **design partners** — they get preferred pricing in exchange for feedback, case studies, and reference calls.

| Company | Industry | Offer            | What We Get                                      |
| ------- | -------- | ---------------- | ------------------------------------------------ |
| INVEX   | Banking  | 50% for 6 months | Case study, logo, CNBV requirements insight      |
| Coppel  | Retail   | 50% for 6 months | Case study, logo, scale testing (large dev team) |
| Telcel  | Telecom  | 50% for 6 months | Case study, logo, digital channels use case      |

**Terms:**

- 50% discount on PRO pricing for 6 months
- Minimum 25 developer seats
- Quarterly feedback sessions
- Permission to use logo and publish case study
- Design partners influence roadmap prioritization

Three enterprise logos in banking/telecom/retail in Mexico = instant VC credibility.

---

## Glossary

| Term                             | Definition                                                                                         |
| -------------------------------- | -------------------------------------------------------------------------------------------------- |
| **BYOK**                   | Bring Your Own Key — customer provides their own AI inference API key                             |
| **Shared Memory**          | Project-level memory that persists across team members and sessions                                |
| **Privacy Gradient**       | Calibration and personal patterns stay private; architecture insights are shared                   |
| **Rai**                    | The persistent AI partner in the RaiSE Triad — one entity per project, multiple runtime instances |
| **Hosted Knowledge Graph** | Cloud-backed PostgreSQL storage for the project's ontology graph                                   |
| **Jumpstart**              | Professional services program for enterprise onboarding                                            |

---

*Created: 2026-02-13*
*Source: RES-V3-TIERS, S19.1 decisions*
*Next update: After S19.3 ADRs (if tier boundaries shift)*
