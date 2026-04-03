# S760.7: Adapter Gap Analysis — Consolidated

**Epic:** RAISE-760
**Date:** 2026-03-27
**Status:** Draft
**Inputs:** S760.2 (Taxonomy), S760.3 (Workflow), S760.4 (Confluence IA), S760.5 (Compass), S760.6 (Bitbucket)

---

## 1. Purpose

This document consolidates all gaps identified across S760.2-S760.6 between
the idiomatic Atlassian model and RaiSE's current adapter/hook layer. Each gap
becomes an actionable backlog story.

---

## 2. Current Adapter Inventory

| Adapter | Protocol | Transport | Product | Status |
|---------|----------|-----------|---------|--------|
| `AcliJiraAdapter` | `AsyncProjectManagementAdapter` | ACLI subprocess | Jira | Production |
| `McpConfluenceAdapter` | `AsyncDocumentationTarget` | mcp-atlassian via McpBridge | Confluence | Production |
| `FilesystemPMAdapter` | `ProjectManagementAdapter` | Local filesystem | None (OSS default) | Production |
| `FilesystemDocsAdapter` | — | Local filesystem | None (planned) | Backlog (RAISE-811) |
| `BacklogHook` | `LifecycleHook` | Jira via adapter | Jira | Production |

**No adapter exists for:** Compass, Bitbucket, Rovo, Jira Automation webhooks.

---

## 3. Gaps by Product

### 3.1 Jira Adapter (AcliJiraAdapter)

Source: S760.2 (Taxonomy), S760.3 (Workflow)

| Gap ID | Description | Source | Priority | Effort | Backlog Story |
|--------|-------------|--------|----------|--------|---------------|
| GAP-J1 | **Initiative issue type support** — `create_issue` doesn't handle Initiative creation. `IssueSpec` needs `issue_type` to accept "Initiative". | S760.2 | P1 | XS | Create Initiative issues via `rai backlog create` |
| GAP-J2 | **Component assignment on create** — `IssueSpec` doesn't include component field. Taxonomy requires every Story/Bug to have a component. | S760.2 | P1 | S | Add `component` field to `IssueSpec` model |
| GAP-J3 | **fixVersion assignment on create** — `IssueSpec` doesn't include fixVersion. Taxonomy requires every Story to have a version. | S760.2 | P1 | S | Add `fix_version` field to `IssueSpec` model |
| GAP-J4 | **Bug/Initiative lifecycle mapping** — `BacklogHook` only maps story/epic events. `jira.yaml` needs `bug_start`, `bug_close`, `initiative_start`, `initiative_close`. | S760.3 | P1 | S | Extend BacklogHook with bug/initiative mappings |
| GAP-J5 | **Phase info in Jira comments** — BacklogHook transitions but doesn't add context about which phase (design, plan, implement, review). | S760.3 | P2 | S | Add phase comment on transition |
| GAP-J6 | **"Selected for Development" transition** — `lifecycle_mapping` doesn't support `story_selected` or `epic_selected` for grooming. | S760.2 | P2 | XS | Add `selected` lifecycle event |

### 3.2 Confluence Adapter (McpConfluenceAdapter)

Source: S760.4 (Confluence IA)

| Gap ID | Description | Source | Priority | Effort | Backlog Story |
|--------|-------------|--------|----------|--------|---------------|
| GAP-C1 | **Label management** — can't add/remove labels on page create/update. IA requires labels for all artifact types (`type:adr`, `epic:RAISE-760`, etc.). | S760.4 | P1 | S | Add label CRUD to McpConfluenceAdapter |
| GAP-C2 | **Artifact-type routing** — `rai docs publish` doesn't route by type to the correct page tree location. Publishing an ADR should land under `Architecture/ADRs/`, a research report under `Research/`. | S760.4 | P1 | M | Route publish by doc_type to IA tree |
| GAP-C3 | **Index page generation** — no auto-generated ADR Index, Pattern Catalog, or Skill Index pages. | S760.4 | P1 | M | Generate index pages on publish |
| GAP-C4 | **Space template registration** — can't register Confluence page templates programmatically. Needed for setup. | S760.4 | P2 | S | Template CRUD support |
| GAP-C5 | **Batch page tree creation** — `rai init --stack atlassian` needs to create the full IA tree (11 sections + sub-pages) in one operation. | S760.4 | P2 | M | Batch page creation for init |
| GAP-C6 | **Content properties** — can't set machine-readable metadata on pages. Useful for Rovo query optimization. | S760.4 | P3 | S | Content property support |
| GAP-C7 | **Attachment support** — can't upload diagrams or images to pages. | S760.4 | P3 | S | Attachment upload support |

