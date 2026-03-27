# S760.5: Compass Capability Catalog Design

**Epic:** RAISE-760
**Story:** S760.5
**Date:** 2026-03-27
**Status:** Draft
**ADR:** ADR-037 (Capabilities en Compass, Initiatives en Jira)

---

## 1. Overview

This document defines how RaiSE's 12 capabilities (C1-C12) map to Atlassian Compass
components, including component definitions, scorecards, dependency graph, DORA metrics
integration, Jira linking model, and migration plan.

**Design principle:** Compass is the software catalog; Jira is the work tracker. A Compass
component represents a permanent technical competency area. Jira issues (Epics, Stories)
represent bounded work that touches those competency areas. The two products integrate
natively -- an Epic links to the Compass component it affects.

---

## 2. Component Definitions

### 2.1 Component Type Rationale

Compass supports these component types: Service, Library, Website, Dataset, Dashboard,
Data Product, Capability, Cloud Resource, Data Pipeline, ML Model, UI Element, Other.

For RaiSE capabilities, we use **Service** for independently deployable units and
**Library** for shared code packages. The rationale:

- **Service**: Has its own deployment, runtime, or operational lifecycle (raise-server,
  rai-agent daemon, CI/CD pipelines).
- **Library**: Consumed as a dependency by other components, no independent deployment
  (raise-core, raise-cli, raise-pro packages).
- **Other**: Cross-cutting concerns that are neither services nor libraries (security,
  portfolio management, self-improvement).

### 2.2 Tier Rationale

Compass supports tiers for Service components. We extend the tiering concept to all
components for prioritization:

- **Tier 1 (Critical):** Failure directly blocks all development. Core engine and runtime.
- **Tier 2 (Important):** Failure degrades developer experience or blocks specific workflows.
- **Tier 3 (Supporting):** Failure has limited blast radius; workarounds exist.

### 2.3 The 12 Compass Components

#### C1: Skill Engine (`raise-skill-engine`)

| Field | Value |
|-------|-------|
| **Name** | `raise-skill-engine` |
| **Display Name** | Skill Engine |
| **Component Type** | Library |
| **Jira Issue** | RAISE-795 |
| **Description** | Define, execute, validate, and evolve skills. The core prompt orchestration system that powers all RaiSE workflows -- skill loading, lifecycle hooks, validation gates, and skill composition. Lives in `raise-cli/skills` and `raise-cli/skills_base`. |
| **Owner** | RaiSE Core Team |
| **Lifecycle** | Active |
| **Tier** | Tier 1 (Critical) |
| **Package** | `raise-cli` (engines, skills, skills_base modules) |
| **Links** | Repo: raise-commons, Docs: Confluence Skill Engine page, Epics: RAISE-301 (skills), RAISE-789 (context/harness) |

#### C2: Adapter Layer (`raise-adapter-layer`)

| Field | Value |
|-------|-------|
| **Name** | `raise-adapter-layer` |
| **Display Name** | Adapter Layer |
| **Component Type** | Library |
| **Jira Issue** | RAISE-796 |
| **Description** | Pluggable integration with external systems (Jira, Confluence, Git, Bitbucket). Protocol-based architecture with concrete adapters for each backend. Lives in `raise-cli/adapters`. |
| **Owner** | RaiSE Core Team |
| **Lifecycle** | Active |
| **Tier** | Tier 1 (Critical) |
| **Package** | `raise-cli` (adapters module), `raise-pro` (Jira/Confluence adapters) |
| **Links** | Repo: raise-commons, Epics: RAISE-760 (Atlassian model), RAISE-819 (Forge) |

#### C3: Session & Workstream (`raise-session-workstream`)

| Field | Value |
|-------|-------|
| **Name** | `raise-session-workstream` |
| **Display Name** | Session & Workstream |
| **Component Type** | Library |
| **Jira Issue** | RAISE-804 |
| **Description** | Maintain context across sessions and enable parallel work. Session lifecycle (start, close, journal), context bundling, workstream isolation. Lives in `raise-cli/session` and `raise-cli/context`. |
| **Owner** | RaiSE Core Team |
| **Lifecycle** | Active |
| **Tier** | Tier 2 (Important) |
| **Package** | `raise-cli` (session, context modules) |
| **Links** | Repo: raise-commons, Epics: RAISE-789 (context patterns) |

#### C4: CLI & Developer Experience (`raise-cli-dx`)

