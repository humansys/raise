# S760.4: Confluence Information Architecture

**Epic:** RAISE-760
**Story:** S760.4
**Date:** 2026-03-27
**Status:** Draft
**Dependencies:** S760.1 (R1-R4 research complete), S760.2 (taxonomy design)

---

## 1. Design Principles

1. **One space, many sections.** A single Confluence space per RaiSE project keeps permissions simple, CQL queries fast, and avoids the overhead of cross-space linking. Multiple spaces only when regulatory or organizational boundaries demand isolation.

2. **Page tree mirrors artifact lifecycle.** The tree follows the work lifecycle (governance > architecture > epics > research), not an arbitrary org chart. A developer navigating the tree follows the same mental model as the RaiSE skill lifecycle.

3. **Labels for cross-cutting, tree for hierarchy.** The page tree handles parent-child relationships (epic > stories). Labels handle orthogonal concerns (artifact type, capability, release version). Never duplicate in both.

4. **Templates enforce structure.** Every artifact type that lands in Confluence has a template. Templates are the contract between `rai docs publish` and human authors. Rovo agents rely on predictable structure.

5. **Skills are pages.** Skill definitions live as Confluence pages (validated in RAISE-273). Rovo reads them natively. Governance teams edit skills without code. This is a core differentiator.

6. **Filesystem is canonical, Confluence is the visibility layer.** Governance docs, ADRs, and skill definitions live in `.raise/` (git-versioned). Confluence is the published, searchable, commentable view. `rai docs publish` pushes; Confluence never writes back to git.

---

## 2. Space Strategy

### Recommendation: One Space Per Project

A RaiSE team needs **one Confluence space** per project/product. This space holds all knowledge artifacts: governance, architecture, research, epics, skills, and operational docs.

| Factor | One Space | Multiple Spaces |
|--------|-----------|----------------|
| **CQL queries** | Simple: `space = "PROJ"` scopes everything | Requires `space IN ("PROJ-GOV", "PROJ-DEV", "PROJ-OPS")` |
| **Permissions** | Use page-level restrictions for sensitive content | Space-level isolation, but administrative overhead |
| **Cross-linking** | All links are intra-space (fast, no broken links on space rename) | Cross-space links are fragile |
| **Rovo agent context** | One space to index | Must configure multiple spaces |
| **Setup cost** | One space per `rai init` | 3-5 spaces per project |

**When to use multiple spaces:**
- Regulatory requirement separates governance from engineering docs (e.g., SOX compliance requires isolated audit trail)
- Separate teams own separate products with independent release cycles
- Partner/client-facing documentation needs its own permission boundary

### Space Naming Convention

```
{PROJECT_KEY}    — e.g., RaiSE1, KURIGAGE, ACME-PAY
```

The space key matches the Jira project key when possible. If Jira and Confluence keys diverge (as with our `RAISE` project / `RaiSE1` space), document the mapping in `.raise/confluence.yaml`.

### Permission Model

| Role | Access Level | What They See |
|------|-------------|---------------|
| **Developers** | Full read/write | Everything |
| **Engineering Leads** | Full read/write | Everything |
| **Product/Governance** | Read all, write governance sections | Governance docs, ADRs, skills-as-pages |
| **Stakeholders/Execs** | Read restricted sections | Epic summaries, release notes, dashboards |
| **Rovo Agents** | Read (via API) | Everything (agents inherit user permissions) |

Sensitive content (security policies, credential references, incident post-mortems) uses **page-level restrictions** rather than separate spaces.

---

## 3. Page Tree Design

```
Space Root: {PROJECT_KEY}
│
├── Governance
│   ├── Code Standards
│   ├── Testing Policy
│   ├── Security Policy
│   ├── Guardrails
│   │   ├── {guardrail-name}          (one page per guardrail)
│   │   └── ...
│   └── Governance Policy Index       (master list with status)
│
├── Architecture
│   ├── ADR Index                     (table of all ADRs with status)
│   ├── ADR-001: {title}
│   ├── ADR-002: {title}
│   ├── ...
│   ├── Architecture Overview         (system-level architecture doc)
│   └── Module Documentation
│       ├── mod-{name}                (one page per module, from rai discover)
│       └── ...
│
├── Epics
│   ├── {EPIC-KEY}: {title}           (one page per epic)
│   │   ├── Scope                     (epic scope document)
│   │   ├── Design                    (epic design document)
│   │   ├── Plan                      (story sequencing, milestones)
│   │   ├── Retrospective             (epic retro)
│   │   ├── Developer Documentation   (from /rai-epic-docs)
│   │   ├── Research
│   │   │   ├── R1 — {title}
│   │   │   └── ...
│   │   └── Stories
│   │       ├── S{N}.{M} — {title}   (story summary page)
│   │       └── ...
│   └── ...
│
├── Research
│   ├── Research Index                (master list of all research)
│   ├── {research-id} — {title}       (standalone research, not under an epic)
│   └── ...
│
├── Skills
│   ├── Skill Index                   (catalog of all skills with metadata)
│   ├── Lifecycle Skills
│   │   ├── rai-session-start
│   │   ├── rai-story-implement
│   │   └── ...
│   ├── Discovery Skills
│   │   ├── rai-discover
│   │   └── ...
│   ├── Meta Skills
│   │   ├── rai-skill-create
│   │   └── ...
│   └── Operational Skills
│       ├── rai-debug
│       ├── rai-doctor
│       └── ...
│
├── Patterns
│   ├── Pattern Catalog               (searchable index, all PAT-E-*)
│   ├── PAT-E-{NNN}: {summary}
│   └── ...
│
├── Glossary
│   └── (Confluence built-in glossary or flat page with terms)
│
├── Templates
│   └── (Confluence template library — see Section 6)
│
├── Releases
│   ├── Release Notes — v{X.Y.Z}
│   └── ...
│
├── Operations
│   ├── Dev Environment Setup
│   ├── Deployment & Operations
│   ├── Setup Guides
│   │   ├── MCP Adapters Setup
│   │   ├── Backlog Adapter Setup
│   │   └── ...
│   └── Runbooks
│
└── Sessions (Archive)
    ├── Session Archive — {date}       (auto-generated from session close)
    └── ...
```

