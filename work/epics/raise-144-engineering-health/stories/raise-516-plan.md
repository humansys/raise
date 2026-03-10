# RAISE-516 Plan: Move raise-core into src/

**Story:** RAISE-516 | **Size:** M | **Date:** 2026-03-10
**Design:** raise-516-design.md

## Task Overview

| # | Task | Size | Depends | AC |
|---|------|------|---------|----|
| T1 | Move raise_core/ to src/ and delete packages/raise-core/ | S | — | AC1, AC2 |
| T2 | Update pyproject.toml — remove workspace, fix all tool paths | M | T1 | AC3 |
| T3 | Update sync-github.sh — exclude src/rai_pro | XS | — | SHOULD-2 |
| T4 | Full verification — tests, types, lint, import check | S | T1, T2 | AC4, AC5, SHOULD-1 |

## Task Details

### T1: Move raise_core/ to src/ (S)

**What:** Move `packages/raise-core/src/raise_core/` → `src/raise_core/`. Delete `packages/raise-core/` entirely.

**Files:**
- `packages/raise-core/` → DELETE (after move)
- `src/raise_core/` → CREATE (moved from packages)

**Steps:**
1. `cp -r packages/raise-core/src/raise_core/ src/raise_core/`
2. `rm -rf packages/raise-core/`
3. Verify `src/raise_core/graph/models.py` exists (spot check)

**TDD:** No test changes — this is a file move. Verification is that existing tests still import correctly (deferred to T4).

**Verify:** `ls src/raise_core/graph/models.py && ! test -d packages/raise-core`

---

### T2: Update pyproject.toml (M) — RISKIEST

**What:** Remove workspace/sources config, update all tool paths, update hatch build targets, remove raise-core from dependencies.

**Files:**
- `pyproject.toml` → MODIFY

**Changes:**
1. DELETE `[tool.uv.workspace]` section (lines 1-2)
2. DELETE `[tool.uv.sources]` section (lines 4-6)
3. REMOVE `"raise-core==2.2.1"` from `[project.dependencies]`
4. UPDATE `[tool.hatch.build.targets.wheel]` packages: add `"src/raise_core"`
5. UPDATE `[tool.hatch.build.targets.sdist]` include: add `"/src/raise_core/"`
6. UPDATE `[tool.ruff]` src: `["src", "packages/raise-core/src"]` → `["src"]`
7. UPDATE `[tool.pyright]` include: remove `"packages/raise-core/src"`
8. UPDATE `[tool.pytest.ini_options]` addopts: `packages/raise-core/src/raise_core` → `src/raise_core`
9. UPDATE `[tool.coverage.run]` source: `packages/raise-core/src/raise_core` → `src/raise_core`

**TDD:** No test code changes. Verification is uv sync + full test suite (T4).

**Verify:** `! grep -q 'tool.uv.workspace' pyproject.toml && ! grep -q 'packages/raise-core' pyproject.toml`

---

### T3: Update sync-github.sh (XS) — parallel with T1/T2

**What:** Add exclusion for `src/rai_pro` so private code stays off GitHub.

**Files:**
- `scripts/sync-github.sh` → MODIFY

**Changes:**
1. After existing `git rm` loop for directories, add: `git rm -r --cached --quiet --ignore-unmatch "src/rai_pro"`

**TDD:** Manual verification via dry-run of sync logic.

**Verify:** `grep -q 'rai_pro' scripts/sync-github.sh`

---

### T4: Full verification (S) — final gate

**What:** Run complete validation suite. Verify zero import breakage.

**Steps:**
1. `uv sync --extra dev` — lock file resolves without workspace
2. `uv run pytest` — all tests green (AC4)
3. `uv run pyright` — no new errors (AC5)
4. `uv run ruff check` — clean (SHOULD-1)
5. Spot-check: `python -c "from raise_core.graph.models import GraphNode; print('OK')"` — imports work
6. Verify MUST NOT: no import statements changed, raise-server untouched

**Verify:** All commands exit 0.

## Execution Order

```
T1 (move files) ──→ T2 (pyproject.toml) ──→ T4 (verify all)
T3 (sync script) ─────────────────────────↗
```

**Rationale:** T2 is riskiest (build config) — do it right after T1 so we can validate early. T3 is independent and can be committed alongside. T4 is the final gate.

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| uv sync fails after workspace removal | T4 catches immediately; revert T2 if needed |
| Pyright can't find raise_core | src/ already in include path — should resolve |
| raise-server workspace breaks | Keep raise-server in sources if needed (but test first without) |

## Duration Tracking

| Task | Estimated | Actual | Notes |
|------|-----------|--------|-------|
| T1 | 5 min | | |
| T2 | 10 min | | |
| T3 | 3 min | | |
| T4 | 5 min | | |
| **Total** | **~23 min** | | |