| Field | Value |
|-------|-------|
| **Name** | `raise-cli-dx` |
| **Display Name** | CLI & Developer Experience |
| **Component Type** | Library |
| **Jira Issue** | RAISE-802 |
| **Description** | Clean, documented, adoptable CLI and onboarding. The `rai` command-line interface, output formatting, onboarding flow, doctor diagnostics, and developer ergonomics. Lives in `raise-cli/cli`, `raise-cli/onboarding`, `raise-cli/output`, `raise-cli/doctor`. |
| **Owner** | RaiSE Core Team |
| **Lifecycle** | Active |
| **Tier** | Tier 1 (Critical) |
| **Package** | `raise-cli` (cli, onboarding, output, doctor, viz modules) |
| **Links** | Repo: raise-commons |

#### C5: CI/CD & Release (`raise-cicd-release`)

| Field | Value |
|-------|-------|
| **Name** | `raise-cicd-release` |
| **Display Name** | CI/CD & Release |
| **Component Type** | Service |
| **Jira Issue** | RAISE-798 |
| **Description** | Publish, version, and distribute software reliably. Release gates, version bumping, changelog management, PyPI publishing, GitHub Actions pipelines. Lives in `raise-cli/publish`, `raise-cli/gates`, and `.github/workflows/`. |
| **Owner** | RaiSE Core Team |
| **Lifecycle** | Active |
| **Tier** | Tier 2 (Important) |
| **Package** | `raise-cli` (publish, gates modules), GitHub Actions workflows |
| **Links** | Repo: raise-commons, ADR-033 (branching) |

#### C6: Security & Compliance (`raise-security-compliance`)

| Field | Value |
|-------|-------|
| **Name** | `raise-security-compliance` |
| **Display Name** | Security & Compliance |
| **Component Type** | Other |
| **Jira Issue** | RAISE-803 |
| **Description** | Meet security standards and compliance requirements. License validation, tier enforcement, secret management, compliance checks. Lives in `raise-cli/compliance`, `raise-cli/tier`, `raise-pro` (licensing). |
| **Owner** | RaiSE Core Team |
| **Lifecycle** | Active |
| **Tier** | Tier 2 (Important) |
| **Package** | `raise-cli` (compliance, tier modules), `raise-pro` (licensing) |
| **Links** | Repo: raise-commons |

#### C7: RaiSE PRO (`raise-pro`)

| Field | Value |
|-------|-------|
| **Name** | `raise-pro` |
| **Display Name** | RaiSE PRO |
| **Component Type** | Library |
| **Jira Issue** | RAISE-805 |
| **Description** | Commercial tier: licensing, distribution, Forge integration, Atlassian adapters (Jira, Confluence), trial management. The `raise-pro` package that extends `raise-cli` with commercial features. |
| **Owner** | RaiSE Core Team |
| **Lifecycle** | Active |
| **Tier** | Tier 2 (Important) |
| **Package** | `raise-pro` |
| **Links** | Repo: raise-commons, Epics: RAISE-819 (Forge MVP) |

#### C8: rai-agent Runtime (`rai-agent-runtime`)

| Field | Value |
|-------|-------|
| **Name** | `rai-agent-runtime` |
| **Display Name** | rai-agent Runtime |
| **Component Type** | Service |
| **Jira Issue** | RAISE-800 |
| **Description** | Autonomous agent operation: daemon process, communication channels, delegation framework, event system. The `rai-agent` package that runs as a persistent service. |
| **Owner** | RaiSE Core Team |
| **Lifecycle** | Pre-release |
| **Tier** | Tier 2 (Important) |
| **Package** | `rai-agent` |
| **Links** | Repo: raise-commons |

#### C9: rai-agent Operations (`rai-agent-ops`)

| Field | Value |
|-------|-------|
| **Name** | `rai-agent-ops` |
| **Display Name** | rai-agent Operations |
| **Component Type** | Service |
| **Jira Issue** | RAISE-797 |
| **Description** | Deploy and operate the agent in production. Container orchestration (Docker), health monitoring, log management, scaling configuration. Dockerfiles and deployment manifests. |
| **Owner** | RaiSE Core Team |
| **Lifecycle** | Pre-release |
| **Tier** | Tier 3 (Supporting) |
| **Package** | `rai-agent` (Dockerfile, deployment configs) |
| **Links** | Repo: raise-commons |

#### C10: SAFe & Portfolio Management (`raise-portfolio-mgmt`)

