# Structure Analysis: Public Repository Readiness

**Feature**: 007-public-repo-readiness
**Date**: 2026-01-16
**Phase**: WP0 (Deep Content & Structure Audit)
**Status**: 🔄 IN PROGRESS - Awaiting Orquestador decisions

---

## Executive Summary

**Total Repository**: 254 Markdown files across multiple categories
**Decision Required**: Option C (Documentation Hub) with `.private/` folder

### Key Finding: Language Policy Needed

The repository mixes Spanish and English content. **Public content should be in English** per Orquestador requirement. This affects:
- Directory names (Spanish → English)
- Content translation (TBD)

---

## Part A: Complete Repository Inventory

### 📊 File Count by Location

| Location | Files | Category | Proposed |
|----------|-------|----------|----------|
| `docs/framework/v2.1/model/` | 29 | Mixed (see below) | Split public/private |
| `docs/framework/v2.1/adrs/` | 13 | Technical decisions | **PUBLIC** |
| `docs/framework/v2.1/katas/` | 6 | Internal prompts/tools | **PRIVATE** |
| `docs/framework/v2.1/reportes/` | 3 | Internal reports | **PRIVATE** |
| `src/katas-v2.1/` | 13 | Learning exercises | **PUBLIC** |
| `src/katas/` (legacy) | 26 | Deprecated katas | **ARCHIVE** |
| `src/gates/` | 6 | Validation gates | **PUBLIC** |
| `src/templates/` | 28 | Reusable templates | **PUBLIC** |
| `src/agents/` | 19 | Internal agent configs | **PRIVATE** |
| `docs/archive/` | 18 | Historical v1.x | **ARCHIVE** |
| `docs/research/` | 3 | Internal research | **PRIVATE** |
| `docs/stack/` | 3 | Implementation guides | **PUBLIC** |
| `specs/` | 66 | Development specs | **PRIVATE** |
| **TOTAL** | **254** | | |

---

## Part B: Content Classification (Detailed)

### ✅ PUBLIC: Core Ontology (`docs/framework/v2.1/model/`) - 18 files

These form the foundation of RaiSE and are essential for F&F users:

| File | Purpose |
|------|---------|
| `00-constitution-v2.md` | Core principles and philosophy |
| `01-product-vision-v2.1.md` | Product vision statement |
| `05-learning-philosophy-v2.md` | Heutagogy approach |
| `10-system-architecture-v2.1.md` | System architecture |
| `11-data-architecture-v2.1.md` | Data model |
| `12-integration-patterns-v2.1.md` | Integration patterns |
| `12-kata-schema-v2.1.md` | Kata structure definition |
| `13-security-compliance-v2.1.md` | Security considerations |
| `15-tech-stack-v2.1.md` | Technology stack |
| `20-glossary-v2.1.md` | **Canonical terminology** |
| `20a-glossary-seed.md` | Glossary seed document |
| `21-methodology-v2.md` | RaiSE methodology |
| `22-templates-catalog-v2.md` | Templates catalog |
| `23-commands-reference-v2.1.md` | Commands reference |
| `24-examples-library-v2.1.md` | Examples library |
| `25-ontology-bundle-v2_1.md` | Ontology bundle |
| `26-work-cycles-v2.1.md` | Work cycles |
| `38-commands-reference-consolidated.md` | Commands consolidated |

---

### 🔒 PRIVATE: Internal Documents (`docs/framework/v2.1/model/`) - 11 files

Business, planning, and work artifacts that should NOT be public:

| File | Reason for Private |
|------|-------------------|
| `02-business-model-v2.md` | Business stakeholder content |
| `03-market-context-v2.md` | Market analysis, internal |
| `04-stakeholder-map-v2.md` | Internal org information |
| `30-roadmap-v2.1.md` | Internal planning |
| `31-current-state-v2.1.md` | Internal status tracking |
| `32-session-log-v2.md` | Work artifact |
| `33-issues-decisions-v2.md` | Internal tracking |
| `34-dependencies-blockers-v2.md` | Internal issues |
| `35-ontology-backlog-v2.md` | Internal backlog |
| `36-roadmap-tecnico-mvp.md` | Technical roadmap |
| `37-roadmap-tecnico-mvp-legacy.md` | Legacy planning |

