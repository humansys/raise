# RAISE-145: Plan

## Summary

Clean stale "Unified" class name references from documentation and discovery artifacts.
Source code renaming is already complete; this is artifact cleanup only.

## Tasks

### T1: Fix stale class name references in docs

**Files:**
- `dev/architecture-overview.md` — 6 references to old Unified* class names (~lines 130-132, 172, 327, 334, 368)
- `dev/components.md` — 1 reference to `UnifiedGraphBuilder`

**Action:** Read each file, replace stale class names per the mapping in scope.md, commit.

**Validation:** `grep -r 'Unified\(Graph\|Query\|GraphBuilder\)' dev/` returns no hits (excluding ADR-019 title references).

### T2: Regenerate discovery artifacts

**Files:**
- `work/discovery/components-draft.yaml` — stale Unified* component names
- `work/discovery/components-validated.json` — stale Unified* component names

**Action:** Delete stale files and re-scan with `rai discover scan`, or manually update the 7 component names in place if re-scan is not practical.

**Validation:** `grep -r 'Unified' work/discovery/` returns no class-name hits.

## Done

- [ ] T1 complete and committed
- [ ] T2 complete and committed
- [ ] All tests pass (`uv run pytest`)
- [ ] Type checks pass (`uv run pyright`)
- [ ] Lint passes (`uv run ruff check`)