| Field | Value |
|-------|-------|
| **Name** | `raise-portfolio-mgmt` |
| **Display Name** | SAFe & Portfolio Management |
| **Component Type** | Other |
| **Jira Issue** | RAISE-799 |
| **Description** | SAFe practices, portfolio kanban, ITSM lifecycle alignment. The conceptual framework and tooling for scaling RaiSE governance to enterprise portfolio management. Cross-cutting concern spanning Jira configuration and Compass catalog structure. |
| **Owner** | RaiSE Core Team |
| **Lifecycle** | Pre-release |
| **Tier** | Tier 3 (Supporting) |
| **Package** | Governance artifacts, Jira/Compass configuration |
| **Links** | Repo: raise-commons, Epics: RAISE-760 (Atlassian model) |

#### C11: Memory & Knowledge (`raise-memory-knowledge`)

| Field | Value |
|-------|-------|
| **Name** | `raise-memory-knowledge` |
| **Display Name** | Memory & Knowledge |
| **Component Type** | Library |
| **Jira Issue** | RAISE-801 |
| **Description** | Learn, remember, and structure knowledge with pluggable backends. Knowledge graph (raise-core/graph), memory management (raise-cli/memory), pattern registry, calibration data, graph build/query/sync. |
| **Owner** | RaiSE Core Team |
| **Lifecycle** | Active |
| **Tier** | Tier 1 (Critical) |
| **Package** | `raise-core` (graph module), `raise-cli` (memory, graph modules) |
| **Links** | Repo: raise-commons, Epics: RAISE-275 (graph server) |

#### C12: Self-Improvement (`raise-self-improvement`)

| Field | Value |
|-------|-------|
| **Name** | `raise-self-improvement` |
| **Display Name** | Self-Improvement |
| **Component Type** | Other |
| **Jira Issue** | RAISE-815 |
| **Description** | Autonomous detection, research, and adoption of best practices. Evidence-based evolution with HITL approval gates. Jiritsu Kaizen codified. Owns the research process and gap analysis pipelines, not the implementation in other capabilities. |
| **Owner** | RaiSE Core Team |
| **Lifecycle** | Pre-release |
| **Tier** | Tier 3 (Supporting) |
| **Package** | Research artifacts, pattern registry, `/rai-research` skill |
| **Links** | Repo: raise-commons |

### 2.4 Summary Table

| # | Compass Name | Display Name | Type | Tier | Lifecycle | Package(s) |
|---|-------------|-------------|------|------|-----------|------------|
| C1 | `raise-skill-engine` | Skill Engine | Library | 1 | Active | raise-cli |
| C2 | `raise-adapter-layer` | Adapter Layer | Library | 1 | Active | raise-cli, raise-pro |
| C3 | `raise-session-workstream` | Session & Workstream | Library | 2 | Active | raise-cli |
| C4 | `raise-cli-dx` | CLI & Developer Experience | Library | 1 | Active | raise-cli |
| C5 | `raise-cicd-release` | CI/CD & Release | Service | 2 | Active | raise-cli, GitHub Actions |
| C6 | `raise-security-compliance` | Security & Compliance | Other | 2 | Active | raise-cli, raise-pro |
| C7 | `raise-pro` | RaiSE PRO | Library | 2 | Active | raise-pro |
| C8 | `rai-agent-runtime` | rai-agent Runtime | Service | 2 | Pre-release | rai-agent |
| C9 | `rai-agent-ops` | rai-agent Operations | Service | 3 | Pre-release | rai-agent |
| C10 | `raise-portfolio-mgmt` | SAFe & Portfolio Mgmt | Other | 3 | Pre-release | Governance |
| C11 | `raise-memory-knowledge` | Memory & Knowledge | Library | 1 | Active | raise-core, raise-cli |
| C12 | `raise-self-improvement` | Self-Improvement | Other | 3 | Pre-release | Research |

---

## 3. Scorecard Design

### 3.1 Scorecard Strategy

Compass supports scorecards with weighted criteria that evaluate component health.
Scorecards can be applied by component type and tier, enabling differentiated standards
for critical vs. supporting capabilities.

We define three scorecards:

1. **Component Readiness** -- Is this capability production-ready?
2. **DevOps Health** -- Does this capability follow healthy engineering practices?
3. **Governance Compliance** -- Does this capability meet RaiSE governance standards?

### 3.2 Scorecard 1: Component Readiness

**Applies to:** All components (all types, all tiers)
**Purpose:** Ensure every capability has the minimum metadata and ownership for production use.

