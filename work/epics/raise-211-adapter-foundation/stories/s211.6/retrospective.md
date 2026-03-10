---
story_id: "S211.6"
title: "rai adapters list/check"
phase: "review"
created: "2026-02-23"
---

# Retrospective: rai adapters list/check

## Summary
- **Story:** S211.6 (last story in E211)
- **Size:** S
- **Commits:** 4 (scope, impl, check tests, quality fix)
- **Files created:** 2 (`cli/commands/adapters.py`, `output/formatters/adapters.py`)
- **Files modified:** 1 (`cli/main.py`)
- **Tests:** 10 (6 list + 4 check)

## What Went Well

- **Pre-implementation arch review caught over-engineering.** R1 eliminated 3 Pydantic models for display-only data. Q1 placed ADAPTER_GROUPS in its only consumer. Both simplifications were applied before writing any production code — zero rework.
- **Quality review caught UX edge case.** "All 0 adapters passed" would have been confusing. 4-line fix.
- **Clean implementation.** No changes to `registry.py` — command iterates `entry_points()` directly for richer metadata than `_discover()` provides. No private function imports.
- **T1 delivered both commands.** `check` was small enough that it landed in the same task as `list`. T2 became tests-only. Honest about plan deviation instead of pretending T2 was separate impl work.

## What Could Improve

- **Entry point install state assumption.** Graph backend `local` is in pyproject.toml but didn't appear in `rai adapters list` because the editable install wasn't refreshed after S211.4 added it. Test was adjusted to not depend on it. This is a real user-facing issue: after `pip install --upgrade rai-cli`, entry points should always be current. Not a code bug, but worth noting for docs.

## Heutagogical Checkpoint

### What did you learn?
- `entry_points()` returns metadata without loading classes — useful for `list` vs `check` separation. `_discover()` loads eagerly which is more than `list` needs.
- Pre-implementation reviews (arch + quality) compound: arch review saved 3 unnecessary models, quality review caught a display edge case. Both before any code existed.

### What would you change about the process?
- Nothing — S-sized story, lean cycle, two reviews caught real issues. Process was proportional to scope.

### Are there improvements for the framework?
- No framework changes needed. The pre-implementation review pattern (from S211.5 onwards) continues to pay off.

### What are you more capable of now?
- Better at designing CLI commands that consume entry points without coupling to the registry's internal API.

## Action Items
- None. Story is clean. Ready for epic close.
