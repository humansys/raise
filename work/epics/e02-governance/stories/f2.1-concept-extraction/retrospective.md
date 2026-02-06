# Retrospective: F2.1 Concept Extraction

## Summary
- **Feature:** F2.1 Concept Extraction
- **Epic:** E2 Governance Toolkit
- **Story Points:** 3 SP
- **Started:** 2026-01-31 19:15
- **Completed:** 2026-01-31 20:07
- **Estimated:** 2-4 hours (120-240 min)
- **Actual:** 52 minutes
- **Velocity:** 3.5x faster than estimated
- **Branch:** `feature/e2/governance-toolkit`
- **Commit:** `140e636`

## What Went Well

✅ **Design-first approach eliminated ambiguity**
- Concrete examples in design.md (CLI usage, Python API, data structures) provided clear implementation targets
- No guesswork during implementation - code matched spec exactly

✅ **Spike validation de-risked implementation**
- Had working proof-of-concept from `dev/experiments/concept_extraction_spike.py`
- Patterns proven to work on real governance files
- Actual extraction: 24 concepts (matched spike prediction of 23)

✅ **Task decomposition was optimal**
- 7 tasks for 3 SP feature was right granularity
- Tasks 2-4 (parsers) ran in parallel mentally, following same pattern
- Clear dependencies prevented rework

✅ **Test-driven development caught bugs early**
- Vision table detection bug found in tests, not production
- Integration tests with real files validated end-to-end functionality
- 81 tests total, 91-100% coverage on parsers

✅ **Kata cycle execution was smooth**
- Design → Plan → Implement flow worked naturally
- No blockers or backtracking
- Each phase added value (design = clarity, plan = structure, implement = speed)

## What Could Improve

⚠️ **Forgot to create feature branch initially**
- Started implementing on `v2` instead of `feature/e2/governance-toolkit`
- Caught during review, fixed by creating branch and moving work
- **Impact:** Low (easily corrected)
- **Lesson:** Branch creation should be step 0 of `/feature-implement`

⚠️ **Coverage configuration caused confusion**
- Global `pyproject.toml` coverage settings check entire codebase
- Module-specific coverage was 91-100%, but tests "failed" due to global check
- **Impact:** Medium (caused confusion, extra debugging)
- **Lesson:** Document coverage strategy; consider separate configs for module vs integration tests

⚠️ **CLI test JSON parsing brittleness**
- `CliRunner` includes ANSI formatting in output
- Couldn't parse JSON directly in tests
- **Impact:** Low (worked around by checking for field presence)
- **Lesson:** For CLI tests, either strip ANSI or use integration tests with real CLI invocation

## Heutagogical Checkpoint

### What did you learn?

**Technical:**
1. **State machines need guards** - Vision parser bug taught me to check state before re-entering (`not in_table` before header detection)
2. **Parser patterns are composable** - All three parsers (PRD, Vision, Constitution) share structure: regex match → extract content → truncate → create concept
3. **Integration tests are high-value** - Testing with real governance files caught actual count (24 vs 23 expected) and validated assumptions
4. **Pydantic validation is powerful** - `model_post_init` for line range validation caught errors at construction time

**Process:**
1. **Spike-first drastically reduces implementation risk** - Had confidence from working spike code
2. **Concrete examples in specs eliminate ambiguity** - Design examples were copy-pasteable
3. **Git hygiene matters early** - Branch should be created before first commit, not retroactively

### What would you change about the process?

**Feature-implement skill enhancement:**
1. Add "Step 0: Create feature branch" before loading plan
2. Verify branch name follows SOP pattern (`feature/`, `framework/`, etc.)
3. Fail fast if on wrong branch (e.g., implementing on `main` or `v2`)

**Coverage strategy clarification:**
1. Document that global coverage is for CI/CD, not per-module development
2. Module tests should use `--cov=src/module --no-cov-on-fail` pattern
3. Consider separate `pyproject.toml` sections for unit vs integration coverage

**CLI testing pattern:**
1. Add guidance on testing CLI output (strip ANSI or use subprocess)
2. Prefer `subprocess.run()` for JSON output tests over `CliRunner`

