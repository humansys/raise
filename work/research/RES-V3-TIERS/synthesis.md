# V3 Release — Research Synthesis & Epic Definitions

> **Research ID:** RES-V3-TIERS
> **Date:** 2026-02-13
> **Session:** SES-149
> **Status:** Draft — pending formal release ontology (S-RELEASE-ONTOLOGY)
> **Participants:** Emilio + Rai

---

## 1. Strategic Context

### Market Position

RaiSE is **first to market** with a holistic approach to AI-assisted software engineering that combines methodology, governance, and persistent intelligence. No competitor offers this combination:

- **Code completion tools** (Copilot, Cursor, Windsurf) optimize for speed, not reliability
- **Platform tools** (GitLab, GitHub) provide CI/CD and project management, not AI methodology
- **Continue/Tabnine** offer team features but no governance framework

RaiSE's differentiation is the **Triad**: Human judgment + AI execution + Methodology governance.

### Business Momentum (Feb 2026)

- **3 corporate demos in 1 week:** INVEX (banking), Coppel (retail), Telcel (telecom — digital channels)
- **Jumpstart program:** First paying customer (kicked off 2026-02-10)
- **Atlassian Gold Partner:** Channel advantage + March 14 webinar
- **Team expanding:** Aquiles (E18), Daniel Urbina, Fernando (v2/v3 contributions)

### Strategic Objective

**Cash in ASAP. Become a viable business model. Seek VC funding. Race to the top.**

March 14, 2026: Commercial offering available as BYOK trial for corporate customers.

---

## 2. Tier Model (Evidence-Informed)

### Research Basis

| Research                            | Key Finding                                                                                                                                                                                         |
| ----------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **RQ1** (Enterprise tiers)    | SSO/SAML is universal enterprise gate. Free→Paid = "I need a team." Paid→Enterprise = "procurement requires it."                                                                                  |
| **RQ2** (AI dev tools)        | Market bifurcating: inference sellers vs workflow sellers. RaiSE = workflow seller. BYOK is the trend. Persistence/memory is a nascent differentiator where RaiSE leads.                            |
| **RQ3** (Infrastructure)      | PostgreSQL on Supabase, NOT a graph DB. $25-30/mo for 10 users. 4-week MVP achievable. Sync engine is critical path.                                                                                |
| **RQ4** (Enterprise adoption) | 5 blockers: SSO, audit, compliance certs, RBAC, data training opt-out. LatAm: ISO 27001 > SOC 2. CNBV banking regs may require on-prem for INVEX. CLI-first BYOK is already a structural advantage. |

### Tier Definitions

#### COMMUNITY (Free, Open Source)

**Who:** Solo developers, OSS contributors, students, individual practitioners.
**Model:** Free forever. BYOK — works with Claude Code, Cursor, any capable agent.
**Boundary:** Local only. Git-based. Everything lives in your repo.

**Features:**

- `rai` CLI (all commands)
- All 20 skills (session, epic, story, discovery, meta)
- Memory system (personal — patterns, calibration, sessions)
- Multi-language discovery (Python, TS/TSX, PHP, Svelte)
- Governance framework scaffolding (`rai init`, onboarding)
- Knowledge graph (local JSON-based)
- Local telemetry (Phase 1)
- BYOK inference — customer's own API key, always

**Value proposition:** *"Ship reliable software at AI speed. Solo."*

**Purpose in funnel:** Adoption engine. Developer tries it, loves it, brings it to work. Bottom-up entry into enterprises.

---

#### PRO (Paid, BYOK) — $79/user/month

**Who:** Development teams in corporate context. 5-200 developers.
**Model:** Paid SaaS. Customer brings own Claude API key (inference theirs). Humansys hosts knowledge graph + memory persistence.
**Boundary:** Hosted intelligence layer. Shared memory. External tool integrations.

**Features (everything in COMMUNITY, plus):**

**Shared Memory (core differentiator):**

- Project-level memory — patterns, decisions, architecture understanding shared across team
- Team awareness — "Daniel worked on auth yesterday, found 3 edge cases"
- Cross-session persistence — Rai remembers across machines, sessions, developers
- Conflict resolution — when two Rai instances learn contradicting patterns
- Privacy gradient — calibration stays personal, architecture insights are shared

