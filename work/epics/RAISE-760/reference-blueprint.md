# RaiSE on Atlassian — Reference Blueprint

**Epic:** RAISE-760 | **Story:** S760.8
**Date:** 2026-03-27
**Version:** 1.0
**Audience:** Partner teams adopting RaiSE on the Atlassian stack
**Evidence base:** 4 research tracks (85 sources), 6 design documents, 4 ADRs

---

## Executive Summary

This blueprint defines how RaiSE — an AI-augmented software engineering
framework — maps to the Atlassian product suite. It is grounded in 4 research
tracks covering 85 evidence sources, validated against the Atlassian API
landscape as of March 2026, and designed so that any team already on Atlassian
can adopt RaiSE with zero friction.

The core principle is **each product does what it was designed for**:

- **Jira** tracks work (Initiative → Epic → Story → Sub-task)
- **Confluence** holds knowledge (governance, architecture, skills, research)
- **Compass** catalogs software (capabilities with health scorecards and DORA)
- **Forge + Rovo** provide AI interface (governance agents querying the knowledge graph)
- **Bitbucket** enables code collaboration (branch linking, pipelines, dev panel)
- **Jira Automation** is the glue (cross-product lifecycle cascades)

The result: a team using RaiSE on Atlassian gets AI-governed software delivery
where governance lives in Confluence pages, work tracking lives in Jira,
software health lives in Compass, and a Rovo agent ties it all together with
natural language queries.

---

## 1. The Model: Seven Products, One Platform

### 1.1 Product Responsibility Matrix

Every RaiSE concept maps to exactly ONE primary Atlassian product. Secondary
products participate via integration, not duplication.

| Product | Primary Responsibility | RaiSE Concepts |
|---------|----------------------|----------------|
| **Jira** | Work tracking & lifecycle | Initiatives, Epics, Stories, Bugs, Tasks, Sprints, Versions |
| **Confluence** | Knowledge & documentation | Governance docs, ADRs, skills-as-pages, research, patterns, designs, retros, templates, glossary, release notes |
| **Compass** | Software catalog & health | Capabilities (12 components), scorecards, DORA metrics, dependency graphs, ownership |
| **Forge** | App platform & state | Rovo agent backend functions, KVS (conversation state), Secret Store (API keys), async queue consumers |
| **Rovo** | AI interface | Rai Governance agent, Rai Dev agent — natural language queries over Jira + Confluence + Compass |
| **Bitbucket** | Code collaboration | PR ↔ Jira links, branch naming (auto-link), pipelines (quality gates), development panel |
| **Automation** | Cross-product glue | Story → Done triggers retro page, Epic closed updates scorecard, session close archives to Confluence |

### 1.2 Where RaiSE Artifacts Live

| RaiSE Artifact | Filesystem (canonical) | Atlassian Product | Sync Mechanism |
|----------------|----------------------|-------------------|----------------|
| Knowledge graph | `.raise/` + raise-server | Forge (cache) + raise-server (canonical) | `rai graph sync` → raise-server; Forge `fetch()` → raise-server |
| Governance docs | `.raise/governance/` | Confluence (Governance section) | `rai docs publish governance` |
| ADRs | `dev/decisions/` | Confluence (Architecture/ADRs/) | `rai docs publish adr` |
| Epic scope/design/retro | `work/epics/{id}/` | Confluence (Epics/{KEY}/) + Jira Epic | Automation Rule 1 (start) + Rule 2 (close) |
| Skills (prompts) | `.raise/skills/` | Confluence (Skills/) | `rai docs publish skill`; Rovo reads natively |
| Patterns | `.raise/rai/memory/patterns.jsonl` | Confluence (Patterns/) | `rai docs publish pattern` |
| Research reports | `work/epics/{id}/research/` | Confluence (under Epic or Research/) | `rai docs publish research` |
| Capabilities | Implicit in code | Compass (12 components) | Manual setup → Forge dataProvider (future) |
| Session journal | `.raise/rai/sessions/` | Confluence (Sessions/) via Automation | Hook → webhook → Automation Rule 4 |
| Telemetry | `.raise/telemetry/` | Forge Entity Store → Compass (DORA) | CompassMetricHook (future) |
| Branches/PRs | Git | Bitbucket dev panel in Jira | Auto-link via Jira key in branch name |
| Release notes | Git tags + changelog | Confluence (Releases/) + Jira versions | Automation Rule 5 (version released) |

