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

## Implementation Plan

> Added by `/rai-epic-plan` — 2026-03-11

### Story Sequence

| Order | Story | Size | Dependencies | Milestone | Rationale |
|:-----:|-------|:----:|--------------|-----------|-----------|
| 1 | S478.1 — Move pro adapters | S | None | M1 | Risk-first: code move is the core change; everything else depends on it |
| 2 | S478.2 — Clean entry points & deps | S | S478.1 | M2 | Can't remove entry points until code has moved |
| 3 | S478.3 — Clean CLI logic | XS | S478.2 | M2 | Cosmetic cleanup; adapter discovery already works via entry points |

### Milestones

| Milestone | Stories | Success Criteria |
|-----------|---------|------------------|
| **M1: Code separated** | S478.1 | Pro adapters live in `src/rai_pro/adapters/`, not in `raise_cli` wheel. All tests pass. |
| **M2: Clean package** | S478.2, S478.3 | `pip install raise-cli` pulls zero Atlassian deps. `rai adapter list` shows filesystem only. Done criteria met. |

### Sequencing

```
S478.1 (move code) ─► S478.2 (entry points + deps) ─► S478.3 (CLI cleanup)
```

Strictly sequential — each story depends on the previous. No parallel opportunities (same files touched).

### Key Decision: rai_pro packaging

`rai_pro` currently has no `pyproject.toml`. S478.2 must either:
- **(A)** Create `packages/raise-pro/` as a workspace package with its own pyproject.toml and entry points
- **(B)** Keep `rai_pro` in the monorepo root but exclude it from the community wheel via hatch config

Recommend **(A)** — consistent with existing workspace pattern (`packages/raise-server/`). Entry points register naturally.

### Progress Tracking

| Story | Size | Status | Notes |
|-------|:----:|:------:|-------|
| S478.1 — Move pro adapters | S | Done | Merged to dev cc0bf418 |
| S478.2 — Clean entry points & deps | S | Done | Merged to dev 0b9c357c |
| S478.3 — Clean CLI logic | XS | Pending | |

### Sequencing Risks

| Risk | L/I | Mitigation |
|------|:---:|------------|
| Import paths break in rai_pro after move | M/M | Grep all imports before/after; TDD catches it |
| `requests`/`urllib3`/`certifi` used by community code too | L/H | Verify no community imports before removing |
| rai_pro pyproject.toml missing — entry points won't register | M/H | Create in S478.2; verify with `rai adapter list` |

## Done Criteria
- [ ] `pip install raise-cli` installs zero Atlassian/Jira/Confluence packages
- [ ] `mcp_jira.py`, `mcp_confluence.py`, `jira_sync.py` not present in community wheel
- [ ] Entry points for jira/confluence only appear when `rai_pro` is installed
- [ ] All existing tests pass (both community and pro)
- [ ] `rai adapter list` shows filesystem only (community), adds jira/confluence when pro installed
