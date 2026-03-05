# Backlog: raise-cli

> **Status**: Active
> **Date**: 2026-03-03
> **Version**: 2.2.0-dev
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
| [RAISE-143](https://humansys.atlassian.net/browse/RAISE-143) | **Collective Intelligence** (was E10) | 📋 Backlog | `dev/epic-e10-scope.md` | P2 (V3) |
| E11 | **Unified Context Architecture** | ✅ Complete | `dev/epic-e11-scope.md` | — |
| E12 | **Complete Knowledge Graph** | ✅ Complete | `dev/epic-e12-scope.md` | — |
| E13 | **Discovery** | ✅ Complete | `dev/epic-e13-scope.md` | — |
| E14 | **Rai Distribution** | ✅ Complete | `work/epics/e14-rai-distribution/scope.md` | — |
| E15 | **Ontology Graph Refinement** | ✅ Complete | `work/epics/e15-ontology-refinement/scope.md` | — |
| E16 | **Incremental Coherence** | ✅ Complete | `work/epics/e16-incremental-coherence/scope.md` | — |
| E17 | **Multi-Language Discovery** | ✅ Complete | `work/epics/e17-multi-language-discovery/scope.md` | — |
| E18 | **Pre-Launch Repo Readiness** | ✅ Complete | `work/epics/e18-prelaunch-repo/scope.md` | — |
| **E-DEMO** | **JIRA Sync Enabler** | 🚀 In Progress | `demo/atlassian-webinar/scope.md` | P0 (Demo) |
| [RAISE-127](https://humansys.atlassian.net/browse/RAISE-127) | **Multi-Agent Support** | 🚀 In Progress (pt1 done, pt2 pending) | `work/epics/raise-127-multi-agent/scope.md` | P0 (v2.1) |
| [RAISE-128](https://humansys.atlassian.net/browse/RAISE-128) | **IDE Integration** | ✅ Complete | `work/epics/raise-128-ide-integration/scope.md` | P1 (v2.1) |
| [RAISE-135](https://humansys.atlassian.net/browse/RAISE-135) | **Hierarchical Memory Architecture** (was E20) | 📋 Backlog | — | P1 (v2.1+) |
| [RAISE-140](https://humansys.atlassian.net/browse/RAISE-140) | **V3 Product Design** (was E19) | 📋 Backlog | — | P1 (V3) |
| [RAISE-141](https://humansys.atlassian.net/browse/RAISE-141) | **Platform Integration — Backlog Backends** (was E21) | 📋 Backlog | — | P1 (V3) |
| [RAISE-142](https://humansys.atlassian.net/browse/RAISE-142) | **Enterprise Readiness** (was E22) | 📋 Backlog | — | P2 (V3) |
| [RAISE-143](https://humansys.atlassian.net/browse/RAISE-143) | **Collective Intelligence** (was E10) | 📋 Backlog | `dev/epic-e10-scope.md` | P2 (V3) |
| [RAISE-144](https://humansys.atlassian.net/browse/RAISE-144) | **Engineering Health** | 🚀 Active | §6 | Rolling |
| [RAISE-153](https://humansys.atlassian.net/browse/RAISE-153) | **Developer Enablement** | ✅ Complete | `work/epics/raise-153-developer-enablement/scope.md` | — |
| [RAISE-168](https://humansys.atlassian.net/browse/RAISE-168) | **Neurosymbolic Memory Density** | ✅ Complete | `work/epics/raise-168-neurosymbolic-memory-density/scope.md` | — |
| [RAISE-173](https://humansys.atlassian.net/browse/RAISE-173) | **Team Enablement & Operational Readiness** | 🚀 In Progress | — | P1 |
| [RAISE-211](https://humansys.atlassian.net/browse/RAISE-211) | **Adapter Foundation** | ✅ Complete | `work/epics/raise-211-adapter-foundation/scope.md` | — |
| [RAISE-242](https://humansys.atlassian.net/browse/RAISE-242) | **Skill Ecosystem** | ✅ Complete | `work/epics/raise-242-skill-ecosystem/scope.md` | P1 (v2.1 partial, v2.3 full) |
| [RAISE-247](https://humansys.atlassian.net/browse/RAISE-247) | **CLI Ontology Restructuring** | ✅ Complete | `work/epics/raise-247-cli-ontology/scope.md` | — |
| [RAISE-248](https://humansys.atlassian.net/browse/RAISE-248) | **Lifecycle Hooks & Workflow Gates** | ✅ Complete | `work/epics/raise-248-hooks-gates/scope.md` | — |
| [RAISE-249](https://humansys.atlassian.net/browse/RAISE-249) | **Artifact Ontology & Contract Chain** | ✅ Complete | `work/epics/raise-249-artifact-ontology/scope.md` | — |
| [RAISE-257](https://humansys.atlassian.net/browse/RAISE-257) | **Skill Excellence** | ✅ Complete | `work/epics/raise-257-skill-excellence/scope.md` | — |
| [RAISE-258](https://humansys.atlassian.net/browse/RAISE-258) | **Telcel Collect Skill** | 🚀 In Progress | — | P1 (Client) |
| [RAISE-274](https://humansys.atlassian.net/browse/RAISE-274) | **Governance Copilot POC — Forge** | 🚀 In Progress | — | P0 (Demo) |
| [RAISE-275](https://humansys.atlassian.net/browse/RAISE-275) | **Shared Memory Backend** | ✅ Complete | `work/epics/e275-shared-memory-backend/scope.md` | — |
| [RAISE-283](https://humansys.atlassian.net/browse/RAISE-283) | **CI/CD Security Pipeline** | ✅ Complete | — | — |
| [RAISE-292](https://humansys.atlassian.net/browse/RAISE-292) | **TDD Policy Reform** | ✅ Complete | `work/epics/e292-tdd-policy-reform/scope.md` | — |
| [RAISE-293](https://humansys.atlassian.net/browse/RAISE-293) | **Workstream Concept (Worktrees)** | 📋 Backlog | — | P2 |
| [RAISE-294](https://humansys.atlassian.net/browse/RAISE-294) | **Test Infrastructure Migration** | 📋 Backlog | — | P2 |
| [RAISE-295](https://humansys.atlassian.net/browse/RAISE-295) | **Security Fixes (Snyk/SAST/Sonar)** | 📋 Backlog | — | P2 |
| [RAISE-156](https://humansys.atlassian.net/browse/RAISE-156) | **GTM Website** | 📋 Backlog | — | P2 |
| [RAISE-208](https://humansys.atlassian.net/browse/RAISE-208) | **[PRO] Jira Adapter** | 📋 Backlog | — | P1 (Pro) |
| [RAISE-209](https://humansys.atlassian.net/browse/RAISE-209) | **[PRO] Team/Org Memory** | 📋 Backlog | — | P1 (Pro) |
| [RAISE-210](https://humansys.atlassian.net/browse/RAISE-210) | **[PRO] Jira-first UI** | 📋 Backlog | — | P2 (Pro) |
| [RAISE-301](https://humansys.atlassian.net/browse/RAISE-301) | **Agent Tool Abstraction** | ✅ Complete | `work/epics/e301-agent-tool-abstraction/scope.md` | — |
| [RAISE-325](https://humansys.atlassian.net/browse/RAISE-325) | **Agent-Orchestrated Workflow** | ✅ Complete | `work/epics/e325-agent-orchestrated-workflow/scope.md` | — |
| [RAISE-337](https://humansys.atlassian.net/browse/RAISE-337) | **Declarative MCP Adapter Framework** | ✅ Complete | `work/epics/e337-declarative-mcp-adapter/scope.md` | — |
| [RAISE-384](https://humansys.atlassian.net/browse/RAISE-384) | **MCP Platform** (E338) | ✅ Complete | `work/epics/e338-mcp-platform/scope.md` | — |
| [RAISE-340](https://humansys.atlassian.net/browse/RAISE-340) | **Skill Set Ecosystem** | ✅ Complete | `work/epics/e340-skill-set-ecosystem/scope.md` | — |
| [RAISE-346](https://humansys.atlassian.net/browse/RAISE-346) | **Skill Lifecycle Hardening** | ✅ Complete | `work/epics/e346-skill-lifecycle-hardening/scope.md` | — |
| [RAISE-347](https://humansys.atlassian.net/browse/RAISE-347) | **Backlog Automation** | 🚀 In Progress | `work/epics/e347-backlog-automation/scope.md` | P0 (v2.2) |
| [RAISE-348](https://humansys.atlassian.net/browse/RAISE-348) | **Documentation Refresh** | 📋 Backlog | — | P0 (v2.2) |
| [RAISE-349](https://humansys.atlassian.net/browse/RAISE-349) | **Adapter Integration Validation** | 📋 Backlog | — | P0 (v2.2) |
| [RAISE-364](https://humansys.atlassian.net/browse/RAISE-364) | **Rai Experience Portability** (E350) | ✅ Complete | `work/epics/e350-experience-portability/scope.md` | — |
| [RAISE-369](https://humansys.atlassian.net/browse/RAISE-369) | **Open Source Readiness Audit** | 📋 Backlog | — | P0 (v2.2) |
| [RAISE-378](https://humansys.atlassian.net/browse/RAISE-378) | **rai doctor — Diagnostic & Bug Reporting** | 📋 Backlog | — | P0 (v2.2) |
| [RAISE-402](https://humansys.atlassian.net/browse/RAISE-402) | **Typed Skill Artifacts** (E354) | ✅ Complete | `work/epics/e354-typed-skill-artifacts/scope.md` | P1 |

### Release Roadmap (revised SES-294, 2026-02-26)

See `governance/roadmap.md` for full roadmap with 10 releases.

**MVP — Mar 15, 2026 (Atlassian Webinar)**
- RAISE-274: Governance Copilot POC (Forge) — Jira + Confluence integration
- RAISE-275: Shared Memory Backend ✅ — rai-server + PostgreSQL + API
- E-GOV-FOUNDATION: Governance Foundation (needs /rai-epic-design)

**Post-MVP releases:** Guardrails (Q2), Portfolio Health (Q2), Patterns/OrgIntel/Forge (Q3)

**Category:** AI Agentic Governance — "When AI agents build your software, RaiSE ensures they follow your rules."

**Summary:** 22+ internal epics complete. RAISE-144 (Engineering Health) is permanent.
MVP focus is governance + shared memory + Atlassian integration.

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

### Skills (27 total, all ADR-040 compliant)

Session (2), Epic (4), Story (6), Discovery (4), Meta (1), Other (10)

### Metrics

- **Tests:** 2770 passing
- **Graph:** 345+ nodes across governance, memory, work, code, identity
- **Modules:** 15 source modules

---

## 4. Hotfixes & Bugfixes

> **Note**: Bugfix stories branch directly from `v2` (no epic wrapper). Format compatible with Jira import/sync.

| ID | Title | Description | Status | Priority | Found In | Target |
|----|-------|-------------|--------|----------|----------|--------|
| [RAISE-134](https://humansys.atlassian.net/browse/RAISE-134) | Context leak: session data cross-project | Fixed by RAISE-139 (CWD poka-yoke guard on session close). | ✅ Done | P1 | v2.0.0a1 | v2.1 |
| [RAISE-136](https://humansys.atlassian.net/browse/RAISE-136) | Graph schema crash on unknown NodeType | Graceful degradation in iter_concepts — skip + warn on unknown types. | ✅ Done | P1 | v2.0.0a1 | v2.0.0a6 |
| **HF-3** | Type annotations incomplete in governance models | `governance/models.py:131` - ExtractionResult.concepts field has partial type `list[Unknown]`. Causes pyright errors in strict mode. | 🔴 Open | P2 | v2.0.0a7 | v2.0.0a9 |
| **HF-4** | Type annotations incomplete in profile schema | `onboarding/profile.py:168,216` - CoachingState.corrections and deadlines fields have partial types `list[Unknown]`. Pyright strict mode failures. | 🔴 Open | P2 | v2.0.0a7 | v2.0.0a9 |
| **HF-5** | Extend governance extractor to parse SOPs | Governance extractor currently parses principles, requirements, terms, glossary, ADRs, but not SOPs. Need to add SOP parsing support for `governance/sops/*.md` files. | 🔴 Open | P3 | v2.0.0a8 | v2.0.0a10 |

**Completed:**
- **HF-1**: Session narrative schema (completed in v2.0.0a6)
- **HF-2**: Publish skill integration (completed in v2.0.0a7)

---

## 5. Next: RAISE-127 Urgent Subset (Bugfix Grande)

> **Goal:** Devs and F&F can use multiple IDEs/agents without session corruption.
> **Scope:** 3 stories from RAISE-127, branches directly from v2. Fixes RAISE-134.

| # | JIRA | Story | Size | Depends On |
|---|------|-------|------|------------|
| 1 | [RAISE-137](https://humansys.atlassian.net/browse/RAISE-137) | Agent Identity — detect IDE/runtime, assign agent ID | S | — |
| 2 | [RAISE-138](https://humansys.atlassian.net/browse/RAISE-138) | Namespaced Session State — per-agent isolated directories | M | RAISE-137 |
| 3 | [RAISE-139](https://humansys.atlassian.net/browse/RAISE-139) | Project-scoped session writes — poka-yoke CWD (fixes RAISE-134) | S | RAISE-138 |

### Other Candidates

| Candidate | What | Priority | Effort |
|-----------|------|----------|--------|
| **RAISE-136: CM-1 Graceful Degradation** | Skip unknown node types with warning instead of crash | P1 (immediate) | XS (1 story) |
| **E9 Phase 2** | Local insights from telemetry — signal analysis, insight generation, calibration updates | Post-F&F | M (3-4 stories) |
| **RAISE-143: Collective Intelligence** | Pattern sharing, aggregate telemetry, team memory | V3 | L |
| **Governance frontmatter standardization** | Migrate 5 remaining docs to YAML frontmatter (PAT-184) | Post-F&F | S (1 epic) |
| [RAISE-145](https://humansys.atlassian.net/browse/RAISE-145): "Unified" rename | Remove vestigial prefix from graph classes (under RAISE-144) | Post-F&F | S (1 story) |

See `dev/parking-lot.md` for full idea backlog.

---

## 6. RAISE-144: Engineering Health (Rolling)

> **Goal:** Platform stability, language coverage, and tech debt reduction. Permanent epic — stories branch directly from `v2`.
> **Driven by:** Kurigage Jumpstart (first client onboarding) requirements.

| # | JIRA | Story | Size | Priority | Status |
|---|------|-------|------|----------|--------|
| 1 | [RAISE-158](https://humansys.atlassian.net/browse/RAISE-158) | C#/.NET discovery scanner | S | P0 | ✅ Done |
| 2 | [RAISE-161](https://humansys.atlassian.net/browse/RAISE-161) | Windows compatibility verification | XS | P0 | ✅ Done |
| 3 | [RAISE-160](https://humansys.atlassian.net/browse/RAISE-160) | Flutter/Dart discovery scanner | S | P2 (before Track 2) | ✅ Done |
| 4 | [RAISE-145](https://humansys.atlassian.net/browse/RAISE-145) | "Unified" prefix rename | S | Post-F&F | 📋 Backlog |
| 5 | [RAISE-291](https://humansys.atlassian.net/browse/RAISE-291) | Bandit security gate — integrate SAST into quality pipeline | XS | P2 | 📋 Backlog |
| 6 | [RAISE-256](https://humansys.atlassian.net/browse/RAISE-256) | CI: uv sync --extra dev fix | XS | P0 | ✅ Done |
| 7 | [RAISE-136](https://humansys.atlassian.net/browse/RAISE-136) | Graph schema crash — graceful degradation | XS | P1 | ✅ Done |

**Completed:**
- **HF-SES-MIGRATED**: SES-MIGRATED zombie blocks session close — migration clears stale session + CWD guard filters by project (v2.0.1)
- **HF-TEST-LEAKAGE**: Test leakage into ~/.rai/developer.yaml — autouse conftest.py fixture (v2.0.1)

---

## 6. Definition of Done

Each feature is complete when:

- [ ] Code implemented with type annotations
- [ ] Unit tests passing — each test asserts observable behavior, not implementation details
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

### Related Epics (JIRA-tracked)

| JIRA | Description | Tier |
|------|-------------|------|
| [RAISE-127](https://humansys.atlassian.net/browse/RAISE-127) | Multi-Agent Support — concurrent Rai instances | Core (v2.1) |
| [RAISE-128](https://humansys.atlassian.net/browse/RAISE-128) | IDE Integration — Cursor, Antigravity, VSCode/Kilo | Core (v2.1) |
| [RAISE-135](https://humansys.atlassian.net/browse/RAISE-135) | Hierarchical Memory — instance → repo → team → org | Pro/Enterprise |
| [RAISE-140](https://humansys.atlassian.net/browse/RAISE-140) | V3 Product Design — commercial architecture | V3 |
| [RAISE-141](https://humansys.atlassian.net/browse/RAISE-141) | Platform Integration — backlog backends (JIRA/GitLab/Odoo) | Commercial |
| [RAISE-142](https://humansys.atlassian.net/browse/RAISE-142) | Enterprise Readiness — org governance, compliance | Enterprise |

| [RAISE-143](https://humansys.atlassian.net/browse/RAISE-143) | Collective Intelligence — pattern sharing, team memory | V3 |
| [RAISE-144](https://humansys.atlassian.net/browse/RAISE-144) | Engineering Health — rolling tech debt epic | Permanent |

**Dependency chain:** RAISE-127 → RAISE-128, RAISE-135 → RAISE-142/143.
E-DEMO learnings feed into RAISE-141 (backlog backends).

---

### Documentation

- **Strategy Doc:** `DEMO-STRATEGY.md` in `demo/atlassian-webinar` branch
- **Research:** `/work/research/` (6 comprehensive studies)
- **Parking Lot:** "E-NEXT: Backlog Abstraction Layer (RaiSE PRO)"

---

## Changelog

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 2.7.0 | 2026-02-26 | Rai | Full Jira sync: 11 stories closed (E275 S1-S7, RAISE-136, RAISE-256, RAISE-266, RAISE-283). Added 10 missing epics (258, 274, 283, 293-295, 156, 208-210). RAISE-275 → Done. Merge conflict resolved. Roadmap updated to SES-294 MVP Mar 15. |
| 2.6.0 | 2026-02-24 | Rai | JIRA sync: RAISE-128/153/168/211/247/248/249 → Done, RAISE-134 → Done (was stale), RAISE-236 → Done (sync-skills bug fixed today). Skill Excellence assigned RAISE-257 (was local-only RAISE-250). |
| 2.5.0 | 2026-02-23 | Rai | E250 Skill Excellence complete: 27/27 skills ADR-040 compliant (7 sections, ≤150 lines), ~65% total line reduction, validator + scaffold updated, sync pipeline verified |
| 2.4.0 | 2026-02-16 | Rai | RAISE-153 complete, RAISE-144 activated with Kurigage-driven stories (RAISE-158/160/161), SES-MIGRATED + test leakage fixes |
| 2.3.0 | 2026-02-15 | Rai | Full JIRA sync: E10/E19-E22 → RAISE-140-143, Engineering Health epic (RAISE-144), RAISE-134/136 bugs, RAISE-137-139 urgent stories, Fix Version strategy |
| 2.2.0 | 2026-02-14 | Rai | Added Demo & Commercial Strategy section (§7), documented demo/atlassian-webinar branch |
| 2.1.0 | 2026-02-14 | Rai | Added Hotfixes section (§4) for quality gate tracking, renumbered subsequent sections |
| 2.0.0 | 2026-02-09 | Rai | Full refresh: E5→E13, E6→E9, E7 complete, E12-E16 added, stale sections removed |
| 1.3.0 | 2026-02-03 | Rai | E9 Phase 1 + E11 complete, only E7 remaining for F&F |
| 1.2.0 | 2026-02-03 | Rai | E8 complete, E9 in progress (F9.1 done), sequence: E9→E7 |
| 1.1.0 | 2026-02-02 | Rai | Sync with reality: E1-E3 complete, E4 via skills, F&F readiness section |
| 1.0.0 | 2026-01-30 | Claude Opus 4.5 | Initial backlog |

---

*Updated by: Rai + Emilio*
*Last sync: 2026-02-26*
