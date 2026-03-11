# Epic Retrospective: E478 Pro/Community Boundary

**Completed:** 2026-03-11
**Duration:** 1 day (started 2026-03-11)
**Stories:** 3 stories delivered

---

## Summary

Established a clean boundary between the open-source `raise-cli` package and the proprietary `raise-pro` package. Moved all Jira/Confluence adapter code, entry points, and dependencies out of the community package into a new `packages/raise-pro/` workspace package. Removed 207 lines of hardcoded Jira-specific CLI logic.

## Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| Stories Delivered | 3 | S478.1, S478.2, S478.3 |
| Commits | 25 | Across all 3 stories |
| Lines Removed (net) | ~500 | From raise_cli (moved or deleted) |
| Tests | 3709 passing | 6 Jira-specific tests removed, net -6 |
| Dependencies Removed | 6 | atlassian-python-api, authlib, cryptography, requests, urllib3, certifi |
| Calendar Time | 1 session | |

### Story Breakdown

| Story | Size | Velocity | Key Learning |
|-------|:----:|:--------:|--------------|
| S478.1 — Move pro adapters | S | 1.2x | Entry point updates can't be deferred when discovery tests exist |
| S478.2 — Clean entry points & deps | S | 0.86x | Hatch doesn't support out-of-tree relative paths |
| S478.3 — Clean CLI logic | XS | 1.25x | Grep docs/ for stale references when removing CLI commands |

## What Went Well

- **Clean separation achieved in one session** — all 3 stories planned, implemented, reviewed, and merged
- **AR caught real bugs** — stale entry point (S478.1) and missing sdist include would have broken runtime
- **QR caught stale docs** — `adapter.mdx` still referenced removed command
- **Design fallbacks worked** — S478.2 design predicted hatch path limitation and had a pre-planned fallback
- **TDD and gates prevented regressions** — 3709 tests green throughout

## What Could Be Improved

- **S478.1 scope creep** — entry point updates were originally S478.2 scope but had to happen in S478.1 because entry point discovery tests required it. Plan should have anticipated this coupling.
- **Remaining Jira references in raise_cli** — config-driven references (backlog hook, doctor checks, onboarding) still exist. Deferred intentionally but should be tracked.
- **No sdist config for raise-pro** — AR flagged this as Q1. Needed before publishing raise-pro to PyPI.

## Patterns Discovered

| ID | Pattern | Context |
|----|---------|---------|
| PAT-E-004 | Entry point discovery tests force updating entry points in the same story as code moves | workspace, entry-points, packaging |
| PAT-E-005 | Hatch wheel config requires source code inside the package directory | hatch, workspace, packaging |
| PAT-E-006 | When removing CLI commands, grep docs/ for stale references | docs, cli, removal |

## Process Insights

- **Small epics (S appetite) work well as single-session deliveries** — the 3-story sequence was tight enough to maintain full context
- **AR/QR gates add real value even for "simple" moves** — both caught issues that automated gates (tests, types, lint) missed
- **Design fallbacks save time** — pre-thinking "what if X doesn't work" in the design doc converted a potential blocker into a 5-minute pivot

## Artifacts

- **Scope:** `work/epics/e478-pro-boundary/scope.md`
- **Stories:** `work/epics/e478-pro-boundary/stories/` (9 artifacts across 3 stories)
- **Package:** `packages/raise-pro/pyproject.toml` (new workspace package)
- **Config:** `.gitignore` (jira.yaml, confluence.yaml now excluded)

## Next Steps

- Track remaining Jira references in raise_cli (backlog hook, doctor, onboarding) — future cleanup story
- Add sdist config to raise-pro before first PyPI publish
- Verify `pip install raise-cli` in a clean venv (manual smoke test)