---

### ✅ PUBLIC: Architecture Decision Records - 13 files

| File | Topic |
|------|-------|
| `adr-000-index.md` | ADR Index |
| `adr-001-python-cli.md` | Python CLI decision |
| `adr-002-git-distribution.md` | Git distribution |
| `adr-003-mcp-protocol.md` | MCP protocol |
| `adr-004-markdown-json.md` | Markdown + JSON format |
| `adr-005-local-first.md` | Local-first approach |
| `adr-006-dod-fractales.md` | DoD fractals |
| `adr-006a-validation-gates.md` | Validation Gates |
| `adr-007-guardrails.md` | Guardrails |
| `adr-008-observable-workflow.md` | Observable workflow |
| `adr-009-shuhari-hybrid.md` | Shu-Ha-Ri hybrid |
| `adr-010-cli-ontology.md` | CLI ontology |
| `adr-011-hybrid-kata-template-gate.md` | Hybrid Kata model |

---

### ⚠️ CRITICAL: Two Different "Katas" Locations

**These are NOT duplicates - they are DIFFERENT content types:**

#### `src/katas-v2.1/` - DEFAULT PROCESS TEMPLATES (13 files) → **PUBLIC**

**These are NOT training exercises.** Katas are process definitions that describe HOW to execute each phase of the RaiSE methodology. They are default templates from HumanSys that users adapt for their own projects.

The relationship is:
```
TEMPLATE (what to produce) → KATA (how to do it) → VALIDATION GATE (quality check)
```

Like martial arts katas, these are forms/patterns that practitioners execute and adapt to their context:

```
src/katas-v2.1/
├── README.md                           # Index of katas (Spanish)
├── principios/                         # Principles level (Spanish dir name)
│   ├── 00-meta-kata.md                # What is a kata?
│   └── 01-execution-protocol.md       # 7-step execution protocol
├── flujo/                              # Flow level (Spanish dir name)
│   ├── 01-discovery.md                # Discovery → PRD
│   ├── 02-solution-vision.md          # Solution Vision
│   ├── 03-tech-design.md              # Tech Design
│   ├── 04-implementation-plan.md      # Implementation Plan
│   ├── 05-backlog-creation.md         # Backlog Creation
│   └── 06-development.md              # Development
├── patron/                             # Pattern level (Spanish dir name)
│   ├── 01-code-analysis.md            # Code analysis pattern
│   ├── 02-ecosystem-discovery.md      # Ecosystem discovery
│   ├── 03-tech-design-stack-aware.md  # Stack-aware design
│   └── 04-dependency-validation.md    # Dependency validation
└── tecnica/                            # Technique level (empty)
```

**Language Issue**: Directory names and content are in Spanish.

---

#### `docs/framework/v2.1/katas/` - INTERNAL PROMPTS/TOOLS (6 files) → **PRIVATE**

Meta-content and prompts for ontology development work, NOT learning exercises:

| File | Content Type |
|------|--------------|
| `kata-L0-validacion-ontologica-v2.md` | Prompt for corpus validation |
| `kata-shuhari-schema-v2.1.md` | Schema definition for Shu-Ha-Ri |
| `kata-refinamiento-ontologico.md` | Ontology refinement process |
| `prompt-esceptico-informado-raise.md` | Skeptical review prompt |
| `prompt-procesar-transcript.md` | Transcript processing prompt |
| `PROMPT-CONTINUACION-P2.md` | Continuation prompt |

**These are internal tools, NOT user-facing katas.**

---

### ✅ PUBLIC: Validation Gates - 6 files

