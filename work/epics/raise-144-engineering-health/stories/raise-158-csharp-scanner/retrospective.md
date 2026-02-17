# Retrospective: RAISE-158 C#/.NET Discovery Scanner

## Summary
- **Story:** RAISE-158
- **Size:** S
- **Commits:** 4 (scope, extractor, CLI wiring, exclude fix)
- **Tests:** 13 new, 90 total passing
- **Files changed:** scanner.py, discover.py, test_scanner.py, pyproject.toml

## What Went Well
- PHP scanner as template made implementation fast — pattern is well-established
- AST inspection before writing tests (PAT-E-232) confirmed all node types upfront, zero surprises
- TDD caught nothing broken — clean RED→GREEN→REFACTOR cycle
- All MUST and SHOULD acceptance criteria met (visibility modifiers, inheritance in signatures)

## What Could Improve
- Integration test (Task 3) revealed a bug that unit tests didn't catch: CLI had hardcoded exclude patterns diverging from `DEFAULT_EXCLUDE_PATTERNS`. The manual integration test earned its keep.

## Heutagogical Checkpoint

### What did you learn?
- CLI `discover.py` had a stale copy of exclude patterns — classic drift between two sources of truth. The fix was to delegate to `None` and let `scan_directory` use its own defaults.
- `PurePath.match("**/*.X.cs")` works in Python 3.12 but `"*.X.cs"` is simpler and equally correct for filename-level patterns.

### What would you change about the process?
- Nothing significant — the 3-task decomposition was right-sized for an S story following an established pattern.

### Are there improvements for the framework?
- The CLI exclude pattern drift is a general pattern: when CLI and library have overlapping defaults, the CLI should delegate rather than duplicate. Worth a poka-yoke or lint.

### What are you more capable of now?
- Adding new language scanners is now fully routine — PHP, Svelte, C# all follow the same pattern. Next scanner (Flutter/Dart) should be even faster.

## Bug Found During Integration
- **CLI exclude patterns drift:** `discover.py` hardcoded its own exclude list, missing `*.blade.php` and `*.Designer.cs`. Fixed by delegating to `DEFAULT_EXCLUDE_PATTERNS` (single source of truth).
- **Impact:** Also fixed pre-existing blade.php exclusion bug in CLI path.

## Patterns to Persist
1. CLI should delegate defaults to library, not duplicate them (single source of truth)
2. Manual integration tests catch drift between layers that unit tests miss
