# Backlog: raise-cli

> **Status**: Active
> **Date**: 2026-02-09
> **Version**: 2.0.0
> **Related**: PRD v1.1.0, Vision v1.0.0, Design v1.1.0

---

## 1. Epics Overview

| ID | Epic | Status | Scope Doc | Priority |
|----|------|--------|-----------|----------|
| E1 | **Core Foundation** | ✅ Complete | `dev/epic-e1-scope.md` | — |
| E2 | **Governance Toolkit** | ✅ Complete | `dev/epic-e2-scope.md` | — |
| E3 | **Identity Core** | ✅ Complete | `dev/epic-e3-scope.md` | — |
| E4 | **Context Generation** | ✅ Via Skills | — | — |
| E5 | **SAR Engine** | ✅ Replaced by E13 | — | — |
| E6 | **Observability** | ✅ Replaced by E9 | — | — |
| E7 | **Onboarding** | ✅ Complete | `work/epics/e7-onboarding/scope.md` | — |
| E8 | **Work Tracking Graph** | ✅ Complete | `dev/epic-e8-scope.md` | — |
| E9 | **Telemetry & Self-Awareness** | ✅ Phase 1 Complete | `dev/epic-e9-scope.md` | — |
| E10 | **Collective Intelligence** | 📋 Explored | `dev/epic-e10-scope.md` | P2 (V3) |
| E11 | **Unified Context Architecture** | ✅ Complete | `dev/epic-e11-scope.md` | — |
| E12 | **Complete Knowledge Graph** | ✅ Complete | `dev/epic-e12-scope.md` | — |
| E13 | **Discovery** | ✅ Complete | `dev/epic-e13-scope.md` | — |
| E14 | **Rai Distribution** | ✅ Complete | `work/epics/e14-rai-distribution/scope.md` | — |
| E15 | **Ontology Graph Refinement** | ✅ Complete | `work/epics/e15-ontology-refinement/scope.md` | — |
| E16 | **Incremental Coherence** | ✅ Complete | `work/epics/e16-incremental-coherence/scope.md` | — |
| E17 | **Multi-Language Discovery** | ✅ Complete | `work/epics/e17-multi-language-discovery/scope.md` | — |
| E18 | **Pre-Launch Repo Readiness** | ✅ Complete | `work/epics/e18-prelaunch-repo/scope.md` | — |
| E19 | **V3 Product Design** | Planning | — | P1 (V3) |
| E20 | **Shared Memory Architecture** | Planning | — | P1 (V3) |
| E21 | **Platform Integration** | Planning | — | P1 (V3) |
| E22 | **Enterprise Readiness** | Planning | — | P2 (V3) |
| **E-DEMO** | **JIRA Sync Enabler** | 🚀 In Progress | `demo/atlassian-webinar/scope.md` | P0 (Demo) |

**Summary:** 17 of 22 epics complete. E19-E22 are V3 scope. E-DEMO is enabler epic (demo branch, non-merging).

---

## 2. What's Been Delivered

### Foundation (E1-E4)

| Epic | Key Deliverables |
|------|-----------------|
| E1 Core Foundation | CLI skeleton (Typer), config (Pydantic Settings), exceptions, output formatters |
| E2 Governance Toolkit | Concept extraction, graph builder, MVC query engine, CLI commands |
| E3 Identity Core | `.rai/` structure, memory JSONL + graph, session continuity, memory query CLI |
| E4 Context Generation | Via `/framework-sync` skill (ADR-012: skills orchestrate, CLI provides data) |

### Knowledge & Context (E8, E11, E12, E15, E16)

| Epic | Key Deliverables |
|------|-----------------|
| E8 Work Tracking Graph | Backlog/epic parsing, work context queries |
| E11 Unified Context | Single queryable graph merging governance, memory, work, code structure |
| E12 Complete Knowledge Graph | All extractors wired: governance, memory, work, skills, identity |
| E15 Ontology Refinement | Bounded contexts, layers, constraint edges, architectural context queries |
| E16 Incremental Coherence | Graph diff, `/docs-update` skill, coherence loop in story-close |

