---
epic_id: "E680"
jira_key: "RAISE-680"
title: "Release v2.3.0 Prep"
status: "in-progress"
created: "2026-03-23"
fix_version: "2.3.0"
release_date: "2026-03-30"
---

# E680: Release v2.3.0 Prep

## Objective

Ship v2.3.0 as the last pre-monorepo release, covering the 7 dimensions that differentiate a reliable release from an ad-hoc one: scope audit, changelog, documentation, security audit, test verification, release mechanics, and communication.

## Value

- Users get 3 epics + 12 bugfixes + 3 security patches that have been sitting on dev
- Team establishes release prep as leader standard work (repeatable process)
- Clean cut point before monorepo migration (v2.3.0 = last single-package release)

## Context

v2.3.0 consolidates what was originally v2.2.4 (bugfixes) + significant feature work:
- 3 completed epics: E478 (Pro/Community), E494 (ACLI Adapter), E654 (Session Identity)
- 12+ bugfixes, 3 security patches, ~200 commits since v2.2.3
- 36 Jira tickets tagged to v2.3.0 (scope audit done 2026-03-23)
- Release date: 2026-03-30
- 3 tickets still open (RAISE-539, 634, 213) — all assigned to Fernando, documented as known issues

## Research Input

`work/research/release-prep-best-practices/release-prep-report.md` — 13 sources, 7 claims triangulated.
Key finding: a proper release covers 7 dimensions (scope audit, changelog, documentation, security, verification, mechanics, communication).

## Scope Boundaries

### In (MUST)
- Dimensions 1-6: scope audit (done), changelog, epic docs, security verify, test verification, publish
- CHANGELOG.md in Keep a Changelog format
- `/rai-epic-docs` for E478, E494, E654
- Full test suite + session roundtrip verification
- `rai gate check --all` + `rai skill validate` + dependency audit

### In (SHOULD)
- Dimension 7: release communication (GitHub release notes, Confluence announcement)
- User/dev docs update in `/docs` for ACLI adapter, session identity, CLI extensions

### Out of Scope
- Building `/rai-release-prep` skill (retro output, not this epic)
- Fixing open bugs (RAISE-539, 634, 213) — Fernando's, documented as known issues
- Redesigning docs site (RAISE-634)
- Monorepo migration (separate epic, after this release)

## Stories

| ID | Jira | Story | Description | Size | Status |
|----|------|-------|-------------|:----:|--------|
| S680.1 | RAISE-683 | Epic documentation | `/rai-epic-docs` for E478, E494, E654 → Confluence | M | pending |
| S680.2 | RAISE-686 | Changelog & release notes | CHANGELOG.md (Keep a Changelog) + GitHub release notes | S | done |
| S680.3 | RAISE-684 | User & dev docs | Update `/docs` — ACLI migration, session identity, CLI extensions | S | pending |
| S680.4 | RAISE-682 | Quality gates & security | `rai gate check --all`, `rai skill validate`, dep scan, full test suite | S | pending |
| S680.5 | RAISE-685 | Smoke test & verification | Session roundtrip, ACLI integration smoke, clean install test | S | done |
| S680.6 | RAISE-687 | Release publish & announce | `/rai-publish` minor + GitHub release + Confluence release notes | XS | pending |

## Dependencies

```
S680.1 ──→ S680.2 ──→ S680.6
S680.3 ──────────────→ S680.6
S680.4 ──→ S680.5 ──→ S680.6
```

- S680.1 before S680.2 (epic docs inform changelog content)
- S680.4 before S680.5 (gates pass before smoke test)
- S680.2 + S680.3 + S680.5 before S680.6 (all prep done before publish)
- S680.1 and S680.3 and S680.4 can run in parallel (independent)

## Done Criteria

- [ ] 3 Confluence pages published (E478, E494, E654 epic docs)
- [ ] CHANGELOG.md with v2.3.0 entry in Keep a Changelog format
- [ ] `/docs` updated for ACLI adapter and session identity
- [ ] `rai gate check --all` passes
- [ ] 0 open CVEs in dependencies
- [ ] Test suite 100% pass
- [ ] Session start/close roundtrip verified from main repo (not worktree)
- [ ] v2.3.0 published on PyPI
- [ ] GitHub release with release notes
- [ ] Retrospective captures release prep patterns for future skill

## Risks

| Risk | L | I | Mitigation |
|------|:-:|:-:|------------|
| Epic artifacts incomplete for `/rai-epic-docs` | M | M | Use git log + retrospectives as alternative input |
| Open bugs (539, 634, 213) affect release perception | L | L | Document as "known issues" in release notes |
| Monorepo pressure creates urgency to skip steps | M | H | Release date is firm (Mar 30) — don't compress, cut scope |

