# RAISE-463: Package Namespace Rename — Scope

## Objective

Rename all Python packages from `rai-*` to `raise-*` to resolve PyPI namespace
collision with Robotec.AI's `rai-core`. CLI command remains `rai`.

## In Scope

- Rename package names in pyproject.toml (rai-cli → raise-cli, rai-core → raise-core, rai-server → raise-server)
- Rename Python namespaces (rai_cli → raise_cli, rai_core → raise_core, rai_server → raise_server)
- Rename source directories (src/rai_cli → src/raise_cli, etc.)
- Update all imports across the codebase
- Update entry points, scripts, and tool configuration
- Update tests (imports, mock paths, conftest)
- Publish to PyPI as raise-cli, raise-core, raise-server v2.2.1

## Out of Scope

- Changing the `rai` CLI command name
- Renaming entry point groups (`rai.*` stays — CLI brand, not package name)
- Renaming governance/work artifacts or historical docs
- Deprecation wrapper for old `rai-cli` package
- Structural refactoring of modules

## Stories

- [x] S463.1: Rename raise-core (S) — dir, namespace, pyproject, imports, 11 src + 38 test files
- [x] S463.2: Rename raise-server (S) — dir, namespace, pyproject, imports, Dockerfile, alembic, 25 src + 33 test files. Depends: S463.1
- [x] S463.3: Rename raise-cli (M) — dir rename (197 src files), namespace, imports, importlib.resources, 329 mock paths, conftest. Depends: S463.1
- [x] S463.4: Config and CI (S) — root pyproject.toml, uv.lock, CI workflows, docker-compose, README, CHANGELOG, skills, dev docs. Depends: S463.1-3
- [x] S463.5: Validate (publish deferred) (S) — full test suite, type check, lint, bump to 2.2.1, PyPI publish (core → server → cli). Depends: S463.4

## Implementation Plan

### Sequencing Strategy: Dependency-driven

Linear sequence — each package rename must complete before the next can start,
because packages import each other. No parallelism possible.

### Sequence

| # | Story | Size | Rationale | Enables |
|---|-------|------|-----------|---------|
| 1 | S463.1: Rename raise-core | S | No deps, foundation for all others | S463.2, S463.3 |
| 2 | S463.2: Rename raise-server | S | Depends on core, small surface | S463.4 |
| 3 | S463.3: Rename raise-cli | M | Largest surface (197 src, 329 mocks), depends on core | S463.4 |
| 4 | S463.4: Config and CI | S | All renames done, wire up tooling | S463.5 |
| 5 | S463.5: Validate and publish | S | Final gate before release | Epic done |

Note: S463.2 and S463.3 could theoretically run in parallel (both depend only
on S463.1), but the shared pyproject.toml and uv workspace make sequential
safer — avoids merge conflicts in config files.

### Milestones

**M1: Core renamed (after S463.1)**
- `from raise_core.graph.models import GraphNode` works
- Core tests pass in isolation
- Proves the rename strategy works at small scale

**M2: All packages renamed (after S463.3)**
- All source uses `raise_*` namespaces
- `uv run rai --version` works (smoke test)
- No `rai_cli`/`rai_core`/`rai_server` imports in src/

**M3: Epic complete (after S463.5)**
- Full test suite green (3699+)
- Type checks + lint pass
- v2.2.1 published on PyPI (raise-core, raise-server, raise-cli)

### Progress Tracking

| Story | Status | Notes |
|-------|--------|-------|
| S463.1 raise-core | Done | 4 checkpoints, 3699 tests pass |
| S463.2 raise-server | Done | 3 checkpoints, 3699 tests pass |
| S463.3 raise-cli | Done | 5 checkpoints, 3 dragons, 3699 tests pass |
| S463.4 Config/CI | Done | 18 files updated |
| S463.5 Validate/publish | Done (validate only) | 3699 pass, pyright 0 err, ruff clean. Publish deferred to post-bugfix |

### Sequencing Risks

1. **Shared pyproject.toml contention** — root pyproject.toml references all 3 packages.
   Mitigation: update root config in S463.4, not per-story.
2. **uv workspace resolution** — renaming workspace members may confuse uv cache.
   Mitigation: `uv cache clean` + `uv lock` after each rename.
3. **329 mock paths** — bulk sed could miss edge cases (string concatenation, f-strings).
   Mitigation: run full test suite after S463.3, fix stragglers manually.

## Done Criteria

1. `from raise_core.graph.models import GraphNode` works
2. `from raise_cli.cli import app` works
3. `rai --version` prints 2.2.1
4. All tests pass (3699+)
5. PyPI packages published: raise-core, raise-cli, raise-server
6. No `rai_core` or `rai_cli` or `rai_server` imports remain in source
