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

**Summary:** 17 of 22 epics complete. E19-E22 are V3 scope.

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

## 4. Next Candidates

| Candidate | What | Priority | Effort |
|-----------|------|----------|--------|
| **E9 Phase 2** | Local insights from telemetry — signal analysis, insight generation, calibration updates | Post-F&F | M (3-4 stories) |
| **E10 Collective Intelligence** | Pattern sharing, aggregate telemetry, team memory | V3 | L |
| **Governance frontmatter standardization** | Migrate 5 remaining docs to YAML frontmatter (PAT-184) | Post-F&F | S (1 epic) |
| **"Unified" rename** | Remove vestigial prefix from graph classes | Post-F&F | S (1 story) |

See `dev/parking-lot.md` for full idea backlog.

---

## 5. Definition of Done

Each feature is complete when:

- [ ] Code implemented with type annotations
- [ ] Unit tests passing (>90% coverage on feature)
- [ ] Integration tests for CLI commands
- [ ] Error handling with proper exception types
- [ ] Code passes `ruff check` and `pyright`
- [ ] Retrospective complete

---

## Changelog

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 2.0.0 | 2026-02-09 | Rai | Full refresh: E5→E13, E6→E9, E7 complete, E12-E16 added, stale sections removed |
| 1.3.0 | 2026-02-03 | Rai | E9 Phase 1 + E11 complete, only E7 remaining for F&F |
| 1.2.0 | 2026-02-03 | Rai | E8 complete, E9 in progress (F9.1 done), sequence: E9→E7 |
| 1.1.0 | 2026-02-02 | Rai | Sync with reality: E1-E3 complete, E4 via skills, F&F readiness section |
| 1.0.0 | 2026-01-30 | Claude Opus 4.5 | Initial backlog |

---

*Updated by: Rai + Emilio*
*Last sync: 2026-02-09*
