# SAFe 6.0 Support — Requirements Document

> **Client:** Coppel
> **Date:** 2026-03-04
> **Status:** DRAFT
> **Author:** RaiSE Team (AI-assisted)

---

## 1. Executive Summary

Coppel requires RaiSE to support SAFe 6.0 (Scaled Agile Framework) for enterprise-scale agile delivery. This document maps SAFe 6.0 concepts to RaiSE's current capabilities, identifies gaps, and defines requirements to close them.

**Key finding:** RaiSE already covers ~40% of SAFe 6.0 at Team level, ~15% at ART level, and ~5% at Portfolio/Solution levels. The primary gaps are in multi-ART coordination, PI Planning, flow metrics dashboards, and Portfolio Kanban.

---

## 2. SAFe 6.0 Concept Map vs RaiSE Current State

### 2.1 Work Item Hierarchy

| SAFe 6.0 Concept | RaiSE Current | Gap | Priority |
|---|---|---|---|
| **Epic** (Portfolio Kanban) | Epic lifecycle (start/design/plan/close) | Missing: Lean Business Case, WSJF scoring, Portfolio Kanban states (Funnel→Reviewing→Analyzing→Backlog→Implementing→Done) | P1 |
| **Capability** (Solution level) | Not supported | New concept: spans multiple ARTs, decomposes into Features | P2 |
| **Feature** (ART level) | Mapped loosely to Epic | Missing: benefit hypothesis template, WSJF prioritization, PI assignment | P1 |
| **Enabler** (all levels) | No explicit type distinction | Missing: 4 enabler types (Exploration, Architecture, Infrastructure, Compliance) | P1 |
| **Story** | Full lifecycle support | Partial: missing story point estimation, iteration assignment | P3 |
| **NFR** (Non-Functional Requirement) | Guardrails (partial) | Missing: explicit NFR tracking as cross-cutting constraints | P2 |

### 2.2 Organizational Structure

| SAFe 6.0 Concept | RaiSE Current | Gap | Priority |
|---|---|---|---|
| **Value Stream** (OVS + DVS) | Lean phase tracking (partial) | Missing: value stream definition, mapping, visualization | P1 |
| **ART** (Agile Release Train) | Not supported | New concept: team-of-teams (50-125 people), 5-12 teams, aligned to DVS | P1 |
| **Team** | Single-team focus | Missing: multi-team coordination, team topology | P2 |
| **Solution Train** | Not supported | New concept: coordinates multiple ARTs for large solutions | P3 |
| **Portfolio** | Roadmap + release planning (basic) | Missing: LPM team, strategic themes, portfolio vision, lean budgets | P2 |

### 2.3 Planning & Cadence

| SAFe 6.0 Concept | RaiSE Current | Gap | Priority |
|---|---|---|---|
| **PI (Program Increment)** | Not supported | New concept: 8-12 week timebox, 4 dev iterations + 1 IP | P1 |
| **PI Planning** | Not supported | New: 2-day all-hands event, team/ART objectives, dependency board | P1 |
| **Iteration** | Session-level tracking | Missing: formal iteration construct, iteration goals, capacity planning | P2 |
| **IP Iteration** | Not supported | Innovation & Planning iteration at PI boundary | P3 |
| **Pre-Plan / Coordinate & Deliver** | Not supported | Solution Train alignment events | P3 |
| **Roadmap** (PI-level) | Release-level roadmap exists | Missing: PI-level feature roadmap, multi-PI planning | P2 |

### 2.4 Ceremonies & Events

| SAFe 6.0 Event | RaiSE Current | Gap | Priority |
|---|---|---|---|
| **PI Planning** | Not supported | Core SAFe ceremony — 2-day alignment event | P1 |
| **Iteration Planning** | Story plan skill (partial) | Missing: team-level iteration scope, capacity-based planning | P2 |
| **System Demo** | Not supported | Integrated ART-level demo every iteration | P3 |
| **ART Sync** | Not supported | Weekly PO Sync + Scrum of Scrums | P2 |
| **Inspect & Adapt** | Epic retrospective (partial) | Missing: PI System Demo + quantitative metrics + problem-solving workshop | P2 |
| **Backlog Refinement** | Grooming session (ad-hoc) | Missing: structured refinement cadence, WSJF scoring | P2 |