| Criterion | Type | Weight | Passing Condition | Automated? |
|-----------|------|--------|-------------------|------------|
| Has owner team assigned | Field check | 20% | Owner field is not empty | Yes (Compass native) |
| Has description | Field check | 10% | Description field is not empty | Yes (Compass native) |
| Has documentation link | Link regex | 15% | At least one link of type "Documentation" matching `https://.*atlassian.net/wiki/.*\|https://raise.dev/docs/.*` | Yes (Compass regex criterion) |
| Has repository link | Link regex | 15% | At least one link of type "Repository" matching `https://github.com/.*raise.*` | Yes (Compass regex criterion) |
| Lifecycle is set | Field check | 10% | Lifecycle is not empty | Yes (Compass native) |
| Has on-call or support contact | Link regex | 10% | At least one link of type "On-call" or "Chat channel" | Yes (Compass regex criterion) |
| Has at least one dependency defined | Custom field | 10% | Dependency count > 0 (except for `raise-memory-knowledge` which is the root) | Manual review |
| Tier is assigned | Field check | 10% | Tier field is set (for Service types; custom field for others) | Yes (Compass native for Services) |

**Passing threshold:** 80% weighted score = Healthy. Below 60% = Needs Attention.

### 3.3 Scorecard 2: DevOps Health

**Applies to:** Library and Service components (Tier 1 and Tier 2)
**Purpose:** Measure engineering practices that correlate with high-performing teams.

| Criterion | Type | Weight | Passing Condition | Automated? |
|-----------|------|--------|-------------------|------------|
| Test coverage >= 80% | Metric threshold | 25% | `test_coverage` metric >= 80 | Yes (via Forge data provider from CI) |
| Deployment frequency | DORA metric | 20% | `deployment_frequency` >= 1 per week (for Active components) | Yes (derived from CI events) |
| Change failure rate < 15% | DORA metric | 20% | `change_failure_rate` < 15% | Yes (derived from bug/hotfix data) |
| Lead time for changes < 7 days | DORA metric | 20% | `lead_time_for_changes` < 7 days | Yes (derived from story lifecycle) |
| Has CI pipeline | Link regex | 15% | At least one link matching `https://github.com/.*/actions.*` | Yes (Compass regex criterion) |

**Passing threshold:** 70% weighted score = Healthy. Below 50% = Needs Attention.

**Note:** DORA metrics require the Forge data provider to be operational (post-RAISE-819).
Until then, these criteria will show as "No data" rather than failing.

### 3.4 Scorecard 3: Governance Compliance

**Applies to:** All Active components (all types)
**Purpose:** Ensure capabilities meet RaiSE governance standards.

| Criterion | Type | Weight | Passing Condition | Automated? |
|-----------|------|--------|-------------------|------------|
| Has ADR for key decisions | Custom field (checkbox) | 25% | `has_adrs` checkbox is checked | Manual (set during epic review) |
| Architecture doc exists | Link regex | 25% | Documentation link to Confluence architecture page exists | Yes (Compass regex criterion) |
| Code standards compliance | Metric threshold | 25% | `governance_score` metric >= 90 (from `rai gate check`) | Yes (via Forge data provider) |
| Type annotations complete | Metric threshold | 25% | `type_coverage` metric >= 95 (from pyright) | Yes (via Forge data provider from CI) |

**Passing threshold:** 75% weighted score = Healthy. Below 50% = Needs Attention.

### 3.5 Scorecard Application Matrix

| Scorecard | Tier 1 | Tier 2 | Tier 3 |
|-----------|--------|--------|--------|
| Component Readiness | Required | Required | Required |
| DevOps Health | Required | Required | Optional |
| Governance Compliance | Required | Required | Optional |

---

## 4. Dependency Graph

### 4.1 Package-Level Dependencies (from pyproject.toml)

The monorepo has a clear dependency chain:

```
raise-core (foundation -- no internal dependencies)
    ^
    |
raise-cli (depends on raise-core)
    ^
    |
raise-pro (depends on raise-cli)
    ^
    |
rai-agent (depends on raise-core + raise-cli)

raise-server (independent -- no internal package dependencies)
```

### 4.2 Capability Dependency Map

Dependencies represent "depends on" relationships -- the source capability requires
the target capability to function.