### Discovery & Analysis (E13, replacing E5)

| Epic | Key Deliverables |
|------|-----------------|
| E13 Discovery | `rai discover scan/validate/complete`, component catalog, Python code analyzer |
| E17 Multi-Language Discovery | TS/TSX, PHP, Svelte extractors, multi-language analyzer categories and module paths |

E5 (SAR Engine) was the original plan for brownfield analysis. E13 Discovery delivered this capability with a different approach: protocol-based code analyzers, component discovery, and drift detection. E5 is fully superseded.

### Telemetry & Observability (E9, replacing E6)

| Epic | Key Deliverables |
|------|-----------------|
| E9 Phase 1 | Signal schema, JSONL writers, `emit-work`/`emit-calibration` commands, skill lifecycle events |

E6 (Observability) was replaced by E9's local-first telemetry approach. Phase 2 (insights, calibration updates) is deferred.

### Distribution & Onboarding (E7, E14)

| Epic | Key Deliverables |
|------|-----------------|
| E14 Rai Distribution | Base Rai bundled in package, bootstrap on `rai init`, MEMORY.md generation, skills scaffolding |
| E7 Onboarding | `rai init` governance scaffolding, `/project-create` (greenfield), `/project-onboard` (brownfield) |

---

## 3. Current State

### CLI Commands

```
rai init          — Initialize project (greenfield/brownfield detection)
rai discover      — Codebase discovery (scan, validate, complete, drift)
rai memory        — Query and manage memory (query, context, build, add-pattern, emit-work)
rai session       — Session lifecycle (start, close)
rai skill         — Skill management (list, validate)
rai profile       — Developer profile
rai base          — Base Rai package info
```

### Skills (20 total)

Session (2), Epic (4), Story (6), Discovery (4), Meta (1), Other (3)

### Metrics

- **Tests:** 1610 passing, 92.61% coverage
- **Graph:** 345+ nodes across governance, memory, work, code, identity
- **Modules:** 15 source modules

---

## 4. Hotfixes & Bugfixes

> **Note**: Bugfix stories branch directly from `v2` (no epic wrapper). Format compatible with Jira import/sync.

| ID | Title | Description | Status | Priority | Found In | Target |
|----|-------|-------------|--------|----------|----------|--------|
| **HF-3** | Type annotations incomplete in governance models | `governance/models.py:131` - ExtractionResult.concepts field has partial type `list[Unknown]`. Causes pyright errors in strict mode. | 🔴 Open | P2 | v2.0.0a7 | v2.0.0a9 |
| **HF-4** | Type annotations incomplete in profile schema | `onboarding/profile.py:168,216` - CoachingState.corrections and deadlines fields have partial types `list[Unknown]`. Pyright strict mode failures. | 🔴 Open | P2 | v2.0.0a7 | v2.0.0a9 |
| **HF-5** | Extend governance extractor to parse SOPs | Governance extractor currently parses principles, requirements, terms, glossary, ADRs, but not SOPs. Need to add SOP parsing support for `governance/sops/*.md` files. | 🔴 Open | P3 | v2.0.0a8 | v2.0.0a10 |

**Completed:**
- **HF-1**: Session narrative schema (completed in v2.0.0a6)
- **HF-2**: Publish skill integration (completed in v2.0.0a7)

---

## 5. Next Candidates

| Candidate | What | Priority | Effort |
|-----------|------|----------|--------|
| **E9 Phase 2** | Local insights from telemetry — signal analysis, insight generation, calibration updates | Post-F&F | M (3-4 stories) |
| **E10 Collective Intelligence** | Pattern sharing, aggregate telemetry, team memory | V3 | L |
| **Governance frontmatter standardization** | Migrate 5 remaining docs to YAML frontmatter (PAT-184) | Post-F&F | S (1 epic) |
| **"Unified" rename** | Remove vestigial prefix from graph classes | Post-F&F | S (1 story) |

See `dev/parking-lot.md` for full idea backlog.

---

## 6. Definition of Done

