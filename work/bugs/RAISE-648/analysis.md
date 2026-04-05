# RAISE-648: Analysis

## Method: Stack trace analysis + hypothesis-driven

### Causal chain (3 levels)

1. **ID generation** (`governance/parsers/epic.py:81-85`): `re.search(r"^e(\d+)", parent_dir)` extracts only the number — `e14-rai-distribution` and `e14-skill-product-evaluation` both → `E14` → `epic-e14`
2. **No cross-source deduplication**: `extract_epics` from backlog.md and `extract_epic_details` from scope.md can both produce `epic-e14` — governance extractor merges same-source dupes but builder sees cross-loader dupes
3. **Crash in builder** (`context/builder.py:102`): `raise ValueError` on duplicate — kills entire graph build, no index.json generated

### UX impact

All graph-dependent commands fail: `rai graph query`, PRIME in skills, `rai session start --context`. The user sees an unhandled ValueError traceback with no recovery path.

## Root Cause

`GraphBuilder.build()` raises `ValueError` on duplicate node IDs with no graceful degradation. The design comment says "silent overwrites lose data" — true, but crashing loses the entire graph.

Note: The ID generation issue (extracting only the number) is tracked separately as RAISE-1204/RAISE-1199.

## Fix Approach (Option B)

1. Add `strict: bool` parameter to `GraphBuilder.__init__()` (default `False`)
2. In `build()`: if duplicate and `strict=False` → log warning, skip duplicate (keep first). If `strict=True` → raise as today.
3. Add `--strict` flag to `rai graph build` CLI command
4. `build()` collects warnings in a list accessible after build for CLI reporting
