# RAISE-516 Design: Move raise-core into src/

## Problem & Value

`raise-core` lives in `packages/raise-core/` as a uv workspace member. GitHub CI breaks because `packages/` is excluded from the public mirror but `pyproject.toml` references workspace members. The workspace pattern adds no value — raise-core and raise-cli are always released together.

## Approach

Move `packages/raise-core/src/raise_core/` into `src/raise_core/` (alongside `raise_cli/` and `rai_pro/`). Remove workspace config. Delete `packages/raise-core/`.

**Key insight:** All imports use `from raise_core.graph...` — the module path doesn't change, only the physical location. Zero import changes needed.

## Components

| Component | Change | Notes |
|-----------|--------|-------|
| `packages/raise-core/` | Delete | Contents moved to src/ |
| `src/raise_core/` | Create | Moved from packages |
| `pyproject.toml` | Modify | Remove workspace/sources, update tool paths, add to hatch build |
| `scripts/sync-github.sh` | Modify | Exclude src/rai_pro |

## Decisions

| ID | Choice | Rationale |
|----|--------|-----------|
| D1 | Flat sibling in src/ | Same release cycle, workspace adds no value |
| D2 | Zero import changes | Module path unchanged, only physical location moves |
| D3 | Remove raise-core from deps | No longer a separate package |

## Acceptance Criteria

**MUST:**
1. `src/raise_core/` has all modules from `packages/raise-core/`
2. `packages/raise-core/` deleted
3. No `[tool.uv.workspace]` or `[tool.uv.sources]` in pyproject.toml
4. `uv run pytest` — all green
5. `uv run pyright` — clean

**SHOULD:**
1. `uv run ruff check` passes
2. `sync-github.sh` excludes `src/rai_pro`

**MUST NOT:**
1. Change any `from raise_core.*` import
2. Modify `packages/raise-server/`
3. Change public API surface
