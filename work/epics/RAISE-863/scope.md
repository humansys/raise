# RAISE-863: Confluence IA Grooming — Scope

**Jira:** RAISE-863
**Labels:** confluence, governance, documentation
**Branch:** release/2.4.0
**Design source:** S760.4 (work/epics/RAISE-760/confluence-ia-design.md)
**Research:** S863.0 spike (RAISE-865) — 12 sources, grounding adjustments

## Objective

Apply the Confluence Information Architecture designed in S760.4 to the RaiSE1
space, adjusted by research findings from S863.0. Transform ~40+ flat pages
into a structured, navigable page tree with consistent naming, labels, and
index pages.

## Design Constraints (from S863.0 research)

1. **Max 7-9 top-level sections** — community consensus is 6-8; only create
   sections with existing content (no empty aspirational sections)
2. **Max 3 levels of depth** — root > section > page. Epic subtrees: epic page
   > child pages (flat, no sub-sections like Research/ or Stories/)
3. **Parent pages, not folders** — folders are invisible to search and Rovo;
   all sections must be parent pages with index content
4. **Section pages must have content** — index table + brief description;
   no blank parent pages
5. **Rovo-friendly** — parent+children scoping works; labels enable CQL
   retrieval at query time; content quality matters most

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

## Target State (adjusted from S760.4 per S863.0 research)

```
RaiSE1 (Space Root)                          ← Level 0
│
├── Epics                                     ← Level 1 (section page with index)
│   ├── RAISE-706: rai-agent Product Discovery    ← Level 2 (epic page)
│   │   ├── Phase 1: Market Analysis                  ← Level 3 (max depth)
│   │   ├── Phase 2: User Research
│   │   ├── Phase 3: Value Proposition
│   │   ├── Phase 4: MVP Scope
│   │   └── Phase 5: Go-to-Market
│   ├── RAISE-760: RaiSE Project Management Model
│   │   ├── Research Summary & Strategic Recommendations
│   │   ├── R1 — Atlassian API Landscape 2026
│   │   ├── R2 — Python Atlassian Ecosystem 2026
│   │   ├── R3 — RaiSE ↔ Atlassian Value Map
│   │   ├── R4 — Forge Platform Deep-Dive 2026
│   │   ├── S760.2 — Taxonomy Design
│   │   ├── S760.3 — Workflow & Lifecycle Mapping
│   │   ├── S760.4 — Confluence Information Architecture
│   │   ├── S760.5 — Compass Capability Catalog Design
│   │   ├── S760.6 — Bitbucket Integration Design
│   │   ├── S760.7 — Adapter Gap Analysis
│   │   ├── S760.8 — Reference Blueprint
│   │   └── Visión de Producto: RaiSE sobre Atlassian
│   ├── RAISE-783: Session Management Reliability
│   │   └── Problem Brief — Session Management Reliability
│   ├── RAISE-789: E-ANTHROPIC
│   │   ├── E789 Scope — Research Design & Benchmark Framework
│   │   ├── RaiSE Blueprint — Framework Baseline 2026
│   │   ├── S789.1 — Context & Harness Patterns Research
│   │   ├── Research: Context & Harness Patterns (full report)
│   │   ├── Enterprise Design Implications
│   │   ├── S789.2 — Evaluation Patterns Research
│   │   ├── S789.3 — Tool & MCP Patterns Research
│   │   ├── S789.4 — Multi-Agent Patterns Research
│   │   ├── Blog: Lo que Anthropic recomienda...
│   │   └── RaiSE Capability Cockpit
│   ├── RAISE-806: E-PATTERNS (epic brief)
│   ├── RAISE-839: E-AGENT-PATTERNS (epic brief)
│   └── RAISE-840: E-CARTRIDGE-ABP (epic brief)
│
├── Architecture                              ← Level 1
│   ├── ADR-033: Release Branch Model             ← Level 2
│   └── ADR-034: Reformulación de P1
│
├── Product                                   ← Level 1
│   ├── rai-agent — Product Vision                ← Level 2
│   └── RaiSE Forge — Product Brief & Epic Structure
│
├── Developer Docs                            ← Level 1
│   ├── E494: ACLI Jira Adapter                   ← Level 2
│   ├── E654: Session Identity Fix
│   ├── E680: Release v2.3.0 Prep
│   └── E478: Pro/Community Boundary
│
├── Operations                                ← Level 1
│   └── Instalación de RaiSE en Windows 11       ← Level 2
│
├── Releases                                  ← Level 1
│   └── Release Notes — v2.3.0                    ← Level 2
│
└── Sales & Delivery                          ← Level 1
    └── Reporte BigPicture — Inter                ← Level 2
```