```
C12: Self-Improvement
  |
  +--depends-on--> C11: Memory & Knowledge
  +--depends-on--> C1: Skill Engine

C10: SAFe & Portfolio Mgmt
  |
  +--depends-on--> C2: Adapter Layer
  +--depends-on--> C4: CLI & DX

C9: rai-agent Operations
  |
  +--depends-on--> C8: rai-agent Runtime
  +--depends-on--> C5: CI/CD & Release

C8: rai-agent Runtime
  |
  +--depends-on--> C1: Skill Engine
  +--depends-on--> C3: Session & Workstream
  +--depends-on--> C11: Memory & Knowledge

C7: RaiSE PRO
  |
  +--depends-on--> C2: Adapter Layer
  +--depends-on--> C4: CLI & DX
  +--depends-on--> C6: Security & Compliance

C6: Security & Compliance
  |
  +--depends-on--> C4: CLI & DX

C5: CI/CD & Release
  |
  +--depends-on--> C4: CLI & DX

C4: CLI & DX
  |
  +--depends-on--> C11: Memory & Knowledge
  +--depends-on--> C1: Skill Engine

C3: Session & Workstream
  |
  +--depends-on--> C11: Memory & Knowledge
  +--depends-on--> C1: Skill Engine

C2: Adapter Layer
  |
  +--depends-on--> C4: CLI & DX

C1: Skill Engine
  |
  +--depends-on--> C11: Memory & Knowledge

C11: Memory & Knowledge
  |
  (root -- depends on raise-core graph, no capability dependencies)
```

### 4.3 Critical Path

The critical path flows upward from the foundation:

```
C11 Memory & Knowledge  (foundation -- graph, patterns, calibration)
         |
         v
C1  Skill Engine         (core orchestration -- everything uses skills)
         |
    +----+----+
    v         v
C3 Session  C4 CLI & DX  (user-facing layers)
    |         |
    v    +----+----+----+
C8 Agent C2  C5   C6    (integration, delivery, security)
Runtime  Adapter CI/CD  Compliance
    |         |
    v         v
C9 Agent  C7 PRO        (deployment, commercial)
Operations
```

**Blast radius analysis:**
- C11 failure: All capabilities degraded (no graph, no memory)
- C1 failure: All skill-based workflows blocked (most of RaiSE)
- C4 failure: CLI unusable, blocks C2, C5, C6, C7
- C2 failure: External integrations blocked (Jira, Confluence, Git)

### 4.4 Compass Dependency Configuration

Each dependency is registered in Compass as a "Depends on" relationship:

| Source Component | Depends On | Direction |
|-----------------|------------|-----------|
| `raise-skill-engine` | `raise-memory-knowledge` | Horizontal |
| `raise-adapter-layer` | `raise-cli-dx` | Horizontal |
| `raise-session-workstream` | `raise-memory-knowledge`, `raise-skill-engine` | Horizontal |
| `raise-cli-dx` | `raise-memory-knowledge`, `raise-skill-engine` | Horizontal |
| `raise-cicd-release` | `raise-cli-dx` | Horizontal |
| `raise-security-compliance` | `raise-cli-dx` | Horizontal |
| `raise-pro` | `raise-adapter-layer`, `raise-cli-dx`, `raise-security-compliance` | Horizontal |
| `rai-agent-runtime` | `raise-skill-engine`, `raise-session-workstream`, `raise-memory-knowledge` | Horizontal |
| `rai-agent-ops` | `rai-agent-runtime`, `raise-cicd-release` | Horizontal |
| `raise-portfolio-mgmt` | `raise-adapter-layer`, `raise-cli-dx` | Horizontal |
| `raise-self-improvement` | `raise-memory-knowledge`, `raise-skill-engine` | Horizontal |

**Constraint note:** Compass allows max 25 outbound dependencies per component. Our max
is 3 per component, well within limits.

---

## 5. DORA Metrics Mapping

### 5.1 The Four DORA Metrics

| DORA Metric | Definition | RaiSE Data Source | Compass Metric |
|-------------|-----------|-------------------|----------------|
| **Deployment Frequency** | How often code is deployed to production | GitHub Actions release workflow completions per component | `deployment_frequency` (derived from deployment events) |
| **Lead Time for Changes** | Time from commit to production | Story start (Jira transition to In Progress) to release tag containing the story's commits | `lead_time_for_changes` (derived from deployment + commit events) |
| **Change Failure Rate** | % of deployments causing failures | Bug issues created with `fixVersion` matching a release / total releases | `change_failure_rate` (custom metric via Forge) |
| **Mean Time to Recovery** | Time from failure detection to fix | Bug created timestamp to Bug resolved timestamp (Jira) | `time_to_restore_service` (custom metric via Forge) |

### 5.2 Data Flow Architecture