Used by katas for quality verification:

| File | Phase |
|------|-------|
| `gate-discovery.md` | Phase 1 - PRD validation |
| `gate-vision.md` | Phase 2 - Vision validation |
| `gate-design.md` | Phase 3 - Design validation |
| `gate-backlog.md` | Phase 4 - Backlog validation |
| `gate-plan.md` | Phase 5 - Plan validation |
| `gate-code.md` | Phase 6 - Code validation |

---

### ✅ PUBLIC: Templates - 28 files

Reusable document templates for RaiSE workflow:

| Category | Files | Examples |
|----------|-------|----------|
| `backlog/` | 5 | user_story.md, epic.md, bug.md |
| `solution/` | 6 | solution-vision-template.md, project_requirements.md |
| `tech/` | 3 | tech_design.md, api_spec.md, component_spec.md |
| `cursor-rules/` | 5 | template-repo-architecture.md, template-meta-rule.md |
| `sar/` | 9 | Software Architecture Review templates |

**Note**: Some templates have Spanish versions (`*_es.md`).

---

### 🔒 PRIVATE: Agent Configurations - 19 files

Internal prompts and docs for AI agents:

| Agent | Files | Content |
|-------|-------|---------|
| `cursor-rules-engineer/` | 7 | Prompts and guides for Cursor rules |
| `raise-coder/` | 4 | RaiSE Coder agent prompts |
| `raise-architect/` | 5 | RaiSE Architect prompts and research |
| `raise-tech-lead/` | 1 | Tech Lead system prompt |
| `transcript-analyst/` | 2 | Transcript analysis prompts |

---

### 🗄️ ARCHIVE: Legacy Katas - 26 files

Deprecated katas with old L0-L3 naming convention:

- Has `DEPRECATED.md` marker
- Uses old terminology (L0, L1, L2, L3 levels)
- Contains specialized katas (cursor_rules, flujo, patron, etc.)
- **Keep in archive for reference but clearly marked deprecated**

---

### 🔒 PRIVATE: Other Internal Content

| Location | Files | Reason |
|----------|-------|--------|
| `docs/research/` | 3 | Internal research notes |
| `docs/framework/v2.1/reportes/` | 3 | Internal validation reports |
| `specs/` | 66 | Active development work (spec-kit) |

### ✅ PUBLIC: Implementation Guides

| Location | Files | Content |
|----------|-------|---------|
| `docs/stack/agents/claude-code/` | 3 | Claude Code implementation guides |

---

## Part C: Language Policy Decision Required

### Current State

| Content | Language |
|---------|----------|
| Core model documents | Spanish |
| Katas (src/katas-v2.1/) | Spanish (content + directory names) |
| Katas README | Spanish |
| Templates | Mixed (some have `_es` versions) |
| ADRs | Spanish |
| Glossary | Spanish |

### Orquestador Requirement

> "Todo lo público debe ser en inglés"

### Options

1. **Directory names only** → Rename `principios/` to `principles/`, etc.
2. **Full translation** → Translate all public content to English
3. **Bilingual with English primary** → English directories, Spanish content acceptable

**Decision Required**: Which option?

---

## Part D: Proposed Structure (Option C - Documentation Hub)

### Design Principles for Developer Experience

1. **Cognitive Simplicity**: Directory names explain content at a glance
2. **Clear Triad**: The Template → Kata → Gate relationship is visible in structure
3. **Shallow Depth**: Maximum 3 levels deep for any content
4. **Canonical Terms**: Use RaiSE vocabulary consistently (`katas/` not `exercises/`)
5. **Flat Hierarchy**: Related content grouped together, not scattered

### The RaiSE Triad (Core Mental Model)

Developers should immediately understand this relationship:

```
┌─────────────────────────────────────────────────────────────────┐
│   docs/templates/         docs/katas/         docs/gates/       │
│   ─────────────          ───────────         ──────────         │
│   WHAT to produce        HOW to do it        IS IT GOOD?        │
│                                                                 │
│   Artifact structure     Process steps       Quality criteria   │
│   (the deliverable)      (the workflow)      (the checkpoint)   │
└─────────────────────────────────────────────────────────────────┘

Example: Discovery Phase
  templates/solution/project_requirements.md  →  PRD structure
  katas/flow/discovery.md                     →  How to create it
  gates/gate-discovery.md                     →  Validation criteria
```

### Proposed Structure (Optimized for DX)

```
raise-commons/
│
├── README.md                           # Entry point: What is RaiSE, how to start
├── LICENSE                             # Apache 2.0
├── CONTRIBUTING.md                     # How to contribute
│
├── docs/                               # ═══ ALL PUBLIC CONTENT ═══
│   │
│   ├── core/                           # Foundation (read these first)
│   │   ├── constitution.md             # Core principles
│   │   ├── glossary.md                 # Canonical terminology
│   │   └── methodology.md              # How RaiSE works
│   │
│   ├── katas/                          # ═══ THE HOW (process definitions) ═══
│   │   ├── README.md                   # What are katas, how to use them
│   │   ├── principles/                 # Meta-level: why & when
│   │   │   ├── meta-kata.md
│   │   │   └── execution-protocol.md
│   │   ├── flow/                       # Phase-based: the workflow sequence
│   │   │   ├── discovery.md           # Phase 1: Problem → PRD
│   │   │   ├── solution-vision.md     # Phase 2: PRD → Vision
│   │   │   ├── tech-design.md         # Phase 3: Vision → Design
│   │   │   ├── backlog-creation.md    # Phase 4: Design → Backlog
│   │   │   ├── implementation-plan.md # Phase 5: Backlog → Plan
│   │   │   └── development.md         # Phase 6: Plan → Code
│   │   ├── patterns/                   # Reusable: specialized workflows
│   │   │   ├── code-analysis.md       # Brownfield analysis
│   │   │   ├── ecosystem-discovery.md # Integration mapping
│   │   │   ├── tech-design-stack.md   # Stack-aware design
│   │   │   └── dependency-validation.md
│   │   └── techniques/                 # Specific: detailed how-tos (future)
│   │
│   ├── templates/                      # ═══ THE WHAT (artifact structures) ═══
│   │   ├── backlog/                    # User stories, epics, bugs
│   │   ├── solution/                   # PRD, vision, SOW
│   │   ├── tech/                       # Tech design, API specs
│   │   └── sar/                        # Architecture review
│   │
│   ├── gates/                          # ═══ THE QUALITY (validation criteria) ═══
│   │   ├── gate-discovery.md           # Phase 1 checkpoint
│   │   ├── gate-vision.md              # Phase 2 checkpoint
│   │   ├── gate-design.md              # Phase 3 checkpoint
│   │   ├── gate-backlog.md             # Phase 4 checkpoint
│   │   ├── gate-plan.md                # Phase 5 checkpoint
│   │   └── gate-code.md                # Phase 6 checkpoint
│   │
│   ├── decisions/                      # ADRs (architectural decisions)
│   │   ├── index.md
│   │   └── adr-*.md
│   │
│   ├── guides/                         # Implementation guides
│   │   └── claude-code/
│   │
│   └── reference/                      # Additional reference (optional)
│       ├── architecture.md             # System architecture
│       ├── kata-schema.md              # Kata structure definition
│       └── ...
│
├── .private/                           # ═══ ALL INTERNAL CONTENT ═══
│   ├── README.md                       # Index of internal docs
│   │
│   ├── business/                       # Business docs (3 files)
│   │   ├── business-model.md
│   │   ├── market-context.md
│   │   └── stakeholder-map.md
│   │
│   ├── planning/                       # Roadmaps and status
│   │   └── [roadmap files]
│   │
│   ├── work-artifacts/                 # Session logs, tracking
│   │   └── [work logs]
│   │
│   ├── tools/                          # Internal prompts
│   │   └── [ontology tools]
│   │
│   ├── agents/                         # Agent configurations
│   │   └── [all agent configs]
│   │
│   ├── research/                       # Research notes
│   │   └── [research docs]
│   │
│   ├── reports/                        # Internal reports
│   │   └── [validation reports]
│   │
│   ├── archive/                        # Historical content
│   │   ├── v1-framework/              # Old framework docs
│   │   └── legacy-katas/              # Deprecated L0-L3 katas
│   │
│   └── current-docs/                   # Docs moved from public (historical)
│       └── [archived model docs]
│
├── specs/                              # spec-kit work (unchanged, internal)
├── .specify/                           # spec-kit config (unchanged)
├── .raise/                             # RaiSE agent config (unchanged)
├── .claude/                            # Claude commands (unchanged)
│
└── CLAUDE.md                           # Internal development guide
```

