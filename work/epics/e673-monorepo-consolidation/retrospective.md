# E673 Retrospective: Monorepo Consolidation

## Summary

- **Epic:** E673 (RAISE-673)
- **Duration:** ~3 weeks (multiple sessions)
- **Stories:** 5 completed (S11.1-S11.5)
- **Commits:** 50 on dev ahead of origin
- **Tests:** 4622 passing, 91% coverage

## Deliverables

1. **Jira migration** — RAISE project with component `rai-agent`, linked to STRAT initiatives (S11.1)
2. **uv workspace monorepo** — 5 packages (raise-core, raise-cli, raise-pro, raise-server, rai-agent) with single lockfile (S11.2, S11.3)
3. **Selective CI/CD** — reusable workflow + per-package callers with native path filters, per-package release tags (S11.4/RAISE-676)
4. **Distribution packaging** — multi-stage Dockerfile (Node + Python + Claude Code CLI), docker-compose, .env.example with 6 auth scenarios (S11.5/RAISE-677)

## Metrics

| Story | Jira | Estimated | Actual | Velocity |
|-------|------|-----------|--------|----------|
| S11.4 | RAISE-676 | 30 min | 25 min | 1.2x |
| S11.5 | RAISE-677 | 35 min | 60 min | 0.58x |

S11.5 underestimated due to two design pivots on auth model (assumed API key, discovered SubprocessCLITransport).

## What Went Well

- **uv workspaces** proved solid — single lockfile, cross-package deps resolved cleanly
- **Reusable workflow pattern** scales well for monorepo CI (PAT-E-706)
- **AR before implementation** caught design questions early (Q1-Q3 in S11.4)
- **Docker build verified** end-to-end in session — not deferred to CI
- **Scope discipline** — removed 3 stories (RAISE-678, 701, 702) that didn't belong

## What To Improve

- **Verify SDK internals before designing** — the claude-agent-sdk transport assumption cost 2 pivots and ~25 min
- **Numbering mismatch** (S11.3 vs S11.4 between repos) caused confusion. Next time, use Jira keys as canonical IDs from the start
- **pyproject.toml workspace references** break Docker builds and GitHub mirrors — same pattern needed in two places (sync-github.sh, Dockerfile). Consider a shared script or build-time patch

## Patterns Added

| ID | Pattern |
|----|---------|
| PAT-E-706 | uv workspace CI/CD: native GHA path filters + reusable workflow |
| PAT-E-707 | Infrastructure stories use structural verification, not TDD |
| PAT-E-708 | claude-agent-sdk spawns claude binary — Docker needs Node.js |
| PAT-E-709 | Monorepo Docker must patch pyproject.toml for excluded packages |

## Decisions Deferred

- **D2:** rai-agent OSS vs proprietary — affects GitHub mirror, GHCR publishing
- **OSS MVP definition** — needs `/rai-problem-shape` before GHCR/deploy epics
- **Product vision** — Google Chat, Onboarding Wizard, Plane adapter, One-click deploy (captured in parking lot)

## Scope Changes

- RAISE-678 (Personal Instance Cleanup) → moved to rai personal repo
- RAISE-701 (GHCR) → promoted from story to independent Epic
- RAISE-702 (One-click deploy) → promoted from story to independent Epic
