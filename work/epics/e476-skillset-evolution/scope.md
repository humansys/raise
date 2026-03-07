# E476: Skillset Evolution — Scope

## Objective
Separate language-specific gate configuration from core skills so RaiSE works cleanly across any tech stack.

## Gemba Findings
- Manifest already has `project.test_command`, `project.lint_command`, `project.type_check_command`
- 5 skills already use manifest-first with language detection fallback (story-review, story-close, epic-close, quality-review, bugfix-examples)
- 3 skills hardcode without manifest fallback: implement, plan, bugfix
- 4 builtin gates (TestGate, LintGate, TypeGate, CoverageGate) hardcode pytest/ruff/pyright in Python code — don't read manifest
- Skillset system exists (`rai skill set create/list/diff`) but no sets created yet

## In Scope
1. **Builtin gates read manifest** — TestGate, LintGate, TypeGate, CoverageGate read commands from `.raise/manifest.yaml` instead of hardcoding
2. **Language-agnostic skills** — implement, plan, bugfix use manifest-first pattern (same as story-review/close already do)
3. **raise-dev skillset** — Python-specific skill overlays using the skillset system
4. **raise-dev-ts example** — TypeScript skillset demonstrating extensibility

## Out of Scope
- Full CI/CD pipeline generation
- Auto-detection of project language (manifest is explicit config)
- Rewriting skills that already use manifest-first pattern (story-review, story-close, epic-close, quality-review)
- Gate configuration schema changes — manifest fields already exist

## Stories

| ID | Story | Size | Deps | Description |
|----|-------|------|------|-------------|
| S476.1 | Builtin gates read manifest | S | — | TestGate, LintGate, TypeGate, CoverageGate read `project.*_command` from manifest, fallback to current hardcoded defaults |
| S476.2 | Skills use manifest-first pattern | S | — | Refactor implement, plan, bugfix to use manifest commands (same pattern as story-review/close) |
| S476.3 | Create raise-dev skillset | XS | S476.2 | Python-specific skill overlays via `rai skill set create raise-dev` |
| S476.4 | Create raise-dev-ts example | XS | S476.3 | TypeScript skillset demonstrating the pattern for non-Python projects |
| S476.5 | Skillset documentation | XS | S476.3 | How to create custom skillsets, gate configuration guide |

Dependency graph: `S476.1 ──┐`  `S476.2 ──→ S476.3 ──→ S476.4`  `                    └──→ S476.5`

## Done Criteria
- All builtin gates read commands from manifest (with sensible defaults)
- All skills that invoke test/lint/typecheck use manifest-first pattern
- `raise-dev` skillset exists with Python-specific overlays
- `raise-dev-ts` example exists
- Existing Python workflow unchanged (backwards compatible)
- `rai gate check --all` works correctly with manifest config

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Breaking existing gate behavior during refactor | Medium | High | TDD — regression tests before any change |
| Skillset overlay mechanism not working as expected | Low | Medium | Test with actual `rai skill set create` before relying on it |
| Manifest not available in all contexts (e.g., no .raise/) | Low | Low | Fallback to current hardcoded defaults — graceful degradation |
