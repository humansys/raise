---
id: "ADR-014"
title: "Atlassian Transport Backend: atlassian-python-api"
date: "2026-03-28"
status: "Accepted"
related_to: ["ADR-033", "ADR-041"]
supersedes: []
story: "RAISE-1047"
---

# ADR-014: Atlassian Transport Backend

## Context

### Problem

RaiSE uses two different transport backends for Atlassian integration:

- **Jira**: AcliJiraAdapter invokes ACLI (Java subprocess) — requires Java runtime + ACLI binary
- **Confluence**: McpConfluenceAdapter invokes mcp-atlassian (MCP stdio) — requires Node/uvx

This creates two dependency chains for one vendor. Both are problematic on Windows
(RAISE-990: 156-minute install session). Neither covers the full function set
required by the v2 adapter vision (37 functions across 4 adapters).

### Current coverage

| Backend | Functions covered | Functions needed | Gap |
| --- | --- | --- | --- |
| ACLI (Jira) | 11 | 15 | 4 (discovery/validation) |
| mcp-atlassian (Confluence) | 5 | 11 | 6 (labels, tree, create) |
| **Total** | **16** | **26** | **10 (38% missing)** |

### Evaluation

Four options evaluated against 7 criteria (RAISE-1047 spike):

| Criterion | ACLI | mcp-atlassian | atlassian-python-api | REST direct |
| --- | --- | --- | --- | --- |
| Dependencies | Java + JAR | Node/uvx | pip install | pip install httpx |
| Windows | Hard | Hard | Trivial | Trivial |
| Jira coverage | 11/15 | 11/15 | 15/15 | 15/15 (we build) |
| Confluence coverage | N/A | 5/11 | 10/11 | 11/11 (we build) |
| Auth methods | 1 (site switch) | 1 (env vars) | 7 | We implement |
| Maintenance | Us + vendor | Community | 328 contributors | 100% us |
| Testability | Hard (subprocess) | Medium (MCP mock) | Easy (class mock) | Easy |

## Decision

Adopt `atlassian-python-api` as the single transport backend for all Atlassian
adapters (Jira + Confluence) in adapter v2.

### Why this option

1. **Already a dependency** — `atlassian-python-api>=3.41.0` is in raise-pro
   pyproject.toml but unused. Zero new installation cost.
2. **25/26 functions covered** — native methods for 25 required functions. The
   1 gap (Confluence health check) is trivially bridged via the base class
   `get()` method which exposes raw HTTP.
3. **Pure Python** — eliminates Java and Node as runtime dependencies.
   Reduces Atlassian install steps from 7 to 3.
4. **One package, two products** — Jira and Confluence in a single library
   with consistent API patterns.
5. **Cloud + Server/DC** — explicit support for both deployment models with
   platform-aware behavior.
6. **Testable** — class methods, not subprocesses. Standard mock/patch
   patterns work.

### What this means for existing adapters

- `AcliJiraAdapter` becomes **legacy** — maintained for backwards compat,
  not used by v2 skills
- `McpConfluenceAdapter` becomes **legacy** — same treatment
- New adapters: `PythonApiJiraAdapter` and `PythonApiConfluenceAdapter`
  implement the same Protocols using `atlassian-python-api` as transport
- Declarative MCP adapters remain available for non-Atlassian backends

### Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Library is "Beta" (v4.0.x) | Our Protocol layer wraps it — changes affect one file |
| Confluence Cloud vs Server class split | Config exposes `cloud: true`, adapter selects class |
| Method naming inconsistency | Protocol normalizes names, library is implementation detail |
| Library abandoned | 328 contributors, 5200 dependents, active (Mar 2026). If abandoned, migrate to REST direct (same HTTP, different client) |

## Consequences

### Positive

- Windows installation drops from ~7 steps to ~3 (Python + uv + pip install)
- All 26 Atlassian functions available from day one
- Single dependency chain for Jira + Confluence
- Tests are faster (no subprocess overhead) and simpler (class mocking)
- Cloud and Server/DC supported from single codebase

### Negative

- Two legacy adapters to maintain during transition (ACLI + MCP)
- Library updates may break our wrapper (mitigated by Protocol layer)
- "Beta" status means no formal API stability guarantees

### Not addressed

- Python + uv installation on Windows remains the primary friction point
  (RAISE-990). This ADR eliminates the Atlassian-specific friction but
  not the Python runtime friction. See RAISE-990 for that track.

## References

- Spike: RAISE-1047
- Library: https://github.com/atlassian-api/atlassian-python-api
- PyPI: https://pypi.org/project/atlassian-python-api/
- Adapter Vision: `governance/product/adapter-vision.md`
- Windows DX: RAISE-990
