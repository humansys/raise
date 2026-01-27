# Implementation Plan: Public Repository Readiness

**Branch**: `007-public-repo-readiness` | **Date**: 2026-01-16 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/007-public-repo-readiness/spec.md`

## Summary

Prepare raise-commons for public Friends & Family release by creating missing entry-point documentation (README.md, LICENSE, CONTRIBUTING.md), auditing existing documentation for terminology consistency and broken links, and ensuring clear navigation to core framework artifacts. This is a **documentation-focused feature** with no code implementation.

## Technical Context

**Language/Version**: Markdown (CommonMark spec)
**Primary Dependencies**: Git 2.0+, GitLab (platform)
**Storage**: Git repository (versioned Markdown files)
**Testing**: Manual audit + grep-based verification scripts
**Target Platform**: GitLab web interface + local clone
**Project Type**: Documentation repository (conceptual/ontological)
**Performance Goals**: N/A (static documentation)
**Constraints**: 2-day timeline for F&F launch; Spanish/English bilingual content acceptable
**Scale/Scope**: 76 existing Markdown documents; 3 new files to create; ~10 files to audit/modify

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*
*Reference: `.specify/memory/constitution.md`*

| Principio | Verificación | Estado |
|-----------|--------------|--------|
| I. Coherencia Semántica | Términos alineados con glosario v2.1; deprecated terms mapped | [x] |
| II. Governance como Código | Todos los artefactos versionados en Git; decisiones en ADRs | [x] |
| III. Validación en Cada Fase | Gates definidos: Link Audit, Terminology Audit, Security Scan | [x] |
| IV. Simplicidad | README conciso enfocado en 80% de casos; sin sobre-documentación | [x] |
| V. Mejora Continua | GitLab Issues habilitado para feedback F&F | [x] |

## Project Structure

### Documentation (this feature)

```text
specs/007-public-repo-readiness/
├── plan.md              # This file
├── research.md          # Phase 0: Repository state analysis
├── data-model.md        # Phase 1: Navigation structure design
├── quickstart.md        # Phase 1: README content draft
├── checklists/
│   └── requirements.md  # Specification quality checklist (PASSED)
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Repository Changes (implementation target)

```text
raise-commons/                    # Repository root
├── README.md                     # NEW: Primary entry point (FR-001)
├── LICENSE                       # NEW: Apache 2.0 (FR-003)
├── CONTRIBUTING.md               # NEW: Contribution guidelines (FR-008)
├── CLAUDE.md                     # EXISTS: Development guide (internal)
│
├── docs/
│   └── framework/v2.1/
│       ├── model/                # EXISTS: 29 core documents
│       │   ├── 00-constitution-v2.md
│       │   ├── 20-glossary-v2.1.md
│       │   └── 21-methodology-v2.md
│       ├── adrs/                 # EXISTS: 13 ADRs (indexed)
│       └── katas/                # EXISTS: 6 kata documents
│
├── src/
│   ├── katas-v2.1/              # EXISTS: Normalized v2.1 katas
│   │   ├── principios/
│   │   ├── flujo/
│   │   ├── patrón/
│   │   └── técnica/
│   ├── katas/                   # EXISTS: Legacy (DEPRECATED.md present)
│   └── templates/               # EXISTS: 20+ templates
│
└── docs/archive/                # EXISTS: v1.x archived content
```

**Structure Decision**: No structural changes needed. Focus is on adding entry-point files and auditing existing content for public readiness.

## Complexity Tracking

> No Constitution violations detected. All work aligns with principles.

| Aspect | Alignment | Notes |
|--------|-----------|-------|
| Simplicidad | ✅ | 3 new files, minimal modifications to existing docs |
| Coherencia | ✅ | All terminology aligned with v2.1 glossary |
| Governance | ✅ | All changes tracked in Git, documented in this plan |

---

## Phase 0: Research Summary

### Repository State Analysis

