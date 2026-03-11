---
epic_id: "E478"
title: "Pro/Community Boundary"
status: "active"
created: "2026-03-11"
---

# E478: Pro/Community Boundary

## Objective
Ensure the open-source `raise-cli` package contains zero pro-only code (Jira, Confluence adapters) and zero pro-only dependencies. Pro features ship exclusively via `rai_pro`.

## Current State (what leaks)

| Item | Location | Problem |
|------|----------|---------|
| `mcp_jira.py` | `src/raise_cli/adapters/` | Pro adapter in community wheel |
| `mcp_confluence.py` | `src/raise_cli/adapters/` | Pro adapter in community wheel |
| `jira_sync.py` | `src/raise_cli/hooks/builtin/` | Pro hook in community wheel |
| Entry point: `jira` | `pyproject.toml` | Registers pro adapter from community |
| Entry point: `confluence` | `pyproject.toml` | Registers pro adapter from community |
| Entry point: `jira-sync` | `pyproject.toml` | Registers pro hook from community |
| `atlassian-python-api` | `[project.dependencies]` | Pro dep in community install |
| `authlib` | `[project.dependencies]` | Pro dep in community install |
| `cryptography` | `[project.dependencies]` | Pro dep in community install |
| `requests`, `urllib3`, `certifi` | `[project.dependencies]` | Likely pro-only deps |
| `.raise/jira.yaml` | `.gitignore` | Fixed (this session) |
| `.raise/confluence.yaml` | `.gitignore` | Fixed (this session) |
| `_check_jira_config()` | `cli/commands/adapters.py` | Hardcoded Jira logic in community CLI |

## Planned Stories

1. **S478.1 — Move pro adapters to `rai_pro`**: relocate `mcp_jira.py`, `mcp_confluence.py`, `jira_sync.py` and their tests to `src/rai_pro/adapters/`
2. **S478.2 — Clean entry points and dependencies**: remove pro entry points and deps from `raise_cli` pyproject.toml, add them to `rai_pro` pyproject.toml
3. **S478.3 — Clean pro-specific CLI logic**: extract `_check_jira_config` and Jira status logic from `adapters.py` CLI command into plugin-provided functionality

## Done Criteria
- [ ] `pip install raise-cli` installs zero Atlassian/Jira/Confluence packages
- [ ] `mcp_jira.py`, `mcp_confluence.py`, `jira_sync.py` not present in community wheel
- [ ] Entry points for jira/confluence only appear when `rai_pro` is installed
- [ ] All existing tests pass (both community and pro)
- [ ] `rai adapter list` shows filesystem only (community), adds jira/confluence when pro installed
