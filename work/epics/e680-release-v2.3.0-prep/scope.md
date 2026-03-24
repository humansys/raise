---
epic_id: "E680"
jira_key: "RAISE-680"
title: "Release v2.3.0 Prep"
status: "in-progress"
created: "2026-03-23"
fix_version: "2.3.0"
---

# E680: Release v2.3.0 Prep

## Objective

Prepare v2.3.0 for release with complete documentation, changelog, and verification. Capture the process for future standardization.

## Context

v2.3.0 consolidates what was originally v2.2.4 (bugfixes) + significant feature work:
- 3 completed epics: E478 (Pro/Community), E494 (ACLI Adapter), E654 (Session Identity)
- 12+ bugfixes, 3 security patches
- ~200 commits since v2.2.3
- Release date: 2026-03-30

## Stories

| ID | Story | Size | Status |
|----|-------|------|--------|
| S680.1 | Epic documentation — `/rai-epic-docs` for E478, E494, E654 | M | pending |
| S680.2 | CHANGELOG & release notes | S | pending |
| S680.3 | Dev & user docs update in `/docs` | S | pending |
| S680.4 | Verification & smoke test | S | pending |
| S680.5 | Release publish — `/rai-publish` minor | XS | pending |

## Dependencies

- S680.1 before S680.2 (epic docs inform changelog)
- S680.2, S680.3 before S680.5 (docs complete before publish)
- S680.4 can run in parallel with S680.2/S680.3

## Done Criteria

- [ ] All 3 epics documented in Confluence
- [ ] CHANGELOG.md complete for v2.3.0
- [ ] `/docs` updated for breaking/new features
- [ ] Test suite passes, session roundtrip verified
- [ ] v2.3.0 published to PyPI
- [ ] Retrospective captures release prep patterns

## Hypothesis: Release Prep by Type

To validate in retro:

| Step | Patch (2.x.Y) | Minor (2.X.0) | Major (X.0.0) |
|------|:---:|:---:|:---:|
| Scope audit (Jira vs git) | auto | auto | auto |
| `/rai-epic-docs` per epic | skip | run | run |
| CHANGELOG | auto-generate | review + edit | review + edit |
| Update user docs | conditional | run | run |
| Update dev docs | skip | conditional | run |
| Breaking changes review | skip | check | deep review |
| Session/smoke test | quick | full | full |
| `/rai-publish` | run | run | run + announcement |
