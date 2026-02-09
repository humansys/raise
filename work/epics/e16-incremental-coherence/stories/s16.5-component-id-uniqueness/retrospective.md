# Retrospective: S16.5 Component ID Uniqueness

## Summary
- **Story:** S16.5
- **Size:** S (3 SP)
- **Started:** 2026-02-09
- **Completed:** 2026-02-09
- **Commits:** 6 (scope + 4 tasks + 1 hotfix)
- **Tests added:** 4 new tests (83 total analyzer, 187 total affected)

## Results
- **Before:** 345 validated components → 335 in graph (10 silently dropped)
- **After:** 345 validated components → 345 in graph (0 drops)
- **Graph:** 1013 nodes, 9935 edges

## What Went Well
- Jidoka assertion (Task 2) caught an unforeseen collision during integration test (Task 4) — module-level entries (`kind=module`) colliding with same-named functions. The assertion paid for itself immediately.
- Scope doc from SES-121 was thorough — root cause, affected IDs, proposed fix were all accurate. Design phase was a quick Gemba confirmation, no separate design.md needed.
- TDD cycle was clean: RED → GREEN → REFACTOR on every task, no regressions.

## What Could Improve
- The scope doc proposed `comp-{dotted.module.path}-{name}` but didn't account for the module/function name collision within the same file. This was only caught at integration time. A more thorough ID format analysis during scope writing (checking all `(kind, file, name)` triples) would have caught it earlier.

## Heutagogical Checkpoint

### What did you learn?
- Module-level symbols from the scanner use the file stem as their name (e.g., `name="test_version"` for `test_version.py`). When a function has the same name, the IDs collide even with unique module paths. The fix: use `"module"` as a canonical suffix for module-level entries.

### What would you change about the process?
- For ID format changes, enumerate all `(kind, name, file)` triples in the real dataset before committing to a format. A quick script during design would have caught the module/function collision.

### Are there improvements for the framework?
- No framework changes needed. The existing Jidoka principle (stop on defect) worked exactly as intended — the assertion caught the bug before it reached the graph.

### What are you more capable of now?
- Better understanding of the discovery pipeline's data flow: scanner → analyzer → validated JSON → graph builder. The ID is generated in `build_hierarchy()`, not in a separate `_generate_id()` function as the scope doc assumed.

## Patterns

### PAT-NEW: Jidoka assertions as integration safety nets
When changing data formats (IDs, keys, schemas), adding a uniqueness/validity assertion in the transformation step catches unforeseen collisions during integration testing. The assertion from Task 2 caught the module/function collision in Task 4 — a bug that would have been silent without it.

### PAT-NEW: ID format changes need dataset enumeration
Before committing to an ID format, enumerate all real triples `(kind, name, file)` in the actual dataset. Theoretical analysis misses edge cases that real data exposes (e.g., `test_version.py` having both a module and function named `test_version`).

## Action Items
- [ ] Fix pyright error in `tests/discovery/test_analyzer.py:51` — `_symbol` helper `kind: str` should be `SymbolKind` (pre-existing, observed during Task 1)
- [ ] Fix 3x SIM117 lint warnings in `tests/context/test_builder.py` — nested `with` → combined context managers (pre-existing, observed during Task 3)
- [ ] Add "enumerate real dataset triples" step to `/story-design` skill when story involves ID/key format changes (PAT-220 operationalized)

## Acceptance Criteria Status
- [x] All 345 validated components appear in the graph (0 silent drops)
- [x] Component IDs are unique across the entire discovery catalog
- [x] `raise discover analyze` fails if duplicate IDs would be generated
- [x] Graph builder warns on component ID collision
- [x] All existing tests pass with updated IDs
- [x] Quality gates pass (ruff, pyright — no new errors)