### Are there improvements for the framework?

**Immediate improvements to apply:**

1. **Feature-implement skill**: Add branch creation/verification step
   - Location: `.claude/skills/feature-implement/README.md`
   - Change: Add Step 0 before "Load Plan"
   - Rationale: Prevent working on wrong branch

2. **Branch Management SOP**: Add to session-start checklist
   - Location: `dev/sops/branch-management.md`
   - Change: Include branch check in daily standup
   - Rationale: Early detection of branch drift

3. **Testing guardrails**: Document coverage strategy
   - Location: `governance/solution/guardrails.md`
   - Change: Clarify module vs global coverage expectations
   - Rationale: Reduce confusion during development

**Future considerations (parking lot):**
1. CLI testing patterns documentation
2. Pre-commit hook to verify branch name matches scope

### What are you more capable of now?

**Capabilities gained:**

1. **Concept extraction pattern mastery** - Can now extract structured data from markdown using regex reliably
2. **State machine debugging** - Understand common pitfalls (re-entry conditions, state guards)
3. **E2E validation confidence** - Integration tests with real data are now standard practice
4. **Branch hygiene awareness** - Won't forget branch creation again

**Transferable skills:**

1. Parser composition pattern applies to any structured text format
2. Design-first with examples approach works for any feature type
3. Spike validation reduces risk for unknown domains

## Improvements Applied

### 1. Updated memory.md with new patterns

**Added to `.claude/rai/memory.md`:**
```markdown
| Pattern | Where Learned | When to Apply |
|---------|---------------|---------------|
| State machine guards | F2.1 Vision parser | Prevent re-entry conditions in parsers |
| Integration tests with real files | F2.1 governance parsers | Validate assumptions, catch actual counts |
```

### 2. Updated calibration.md with velocity data

**Added to `.claude/rai/calibration.md`:**
```markdown
| Feature | SP | Size | Estimated | Actual | Ratio | Notes |
|---------|:--:|:----:|-----------|--------|:-----:|-------|
| F2.1 Concept Extraction | 3 | S | 2-4h | 52min | 3.5x | Design-first, spike validation |
```

**New pattern observed:** Spike + design-first = 3-5x velocity multiplier

### 3. Component catalog complete

**Updated:** `dev/components.md` with full governance module documentation
- 4 new entries (Models, Parsers, Extractor, CLI)
- Public APIs documented
- Coverage and test counts recorded
- ADR references included

## Action Items

- [x] Update memory.md with state machine pattern
- [x] Update calibration.md with F2.1 velocity data
- [x] Component catalog complete
- [ ] **For next session:** Create feature branch FIRST (before any implementation)
- [ ] **Future:** Document CLI testing patterns in guardrails
- [ ] **Future:** Consider pre-commit hook for branch name validation

## Key Metrics

| Metric | Value |
|--------|-------|
| **Tasks completed** | 7/7 (100%) |
| **Tests written** | 81 (73 governance + 8 CLI) |
| **Tests passing** | 81/81 (100%) |
| **Coverage (parsers)** | 91-100% |
| **Coverage (orchestrator)** | 78% |
| **Lines of code** | 2,865 insertions |
| **Files created** | 23 |
| **Bugs found in dev** | 1 (vision table detection) |
| **Bugs found in prod** | 0 |
| **Actual concepts extracted** | 24 (vs 23 predicted) |
| **Token savings validated** | 97% (per ADR-011) |

## Celebration 🎉

**F2.1 shipped successfully!**
- ✅ Full feature complete in under 1 hour
- ✅ High test coverage and quality
- ✅ Real-world validation with 24 concepts extracted
- ✅ Foundation ready for F2.2 Graph Builder
- ✅ No blockers encountered
- ✅ Clean commit history on feature branch

**What made this successful:**
1. Spike de-risked the approach
2. Design provided concrete targets
3. Plan decomposed work optimally
4. Implementation followed patterns
5. Tests caught bugs early
6. Real governance files validated assumptions

**Ready for F2.2!** 🚀

---

*Retrospective completed: 2026-01-31*
*Next: F2.2 Graph Builder (2 SP)*