### Rationale for Top-Level Sections

| Section | Contents | Why Top-Level |
|---------|----------|---------------|
| **Governance** | Code standards, testing policy, guardrails | Rovo agents need a stable, predictable path to governance docs. Top-level = immediate CQL access. |
| **Architecture** | ADRs, module docs, architecture overview | Architectural decisions are long-lived, cross-cutting, and referenced from everywhere. |
| **Epics** | All epic lifecycle artifacts | Mirrors `work/epics/` in the filesystem. Each epic is a self-contained subtree. |
| **Research** | Standalone research reports | Research that isn't epic-scoped (market analysis, technology evaluations). Epic-scoped research lives under its epic. |
| **Skills** | Skill definitions as pages | Core to the skills-as-pages model. Rovo reads these natively. |
| **Patterns** | Learned engineering patterns | Organizational learning asset. Cross-team reuse via CQL. |
| **Glossary** | Project/domain terminology | Rovo can define terms in context. Onboarding accelerator. |
| **Templates** | Confluence template library | Consistency across all artifact types. |
| **Releases** | Release notes per version | Traceability from version to stories to code. |
| **Operations** | Setup guides, runbooks, deployment | Operational knowledge that doesn't fit governance or architecture. |
| **Sessions** | Archived session journals | Audit trail. Team visibility into AI agent sessions. |

---

## 4. RaiSE Artifact to Confluence Page Mapping

This section maps every RaiSE artifact type from the Product Responsibility Matrix (taxonomy-design.md, Section 3) to its Confluence location, template, and sync mechanism.

### 4.1 Governance Documents

| Attribute | Value |
|-----------|-------|
| **Filesystem** | `.raise/governance/code-standards.md`, `.raise/governance/guardrails/*.md` |
| **Confluence location** | `Governance/` subtree |
| **Template** | `tmpl-governance-policy` |
| **Sync mechanism** | `rai docs publish governance` |
| **Labels** | `governance`, `type:policy` |
| **Rovo interaction** | Read natively; answers "what are our code standards?" |
| **CQL** | `space = "RaiSE1" AND ancestor = {governance-page-id} AND label = "governance"` |

Governance docs are the **primary Rovo agent data source**. They must be well-structured with clear headings so Rovo can extract specific rules. Each guardrail is its own page for granular linking from Jira issues.

### 4.2 ADRs (Architecture Decision Records)

| Attribute | Value |
|-----------|-------|
| **Filesystem** | `.raise/governance/adrs/` (or inline in epic directories) |
| **Confluence location** | `Architecture/ADR-{NNN}: {title}` |
| **Template** | `tmpl-adr` |
| **Sync mechanism** | `rai docs publish adr` |
| **Labels** | `adr`, `status:{proposed|accepted|deprecated|superseded}` |
| **Cross-links** | Jira issue link to implementing stories; supersedes link to prior ADR |
| **CQL** | `space = "RaiSE1" AND label = "adr" AND label = "status:accepted"` |

The ADR Index page is auto-generated: a table listing all ADRs with ID, title, status, date, and linked stories. This index is regenerated on each `rai docs publish adr`.

### 4.3 Epic Scope / Design / Plan / Retro

| Attribute | Value |
|-----------|-------|
| **Filesystem** | `work/epics/{epic-id}/scope.md`, `design.md`, `plan.md`, `retrospective.md` |
| **Confluence location** | `Epics/{EPIC-KEY}: {title}/Scope`, `.../Design`, `.../Plan`, `.../Retrospective` |
| **Template** | `tmpl-epic-scope`, `tmpl-epic-design`, `tmpl-epic-retro` |
| **Sync mechanism** | `rai docs publish epic-scope`, auto via Jira Automation on Epic transitions |
| **Labels** | `epic`, `epic:{key}`, `type:{scope|design|plan|retro}` |
| **Cross-links** | Jira Epic issue linked via Web Link; child story pages linked |
| **CQL** | `space = "RaiSE1" AND label = "epic:RAISE-760" AND label = "type:retro"` |

Epic pages mirror the filesystem structure. The epic root page serves as a hub with links to all sub-artifacts. Jira Automation can create the epic page structure when an Epic enters "In Progress" status.

### 4.4 Developer Documentation (from /rai-epic-docs)

