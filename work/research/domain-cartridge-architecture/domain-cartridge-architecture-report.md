# Research Report: Domain Cartridge Architecture

> **Date:** 2026-03-22
> **Researcher:** Emilio + Rai
> **Depth:** Standard (24 sources, 3 parallel research tracks)
> **Confidence:** HIGH — all major claims triangulated by 3+ independent sources
> **Feeds into:** ADR for Unified Cartridge Runtime (RAISE-652)

---

## Executive Summary

The research confirms that treating Work, Governance, and Knowledge as pluggable domain cartridges is well-grounded in SOTA. The pattern is not novel — it's a convergence of three mature architectural traditions:

1. **Schema-as-contract** (Data Contract Specification, dbt, Specmatic)
2. **Provider-isolation + composition** (Backstage Catalog, Apollo Federation, Jena)
3. **Work-as-knowledge-graph** (Rovo Teamwork Graph, Linear, GitLab Work Items)

The unique contribution of RaiSE is **applying this convergence to AI agent infrastructure** — making the agent's operational knowledge (work items, governance decisions, domain expertise) uniformly pluggable, schema-validated, and queryable.

---

## 1. The Convergence Pattern

Three independent architectural traditions converge on the same structure:

```
Domain Cartridge (universal pattern)
├── Schema     → Data Contract Spec / dbt contracts / Pydantic models
├── Provider   → Backstage EntityProvider / Apollo subgraph / Jena sub-graph
├── Validation → Great Expectations / Haystack assembly / Apollo composition
├── Query      → GraphQL / Dataview DQL / SPARQL / rai graph query
└── Operations → LlamaIndex Packs / Haystack pipelines / rai skills
```

**This is not a coincidence.** The pattern emerges because all these systems face the same fundamental problem: heterogeneous data from multiple sources must be unified into a queryable graph with consistency guarantees.

---

## 2. Five Design Principles (from SOTA)

### P1: Schema-as-Contract at the Boundary

**Sources:** Data Contract Spec, dbt, Specmatic, Pydantic

The schema is not documentation — it's an executable contract. Each cartridge declares what data it produces (fields, types, constraints) in a machine-readable format. Validation happens at the adapter boundary when data enters the system, not at query time.

**For RaiSE:** Each cartridge's `schema.yaml` defines the GraphNode fields required for that domain. The adapter validates data against the schema before producing nodes. Invalid data is rejected or flagged, not silently ingested.

### P2: Provider-Owns-Bucket Isolation

**Sources:** Backstage EntityProvider, Apollo Federation subgraphs, Jena union graphs

Each data source (provider) owns an isolated "bucket" of entities. Providers can't overwrite each other's data. Conflict resolution is explicit (locationKey in Backstage, @key in Apollo).

**For RaiSE:** The JiraWorkAdapter owns all `epic-RAISE-*` and `story-RAISE-*` nodes. The FilesystemGovernanceAdapter owns all `adr-*` nodes. Neither can produce nodes in the other's namespace. The graph builder merges buckets into a union graph.

### P3: Composition over Rigid Schema

**Sources:** GitLab widgets, Notion properties, Backstage extensible kinds, DDD bounded contexts

Entity types are not fixed — they're compositions of capabilities. A work item in GitLab is a base entity + selected widgets. A page in Notion is a block + selected properties.

**For RaiSE:** A cartridge's schema defines which metadata fields are required for that domain, but the GraphNode model is extensible via the `metadata` dict. The Work cartridge requires `status`, `priority`, `labels`; the Knowledge cartridge requires `decision_area`, `difficulty`, `relationships`. Both produce GraphNode, but with different metadata contracts.

### P4: Build-Time Validation (Shift Left)

**Sources:** Apollo composition, Haystack assembly validation, dbt contract enforcement, Specmatic

Catch inconsistencies at build/assembly time, not at runtime. Apollo's Rover CLI checks schema composition in CI. Haystack validates pipeline connections before execution.

**For RaiSE:** `rai graph build` is the composition step. Schema validation runs during build — before any query. A work item missing required labels produces a build warning. A governance artifact without frontmatter produces a build error. CI can gate on `rai graph build --strict`.

### P5: Overlay Graph (No Migration Required)

**Sources:** Rovo Teamwork Graph, Obsidian Dataview, SKOS/Dublin Core

The graph is a **view** over existing data, not a copy. Data stays in Jira, Confluence, filesystem. The graph indexes and links entities without requiring migration.

**For RaiSE:** `rai graph build` doesn't copy data from Jira into files — it queries Jira at build time and produces graph nodes. The files in `work/epics/` become optional (legacy or fallback), not the source of truth. The graph is ephemeral — rebuilt on demand from live sources.

---

## 3. The Cartridge Anatomy (Grounded)

Based on the convergence of all 24 sources, the universal cartridge anatomy is:

```yaml
# .raise/cartridges/{domain}/cartridge.yaml
name: work                          # domain identifier
version: "1.0"
kind: cartridge                     # Backstage-inspired kind system

schema:
  node_types:                       # what GraphNode types this cartridge produces
    - epic
    - story
    - task
    - bug
  required_metadata:                # Data Contract Spec -inspired field contracts
    epic:
      - field: status
        type: enum
        values: [backlog, selected, in_progress, done]
      - field: labels
        type: list[str]
        min_items: 1                # at least 1 domain label
      - field: priority
        type: enum
        values: [critical, high, major, minor, trivial]
    story:
      - field: status
        type: enum
        values: [backlog, selected, in_progress, done]
      - field: epic_key
        type: str
        required: true              # no orphan stories

provider:                           # Backstage EntityProvider -inspired
  backend: jira                     # or: filesystem, server
  config:
    project: RAISE
    instance: humansys              # from .raise/jira.yaml

gates:                              # validation at build time
  - id: no-orphan-stories
    check: "all stories have epic_key"
  - id: required-labels
    check: "all epics have at least 1 domain label"
  - id: meaningful-priority
    check: "not all issues have same priority"

skills:                             # operations on this domain
  - /rai-story-start
  - /rai-story-close
  - /rai-backlog-search

prompting:                          # LLM context when working with this domain
  system: |
    Work items follow the lifecycle: Backlog → Selected → In Progress → Done.
    Stories must belong to an epic. Epics must belong to a capability.
```

---

## 4. Key Architectural Decision Points

### 4.1: Single canonical schema vs. per-context schemas?

**DDD says:** Per-context (Anti-Corruption Layer). The Work cartridge's view of an "epic" is different from the Knowledge cartridge's view.

**Backstage/Apollo say:** Shared entity kinds with extensible properties. The `Component` kind is universal but different systems add different metadata.

**Recommendation:** **Shared GraphNode model + per-cartridge metadata contract.** All cartridges produce `GraphNode`, but each defines its own `required_metadata` schema. The ACL is the adapter — it translates Jira fields to GraphNode metadata, Confluence pages to GraphNode metadata, etc. The graph is the union of all cartridge outputs.

**Confidence:** HIGH

### 4.2: Runtime validation or build-time validation?

**Apollo/dbt say:** Build-time (shift left).

**Pydantic/Great Expectations say:** Runtime at boundary.

**Recommendation:** **Both.** Pydantic validates at the adapter boundary (data entering the system). `rai graph build --strict` validates the assembled graph against all cartridge schemas. CI gates on strict mode.

**Confidence:** HIGH

### 4.3: Data copy or overlay graph?

**Rovo/Obsidian say:** Overlay (no copy).

**KGTK says:** Export to flat format for pipeline processing.

**Recommendation:** **Overlay as default, export as option.** `rai graph build` queries live sources. `rai graph export` produces static artifacts for CI/offline use. No migration step — the graph IS the query.

**Confidence:** HIGH

### 4.4: Cartridge discovery — explicit registration or convention-based?

**Backstage says:** Explicit EntityProvider registration.

**Jena says:** Import declarations in ontology metadata.

**LlamaIndex says:** CLI installation + hub discovery.

**Recommendation:** **Convention-based with explicit override.** Default: discover cartridges in `.raise/cartridges/*/cartridge.yaml`. Override: `rai cartridge install <name>` for external cartridges. Entry points for Python-code cartridges (backward compat with ScaleUp).

**Confidence:** MEDIUM-HIGH

---

## 5. Implications for RaiSE

### RAISE-650 (Domain Cartridges) evolves to:
- The cartridge runtime in raise-core
- ScaleUp, GTD, etc. are Knowledge cartridges
- The cartridge.yaml manifest replaces domain.yaml (superset)

### RAISE-651 (Graph Data Abstraction) evolves to:
- The "managers" become cartridge providers (one per domain)
- `.raise/graph.yaml` becomes `.raise/cartridges/` directory
- The Protocol is the cartridge provider interface

### Both epics merge conceptually:
- RAISE-650 defines the runtime + Knowledge cartridge type
- RAISE-651 defines the Work + Governance cartridge types
- The ADR unifies them under one architecture

### governance/jira-confluence-standards.md evolves to:
- `work/cartridge.yaml` schema section (machine-readable)
- `governance/cartridge.yaml` schema section
- The markdown doc becomes the human-readable companion

---

## 6. Risks and Mitigations

| Risk | Source | Mitigation |
|------|--------|------------|
| Over-engineering — cartridge runtime too complex for current needs | P2 Simplicity principle | Start with 2 cartridges (Work + Knowledge). Governance comes later. Keep runtime minimal |
| Schema alignment across cartridges remains manual | ODPs literature | Accept this — automated alignment is unsolved. Provide tooling for validation, not automation |
| Performance — querying live Jira/Confluence at build time is slow | Rovo architecture | Cache strategy: build produces cached graph file. Incremental builds via change detection |
| Backward compatibility — existing ScaleUp code uses Python classes | Jena three-axis pattern | Python-class adapters remain valid as a provider type alongside YAML-configured generic adapters |

---

## 7. Recommendation

**Proceed with the ADR.** The research confirms:

1. The pattern is well-grounded (convergence of 3 mature traditions, 24 sources)
2. No prior art combines all three into an AI agent infrastructure layer (our unique contribution)
3. The five design principles (P1-P5) provide clear architectural guardrails
4. The cartridge anatomy is concrete enough to implement
5. Key decision points have HIGH confidence recommendations

**Suggested ADR structure:**
- Context: RAISE-650 + RAISE-651 convergence insight
- Decision: Unified Cartridge Runtime with P1-P5 principles
- Consequences: Both epics align, schema-as-contract replaces governance markdown, graph build becomes cartridge composition

---

*Evidence catalog: [sources/evidence-catalog.md](sources/evidence-catalog.md)*
*Research directory: `work/research/domain-cartridge-architecture/`*
*Next: ADR draft → RAISE-652*