```
GitHub Actions (CI/CD)          Jira (Work Tracking)
  |                               |
  | deployment events             | issue transitions
  | test coverage reports         | bug lifecycle
  | build status                  | story lifecycle
  |                               |
  v                               v
raise-server (Telemetry API)    raise-server (Telemetry API)
  |                               |
  | /telemetry/events             | /telemetry/events
  |                               |
  +----------- merge ------------+
                |
                v
        Forge App (Data Provider)
                |
                | compass:dataProvider module
                | insertMetricValueByExternalId()
                |
                v
        Compass (Metric Storage)
                |
                | Derived + custom metrics
                | per component
                |
                v
        Compass Scorecards
                |
                | DevOps Health scorecard
                | evaluates metric thresholds
                |
                v
        Component Health Dashboard
```

### 5.3 Metric Provider Implementation (Forge)

The Forge app (RAISE-819) includes a `compass:dataProvider` module that:

1. **Listens to events** from raise-server via scheduled Forge async functions
2. **Transforms events** into Compass metric format
3. **Pushes metrics** using the Forge GraphQL Toolkit:
   - `insertMetricValueByExternalId()` for custom metrics
   - Deployment events automatically derive DORA metrics

**Event types to push:**

| Event Type | Source | Compass Metric | Frequency |
|------------|--------|----------------|-----------|
| `deployment.completed` | GitHub Actions webhook -> raise-server | Deployment Frequency, Lead Time | Per release |
| `build.completed` | GitHub Actions webhook -> raise-server | Build success rate | Per commit |
| `test.coverage` | CI pipeline -> raise-server | Test coverage % | Per commit |
| `bug.created` | Jira webhook -> raise-server | Change Failure Rate input | Per bug |
| `bug.resolved` | Jira webhook -> raise-server | MTTR input | Per bug resolution |
| `story.completed` | `rai backlog transition` -> raise-server | Lead Time input | Per story |
| `gate.check` | `rai gate check` -> raise-server | Governance score | Per gate run |

### 5.4 Pre-Forge Interim Approach

Before the Forge data provider is operational (pre-RAISE-819):

1. **Manual metric updates** via Compass REST API v2 (`POST /gateway/api/compass/v2/metrics`)
   using OAuth 2.0 authentication
2. **Scripted collection** from GitHub Actions API and Jira JQL queries
3. **Frequency:** Weekly batch update via scheduled script

This provides baseline DORA visibility without Forge dependency.

---

## 6. Jira <-> Compass Integration

### 6.1 Linking Model

Compass components replace Jira Components for the RAISE project. This is a one-time
switch (per Atlassian docs, a project cannot use both Jira and Compass components
simultaneously).

**After the switch:**

- The Jira `component` field on issues points to Compass components
- Jira's project Components page shows Compass component data
- Each Compass component's Issues page shows linked Jira issues

### 6.2 Epic -> Compass Component Linking

Every Epic MUST have exactly one Compass component assigned via the `component` field.
This enables:

```sql
-- All epics touching the Adapter Layer
component = "raise-adapter-layer" AND issuetype = Epic

-- All open stories for Memory & Knowledge
component = "raise-memory-knowledge" AND issuetype = Story AND status != Done

-- All bugs in Tier 1 capabilities (requires JQL with component list)
component in ("raise-skill-engine", "raise-adapter-layer", "raise-cli-dx",
              "raise-memory-knowledge") AND issuetype = Bug AND status != Done
```

### 6.3 Cross-Cutting Epics

Some epics touch multiple capabilities (e.g., RAISE-760 touches C2, C4, C7, C10).
Policy:

- Assign the **primary** capability -- the one most affected
- Use **Jira issue links** (type: "relates to") to reference other affected capabilities
  in their Compass component pages
- The Compass dependency graph makes cross-cutting impact visible

### 6.4 Development Panel Integration

When Compass components are active, Jira's development panel on issues shows:

- **Component health:** Scorecard summary for the linked component
- **Dependencies:** Which other components might be affected
- **Recent deployments:** From Compass deployment events

This gives developers context about the component they are touching without leaving Jira.

### 6.5 Automation Opportunities

| Trigger | Condition | Action | Value |
|---------|-----------|--------|-------|
| Epic transitions to Done | Epic has Compass component | Update Compass component custom field: `last_epic_completed` | Track activity per capability |
| Bug created with Tier 1 component | Component tier = 1 | Send notification to component owner | Fast response for critical capabilities |
| Story transitions to Done | Story has Compass component | Push `story.completed` event to raise-server | Feed DORA Lead Time metric |
| New Epic created | Always | Require Compass component field | Ensure every epic is classified |
| Scorecard drops below threshold | Component health < 60% | Create Jira Task: "Improve {component} health" | Automated health maintenance |