| Attribute | Value |
|-----------|-------|
| **Filesystem** | Generated by `/rai-epic-docs`, not persisted locally |
| **Confluence location** | `Epics/{EPIC-KEY}: {title}/Developer Documentation` |
| **Template** | `tmpl-epic-docs` |
| **Sync mechanism** | Direct publish from `/rai-epic-docs` skill |
| **Labels** | `epic`, `epic:{key}`, `type:dev-docs` |
| **CQL** | `space = "RaiSE1" AND label = "type:dev-docs"` |

### 4.5 Research Reports

| Attribute | Value |
|-----------|-------|
| **Filesystem** | `work/epics/{epic-id}/research/` or `work/research/` |
| **Confluence location** | Under epic: `Epics/{EPIC-KEY}/Research/R{N} — {title}`. Standalone: `Research/{id} — {title}` |
| **Template** | `tmpl-research-report` |
| **Sync mechanism** | `rai docs publish research` |
| **Labels** | `research`, `epic:{key}` (if epic-scoped), `confidence:{high|medium|low}` |
| **Cross-links** | Links to ADRs informed by research; links to Jira research tasks |
| **CQL** | `space = "RaiSE1" AND label = "research" AND label = "confidence:high"` |

Research reports include evidence catalogs. Each evidence item can be a child page or a table row, depending on volume. For reports with >20 sources, use a child "Evidence Catalog" page.

### 4.6 Skills (as Pages)

| Attribute | Value |
|-----------|-------|
| **Filesystem** | `.claude/skills/{skill-name}/` |
| **Confluence location** | `Skills/{category}/{skill-name}` |
| **Template** | `tmpl-skill-definition` |
| **Sync mechanism** | `rai docs publish skill` |
| **Labels** | `skill`, `skill-category:{lifecycle|discovery|meta|operational}` |
| **Rovo interaction** | **Primary use case.** Rovo reads skill pages natively for execution context. |
| **CQL** | `space = "RaiSE1" AND label = "skill" AND title ~ "rai-story"` |

See Section 8 for the full skills-as-pages model.

### 4.7 Templates

