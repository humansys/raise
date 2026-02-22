---
story_id: "S211.2"
title: "Entry point registry"
status: "complete"
created: "2026-02-22"
---

# Retrospective: Entry point registry

## Summary
- **Story:** S211.2
- **Size:** S (3 tasks)
- **Commits:** 3 (scope + T1 + T2)
- **New production code:** 63 lines (`registry.py`)
- **New tests:** 20 (15 registry + 5 init updates)
- **Total tests after:** 2427 passed, 90.20% coverage
- **Regressions:** 0

## What Went Well
- **ADR validation at gemba:** Design decisions from ADR-033/034 held up under implementation. `dict[str, type]` was correct — registry discovers, consumer instantiates.
- **DRY internal `_discover()`:** Single error handling path, 5 one-liner public functions. Clean separation.
- **PAT-E-241 caught proactively:** Predicted the `__all__` count breakage in design phase, addressed in T2 RED before it could surprise.
- **TDD flow clean:** RED→GREEN on both tasks with zero rework. Mock strategy for `importlib.metadata` was straightforward.
- **pyright strict passed first try:** The `type: ignore[assignment]` on `ep.load()` was the only escape hatch, and it's at the boundary where `Any` enters our typed world.

## What Could Improve
- Nothing significant for an S story. Process was proportional to complexity.

## Heutagogical Checkpoint

### What did you learn?
- `importlib.metadata.entry_points(group=...)` returns an iterable directly filterable by group (Python 3.12+). No need for the old `select()` pattern.
- Questioning ADR decisions at gemba (not just accepting them) builds confidence in the implementation. We confirmed `dict[str, type]` vs alternatives by reasoning about real consumers (S211.3, S211.4, S211.6).

### What would you change about the process?
- Nothing. Full lifecycle (start→design→plan→implement→review) for an S story took one session. Proportional.

### Are there improvements for the framework?
- None identified.

### What are you more capable of now?
- Entry point discovery pattern is now a known tool for future extensibility work. Same pattern applies to any plugin architecture in Python.

## Patterns Reinforced
- **PAT-E-186** (design not optional): Design conversation surfaced the cache and return-type decisions before code.
- **PAT-E-183** (grounding over speed): Gemba walk on ADRs + existing code before designing.
- **PAT-E-187** (code as gemba): Read actual `__init__.py`, `protocols.py`, `pyproject.toml` before designing.
- **PAT-E-241** (registry changes break downstream): Predicted and addressed `__all__` count change.

## Action Items
- None — clean story, no technical debt introduced.