### 6.6 Querying "All Epics Touching Adapter Layer"

**From Jira (JQL):**
```sql
component = "raise-adapter-layer" AND issuetype = Epic ORDER BY created DESC
```

**From Compass (UI):**
Navigate to `raise-adapter-layer` component -> Issues tab -> filter by Epic type

**From Compass (GraphQL API via Forge):**
```graphql
query {
  compass {
    component(id: "<adapter-layer-component-id>") {
      name
      relationships(type: DEPENDS_ON) {
        nodes { name }
      }
    }
  }
}
```

**From raise-server (via Forge data provider):**
The Forge app can query both Compass GraphQL and Jira REST API to build cross-product
reports.

---

## 7. Migration Plan

### Phase 0: Preparation (Current -- RAISE-760)

| Step | Action | Owner | Status |
|------|--------|-------|--------|
| 0.1 | Document all 12 component definitions (this document) | Rai | Done |
| 0.2 | Define scorecards and criteria | Rai | Done |
| 0.3 | Map dependency graph | Rai | Done |
| 0.4 | Design DORA metric data flow | Rai | Done |
| 0.5 | Get ADR-037 accepted | Emilio | Proposed |

### Phase 1: Compass Setup (Post-RAISE-760, Pre-RAISE-819)

| Step | Action | Owner | Estimate |
|------|--------|-------|----------|
| 1.1 | Enable Compass for the Atlassian site (if not already active) | Emilio | 15 min |
| 1.2 | Switch RAISE project from Jira Components to Compass Components | Emilio | 30 min |
| 1.3 | Create 12 Compass components from definitions in Section 2 | Rai (scripted) | 1 hour |
| 1.4 | Set lifecycle, tier, owner, and description for each component | Rai (scripted) | 30 min |
| 1.5 | Add repository, documentation, and support links to each component | Rai | 1 hour |
| 1.6 | Register dependencies from Section 4.4 | Rai | 30 min |

**Scripting approach:** Use Compass REST API v2 to create components programmatically.
A Python script using `requests` + OAuth 2.0 can automate steps 1.3-1.6. Alternatively,
use Compass CSV import for bulk creation.

### Phase 2: Scorecard Activation (After Phase 1)

| Step | Action | Owner | Estimate |
|------|--------|-------|----------|
| 2.1 | Create "Component Readiness" scorecard | Emilio | 30 min |
| 2.2 | Create "Governance Compliance" scorecard | Emilio | 30 min |
| 2.3 | Apply scorecards to all components | Emilio | 15 min |
| 2.4 | Review initial scores and fix gaps (add missing links, descriptions) | Rai | 2 hours |
| 2.5 | Create "DevOps Health" scorecard (initially without DORA -- metrics show "No data") | Emilio | 30 min |

### Phase 3: Jira Re-linking (After Phase 1)

| Step | Action | Owner | Estimate |
|------|--------|-------|----------|
| 3.1 | Assign Compass components to all open Epics | Rai (scripted via Jira API) | 1 hour |
| 3.2 | Assign Compass components to all open Stories and Bugs | Rai (scripted via Jira API) | 1 hour |
| 3.3 | Verify JQL queries from Section 6.2 return expected results | Rai | 30 min |
| 3.4 | Update board filters if needed for Compass component field | Emilio | 15 min |

### Phase 4: Jira Cleanup (After Phase 3)

| Step | Action | Owner | Estimate |
|------|--------|-------|----------|
| 4.1 | Archive Capability issues RAISE-795 through RAISE-815 (transition to Done with note) | Rai | 30 min |
| 4.2 | Add comment to each archived issue: "Migrated to Compass component: {name}" | Rai (scripted) | 15 min |
| 4.3 | Consider retiring Capability as Jira issue type (after validation period of 2 weeks) | Emilio | Decision |

### Phase 5: DORA Metrics (After RAISE-819 Forge MVP)

| Step | Action | Owner | Estimate |
|------|--------|-------|----------|
| 5.1 | Implement `compass:dataProvider` module in Forge app | Rai | Story |
| 5.2 | Configure raise-server telemetry endpoints for CI/CD events | Rai | Story |
| 5.3 | Set up GitHub Actions webhooks to raise-server | Rai | Story |
| 5.4 | Validate DORA metrics appear on Compass components | Rai + Emilio | 1 hour |
| 5.5 | Activate DevOps Health scorecard metric criteria (previously "No data") | Emilio | 15 min |