### 1.3 Data Flow Architecture

```
Developer Workstation
  │
  │  rai graph sync, rai docs publish, rai signal emit-work
  ▼
raise-server (PostgreSQL) ◄──── Canonical knowledge store
  │                                    │
  │  Forge fetch()                     │  CLI push
  ▼                                    ▼
Forge App ◄────────────────────── RaiSE CLI
  │                                    │
  │  Rovo agent/action modules         │  BacklogHook
  ▼                                    ▼
Rovo Chat ──── queries ────► Jira ──── Automation ────► Confluence
  │                           │                          │
  │  user answers             │  dev panel               │  pages
  ▼                           ▼                          ▼
Developer ◄─────────────── Bitbucket ◄──────────── Compass
                             (code)              (catalog, DORA)
```

**Key principle:** raise-server is the canonical knowledge store. Atlassian
products are the visibility and collaboration layer. This avoids duplicating
graph logic in Forge (25s timeout constraint) while leveraging Atlassian's UI,
search, and permission model.

---

## 2. Jira: Work Tracking

### 2.1 Issue Type Hierarchy

```
Initiative              ← Strategic business objective (rolling, no fixed end)
  └── Epic              ← Bounded delivery (3-10 stories, has scope/design/retro)
       ├── Story        ← Delivers user/developer value
       ├── Bug          ← Defect
       ├── Task         ← Technical work (research, spike, infra via labels)
       │    └── Sub-task
       └── Sub-task
```