### Why This Structure Works

| Design Choice | Rationale |
|---------------|-----------|
| **`katas/` not `exercises/`** | Uses canonical RaiSE term; katas are process definitions, not training |
| **Triad at same level** | `katas/`, `templates/`, `gates/` siblings show relationship clearly |
| **`core/` first** | Constitution, Glossary, Methodology = starting point |
| **Simple file names** | `discovery.md` not `01-discovery.md` - numbers removed for clarity |
| **English directories** | `principles/`, `flow/`, `patterns/` (not Spanish) |
| **Flat `.private/`** | All internal content in one hidden location |
| **`reference/` optional** | Detailed docs moved here if not essential |

---

## Part E: Decisions Required from Orquestrador

### Previously Confirmed Decisions ✅

| Decision | Choice | Source |
|----------|--------|--------|
| Structure | **Option C** (Documentation Hub) | Earlier conversation |
| Non-public content | Move to **`.private/`** | Earlier conversation |
| Archives | Move to **`.private/archive/`** | Earlier conversation |
| Terminology | Use **`katas/`** not `exercises/` | Earlier conversation |

---

### Decisions Confirmed ✅

#### Decision 1: Language Policy ✅

**Choice**: English for all new content with RaiSE Brand Voice
- New documentation: American English
- File names and directories: Always English
- Existing Spanish content: Acceptable for F&F (translation is future phase)

---

#### Decision 2: File Naming ✅

**Choice**: Option A - Simplified English names
- Remove version prefixes: `constitution.md` not `00-constitution-v2.md`
- Clean URLs and cognitive simplicity

---

#### Decision 3: Internal Tools ✅

**Choice**: Move to `.private/tools/`
- The 6 files in `docs/framework/v2.1/katas/` are internal ontology prompts
- Not user-facing katas

---

#### Decision 4: Implementation Scope ✅

**Choice**: Option A - Full restructure
- Move and rename all files per new structure
- Update internal links
- Complete reorganization for F&F launch

---

## Part F: File Count Summary (Revised)

### After Restructuring

| Category | Files | New Location |
|----------|-------|--------------|
| **PUBLIC** | | **`docs/`** |
| Core (constitution, glossary, methodology) | 3 | `docs/core/` |
| Katas (process definitions) | 13 | `docs/katas/` |
| Validation Gates | 6 | `docs/gates/` |
| Templates | 28 | `docs/templates/` |
| ADRs | 13 | `docs/decisions/` |
| Implementation Guides | 3 | `docs/guides/` |
| Reference (architecture, etc.) | ~12 | `docs/reference/` |
| **PUBLIC TOTAL** | **~78** | |
| | | |
| **PRIVATE** | | **`.private/`** |
| Business docs | 3 | `.private/business/` |
| Planning/Roadmaps | 5 | `.private/planning/` |
| Work artifacts (logs, tracking) | 4 | `.private/work-artifacts/` |
| Internal tools (prompts) | 6 | `.private/tools/` |
| Agent configs | 19 | `.private/agents/` |
| Research notes | 3 | `.private/research/` |
| Reports | 3 | `.private/reports/` |
| Legacy katas (L0-L3) | 26 | `.private/archive/legacy-katas/` |
| Archive (v1.x framework) | 18 | `.private/archive/v1-framework/` |
| **PRIVATE TOTAL** | **~87** | |
| | | |
| **INTERNAL (unchanged)** | | |
| specs/ | 66 | `specs/` |
| .specify/, .raise/, .claude/ | ~35 | (tooling dirs) |
| **INTERNAL TOTAL** | **~101** | |
| | | |
| **GRAND TOTAL** | **~266** | |

