# RAISE-863: Confluence IA Grooming — Scope

**Jira:** RAISE-863
**Labels:** confluence, governance, documentation
**Branch:** release/2.4.0
**Design source:** S760.4 (work/epics/RAISE-760/confluence-ia-design.md)

## Objective

Apply the Confluence Information Architecture designed in S760.4 to the RaiSE1
space. Transform ~40+ flat pages into a structured, navigable page tree with
consistent naming, labels, and index pages.

## Current State

~40+ pages, all at root level. No sections, no hierarchy. Mix of:
- Epic scopes and stories (RAISE-760, RAISE-789, RAISE-706, RAISE-783)
- Research reports (R1-R4, S789.x)
- Design documents (S760.x)
- Developer documentation (E680, E654, E494, E478)
- ADRs (ADR-033, ADR-034)
- Product/strategy docs (rai-agent vision, Forge brief, capability cockpit)
- Setup guides (Windows 11 install)
- Release notes (v2.3.0)
- Sales/client content (Inter BigPicture report)

## Target State (from S760.4)

```
RaiSE1 (Space Root)
├── Governance
├── Architecture
│   ├── ADR Index
│   ├── ADR-033: Release Branch Model
│   ├── ADR-034: ...
│   └── Module Documentation
├── Epics
│   ├── RAISE-706: rai-agent Product Discovery
│   │   └── (phase pages as children)
│   ├── RAISE-760: RaiSE Project Management Model
│   │   └── (research, design, blueprint as children)
│   ├── RAISE-783: Session Management Reliability
│   │   └── (problem brief as child)
│   ├── RAISE-789: E-ANTHROPIC
│   │   └── (research stories as children)
│   └── ...
├── Research
│   └── (standalone research not under an epic)
├── Product
│   ├── rai-agent Product Vision
│   ├── RaiSE Capability Cockpit
│   ├── RaiSE Forge Product Brief
│   └── Visión de Producto: RaiSE sobre Atlassian
├── Developer Docs
│   ├── E494: ACLI Jira Adapter
│   ├── E654: Session Identity Fix
│   ├── E680: Release v2.3.0 Prep
│   └── E478: Pro/Community Boundary
├── Releases
│   └── Release Notes — v2.3.0
├── Operations
│   └── Instalación de RaiSE en Windows 11
└── Sales & Delivery
    └── Inter BigPicture Compliance Report
```

## Stories

### S863.1: Create Section Structure (XS)

Create the top-level section pages that form the page tree backbone:
- Governance, Architecture, Epics, Research, Product, Developer Docs,
  Releases, Operations, Sales & Delivery
- Each section page gets a brief description of what belongs there

**Deliverable:** 9 section pages created under space root

### S863.2: Organize Epics & Their Artifacts (M)

Move epic pages and their related artifacts under `Epics/{KEY}`:
- RAISE-706 + its 5 phase pages → Epics/RAISE-706
- RAISE-760 + research (R1-R4), designs (S760.x), blueprint → Epics/RAISE-760
- RAISE-783 + problem brief → Epics/RAISE-783
- RAISE-789 + research stories (S789.x), blog, enterprise implications → Epics/RAISE-789
- RAISE-806, RAISE-839, RAISE-840 (epic briefs) → Epics/{KEY}

**Deliverable:** All epic content nested under parent epic pages

### S863.3: Organize Architecture, Product & Developer Docs (S)

Move remaining pages to their sections:
- ADR-033, ADR-034 → Architecture
- rai-agent vision, capability cockpit, Forge brief, visión producto → Product
- E494, E654, E680, E478 developer docs → Developer Docs
- Release notes → Releases
- Windows install guide → Operations
- Inter report → Sales & Delivery

**Deliverable:** All non-epic pages in correct sections

### S863.4: Create Index Pages & Apply Labels (S)

- Create index tables in each section page (title, status, date)
- Apply label taxonomy from S760.4:
  - `type:adr`, `type:research`, `type:design`, `type:epic`, `type:devdoc`
  - `epic:{key}` for epic-scoped content
  - `release:{version}` where applicable

**Deliverable:** Navigable indexes, consistent labels across all pages

## In Scope (MUST)

- Create section page tree structure
- Move all existing pages to correct sections
- Apply naming conventions from S760.4
- Create basic index pages per section
- Apply label taxonomy

## In Scope (SHOULD)

- Brief description on each section page
- Consistent page title format across all pages

## Out of Scope

- Template creation → RAISE-830
- Confluence adapter alignment → RAISE-830
- Skills-as-pages → separate story
- Rovo agent configuration → post-grooming
- New content creation (only organize existing)
- Page content edits (only move/rename/label)

## Done Criteria

- [ ] All existing pages nested under a section (zero orphans at root)
- [ ] Section pages created with descriptions
- [ ] Index pages with tables listing contents
- [ ] Labels applied per taxonomy
- [ ] Page tree matches S760.4 design (adapted to current content)