**Platform Integration:**

- `rai backlog` — Platform-agnostic backlog commands (Jira first, GitLab later)
  - Create/read/update/transition issues
  - JQL search abstracted
  - Story lifecycle synced to Jira (story-start → issue, story-close → transition)
- `rai docs publish` — Design docs → Confluence pages
- `rai search` — Unified search across Jira + Confluence (Rovo)
- Compass catalog — Component registry sync (beta)
- Token-efficient CLI wrappers (~200 tokens vs ~8,000 raw MCP per operation)

**Hosted Knowledge Graph:**

- PostgreSQL on Supabase (not a graph DB — our scale doesn't need it)
- Sync protocol: local ↔ cloud memory stays consistent
- Row-level security for multi-tenancy
- pgvector ready for future semantic search

**Value proposition:** *"Your team's Rai gets smarter with every session. Shared intelligence that compounds."*

**Pricing justification:** $79/user/mo is less than GitLab Ultimate ($99), delivers more process value than any single tool in the stack. The methodology + persistent intelligence + integrations justify premium positioning. At 50 developers, that's $47,400/year — trivial against the cost of one production incident from missed governance.

---

#### ENTERPRISE ($149/user/month + custom)

**Who:** Regulated industries, large enterprises. 200+ developers. Procurement process.
**Model:** Custom contracts. On-premise option. Dedicated support.
**Boundary:** Security, compliance, deployment control.

**Features (everything in PRO, plus):**

**Security & Compliance (BLOCKERS per RQ4):**

- SSO/SAML authentication
- SCIM provisioning
- Comprehensive audit logging
- Compliance certifications (ISO 27001 priority for LatAm, SOC 2 for US)
- Data training opt-out guarantee (contractual)
- RBAC — role-based access control

**Deployment:**

- Data residency controls
- On-premise / air-gapped option (critical for INVEX per CNBV regulations)
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

**Status:** Future/beta. Not building for March 14 unless INVEX forces the timeline (CNBV on-prem requirement).

---

### Pricing Strategy: Value-Based, Not Competitive

**Why not $15-25/user/month:**
We initially benchmarked against code completion tools (Copilot $19, Cursor $20-40). But RaiSE isn't autocomplete — it's a methodology + governance + persistent AI partner. The right comparison is the cost of NOT having it:

| Problem Cost                                    | Monthly per Developer         |
| ----------------------------------------------- | ----------------------------- |
| 1 production incident from skipped governance   | $5,000-50,000 (one event)     |
| 5-10 hrs/week wasted on process overhead        | $2,000-6,000/mo               |
| Developer onboarding (3-6 months to productive) | $8,000-15,000/mo unproductive |
| Knowledge loss when someone leaves              | Incalculable                  |
| Rework from bad architecture decisions          | $3,000-10,000/mo              |

If RaiSE saves 20% of that waste, the value is $2,000-5,000/user/month. Charging $79 captures ~2-4% of value delivered.

**VC-relevant ARR projections:**

- 3 enterprise deals × 50 devs × $79/mo = **$142K ARR** (seed-stage proof)
- 10 deals × 50 devs × $79/mo = **$474K ARR** (Series A territory)
- 50 deals × 100 devs × mixed pricing = **$3M+ ARR** (growth stage)

---

## 3. Release Epics (REL-V3.0)

### E19: V3 Product Design

**Objective:** Turn research and strategic conversations into formalized governance artifacts and architecture decisions.

**Stories:**

| ID    | Story                     | Size | Description                                                                               |
| ----- | ------------------------- | ---- | ----------------------------------------------------------------------------------------- |
| S19.1 | Research synthesis        | S    | Formalize RQ1-4 findings into actionable decisions (THIS DOCUMENT)                        |
| S19.2 | Tier & pricing definition | S    | Governance doc: features per tier, pricing model, positioning                             |
| S19.3 | Architecture decisions    | M    | ADRs: hosted infrastructure (Supabase), sync protocol, auth, BYOK handling, multi-tenancy |
| S19.4 | Implementation roadmap    | S    | Sequence E20-E22, dependencies, March 14 critical path                                    |

**Output:** Governance artifacts, ADRs, epic scopes. No code.

---

### E20: Shared Memory Architecture

**Objective:** Enable persistent, shared intelligence across team members — the core PRO differentiator and data moat.

**Stories (draft):**

| ID    | Story               | Size | Description                                                            |
| ----- | ------------------- | ---- | ---------------------------------------------------------------------- |
| S20.1 | Memory taxonomy     | S    | Classify what's personal vs project vs team. Privacy boundaries.       |
| S20.2 | Cloud persistence   | M    | Supabase schema, API layer, graph storage in PostgreSQL                |
| S20.3 | Sync protocol       | L    | Local ↔ cloud sync. Graph diffing. Conflict detection. CRITICAL PATH. |
| S20.4 | Conflict resolution | M    | Merge strategy for competing patterns. Policy-based resolution.        |
| S20.5 | Team awareness      | M    | Session summaries visible to team. "What did X work on?"               |
| S20.6 | CLI integration     | M    | `rai memory sync`, `rai memory team`, config for hosted mode       |

**Key design questions:**

1. One Rai per project (shared brain) vs multiple Rai instances that sync?
2. Sync model: real-time, eventually consistent, or git-like push/pull?
3. Conflict resolution: last-write-wins, merge, or human-arbitrated?
4. Privacy: what's shared by default vs opt-in?

**Critical path:** S20.3 (sync protocol) — if this slips, everything slips.

---

### E21: Platform Integration (Backlog Abstraction Layer)

**Objective:** Rai speaks the team's tools — Jira, Confluence, Compass — natively from the CLI.

**Stories (draft):**

| ID    | Story                     | Size | Description                                                             |
| ----- | ------------------------- | ---- | ----------------------------------------------------------------------- |
| S21.1 | BacklogProvider interface | S    | Port/adapter pattern. Abstract interface for backlog operations.        |
| S21.2 | JiraAdapter               | M    | Jira read/write via atlassian-python-api. Token-efficient CLI wrappers. |
| S21.3 | ConfluenceAdapter         | M    | Confluence read/write. Design docs → pages.                            |
| S21.4 | `rai backlog` commands  | M    | CLI commands: create, read, update, transition, search                  |
| S21.5 | `rai docs publish`      | S    | Publish design.md / architecture docs to Confluence                     |
| S21.6 | Skill lifecycle sync      | M    | story-start → creates Jira issue, story-close → transitions           |
| S21.7 | Compass integration       | S    | Component catalog sync (beta, needs site admin)                         |

**Architecture:** Port/Adapter pattern. `BacklogProvider` interface → `JiraAdapter` first, `GitLabAdapter` later. Clean interfaces enable parallel development (Daniel/Fernando can build adapters against the contract).

**PoC validated:** MCP integration works (SES-148). JIRA + Confluence read/write confirmed.

---

### E22: Enterprise Readiness

**Objective:** Security, compliance, and deployment controls that unlock enterprise sales.

**Stories (draft):**

| ID    | Story                 | Size | Description                                            |
| ----- | --------------------- | ---- | ------------------------------------------------------ |
| S22.1 | SSO/SAML              | M    | Supabase Auth + SAML provider integration              |
| S22.2 | Audit logging         | M    | Comprehensive audit trail for all operations           |
| S22.3 | RBAC                  | M    | Role-based access control at organization level        |
| S22.4 | Compliance framework  | L    | ISO 27001 process + documentation. SOC 2 prep.         |
| S22.5 | On-premise deployment | L    | Air-gapped deployment option (critical for INVEX/CNBV) |
| S22.6 | Data residency        | M    | Customer choice of data region                         |

**Status:** Scoped but unscheduled. Post-March 14 unless INVEX/CNBV forces the timeline.

---

## 4. March 14 Critical Path

### What Must Ship

1. **E19 complete** — Tier definitions formalized, architecture decisions made
2. **E20 MVP** — At minimum: cloud persistence + basic sync (single-user first, team features v1.1)
3. **E21 MVP** — Jira integration + Confluence publish (the demo)
4. **E18 complete** — Repo public, CI/CD live (Aquiles)

### Timeline (4 weeks)

```
Week 1 (Feb 14-20):  E19 (Product Design) + E18 close + Supabase schema
Week 2 (Feb 21-27):  E20.2-20.3 (Cloud persistence + sync engine) ← CRITICAL PATH
Week 3 (Feb 28-Mar 6): E20.5 (Team awareness) + E21.1-21.3 (Adapters)
Week 4 (Mar 7-13):   E21.4-21.6 (CLI + skill sync) + integration testing + demo prep
```

### Team Allocation

| Person                      | Focus                                                     | Weeks    |
| --------------------------- | --------------------------------------------------------- | -------- |
| **Aquiles**           | E18 S18.3 (release engineering)                           | Week 1-2 |
| **Daniel + Fernando** | V2 polish (parking lot items), ramp up, then E21 adapters | Week 1-4 |
| **Emilio + Rai**      | E19 → E20 → E21 core                                    | Week 1-4 |

### Risk

- **Sync engine complexity** — Graph diffing is the hard part. If it slips, cut to single-user persistence first.
- **Daniel/Fernando ramp** — They need onboarding time. First 1-2 weeks may be learning.
- **INVEX on-prem** — If CNBV requires it for March 14, E22 scope gets pulled forward.

---

## 5. Design Partners

First customers should be **design partners**, not just buyers:

| Company          | Industry | Offer            | What We Get                                                  |
| ---------------- | -------- | ---------------- | ------------------------------------------------------------ |
| **INVEX**  | Banking  | 50% for 6 months | Case study, logo, reference calls, CNBV requirements insight |
| **Coppel** | Retail   | 50% for 6 months | Case study, logo, scale testing (large dev team)             |
| **Telcel** | Telecom  | 50% for 6 months | Case study, logo, digital channels use case                  |

Three enterprise logos in banking/telecom/retail in Mexico = instant VC credibility.

---

## 6. VC Positioning

**Pitch summary:** *First AI governance platform. Methodology + persistent AI partner + enterprise integrations. BYOK. Three regulated-industry customers in pipeline. Atlassian Gold Partner. $142K ARR potential from first 3 deals.*

| Signal                     | Evidence                                                               |
| -------------------------- | ---------------------------------------------------------------------- |
| **Market timing**    | AI governance becoming regulatory (Mexico LFPDPPP reform, CNBV)        |
| **Moat**             | Accumulated intelligence compounds. Network effects. First-mover.      |
| **Enterprise logos** | INVEX (banking), Coppel (retail), Telcel (telecom) — in pipeline      |
| **ARR trajectory**   | 3 × 50 devs × $79 = $142K. Path to $500K with 10 deals.              |
| **Channel**          | Atlassian Gold Partner = built-in distribution                         |
| **Team**             | Growing. Dogfooding daily. Building with the product.                  |
| **Architecture**     | BYOK = no inference cost. Platform fee for methodology + intelligence. |

---

## 7. Ontology Prerequisite

**Before formal V3 work begins:**

Story **S-RELEASE-ONTOLOGY** must add `release` as a first-class concept:

- Add `release` to `NodeType` and `ConceptType`
- Create `governance/roadmap.md` with release definitions
- Roadmap parser (follows backlog parser pattern)
- `part_of` edges: epic → release
- Wire into graph builder

This enables REL-V3.0 to be a proper graph node that groups E19-E22.

---

## 8. Open Questions

1. **One Rai per project vs multiple Rai instances that sync?** — Architectural AND philosophical. Deferred to E20 design.
2. **Per-project pricing component?** — A company with 10 devs and 50 projects gets more value than 10 devs and 1 project. Consider per-project add-on or tiered project limits.
3. **Trial model specifics** — Time-limited (30 days)? Feature-limited? Usage-limited?
4. **INVEX timeline** — Does CNBV require on-prem for their pilot? If yes, E22 scope pulls forward.
5. **Daniel/Fernando onboarding plan** — What parking lot items are best for ramp-up?

---

*Captured during SES-149 strategic session*
*Research inputs: RQ1 (enterprise tiers), RQ2 (AI dev tools), RQ3 (infrastructure), RQ4 (enterprise adoption)*
*To be formalized as governance artifacts after S-RELEASE-ONTOLOGY completes*