**Max depth: 3 levels** (root > section > page, or root > section > epic > child)

### Pages NOT in S760.4 that need placement

| Page | Decision |
|------|----------|
| RaiSE Capability Cockpit | Under Epics/RAISE-789 (produced during that epic) |
| Visión de Producto: RaiSE sobre Atlassian | Under Epics/RAISE-760 (produced during that epic) |
| Research: Personal Knowledge Graphs (RAISE-775) | Under Epics (needs parent epic page or standalone) |
| Research: OpenClaw Gateway Patterns (RAISE-774) | Under Epics (needs parent epic page or standalone) |
| Research: /rai-epic-docs Skill (RAISE-776) | Under Epics (needs parent epic page or standalone) |

### Deferred sections (no content exists yet)

Governance, Skills, Patterns, Glossary, Sessions, Templates — will be created
when first content arrives. NOT created as empty sections.

## Stories (revised)

### S863.0: Confluence IA Grounding Research (XS) — DONE

Spike: 12 sources, 3 questions answered. Adjustments to S760.4 documented.
Branch: story/s863.0/confluence-ia-research

### S863.1: Create Section Structure & Organize Epics (M)

Create the 7 section parent pages with index content, then move all epic-related
pages (~30 pages) under their parent epic pages in the Epics section.

Work:
1. Create 7 section pages (Epics, Architecture, Product, Developer Docs,
   Operations, Releases, Sales & Delivery) — each with brief description
2. Move each epic page under Epics section
3. Move epic child pages under their respective epic parent
4. Handle orphan research pages (RAISE-774, 775, 776) — create minimal
   parent epic pages if needed

**Deliverable:** 7 sections created, all epic content nested correctly

### S863.2: Organize Non-Epic Pages & Apply Labels (S)

Move remaining pages to their sections and apply label taxonomy.

Work:
1. Move ADRs → Architecture
2. Move product docs → Product
3. Move developer docs → Developer Docs
4. Move ops guides → Operations
5. Move release notes → Releases
6. Move sales content → Sales & Delivery
7. Apply labels per S760.4 taxonomy:
   - Base type: `epic`, `adr`, `research`, `design`, `devdoc`, `product`, `release`
   - Epic association: `epic:RAISE-760`, `epic:RAISE-789`, etc.
   - Artifact type: `type:scope`, `type:research`, `type:design`, `type:retro`
8. Update section pages with index tables

**Deliverable:** Zero orphan pages at root, labels applied, indexes populated

## In Scope (MUST)

- Create 7 section parent pages with index content
- Move all ~40 existing pages to correct sections
- Flatten epic subtrees to max 3 levels
- Apply label taxonomy from S760.4
- Index tables on each section page

## In Scope (SHOULD)

- Consistent page title format across all pages
- Verify no broken cross-links after moves

## Out of Scope

- Template creation → RAISE-830
- Confluence adapter alignment → RAISE-830
- Skills-as-pages → separate story
- Rovo agent configuration → post-grooming
- New content creation (only organize existing)
- Page content edits (only move/rename/label)
- Empty aspirational sections (Governance, Skills, Patterns, etc.)

## Done Criteria

- [ ] All existing pages nested under a section (zero orphans at root)
- [ ] 7 section pages created with descriptions and index tables
- [ ] Max 3 levels of depth respected everywhere
- [ ] Labels applied per taxonomy (base type + epic association minimum)
- [ ] Page tree matches adjusted S760.4 design
