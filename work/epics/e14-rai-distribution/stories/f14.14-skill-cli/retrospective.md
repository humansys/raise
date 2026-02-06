# Retrospective: F14.14 Skill CLI Commands

## Summary
- **Feature:** F14.14
- **Started:** 2026-02-05
- **Completed:** 2026-02-05 (same day)
- **Estimated:** 5 SP, S/M size, ~15-20 tests
- **Actual:** 79 new tests, 6 new modules, 13 commits

## What Went Well

- **TDD discipline:** Every task followed RED → GREEN → REFACTOR. No untested code.
- **Modular architecture:** Schema → Parser → Locator → Validator → NameChecker → Scaffold — each module cleanly builds on prior work.
- **Inference economy realized:** The CLI commands now do what AI inference was wasting tokens on (listing skills, checking names, validating structure).
- **Clean integration:** `/skill-create` skill now leverages CLI for deterministic operations, reserving inference for judgment calls.
- **Test coverage exceeded:** 79 tests vs 15-20 estimated — comprehensive edge case coverage.

## What Could Improve

- **Plan underestimated test count:** Actual was 4x the estimate. Not a problem, but calibration data point.
- **Pre-existing issues surfaced:** Validation found `epic-start` missing Context section — should be fixed.
- **File naming deviation:** Plan said `naming.py`, implemented as `name_checker.py` — minor but worth noting.

## Heutagogical Checkpoint

### What did you learn?

1. **Rich console corrupts JSON output** — `console.print()` adds ANSI codes that break JSON parsing. Use `print()` for machine-readable output.
2. **Pydantic + pyright strict mode** — `default_factory=list` fails pyright; needs `default_factory=lambda: []` for strict type checking.
3. **Validation as discovery tool** — Running `raise skill validate` across all skills found pre-existing issues (epic-start missing Context).

### What would you change about the process?

1. **Run validation on all skills earlier** — Could have caught the epic-start issue as part of another feature.
2. **Better test count estimation** — Include module tests + CLI tests + edge cases in estimate.

### Are there improvements for the framework?

1. **Fix epic-start skill** — Add missing Context section (logged, separate fix).
2. **Consider naming warnings configurable** — `debug` and `research` are valid utility skill names but trigger warnings.

### What are you more capable of now?

1. **Building composable CLI tooling** — Pattern of module → tests → CLI → formatter is now muscle memory.
2. **Integrating CLI with skills** — Clear boundary: CLI for deterministic, skills for judgment.

## Improvements Applied

- `/skill-create` skill updated to v2.0.0 with CLI integration
- CLI Toolkit section in skill-create now includes `raise skill` commands

## Action Items

- [ ] Fix `epic-start` skill — add missing Context section (low priority, not blocking)
- [ ] Consider adding naming pattern exceptions for utility skills (future)

## Patterns Captured

- PAT-141: Rich console corrupts JSON — use print() for machine output
- PAT-142: Validation as discovery — running validators surfaces pre-existing issues