**Initiative** groups Epics toward a business goal ("PRO Launch", "OSS
Excellence"). Rolling — closed when the objective is achieved, not on a
schedule.

**Capability** is NOT in Jira. It lives in Compass (ADR-037). An Epic has
ONE Initiative parent (Jira) and links to ONE Compass component (the capability
it touches).

### 2.2 Components

| Component | Scope |
|-----------|-------|
| `rai-agent` | Autonomous personal agent |
| `raise-community` | Open source framework + CLI |
| `raise-pro` | Commercial extensions |
| `raise-forge` | Forge app (Rovo agents) |
| `raise-docs` | Documentation site |

**Policy:** Every Story and Bug MUST have a component.

### 2.3 Versions (fixVersion)

Versions map to release branches (ADR-033):

| Rule | Description |
|------|-------------|
| Every Story gets a fixVersion | "TBD" if uncertain |
| Epics get the primary release version | Where most stories land |
| Bugs get the fix version | Not where discovered |
| Initiatives have no fixVersion | They're rolling |

### 2.4 Labels

| Category | Convention | Examples |
|----------|-----------|----------|
| Work type | `{type}` | `research`, `spike`, `refactor`, `docs` |
| Product area | `{area}` | `atlassian`, `forge`, `rovo` |
| Strategic | `{tag}` | `pro-launch`, `partner`, `marketplace` |

**Rules:** Lowercase-hyphenated. Max 3 per issue. No version labels (use
fixVersion). No component labels (use component field). Capabilities are NOT
labels — they live in Compass.

### 2.5 Boards

| Board | Type | Filter | Swimlanes |
|-------|------|--------|-----------|
| **RaiSE Delivery** | Kanban | Stories/Bugs/Tasks for current release | By Epic |
| **RaiSE Portfolio** | Kanban | Open Epics | By Component |

### 2.6 Workflow

All issue types share the Software Simplified workflow:

```
Backlog (11) → Selected for Development (21) → In Progress (31) → Done (41)
```

**Exception:** Initiatives and Tasks skip "Selected" — they go directly from
Backlog to In Progress.

---

## 3. Confluence: Knowledge

### 3.1 Space Strategy

**One Confluence space per project/product.** Multiple spaces only for
regulatory or organizational boundary requirements.

Space key should match Jira project key when possible.

### 3.2 Page Tree

```
Space Root: {PROJECT_KEY}
├── Governance
│   ├── Code Standards
│   ├── Testing Policy
│   ├── Security Policy
│   ├── Guardrails/
│   └── Governance Policy Index
├── Architecture
│   ├── ADR Index
│   ├── ADR-001: {title}
│   ├── Architecture Overview
│   └── Module Documentation/
│       └── mod-{name} (from rai discover)
├── Epics
│   └── {EPIC-KEY}: {title}/
│       ├── Scope
│       ├── Design
│       ├── Plan
│       ├── Retrospective
│       ├── Research/
│       │   └── R{N} — {title}
│       └── Stories/
│           └── S{N}.{M} — {title}
├── Research (standalone)
│   ├── Research Index
│   └── {research-id} — {title}
├── Skills
│   ├── Skill Index
│   ├── Lifecycle Skills/
│   ├── Discovery Skills/
│   ├── Meta Skills/
│   └── Operational Skills/
├── Patterns
│   ├── Pattern Catalog
│   └── PAT-E-{NNN}: {summary}
├── Glossary
├── Templates
├── Releases
│   └── Release Notes — v{X.Y.Z}
├── Operations
│   ├── Dev Environment Setup
│   └── Deployment & Operations
└── Sessions
    └── Session {id} — {summary}
```

### 3.3 Skills-as-Pages

Skill definitions live as Confluence pages. Rovo agents read them natively —
no custom indexing required. Governance teams edit skills by editing pages.
Adding a governance process = creating a page. No code, no deploy.

This is the core differentiator: zero-code governance customization.

### 3.4 Labels for Confluence

| Category | Prefix | Examples |
|----------|--------|----------|
| Artifact type | `type:` | `type:adr`, `type:governance`, `type:research` |
| Epic | `epic:` | `epic:RAISE-760` |
| Capability | `capability:` | `capability:adapter-layer` |
| Version | `version:` | `version:2.4.0` |
| Status | `status:` | `status:accepted`, `status:draft` |

**CQL examples:**
```sql
-- All accepted ADRs
label = "type:adr" AND label = "status:accepted" AND space = "RaiSE1"

-- All research for an epic
label = "type:research" AND label = "epic:RAISE-760"

-- All governance docs
label = "type:governance" AND space = "RaiSE1"
```

---

## 4. Compass: Software Catalog

### 4.1 Why Compass

Capabilities are not work items — they don't have a lifecycle status, they
don't "complete." They are permanent competency areas of the product with
health, ownership, and dependencies. Compass was designed for exactly this
(ADR-037).

### 4.2 The 12 Components

| # | Name | Type | Tier | Lifecycle |
|---|------|------|------|-----------|
| C1 | Skill Engine | Library | 1 (Critical) | Active |
| C2 | Adapter Layer | Library | 1 (Critical) | Active |
| C3 | Session & Workstream | Library | 2 (Important) | Active |
| C4 | CLI & Developer Experience | Library | 1 (Critical) | Active |
| C5 | CI/CD & Release | Service | 2 (Important) | Active |
| C6 | Security & Compliance | Other | 2 (Important) | Active |
| C7 | RaiSE PRO | Library | 2 (Important) | Active |
| C8 | rai-agent Runtime | Service | 2 (Important) | Pre-release |
| C9 | rai-agent Operations | Service | 3 (Supporting) | Pre-release |
| C10 | SAFe & Portfolio Mgmt | Other | 3 (Supporting) | Pre-release |
| C11 | Memory & Knowledge | Library | 1 (Critical) | Active |
| C12 | Self-Improvement | Other | 3 (Supporting) | Pre-release |

### 4.3 Scorecards

Three scorecards evaluate component health:

1. **Component Readiness** (all components): owner, description, docs, repo
   link, lifecycle, dependencies — 80% pass threshold
2. **DevOps Health** (Tier 1-2): test coverage ≥80%, deployment frequency,
   change failure rate <15%, lead time <7d — 70% pass threshold
3. **Governance Compliance** (Active): ADRs, architecture docs, code standards
   score ≥90, type coverage ≥95% — 75% pass threshold

### 4.4 DORA Metrics

Data flow: CI/CD pipeline → raise-server events → Forge `compass:dataProvider`
→ Compass metrics dashboard.

Metrics: deployment frequency, lead time for changes, change failure rate, MTTR.

---

## 5. Forge + Rovo: AI Interface

### 5.1 Architecture (from RAISE-819)

```
Rovo Chat → Rovo Agent → Forge Actions → fetch() → raise-server
                                       → Forge KVS (state)
```

**No Custom UI for MVP.** Rovo chat is the entire UX (ADR-034). The
intelligence lives in the knowledge graph; Rovo provides distribution to
5M+ users.

### 5.2 Agents

| Agent | Purpose | Key Actions |
|-------|---------|-------------|
| **Rai Governance** | Standards compliance, governance queries | read-page, query-graph, sync-governance, validate-document |
| **Rai Dev** | Architecture, patterns, constraints | read-jira-context, query-graph, report-event |

### 5.3 The "Aha Moment"

Developer asks: "Does this follow our code standards?"

1. Agent queries raise-server knowledge graph for applicable standards
2. Evaluates content against standards
3. Returns structured answer with violations and rationale
4. Links to the Confluence page where the standard is defined

Under 30 seconds. No competitor on Atlassian Marketplace does this.

### 5.4 Key Constraints

| Constraint | Value | Mitigation |
|-----------|-------|------------|
| Sync function timeout | 25s hard limit | Async queue consumer (900s) for backend calls |
| KVS value limit | 240 KiB | Lean state design; raise-server for large data |
| Rate limit | 65K pts/hr (Tier 1) | Backend calls go to raise-server, not Jira API |
| Rovo memory | None between conversations | KVS persistence per user+context |

---

## 6. Bitbucket: Code Collaboration

### 6.1 Branch Naming for Auto-Linking

```
story/{JIRA_KEY}/s{EPIC}.{SEQ}/{slug}
```

Examples:
```
story/RAISE-761/s760.1/forge-scaffold
hotfix/RAISE-720
release/2.4.0
```

Jira issue key in branch name → automatic development panel linking.

### 6.2 Smart Commits

```
RAISE-761 #comment Implemented graph sync
RAISE-761 #in-progress
RAISE-761 #time 2h
```

**Recommendation:** Use smart commits for comments and time logging. Prefer
Jira Automation over `#done` for reliable lifecycle transitions.

### 6.3 Pipelines

Quality gates in `bitbucket-pipelines.yml`:
- `pytest` — test suite
- `pyright` — type checking
- `ruff` — linting
- `forge deploy` — Forge app deployment (staging/production)

### 6.4 GitHub Equivalents

| Bitbucket | GitHub |
|-----------|--------|
| Smart commits | GitHub for Jira app (same pattern) |
| Pipelines | GitHub Actions |
| Development panel | GitHub development sidebar |
| PR auto-link | Issue references in PR body |

---

## 7. Automation: Cross-Product Glue

### 7.1 Sync Model

**Unidirectional: RaiSE CLI → Jira → Automation → Confluence/Compass**

Developers drive lifecycle from the CLI (`/rai-story-start`, `/rai-story-close`).
The CLI pushes state to Jira via BacklogHook. Jira Automation cascades to other
products. No Jira → CLI sync needed because developers ARE in the CLI.

### 7.2 Automation Rules

| # | Rule | Trigger | Products | Priority |
|---|------|---------|----------|----------|
| 1 | Epic Started → Create Scope Page | Epic → In Progress | Jira → Confluence | P1 |
| 2 | Epic Closed → Create Retro Page | Epic → Done | Jira → Confluence | P1 |
| 3 | All Stories Done → Notify Epic Owner | Story → Done | Jira → Notification | P1 |
| 4 | Session Close → Confluence Archive | Incoming webhook | Webhook → Confluence | P2 |
| 5 | Release → Notes Page | Version released | Jira → Confluence | P2 |
| 6 | New Epic → Auto-Link Initiative | Epic created | Jira → Jira | P1 |
| 7 | Stale In Progress → Alert | Weekly schedule | Jira → Notification | P3 |

### 7.3 Lifecycle Event Flow

```
/rai-story-start
  → BacklogHook: Story → In Progress
    → Bitbucket: branch created (auto-linked via key in name)

/rai-story-close
  → BacklogHook: Story → Done
    → Bitbucket: PR merged
    → Automation Rule 3: all stories done? → notify Epic owner

/rai-epic-start
  → BacklogHook: Epic → In Progress
    → Automation Rule 1: Confluence scope page created

/rai-epic-close
  → BacklogHook: Epic → Done
    → Automation Rule 2: Confluence retro page created
    → Compass scorecard updated (future)
```

---

## 8. SAFe Mapping (Partner Reference)

For teams operating within SAFe, this table translates RaiSE concepts:

| SAFe Concept | RaiSE Term | Atlassian Product |
|-------------|-----------|------------------|
| Business Epic | Initiative | Jira — Initiative issue type |
| Capability | Capability | Compass — catalog component |
| PI (Program Increment) | Release | Jira — fixVersion |
| Feature | Epic | Jira — Epic issue type |
| Story | Story | Jira — Story issue type |
| Enabler | Task | Jira — Task + label |

**Initiative ≠ Capability.** Jira tracks work (Initiative → Epic → Story).
Compass catalogs software (Capability with health/ownership). Different
products, different purposes.

RaiSE does not require SAFe. All terminology is generic.

---

## 9. Setup Checklist

### Phase 1: Jira Configuration (Day 1)

- [ ] Verify Initiative issue type is available in project scheme
- [ ] Add components: `raise-forge`, `raise-docs` (keep existing 3)
- [ ] Create Initiatives, link existing Epics as children
- [ ] Set fixVersion on all open Stories
- [ ] Apply label taxonomy (retire version/component labels)
- [ ] Configure 2 boards (Delivery + Portfolio), archive redundant board
- [ ] Configure lifecycle_mapping in `.raise/jira.yaml` (add bug/initiative)
- [ ] Set up 4 P1 Automation rules (Rules 1, 2, 3, 6)

### Phase 2: Confluence Setup (Day 1-2)

- [ ] Create Confluence space (key = project key if possible)
- [ ] Create page tree (11 top-level sections per §3.2)
- [ ] Register templates (governance, ADR, epic scope, research, etc.)
- [ ] Publish existing governance docs via `rai docs publish`
- [ ] Configure `.raise/confluence.yaml` with space key

### Phase 3: Bitbucket Configuration (Day 2)

- [ ] Enable Jira-Bitbucket integration (DVCS connector)
- [ ] Configure branch naming convention in team docs
- [ ] Add `bitbucket-pipelines.yml` with quality gates
- [ ] Add `.bitbucket/pull-request-template.md`
- [ ] Verify smart commits work (test with a commit)

### Phase 4: Compass Setup (Week 2)

- [ ] Verify Compass is available in plan
- [ ] Create 12 components from capability definitions
- [ ] Apply Component Readiness scorecard
- [ ] Map dependencies between components
- [ ] Link existing Epics to Compass components
- [ ] Archive Capability issues in Jira (RAISE-795 to RAISE-815)

### Phase 5: Forge + Rovo (Week 3 — RAISE-819)

- [ ] Deploy Forge app via distribution link
- [ ] Configure raise-server API key in Forge Secret Store
- [ ] Sync governance docs to knowledge graph
- [ ] Test Rai Governance agent: "What are our code standards?"
- [ ] Test Rai Dev agent: "What patterns apply to this story?"

---

## 10. `rai init --stack atlassian` Specification

Future CLI command that scaffolds the complete Atlassian integration:

```bash
rai init --stack atlassian \
  --jira-site humansys.atlassian.net \
  --jira-project RAISE \
  --confluence-space RaiSE1 \
  --compass-project RAISE
```

**What it creates:**

| Artifact | Content |
|----------|---------|
| `.raise/jira.yaml` | Project, workflow, lifecycle mapping, team, automation URLs |
| `.raise/confluence.yaml` | Space key, page tree section IDs |
| `.raise/compass.yaml` (new) | Component IDs, scorecard IDs |
| Confluence page tree | 11 sections with index pages |
| Confluence templates | 10 templates registered in space |
| Jira components | `raise-forge`, `raise-docs` (if missing) |

**Prerequisites:** Jira project, Confluence space, and Compass project must
already exist. `rai init` populates them but does not create them.

---

## 11. Competitive Position

**No app on the Atlassian Marketplace combines:**

1. Neuro-symbolic knowledge graph (typed, deterministic — not RAG)
2. AI agents backed by governance validation (not just chat)
3. Cross-product lifecycle automation (Jira ↔ Confluence ↔ Compass)
4. Skills-as-pages (zero-code governance customization)
5. DORA metrics fed by AI-augmented telemetry

Existing apps address fragments (DORA metrics, documentation, compliance
checklists). RaiSE is the intelligence layer that connects them.

**The "no-brainer" pitch:**

> If your team already uses Jira + Confluence + Rovo, RaiSE turns your
> Atlassian stack into an AI-governed software development platform — no new
> tools to learn. Governance in Confluence pages. Work tracking in Jira.
> Software health in Compass. Rovo knows all three. RaiSE provides the
> deterministic intelligence layer that connects them.

---

## 12. Evidence Base

This blueprint is grounded in 4 research tracks with 85 sources:

| Track | Sources | Confidence | Key Finding |
|-------|---------|------------|-------------|
| R1: Atlassian API Landscape | 31 (24 primary) | High | Forge-only path; 65K pts/hr rate limit; Rovo GA; Teamwork Graph EAP |
| R2: Python Ecosystem | 22 (14 primary) | High | Adapter architecture sound; Rovo MCP strategic; no library migration needed |
| R3: Value Map | 19 (7 primary) | High | 6 business cases; "aha moment" defined; no Marketplace competitor |
| R4: Forge Deep-Dive | 35 (22 primary) | High | 3-week MVP feasible; Rovo-only UI; no sandbox restrictions |

### Key ADRs

| ADR | Decision | Status |
|-----|----------|--------|
| ADR-033 | Parallel version branching | Accepted |
| ADR-034 | Rovo-only UI for Forge MVP | Proposed |
| ADR-035 | raise-server as canonical knowledge store | Proposed |
| ADR-036 | Async queue consumer for backend calls | Proposed |
| ADR-037 | Capabilities → Compass, Initiatives → Jira | Proposed |

### Known Gaps (30 total, from S760.7)

| Priority | Count | Scope |
|----------|-------|-------|
| P1 | 13 | Required for idiomatic model |
| P2 | 11 | Full stack integration |
| P3 | 6 | Nice to have |

Gaps are grouped into 6 proposed implementation epics (see S760.7).

### Open Questions (5)

1. Does current Atlassian plan include Compass with scorecards?
2. Are historical Jira Component assignments preserved after Compass switch?
3. Should raise-server / raise-forge be Compass components?
4. Which Jira Automation plan tier is available?
5. Timeline for Teamwork Graph GA (strategic but not blocking)

---

## 13. Design Documents Index

| Document | Story | Confluence |
|----------|-------|-----------|
| Research R1-R4 | S760.1 | Published under RAISE-760 |
| Taxonomy & Product Responsibility | S760.2 | Published |
| Workflow, Automation & Lifecycle | S760.3 | Published |
| Confluence Information Architecture | S760.4 | Published |
| Compass Capability Catalog | S760.5 | Published |
| Bitbucket Integration | S760.6 | Published |
| Adapter Gap Analysis | S760.7 | Published |
| This Blueprint | S760.8 | Published |

---

*RaiSE on Atlassian — Reference Blueprint v1.0*
*RAISE-760 — RaiSE Project Management Model*
*March 2026*
