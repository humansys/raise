# RAISE-516 Retrospective

**Story:** Move raise-core into src/ and eliminate uv workspace pattern
**Date:** 2026-03-10
**Estimated:** ~23 min (4 tasks) | **Actual:** ~20 min

## What Went Well

- Zero import changes needed — the design insight (module path unchanged) was correct
- Git detected all file moves as 100% renames — history preserved
- uv lock regeneration cleanly removed raise-core — no stale references
- Clean task decomposition: T1-T4 executed sequentially without blockers

## What to Improve

- **Design missed cross-dependency:** raise-server's pyproject.toml depended on raise-core. This was discovered during T2, not during design. Should have grepped all pyproject.toml files for `raise-core` references during Step 3 (Approach).
- **Pre-existing test failures:** 73 tests failing on dev were carried forward without a tracking story. Jidoka principle correctly invoked by human — these need a dedicated bug fix.

## Heutagogical Checkpoint

1. **Learned:** uv workspace source resolution rules — workspace members that depend on each other need explicit `[tool.uv.sources]` entries. Removing the dep entirely is cleaner than adding circular source entries.
2. **Process change:** When planning package removal, always audit ALL pyproject.toml files for cross-references (PAT-E-002).
3. **Framework improvement:** Need bug story for 73 pre-existing test failures. Jidoka must be applied consistently.
4. **New capability:** uv workspace mechanics — how to restructure without breaking dependency resolution.

## Patterns

- **PAT-E-002:** Grep all pyproject.toml files when removing workspace packages
- **PAT-E-003:** Use cp+rm for file moves to preserve git rename detection

## Outcome

All acceptance criteria met:
- AC1: src/raise_core/ has all 11 modules
- AC2: packages/raise-core/ deleted
- AC3: No [tool.uv.workspace] raise-core references in pyproject.toml
- AC4: Tests — 3605 passed (same as dev baseline)
- AC5: Pyright — 29 errors (same as dev baseline)
- SHOULD-1: Ruff — all checks passed
- SHOULD-2: sync-github.sh excludes src/rai_pro
