# Bug RAISE-396 — Retro

## Fix Summary

Single-line change: `.gitlab-ci.yml` line 23
`uv sync --extra dev` → `uv sync --extra dev --extra mcp`

## Root Cause Confirmed

The `mcp` optional dependency group was added to `pyproject.toml` (epic e337,
Declarative MCP Adapter Framework) but the CI config was not updated to install it.

## Systemic Insight

When adding new optional dependency groups to `pyproject.toml`, CI must be updated
in the same commit/PR. Otherwise the test stage breaks silently on merge.

## Pre-existing Issues Noted

- 19 ruff errors (import sorting, unused vars, UP017 datetime.UTC)
- 6 pyright errors (reportUnknownArgumentType in mcp_jira.py)
These are not related to this bug but should be addressed separately.
