# Adapter Backlog v2 — Reconciled & Structured

> **Original:** 2026-03-28 (designed from adapter-vision.md)
> **Reconciled:** 2026-03-31 (cross-referenced with completed work)
> **Restructured:** 2026-03-31 (ADR-015: epic-session-worktree alignment)
> **Status:** Active — single source of truth for adapter roadmap

---

## Design Principle

**Config first, features second, reliability third.**

---

## Capability Map — Delivered

| # | Capability | Epic(s) | Jira | Stories | Status |
|---|-----------|---------|------|:-------:|--------|
| CAP-1 | Protocol Foundation | RAISE-211 | Done | 7/7 | Protocols, registry, TierContext, GraphNode |
| CAP-2 | Jira PM Operations | E494 | Done | 7/7 | ACLI adapter, multi-instance, telemetry |
| CAP-3 | Jira Taxonomy & Lifecycle | RAISE-829 | Done | 7/7 | IssueSpec v2, lifecycle, phase comments |
| CAP-4 | Confluence Documentation | E1051 (RAISE-1051) | Done | 7/10 | Python adapter, config, composite target |
| CAP-5 | Confluence IA Model | RAISE-830 | Done | 6/6 | Labels, routing, index, templates, batch |
| CAP-6 | Declarative Adapter Framework | E337 | Done | 5/5 | YAML adapters, expression evaluator |
| CAP-7 | Adapter Infrastructure | misc | Done | 3/3 | RAISE-662, RAISE-604, RAISE-549 |

**Total delivered: 42 stories across 7 capabilities.**

---

## Roadmap — Remaining Work

### Dependency Graph

```text
RAISE-1052 (Jira Transport)
  │
  └──→ RAISE-1130 (Self-Service)
         │
         └──→ RAISE-1131 (Reliability)
```

### Execution Schedule (ADR-015 aligned)

| Ronda | Epic | Jira | Stories | Session | Worktree | Depends on |
|:-----:|------|------|:-------:|:-------:|----------|------------|
| 1 | Jira Adapter v2 — Transport | RAISE-1052 | ~6 | 1 | `e1052-jira-adapter-v2/` | — |
| 2 | Adapter Self-Service | RAISE-1130 | ~6 | 1 | `e1130-adapter-self-service/` | RAISE-1052 |
| 3 | Adapter Reliability | RAISE-1131 | ~4 | 1 | `e1131-adapter-reliability/` | RAISE-1130 |

**No parallelization within this capability stream** — each ronda depends on the previous.
Parallelization opportunities exist with OTHER capability streams (e.g., domains, skills)
that don't share adapter code.

---

## Ronda 1: RAISE-1052 — Jira Adapter v2 (Transport)

**Objective:** Port Jira from ACLI subprocess to `atlassian-python-api`.
Same pattern as E1051 (Confluence).

| # | Story | Size | Description |
|---|-------|:----:|-------------|
| S1052.1 | Jira Client Wrapper | M | Wrapper over `atlassian.Jira`, auth, error normalization |
| S1052.2 | Config Schema + Pydantic Models | S | Migrate jira.yaml to Pydantic, backwards compat |
| S1052.3 | PythonApiJiraAdapter | M | Replace AcliJiraAdapter, all 11 PM methods |
| S1052.4 | Integration Tests | S | E2E with real Jira, skip when unavailable |
| S1052.5 | Delete ACLI Adapter | S | Remove AcliJiraAdapter, acli_bridge, migrate entry point |
| S1052.6 | Documentation | S | User guide, architecture doc |

**Scope:** `work/epics/e1052-jira-adapter-v2/` (to be created at epic-start)
**Status:** Backlog — ready for `/rai-epic-design`

---

## Ronda 2: RAISE-1130 — Adapter Self-Service

**Objective:** Discovery + Doctor + Config Generator for both Jira and Confluence.
A new user runs `/rai-adapter-setup` → validated config in < 5 minutes.

| # | Story | Size | Description | Origin |
|---|-------|:----:|-------------|--------|
| S1130.1 | Confluence Discovery Service | S | Query spaces, page trees, labels | ex-S1051.4 |
| S1130.2 | Jira Backend Discovery | M | Query projects, workflows, transitions | new |
| S1130.3 | Adapter Doctor — unified | M | Validate config vs live backend (both) | ex-S1051.5 |
| S1130.4 | Config Generator — Confluence | M | Interactive discovery → YAML | ex-S1051.6 |
| S1130.5 | Config Generator — Jira | M | Same pattern for Jira | new |
| S1130.6 | Unified `/rai-adapter-setup` skill | S | Orchestrates both generators | new |

**Scope:** `work/epics/e1130-adapter-self-service/scope.md`
**Status:** Backlog — depends on RAISE-1052

---

## Ronda 3: RAISE-1131 — Adapter Reliability

**Objective:** Observable, resilient, user-friendly when things go wrong.

| # | Story | Size | Description |
|---|-------|:----:|-------------|
| S1131.1 | Generalized Adapter Telemetry | S | Structured events across all adapters |
| S1131.2 | Graceful Degradation | M | Jira fail → Filesystem fallback with warning |
| S1131.3 | Human Error Messages | S | Actionable messages referencing `rai adapter doctor` |
| S1131.4 | Session-Start Health Check | S | Non-blocking adapter health on session start |

**Scope:** `work/epics/e1131-adapter-reliability/scope.md`
**Status:** Backlog — depends on RAISE-1130

---

## Superseded

| Document/Issue | Status | Replaced by |
|----------------|--------|-------------|
| adapter-backlog-v2.md (original 2026-03-28) | Superseded | This document |
| E1021 (Adapter Config Foundation) | Superseded | RAISE-1130 |
| RAISE-829 (Backlog Adapter v2) | Done | CAP-3 |
| RAISE-830 (Documentation Adapter v2) | Done | CAP-5 |
| RAISE-1051 (Confluence Adapter v2) | Done (7/10) | CAP-4 + deferred → RAISE-1130 |
| RAISE-744 (default_instance) | Done | CAP-3 |
| RAISE-662 (custom fields) | Done | CAP-7 |
| RAISE-604 (signal emit-work) | Done | CAP-7 |
| RAISE-549 (clean Jira refs) | Done | CAP-7 |

## Score

| Metric | Value |
|--------|-------|
| Capabilities delivered | 7 (42 stories) |
| Remaining epics | 3 |
| Remaining stories | ~16 |
| Sessions to complete | 3 (sequential) |
| Parallelizable with other streams | Yes (all 3 rondas) |