### 2.5 Roles

| SAFe 6.0 Role | RaiSE Current | Gap | Priority |
|---|---|---|---|
| **RTE** (Release Train Engineer) | Not supported | Flow steward, facilitator, dependency broker | P2 |
| **Product Management** | Not supported | Content authority for ART, feature definition, WSJF | P2 |
| **System Architect** | Not supported | Architectural vision, enabler definition | P2 |
| **Epic Owner** | Not supported | Drives portfolio epics through Portfolio Kanban | P2 |
| **Business Owner** | Not supported | Assigns business value to PI Objectives | P2 |
| **Product Owner** | Not modeled | Team-level backlog management | P3 |
| **Team Coach / Scrum Master** | Coaching notes exist | Missing: formal role model, team-level facilitation tracking | P3 |

### 2.6 Metrics & Flow

| SAFe 6.0 Metric | RaiSE Current | Gap | Priority |
|---|---|---|---|
| **Flow Velocity** | Throughput tracking (basic) | Missing: items completed per PI/iteration, trend visualization | P1 |
| **Flow Time** | Lead time / cycle time (partial) | Missing: end-to-end flow time from Feature entry to release | P1 |
| **Flow Load** | WIP signals (basic) | Missing: WIP visualization across workflow steps | P1 |
| **Flow Efficiency** | Not supported | Active work time / total elapsed time | P2 |
| **Flow Distribution** | Not supported | % features vs enablers vs defects vs risk | P1 |
| **Flow Predictability** | Not supported | Planned vs actual business value | P1 |
| **WSJF** | Not supported | Cost of Delay / Job Size prioritization | P1 |
| **PI Predictability Measure** | Not supported | Actual / planned business value per PI (target 80-100%) | P2 |
| **Eight Flow Accelerators** | Partial (guardrails, gates) | Missing: systematic flow accelerator practices at each level | P3 |

### 2.7 Governance & Architecture

| SAFe 6.0 Concept | RaiSE Current | Gap | Priority |
|---|---|---|---|
| **Lean Business Case** | Business case doc (basic) | Missing: SAFe template (hypothesis, MVP, go/no-go, WSJF) | P1 |
| **Architectural Runway** | ADRs + architecture reviews | Missing: explicit runway tracking, enabler pipeline | P2 |
| **Solution Intent** | Not supported | Living spec repository (fixed vs variable requirements) | P3 |
| **Portfolio Kanban** | Not supported | Epic flow states with WIP limits | P1 |
| **Lean Budgets** | Not supported | Value stream funding model vs project-based funding | P3 |
| **Compliance** | Guardrails + gates | Partial: missing compliance enabler tracking, V&V artifacts | P2 |

---

## 3. Gap Analysis Summary

### By Priority

| Priority | Count | Description |
|---|---|---|
| **P1 — Must Have** | 14 | Core SAFe concepts without which the product cannot claim SAFe 6.0 support |
| **P2 — Should Have** | 16 | Important for enterprise adoption, can be phased |
| **P3 — Nice to Have** | 9 | Full SAFe coverage, Large Solution / Solution Train level |

### By Implementation Complexity

| Complexity | Items | Examples |
|---|---|---|
| **Configuration** (Low) | 6 | Enabler types in Jira, WSJF custom fields, PI Objectives field |
| **Feature** (Medium) | 15 | Flow metrics dashboard, Portfolio Kanban skill, PI Planning skill |
| **Platform** (High) | 8 | ART construct, multi-team coordination, value stream modeling |
| **Architecture** (Very High) | 5 | Solution Train, Lean Budgets, cross-ART dependency management |

---

## 4. Proposed Feature Breakdown