### 3.3 Compass (No Adapter Exists)

Source: S760.5 (Compass Catalog)

| Gap ID | Description | Source | Priority | Effort | Backlog Story |
|--------|-------------|--------|----------|--------|---------------|
| GAP-X1 | **No Compass adapter** — no protocol, no implementation. Need `CompassCatalogAdapter` or similar. | S760.5 | P2 | M | Design Compass adapter protocol |
| GAP-X2 | **Component CRUD** — create/update/archive Compass components from `rai` CLI. | S760.5 | P2 | M | Implement Compass component management |
| GAP-X3 | **Scorecard management** — apply/update scorecard criteria programmatically. | S760.5 | P3 | M | Scorecard API integration |
| GAP-X4 | **DORA metric provider** — push deployment/lead-time/MTTR metrics from RaiSE telemetry to Compass via Forge `compass:dataProvider`. | S760.5 | P3 | L | DORA metric pipeline |
| GAP-X5 | **Jira ↔ Compass linking** — link Epics to Compass components. Native integration exists but needs adapter support for automation. | S760.5 | P2 | S | Epic-to-component linking |

### 3.4 Bitbucket (No Adapter — Design for Partners)

Source: S760.6 (Bitbucket Integration)

| Gap ID | Description | Source | Priority | Effort | Backlog Story |
|--------|-------------|--------|----------|--------|---------------|
| GAP-B1 | **Branch naming helper** — RaiSE branch model (ADR-033) doesn't embed Jira keys in branch names. Need utility to create Bitbucket-compatible branches. | S760.6 | P2 | S | Branch naming convention for Jira auto-linking |
| GAP-B2 | **Pipeline template** — no `bitbucket-pipelines.yml` reference config for RaiSE projects. | S760.6 | P2 | S | Bitbucket Pipeline reference config |
| GAP-B3 | **PR template** — no `.bitbucket/pull-request-template.md` for RaiSE convention. | S760.6 | P3 | XS | Bitbucket PR template |

### 3.5 Hooks & Automation Glue

Source: S760.3 (Workflow & Automation)

| Gap ID | Description | Source | Priority | Effort | Backlog Story |
|--------|-------------|--------|----------|--------|---------------|
| GAP-H1 | **ConfluenceArchiveHook** — `session:close` event should POST session data to Jira Automation webhook for Confluence archiving. | S760.3 | P1 | S | New hook: session → Confluence archive |
| GAP-H2 | **CompassMetricHook** — `release:publish` event should POST deployment event to Compass metric API via Forge. | S760.3 | P2 | M | New hook: release → Compass DORA |
| GAP-H3 | **GraphSyncHook** — `graph:build` event should auto-push to raise-server. Currently requires manual `rai graph sync`. | S760.3 | P2 | S | New hook: graph build → auto-sync |
| GAP-H4 | **Automation webhook URL in jira.yaml** — no config section for Jira Automation webhook endpoints. | S760.3 | P1 | XS | Add `automation` section to jira.yaml |

### 3.6 Protocol Gaps

Source: Cross-cutting analysis

| Gap ID | Description | Source | Priority | Effort | Backlog Story |
|--------|-------------|--------|----------|--------|---------------|
| GAP-P1 | **`IssueSpec` model incomplete** — missing `component`, `fix_version`, `parent_key` fields. Taxonomy requires these for idiomatic Jira usage. | S760.2 | P1 | S | Extend IssueSpec model |
| GAP-P2 | **No `CatalogAdapter` protocol** — Compass needs a new adapter protocol for component catalog operations (CRUD, scorecards, metrics). | S760.5 | P2 | M | Design CatalogAdapter protocol |
| GAP-P3 | **`DocumentationTarget.publish` lacks label support** — metadata dict is untyped. Need explicit label parameter or typed PublishMetadata model. | S760.4 | P1 | S | Type the publish metadata |
| GAP-P4 | **`atlassian-python-api` dependency audit** — may be vestigial in raise-pro. ACLI and MCP replaced direct usage. | R2 | P3 | XS | Audit and remove if unused |

---

## 4. Priority Summary

