# E1130: Adapter Self-Service — Discovery, Doctor, Config Generator

## Objective

Unified self-service configuration for both Jira and Confluence adapters.
A new user runs `/rai-adapter-setup`, answers 3-4 questions, gets validated
YAML config. `rai adapter doctor` catches drift before it causes failures.

## Context

- Absorbs deferred E1051 stories (S1051.4 discovery, S1051.5 doctor, S1051.6 generator)
- E1051 (Confluence Adapter v2) and E1052 (Jira Adapter v2) both merged — no external blockers
- Confluence stories build on existing `ConfluenceClient` discovery methods
- Jira stories require new discovery methods on `JiraClient`
- Design: `work/epics/e1130-adapter-self-service/design.md`

## Design Decisions

1. **Unified doctor** — `rai adapter doctor` checks both Jira and Confluence in one command
2. **Unified setup skill** — `/rai-adapter-setup` detects available backends, guides both
3. **Discovery is a service, not a CLI** — consumed by doctor and generator, not user-facing
4. **Config generated, not written** — humans never need to know transition IDs (Adapter Vision §3)

## Stories

| # | Story | Size | Description | Origin |
|---|-------|------|-------------|--------|
| S1130.1 | Confluence Discovery Service | S | Wrap `ConfluenceClient` methods into `ConfluenceDiscovery` → `ConfluenceSpaceMap`. | ex-S1051.4 |
| S1130.2 | Jira Discovery Service | M | Add `list_projects()`, `get_project_workflows()`, `get_issue_types()` to `JiraClient` + `JiraDiscovery` → `JiraProjectMap`. | new |
| S1130.3 | Adapter Doctor Check | M | `AdapterDoctorCheck` implementing `DoctorCheck` Protocol. Validates config + env vars + live backend for both adapters. | ex-S1051.5 (expanded) |
| S1130.4 | Config Generator — Confluence | S | `generate_confluence_config(space_map, selections) → dict`. Pure function. | ex-S1051.6 |
| S1130.5 | Config Generator — Jira | M | `generate_jira_config(project_map, selections) → dict`. Discovers workflows, transitions. | new |
| S1130.6 | `/rai-adapter-setup` skill | S | Interactive skill: detect backends → run generators → write YAML. 3-4 questions max. | new |

## Dependencies

```
S1130.1 (Confluence Discovery) ──┐
                                 ├──→ S1130.3 (Doctor) ──→ S1130.6 (Unified Skill)
S1130.2 (Jira Discovery) ────────┘         │
                                           │
S1130.1 ──→ S1130.4 (Confluence Generator) ┘
S1130.2 ──→ S1130.5 (Jira Generator) ──────┘
```

S1130.1 and S1130.2 can run in parallel.
S1130.4 and S1130.5 can run in parallel after their respective discoveries.

**External:** None — E1051 and E1052 both merged.

## Done Criteria

1. `/rai-adapter-setup` on a new repo → 3-4 questions → complete validated config
2. `rai adapter doctor` reports Jira + Confluence health with actionable suggestions
3. Generated config passes doctor validation without edits
4. Existing manually-written configs continue working (backwards compat)

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| Jira workflow discovery returns unexpected structures | Medium | Medium | E494 spike already validated ACLI JSON; new client validates same fields |
| Doctor false positives annoy users | Low | Medium | Warnings vs errors; only error on confirmed mismatches |
| Setup skill UX too complex | Medium | Low | Keep it to 3-4 questions; advanced options in YAML directly |

---

## Implementation Plan

### Sequencing Strategy

**Quick wins + dependency-driven.** Confluence discovery (S) is the quick win — existing
client methods, fast to deliver, unblocks doctor and generator. Jira discovery (M) runs
in parallel as the higher-risk item (new JiraClient methods).

**Critical path:** S1130.2 → S1130.5 → S1130.6

### Parallel Streams

```
Stream A (Confluence):  S1130.1 (S) ──→ S1130.4 (S)  ──┐
                                                         ├──→ S1130.6 (S)
Stream B (Jira):        S1130.2 (M) ──→ S1130.5 (M)  ──┘
                                   │                     │
                                   └──→ S1130.3 (M) ────┘
                        S1130.1 ───────┘
```

### Execution Order

| Pos | Story | Size | Rationale | Enables |
|-----|-------|------|-----------|---------|
| 1a | S1130.1 Confluence Discovery | S | Quick win — wraps existing methods | S1130.3, S1130.4 |
| 1b | S1130.2 Jira Discovery | M | Parallel with 1a — highest risk, start early | S1130.3, S1130.5 |
| 2a | S1130.4 Config Gen Confluence | S | Unblocked by 1a — fast, validates pattern | S1130.6 |
| 2b | S1130.3 Adapter Doctor | M | Unblocked by 1a+1b — validates both discoveries | S1130.6 |
| 2c | S1130.5 Config Gen Jira | M | Unblocked by 1b — applies pattern from 2a | S1130.6 |
| 3 | S1130.6 /rai-adapter-setup | S | Final — orchestrates everything | Done criteria |

### Milestones

#### M1: Discovery (after S1130.1 + S1130.2)
- [ ] `ConfluenceDiscovery.discover()` returns `ConfluenceSpaceMap` from live backend
- [ ] `JiraDiscovery.discover()` returns `JiraProjectMap` from live backend
- [ ] Both services have unit tests with mocked clients + integration tests

#### M2: Doctor + Generators (after S1130.3 + S1130.4 + S1130.5)
- [ ] `rai doctor` includes adapter checks (config + env vars + live validation)
- [ ] `generate_confluence_config()` produces valid YAML matching `ConfluenceConfig` schema
- [ ] `generate_jira_config()` produces valid YAML matching `JiraConfig` schema
- [ ] Generated configs pass doctor validation without edits

#### M3: Epic Complete (after S1130.6)
- [ ] `/rai-adapter-setup` on clean repo → 3-4 questions → complete validated config
- [ ] Existing manually-written configs still work (backwards compat)
- [ ] Retrospective complete

### Progress Tracking

| Story | Size | Status | Notes |
|-------|------|--------|-------|
| S1130.1 Confluence Discovery | S | pending | |
| S1130.2 Jira Discovery | M | pending | |
| S1130.3 Adapter Doctor | M | pending | |
| S1130.4 Config Gen Confluence | S | pending | |
| S1130.5 Config Gen Jira | M | pending | |
| S1130.6 /rai-adapter-setup | S | pending | |
