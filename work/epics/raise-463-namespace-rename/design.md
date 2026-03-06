# RAISE-463: Package Namespace Rename — Design

## Gemba Summary

### Blast Radius

| Area | Files | Change Type |
|------|-------|-------------|
| Source `rai_cli` → `raise_cli` | 197 .py + dir rename | imports, module paths |
| Source `rai_core` → `raise_core` | 11 .py + dir rename | imports, module paths |
| Source `rai_server` → `raise_server` | 25 .py + dir rename | imports, module paths |
| Tests (imports) | ~435 files | imports |
| Tests (mock paths) | 329 occurrences | `patch("rai_cli.x")` → `patch("raise_cli.x")` |
| pyproject.toml (root) | 38 references | name, deps, entry points, tool config |
| pyproject.toml (core) | 4 references | name, wheel target |
| pyproject.toml (server) | 3 references | name, dep, wheel target |
| Entry point groups | 7 groups | **NO CHANGE** — stay as `rai.*` |
| CI/CD | 2 workflow files | PyPI URL, package ref |
| Docker | Dockerfile + compose | paths, uvicorn cmd |
| Alembic | env.py | 1 import |
| Skills (.md) | 9 files | narrative references |
| conftest.py | 2 files | mock paths |
| README, CHANGELOG | 2 files | package name refs |
| uv.lock | auto | regenerate |
| `rai_base` subpackage | internal | moves with dir, update importlib.resources refs |

### Decisions

1. **Entry point groups stay `rai.*`** — they represent the CLI brand, not the PyPI
   package. Can be renamed independently later without breaking changes.

2. **Historical docs untouched** — ADRs, epic scopes, session logs are
   point-in-time records. Only update README, CHANGELOG, architecture-overview,
   and active dev docs.

3. **Version 2.2.1** — patch bump signals bugfix (namespace collision), not new
   features. All three packages publish at 2.2.1.

4. **`rai_base` stays named `rai_base`** — it's a data subpackage inside the CLI,
   not a Python namespace concern. Its import path changes from
   `rai_cli.rai_base` → `raise_cli.rai_base` automatically with the dir rename.

### Rename Strategy

Use `git mv` for directory renames to preserve history, then `sed` for bulk
import/reference replacement. Order matters — rename in dependency order:

1. `rai_core` first (no internal deps)
2. `rai_server` second (depends on core)
3. `rai_cli` last (depends on core)

Each rename follows: dir rename → import update → test update → verify.

### Key Contracts

```
# Before
from rai_core.graph.models import GraphNode
from rai_cli.cli.main import app
from rai_server.app import create_app

# After
from raise_core.graph.models import GraphNode
from raise_cli.cli.main import app
from raise_server.app import create_app

# CLI command unchanged
rai = "raise_cli.cli.main:app"

# Entry point groups unchanged
[project.entry-points."rai.hooks"]
[project.entry-points."rai.gates"]
[project.entry-points."rai.governance.parsers"]
```

### Risk Mitigations

| Risk | Mitigation |
|------|-----------|
| 329 mock paths broken | `sed -i 's/rai_cli/raise_cli/g'` on tests/, verify with pytest |
| Entry points don't resolve | Smoke test: `uv run rai --version` after each story |
| importlib.resources paths | Search `files("rai_cli` and `files("rai_base` — update |
| uv.lock stale | `uv lock` after pyproject.toml changes |
| Docker build breaks | Update Dockerfile paths + test build |

## Stories (revised from scope)

| ID | Name | Size | Depends | Description |
|----|------|------|---------|-------------|
| S463.1 | Rename raise-core | S | — | Dir rename, namespace, pyproject.toml, internal imports, tests |
| S463.2 | Rename raise-server | S | S463.1 | Dir rename, namespace, pyproject.toml, imports, Dockerfile, alembic, tests |
| S463.3 | Rename raise-cli | M | S463.1 | Dir rename (197 files), namespace, imports, entry points, importlib.resources, mock paths (329), conftest, tests |
| S463.4 | Config and CI update | S | S463.1-3 | Root pyproject.toml, uv.lock, CI workflows, docker-compose, README, CHANGELOG, skills, active dev docs |
| S463.5 | Validate and publish | S | S463.4 | Full test suite, type check, lint, version bump to 2.2.1, PyPI publish (core → server → cli) |

## Out of Scope (parking lot)

- Rename entry point groups `rai.*` → `raise.*` (independent, no urgency)
- Deprecation wrapper for old `rai-cli` PyPI package
- Update historical docs (ADRs, epic scopes, session logs)