### P1 — Required for Idiomatic Model (13 gaps)

| ID | Description | Effort |
|----|-------------|--------|
| GAP-J1 | Initiative issue type support | XS |
| GAP-J2 | Component on create | S |
| GAP-J3 | fixVersion on create | S |
| GAP-J4 | Bug/Initiative lifecycle in BacklogHook | S |
| GAP-C1 | Label management in Confluence adapter | S |
| GAP-C2 | Artifact-type routing for publish | M |
| GAP-C3 | Index page generation | M |
| GAP-H1 | ConfluenceArchiveHook | S |
| GAP-H4 | Automation webhook URL config | XS |
| GAP-P1 | Extend IssueSpec model | S |
| GAP-P3 | Type publish metadata | S |

**Estimated effort:** ~2-3 epics worth of work (5-8 stories each)

### P2 — Enables Full Stack Integration (11 gaps)

| ID | Description | Effort |
|----|-------------|--------|
| GAP-J5 | Phase info in Jira comments | S |
| GAP-J6 | "Selected" lifecycle event | XS |
| GAP-C4 | Space template registration | S |
| GAP-C5 | Batch page tree creation | M |
| GAP-X1 | Compass adapter protocol | M |
| GAP-X2 | Compass component CRUD | M |
| GAP-X5 | Jira ↔ Compass linking | S |
| GAP-B1 | Branch naming helper | S |
| GAP-B2 | Pipeline template | S |
| GAP-H2 | CompassMetricHook | M |
| GAP-H3 | GraphSyncHook | S |
| GAP-P2 | CatalogAdapter protocol | M |

### P3 — Nice to Have (6 gaps)

| ID | Description | Effort |
|----|-------------|--------|
| GAP-C6 | Content properties | S |
| GAP-C7 | Attachment support | S |
| GAP-X3 | Scorecard management | M |
| GAP-X4 | DORA metric pipeline | L |
| GAP-B3 | PR template | XS |
| GAP-P4 | atlassian-python-api audit | XS |

---

## 5. Recommended Epic Grouping

Gaps should be grouped into implementation epics:

| Proposed Epic | Gaps | Scope | Depends On |
|---------------|------|-------|-----------|
| **Stabilize Backlog Adapter v2** | GAP-J1, J2, J3, J4, J5, J6, P1, H4 | Extend Jira adapter for idiomatic taxonomy | RAISE-760 |
| **Stabilize Documentation Adapter v2** | GAP-C1, C2, C3, C4, C5, P3, H1 | Extend Confluence adapter for IA model | RAISE-760 |
| **Compass Adapter Foundation** | GAP-X1, X2, X5, P2 | New adapter protocol + basic Compass CRUD | RAISE-760 |
| **Bitbucket Integration Kit** | GAP-B1, B2, B3 | Templates and conventions for partner teams | RAISE-760 |
| **DORA & Telemetry Pipeline** | GAP-X3, X4, H2, H3 | Compass metrics, graph auto-sync | Compass Adapter |
| **Confluence Advanced** | GAP-C6, C7 | Content properties, attachments | Stabilize Docs v2 |

---

## 6. Open Questions from Sub-Designs

| # | Question | Source | Impact |
|---|----------|--------|--------|
| 1 | Does current Atlassian plan include Compass with scorecards? | S760.5 | Blocks Compass adapter work |
| 2 | Are historical Jira Component assignments preserved after switching to Compass? | S760.5 | Data preservation |
| 3 | Should raise-server be a Compass component? | S760.5 | Catalog completeness |
| 4 | Should raise-forge be a Compass component? | S760.5 | Catalog completeness (post RAISE-819) |
| 5 | Which Jira Automation plan is available? (Free/Standard/Premium rules?) | S760.3 | Limits number of automation rules |

---

## References

- S760.2: Taxonomy Design — issue types, components, labels, versions
- S760.3: Workflow, Automation & Lifecycle — hooks, automation rules, sync model
- S760.4: Confluence IA — page tree, templates, adapter gaps (GAP-C1 to C7)
- S760.5: Compass Catalog — component definitions, scorecards, migration plan
- S760.6: Bitbucket Integration — branch naming, smart commits, pipelines
- `raise_cli.adapters.protocols` — current adapter contracts
- `raise_cli.hooks.events` — current event types
- `raise_cli.hooks.builtin.backlog` — BacklogHook implementation
