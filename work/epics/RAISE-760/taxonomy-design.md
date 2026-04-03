# S760.2: Taxonomy Design — Idiomatic Atlassian for RaiSE

**Epic:** RAISE-760
**Story:** RAISE-761
**Date:** 2026-03-27
**Status:** Draft

---

## 1. Gemba: Current State

### What Exists in Jira (RAISE project)

| Dimension | Current State | Issues |
|-----------|--------------|--------|
| **Issue types** | Epic, Story, Task, Bug, Sub-task | No Initiative type active (created, deleted, recreated, deleted again during grooming) |
| **Components** | `rai-agent`, `raise-community`, `raise-pro` | Not consistently assigned — many epics/stories have no component |
| **Versions** | 2.3.1, 2.4.0, 2.5.0, 2.6.0, 3.0.0, TBD | Active and well-maintained. TBD version for items needing product decision |
| **Boards** | 3 Kanban boards: "RaiSE Stories", "RaiSE Epics", "RAISE board" | Redundant — 3 boards for 1 developer |
| **Workflow** | Simplified: Backlog → Selected → In Progress → Done | Same workflow for all issue types. 4 states. |
| **Labels** | Organic, ~30+ distinct labels | Inconsistent: mix of functional (`atlassian`, `forge`), lifecycle (`pro-launch`), and ad-hoc |
| **Initiatives** | None active | Attempted twice (RAISE-637-645, then RAISE-766-771), both deleted. Jira "Initiative" type not available in current scheme |
| **Parent links** | Epics link to nothing above; Stories link to Epics | No portfolio-level grouping persists |

### What Exists in RaiSE Framework

| RaiSE Concept | Jira Equivalent Today | Gap |
|---------------|----------------------|-----|
| Epic (bounded work, 3-10 stories) | Jira Epic | Aligned |
| Story (independently deliverable value) | Jira Story | Aligned |
| Task (technical, no direct user value) | Jira Task | Aligned |
| Bug (defect) | Jira Bug | Aligned |
| Initiative (strategic objective, groups epics) | None active | **No persistent grouping above Epic** |
| Capability (cross-cutting competency area) | Implicit, not tracked | **No classification mechanism** |
| Research track | Jira Story or nothing | **No distinct type — mixed with features** |
| Spike (time-boxed investigation) | Jira Story with label | **No formal type** |
| Improvement (non-feature enhancement) | Jira Story or Task | **Ambiguous** |
| Skill lifecycle phases | Mapped in `jira.yaml` lifecycle_mapping | Functional but coarse (4 states) |

---

## 2. Design Principles

1. **Use Jira features as designed** — issue types for classification, components for ownership, versions for release targeting, labels for cross-cutting concerns. Don't abuse one mechanism for another's job.

2. **Minimum viable taxonomy** — add types/fields only when the classification enables a workflow or query that matters. "Nice to categorize" is not enough.

3. **Queryable by default** — every classification decision should enable a useful JQL query. If you can't write the JQL, the field isn't earning its place.

4. **Scalable to partner teams** — a team of 5 or 50 should use the same model. Complexity scales with team size, not with the taxonomy.

5. **AI-agent friendly** — `rai backlog` commands and Rovo agents need predictable, machine-readable issue structure. Avoid free-text classification where structured fields work.

6. **Each product does what it was designed for** — don't force Jira to be a software catalog (that's Compass), don't force Confluence to be a work tracker (that's Jira), don't build UI when Rovo provides one.

---

## 3. Product Responsibility Matrix

Every RaiSE artifact and concept maps to exactly ONE primary Atlassian product.
Secondary products participate via integration, not duplication.

### By Product

| Product | Primary Responsibility | RaiSE Artifacts |
|---------|----------------------|-----------------|
| **Jira** | Work tracking & lifecycle | Initiatives, Epics, Stories, Bugs, Tasks. Sprint planning. Versions/releases. |
| **Confluence** | Knowledge & documentation | Governance docs, ADRs, research reports, epic designs/retros, skills-as-pages, templates, patterns (human-readable), glossary, release notes |
| **Compass** | Software catalog & health | Capabilities (C1-C12), scorecards, DORA metrics, dependency graphs, ownership, architecture docs |
| **Forge** | App platform & state | Rovo agent backend, KVS (conversation state), Custom Entity Store (cached graph), Secret Store (API keys), async queue consumers |
| **Rovo** | AI interface | Rai Governance agent, Rai Dev agent. Natural language queries over Jira + Confluence + Compass |
| **Bitbucket** | Code collaboration | PR ↔ Jira links, branch naming (ADR-033), pipelines, code review, development panel |
| **Automation** | Cross-product glue | Story→Done triggers retro page, Epic closed updates scorecard, webhook from `rai backlog`, auto-linking |

