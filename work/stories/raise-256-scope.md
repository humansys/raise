---
story: RAISE-256
title: CI pipeline broken — uv sync --dev does not install pytest
size: XS
branch: story/standalone/raise-256-ci-uv-sync-dev
base: v2
status: in-progress
---

## Root Cause

`pyproject.toml` defines dev tools (pytest, ruff, pyright) under
`[project.optional-dependencies]` as the `dev` extra (PEP 508).

`uv sync --dev` installs from `[dependency-groups.dev]` (PEP 735),
which does not exist in this project. Result: pytest not installed,
CI fails on `uv run pytest`.

## In Scope

- Fix CI workflow to use `uv sync --extra dev` (correct flag for optional-dependencies)
- Also update ruff and pyright lines to use `--extra dev` for consistency

## Out of Scope

- Migrating to `[dependency-groups]` (PEP 735) — separate decision
- Adding new CI steps
- Changing pyproject.toml dependency structure

## Done When

- [ ] `uv sync --extra dev` in ci.yml installs pytest, ruff, pyright
- [ ] CI workflow file is syntactically valid
- [ ] Verified locally that `uv sync --extra dev` resolves correctly
