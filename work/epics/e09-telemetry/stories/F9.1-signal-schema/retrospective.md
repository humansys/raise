# Retrospective: F9.1 Signal Schema

## Summary
- **Feature:** F9.1 Signal Schema
- **Epic:** E9 Local Learning
- **Started:** 2026-02-03
- **Completed:** 2026-02-03
- **Estimated:** 25 min
- **Actual:** ~18 min
- **Velocity:** 1.4x (faster than estimated)

## What Went Well

- **ADR-018 as spec:** Having schemas pre-defined in the ADR made implementation trivial — essentially copy-paste with type annotations
- **Test-first thinking:** Writing comprehensive tests (25) caught the discriminated union parsing pattern early
- **Lean planning:** XS feature → 2 tasks was right granularity, didn't over-decompose
- **Quality gates passed first try:** Lint, type check, tests all green on first run (after one ruff fix)

## What Could Improve

- **Initial process skip:** Started coding before being reminded to follow the kata cycle — need to internalize "process first" habit
- **Coverage tool confusion:** `--cov` flag checks entire codebase, not just specified path — caused momentary confusion

## Heutagogical Checkpoint

### What did you learn?

- **Pydantic TypeAdapter:** For parsing discriminated unions from raw dict/JSON, use `TypeAdapter(Signal).validate_python(data)` rather than trying to instantiate Signal directly
- **ruff UP007:** Modern Python prefers `X | Y` over `Union[X, Y]` — ruff enforces this

### What would you change about the process?

- **Nothing major** — the kata cycle (plan → implement → review) worked well for this XS feature
- **Could skip plan for trivial features?** No — even minimal planning (2 tasks, 5 min) provided structure and tracking value

### Are there improvements for the framework?

- **Pattern to capture:** "ADR as spec" — when architecture decisions include detailed schemas, implementation becomes mechanical. This is a good pattern to encourage.
- **Calibration note:** XS features with ADR-specified schemas complete ~1.4x faster than estimated

### What are you more capable of now?

- Telemetry signal schemas are defined and tested
- Foundation for F9.2 (Signal Writer) is ready
- Pattern for discriminated unions in Pydantic is understood

## Improvements Applied

- None needed — process worked well for this feature size

## Action Items

- [x] Update calibration with F9.1 velocity (1.4x for ADR-specified XS)
- [ ] Consider documenting "ADR as spec" pattern in framework

## Acceptance Criteria Verification

- [x] 5 signal types defined as Pydantic models
- [x] Each signal has `type` discriminator field (Literal)
- [x] Each signal has `timestamp` field (datetime)
- [x] Signal union type for type-safe handling
- [x] All models serialize to JSON correctly
- [x] Tests pass with >90% coverage (100% achieved)

---

*Retrospective completed: 2026-02-03*
*Next: F9.2 Signal Writer*
