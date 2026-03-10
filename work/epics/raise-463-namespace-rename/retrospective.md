# RAISE-463: Package Namespace Rename — Retrospective

## Summary

Renamed all 3 packages from `rai-*` to `raise-*` to resolve PyPI namespace
collision with Robotec.AI's `rai-core`. CLI command stays `rai`.

## Metrics

| Metric | Value |
|--------|-------|
| Stories | 5 (all complete) |
| Total commits | ~25 |
| Files modified | 500+ (renames + import updates) |
| Tests | 3699 passed throughout |
| Dragons found | 4 |

## What was delivered

- `raise-core` (was rai-core): 11 src files, shared domain models
- `raise-server` (was rai-server): 25 src files, Dockerfile, alembic, docker-compose
- `raise-cli` (was rai-cli): 197 src files, 329 mock paths, entry points
- CI/CD, docs, skills all updated
- Validated: pyright 0 errors, ruff clean, full test suite green
- PyPI publish deferred to post-bugfix v2.2.1 release

## Dragons Encountered

1. **rai_pro cross-import** — `src/rai_pro/providers/auth/credentials.py` imports
   `rai_cli.compat`. Not in the original blast radius map because rai_pro wasn't
   scanned. **Lesson:** scan ALL `src/` subdirs, not just the target package.

2. **Stale entry points** — after renaming package, old `rai-cli` entry points
   persisted in venv alongside `raise-cli`. Required explicit
   `uv pip uninstall rai-cli rai-core rai-server`.
   **Lesson:** package rename ≠ package replacement in pip/uv.

3. **MCP optional extra** — `uv sync --extra dev` doesn't install `mcp` extra.
   Need `uv sync --all-extras` for full test suite.
   **Lesson:** always test with `--all-extras` for validation gates.

4. **Import sorting drift** — `sed` bulk rename changed import line lengths,
   triggering ruff I001 (unsorted imports) on 2 files.
   **Lesson:** always run `ruff check --fix` after bulk sed operations.

## What went well

- **Checkpoint strategy** — C1-C4 commits per story gave confidence and easy
  rollback points. Each checkpoint was independently verifiable.
- **Dependency ordering** — core → server → cli sequence meant each step could
  be validated before the next.
- **`git mv`** — preserved file history through renames.
- **sed reliability** — bulk `s/rai_cli/raise_cli/g` worked cleanly on 500+ files
  with only 2 lint formatting issues.

## What could improve

- **Blast radius gemba** should scan ALL source directories, not just the target.
  rai_pro was missed because it wasn't in the scope map.
- **Post-rename venv cleanup** should be documented as a standard step — old
  packages don't auto-uninstall when the name changes.

## Patterns

- **PAT: Checkpoint commits for large mechanical renames** — commit after each
  phase (dir rename, internal imports, external imports, config). Each is
  independently revertible. Reduces risk significantly.
- **PAT: Dependency-ordered package renames** — rename in dependency order
  (leaf → root) so imports resolve at each step.

## Process Notes

- Epic was scoped correctly at 5 stories (1S + 1S + 1M + 1S + 1S)
- No scope creep — stayed disciplined on "rename only, no refactoring"
- PyPI publish correctly deferred — bundling with bugfixes is more efficient