**What Exists (Ready for Public):**
- ✅ Comprehensive ontological model (29 documents in `docs/framework/v2.1/model/`)
- ✅ 13 ADRs indexed and well-organized
- ✅ Glossary v2.1 with canonical terminology
- ✅ Normalized Kata framework (Principio/Flujo/Patrón/Técnica)
- ✅ 20+ reusable templates
- ✅ Legacy content properly archived with DEPRECATED.md markers
- ✅ spec-kit configuration complete

**What's Missing (Blocking):**
- ❌ README.md - No entry point for first-time visitors
- ❌ LICENSE - No legal terms (Apache 2.0 specified)
- ❌ CONTRIBUTING.md - No contribution guidelines

**What Needs Verification:**
- ⚠️ Link integrity across 76 documents (manual audit)
- ⚠️ Terminology consistency (grep audit for deprecated terms)
- ⚠️ Sensitive information scan (API keys, internal URLs)

### Terminology Audit Results

| Deprecated Term | Canonical (v2.1) | Status |
|-----------------|------------------|--------|
| DoD | Validation Gate | 95% migrated; documented in ADR-006a |
| Rule | Guardrail | 95% migrated; documented in ADR-007 |
| Developer | Orquestador | 90% migrated |
| L0/L1/L2/L3 | Principio/Flujo/Patrón/Técnica | 85% migrated; mapping documented |

**Decision**: Remaining deprecated terms are in backward-compatibility contexts with explicit mapping. Acceptable for F&F release.

### Navigation Path Analysis

**Current State**: No clear entry point. Users must know to look at CLAUDE.md (internal) or navigate to `docs/framework/v2.1/model/`.

**Designed Navigation (2 clicks to core docs):**
```
README.md
├── [Quick Links] → Glossary, Constitution, Methodology
├── [Documentation] → docs/framework/v2.1/model/
├── [Decisions] → docs/framework/v2.1/adrs/
├── [Exercises] → src/katas-v2.1/
├── [Templates] → src/templates/
└── [Contributing] → CONTRIBUTING.md
```

---

## Phase 1: Design Artifacts

### 1. Navigation Structure (data-model.md)

**Primary Navigation Hierarchy:**

```yaml
Entry Points:
  - README.md: First-time visitor orientation
  - CONTRIBUTING.md: Contributor onboarding
  - docs/framework/v2.1/model/00-constitution-v2.md: Deep dive start

Quick Access (from README):
  Core Concepts:
    - Constitution: docs/framework/v2.1/model/00-constitution-v2.md
    - Glossary: docs/framework/v2.1/model/20-glossary-v2.1.md
    - Methodology: docs/framework/v2.1/model/21-methodology-v2.md

  Technical Reference:
    - ADRs: docs/framework/v2.1/adrs/adr-000-index.md
    - Architecture: docs/framework/v2.1/model/10-system-architecture-v2.1.md

  Practical Application:
    - Katas: src/katas-v2.1/README.md
    - Templates: src/templates/

  Meta:
    - License: LICENSE
    - Contributing: CONTRIBUTING.md
    - Issues: GitLab Issues URL
```

### 2. README.md Content Structure (quickstart.md)

```markdown
# RaiSE Commons

[One-line tagline explaining what RaiSE is]

## What is RaiSE?

[2-3 paragraphs explaining:]
- Problem: Challenges in AI-assisted software development
- Solution: RaiSE framework approach
- This repo: Conceptual/ontological foundation (not production code)

## Quick Start

| I want to... | Start here |
|--------------|------------|
| Understand RaiSE principles | [Constitution](docs/...) |
| Learn the terminology | [Glossary](docs/...) |
| See how it works | [Methodology](docs/...) |
| Practice with exercises | [Katas](src/katas-v2.1/) |
| Understand key decisions | [ADRs](docs/...) |

## Repository Structure

[Brief explanation of directory layout]

## RaiSE Ecosystem

This repository is part of a broader RaiSE ecosystem. [Brief acknowledgment without detailing other repos]

## Contributing

[Link to CONTRIBUTING.md, GitLab Issues]

## License

Apache 2.0 - See [LICENSE](LICENSE)
```

### 3. CONTRIBUTING.md Content Structure

