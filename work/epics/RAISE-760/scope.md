# RAISE-760: RaiSE Project Management Model — Scope

**Jira:** RAISE-760
**Labels:** atlassian, governance, partner, process
**Branch:** release/2.4.0
**Feeds into:** RAISE-819 (Forge MVP construction)
**Research:** [research/](research/) (R1-R4, completed 2026-03-27)

## Objective

Design the idiomatic integration model between RaiSE and the full Atlassian
stack (Jira, Confluence, Compass, Forge, Rovo, Bitbucket, Automation). Produce
a grounded blueprint that maximizes the value of both platforms — so that any
team already on Atlassian can adopt RaiSE with zero friction and immediately
benefit from AI-governed software delivery.

## Value

- **For partner teams:** turnkey blueprint — "this is how RaiSE maps to your Atlassian stack"
- **For RaiSE product:** design foundation for Forge app (RAISE-819), adapter evolution, and Compass integration
- **For Atlassian partnership:** reference implementation showcasing the full stack
- **Unlocks:** RAISE-819 (Forge MVP), adapter alignment stories, Compass setup, Marketplace positioning

## Design Principle

**Each Atlassian product does what it was designed for:**

| Product | Responsibility in RaiSE |
|---------|------------------------|
| **Jira** | Work tracking — Initiative → Epic → Story/Bug/Task → Sub-task |
| **Confluence** | Knowledge — governance docs, ADRs, research, designs, templates, skills-as-pages |
| **Compass** | Software catalog — capabilities (C1-C12) with scorecards, DORA, dependencies |
| **Forge** | App platform — Rovo agent backend, state persistence, external fetch to raise-server |
| **Rovo** | AI interface — governance agents, dev agents, natural language over Jira+Confluence+Compass |
| **Bitbucket** | Code collaboration — PR↔Jira links, branch conventions, pipeline triggers |
| **Automation** | Glue — cross-product workflows connecting lifecycle events across products |

## Stories

### S760.1: Atlassian Platform & Ecosystem Research (M) — DONE

4 research tracks completed:
- R1: Atlassian API Landscape (11 products, rate limits, auth, timeline)
- R2: Python Ecosystem (libraries, MCP servers, adapter analysis)
- R3: RaiSE ↔ Atlassian Value Map (artifact mapping, 6 business cases, competitive analysis)
- R4: Forge Platform Deep-Dive (runtime, storage, Rovo, MVP architecture)

All published to Confluence under RAISE-760.

**Dependencies:** None

### S760.2: Taxonomy & Product Responsibility Design (M) — DONE

Define how RaiSE concepts map across the Atlassian stack:
- Issue type hierarchy: Initiative → Epic → Story/Bug/Task → Sub-task
- Capability → Compass components (ADR-037)
- Component, fixVersion, label conventions
- Board configuration
- Product Responsibility Matrix (which artifact lives where)
- SAFe mapping for partner reference

Deliverable: Taxonomy Design Document + ADR-037

**Dependencies:** S760.1

### S760.3: Workflow, Automation & Lifecycle Mapping (M)

Design how RaiSE skill lifecycle connects to Jira workflows AND cross-product
automation:
- Workflow per issue type (Backlog → Selected → In Progress → Done)
- RaiSE skill lifecycle ↔ Jira transitions mapping (story-start → In Progress, etc.)
- **Jira Automation rules** — the glue between products:
  - Story → Done triggers retro page creation in Confluence
  - Epic closed triggers Compass scorecard update
  - Incoming webhook from `rai backlog transition` triggers cascade
  - New Epic auto-links to Compass component
- **Bidirectional sync model:** `rai backlog` ↔ Jira ↔ Automation ↔ Confluence/Compass
- Automation rule specifications (trigger, condition, action, smart values)

Deliverable: Workflow & Automation Design Document

**Dependencies:** S760.2

### S760.4: Confluence Information Architecture (M)

Define how RaiSE artifacts map to Confluence:
- Space structure: sections, page trees, permissions
- RaiSE artifacts → Confluence pages (scope, design, plan, retro, ADRs, research)
- Template library (governance, architecture, tech design)
- Skills-as-pages model validation
- `rai docs` adapter alignment with IA

