---
research_id: R2-RAISE-760
title: Python Atlassian Ecosystem 2026
epic: RAISE-760
date: 2026-03-27
status: complete
confidence: High
---

# R2: Python Atlassian Ecosystem

## Executive Summary

The Python ecosystem for interacting with Atlassian products in 2026 is fragmented across several libraries, two MCP server implementations, and a first-party CLI tool. The dominant library remains **atlassian-python-api** (4.0.x, Apache-2.0, ~1.6K GitHub stars), which RaiSE already depends on via `raise-pro`. It covers Jira, Confluence, Bitbucket, and more, but lacks async support, has no type annotations, and returns untyped dicts -- making it a poor fit for RaiSE's strict-typing, Pydantic-first, async-native architecture. The Jira-specific **jira** (PyJira, 3.10.x) library is similarly sync-only with minimal type hints.

A newer entrant, **pyatlassian** (0.3.x), markets itself as fully typed and built for modern REST API versions, but is very early-stage (low adoption, sparse documentation). The **mcp-atlassian** server by sooperset (0.21.x, MIT, 4.7K stars, 103 contributors) has emerged as the most active community project, providing 65+ MCP tools for Jira and Confluence -- and is already RaiSE's Confluence transport layer. Atlassian themselves launched the **Rovo MCP Server** (GA, cloud-hosted at `mcp.atlassian.com/v1/mcp`) with OAuth 2.1 and enterprise security, covering Jira, Confluence, and Compass.

For RaiSE's Forge app and adapter layer, the recommendation is a **layered strategy**: (1) keep ACLI for Jira CLI operations where it excels, (2) keep mcp-atlassian for Confluence via McpBridge, (3) evaluate Atlassian's official Rovo MCP Server as a potential replacement for both when OAuth 2.1 auth is available, and (4) use `atlassian-python-api` only as a direct-API fallback for edge cases not covered by the above. Do not invest in migrating to pyatlassian or PyJira -- neither offers enough advantage over what we already have.

## Library Comparison Matrix

| Library | Version | Stars | License | Products | API Versions | Auth | Python | Typed | Async | Maintenance | RaiSE Fit |
|---------|---------|-------|---------|----------|-------------|------|--------|-------|-------|-------------|-----------|
| atlassian-python-api | 4.0.7 | ~1.6K | Apache-2.0 | Jira, Confluence, Bitbucket, StatusPage, Insight, X-Ray | v2 + v3 (partial) | Basic, OAuth 1.0/2.0, PAT, Cookie | >=3.9 | No | No | Active (regular releases) | Low -- no types, no async |
| jira (PyJira) | 3.10.5 | ~1.9K | BSD | Jira only | v2 | Basic, OAuth 1.0, PAT, Cookie | >=3.10 | Minimal | Pseudo (thread-pool) | Moderate (slow release cadence) | Low -- Jira-only, no real async |
| pyatlassian | 0.3.2 | <100 | Unknown | Jira, Confluence (Cloud only) | v3 (latest) | Basic, PAT | >=3.10 | Yes (fully typed) | Unknown | Early-stage | Medium -- typed but immature |
| atlassian-api-py | 0.7.0 | <50 | MIT | Jira, Confluence, Bitbucket | v2 | Basic, PAT | >=3.9 | Unknown | No | Low activity | Low -- small project |
| mcp-atlassian (sooperset) | 0.21.0 | 4.7K | MIT | Jira, Confluence | v2 + v3 | Basic, OAuth 2.0, PAT | >=3.10 | N/A (MCP server) | N/A (MCP protocol) | Very active (weekly releases) | High -- already in use |
| Atlassian Rovo MCP Server | GA | N/A | Proprietary (Atlassian-hosted) | Jira, Confluence, Compass | v3 (Cloud) | OAuth 2.1 | N/A (remote) | N/A | N/A | Atlassian-maintained | High -- enterprise auth |
| Atlassian CLI (ACLI) | Latest | N/A | Proprietary | Jira (primary) | v2 + v3 | OAuth 2.0, PAT | N/A (binary) | N/A | N/A | Atlassian-maintained | High -- already in use |

## Detailed Evaluations

### atlassian-python-api