```markdown
# Contributing to RaiSE Commons

## This is a Conceptual Repository

[Clarify: documentation/ontology, not code]

## How to Provide Feedback

- **Questions & Discussion**: Open a GitLab Issue
- **Bug Reports**: [Issue template guidance]
- **Suggestions**: [Process]

## Contribution Process

1. Open an Issue describing the change
2. Fork and create feature branch
3. Follow terminology guidelines (v2.1 Glossary)
4. Submit Merge Request

## Style Guidelines

- Use canonical v2.1 terminology
- Spanish or English acceptable
- Follow existing document structure
```

### 4. LICENSE Content

Standard Apache 2.0 license text with:
- Copyright: [Year] [Organization]
- Standard Apache 2.0 terms

### 5. Validation Gates for Implementation

| Gate | Validation Method | Pass Criteria |
|------|-------------------|---------------|
| Gate-Links | grep + manual verification | 0 broken internal links |
| Gate-Terminology | grep for deprecated terms | 0 uncontextualized deprecated terms in v2.1 docs |
| Gate-Secrets | grep for patterns | 0 API keys, credentials, internal URLs |
| Gate-Structure | File existence check | README.md, LICENSE, CONTRIBUTING.md present |
| Gate-Navigation | Manual test | Core docs accessible in ≤2 clicks from README |

---

## Implementation Approach

### Work Packages

**WP0: Deep Content & Structure Audit** (P0 - Foundation) ⬅️ INTERACTIVE
- **Part A**: Audit EVERY document - does it belong in a public repo?
- **Part B**: Analyze structural problems (duplication, depth, audience mixing)
- **Part C**: Enforce strict terminology rules for user-facing content
- **Interactive decisions** with Orquestador:
  - What stays, what goes, what moves?
  - Final directory structure
  - Where does removed content go?
- Document decisions in ADR if significant changes
- Output: `structure-analysis.md` with content audit + structure decision

**WP1: Restructure Repository** (P1 - Depends on WP0) ⬅️ INTERACTIVE
- **Interactive execution** of directory reorganization with Orquestador
- Review each move/rename/delete before executing
- Update internal links affected by moves
- Verify no broken references post-restructure
- Confirm final structure matches WP0 decision

**WP2: Create Entry Point Files** (P1 - Depends on WP1)
- Create README.md with navigation to NEW structure
- Create LICENSE (Apache 2.0)
- Create CONTRIBUTING.md with guidelines

**WP3: Audit & Fix Content** (P1 - Quality)
- Run terminology audit (grep for DoD, Rule, Developer, L0-L3)
- Run link audit (verify all internal references)
- Run secrets scan (grep for sensitive patterns)

**WP4: Final Validation** (P1 - Gate)
- Execute all Validation Gates
- User test: Fresh eyes walkthrough
- Commit and prepare for merge

### Estimated Effort

| Work Package | Complexity | Estimated Time |
|--------------|------------|----------------|
| WP0: Content & Structure Audit | High | 2-3 hours (interactive) |
| WP1: Restructure + Content Migration | High | 2-3 hours (interactive) |
| WP2: Entry Files | Low | 1 hour |
| WP3: Terminology & Link Audits | Medium | 2-3 hours |
| WP4: Validation | Low | 1 hour |
| **Total** | | **8-11 hours** |

> ⚠️ Timeline note: With 2 days to F&F launch, this is tight. Consider:
> - Parallel execution where possible
> - Deferring WP3 audits for post-launch cleanup if needed
> - Focusing WP0 on high-impact decisions first

### WP0 Detail: Deep Content & Structure Audit

> ⚠️ **Critical Assumption**: Current repository content and structure is ARBITRARY/LEGACY.
> Nothing is assumed to be correct. Every document requires explicit justification.

**Part A: Content Audit (Document-by-Document)**

Each document must answer:
1. **Does this belong in a PUBLIC conceptual repository?**
   - YES → Keep, determine location
   - NO → Remove or relocate to private repo

2. **Who is the audience?**
   - End user (developer learning RaiSE) → User-facing, strict terminology
   - Internal team (ontology work) → Can stay but mark clearly
   - Business stakeholder → Likely doesn't belong here

3. **Content classification:**

