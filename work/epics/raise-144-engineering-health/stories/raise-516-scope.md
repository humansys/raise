# RAISE-516 Scope

## In Scope

- Move `packages/raise-core/src/raise_core/` → `src/raise_core/`
- Move raise-core tests into `tests/` (if separate)
- Remove `[tool.uv.workspace]` and `[tool.uv.sources]` from pyproject.toml
- Update paths in ruff, pyright, pytest, coverage configs
- Update imports if any cross-package references exist
- Delete `packages/raise-core/` after move
- Exclude `src/rai_pro/` from GitHub sync script
- Keep `packages/raise-server/` as-is (private, excluded from GitHub)

## Out of Scope

- Changes to raise-server package structure
- New features or API changes
- Release process (separate step after merge)

## Done When

- `src/raise_core/` exists, `packages/raise-core/` deleted
- No `[tool.uv.workspace]` in pyproject.toml
- All tests pass locally (`uv run pytest`)
- Type checks pass (`uv run pyright`)
- Linting passes (`uv run ruff check`)
- `sync-github.sh` excludes `src/rai_pro/`
- GitHub CI would pass without pyproject.toml patching
