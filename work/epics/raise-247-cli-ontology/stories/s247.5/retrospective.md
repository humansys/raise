# Retrospective: S247.5 — Merge publish+release, flatten singletons

## Summary
- **Story:** S247.5 (RAISE-254)
- **Size:** S
- **Started:** 2026-02-23 12:46
- **Completed:** 2026-02-23 13:15
- **Estimated:** 60 min (S baseline)
- **Actual:** ~29 min
- **Velocity:** 2.07x

## What Went Well
- Arch review + test muda analysis before implementation identified 6 muda tests in advance — no surprises during implementation
- The merge pattern (different from S1-S3 extract pattern) was smoother than expected — the deprecation shim infrastructure was already proven
- Quality review caught a real redundancy (double `invoke_without_command`) — worth the extra pass
- Deleting `tests/publish/test_cli.py` entirely (6 tests) per PAT-E-444 was the right call — domain tests in `test_check.py`/`test_version.py` cover the logic

## What Could Improve
- The RED test for T1 (`test_publish_requires_bump_or_version`) initially passed because Typer returns exit code != 0 for unknown subcommands — needed to add a more specific assertion. This is a recurring gotcha with Typer CLI tests.

## Heutagogical Checkpoint

### What did you learn?
- Typer's `invoke_without_command=True` can be declared in either the constructor or the callback — declaring in both is redundant. The callback declaration is the one that matters.
- Pre-implementation arch review + test muda analysis is a good combo — the muda findings naturally integrate into implementation tasks rather than creating separate cleanup work.

### What would you change about the process?
- The arch review + quality review combo worked well for this story. Consider making the pre-implementation arch review standard for stories that touch test files (where muda is most common).

### Are there improvements for the framework?
- No framework changes needed. PAT-E-444 (no tests for CLI plumbing) continues to apply well.

### What are you more capable of now?
- The merge pattern (two source files → one target + shim) is now proven alongside the extract pattern (S1-S3). S247.6 can reference both patterns.

## Patterns

### New
- **PAT-E-445:** Typer RED test gotcha: `exit_code != 0` passes for both "command doesn't exist" and "command validation error". Always add content assertions (check output message) alongside exit code checks.
- **PAT-E-446:** Pre-implementation arch review + test muda analysis: run together, integrate muda cleanup into implementation tasks. Avoids separate cleanup stories and catches waste before it's written.

### Reinforced
- PAT-E-444: Coverage Goodhart — applied (deleted 7 muda tests total)
- PAT-E-187: Code as Gemba — applied (read all source files before design)
- PAT-E-186: Design not optional — applied (full design cycle)

## Improvements Applied
- None needed — process worked smoothly

## Action Items
- None