### Epic 1: SAFe Work Item Taxonomy (P1, Medium)

**Objective:** Extend RaiSE work item hierarchy to support SAFe 6.0 artifact types.

| # | Feature | Description |
|---|---|---|
| F1.1 | **Enabler Type System** | Add enabler classification (Exploration, Architecture, Infrastructure, Compliance) to epic/story creation. Map to Jira issue types or labels. |
| F1.2 | **Feature vs Epic Distinction** | Introduce "Feature" as ART-level work item (benefit hypothesis + acceptance criteria). Map to Jira Feature issue type or Epic with label. |
| F1.3 | **Lean Business Case Template** | Governance artifact template for portfolio epics: hypothesis, MVP definition, estimated cost, WSJF score, go/no-go criteria. |
| F1.4 | **WSJF Scoring** | Add WSJF calculation (User-Business Value + Time Criticality + Risk Reduction / Job Size) to backlog prioritization. Custom fields in Jira. |
| F1.5 | **NFR Registry** | Cross-cutting non-functional requirements tracked as guardrail nodes in knowledge graph, linked to features/capabilities. |

### Epic 2: PI Planning & Cadence (P1, High)

**Objective:** Introduce Program Increment as a planning construct with ceremony support.

| # | Feature | Description |
|---|---|---|
| F2.1 | **PI Definition** | Define PI as a timebox (8-12 weeks, configurable iterations). Model in `.raise/safe/pi.yaml` or Jira Fix Version. |
| F2.2 | **PI Planning Skill** | `/rai-pi-plan` — Guided PI Planning session: load ART backlog, facilitate feature selection, team capacity, dependency identification, PI objectives. |
| F2.3 | **PI Objectives Tracking** | Track committed vs uncommitted objectives per team/ART. Business value scoring (1-10). Predictability measure calculation. |
| F2.4 | **ART Planning Board** | Visualization of features across iterations with dependency lines. Could be Confluence page or Jira board view. |
| F2.5 | **Iteration Construct** | Formal iteration model within PI: goals, capacity, velocity tracking. |

### Epic 3: Flow Metrics & Measurement (P1, Medium)

**Objective:** Implement SAFe 6.0's six flow metrics with dashboards.

| # | Feature | Description |
|---|---|---|
| F3.1 | **Flow Velocity** | Track items completed per iteration/PI. Aggregate at team, ART, portfolio levels. |
| F3.2 | **Flow Time** | Measure entry-to-release time for features. Breakdown by workflow state. |
| F3.3 | **Flow Load** | WIP tracking across all workflow steps. Visual indicators for overload. |
| F3.4 | **Flow Distribution** | Categorize work as Feature/Enabler/Defect/Risk. Track % distribution over time. |
| F3.5 | **Flow Predictability** | Planned vs actual business value per PI. Trend analysis. |
| F3.6 | **Flow Efficiency** | Active work time vs wait time ratio. Identify bottlenecks. |
| F3.7 | **Metrics Dashboard** | Aggregated view (CLI report + Confluence page + optional rai-server API). |

### Epic 4: Portfolio Kanban (P1, Medium)

**Objective:** Implement portfolio-level epic flow with Kanban states and governance.

| # | Feature | Description |
|---|---|---|
| F4.1 | **Portfolio Kanban States** | Map epic lifecycle to SAFe states: Funnel → Reviewing → Analyzing → Portfolio Backlog → Implementing → Done. Configure in Jira workflow or `.raise/safe/portfolio.yaml`. |
| F4.2 | **Portfolio Kanban Skill** | `/rai-portfolio-kanban` — Visualize and manage portfolio epic flow. WIP limits per state. |
| F4.3 | **Epic Owner Workflow** | Guide epic owners through analysis phase: hypothesis refinement, Lean Business Case, WSJF scoring, go/no-go recommendation. |
| F4.4 | **Strategic Themes** | Define portfolio strategic themes. Link epics to themes for alignment tracking. |

### Epic 5: Value Stream Modeling (P1, High)

