# Adapter Backlog v2 — Designed from Vision

> **Date:** 2026-03-28
> **Story:** RAISE-1000
> **Source:** `governance/product/adapter-vision.md`
> **Status:** Proposal — pending comparison with existing backlog (RAISE-829, 830)

---

## Design Principle

**Config first, features second, reliability third.**

The adapter cannot be reliable if its configuration is fragile. The configuration
cannot be reliable if a human must know Jira transition IDs. Therefore: generate
and validate config before building features on top of it.

This inverts the current backlog (RAISE-829/830) which patches features onto
fragile config.

---

## Epic 1: Adapter Configuration Foundation

**Tesis:** Sin config confiable, todo lo demas es fragil.

| # | Story | Description | Size |
| --- | --- | --- | --- |
| 1.1 | Jira Backend Discovery | Query Jira API: projects, workflows, transition IDs, components, versions, issue types. Produce backend map. | M |
| 1.2 | Confluence Backend Discovery | Query Confluence: spaces, page tree, templates, labels. Produce space map. | S |
| 1.3 | Config Generator (`/rai-adapter-setup`) | Interactive skill: present discoveries, human selects, generate correct YAML. | M |
| 1.4 | Adapter Doctor (`rai adapter doctor`) | Read config, query backend, report mismatches, suggest fixes, score health. | M |
| 1.5 | Confluence Config Schema | Expand `.raise/confluence.yaml`: routing by artifact-type, parent pages, templates, labels. | S |
| 1.6 | Jira Multi-Project Routing | Expand `.raise/jira.yaml`: routing by project, resolved from issue key prefix. | S |

**Dependencies:**

- 1.1, 1.2 are independent (can parallel)
- 1.3 depends on 1.1 + 1.2
- 1.4 depends on 1.1 + 1.2
- 1.5, 1.6 depend on 1.3

**Deliverable:** `/rai-adapter-setup` on a new repo → 3-4 questions → complete validated config.

---

## Epic 2: Protocol Completeness

**Tesis:** Adapter protocols must be complete contracts. If a skill needs a
workaround, the adapter is incomplete.

| # | Story | Description | Size |
| --- | --- | --- | --- |
| 2.1 | IssueSpec v2 — Complete Work Domain Contract | Redesign IssueSpec as the complete model: component, fix_version, parent_key, all issue types (Initiative, Bug). Design the final model, not incremental patches. | M |
| 2.2 | Lifecycle Mapping v2 | Redesign BacklogHook lifecycle: story, epic, bug, initiative with start/close/selected. Derived from config, not hardcoded. | S |
| 2.3 | DocumentationTarget v2 — Publish with Routing | `publish()` accepts artifact-type, resolves parent page, template, and labels from Confluence config. | M |
| 2.4 | Label Management in Confluence | `add_label`, `get_labels`, `remove_label` in DocumentationTarget. Required for CQL and Rovo. | S |
| 2.5 | Phase Comments on Transitions | BacklogHook adds context comment on transitions: skill, source state, timestamp. Automatic audit trail. | S |

**Dependencies:**

- 2.1 depends on Epic 1 (config informs what fields are possible)
- 2.2 depends on 2.1
- 2.3 depends on 1.5
- 2.4 depends on 2.3
- 2.5 depends on 2.2

**Deliverable:** `rai backlog create` creates idiomatic issues. `rai docs publish adr` routes correctly with labels.

---

## Epic 3: Operational Reliability

**Tesis:** Observable, diagnosable, resilient to config errors. Silent failures
are unacceptable.

| # | Story | Description | Size |
| --- | --- | --- | --- |
| 3.1 | Adapter Telemetry | Structured event per operation: operation, duration, success/failure, backend. | S |
| 3.2 | Graceful Degradation | Jira fail → Filesystem fallback (if available). Warning, not error. | M |
| 3.3 | Human Error Messages | Replace tracebacks with actionable messages referencing `rai adapter doctor`. | S |
| 3.4 | Confluence Index Auto-Generation | Regenerate section index pages on publish (ADR Index, Pattern Catalog, etc.). | M |
| 3.5 | Fix default_instance Blocker | Defensive fix for fresh installs. Should be impossible after 1.3/1.4 but backwards compat. | XS |

**Dependencies:**

- 3.1 independent
- 3.2 depends on 2.1
- 3.3 depends on 1.4
- 3.4 depends on 2.3
- 3.5 depends on 1.4

**Deliverable:** Adapter tells you what went wrong and how to fix it. Doesn't break if backend unavailable.

---

## Sequencing

```text
Epic 1: Config Foundation
  1.1 Jira Discovery ─────┐
  1.2 Confluence Discovery ┼──→ 1.3 Setup Skill ──→ 1.5 Confluence Schema
                           │                    └──→ 1.6 Multi-Project
                           └──→ 1.4 Doctor

Epic 2: Protocol Completeness
  2.1 IssueSpec v2 ←── Epic 1 (config informs model)
  2.2 Lifecycle v2 ←── 2.1
  2.3 Publish with Routing ←── 1.5
  2.4 Label Management ←── 2.3
  2.5 Phase Comments ←── 2.2

Epic 3: Operational Reliability
  3.1 Telemetry (independent)
  3.2 Graceful Degradation ←── 2.1
  3.3 Error Messages ←── 1.4
  3.4 Index Auto-Gen ←── 2.3
  3.5 Fix default_instance ←── 1.4
```

**Critical path:** 1.1 → 1.3 → 2.1 → 2.2 (Jira end-to-end)
**Parallel path:** 1.2 → 1.5 → 2.3 → 2.4 (Confluence end-to-end)

---

## Total Scope

| Epic | Stories | Estimated Size |
| --- | --- | --- |
| 1: Config Foundation | 6 | 3M + 3S |
| 2: Protocol Completeness | 5 | 2M + 3S |
| 3: Operational Reliability | 5 | 2M + 2S + 1XS |
| **Total** | **16** | **7M + 8S + 1XS** |

---

## What this replaces (comparison pending)

This backlog was designed from `adapter-vision.md` without reference to existing
issues. The following existing epics/stories need comparison:

- RAISE-829 (Stabilize Backlog Adapter v2) — 7 stories
- RAISE-830 (Stabilize Documentation Adapter v2) — 6 stories
- RAISE-744 (default_instance bug)
- RAISE-549 (Clean Jira references)
- RAISE-662 (Custom fields flag)
- RAISE-604 (signal emit-work multi-adapter)

Comparison should determine:

1. Which existing stories map cleanly to v2 stories
2. Which existing stories are obsoleted by the new design
3. Which existing stories cover scope not in v2 (gaps in the new design)
4. Which existing bugs are fixed by the new architecture vs need explicit fixes
