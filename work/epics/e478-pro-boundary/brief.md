---
epic_id: "E478"
title: "Pro/Community boundary — prevent pro code leaking into open-source package"
status: "draft"
created: "2026-03-11"
---

# Epic Brief: Pro/Community Boundary

## Hypothesis
For open-source users installing `raise-cli` from PyPI,
the package currently ships pro-only adapter code (Jira, Confluence) and unnecessary dependencies.
This violates the community/pro boundary and bloats the install with `atlassian-python-api`, `authlib`, `cryptography`.
Unlike the current state, the clean package will contain only filesystem adapters and generic protocols.

## Success Metrics
- **Leading:** `pip install raise-cli` pulls zero Jira/Confluence/Atlassian dependencies
- **Lagging:** `rai_pro` package installs cleanly as an add-on, registers its adapters via entry points

## Appetite
S — 3-4 stories

## Scope Boundaries
### In (MUST)
- Move `mcp_jira.py`, `mcp_confluence.py` out of `raise_cli` wheel
- Move `jira_sync.py` hook out of `raise_cli` wheel
- Remove Jira/Confluence entry points from `raise_cli` pyproject.toml
- Remove pro-only dependencies from base `[project.dependencies]`
- Ensure `.raise/jira.yaml` and `.raise/confluence.yaml` stay gitignored (done)
- `rai_pro` registers its adapters/hooks via entry points when installed

### In (SHOULD)
- Clean up `adapters.py` CLI command — Jira-specific status logic should come from plugin
- Verify `rai_pro` has its own `pyproject.toml` with correct deps and entry points

### No-Gos
- Full `rai_pro` packaging/release pipeline (separate epic)
- Changing adapter protocols or models
- Refactoring the MCP bridge (shared infrastructure, stays in `raise_cli`)

### Rabbit Holes
- Over-engineering a plugin discovery system — entry points already work, keep it simple
- Trying to make adapters lazy-loadable — just move them, don't add complexity