## Hypothesis: Release Prep by Type

To validate in retro — does this matrix hold?

| Dimension | Patch (2.x.Y) | Minor (2.X.0) | Major (X.0.0) |
|-----------|:---:|:---:|:---:|
| 1. Scope audit (Jira ↔ git) | auto | auto | auto |
| 2. Changelog (Keep a Changelog) | required | required | required |
| 3. Epic docs (`/rai-epic-docs`) | skip | run per epic | run per epic |
| 4. User/dev docs (`/docs`) | conditional | run | run + migration guide |
| 5. Security audit (dep scan) | verify clean | verify clean | full audit |
| 6. Quality gates (test + lint + type) | unit + smoke | full suite + integration | full + install test |
| 7. Release mechanics | PyPI direct | PyPI direct | TestPyPI → PyPI |
| 8. Communication | changelog only | release notes | blog post + migration guide |
| RaiSE: skill validate | skip | run | run |
| RaiSE: graph build | skip | run | run |
| RaiSE: gate check --all | run | run | run |

---

## Implementation Plan

### Sequencing Strategy

**Quick wins + dependency-driven.** No technical uncertainty (all code exists), optimize for throughput and critical path.

### Execution Order

| # | Story | Stream | Rationale | Enables |
|:-:|-------|:------:|-----------|---------|
| 1 | S680.4 Quality gates & security | C | Quick win — automated, fast feedback. If gates fail, everything else is moot. | S680.5 |
| 2 | S680.1 Epic documentation | A | Critical path (M size). Start early, runs in parallel with S680.4. | S680.2 |
| 3 | S680.3 User & dev docs | B | Independent. Parallel with S680.1. | S680.6 |
| 4 | S680.5 Smoke test & verification | C | Depends on S680.4. Run after gates pass. | S680.6 |
| 5 | S680.2 Changelog & release notes | A | Depends on S680.1 (epic docs inform content). | S680.6 |
| 6 | S680.6 Release publish & announce | — | Final gate. All prep done. | Done |

### Parallel Streams

```
         Day 1-2                    Day 3-4              Day 5
Stream A: ████ S680.1 (M) ████ → ██ S680.2 (S) ██ ─┐
Stream B: ██ S680.3 (S) ██ ─────────────────────────┤→ S680.6 (XS)
Stream C: █ S680.4 (S) █ → ██ S680.5 (S) ██ ───────┘
```

- Stream A is the critical path (S680.1 at M is the largest story)
- Stream C starts first (S680.4 is fast, automated)
- Stream B runs independently, finishes early

### Milestones

#### M1: Docs Complete (target: Day 3)
- [ ] S680.1: 3 Confluence pages published (E478, E494, E654)
- [ ] S680.3: `/docs` updated for ACLI adapter, session identity, CLI extensions
- [ ] S680.2: CHANGELOG.md v2.3.0 entry written

**Demo:** Show Confluence pages + CHANGELOG diff.

#### M2: Release Ready (target: Day 4)
- [ ] S680.4: `rai gate check --all` passes, 0 CVEs, full test suite green
- [ ] S680.5: Session roundtrip verified, ACLI smoke test passes

**Demo:** Gate output + smoke test evidence.

#### M3: Released (target: Day 5 — 2026-03-30)
- [ ] S680.6: v2.3.0 on PyPI, GitHub release with notes
- [ ] Retrospective captured

**Demo:** `pip install raise-cli==2.3.0` works.

### Progress Tracking

| Story | Jira | Size | Status | Started | Completed | Notes |
|-------|------|:----:|--------|---------|-----------|-------|
| S680.4 | RAISE-682 | S | pending | | | gates + security |
| S680.1 | RAISE-683 | M | pending | | | epic docs (critical path) |
| S680.3 | RAISE-684 | S | pending | | | user/dev docs |
| S680.5 | RAISE-685 | S | done | 2026-03-23 | 2026-03-23 | smoke tests — 6/6 PASS |
| S680.2 | RAISE-686 | S | done | 2026-03-23 | 2026-03-23 | changelog |
| S680.6 | RAISE-687 | XS | pending | | | publish |

### Sequencing Risks

| Risk | Mitigation |
|------|------------|
| S680.1 takes longer than 2 days (artifact gaps) | Use git log + retros as fallback. Reduce doc depth for E478 (simplest epic). |
| S680.4 finds failing gates | Fix before proceeding — this is the point of running gates first. |
| Fernando's bugs not closed by Day 5 | Already planned: document as known issues. Don't block release. |