- **PyPI**: [atlassian-python-api](https://pypi.org/project/atlassian-python-api/)
- **GitHub**: [atlassian-api/atlassian-python-api](https://github.com/atlassian-api/atlassian-python-api) (~1.6K stars, 200+ contributors)
- **Latest release**: v4.0.7 (docs reference v4.0.8)
- **Maintenance**: Active, regular releases. Community-maintained (not official Atlassian).
- **Products**: Jira, Jira Service Management, Confluence, Bitbucket, StatusPage, Insight, X-Ray
- **API versions**: Covers v2 and partial v3 endpoints. REST-based with some xml+rpc and raw HTTP.
- **Auth**: Basic auth, OAuth 1.0a, OAuth 2.0, PAT (personal access token), cookie-based
- **Python**: >=3.9. Dependencies: requests, beautifulsoup4, oauthlib, jmespath
- **Type annotations**: None. No `py.typed` marker. Returns plain dicts throughout.
- **Async**: None. Entirely synchronous (requests-based).
- **License**: Apache-2.0

**Strengths**: Broadest product coverage of any Python library. Battle-tested in production. Huge example catalog. Supports both Cloud and Server/Data Center.

**Weaknesses**: No type annotations means Pyright strict fails on all return values. No async means wrapping in `asyncio.to_thread()` for every call. Dict-based returns require manual Pydantic model construction at the adapter boundary. The library is a dependency of `mcp-atlassian` internally, so we get it transitively already.

**RaiSE relevance**: Listed as a direct dependency in `raise-pro` (`>=3.41.0`), but the ACLI bridge and MCP bridge have replaced direct usage. The dependency may be vestigial or used only in edge-case utility functions. Worth auditing whether it can be removed from direct dependencies.

### jira (PyJira)

- **PyPI**: [jira](https://pypi.org/project/jira/)
- **GitHub**: [pycontribs/jira](https://github.com/pycontribs/jira) (~1.9K stars)
- **Latest release**: v3.10.5 (v3.10.6.dev6 in development)
- **Maintenance**: Moderate. Healthy community but slow release cadence.
- **Products**: Jira only
- **API versions**: v2 (REST)
- **Auth**: Basic, OAuth 1.0a, PAT, cookie-based
- **Python**: >=3.10
- **Type annotations**: Minimal. Open issue #689 requesting type hints since 2018.
- **Async**: Pseudo-async via thread pool (`async_` parameter, `async_workers`). Not native async/await.
- **License**: BSD

**Strengths**: Rich Jira-specific functionality. Mature JIRA object model (Issue, Project, etc. are Python objects, not raw dicts). Good for Jira-heavy automation.

**Weaknesses**: Jira-only -- no Confluence, Bitbucket coverage. Thread-pool "async" is not real async. Minimal type hints. Slower development pace. `aiojira` exists as a separate async wrapper but appears abandoned.

**RaiSE relevance**: Not currently used. Does not offer enough advantage over ACLI bridge for Jira operations. The object model is interesting but would need Pydantic conversion at the boundary anyway. Not recommended.

### pyatlassian

- **PyPI**: [pyatlassian](https://pypi.org/project/pyatlassian/)
- **GitHub**: Not found via search (possibly private or very new)
- **Latest release**: v0.3.2
- **Maintenance**: Early-stage. Very low adoption.
- **Products**: Jira, Confluence (Cloud only)
- **API versions**: v3 (latest Cloud REST APIs)
- **Auth**: Basic, PAT
- **Python**: >=3.10 (estimated)
- **Type annotations**: Yes -- marketed as "fully typed"
- **Async**: Unknown from available documentation
- **License**: Unknown

**Strengths**: Built for modern API versions. Fully typed. Pythonic interface design. Cloud-first (aligns with Atlassian's direction).

**Weaknesses**: Very early-stage (v0.3.x). Low community adoption (<100 stars). Sparse documentation. No Server/Data Center support. Unknown async support. Risk of abandonment.

**RaiSE relevance**: The typed, modern approach aligns with RaiSE's values, but maturity is too low to depend on for production. Worth monitoring for v1.0. Not recommended for adoption now.

### atlassian-api-py

- **PyPI**: [atlassian-api-py](https://pypi.org/project/atlassian-api-py/)
- **Latest release**: v0.7.0 (2026-03-19)
- **Maintenance**: Low activity. Small contributor base.
- **Products**: Jira, Confluence, Bitbucket
- **API versions**: v2
- **Auth**: Basic, PAT
- **Python**: >=3.9
- **Type annotations**: Unknown (likely minimal)
- **Async**: No
- **License**: MIT

**RaiSE relevance**: Too small and immature. No advantage over atlassian-python-api. Not recommended.

### mcp-atlassian (sooperset)

- **PyPI**: [mcp-atlassian](https://pypi.org/project/mcp-atlassian/)
- **GitHub**: [sooperset/mcp-atlassian](https://github.com/sooperset/mcp-atlassian) (4.7K stars, 103 contributors)
- **Latest release**: v0.21.0 (2026-03-02)
- **Maintenance**: Very active. Weekly releases. Large contributor base.
- **Products**: Jira, Confluence
- **API versions**: v2 + v3 (Cloud), v2 (Server/Data Center)
- **Auth**: Basic, OAuth 2.0, PAT. OAuth proxy support. Multi-user support.
- **Python**: >=3.10
- **Type annotations**: N/A (consumed as MCP server, not as library)
- **Async**: N/A (MCP protocol handles this via stdio/SSE)
- **License**: MIT

**Features (v0.21.0)**: 65+ tools, sprint management, page moves, page diffs, comment replies, markdown table rendering, selective tool enabling, SSRF protection, Kubernetes Helm chart, Docker distribution. E2E test suites (61 DC tests, 48 Cloud tests).

**Strengths**: Most active Atlassian integration project in the ecosystem. Protocol boundary (MCP) isolates RaiSE from internal API changes. Already proven in RaiSE Confluence adapter. Supports both Cloud and Data Center. Enterprise features (multi-user, SSRF protection).

**Weaknesses**: Consumed as subprocess -- adds process management overhead. JSON serialization overhead for every call. No way to extend or customize tool behavior without forking. Token verbosity (parking lot item: MCP returns ~8K tokens vs ~200 for CLI wrapper).

**RaiSE relevance**: Already the transport layer for `McpConfluenceAdapter`. The token verbosity issue was noted in parking-lot. ACLI replaced MCP for Jira (epic E494) precisely because of this overhead. Continue using for Confluence; do not revert Jira to MCP.

### Atlassian Rovo MCP Server (Official)

- **Endpoint**: `https://mcp.atlassian.com/v1/mcp` (SSE endpoint `/v1/sse` deprecated after June 30, 2026)
- **GitHub**: [atlassian/atlassian-mcp-server](https://github.com/atlassian/atlassian-mcp-server)
- **Status**: GA (Generally Available, 2026)
- **Products**: Jira, Confluence, Compass
- **Auth**: OAuth 2.1 (enterprise-grade, inherits Atlassian Cloud permissions)
- **Maintenance**: Atlassian-maintained. Enterprise SLA.

**Strengths**: First-party. Enterprise security (OAuth 2.1, admin controls for allowed clients). Semantic search across products. Permission model inherited from Atlassian Cloud. Supports Claude, ChatGPT, Cursor, VS Code, and many AI clients. No infrastructure to manage -- cloud-hosted.

**Weaknesses**: Cloud-only (no Server/Data Center). Requires Atlassian Cloud subscription. Closed-source. Less granular control than sooperset's server. May not expose all the endpoints RaiSE needs. Dependency on Atlassian's infrastructure availability.

**RaiSE relevance**: High strategic value for the Forge app and enterprise customers. The OAuth 2.1 auth model is what we need for multi-tenant deployments. Evaluate as potential replacement for sooperset mcp-atlassian once we confirm it exposes all needed operations. The `/v1/sse` deprecation timeline (June 2026) means we must use the newer `/v1/mcp` endpoint.

### Atlassian CLI (ACLI)

- **Documentation**: [developer.atlassian.com/cloud/acli](https://developer.atlassian.com/cloud/acli/guides/introduction/)
- **Status**: Official Atlassian product. Active development.
- **Products**: Jira (primary), with Rovo Dev integration
- **Auth**: OAuth 2.0, PAT, API tokens
- **Platform**: macOS, Windows, Linux binary

**Strengths**: First-party support. Clean JSON output (`--json`). Multi-site support (auth switch). Safety features (impact notifications, bulk previews). CI/CD integration guide. RaiSE has a proven, tested adapter (`AcliJiraBridge`).

**Weaknesses**: Binary distribution (not pip-installable). Jira-focused. Subprocess overhead per call. Auth switch is stateful (process-level side effect).

**RaiSE relevance**: Currently the production Jira adapter. Working well (per E494, E301 retrospectives). The subprocess model adds latency but provides clean isolation. Keep as primary Jira adapter.

### Other Notable Mentions

**atlassian_jwt_auth**: Official Atlassian package for service-to-service JWT authentication. Useful for Forge app backend authentication but not a general-purpose API client.

**asap-authentication-python**: Official Atlassian package for ASAP (Atlassian Service Authentication Protocol). Niche use case for Atlassian-internal service auth.

**Forge MCP Server**: Atlassian's MCP server specifically for Forge development knowledge. Not for Jira/Confluence data access -- provides Forge documentation and development context to coding agents. Relevant for our Forge app development workflow but not for the adapter layer.

## Current RaiSE Adapter Analysis

### What We Have

RaiSE uses a **protocol-based adapter architecture** defined in `raise_cli.adapters.protocols`:

1. **AsyncProjectManagementAdapter / ProjectManagementAdapter** -- 11 methods for Jira CRUD, batch ops, comments, search, health
2. **AsyncDocumentationTarget / DocumentationTarget** -- 5 methods for Confluence publish, get, search, health
3. **Sync wrappers** (`SyncPMAdapter`, `SyncDocsAdapter`) bridge async adapters to CLI consumption
4. **Entry point registration** via `pyproject.toml` for pluggable adapter discovery

Current concrete implementations:

| Adapter | Transport | Status | Package |
|---------|-----------|--------|---------|
| `AcliJiraAdapter` | ACLI subprocess | Production | raise-pro |
| `McpConfluenceAdapter` | mcp-atlassian via McpBridge | Production | raise-pro |

### Architecture Strengths

- **Protocol-based**: Structural typing means any class matching the method signatures works. No inheritance required.
- **Async-first**: Core protocols are async; sync is a convenience wrapper.
- **Transport-agnostic**: The protocol doesn't care if the backend is ACLI, MCP, or direct HTTP.
- **Pydantic models**: All adapter I/O uses typed Pydantic models (`IssueRef`, `IssueDetail`, `PageContent`, etc.).
- **Multi-instance**: Jira adapter supports multi-site via `jira.yaml` configuration.
- **Telemetry**: Logfire spans on ACLI bridge calls.

### Gaps and Opportunities

1. **Direct `atlassian-python-api` dependency may be vestigial**: `raise-pro` depends on `atlassian-python-api>=3.41.0` but the actual adapters use ACLI and MCP bridges. Audit whether this dependency is still needed directly.

2. **No Bitbucket adapter**: The protocol layer could support a Bitbucket adapter but none exists. Not currently needed (we use GitHub), but relevant if enterprise customers use Bitbucket.

3. **Token verbosity on Confluence**: The parking lot notes MCP returns ~8K tokens per operation vs ~200 for ACLI. This was the motivation for E494 (ACLI Jira adapter). A similar optimization path exists for Confluence if needed.

4. **No official Rovo MCP integration**: The Atlassian Rovo MCP Server (GA) could provide a single, enterprise-authenticated endpoint for both Jira and Confluence, potentially replacing both ACLI and sooperset mcp-atlassian for Cloud customers.

5. **Forge app authentication**: The Forge app (MVP deadline Apr 16, 2026) will need OAuth 2.1 / Forge auth for its backend. None of the current adapters handle this auth flow. The Rovo MCP Server or `atlassian_jwt_auth` would be the path here.

## Evidence Catalog

| ID | Source | Type | Evidence Level | URL |
|----|--------|------|----------------|-----|
| S1 | atlassian-python-api PyPI | Package registry | Very High | https://pypi.org/project/atlassian-python-api/ |
| S2 | atlassian-python-api GitHub | Repository | Very High | https://github.com/atlassian-api/atlassian-python-api |
| S3 | jira (PyJira) PyPI | Package registry | Very High | https://pypi.org/project/jira/ |
| S4 | jira GitHub | Repository | Very High | https://github.com/pycontribs/jira |
| S5 | mcp-atlassian PyPI | Package registry | Very High | https://pypi.org/project/mcp-atlassian/ |
| S6 | mcp-atlassian GitHub | Repository | Very High | https://github.com/sooperset/mcp-atlassian |
| S7 | Atlassian Rovo MCP Server announcement | Official blog | Very High | https://www.atlassian.com/blog/announcements/remote-mcp-server |
| S8 | Atlassian Rovo MCP GA announcement | Official blog | Very High | https://www.atlassian.com/blog/announcements/atlassian-rovo-mcp-ga |
| S9 | Atlassian MCP Server GitHub | Repository | Very High | https://github.com/atlassian/atlassian-mcp-server |
| S10 | Atlassian CLI documentation | Official docs | Very High | https://developer.atlassian.com/cloud/acli/guides/introduction/ |
| S11 | pyatlassian PyPI | Package registry | High | https://pypi.org/project/pyatlassian/ |
| S12 | pyatlassian documentation | ReadTheDocs | High | https://pyatlassian.readthedocs.io/en/latest/ |
| S13 | atlassian-api-py PyPI | Package registry | High | https://pypi.org/project/atlassian-api-py/ |
| S14 | Rovo MCP support docs | Official support | Very High | https://support.atlassian.com/atlassian-rovo-mcp-server/docs/getting-started-with-the-atlassian-remote-mcp-server/ |
| S15 | Forge MCP Server docs | Official docs | Very High | https://developer.atlassian.com/platform/forge/forge-mcp/ |
| S16 | jira type hints issue #689 | GitHub issue | High | https://github.com/pycontribs/jira/issues/689 |
| S17 | RaiSE E301 retrospective | Internal | Very High | (local: work/epics/e301-agent-tool-abstraction/retrospective.md) |
| S18 | RaiSE E494 design | Internal | Very High | (local: work/epics/e494-acli-jira-adapter/design.md) |
| S19 | RaiSE parking lot (token economy note) | Internal | High | (local: dev/parking-lot.md) |
| S20 | Atlassian Rovo MCP platform page | Official | Very High | https://www.atlassian.com/platform/remote-mcp-server |
| S21 | Libraries.io atlassian-python-api | Aggregator | Medium | https://libraries.io/pypi/atlassian-python-api |
| S22 | Snyk jira health analysis | Aggregator | Medium | https://snyk.io/advisor/python/jira |

## Recommendations for RaiSE

### Keep: Current Adapter Architecture (No Migration Needed)

The protocol-based, transport-agnostic architecture is sound. The two-adapter setup (ACLI for Jira, MCP for Confluence) reflects real engineering trade-offs (token economy, tool maturity). No library in the ecosystem today offers a compelling reason to rewrite.

### Keep: ACLI for Jira (AcliJiraBridge)

ACLI is first-party, actively maintained, and our adapter is battle-tested. The subprocess overhead is acceptable for CLI use. No Python library offers better Jira coverage with less friction.

### Keep: mcp-atlassian for Confluence (McpConfluenceAdapter)

sooperset's mcp-atlassian is the most active community project (4.7K stars, 103 contributors, weekly releases). It provides reliable Confluence access. The token verbosity issue is real but tolerable for Confluence operations (which are less frequent than Jira ops).

### Evaluate: Atlassian Rovo MCP Server for Forge App

For the Forge app (RAISE-760), the official Rovo MCP Server is the strategic choice:
- OAuth 2.1 authentication aligns with Forge's auth model
- Enterprise-grade (inherits Cloud permissions)
- Covers Jira + Confluence + Compass in one endpoint
- Atlassian-maintained -- no community dependency risk
- Timeline: SSE endpoint deprecated June 30, 2026 -- use `/v1/mcp`

**Action**: Prototype a `RovoMcpAdapter` that implements both `AsyncProjectManagementAdapter` and `AsyncDocumentationTarget` via the Rovo MCP endpoint. This could eventually replace both ACLI and sooperset adapters for Cloud customers.

### Audit: Remove Direct atlassian-python-api Dependency

The `raise-pro` dependency on `atlassian-python-api>=3.41.0` may be vestigial now that ACLI and MCP bridges handle all operations. If it is only used transitively (via mcp-atlassian), remove it from direct dependencies to reduce surface area.

### Do Not Adopt: PyJira, pyatlassian, atlassian-api-py

None of these offer enough advantage over the current architecture to justify migration cost:
- **PyJira**: Jira-only, no real async, minimal types
- **pyatlassian**: Too immature (v0.3.x), risk of abandonment
- **atlassian-api-py**: Too small, no advantage

### Future: Consider Building a Typed Atlassian Client

If RaiSE eventually needs a direct API client (bypassing both ACLI and MCP), the right approach would be:
- httpx-based (async-native)
- Pydantic models for all request/response types
- Generated from OpenAPI specs where available
- Auth via authlib (already a dependency)

This is a significant investment and should only be considered if both ACLI and MCP prove insufficient for the Forge app's needs. The protocol architecture makes this a drop-in replacement when needed.

### Decision Matrix

| Decision | Recommendation | Confidence | Urgency |
|----------|---------------|------------|---------|
| Keep ACLI for Jira CLI | Keep | High | N/A (stable) |
| Keep mcp-atlassian for Confluence | Keep | High | N/A (stable) |
| Evaluate Rovo MCP for Forge app | Evaluate (prototype) | Medium | High (Apr 16 deadline) |
| Audit atlassian-python-api dependency | Audit | High | Low |
| Adopt PyJira | Do not adopt | High | N/A |
| Adopt pyatlassian | Do not adopt (monitor) | High | N/A |
| Build custom typed client | Defer | Medium | Low |