### Migration Summary

```
Current                                →  New Location
──────────────────────────────────────────────────────────────────
docs/framework/v2.1/model/ (public)    →  docs/core/, docs/reference/
docs/framework/v2.1/model/ (private)   →  .private/business/, planning/, etc.
docs/framework/v2.1/adrs/              →  docs/decisions/
docs/framework/v2.1/katas/ (prompts)   →  .private/tools/
docs/framework/v2.1/reportes/          →  .private/reports/
src/katas-v2.1/                        →  docs/katas/
src/katas/ (legacy)                    →  .private/archive/legacy-katas/
src/gates/                             →  docs/gates/
src/templates/                         →  docs/templates/
src/agents/                            →  .private/agents/
docs/archive/                          →  .private/archive/v1-framework/
docs/research/                         →  .private/research/
docs/stack/                            →  docs/guides/
```

---

## Part G: Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Spanish content in public | Decision 1 defines policy; English dirs minimum |
| Katas terminology confusion | Use `katas/` not `exercises/`; clear README explains |
| Broken links | Update all internal links during migration |
| Lost content | Move to `.private/`, never delete |
| User confusion on entry | Clear README with triad navigation |
| Complex restructure | Phase approach available (Decision 4) |

---

## Status

**Phase**: WP1/WP2 Complete ✅
**Katas Understanding**: Corrected ✅ (process definitions, not training)
**Structure**: Option C implemented ✅
**Brand Voice**: Established ✅
**All Decisions**: Confirmed ✅
**Entry Files**: Created ✅ (README.md, LICENSE, CONTRIBUTING.md)

---

## Migration Complete - Cleanup Pending

### New Structure (CREATED) ✅

```
✅ README.md                 # Entry point
✅ LICENSE                   # Apache 2.0
✅ CONTRIBUTING.md           # Contribution guide
✅ docs/README.md            # Docs landing page
✅ docs/BRAND-VOICE.md       # Brand voice guide
✅ docs/core/                # constitution, glossary, methodology
✅ docs/katas/               # Process definitions (English README)
✅ docs/gates/               # Validation gates
✅ docs/templates/           # Artifact templates
✅ docs/decisions/           # ADRs
✅ docs/reference/           # Technical reference
✅ docs/guides/              # Implementation guides
✅ .private/                 # Internal content
```

### Old Structure (TO BE REMOVED)

These directories contain duplicated content and should be removed for a clean public release:

| Directory | Status | Migrated To |
|-----------|--------|-------------|
| `src/katas-v2.1/` | REMOVE | `docs/katas/` |
| `src/katas/` | REMOVE | `.private/archive/legacy-katas/` |
| `src/gates/` | REMOVE | `docs/gates/` |
| `src/templates/` | REMOVE | `docs/templates/` |
| `src/agents/` | REMOVE | `.private/agents/` |
| `docs/framework/` | REMOVE | Distributed to new locations |
| `docs/archive/` | REMOVE | `.private/archive/v1-framework/` |
| `docs/research/` | REMOVE | `.private/research/` |
| `docs/stack/` | REMOVE | `docs/guides/` |

**Next Step**: Remove old directories to complete restructure

---

*Analysis updated: 2026-01-16*
*WP1/WP2 complete - cleanup phase next*
