# RAISE-1060: Adapter Models Restructure — Scope

## In Scope
1. Split `models.py` into `models/` package with per-protocol modules
2. Move `BacklogItem`, `BacklogLink`, `BacklogComment` to filesystem adapter
3. Re-export all public models from `models/__init__.py` (zero breaking changes)
4. Add `SpaceInfo` to `models/docs.py` (needed by RAISE-1051)
5. Update `adapters/__init__.py` if needed
6. All tests pass, types pass, lint passes — no regressions

## Out of Scope
- Moving protocols or models to raise-core (v3.0 concern)
- Changing model definitions (fields, validators, etc.)
- Renaming any models
- Modifying any adapter logic
- Adding new tests beyond what's needed for SpaceInfo

## Done Criteria
1. `models.py` replaced by `models/` package with 4 modules + `__init__.py`
2. BacklogItem/BacklogLink/BacklogComment live in filesystem module
3. All 47+ existing import sites work unchanged
4. `SpaceInfo` available in `models/docs.py`
5. `pytest`, `pyright`, `ruff` all green
6. No functional changes — pure restructure
