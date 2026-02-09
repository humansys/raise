# Retrospective: S16.2 Graph Diff Engine

## Summary
- **Story:** S16.2 Graph Diff Engine
- **Size:** M
- **Started:** 2026-02-09
- **Completed:** 2026-02-09
- **Tasks:** 5 (1M + 3S + 1XS)
- **Tests:** 39 (29 unit + 5 integration + 5 CLI)
- **Coverage:** 98% on diff.py

## What Went Well

- **Deliberate design paid off.** 8 explicit decision points before writing code. Every design choice was agreed upfront — zero rework during implementation.
- **Simplification cascade.** Dropping edge tracking (Decision 5.5) eliminated ~40% of planned complexity with no loss of consumer value. The diff model went from 4 classes to 2.
- **Impact classification simplified.** Three levels (none/module/architectural) instead of four. The consumer (`/docs-update`) doesn't need the diff to pre-classify granularity — it reads `changed_fields` directly.
- **TDD was smooth.** Tests first, implementation straightforward. 29 unit tests covered every code path before integration tests even ran.
- **Real-world validation.** Integration tests against actual 345-node graph caught nothing — the unit tests already covered it. But the manual `raise memory build` run showed the diff working on real changes (3 added nodes + 1 modified module from our own work).

## What Could Improve

- **pyproject.toml coverage config.** The `--cov-fail-under=90` is project-wide but we run per-module tests. Every test run shows a misleading "FAIL" for global coverage. Not a blocker but noisy.
- **Pre-existing pyright errors in memory.py.** 17 errors, all pre-existing. They don't block but they're tech debt that makes it harder to verify new code is clean.

## Heutagogical Checkpoint

### What did you learn?
- Deliberate design conversations (with HITL at each decision) produce better architecture than designing in isolation. The "do we even need edge tracking?" question only emerged because we were going slow.
- `dict` comparison in Python works correctly for Pydantic metadata — no key ordering issues. The feared "metadata comparison noise" risk didn't materialize.

### What would you change about the process?
- Nothing significant. The deliberate pace was right for an M-sized foundational story. The 8-decision design phase took ~15 minutes of conversation but saved implementation time.

### Are there improvements for the framework?
- Consider adding a `--cov-module` pattern to the test runner to avoid the misleading global coverage failure.

### What are you more capable of now?
- Graph diffing infrastructure is in place. S16.3 can consume `last-diff.json` directly. The models are clean and serialize/deserialize correctly.

## Design Decisions Made (8)

| # | Decision | Choice |
|---|----------|--------|
| 1 | Module placement | `context/diff.py` — graph operation lives with graph |
| 2 | Comparison fields | content, type, metadata only |
| 3 | Old graph source | Load existing index.json before overwriting |
| 4 | Impact levels | Three: none / module / architectural |
| 5 | Edge tracking | Skipped entirely |
| 6 | Summary | Deterministic template |
| 7 | Diff persistence | `.raise/rai/personal/last-diff.json` |
| 8 | Default behavior | Diff on by default, `--no-diff` to skip |

## Improvements Applied
- None to framework (no process issues found)

## Patterns Worth Persisting
- Deliberate design with HITL at each decision point produces better M-sized story outcomes than designing in isolation
- Dropping edge tracking for graph diff: edges are derived from nodes in rebuild-from-scratch architectures, so node diff captures all signal
