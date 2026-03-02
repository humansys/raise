# Epic Scope: E337 — Declarative MCP Adapter Framework

## Objective

Enable integration of any MCP server via declarative YAML config (~50-80 lines) instead of dedicated Python adapter code (~400 LOC), while keeping existing adapters unchanged.

**Value:** Unblocks GitHub, Linear, GitLab integrations without framework developer effort. Users write YAML, not Python.

## In Scope (MUST)

- Mini expression evaluator (dot-access, type coercion, default, pluck, json filters)
- Pydantic models for YAML adapter config validation
- Generic `DeclarativeMcpAdapter` class implementing both PM and Docs protocols via YAML mapping
- YAML discovery integrated in `_resolve.py` (not in `registry.py` — keeps core stable)
- Reference config (github.yaml) + CLI validation command (`rai adapter validate`)

## In Scope (SHOULD)

- Docs protocol support in same adapter class (5 additional methods)

## Out of Scope

| Item | Rationale | Deferred To |
|------|-----------|-------------|
| Auto-discovery of MCP tools (Level 3) | Premature — Level 2 covers 80% | Future epic |
| Jinja2 or complex template engine | 4 filters suffice, zero deps | Extend evaluator if needed |
| Changes to existing adapters | Not needed — entry points have priority | N/A |
| Changes to McpBridge | Already stable (E301) | N/A |
| Changes to `registry.py` | Stable core, discovery goes in `_resolve.py` instead (AR-Q2) | N/A |
| MCP server installation/management | Orthogonal concern | Toolchain epic |

## Stories

| # | Story | Size | Description | Depends On |
|---|-------|------|-------------|------------|
| S337.1 | Expression evaluator + YAML schema | S | `ExpressionEvaluator` (~100 LOC) + `DeclarativeAdapterConfig` Pydantic models (~80 LOC). Merged: tightly coupled, no artificial boundary (AR-R3). | — |
| S337.2 | DeclarativeMcpAdapter (PM) | M | Generic adapter class, 11 `AsyncProjectManagementAdapter` methods via YAML dispatch. Single shared McpBridge (AR-C2). Response model inferred from method name, not YAML (AR-R1). | S337.1 |
| S337.3 | YAML discovery in resolver | S | `discover_yaml_adapters()` in `_resolve.py`, merge with entry point results. Factory closure for no-arg instantiation (AR-C1). | S337.2 |
| S337.4 | Docs protocol support | S | Extend same adapter class for `AsyncDocumentationTarget` (5 methods). One class, both protocols (AR-Q1). | S337.2 |
| S337.5 | Reference config + validation CLI | S | Working `github.yaml`, `rai adapter validate <file>`, authoring docs. Merged: validate without reference has no user (AR-Q3). | S337.3 |

**Critical path:** S337.1 → S337.2 → S337.3 → S337.5
**Parallel after S337.2:** S337.3, S337.4

## Architecture Review Decisions (AR-*)

| ID | Decision | Rationale |
|----|----------|-----------|
| AR-C1 | Factory closure for YAML adapters (not `type`) | `_resolve.py:82` calls `cls()` with no args; YAML adapter needs config at construction |
| AR-C2 | Single shared McpBridge per adapter lifetime | Bridge creates subprocess — must reuse, not create per-call |
| AR-R1 | Eliminate `model` field from ResponseMapping | Adapter knows return type per protocol method — no string→class registry needed |
| AR-R2 | Simplify `env` to list of var names | Most MCP servers read env vars directly; `env→flag` conversion is rare edge case |
| AR-R3 | Merge expression evaluator + schema into one story | ~180 LOC combined, tightly coupled, still S size |
| AR-Q1 | One class for PM + Docs | Dispatch table, not logic — two classes would duplicate constructor + dispatch |
| AR-Q2 | Discovery in `_resolve.py`, not `registry.py` | Registry is stable core (91 LOC, stdlib). Keeps dependency direction correct. |
| AR-Q3 | Merge validation CLI + reference config | Validate command without example has no user |

## Done Criteria

- [ ] Any MCP server can be integrated via YAML config (validated by reference config)
- [ ] `rai backlog --adapter <name>` works with YAML-defined adapter
- [ ] `rai adapter validate` catches invalid configs with clear errors
- [ ] Existing adapters (Jira, Confluence, Filesystem) unaffected (regression test)
- [ ] All new code has unit + integration tests
- [ ] ADR-041 accepted and referenced

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Expression evaluator insufficient for edge cases | Low | Medium | `| json` filter as escape hatch; extend evaluator incrementally |
| MCP server response format varies unpredictably | Medium | Medium | `items_path` + `fields` mapping handle nesting; fallback to raw bridge |
| Registry collision between YAML and entry point names | Low | Low | Entry points have priority (D4); warn on collision |

---

## Implementation Plan

### Sequence

| # | Story | Size | Strategy | Rationale |
|---|-------|------|----------|-----------|
| 1 | S337.1: Expression evaluator + YAML schema | S | Walking skeleton | Foundation — every other story imports these. Well-defined from research, zero risk. |
| 2 | S337.2: DeclarativeMcpAdapter (PM) | M | Risk-first | Core architectural bet. If dispatch-table-over-YAML doesn't work, pivot early. Largest story, most unknowns. |
| 3a | S337.3: YAML discovery in resolver | S | Dependency-driven | Unblocks E2E: `rai backlog --adapter github` works with YAML. Critical path. |
| 3b | S337.4: Docs protocol support | S | Parallel (with 3a) | Independent — extends adapter.py with 5 docs methods. Same dispatch pattern from S337.2. |
| 4 | S337.5: Reference config + validation CLI | S | Quick win | Capstone — validates whole stack E2E with real github.yaml. |

### Milestones

| Milestone | Stories | Success Criteria |
|-----------|---------|------------------|
| **M1: Walking Skeleton** | S337.1 + S337.2 | Adapter instantiated from YAML fixture, mocked bridge returns parsed IssueRef. All 11 PM methods dispatch or raise NotImplementedError. |
| **M2: E2E Integration** | + S337.3 | `rai backlog search --adapter github "query"` resolves YAML adapter → creates bridge → calls tool → returns IssueSummary list. Existing adapters (jira, filesystem) unaffected. |
| **M3: Epic Complete** | + S337.4 + S337.5 | Reference github.yaml documented. `rai adapter validate` catches invalid configs. Docs protocol works. All done criteria met. |

### Progress Tracking

| Story | Status | Velocity | Notes |
|-------|--------|----------|-------|
| S337.1 | pending | — | |
| S337.2 | pending | — | |
| S337.3 | pending | — | |
| S337.4 | pending | — | |
| S337.5 | pending | — | |

### Sequencing Risks

| Risk | Mitigation |
|------|------------|
| S337.2 (M) takes longer than expected due to response parsing edge cases | Timebox response mapping to known protocol models; complex cases use `| json` filter |
| S337.3 factory closure breaks `_resolve.py` type assumptions | Type change is minimal; test with both entry point and YAML adapters in same run |
| Parallel S337.3/S337.4 creates merge conflicts in adapter.py | S337.4 only adds methods, S337.3 doesn't touch adapter.py — no overlap |