### By RaiSE Artifact

| RaiSE Artifact | Primary Product | Secondary | Integration |
|----------------|----------------|-----------|-------------|
| Knowledge graph | raise-server (canonical) | Forge (cache) | Forge fetch() → raise-server API |
| Session state/journal | Forge KVS (active) | Confluence (archive) | Automation: session close → Confluence page |
| Patterns | Confluence (human-readable) | Forge Entity Store (queryable) | Rovo surfaces via graph query |
| Governance docs | Confluence | — | Rovo reads natively; sync to raise-server graph |
| ADRs | Confluence | Jira (linked stories) | Jira issue links to Confluence page |
| Epic scope/design/retro | Confluence | Jira (Epic issue) | Automation: Epic transitions → Confluence page updates |
| Story lifecycle | Jira | Confluence (design doc) | Automation: Story→Done → retro page |
| Skills (prompts) | Confluence (pages) | — | Rovo reads as native content |
| Capabilities | Compass | Jira (linked Epics) | Native Compass ↔ Jira integration |
| Telemetry/metrics | Forge Entity Store | Compass (DORA) | Forge → Compass metric provider API |
| Module/architecture docs | Confluence | Compass (catalog entry) | Compass links to Confluence page |
| Templates | Confluence templates | — | Rovo pre-fills from context |
| Release notes | Confluence + Jira versions | — | Automation: version released → Confluence page |
| Branch/PR | Bitbucket | Jira (dev panel) | Native smart commits + dev panel |

---

## 4. Issue Type Hierarchy

### Recommended Model

```
JIRA (work tracking)                    COMPASS (software catalog)
────────────────────                    ───────────────────────────
Initiative                              Capability (component)
  └── Epic ·····························→ linked to Compass component
       ├── Story                        Health scorecards
       ├── Bug                          Dependency mapping
       ├── Task                         DORA metrics
       │    └── Sub-task                Ownership
       └── Sub-task
```

**Two products, two axes:**
- **Jira** (vertical): Initiative → Epic → Story/Bug/Task → Sub-task. Work tracking with lifecycle.
- **Compass** (horizontal): Capabilities as software catalog components. Permanent, no workflow — health, ownership, dependencies.

An Epic has ONE Initiative parent (Jira) and ONE Compass component link (the capability it touches). These are independent classifications across different products — Initiative answers "what business goal?" and Capability answers "what technical competency?"

**ADR-037:** Capabilities migrate from Jira issue type to Compass components. Initiatives stay in Jira as parent of Epics. Each product does what it was designed for.

### Issue Type Definitions

| Type | Purpose | When to Use | JQL Example |
|------|---------|-------------|-------------|
| **Initiative** | Strategic objective grouping multiple epics. Rolling — no fixed end. | When work represents a business-level theme (e.g., "RaiSE PRO Launch", "OSS Product Excellence") | `issuetype = Initiative AND project = RAISE` |
| **Epic** | Bounded body of work. Contains 3-10 stories. Has scope, design, retro. | When work requires architectural direction or spans multiple deliverables | `issuetype = Epic AND fixVersion = 2.4.0` |
| **Story** | Delivers user/developer value — new capability, feature, UX | When a stakeholder can use or observe the output | `issuetype = Story AND status = "In Progress"` |
| **Task** | Technical work — infra, CI, config, maintenance, research | When work is necessary but has no direct user value | `issuetype = Task AND component = raise-pro` |
| **Bug** | Defect — something worked and broke, or never worked as specified | Actual defects. Use priority for severity | `issuetype = Bug AND priority = Critical` |
| **Sub-task** | Child of any issue for breaking down complex work | When a Story/Task/Bug needs visible sub-steps | `parent = RAISE-760` |

### Decision: Initiative Type

**Problem:** Initiatives were created twice and deleted twice. The Jira "Initiative" hierarchy level requires Jira Premium/Advanced plan features.

**Recommendation:** Use Jira's native parent hierarchy:
- **If Premium/Advanced available:** Enable Initiative as a hierarchy level above Epic. Parent-child linking provides native portfolio views, roadmaps, and JQL filtering.
- **If Standard plan:** Use a dedicated **label convention** (`initiative:pro-launch`, `initiative:oss-excellence`) on Epics to group them. Queryable via `labels = "initiative:pro-launch"`. Not ideal but workable.