| Attribute | Value |
|-----------|-------|
| **Filesystem** | `.raise/templates/{category}/{name}.md` |
| **Confluence location** | Confluence **space templates** (not regular pages) |
| **Sync mechanism** | Manual setup during `rai init --stack atlassian`; maintained via space admin |
| **Labels** | N/A (templates don't have labels in Confluence) |

Templates are registered as Confluence space templates, not as regular pages under the Templates section. The Templates page in the tree serves as a human-readable catalog linking to the actual Confluence templates.

### 4.8 Patterns

| Attribute | Value |
|-----------|-------|
| **Filesystem** | `.raise/rai/memory/patterns.jsonl` |
| **Confluence location** | `Patterns/PAT-E-{NNN}: {summary}` |
| **Template** | `tmpl-pattern` |
| **Sync mechanism** | `rai docs publish pattern` (batch from JSONL) |
| **Labels** | `pattern`, `pattern-type:{engineering|process|integration}` |
| **Cross-links** | Link to the story that discovered the pattern (Jira issue link) |
| **CQL** | `space = "RaiSE1" AND label = "pattern" AND text ~ "test seam"` |

The Pattern Catalog page is an auto-generated index sorted by recency. Patterns are organizational learning assets -- the most valuable content for cross-team reuse via Rovo.

### 4.9 Module / Architecture Documentation

| Attribute | Value |
|-----------|-------|
| **Filesystem** | Generated by `rai discover`, persisted as `.raise/docs/modules/` |
| **Confluence location** | `Architecture/Module Documentation/mod-{name}` |
| **Template** | `tmpl-module-doc` |
| **Sync mechanism** | `rai docs publish module` |
| **Labels** | `module`, `component:{jira-component}` |
| **Cross-links** | Compass component link (post-MVP); links to owning epics |
| **CQL** | `space = "RaiSE1" AND label = "module" AND label = "component:raise-pro"` |

Module docs are generated from code analysis (`rai discover scan`) and published to Confluence as living architecture documentation. They include: purpose, public API, dependencies, test coverage, and architecture notes.

### 4.10 Glossary

| Attribute | Value |
|-----------|-------|
| **Filesystem** | Graph nodes (type: `term`) |
| **Confluence location** | `Glossary/` (single page with structured table, or Confluence glossary macro) |
| **Template** | N/A (structured table) |
| **Sync mechanism** | `rai docs publish glossary` |
| **Labels** | `glossary` |
| **CQL** | `space = "RaiSE1" AND label = "glossary" AND text ~ "neuro-symbolic"` |

### 4.11 Release Notes

| Attribute | Value |
|-----------|-------|
| **Filesystem** | `CHANGELOG.md` (canonical) |
| **Confluence location** | `Releases/Release Notes — v{X.Y.Z}` |
| **Template** | `tmpl-release-notes` |
| **Sync mechanism** | `rai docs publish release-notes` or Jira Automation (version released trigger) |
| **Labels** | `release`, `version:{X.Y.Z}` |
| **Cross-links** | Jira version link; links to Jira stories included in release |
| **CQL** | `space = "RaiSE1" AND label = "release" AND label = "version:2.4.0"` |

### 4.12 Session Archives

| Attribute | Value |
|-----------|-------|
| **Filesystem** | `.raise/rai/sessions/` (JSONL, gitignored) |
| **Confluence location** | `Sessions/Session Archive — {YYYY-MM-DD}` |
| **Template** | `tmpl-session-archive` |
| **Sync mechanism** | Forge async function on session close event; or `rai docs publish session` |
| **Labels** | `session`, `agent:{agent-name}` |
| **CQL** | `space = "RaiSE1" AND label = "session" AND created >= "2026-03-01"` |

Session archives are auto-generated summaries of AI agent sessions. They provide audit trail and team visibility. Daily or weekly rollups are recommended over per-session pages to avoid page proliferation.

---

## 5. Label Taxonomy

### Label Categories

Labels in Confluence are consistent with the Jira label taxonomy from S760.2. They serve cross-cutting concerns that the page tree hierarchy cannot express.

| Category | Convention | Examples | Purpose |
|----------|-----------|----------|---------|
| **Artifact type** | `type-{type}` | `type-policy`, `type-adr`, `type-scope`, `type-design`, `type-retro`, `dev-docs` | Filter by artifact kind across the tree |
| **Epic association** | `epic-{key}` | `epic-raise-760`, `epic-raise-789` | Find all pages for an epic |
| **Capability** | `capability-{id}` | `capability-c1-skill-engine`, `capability-c4-cli-dx` | Cross-reference with Compass components |
| **Release version** | `version-{ver}` | `version-2-4-0`, `version-3-0-0` | Find content relevant to a release |
| **Confidence** | `confidence-{level}` | `confidence-high`, `confidence-medium` | Research report evidence quality |
| **Status** | `status-{state}` | `status-accepted`, `status-deprecated`, `status-draft` | ADR lifecycle, governance doc status |
| **Skill category** | `skill-category-{cat}` | `skill-category-lifecycle`, `skill-category-discovery` | Skill catalog filtering |
| **Pattern type** | `pattern-type-{type}` | `pattern-type-engineering`, `pattern-type-process` | Pattern catalog filtering |
| **Base types** | (no prefix) | `governance`, `adr`, `research`, `skill`, `pattern`, `module`, `glossary`, `release`, `session`, `epic` | Broad artifact class for simple CQL |

> **Note (2026-03-28):** Confluence Cloud does NOT support colons (`:`) in labels.
> The original design used `category:value` format but this was rejected by the API
> during RAISE-863 execution. All structured labels use hyphens instead: `epic-raise-760`
> not `epic:RAISE-760`. CQL queries updated accordingly.

### Label Hygiene Rules

1. **Lowercase, hyphenated** -- `type-dev-docs` not `Type:DevDocs`
2. **Prefixed categories** -- always use `category-value` format (hyphens, not colons — Confluence rejects colons)
3. **Base type label always present** -- every page gets at least one base type label (e.g., `adr`, `research`)
4. **Max 5 labels per page** -- base type + 2-3 structured labels + 1 optional tag
5. **Consistent with Jira** -- same vocabulary: `research`, `spike`, `refactor` mean the same in both products

### CQL Query Examples

```sql
-- All governance docs (for Rovo agent indexing)
space = "RaiSE1" AND label = "governance"

-- All accepted ADRs
space = "RaiSE1" AND label = "adr" AND label = "status:accepted"

-- Everything related to a specific epic
space = "RaiSE1" AND label = "epic:RAISE-760"

-- All high-confidence research
space = "RaiSE1" AND label = "research" AND label = "confidence:high"

-- Skills in the lifecycle category
space = "RaiSE1" AND label = "skill" AND label = "skill-category:lifecycle"

-- All patterns discovered in the last month
space = "RaiSE1" AND label = "pattern" AND created >= "2026-03-01"

-- Module docs for a specific component
space = "RaiSE1" AND label = "module" AND label = "component:raise-pro"

-- Release notes for v2.4.0
space = "RaiSE1" AND label = "release" AND label = "version:2.4.0"

-- Full-text search within governance
space = "RaiSE1" AND label = "governance" AND text ~ "testing policy"

-- Recent session archives
space = "RaiSE1" AND label = "session" AND lastModified > startOfWeek()
```

### Cross-Linking: Confluence Pages to Jira Issues

| Link Type | Direction | Mechanism |
|-----------|-----------|-----------|
| Epic page to Jira Epic | Confluence -> Jira | Web Link in Confluence page, mentioning `RAISE-{N}` (auto-links) |
| ADR page to implementing Story | Confluence -> Jira | `Implements` relationship via Jira issue link |
| Jira Story to design doc | Jira -> Confluence | Confluence page link in Jira issue's "Confluence Pages" section (native integration) |
| Pattern to discovering Story | Confluence -> Jira | Web Link: `"Discovered in RAISE-{N}"` |
| Research to informing ADR | Confluence -> Confluence | Inline link within research report |
| Module doc to Compass component | Confluence -> Compass | Compass component links to Confluence page (native) |

---

## 6. Template Library

### Template Inventory

Each template maps to a `.raise/templates/` filesystem template. Confluence templates enforce the same structure, enabling `rai docs publish` to produce consistent output.

#### T1: ADR Template (`tmpl-adr`)

Maps to: `.raise/templates/architecture/adr.md`

| Section | Required | Description |
|---------|----------|-------------|
| **Title** | Yes | `ADR-{NNN}: {Decision Title}` |
| **Status** | Yes | Proposed / Accepted / Deprecated / Superseded |
| **Date** | Yes | Decision date |
| **Decision Makers** | Yes | Who made this decision |
| **Related** | No | Links to related ADRs, stories, epics |
| **Context** | Yes | 2-4 sentences: situation requiring decision |
| **Decision** | Yes | 1-2 sentences: the decision, clear and direct |
| **Consequences** | Yes | Table: positive and negative impacts |
| **Alternatives** | Yes | Table: rejected options with rationale |
| **References** | No | Supporting links |

#### T2: Research Report Template (`tmpl-research-report`)

Maps to: `.raise/templates/tools/research-report.md`

| Section | Required | Description |
|---------|----------|-------------|
| **Frontmatter** | Yes | Research ID, date, status, confidence, reading time |
| **TL;DR** | Yes | 3 bullet points + 1-line recommendation |
| **Research Questions** | Yes | Primary + secondary questions, decision context |
| **Methodology** | Yes | Scope, sources consulted, time invested, limitations |
| **Key Findings** | Yes | Structured findings with evidence levels |
| **Evidence Catalog** | Yes | Table: ID, source, type, evidence level, key finding |
| **Recommendations** | Yes | Numbered, actionable recommendations |

#### T3: Governance Policy Template (`tmpl-governance-policy`)

Maps to: `.raise/templates/governance/governance-policy.md`

| Section | Required | Description |
|---------|----------|-------------|
| **Product context** | Yes | What product, version, last update |
| **Guiding principles** | Yes | Numbered principles with source |
| **Active guardrails** | Yes | MUST (blocking) and SHOULD (warning) tables |
| **Criterion format** | Yes | What / How / Why triple |
| **Dimensions** | Yes | Categorized criteria sections |

#### T4: Epic Scope Template (`tmpl-epic-scope`)

Maps to: epic `scope.md` conventions (no dedicated template file yet)

| Section | Required | Description |
|---------|----------|-------------|
| **Epic metadata** | Yes | Jira key, labels, branch, dependencies |
| **Objective** | Yes | What this epic achieves |
| **Value** | Yes | Who benefits and how |
| **Stories** | Yes | Story list with sizes and dependencies |
| **In Scope / Out of Scope** | Yes | Explicit boundaries |
| **Done Criteria** | Yes | Checklist |
| **Risks** | No | Risk table with likelihood/impact/mitigation |

#### T5: Epic Retrospective Template (`tmpl-epic-retro`)

Maps to: epic `retrospective.md` conventions

| Section | Required | Description |
|---------|----------|-------------|
| **Metrics** | Yes | Stories completed, LOC, duration, velocity |
| **What went well** | Yes | Successes to replicate |
| **What didn't go well** | Yes | Problems to address |
| **Patterns discovered** | Yes | PAT-E-* references |
| **Process improvements** | Yes | Concrete changes to make |

#### T6: Skill Definition Template (`tmpl-skill-definition`)

Maps to: `.claude/skills/{name}/` structure

| Section | Required | Description |
|---------|----------|-------------|
| **Skill metadata** | Yes | Name, category, trigger, description |
| **Purpose** | Yes | What this skill does and when to use it |
| **Prerequisites** | Yes | Gates that must pass before execution |
| **Phases** | Yes | Ordered phases with inputs/outputs |
| **Validation** | Yes | How to verify the skill executed correctly |
| **Examples** | No | Worked examples of skill invocation |

#### T7: Pattern Template (`tmpl-pattern`)

| Section | Required | Description |
|---------|----------|-------------|
| **Pattern ID** | Yes | PAT-E-{NNN} |
| **Summary** | Yes | One-line description |
| **Context** | Yes | When this pattern applies |
| **Problem** | Yes | What problem it solves |
| **Solution** | Yes | The pattern itself |
| **Trade-offs** | Yes | What you give up |
| **Source** | Yes | Story/session where discovered |

#### T8: Module Documentation Template (`tmpl-module-doc`)

| Section | Required | Description |
|---------|----------|-------------|
| **Module ID** | Yes | `mod-{name}` |
| **Purpose** | Yes | What this module does |
| **Public API** | Yes | Key classes, functions, entry points |
| **Dependencies** | Yes | What it imports, what depends on it |
| **Architecture notes** | No | Design decisions, patterns used |
| **Test coverage** | Yes | Coverage percentage, test strategy |

#### T9: Release Notes Template (`tmpl-release-notes`)

| Section | Required | Description |
|---------|----------|-------------|
| **Version** | Yes | Semantic version |
| **Date** | Yes | Release date |
| **Highlights** | Yes | 3-5 bullet summary |
| **New Features** | Yes | Feature list with story links |
| **Bug Fixes** | Yes | Fix list with bug links |
| **Breaking Changes** | Conditional | Only if applicable |
| **Migration Guide** | Conditional | Only if breaking changes exist |
| **Contributors** | Yes | Who contributed |

#### T10: Session Archive Template (`tmpl-session-archive`)

| Section | Required | Description |
|---------|----------|-------------|
| **Session metadata** | Yes | ID, date, agent, project, duration |
| **Goal** | Yes | What was attempted |
| **Outcomes** | Yes | What was accomplished |
| **Decisions made** | Yes | Key decisions with rationale |
| **Patterns discovered** | No | PAT-E-* references |
| **Next session** | No | Suggested continuation |

---

## 7. Template Sync: Filesystem to Confluence

### Mapping Table

| Filesystem Template | Confluence Template | Auto-Sync |
|--------------------|--------------------|-----------|
| `.raise/templates/architecture/adr.md` | `tmpl-adr` | Via `rai docs publish adr` |
| `.raise/templates/tools/research-report.md` | `tmpl-research-report` | Via `rai docs publish research` |
| `.raise/templates/governance/governance-policy.md` | `tmpl-governance-policy` | Via `rai docs publish governance` |
| `.raise/templates/tech/tech-design.md` | `tmpl-tech-design` | Via `rai docs publish design` |
| `.raise/templates/artifacts/story-design.md` | `tmpl-story-design` | Via `rai docs publish story-design` |
| `.raise/templates/solution/business_case.md` | `tmpl-business-case` | Via `rai docs publish business-case` |
| (conventions in epic artifacts) | `tmpl-epic-scope`, `tmpl-epic-retro` | Via `rai docs publish epic-scope` |
| `.claude/skills/{name}/` | `tmpl-skill-definition` | Via `rai docs publish skill` |
| (JSONL patterns) | `tmpl-pattern` | Via `rai docs publish pattern` |
| (generated by rai discover) | `tmpl-module-doc` | Via `rai docs publish module` |

### Sync Direction

```
.raise/templates/ (canonical)
       |
       | rai docs publish (one-way push)
       v
Confluence templates + pages (visibility layer)
```

Template registration in Confluence happens once during project setup (`rai init --stack atlassian`). Ongoing sync is artifact-by-artifact via `rai docs publish {type}`.

---

## 8. Skills-as-Pages Model

### Concept Validation

The skills-as-pages model was first proposed in RAISE-273 research and validated by the E275 implementation of rai-server. The core insight:

> **Skill definitions are knowledge artifacts, not code.** They belong in Confluence where governance teams can read, edit, and approve them -- and where Rovo agents can read them natively without custom indexing.

### How It Works

```
Filesystem (canonical)              Confluence (collaboration)
.claude/skills/                     Skills/
  rai-story-implement/                Lifecycle Skills/
    skill.md (prompt + phases)          rai-story-implement (page)
    metadata.yaml (triggers)
                                    Rovo reads page natively
       |                                    |
       | rai docs publish skill             | Rovo agent action
       v                                    v
  Confluence page                   Agent executes skill
  (structured, searchable)          with governance context
```

### Skill Page Structure

Each skill becomes a Confluence page with:

1. **Metadata panel** (Confluence properties or structured table at top):
   - Name, category, trigger conditions
   - Prerequisites (gates)
   - Last synced from filesystem (timestamp)

2. **Purpose section**: When and why to use this skill

3. **Phase definitions**: Ordered list of phases with:
   - Phase name
   - Inputs (what the phase needs)
   - Actions (what the phase does)
   - Outputs (what the phase produces)
   - Validation criteria

4. **Governance integration**: Which guardrails apply, which gates are checked

5. **Examples**: Worked invocation examples

### Governance Team Workflow

1. **Read skill page** in Confluence -- understand what the skill does
2. **Comment** with suggested changes -- "Phase 3 should also check security policy"
3. **Edit the page** directly (if they have write access) -- add a guardrail reference
4. **Sync back** to filesystem happens manually (governance team opens PR or skill owner syncs)

**Important limitation:** Confluence-to-filesystem sync is NOT automatic. The filesystem remains canonical. Confluence edits are proposals that must be merged via the normal code review process. This preserves git-based governance while enabling non-developer collaboration.

### Rovo Agent Integration

Rovo agents consume skill pages via native Confluence search:

```
1. User invokes Rovo agent: "help me implement this story"
2. Rovo agent queries: CQL "space = RaiSE1 AND label = skill AND title ~ story-implement"
3. Rovo reads the skill page content natively (no custom indexing)
4. Agent follows the phase definitions from the page
5. Agent queries rai-server for knowledge graph context (governance, patterns)
6. Agent executes, referencing both skill structure and governance rules
```

### Skill Categories in Confluence

| Category | Confluence Section | Skills |
|----------|-------------------|--------|
| **Lifecycle** | `Skills/Lifecycle Skills/` | session-start, session-close, epic-start, epic-design, epic-plan, epic-close, story-start, story-design, story-plan, story-implement, story-review, story-close |
| **Discovery** | `Skills/Discovery Skills/` | discover, discover-scan, discover-validate |
| **Meta** | `Skills/Meta Skills/` | skill-create, skillset-manage, framework-sync |
| **Operational** | `Skills/Operational Skills/` | debug, doctor, publish, research, quality-review, architecture-review, code-audit |
| **Orchestration** | `Skills/Orchestration Skills/` | epic-run, story-run, bugfix |
| **Onboarding** | `Skills/Onboarding Skills/` | welcome, project-create, project-onboard |

---

## 9. Adapter Alignment

### Current State: `McpConfluenceAdapter`

The `McpConfluenceAdapter` (in `raise-pro`) wraps the Sooperset MCP Atlassian server. It supports:
- `rai docs publish` -- create/update Confluence pages
- `rai docs get` -- retrieve page content
- `rai docs search` -- CQL search

### What the Adapter Needs to Support This IA

| Capability | Current State | Required | Gap |
|------------|--------------|----------|-----|
| **Create page with parent** | Supported | Required | None |
| **Create page with labels** | Not supported | Required | **GAP: Must add label assignment on page creation** |
| **Update page labels** | Not supported | Required | **GAP: Must add label management** |
| **Page tree creation** (batch) | Not supported | Nice-to-have | GAP: Batch create for `rai init --stack atlassian` |
| **Template registration** | Not supported | Required for setup | **GAP: Must support space template CRUD** |
| **Publish by artifact type** | Partially (generic publish) | Required | **GAP: Must route `rai docs publish {type}` to correct tree location** |
| **Index page generation** | Not supported | Required | **GAP: Auto-generate ADR Index, Pattern Catalog, Skill Index** |
| **Content properties** | Not supported | Nice-to-have | GAP: Machine-readable metadata on pages |
| **Attachment support** | Not supported | Nice-to-have | GAP: Diagrams, images |

### `rai docs publish` Command Mapping

The `rai docs publish` command must map artifact types to the correct Confluence tree location:

| Command | Source | Target Location | Labels |
|---------|--------|----------------|--------|
| `rai docs publish governance` | `.raise/governance/*.md` | `Governance/{name}` | `governance`, `type:policy` |
| `rai docs publish adr` | ADR files | `Architecture/ADR-{NNN}: {title}` | `adr`, `status:{state}` |
| `rai docs publish epic-scope` | `work/epics/{id}/scope.md` | `Epics/{KEY}/Scope` | `epic`, `epic:{key}`, `type:scope` |
| `rai docs publish epic-retro` | `work/epics/{id}/retrospective.md` | `Epics/{KEY}/Retrospective` | `epic`, `epic:{key}`, `type:retro` |
| `rai docs publish research` | Research markdown files | `Epics/{KEY}/Research/R{N}` or `Research/{id}` | `research`, `confidence:{level}` |
| `rai docs publish skill` | `.claude/skills/{name}/` | `Skills/{category}/{name}` | `skill`, `skill-category:{cat}` |
| `rai docs publish pattern` | `.raise/rai/memory/patterns.jsonl` | `Patterns/PAT-E-{NNN}` | `pattern`, `pattern-type:{type}` |
| `rai docs publish module` | `rai discover` output | `Architecture/Module Documentation/mod-{name}` | `module`, `component:{comp}` |
| `rai docs publish release-notes` | `CHANGELOG.md` section | `Releases/Release Notes — v{X.Y.Z}` | `release`, `version:{ver}` |
| `rai docs publish session` | Session JSONL | `Sessions/Session Archive — {date}` | `session`, `agent:{name}` |
| `rai docs publish glossary` | Graph term nodes | `Glossary/` | `glossary` |

### Adapter Gap Summary (feeds S760.7)

| Gap ID | Description | Priority | Effort |
|--------|-------------|----------|--------|
| **GAP-C1** | Label management (add/remove labels on page create/update) | P1 (required) | S |
| **GAP-C2** | Artifact-type routing (publish command maps type to tree location) | P1 (required) | M |
| **GAP-C3** | Index page generation (ADR Index, Pattern Catalog, Skill Index) | P1 (required) | M |
| **GAP-C4** | Space template registration | P2 (setup) | S |
| **GAP-C5** | Batch page tree creation for `rai init --stack atlassian` | P2 (setup) | M |
| **GAP-C6** | Content properties for machine-readable metadata | P3 (post-MVP) | S |
| **GAP-C7** | Attachment support for diagrams | P3 (post-MVP) | S |

---

## 10. Current RaiSE1 Space Audit

### Observed Structure (2026-03-27)

The current RaiSE1 space has **no structured page tree**. All 40+ pages are organized ad-hoc, with implicit grouping by epic (child pages under epic root pages) but no top-level sections.

**What exists today:**

| Content Type | Count | Organization | Matches IA? |
|-------------|-------|-------------|-------------|
| Epic hub pages | ~5 | Top-level, children underneath | Partially -- needs `Epics/` section |
| Research reports | ~8 | Under epic pages | Yes -- matches epic-scoped research |
| ADRs | ~2 | Top-level, no index | Needs `Architecture/` section |
| Product vision/strategy | ~5 | Top-level, scattered | Needs categorization |
| Developer docs (epic-docs) | ~5 | Under epic pages | Matches design |
| Setup/operational guides | ~4 | Top-level | Needs `Operations/` section |
| Problem briefs | ~3 | Top-level | Should be under `Epics/` |
| Release notes | ~1 | Top-level | Needs `Releases/` section |
| Bug analysis (Ishikawa) | ~1 | Top-level | Needs categorization |
| Partner plans | ~1 | Top-level | Needs categorization |

### Migration to IA

Phase 1 (during S760.4 or immediately after):
1. Create top-level section pages: Governance, Architecture, Epics, Research, Skills, Patterns, Glossary, Templates, Releases, Operations, Sessions
2. Move existing pages into correct sections
3. Apply labels to all existing pages
4. Create index pages (ADR Index, Pattern Catalog, Skill Index)

Phase 2 (with adapter updates):
5. Register Confluence space templates
6. Update `rai docs publish` to route to correct locations
7. Publish skills as pages
8. Generate pattern pages from JSONL

---

## 11. Evidence and References

| ID | Source | Evidence Level | Relevance |
|----|--------|---------------|-----------|
| R1 | R1-RAISE-760: Atlassian API Landscape | Very High | Confluence API capabilities, rate limits, content formats |
| R2 | R2-RAISE-760: Python Ecosystem | Very High | Adapter architecture, MCP server capabilities |
| R3 | R3-RAISE-760: Value Map | Very High | Artifact mapping matrix, 7 of 15 artifact types map to Confluence |
| R4 | R4-RAISE-760: Forge Deep-Dive | Very High | Rovo agent integration, Forge storage limitations |
| E3 | RAISE-273 research | Very High | Three-layer architecture, skills-as-pages model validated |
| E4 | E275 implementation | Very High | rai-server APIs for graph sync, pattern sharing |
| E5 | PAT-E-593 | High | CQL search does not index spaces with unusual mixed-case keys |
| E6 | Current RaiSE1 space (40+ pages) | Direct observation | Current state audit |
| E7 | `.raise/templates/` (10+ templates) | Direct observation | Template inventory for Confluence mapping |
| E8 | `.claude/skills/` (30+ skills) | Direct observation | Skill inventory for skills-as-pages |
| E9 | Atlassian Confluence best practices | Official docs | Space structure, template management, CQL syntax |

---

## 12. Open Questions

1. **CQL space key limitation (PAT-E-593):** The `RaiSE1` key works for `get_page` but CQL `siteSearch` may not index it reliably due to mixed case. Should we migrate to a simple key like `RAISE` or accept the limitation?

2. **Session archive granularity:** Per-session pages will proliferate quickly (multiple sessions per day). Should we use daily/weekly rollup pages instead? Recommendation: weekly rollups for archive, with per-session data as expandable sections within the rollup.

3. **Confluence-to-filesystem sync:** The current design is one-way (filesystem -> Confluence). Should we eventually support Confluence edits syncing back to git? This would require conflict resolution and is architecturally complex. Recommendation: defer to post-MVP; use Confluence comments/suggestions as the feedback mechanism.

4. **Template registration automation:** Can `rai init --stack atlassian` automatically create Confluence space templates via API? The Confluence REST API supports template CRUD but it's not exposed in the MCP server. May require direct API call in the adapter.

---

## Appendix A: Complete Artifact-to-Location Quick Reference

| Artifact | Filesystem Path | Confluence Path | Base Label |
|----------|----------------|-----------------|------------|
| Code standards | `.raise/governance/code-standards.md` | `Governance/Code Standards` | `governance` |
| Guardrails | `.raise/governance/guardrails/*.md` | `Governance/Guardrails/{name}` | `governance` |
| ADR | Varies | `Architecture/ADR-{NNN}: {title}` | `adr` |
| Architecture overview | `.raise/templates/architecture/architecture-overview.md` | `Architecture/Architecture Overview` | `module` |
| Module docs | `.raise/docs/modules/` | `Architecture/Module Documentation/mod-{name}` | `module` |
| Epic scope | `work/epics/{id}/scope.md` | `Epics/{KEY}: {title}/Scope` | `epic` |
| Epic design | `work/epics/{id}/design.md` | `Epics/{KEY}: {title}/Design` | `epic` |
| Epic plan | `work/epics/{id}/plan.md` | `Epics/{KEY}: {title}/Plan` | `epic` |
| Epic retro | `work/epics/{id}/retrospective.md` | `Epics/{KEY}: {title}/Retrospective` | `epic` |
| Epic dev docs | Generated by /rai-epic-docs | `Epics/{KEY}: {title}/Developer Documentation` | `epic` |
| Research (epic) | `work/epics/{id}/research/` | `Epics/{KEY}: {title}/Research/R{N}` | `research` |
| Research (standalone) | `work/research/` | `Research/{id} — {title}` | `research` |
| Story page | `work/epics/{id}/stories/` | `Epics/{KEY}: {title}/Stories/S{N}.{M}` | `epic` |
| Skill definition | `.claude/skills/{name}/` | `Skills/{category}/{name}` | `skill` |
| Pattern | `.raise/rai/memory/patterns.jsonl` | `Patterns/PAT-E-{NNN}: {summary}` | `pattern` |
| Glossary | Graph nodes (type: term) | `Glossary/` | `glossary` |
| Release notes | `CHANGELOG.md` | `Releases/Release Notes — v{X.Y.Z}` | `release` |
| Session archive | `.raise/rai/sessions/` | `Sessions/Session Archive — {date}` | `session` |
| Setup guides | Various | `Operations/{title}` | N/A |
| Templates catalog | `.raise/templates/` | `Templates/` (catalog page) | N/A |
