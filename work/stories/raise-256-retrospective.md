---
story: RAISE-256
title: CI pipeline broken — uv sync --dev does not install pytest
date-started: 2026-02-24
date-completed: 2026-02-24
size-estimated: XS
size-actual: XS
time-estimated: 10 min
time-actual: 5 min
velocity: 2x
---

## Summary

1-line fix: `uv sync --dev` → `uv sync --extra dev` in ci.yml.
Root cause: `--dev` targets `[dependency-groups]` (PEP 735);
pyproject.toml uses `[project.optional-dependencies]` (PEP 508 extras).

## What Went Well

- Diagnosis immediate from reading ci.yml + pyproject.toml together
- Fix verified locally before commit (pytest/ruff/pyright all available)
- 2x velocity — XS estimated, faster than estimated

## Learnings

`uv sync --dev` and `uv sync --extra dev` are not interchangeable:
- `--dev` → `[dependency-groups.dev]` (PEP 735, uv-native)
- `--extra dev` → `[project.optional-dependencies.dev]` (PEP 508, standard)

## No patterns added — single-occurrence, not a recurring pattern
