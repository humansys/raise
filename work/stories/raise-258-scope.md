---
story: RAISE-258
title: Pre-publish verification 2.1.0
size: S
branch: story/standalone/raise-258-pre-publish-verification
base: v2
status: in-progress
---

## Context

Release 2.1.0 includes:
- E250: 27 skills refactored (ADR-040 compliant, ~65% size reduction)
- E248: Lifecycle hooks & workflow gates
- RAISE-136: iter_concepts graceful degradation
- RAISE-256: CI uv sync --extra dev
- /rai-debug v2.1.0
- Breaking changes: memory generate/add-calibration/add-session commands removed
- Migration note: users must run `rai init` to receive updated skills

## In Scope

- **README.md** — verify commands, features, breaking changes, and install
  instructions are accurate for 2.1.0
- **CHANGELOG.md** — verify 2.1.0 entry is complete: new features, breaking
  changes, migration notes
- **CLI surface audit** — verify `rai --help` and all command groups reflect
  current state; check for references to removed commands
- **Smoke check** — manual verification of critical paths that unit tests don't
  cover end-to-end (session start, graph build, skill list)

## Out of Scope

- Website docs (docs/) — post-publish, separate story
- New unit tests (existing suite passes)
- ADR or architecture docs updates
- RAISE-145 ("Unified" prefix rename) — explicitly deferred

## Done When

- [ ] README.md accurate for 2.1.0 — no stale command references
- [ ] CHANGELOG.md has complete 2.1.0 entry with breaking changes + migration notes
- [ ] `rai --help` shows no removed commands
- [ ] Smoke check passes: `rai session start`, `rai graph build`, `rai skill list`
- [ ] Any discovered gaps fixed or explicitly documented as known issues