**Verification needed:** Check if current Atlassian plan supports Initiative hierarchy level. If not, the label convention is the pragmatic path.

### Decision: Capabilities → Compass (ADR-037)

**Problem:** 12 Capabilities exist as Jira issue types (RAISE-795 to RAISE-815) but they are not work items — they have no natural lifecycle, never "complete", and don't belong in a workflow. They are permanent competency areas of the product.

**Decision:** Migrate Capabilities to **Atlassian Compass** as software catalog components. Compass is the Atlassian product designed for exactly this — component catalog with health scorecards, dependency mapping, DORA metrics, and ownership.

**Current Capabilities → Compass Components:**

| Jira Issue | Capability | Compass Component |
|-----------|-----------|-------------------|
| RAISE-795 | C1: Skill Engine | `raise-skill-engine` |
| RAISE-796 | C2: Adapter Layer | `raise-adapter-layer` |
| RAISE-797 | C9: rai-agent Operations | `rai-agent-ops` |
| RAISE-798 | C5: CI/CD & Release | `raise-cicd-release` |
| RAISE-799 | C10: SAFe & Portfolio Mgmt | `raise-portfolio-mgmt` |
| RAISE-800 | C8: rai-agent Runtime | `rai-agent-runtime` |
| RAISE-801 | C11: Memory & Knowledge | `raise-memory-knowledge` |
| RAISE-802 | C4: CLI & Developer Experience | `raise-cli-dx` |
| RAISE-803 | C6: Security & Compliance | `raise-security-compliance` |
| RAISE-804 | C3: Session & Workstream | `raise-session-workstream` |
| RAISE-805 | C7: RaiSE PRO | `raise-pro` |
| RAISE-815 | C12: Self-Improvement | `raise-self-improvement` |

**What Compass gives us that Jira can't:**
- Health scorecards per capability (test coverage, doc quality, deployment frequency)
- Dependency graph between capabilities
- DORA metrics per component
- Ownership model (team/individual per capability)
- Integration with Jira — epics link to Compass components natively

**Migration timing:** Compass setup is P2 (post Forge MVP). Capability definitions documented now in RAISE-760. Jira Capability issues archived after Compass is live.

### Decision: Research & Spike Types

**Problem:** Research tracks (R1-R4) and spikes don't have a distinct type. They're created as Stories or Tasks ad-hoc.

**Recommendation:** Do NOT create custom issue types. Use **Task + label**:
- Research: `issuetype = Task AND labels = research`
- Spike: `issuetype = Task AND labels = spike`

**Rationale:** Custom issue types require workflow configuration, board filters, and reporting adjustments. Labels achieve the same queryability with zero admin overhead. The RaiSE lifecycle (`/rai-research`) already produces artifacts — Jira just needs to track the work item.

---

## 5. Components

### Current vs Recommended

| Current Component | Description | Recommendation |
|-------------------|-------------|----------------|
| `rai-agent` | Autonomous personal agent | **Keep** — distinct product |
| `raise-community` | Open source framework, CLI | **Keep** — maps to `rai` + `raise-core` packages |
| `raise-pro` | Commercial extensions | **Keep** — maps to `raise-pro` + `raise-server` packages |

### New Components to Add

| Component | Description | Rationale |
|-----------|-------------|-----------|
| `raise-forge` | Forge app (Rovo agents, actions) | New package from RAISE-819. Distinct deployment artifact. |
| `raise-docs` | Documentation site (raise.dev) | Website is a separate deliverable with its own release cycle |

### Component Assignment Policy

- **Every Story and Bug MUST have a component.** Enforced by convention (and eventually Jira Automation).
- **Epics MAY have a component** if all stories are in one component. Cross-cutting epics leave it empty.
- **Tasks inherit** from parent Epic if applicable.

**JQL value:** `component = raise-pro AND fixVersion = 2.4.0 AND issuetype = Story` → "what PRO stories are in 2.4.0?"

---

## 6. Versions (fixVersion)

### Current Policy (TN-002, validated)

Versions map to release branches (ADR-033):
- `2.3.x` → hotfix releases
- `2.4.0` → current feature development
- `2.5.0` → SAFe Essential
- `2.6.0` → Platform & Scale
- `3.0.0` → v3 product architecture
- `TBD` → needs product decision

### Recommendation: Keep Current Policy, Add Conventions

| Rule | Description |
|------|-------------|
| **Every story gets a fixVersion** | No exceptions. "TBD" if uncertain. |
| **Epics get fixVersion of primary release** | The release where majority of stories land |
| **Bugs get fixVersion of the fix** | Not the version where discovered |
| **Initiatives have no fixVersion** | They're rolling — versions apply to their child epics |