Each feature is complete when:

- [ ] Code implemented with type annotations
- [ ] Unit tests passing (>90% coverage on feature)
- [ ] Integration tests for CLI commands
- [ ] Error handling with proper exception types
- [ ] Code passes `ruff check` and `pyright`
- [ ] Retrospective complete

---

## 7. Demo & Commercial Strategy

### Atlassian Webinar Demo (March 14, 2026)

**Branch:** `demo/atlassian-webinar` (created 2026-02-14)

**Purpose:** JIRA sync prototype for Atlassian partnership webinar demo

**Merge Policy:** ⚠️ **NEVER MERGES TO v2** — Commercial-only feature

**Status:** Active spike (timeboxed prototype)

---

### Commercial Strategy

**Decision (2026-02-14):** JIRA/backlog sync is **commercial-only**, not distributed in open-source raise-cli.

**Rationale:**
- Part of future RaiSE PRO offering (premium tier)
- Atlassian partnership demo validates market demand
- May retrofit to open version later (decision deferred)

**Research Foundation:**
- 6 parallel research streams completed (2026-02-14)
- 184+ sources analyzed, ~6,500 lines of documentation
- Location: `/work/research/{bidirectional-sync,jira-sync,gitlab-sync,offline-first,pm-sync-boundaries,sync-triggers}/`

---

### Demo Branch Lifecycle

| Phase | Timeline | Action |
|-------|----------|--------|
| **Prototype** | Feb 14 - Mar 13 | Build demo MVP in `demo/atlassian-webinar` |
| **Demo** | Mar 14 | Atlassian webinar presentation |
| **Decision** | Mar 15 - 31 | Choose commercial architecture (raise-pro package vs monorepo vs fork) |
| **Migrate or Archive** | Apr 1+ | Move to raise-pro or archive branch |

---

### Post-Demo Options

**Option 1: Separate Package (Recommended)**
```
raise-cli (open, PyPI) → Core + extension points
raise-pro (commercial) → JIRA/GitLab/Odoo adapters
```

**Option 2: Monorepo with Private Modules**
```
src/rai_cli/  (distributed)
src/rai_pro/  (filtered out of build)
```

**Option 3: Private Fork**
```
raise-commons (open)
raise-commercial (private fork)
```

Decision deferred until post-demo customer validation.

---

### Related V3 Epics (Potentially Commercial)

| Epic | Description | Tier |
|------|-------------|------|
| E19 | V3 Product Design | TBD |
| E20 | Shared Memory Architecture | TBD |
| E21 | Platform Integration (JIRA/GitLab/Odoo) | Commercial |
| E22 | Enterprise Readiness | Commercial |

E21 absorbs demo branch learnings if raise-pro is built.

---

### Documentation

- **Strategy Doc:** `DEMO-STRATEGY.md` in `demo/atlassian-webinar` branch
- **Research:** `/work/research/` (6 comprehensive studies)
- **Parking Lot:** "E-NEXT: Backlog Abstraction Layer (RaiSE PRO)"

---

## Changelog

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 2.2.0 | 2026-02-14 | Rai | Added Demo & Commercial Strategy section (§7), documented demo/atlassian-webinar branch |
| 2.1.0 | 2026-02-14 | Rai | Added Hotfixes section (§4) for quality gate tracking, renumbered subsequent sections |
| 2.0.0 | 2026-02-09 | Rai | Full refresh: E5→E13, E6→E9, E7 complete, E12-E16 added, stale sections removed |
| 1.3.0 | 2026-02-03 | Rai | E9 Phase 1 + E11 complete, only E7 remaining for F&F |
| 1.2.0 | 2026-02-03 | Rai | E8 complete, E9 in progress (F9.1 done), sequence: E9→E7 |
| 1.1.0 | 2026-02-02 | Rai | Sync with reality: E1-E3 complete, E4 via skills, F&F readiness section |
| 1.0.0 | 2026-01-30 | Claude Opus 4.5 | Initial backlog |

---

*Updated by: Rai + Emilio*
*Last sync: 2026-02-14*