Deliverable: Confluence IA Document + template specs

**Dependencies:** S760.1

### S760.5: Compass Capability Catalog Design (M)

Design how RaiSE capabilities map to Compass:
- 12 Compass component definitions from C1-C12
- Scorecard design per component (which health metrics matter)
- Dependency graph between capabilities
- Jira ↔ Compass linking model (Epic → Compass component)
- DORA metric mapping (what RaiSE telemetry feeds Compass)
- Ownership model (team/individual per capability)

Deliverable: Compass Catalog Design Document

**Dependencies:** S760.2

### S760.6: Bitbucket Integration Design (S)

Design how RaiSE git conventions map to Bitbucket features:
- Branch naming → Jira issue auto-linking (ADR-033 branch model)
- PR → Jira issue status transitions
- Pipeline triggers from RaiSE lifecycle events
- Code review workflow alignment
- Development panel in Jira issues

Deliverable: Bitbucket Integration Design Document

**Dependencies:** S760.2

### S760.7: Adapter Gap Analysis (S)

Map gaps between current RaiSE adapters and the idiomatic model designed in
S760.2-S760.6:
- `AcliJiraAdapter` vs taxonomy/workflow design — what's missing?
- `McpConfluenceAdapter` vs Confluence IA — what's missing?
- No Compass adapter exists — what does it need?
- No Bitbucket adapter exists — what does it need?
- Rovo MCP Server evaluation for Forge app auth
- `atlassian-python-api` dependency audit
- Actionable backlog stories created for each gap

Deliverable: Gap analysis document + backlog stories

**Dependencies:** S760.3, S760.4, S760.5, S760.6

### S760.8: Reference Blueprint (M)

Consolidate all designs into a single partner-facing blueprint:
- Product Responsibility Matrix (consolidated)
- Setup checklist for teams adopting RaiSE on Atlassian
- `rai init --stack atlassian` requirements specification
- Published as Confluence blueprint/guide

Deliverable: Partner Reference Blueprint (Confluence)

**Dependencies:** S760.7

## In Scope (MUST)

- Product Responsibility Matrix across all 7 Atlassian products
- Taxonomy design (issue types, components, labels, versions) — ADR-037
- Workflow & automation design (lifecycle mapping, automation rules)
- Confluence IA design (space structure, templates, artifact mapping)
- Compass capability catalog design (components, scorecards, dependencies)
- Adapter gap analysis with actionable backlog stories
- All designs published to Confluence

## In Scope (SHOULD)

- Bitbucket integration design
- Jira Automation rule specifications
- Partner reference blueprint
- `rai init --stack atlassian` requirements spec

## Out of Scope (design only — no implementation)

- Forge app construction → RAISE-819
- Adapter code changes → stories from gap analysis (S760.7)
- Compass setup and component creation → stories from gap analysis
- Jira project restructuring (board/label cleanup) → stories from gap analysis
- Marketplace listing → RAISE-819
- Multi-tenant architecture → post-MVP

## Done Criteria

- [x] R1-R4 research complete and published
- [x] Taxonomy & Product Responsibility design published (ADR-037)
- [x] Workflow & automation design published
- [x] Confluence IA design published
- [x] Compass capability catalog design published
- [x] Bitbucket integration design published
- [x] Adapter gap analysis complete with 6 backlog epics created (RAISE-829 to RAISE-834)
- [x] Reference blueprint published for partner teams
- [x] Research summary & strategic recommendations published
- [x] Product vision document published
- [x] VE-87 sales opportunity created from research insights

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Model too theoretical without Forge validation | Medium | Medium | RAISE-819 runs in parallel, feeds back learnings |
| Compass requires plan upgrade not available | Medium | Medium | Design the model anyway; degrade to Jira Components if needed |
| Automation rules too complex for initial adoption | Low | Low | Start with 3-5 high-value automations, not full coverage |
| Bitbucket design not applicable (we use GitHub) | Low | Low | Design for Bitbucket (partner-facing); note GitHub equivalents |