### Version Naming Convention

```
{major}.{minor}.{patch}     → release (2.4.0, 2.3.1)
{major}.{minor}.{patch}aN   → alpha (2.2.0a1)
{major}.{minor}.{patch}rcN  → release candidate (2.2.0rc1)
```

---

## 7. Labels

### Current State: Organic, Inconsistent

~30+ labels exist with no convention. Mix of:
- Product area: `atlassian`, `forge`, `governance`
- Lifecycle: `pro-launch`, `v2.4`
- Cross-cutting: `partner`, `process`
- Ad-hoc: various one-offs

### Recommended Label Taxonomy

Labels serve **cross-cutting concerns** that don't fit in components or versions.

| Category | Convention | Examples | JQL |
|----------|-----------|----------|-----|
| **Initiative** (if no hierarchy level) | `initiative:{name}` | `initiative:pro-launch`, `initiative:oss-excellence` | `labels = "initiative:pro-launch"` |
| **Work type** | `{type}` | `research`, `spike`, `refactor`, `docs`, `ci` | `labels = research` |
| **Product area** | `{area}` | `atlassian`, `forge`, `rovo` | `labels = forge` |
| **Strategic** | `{tag}` | `pro-launch`, `partner`, `marketplace` | `labels = pro-launch` |

**Note:** Capabilities are NOT labels — they live in Compass as catalog components (ADR-037). Epics link to Compass components via native Jira ↔ Compass integration.

### Labels to Retire

