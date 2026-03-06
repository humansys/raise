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

- [ ] S463.1: Rename raise-core (S) — dir, namespace, pyproject, imports, 11 src + 38 test files
- [ ] S463.2: Rename raise-server (S) — dir, namespace, pyproject, imports, Dockerfile, alembic, 25 src + 33 test files. Depends: S463.1
- [ ] S463.3: Rename raise-cli (M) — dir rename (197 src files), namespace, imports, importlib.resources, 329 mock paths, conftest. Depends: S463.1
- [ ] S463.4: Config and CI (S) — root pyproject.toml, uv.lock, CI workflows, docker-compose, README, CHANGELOG, skills, dev docs. Depends: S463.1-3
- [ ] S463.5: Validate and publish (S) — full test suite, type check, lint, bump to 2.2.1, PyPI publish (core → server → cli). Depends: S463.4

## Done Criteria

1. `from raise_core.graph.models import GraphNode` works
2. `from raise_cli.cli import app` works
3. `rai --version` prints 2.2.1
4. All tests pass (3699+)
5. PyPI packages published: raise-core, raise-cli, raise-server
6. No `rai_core` or `rai_cli` or `rai_server` imports remain in source