### Migration Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Compass requires Premium plan feature | Medium | Medium | Verify plan features before Phase 1. Degrade to Jira Components + labels if needed |
| Switching from Jira to Compass Components breaks existing board filters | Low | Low | Test in staging first. Board filters use `component =` which works with both |
| DORA metrics inaccurate initially | High | Low | Accept "No data" for first 2 weeks. Validate with manual spot checks |
| Team members unfamiliar with Compass UI | Low | Low | Single developer today. Add Compass walkthrough to onboarding when team grows |

---

## 8. Config-as-Code (compass.yml)

Compass supports managing components via YAML files in the repository. This aligns with
RaiSE's "governance as code" principle.

### 8.1 Example compass.yml for raise-skill-engine

```yaml
# compass.yml — stored in repository root or packages/raise-cli/
name: raise-skill-engine
id: ari:cloud:compass:<site-id>:component/<uuid>  # assigned after creation
description: >
  Define, execute, validate, and evolve skills. The core prompt orchestration
  system that powers all RaiSE workflows.
ownerId: ari:cloud:teams:<site-id>:team/<team-uuid>
fields:
  tier: 1
  lifecycle: Active
typeId: LIBRARY
links:
  - name: Repository
    type: REPOSITORY
    url: https://github.com/humansys-io/raise-commons
  - name: Documentation
    type: DOCUMENT
    url: https://humansys.atlassian.net/wiki/spaces/RaiSE1/pages/<page-id>
  - name: CI Pipeline
    type: OTHER_LINK
    url: https://github.com/humansys-io/raise-commons/actions
relationships:
  DEPENDS_ON:
    - raise-memory-knowledge
```

### 8.2 Config-as-Code Considerations

- Requires Bitbucket, GitHub, or GitLab integration configured in Compass
- Changes to compass.yml are automatically synced on push
- Good for ensuring component definitions stay in sync with code
- **Recommendation:** Adopt config-as-code in Phase 2 after manual setup is validated

---

## 9. Open Questions

| # | Question | Impact | Resolution Path |
|---|----------|--------|-----------------|
| 1 | Does the current Atlassian plan include Compass with scorecards? | Blocks Phase 1 | Verify in Atlassian admin panel |
| 2 | Can we use Compass Components and still retain existing Jira Component assignments on historical (Done) issues? | Data preservation | Test the Jira-to-Compass component switch behavior |
| 3 | Should `raise-server` be a 13th Compass component? | Catalog completeness | raise-server is an independent deployment. Defer: add when raise-server has its own epic/story flow |
| 4 | How to handle the Forge app itself as a component? | Catalog completeness | `raise-forge` is already in the Jira component plan (taxonomy-design.md). Add to Compass when the package exists (post-RAISE-819) |

---

## 10. References

- [ADR-037: Capabilities en Compass, Initiatives en Jira](../../dev/decisions/adr-037-capability-compass-initiative-jira.md)
- [S760.2: Taxonomy Design](./taxonomy-design.md)
- [R1: Atlassian API Landscape](./research/R1-atlassian-api-landscape.md) -- Compass API details
- [R3: RaiSE <> Atlassian Value Map](./research/R3-raise-atlassian-value-map.md) -- DORA, artifact mapping
- [Compass: Create components](https://support.atlassian.com/compass/docs/create-view-update-and-archive-components/)
- [Compass: Scorecard criteria](https://support.atlassian.com/compass/docs/create-and-manage-scorecard-criteria/)
- [Compass: Dependency mapping](https://support.atlassian.com/compass/docs/add-component-dependencies/)
- [Compass: Metrics with scorecards](https://support.atlassian.com/compass/docs/use-metrics-with-scorecards/)
- [Compass: DORA metrics](https://support.atlassian.com/compass/docs/what-are-derived-metrics/)
- [Compass: Config as code](https://developer.atlassian.com/cloud/compass/config-as-code/manage-components-with-config-as-code/)
- [Compass: Forge data provider](https://developer.atlassian.com/cloud/compass/integrations/create-a-data-provider-app/)
- [Compass: Link Jira issues to components](https://support.atlassian.com/compass/docs/link-jira-issues-to-components/)
- [Jira: Link issues to Compass components](https://support.atlassian.com/jira-software-cloud/docs/link-issues-to-compass-components/)
- [Compass: Component types](https://support.atlassian.com/compass/docs/manage-component-types/)
- [Compass: Scorecard design guide](https://www.atlassian.com/software/compass/guide/design-and-architecture/scorecard-design)
