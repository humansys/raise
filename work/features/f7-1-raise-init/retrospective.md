# Retrospective: F7.1 `raise init` Command

## Summary

- **Feature:** F7.1
- **Epic:** E7 Onboarding
- **Started:** 2026-02-05
- **Completed:** 2026-02-05
- **Estimated:** ~90 min (1.5h)
- **Actual:** ~40 min
- **Velocity:** 2.3x

## What Went Well

- **TDD cycle worked smoothly** — RED-GREEN-REFACTOR for each module kept quality high
- **F7.8 foundation paid off** — DeveloperProfile module integrated seamlessly
- **Parallel task design** — Tasks 1 & 2 (detection + manifest) were independent, allowing clean implementation
- **--path option** — Using explicit path parameter instead of mocking cwd simplified tests significantly
- **Rich output** — Panel and styled text make Shu experience welcoming

## What Could Improve

- **Test patching complexity** — Initial tests tried to patch at wrong location (init.py instead of profile.py)
- **Ruff auto-fix surprise** — Unused import removal broke tests; should verify tests after ruff fixes
- **Coverage threshold** — Global 90% threshold causes noise when running feature-specific tests

## Heutagogical Checkpoint

### What did you learn?

1. **Path-based CLI testing is cleaner** — Using `--path` parameter instead of mocking `cwd()` is more explicit and less fragile
2. **Module boundaries matter for mocking** — Patch where the function is used, not where it's defined, but the import pattern affects which is which
3. **Ruff removes unused imports silently with --fix** — Always re-run tests after auto-fix

### What would you change about the process?

1. Run tests immediately after `ruff --fix` before assuming they still pass
2. Design CLI commands with explicit path parameters for testability

### Are there improvements for the framework?

1. **Add to guardrails:** "Run tests after ruff --fix to catch import removal breakage"
2. **CLI testing pattern:** Prefer explicit path parameters over cwd mocking

### What are you more capable of now?

- Building complete CLI commands with Typer, Rich output, and Pydantic models
- Integrating multiple modules (detection, manifest, profile) into cohesive command
- Adaptive output based on user experience level (Shu/Ha/Ri)

## Improvements Applied

1. **SHOULD-DEV-002** added to guardrails — Run tests after ruff --fix
2. **SHOULD-CLI-001** added to guardrails — Explicit path parameters for testability

## Patterns to Persist

1. **CLI path parameter pattern** — For testability, use `--path` option instead of relying on `cwd()`
2. **Test after ruff --fix** — Auto-fix can break tests by removing imports

## Action Items

- [x] ~~Consider adding "run tests after ruff fix" to pre-commit workflow~~ → Added SHOULD-DEV-002
- [x] ~~Document CLI testing pattern in guardrails~~ → Added SHOULD-CLI-001

---

*Retrospective completed: 2026-02-05*
