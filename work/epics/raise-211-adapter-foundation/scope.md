---
epic_id: "RAISE-211"
title: "Adapter Foundation"
status: "in_progress"
stories_count: 7
---

# Epic Scope: Adapter Foundation

> **Status:** IN PROGRESS
> **Branch:** `epic/e211/adapter-foundation`
> **Created:** 2026-02-22

---

## Objective

Implement ADR-033/034/035/036/037 as Python code — Protocol contracts, entry point registry, TierContext, and KnowledgeGraphBackend. Without this foundation, raise-pro (RAISE-208/209) cannot build and RAISE-207 (repo separation) has no clean code boundary.

**Value proposition:** After this epic, any Python package can extend raise-cli by publishing entry points. PRO adapters (Jira, Supabase) become installable plugins, not core modifications. The open-core boundary is code, not convention.

---

## Stories

| ID | Story | Size | Status | Dependencies | Description |
|----|-------|:----:|:------:|--------------|-------------|
| S211.0 | GraphNode class hierarchy | M | Done ✓ | None | GraphNode base with `__init_subclass__` auto-registration. 18 core subclasses as documented extension points. |
| S211.1 | Protocol contracts | S | Done ✓ | S211.0 | PM, Governance, DocTarget Protocols + Pydantic models (IssueSpec, ArtifactLocator, etc.) |
| S211.2 | Entry point registry | S | Pending | S211.1 | `importlib.metadata` discovery: `get_pm_adapters()`, `get_governance_schemas()`, etc. |
| S211.3 | rai memory build → registry | M | Pending | S211.0, S211.2 | Refactor UnifiedGraphBuilder to use registry instead of hardcoded parsers |
| S211.4 | KnowledgeGraphBackend | M | Pending | S211.0, S211.2 | Protocol + FilesystemGraphBackend (refactor current persistence) |
| S211.5 | TierContext | S | Pending | S211.1 | Tier detection from manifest, Capability enum, progressive enrichment |
| S211.6 | rai adapters list/check | S | Pending | S211.2, S211.5 | CLI surface for adapter discovery and validation |

**Total:** 7 stories (M epic)

---

## In Scope

**MUST:**
- GraphNode class hierarchy with auto-registration (`__init_subclass__`)
- Protocol contracts for all adapter types (PM, Governance, Graph, Tier)
- Entry point registry with `importlib.metadata` discovery
- FilesystemGraphBackend as built-in (current behavior, refactored)
- TierContext with progressive enrichment (no feature gating)
- Zero regression on existing `rai memory build` output

**SHOULD:**
- `rai adapters list/check` CLI commands
- Refactor governance parsers to register as entry points

## Out of Scope

- Concrete PRO adapters (JiraAdapter, SupabaseGraphBackend) → raise-pro (RAISE-208/209)
- IdentityProvider / Profile sync → PRO onboarding
- SecretManagerAdapter → Enterprise (RAISE-142)
- AuditAdapter → Enterprise compliance
- SearchAdapter (semantic search, pgvector) → PRO
- SkillRegistryAdapter → org governance
- NodeType/EdgeType migration layer for old serialized graphs → rebuild on upgrade

---

## Done Criteria

### Per Story
- [ ] Code implemented with type annotations (pyright strict)
- [ ] Tests pass (>90% coverage on new code)
- [ ] Ruff + pyright + bandit pass
- [ ] Retrospective complete

### Epic Complete
- [ ] All 7 stories complete
- [ ] All existing 1610 tests still pass (zero regression)
- [ ] `rai memory build` produces functionally identical graph via registry path
- [ ] Entry points registered in `pyproject.toml`
- [ ] Epic retrospective completed
- [ ] Merged to v2

---

## Dependencies

```
S211.0 (GraphNode hierarchy)
  ├── S211.1 (Protocol contracts)
  │     ├── S211.2 (Entry point registry)
  │     │     ├── S211.3 (rai memory build → registry) ←── also needs S211.0
  │     │     ├── S211.4 (KnowledgeGraphBackend) ←── also needs S211.0
  │     │     └── S211.6 (rai adapters list/check) ←── also needs S211.5
  │     └── S211.5 (TierContext)
  └── S211.3 (needs new node types)
```

**Critical path:** S0 → S1 → S2 → S3
**Parallel after S2:** S4, S6 (once S5 ready)
**Parallel after S1:** S5

**External blockers:** None — all 5 ADRs (033-037) already accepted.

---

## Notes

### Key Design Decisions
- **GraphNode hierarchy** (C+E+D pattern): Class hierarchy with `__init_subclass__` auto-registration. Pattern from pytest/Airflow/Kedro. 18 core subclasses are documented extension points — the codebase is the portfolio. Edges stay flat (str + constants) — no per-type fields needed.
- **Backward compat:** Rebuild on upgrade. Graph is derived, not source. `rai memory build` regenerates.
- **Module layout:** Protocols in `adapters/`, built-in implementations stay in-place (`governance/`, `graph/`).
- **Unknown types:** Graceful fallback with warning + actionable message ("run rai memory build").

### Key Risks
- **S211.0 scope:** GraphNode hierarchy touches models used across 1610 tests. Mitigation: ConceptNode as alias, zero test changes required.
- **S211.3 regression:** Builder refactor must produce identical graph. Mitigation: snapshot test comparing before/after graph output.

### ADR Foundation
| ADR | Concept | Status |
|-----|---------|--------|
| ADR-033 | Open-core adapter architecture | Accepted |
| ADR-034 | Governance extensibility | Accepted |
| ADR-035 | Backend deployment topology | Accepted |
| ADR-036 | KnowledgeGraphBackend | Accepted |
| ADR-037 | TierContext | Accepted |

---

*Created: 2026-02-22*