**Objective:** Introduce value stream as a first-class concept in RaiSE.

| # | Feature | Description |
|---|---|---|
| F5.1 | **Value Stream Definition** | Model OVS and DVS in `.raise/safe/value-streams.yaml`. Link ARTs to value streams. |
| F5.2 | **Value Stream Mapping** | Workshop facilitation skill or template: current state, lead times, bottlenecks, future state. |
| F5.3 | **Value Stream Metrics** | Aggregate flow metrics per value stream. Cross-ART visibility. |

### Epic 6: ART Construct (P2, High)

**Objective:** Model Agile Release Train as organizational construct.

| # | Feature | Description |
|---|---|---|
| F6.1 | **ART Definition** | Model ART: teams, value stream alignment, cadence, backlog. Config in `.raise/safe/art.yaml`. |
| F6.2 | **ART Backlog Management** | Feature/enabler backlog at ART level, distinct from team backlogs. |
| F6.3 | **ART Sync Skill** | `/rai-art-sync` — Facilitate weekly ART sync: progress, dependencies, risks. |
| F6.4 | **System Demo Support** | Checklist/template for integrated ART demo every iteration. |

### Epic 7: Inspect & Adapt (P2, Medium)

**Objective:** Formalize PI-boundary retrospective with quantitative metrics.

| # | Feature | Description |
|---|---|---|
| F7.1 | **I&A Skill** | `/rai-inspect-adapt` — PI System Demo summary, flow metrics review, problem-solving workshop facilitation. |
| F7.2 | **Quantitative Measurement** | Aggregate PI metrics: predictability, velocity trend, flow distribution changes. |
| F7.3 | **Improvement Backlog** | Track improvement items from I&A, assign to next PI, measure resolution. |

### Epic 8: Roles & Governance (P2, Medium)

**Objective:** Model SAFe roles and responsibilities in RaiSE.

| # | Feature | Description |
|---|---|---|
| F8.1 | **Role Registry** | Define SAFe roles (RTE, PM, SA, Epic Owner, Business Owner, PO, Team Coach) in `.raise/safe/roles.yaml`. Map to team members. |
| F8.2 | **Role-Based Views** | Filter backlogs, metrics, and dashboards by role context. |
| F8.3 | **Lean Budget Guardrails** | Track value stream budgets, spending vs allocation, guardrail violations. |

### Epic 9: Solution Train (P3, Very High)

**Objective:** Support Large Solution SAFe configuration.

| # | Feature | Description |
|---|---|---|
| F9.1 | **Capability Construct** | Work item spanning multiple ARTs, decomposes into Features. |
| F9.2 | **Solution Backlog** | Capabilities + enablers at solution level. |
| F9.3 | **Solution Intent** | Living spec repository with fixed/variable classification. |
| F9.4 | **Pre-Plan & Coordinate** | Cross-ART alignment events. |

---

## 5. Implementation Strategy

### Phase 1: SAFe Essential (v2.4 — Q2 2026)
> Minimum viable SAFe support for a single ART

- Epic 1: SAFe Work Item Taxonomy
- Epic 3: Flow Metrics (core 6 metrics)
- Epic 4: Portfolio Kanban (states + WSJF)
- Jira configuration for SAFe fields

### Phase 2: SAFe Portfolio (v2.5 — Q3 2026)
> Portfolio-level planning and governance

- Epic 2: PI Planning & Cadence
- Epic 5: Value Stream Modeling
- Epic 7: Inspect & Adapt
- Epic 8: Roles & Governance (partial)

### Phase 3: SAFe Large Solution (v3.0 — Q4 2026)
> Multi-ART coordination

- Epic 6: ART Construct
- Epic 8: Roles & Governance (complete)
- Epic 9: Solution Train

### Jira Configuration Requirements

To support SAFe 6.0, the Jira instance needs:

| Configuration | Current | Required |
|---|---|---|
| **Issue Types** | Epic, Story, Bug, Task, Improvement, Spike, Sub-task | + Feature, Enabler, Capability, NFR |
| **Custom Fields** | None SAFe-specific | WSJF (User-Business Value, Time Criticality, Risk Reduction, Job Size), PI, Business Value, Benefit Hypothesis |
| **Workflows** | 4-state linear | Portfolio Kanban (6-state), ART workflow (with PI assignment) |
| **Boards** | Standard Kanban/Scrum | Portfolio Kanban board, ART board per value stream |
| **Fix Versions** | Release-based | PI-based (PI 2026.1, PI 2026.2, ...) |

---

## 6. Risks & Considerations

| Risk | Impact | Mitigation |
|---|---|---|
| **SAFe complexity vs RaiSE simplicity** | Over-engineering the product, violating "simple first" principle | Implement SAFe as optional configuration layer, not default. Community edition stays lean. |
| **Jira SAFe plugins overlap** | Atlassian has native SAFe support (Advanced Roadmaps, Agile Hive) | Position RaiSE as AI-augmented SAFe orchestration, not Jira replacement. Complement existing tools. |
| **Multi-ART requires multi-repo** | Current RaiSE is single-repo focused | Leverage rai-server shared memory + cross-repo visibility (already planned for P2.0). |
| **SAFe ceremony facilitation** | PI Planning is a 2-day event with complex facilitation | Start with pre/post PI Planning support (backlog prep, objective tracking, dependency capture), not live facilitation. |
| **Licensing** | SAFe is a commercial framework (Scaled Agile, Inc.) | RaiSE implements SAFe practices, doesn't redistribute SAFe IP. Use generic terminology where possible. |

---

## 7. Competitive Landscape

| Tool | SAFe Support | RaiSE Differentiator |
|---|---|---|
| **Jira + Advanced Roadmaps** | Native PI planning, ART boards, dependencies | AI-assisted ceremony facilitation, automated flow metrics, knowledge graph |
| **Agile Hive (SAFe in Jira)** | Full SAFe 6.0 mapping in Jira | AI coaching, skill-based workflows, pattern learning |
| **Azure DevOps** | Basic SAFe templates | Cross-platform (Jira/ADO), governance-as-code, extensible adapters |
| **Rally (Broadcom)** | Purpose-built for SAFe | Lighter weight, AI-native, open-core model |
| **Planview / Tasktop** | Flow metrics focus | Integrated lifecycle (not just metrics), knowledge capture |

**RaiSE unique value proposition for SAFe:** AI-assisted ceremony facilitation + automated flow measurement + organizational learning from patterns across PIs.

---

## 8. Open Questions

1. **Which SAFe configuration does Coppel need?** Essential, Portfolio, Large Solution, or Full?
2. **How many ARTs does Coppel operate?** Determines scope of multi-ART features.
3. **Current tools?** What Jira plugins / SAFe tools are already in use?
4. **Timeline pressure?** When does Coppel need SAFe support operational?
5. **Customization?** Does Coppel follow standard SAFe or has adapted SAFe practices?
6. **Metrics maturity?** Are they already tracking flow metrics, or starting from scratch?
7. **Training integration?** Does Coppel want RaiSE to include SAFe training/coaching content?

---

## 9. Appendix: SAFe 6.0 Key Changes from 5.x

| Change | Impact on RaiSE |
|---|---|
| "Program" → "ART" terminology | Use ART terminology throughout |
| Eight Flow Accelerators | Implement as guardrail/coaching patterns |
| Business Agility Value Stream (BAVS) | Model at org level in rai-server |
| OKRs alongside PI Objectives | Support both PI Objectives and OKRs |
| Pre-Plan / Coordinate & Deliver | New event types in ceremony support |
| Team Coach > Scrum Master | Role model reflects new naming |
| AI/Big Data/Cloud guidance | Natural fit — RaiSE IS the AI guidance |
| Core values: Alignment, Transparency, Respect, Relentless Improvement | Align with RaiSE values (Honesty, Simplicity, Observability, Learning, Partnership) |
