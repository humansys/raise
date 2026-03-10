---
epic_id: "E211"
title: "Adapter Foundation"
status: "complete"
created: "2026-02-23"
---

# Epic Retrospective: E211 Adapter Foundation

**Completed:** 2026-02-23
**Duration:** 2 days (started 2026-02-22)
**Features:** 7 stories delivered (3M + 4S)

---

## Summary

Implemented the open-core adapter foundation defined by ADR-033/034/035/036/037. The codebase now has Protocol contracts for 5 adapter types, entry point registry with `importlib.metadata`, a `FilesystemGraphBackend` extracted from `UnifiedGraph`, `TierContext` for tier detection, and CLI commands for adapter inspection. Any Python package can now extend raise-cli by publishing entry points — PRO adapters become installable plugins, not core modifications.

---

## Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| Stories Delivered | 7 | 3M + 4S |
| Commits | 61 | Including scope, design, plan, impl, reviews |
| Python Files Changed | 55 | 3458 insertions, 348 deletions |
| Tests Added | ~133 | New test functions across all stories |
| Total Tests | 2503 passing | 17 skipped |
| Coverage | 90.26% | Above 90% gate |
| Calendar Days | 2 | 2026-02-22 to 2026-02-23 |

### Story Breakdown

| Story | Title | Size | Velocity | Key Learning |
|-------|-------|:----:|:--------:|--------------|
| S211.0 | GraphNode class hierarchy | M | 2.5x | `__init_subclass__` auto-registration scales cleanly |
| S211.1 | Protocol contracts | S | — | `@runtime_checkable` enables isinstance checks at cost of structural-only matching |
| S211.2 | Entry point registry | S | — | `importlib.metadata.entry_points()` is the stdlib standard; stevedore unnecessary |
| S211.3 | rai memory build → registry | M | — | 9 parser wrappers: uniform pattern, entry points work |
| S211.4 | KnowledgeGraphBackend | M | 1.5x | Full call-site migration is proportional effort |
| S211.5 | TierContext | S | 1.5x | Pydantic BaseModel over dataclass — consistent with project convention |
| S211.6 | rai adapters list/check | S | 1.5x | Pre-implementation arch review saved 3 unnecessary models |

---

## What Went Well

- **Architecture reviews before implementation** (S211.5, S211.6) caught over-engineering before code existed — zero rework cost.
- **Entry point integration worked first try.** 9 governance parsers registered and discovered via `importlib.metadata` without issues.
- **Zero regression on existing 2503 tests.** The refactoring (especially S211.3 parser wrappers and S211.4 backend extraction) was clean.
- **GraphNode `__init_subclass__` pattern** (S211.0) is elegant and extensible — 18 subclasses auto-register without a central registry.
- **Coverage maintained above 90%** throughout all stories.

## What Could Be Improved

- **Entry point install freshness.** Graph backend `local` didn't appear in `rai adapters list` because editable install wasn't refreshed after S211.4 added it to pyproject.toml. Not a code bug, but a developer experience issue.
- **S211.3 was the riskiest story** (9 parsers refactored) — would have benefited from the pre-implementation arch review pattern established in S211.5. Applied retroactively.

## Patterns Discovered

| ID | Pattern | Context |
|----|---------|---------|
| PAT-E-428 | Pre-implementation arch review catches over-engineering at zero cost | S211.5: Beck Rule 4 applied before code exists |
| PAT-E-430 | `entry_points()` returns metadata without loading — use for display, `ep.load()` for validation | S211.6: list vs check commands |

## Process Insights

- **Pre-implementation reviews compound.** The pattern from S211.5 paid off again in S211.6. Establishing it mid-epic was the right call — earlier stories were simpler and didn't need it.
- **S-sized stories on epic branch (skip story branch)** worked well for all 4 S-stories. No branch proliferation, commits still traceable via message prefix.
- **Design → Plan → Implement → Review → Close** full lifecycle even for S-stories kept quality consistent. No shortcuts even when the work was "obvious."

---

## Artifacts

- **Scope:** `work/epics/raise-211-adapter-foundation/scope.md`
- **Stories:** `work/epics/raise-211-adapter-foundation/stories/s211.{0-6}/`
- **ADRs:** ADR-033, ADR-034, ADR-035, ADR-036, ADR-037 (all pre-existing, accepted)
- **New modules:** `adapters/`, `graph/filesystem_backend.py`, `tier/context.py`
- **New CLI:** `rai adapters list`, `rai adapters check`

---

## Next Steps

- **raise-pro (RAISE-208/209):** The adapter foundation enables PRO adapters (JiraAdapter, SupabaseGraphBackend) as installable plugins
- **RAISE-207 (repo separation):** Clean code boundary now exists for open-core split
- **Backlog Abstraction Layer:** `ProjectManagementAdapter` Protocol is ready for concrete implementations

---

*Epic retrospective — 7/7 stories delivered in 2 days, adapter foundation complete*