| Classification | Belongs Here? | Examples |
|----------------|---------------|----------|
| Core Ontology | ✅ YES | Constitution, Glossary, Methodology |
| Technical Decisions | ✅ YES | ADRs |
| Learning Exercises | ✅ YES | Katas |
| Reusable Templates | ✅ MAYBE | Templates (if useful to users) |
| Business Documents | ❌ NO | Business plan, market analysis |
| Internal Roadmaps | ❌ NO | Roadmap, backlog, session logs |
| Research Notes | ❌ PROBABLY NOT | Unless publishable value |
| Work Artifacts | ❌ NO | Specs/, internal reports |

**Suspect Documents to Review:**
- `02-business-model-v2.md` → Business doc, likely remove
- `03-market-context-v2.md` → Business doc, likely remove
- `30-roadmap-v2.1.md` → Internal planning, likely remove
- `31-current-state-v2.1.md` → Internal status, likely remove
- `32-session-log-v2.md` → Work artifact, likely remove
- `33-issues-decisions-v2.md` → Internal tracking, likely remove
- `34-dependencies-blockers-v2.md` → Internal tracking, likely remove
- `35-ontology-backlog-v2.md` → Internal backlog, likely remove
- `36-roadmap-tecnico-mvp.md` → Internal planning, likely remove
- `37-roadmap-tecnico-mvp-legacy.md` → Legacy internal, likely remove
- `docs/framework/v2.1/reportes/` → Internal reports, likely remove

**Part B: Structure Analysis**

| Problem | Current State | Impact |
|---------|---------------|--------|
| Katas duplicated | `docs/framework/v2.1/katas/` AND `src/katas-v2.1/` | Confusion: which is canonical? |
| `src/` without code | Repo is conceptual, but uses code-style structure | Misleading for visitors |
| Excessive depth | `docs/framework/v2.1/model/` = 4 levels | Hard to navigate |
| Hidden valuable content | `.specify/`, `.raise/` have useful docs | Invisible to users |
| Mixed purposes | model, adrs, katas, reportes all under v2.1/ | No clear hierarchy |
| Business content mixed with ontology | business-model alongside constitution | Wrong audience in same place |

**Part C: Terminology Enforcement**

| Document Type | Deprecated Terms Allowed? |
|---------------|---------------------------|
| User-facing docs (constitution, glossary, methodology, katas) | ❌ NEVER |
| ADRs documenting the migration (ADR-006a, ADR-007, ADR-011) | ✅ YES (historical context) |
| Archive content | ✅ YES (marked as deprecated) |
| Work logs, session logs | ✅ YES (if they stay, which is unlikely) |
| README, CONTRIBUTING | ❌ NEVER |

**Analysis Questions to Answer (Interactive):**

1. What content should remain in this public repo?
2. Where should removed content go? (private repo, delete, archive)
3. What is the ideal structure for remaining content?
4. What should be visible vs. hidden for public users?
5. How to handle versioning (v2.1 vs. archive)?

**Output**: `specs/007-public-repo-readiness/structure-analysis.md` with:
- Content audit results (keep/remove/relocate for each document)
- Final structure decision
- Migration plan for removed content

---

## Post-Phase 1 Constitution Re-Check

| Principio | Post-Design Verificación | Estado |
|-----------|--------------------------|--------|
| I. Coherencia Semántica | README uses only v2.1 terms; links to glossary | [x] |
| II. Governance como Código | All new files tracked in Git; plan documented | [x] |
| III. Validación en Cada Fase | 5 Validation Gates defined with clear criteria | [x] |
| IV. Simplicidad | README focused on quick access; no over-documentation | [x] |
| V. Mejora Continua | GitLab Issues integrated; feedback path clear | [x] |

---

## Next Steps

1. Run `/speckit.tasks` to generate task breakdown
2. Execute WP1 (create files)
3. Execute WP2 (audits)
4. Execute WP3 (validation)
5. Merge to `PRAISE-36-ontology-standarization`
6. Release to Friends & Family 🎉

---

*Plan generated: 2026-01-16 | Ready for `/speckit.tasks`*
