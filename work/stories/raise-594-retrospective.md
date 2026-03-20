# RAISE-594: Retrospective

**Story:** RAISE-594 — CLI Extension Mechanism
**Date:** 2026-03-20
**Size:** XS (estimated 23 min)

## Summary

Added `rai.cli.commands` entry point group for external packages to register Typer command groups under the `rai` namespace. 3 files changed, ~150 LOC production + ~190 LOC tests, 11 unit tests, E2E verified with real installed package.

## What Went Well

- **Interactive design paid off.** The A/B/C alternatives discussion + "what makes it PRO" question elevated the design from 6 inline lines to a properly architected module with collision protection, duplicate detection, and observable return types.
- **TDD cycle was clean.** RED→GREEN→REFACTOR for each task, no test gymnastics needed. Mock-based testing of entry_points was straightforward.
- **Pattern consistency.** Following the hooks/gates registry idiom made the code predictable for anyone familiar with the codebase.
- **All gates passed first try** on every task (except ruff format, which is auto-fixable).

## What to Improve

- **E2E was an afterthought.** Unit tests with mocked entry_points passed, but the real E2E (installing a package, running `rai hello greet`) was only done when asked. Should have been an explicit task in the plan. Now captured as PAT-E-035.
- **uv script caching gotcha.** `uv run rai` caches the entry point script. After installing a new extension, the cached script doesn't see it until `uv pip install -e .` re-creates the script. This is pip/uv behavior, not our bug, but consumers will hit it. Should document in the extension authoring guide.

## Heutagogical Checkpoint

1. **Learned:** uv/pip script entry point caching means `uv run rai` can miss newly installed extensions until reinstall
2. **Would change:** Make E2E with real packages an explicit plan task, not a manual footnote
3. **Framework improvement:** HITL in design is valuable even for XS stories — the "what makes it PRO" question consistently improves designs
4. **More capable of:** Reusable plugin discovery pattern with 3-guard safety (collision, duplicate, type)

## Patterns

- **Added:** PAT-E-035 (E2E as explicit task), PAT-E-036 (CLI extension discovery architecture)
- **Reinforced:** PAT-E-588 (+1, entry point pattern), PAT-E-573 (+1, generic resolver), PAT-E-598 (+1, bare except)

## Artifacts

| File | Type | LOC |
|---|---|---|
| `src/raise_cli/cli/extensions.py` | Production | ~150 |
| `src/raise_cli/cli/main.py` | Modified | +4 |
| `tests/cli/test_extensions.py` | Tests | ~190 |
| 6 commits | Story branch | — |
