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
- Renaming governance/work artifacts or historical docs
- Deprecation wrapper for old `rai-cli` package
- Structural refactoring of modules

## Stories

- [ ] S463.1: Rename rai-core → raise-core (package, namespace, imports)
- [ ] S463.2: Rename rai-server → raise-server (package, namespace, imports)
- [ ] S463.3: Rename rai-cli → raise-cli (package, namespace, imports, entry points)
- [ ] S463.4: Update tooling config (pyright, ruff, coverage, CI)
- [ ] S463.5: Validate, version bump to 2.2.1, publish

## Done Criteria

1. `from raise_core.graph.models import GraphNode` works
2. `from raise_cli.cli import app` works
3. `rai --version` prints 2.2.1
4. All tests pass (3699+)
5. PyPI packages published: raise-core, raise-cli, raise-server
6. No `rai_core` or `rai_cli` or `rai_server` imports remain in source