| Label | Replace With |
|-------|-------------|
| `v2.4` | fixVersion = 2.4.0 (that's what versions are for) |
| `governance` | component = raise-community (governance is in the core package) |
| Any label duplicating a component name | Use the component field |

### Label Hygiene Rules

1. **Lowercase, hyphenated** — `pro-launch` not `Pro Launch` or `PRO_LAUNCH`
2. **No version labels** — use fixVersion field
3. **No component labels** — use component field
4. **Max 3 labels per issue** — if you need more, something is misclassified

---

## 8. Board Configuration

### Current State: 3 Boards, Redundant

| Board | Type | Purpose |
|-------|------|---------|
| RAISE board | Kanban | Original, likely unused |
| RaiSE Stories | Kanban | Story-level view |
| RaiSE Epics | Kanban | Epic-level view |

### Recommendation: 2 Boards

| Board | Type | Filter | Swimlanes | Purpose |
|-------|------|--------|-----------|---------|
| **RaiSE Delivery** | Kanban | `project = RAISE AND issuetype in (Story, Bug, Task) AND fixVersion = latestReleasedVersion() + 1` | By Epic | Day-to-day work for current release |
| **RaiSE Portfolio** | Kanban | `project = RAISE AND issuetype = Epic AND status != Done` | By Component | Epic-level progress view |

- **Archive** "RAISE board" (original) — replace with "RaiSE Delivery"
- **Rename** "RaiSE Epics" to "RaiSE Portfolio"
- **Rename** "RaiSE Stories" to "RaiSE Delivery"

### Column Mapping

Both boards use the same 4-state workflow:

| Column | Status | WIP Limit (Delivery) | WIP Limit (Portfolio) |
|--------|--------|---------------------|----------------------|
| Backlog | Backlog | — (hidden or collapsed) | — |
| Selected | Selected for Development | 5 | 3 |
| In Progress | In Progress | 3 | 2 |
| Done | Done | — (auto-clear 14 days) | — |

**WIP limits are for when the team grows.** For solo developer: informational only.

---

## 9. SAFe Concept Mapping (Partner Reference)

RaiSE has its own terminology. This table helps partner teams already using SAFe
understand where RaiSE concepts land in their existing setup.

| SAFe Concept | RaiSE Term | Atlassian Product | Notes |
|-------------|-----------|------------------|-------|
| Portfolio Backlog | Product roadmap | Jira Roadmap (Premium) | Not formalized in RaiSE |
| Business Epic | **Initiative** | **Jira** — Initiative issue type | Strategic objective grouping epics |
| Capability | **Capability** | **Compass** — software catalog component | Permanent competency area with health scorecards |
| PI (Program Increment) | Release | **Jira** — fixVersion (e.g., 2.4.0) | PI = release version |
| Feature | **Epic** | **Jira** — Epic issue type | Bounded delivery, 3-10 stories |
| Story | **Story** | **Jira** — Story issue type | 1:1 mapping |
| Enabler | **Task** | **Jira** — Task issue type + label | `labels = enabler` if needed |
| Team | Component ownership | **Jira** — Component field + **Compass** ownership | Component ≈ team ownership area |

### Important Distinctions

- **Initiative ≠ Capability.** Initiative is a business objective in Jira (work tracking: Initiative → Epic → Story). Capability is a technical competency area in Compass (software catalog: health, ownership, dependencies). Different products, different purposes.
- **Jira tracks work. Compass catalogs software.** An Epic lives in Jira under an Initiative AND links to a Compass component (capability). Two views of the same reality.
- **RaiSE does not require SAFe.** The taxonomy above works independently. SAFe mapping is provided as a translation guide for partner teams that already operate within SAFe.
- **Terminology is generic.** Initiative, Capability, Epic, Story are standard software engineering terms — not proprietary to any framework.

---

## 10. Summary: Before vs After

| Dimension | Before | After |
|-----------|--------|-------|
| Dimension | Before | After |
|-----------|--------|-------|
| Issue types | Epic, Story, Task, Bug, Sub-task, Capability (misplaced) | Initiative → Epic → Story/Bug/Task → Sub-task. Capability retires from Jira. |
| Capability tracking | 12 Jira issues (C1-C12), no workflow | **Compass** components with scorecards, DORA, dependencies |
| Components | 3, inconsistently used | 5, mandatory on Stories/Bugs |
| Versions | Well-managed | Keep + enforce fixVersion on all stories |
| Labels | ~30, organic | Categorized: work-type, product-area, strategic |
| Boards | 3 redundant | 2 purpose-driven (Delivery + Portfolio) |
| Hierarchy | Epic → Story (flat above) | Initiative → Epic → Story/Bug/Task → Sub-task |
| Workflow | 4-state simplified | Keep (sufficient for current team size) |

---

## 11. Migration Plan

### Phase 1: Jira Cleanup (Now)

| Step | Action | Risk | Reversible |
|------|--------|------|-----------|
| 1 | Add `raise-forge` and `raise-docs` components | None | Yes |
| 2 | Assign components to existing untagged stories | Low | Yes |
| 3 | Ensure fixVersion on all open stories | Low | Yes |
| 4 | Clean up label taxonomy (retire version/component labels) | Low | Yes |
| 5 | Archive "RAISE board", rename remaining two | Low | Yes |
| 6 | Verify Initiative hierarchy is available in plan | None | Read-only |
| 7 | Create Initiatives, re-link epics as children | Medium | Yes |

### Phase 2: Compass Setup (Post-MVP)

| Step | Action | Risk | Reversible |
|------|--------|------|-----------|
| 8 | Setup Compass for RAISE project | None | Yes |
| 9 | Create 12 Compass components from C1-C12 definitions | None | Yes |
| 10 | Define scorecards per component | Low | Yes |
| 11 | Link existing epics to Compass components | Low | Yes |
| 12 | Archive Capability issues (RAISE-795 to RAISE-815) | Low | Yes (re-open) |
| 13 | Consider retiring Capability as Jira issue type | Low | Yes |

**All steps are independently reversible.** No destructive migrations.

---

## 12. Verification Queries

After migration, these JQL queries should return meaningful results:

```sql
-- All PRO stories in current release
component = raise-pro AND fixVersion = 2.4.0 AND issuetype = Story

-- All research tasks
issuetype = Task AND labels = research

-- All epics under an Initiative (native hierarchy)
issuetype = Epic AND parent = RAISE-XXX

-- Open bugs by severity
issuetype = Bug AND status != Done ORDER BY priority DESC

-- Stories without component (should be zero after cleanup)
issuetype = Story AND component is EMPTY AND status != Done

-- Current release work
fixVersion = 2.4.0 AND status = "In Progress"

-- All epics for a Capability (after Compass integration)
-- → Use Compass UI: component view → linked Jira issues
-- → Or Compass GraphQL API from Forge app
```

---

## References

- ADR-037: Capabilities en Compass, Initiatives en Jira
- TN-002: Branching & Versioning Strategy
- ADR-033: Parallel Version Branching
- R1-RAISE-760: Atlassian API Landscape (Compass GraphQL, Jira API, rate limits)
- R3-RAISE-760: RaiSE ↔ Atlassian Value Map (artifact mapping matrix)
- `.raise/jira.yaml`: Current Jira configuration
- RAISE-779: Initiative creation retrospective
- RAISE-795 to RAISE-815: Current Capability issues (C1-C12)
