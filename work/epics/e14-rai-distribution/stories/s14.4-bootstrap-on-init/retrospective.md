# Retrospective: S14.4 Bootstrap on Init

## Summary
- **Story:** S14.4 Bootstrap on Init
- **Epic:** E14 Rai Distribution
- **Size:** M (3 SP)
- **Commits:** 3 (scope, tasks 1-2, task 3)
- **Tests added:** 25 (14 bootstrap + 6 path + 5 init integration)

## What Went Well
- Design phase caught 5 integration decisions that would have caused rework
- `importlib.resources.abc.Traversable` provides clean type-safe API
- Per-file idempotency was simple to implement and test
- Parallel task execution (1+2) saved time
- Existing test patterns in `test_init.py` made integration testing straightforward

## What Could Improve
- Initially skipped design for M-sized story — user correctly challenged this
- First `Traversable` import from deprecated `importlib.abc` caught by deprecation warning in tests

## Heutagogical Checkpoint

### What did you learn?
- `importlib.abc.Traversable` is deprecated in Python 3.14; use `importlib.resources.abc.Traversable`
- Design gate matters even for seemingly clear M-sized stories — integration points are where complexity hides
- `TYPE_CHECKING` guard + `from __future__ import annotations` enables lazy imports with proper type hints

### What would you change about the process?
- Always design M+ stories, no shortcuts. The user was right to challenge.

### Are there improvements for the framework?
- Consider making design mandatory for M+ in `/story-start` skill (currently says "optional for S/XS")

### What are you more capable of now?
- `importlib.resources` API for bundled package files
- Bootstrap/distribution patterns for Python packages

## Patterns Learned
- **PAT-154:** Design gate for M+ stories catches integration decisions early — saves rework
- **PAT-155:** `importlib.resources.abc.Traversable` (not `importlib.abc`) for Python 3.14+ compatibility
