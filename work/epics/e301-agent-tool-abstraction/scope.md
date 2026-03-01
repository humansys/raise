# Epic E301: Agent Tool Abstraction — Scope

> **Status:** IN PROGRESS
> **Release:** MVP (Atlassian Webinar Mar 15)
> **Branch:** `epic/e301/agent-tool-abstraction`
> **Created:** 2026-02-26
> **Revised:** SES-298 (2026-02-27) — MCP SDK bridge strategy (v3, research-grounded)
> **Absorbs:** RAISE-141 (Platform Adapters), RAISE-208 ([PRO] Jira Adapter)

## Objective

AI agents consume abstract CLI commands (`rai backlog`, `rai docs`) instead of
platform-specific APIs, eliminating the need to know Jira transition IDs,
Confluence page IDs, or adapter implementation details.

**Value:** Reduces agent token consumption ~24x per Jira session (120K → 5K tokens
measured). Eliminates daily friction of manual platform operations. Makes governance
workflows portable across PM/docs platforms. Enables skill auto-sync — lifecycle
skills drive Jira transitions automatically.

**Strategic value (SES-298):** The McpBridge is a generic governance layer over the
MCP ecosystem (50+ DevSecOps servers, 17K+ total). RaiSE becomes the only framework
combining developer governance + MCP tool abstraction + telemetry. Enables future
adapters for GitHub, SonarQube, Grafana, Slack, AWS, Terraform, etc. — each as a
thin mapping layer (~50-100 LOC) over existing MCP servers.

## Stories

| ID | Story | Size | Status | Description |
|----|-------|:----:|:------:|-------------|
| S301.1 | Protocols + Models | M | Done ✓ | Extended PM (11 methods) + Docs (5 methods), async primary + sync wrapper, 9 models, `_run_sync()` helper. 103 tests, 1.5x velocity. |
| S301.2 | `rai backlog` CLI group | M | Done ✓ | 7 commands (create, transition, update, link, comment, search, batch-transition). Auto-detect adapter, open-core Pattern B. 16 tests, 1.25x velocity. |
| S301.3 | McpBridge + McpJiraAdapter | M | Done ✓ | Generic McpBridge (async, stdio, telemetry). McpJiraAdapter maps 11 PM methods to mcp-atlassian. Auto-wrap async→sync. Entry point registered. Dual-format parsers (sooperset + raw Jira). D6: adapter for domain logic, `rai mcp call` for pass-through. 44 tests, 0.8x velocity. |
| S301.4 | `rai docs` CLI group | S | Pending | Commands: publish, get, search. Compact output. Delegates to DocumentationTarget registry. |
| S301.5 | McpConfluenceAdapter | S | Pending | Maps 5 DocumentationTarget methods to `mcp-atlassian` Confluence tools via McpBridge. Same bridge, thin mapping layer. Registered as entry point `rai.docs.targets`. |
| S301.6 | Skill auto-sync hooks | S | Pending | Lifecycle skills (epic-start, story-start, story-close, epic-close) emit Jira transitions + comments via E248 hook system. Config from `.raise/jira.yaml` lifecycle_mapping. Graceful degradation if unconfigured. |
| S301.7 | E2E dogfood | S | Pending | Full story lifecycle on raise-commons without direct MCP calls: create story in Jira, link to epic, transition, add comments, publish doc to Confluence. Validate token reduction. |

**Total:** 7 stories (2M + 5S)

## Scope

**In scope (MUST):**
- `rai backlog` CLI group — create, transition, update, link, comment, search, batch-transition
- `rai docs` CLI group — publish, get, search
- **McpBridge** — async Python bridge using official MCP SDK (`ClientSession.call_tool()`) to invoke any MCP server tool, with RaiSE telemetry (timing, success/fail, call tracing). Pure Python, no Node.js dependency.
- McpJiraAdapter implementing ProjectManagementAdapter via McpBridge + `mcp-atlassian`
- McpConfluenceAdapter implementing DocumentationTarget via McpBridge + `mcp-atlassian`
- Compact output format (~200 tokens per operation vs ~8,000 raw MCP JSON)
- Configuration via `.raise/jira.yaml` (existing) for status mapping + MCP server command config
- Skill auto-sync — lifecycle skills drive Jira transitions automatically

**In scope (SHOULD):**
- `rai adapters check` with health detail per adapter
- `rai adapters setup jira` / `rai adapters setup confluence` — guided config wizard
- Graceful fallback when adapter not configured (log warning, continue)

**Out of scope:**
- Native httpx/REST adapters → Phase 2, swap behind same protocol for CI/server environments
- Additional MCP adapters (GitHub, SonarQube, Grafana, Slack, etc.) → separate epics, enabled by McpBridge
- Bidirectional sync (webhooks, polling, conflict resolution) → Phase 2
- Custom field mapping → Phase 2
- Offline queue / pending sync for backlog → Phase 2
- Entity properties for sync metadata → Phase 2
- raise-pro repo separation (RAISE-207) → deferred, adapters live in raise-commons for MVP
- `logfire` full SDK auto-instrumentation (`instrument_pydantic_ai()`) → Phase 2 when PydanticAI agent layer is adopted

## Done Criteria

**Per story:**
- [ ] Code with type annotations
- [ ] Tests passing (TDD, red-green-refactor)
- [ ] Quality checks pass (ruff, pyright)
- [ ] Retrospective complete

**Epic complete:**
- [ ] All stories complete (S301.1–S301.7)
- [ ] `rai backlog transition RAISE-XXX done` works against Jira Cloud
- [ ] `rai docs publish governance/roadmap.md` publishes to Confluence
- [ ] Lifecycle skills auto-transition Jira issues (story-start → In Progress, story-close → Done)
- [ ] Agent (Rai) completes a full story lifecycle without raw MCP calls
- [ ] Token reduction validated (≥10x vs raw MCP for equivalent operations)
- [ ] Epic retrospective done
- [ ] Merged to `dev`

## Dependencies

```
S301.1 ✓ (protocols + models)
  ├──→ S301.2 ✓ (rai backlog CLI) ──→ S301.3 ✓ (McpBridge + McpJiraAdapter) ──→ S301.6 (auto-sync)
  │                                      │                                    ╲
  └──→ S301.4 (rai docs CLI) ───────────╳──→ S301.5 (McpConfluenceAdapter) ──→ S301.7 (E2E)
                                         │                                     ╱
                                    S301.3 (bridge) ──────────────────────────╯
```

**External:**
- `.raise/jira.yaml` — exists, has lifecycle_mapping + team identifiers + transition IDs
- **`mcp` Python SDK** (v1.26.0, PyPI) — `ClientSession` for async tool invocation via stdio/HTTP
- **`mcp-atlassian`** (v0.20.1, PyPI) — Jira + Confluence MCP server (65 tools, 4.4K stars)
- E248 hook system — exists, used for auto-sync wiring

**New dependencies (vs v1 httpx plan):** `mcp` SDK (pip), `mcp-atlassian` as MCP server process.
Replaces: httpx direct REST calls, OAuth implementation, pagination logic, rate limiting code.

## Architecture

| Decision | ADR | Summary |
|----------|-----|---------|
| Open-core adapter architecture | ADR-033 | Protocol + entry points for PM adapters |
| Governance extensibility | ADR-034 | Schema + Parser + DocumentationTarget protocols |
| KnowledgeGraphBackend | ADR-036 | Graph storage abstraction (precedent pattern) |
| TierContext | ADR-037 | Tier detection + capability-aware enrichment |

> Problem Brief: N/A — organic need validated by daily friction (SES-295 measured 120K tokens for 20 MCP calls)

**Key architecture decisions for this epic:**

1. **Adapters in raise-commons (not raise-pro)** — raise-pro repo doesn't exist yet (RAISE-207 deferred). Adapters live alongside CLI for MVP. Extract to raise-pro later.

2. **MCP Python SDK bridge over httpx** (revised SES-298, research-grounded) — instead of implementing OAuth, pagination, rate limiting from scratch, use the official MCP Python SDK (`ClientSession.call_tool()`) to invoke existing MCP servers. The MCP server handles auth, pagination, error handling. Adapters become thin mapping layers: protocol method → MCP tool name + param/response transformation. Pure Python, async-native, no Node.js dependency. Evidence: 16 sources triangulated, see `work/research/mcp-bridge-strategy/evidence-catalog.md`.

3. **Extend existing protocols** — don't create new ones. `ProjectManagementAdapter` and `DocumentationTarget` already exist in `src/rai_cli/adapters/protocols.py`. Add methods, don't fork.

4. **Hook system for auto-sync** — E248 hooks are the right mechanism for cross-cutting concerns. Skills don't call Jira directly; they emit events, hooks handle transitions.

5. **McpBridge as generic reusable infrastructure** (new, SES-298) — the bridge is not Jira/Confluence-specific. Any MCP server can be wrapped into a RaiSE adapter via the same bridge. 50+ DevSecOps MCP servers exist (GitHub 27K stars, AWS 8K, Grafana 2.4K, etc.). Each future adapter is a thin mapping layer (~50-100 LOC) over an existing MCP server. Enables governed, observable, telemetry-enriched access to the entire MCP ecosystem.

**Bridge architecture:**
```
rai backlog transition RAISE-301 done
    │
    ▼
resolve_adapter() → McpJiraAdapter (entry point: rai.adapters.pm)
    │
    ▼
McpBridge.call("mcp-atlassian", "jira_transition_issue", {issue_key, transition_id})
    │  ← telemetry: timing, success/fail, call trace
    ▼
MCP Python SDK: ClientSession.call_tool() via stdio transport
    │
    ▼
mcp-atlassian server process → Jira REST API
```

**Why MCP SDK over MCPorter (research decision):**
- MCPorter requires Node.js/npx — adds non-Python dependency to Python project
- MCP Python SDK v1.26.0 is official, stable, 21K stars, async-native
- FastMCP Client (23K stars) is alternative but adds extra dependency
- `mcp-atlassian` internally wraps `atlassian-python-api` — if MCP bridge ever needs replacing, direct library path exists
- No mature Python CLI equivalent to MCPorter — the Python path is library-based
- See `work/research/mcp-bridge-strategy/evidence-catalog.md` for full analysis

**Ecosystem enablement (future epics):**
```
McpBridge (~150 LOC, telemetry, async)
  ├── McpJiraAdapter        ← E301 (this epic)
  ├── McpConfluenceAdapter  ← E301 (this epic)
  ├── McpGitHubAdapter      ← future (GitHub MCP: 27K stars, 50+ tools, official)
  ├── McpSonarQubeAdapter   ← future (SonarQube MCP: official, quality gates)
  ├── McpGrafanaAdapter     ← future (Grafana MCP: 2.4K stars, dashboards/alerts)
  ├── McpSlackAdapter       ← future (Slack MCP: 1.4K stars, notifications)
  ├── McpSnykAdapter        ← future (Snyk MCP: official, security scanning)
  ├── McpTerraformAdapter   ← future (Terraform MCP: official, IaC governance)
  ├── McpK8sAdapter         ← future (K8s MCP: Red Hat, 1.2K stars)
  ├── McpAzDevOpsAdapter    ← future (Azure DevOps MCP: official, 1.3K stars)
  └── ...any MCP server
```

## Protocol Contracts (Extended)

### ProjectManagementAdapter (extended from ADR-033)

```python
class ProjectManagementAdapter(Protocol):
    # CRUD
    def create_issue(self, project_key: str, issue: IssueSpec) -> IssueRef: ...
    def get_issue(self, key: str) -> IssueDetail: ...
    def update_issue(self, key: str, fields: dict[str, Any]) -> IssueRef: ...
    def transition_issue(self, key: str, status: str) -> IssueRef: ...

    # Batch
    def batch_transition(self, keys: list[str], status: str) -> BatchResult: ...

    # Relationships
    def link_to_parent(self, child_key: str, parent_key: str) -> None: ...
    def link_issues(self, source: str, target: str, link_type: str) -> None: ...

    # Comments
    def add_comment(self, key: str, body: str) -> CommentRef: ...
    def get_comments(self, key: str, limit: int = 10) -> list[Comment]: ...

    # Query
    def search(self, query: str, limit: int = 50) -> list[IssueSummary]: ...

    # Health
    def health(self) -> AdapterHealth: ...
```

### DocumentationTarget (extended from ADR-034)

```python
class DocumentationTarget(Protocol):
    def can_publish(self, doc_type: str, metadata: dict[str, Any]) -> bool: ...
    def publish(self, doc_type: str, content: str, metadata: dict[str, Any]) -> PublishResult: ...
    def get_page(self, identifier: str) -> PageContent: ...
    def search(self, query: str, limit: int = 10) -> list[PageSummary]: ...
```

## Risks

| Risk | L/I | Mitigation |
|------|:---:|------------|
| MCP SDK async complexity in sync CLI | L/M | `_run_sync()` helper already exists from S301.1. `SyncPMAdapter` wraps async adapter for CLI. Proven pattern. |
| `mcp-atlassian` server process lifecycle | M/M | Bridge manages server subprocess start/stop per session. Health check validates before first call. |
| MCP SDK v2 breaking changes | L/H | Pin `mcp>=1.26,<2`. v2 in pre-alpha, v1.x receives security fixes. Migration path when v2 stabilizes. |
| `mcp-atlassian` internal API instability | L/M | We consume it as MCP server (protocol boundary), not as library. MCP tool names are the contract. |
| MCP server config must exist for adapter to work | M/M | Health check validates server reachability. `rai adapters check` reports status. Clear error messages with setup guidance. |
| Rate limits still apply (MCP server → Jira API) | M/H | MCP server handles rate limiting internally. Bridge telemetry captures latency for monitoring. |
| Config complexity for new users | M/M | Sensible defaults, setup wizard (SHOULD), graceful degradation if unconfigured |
| Protocol extension breaks existing code | L/H | Backward-compatible: new methods only, existing 4 methods unchanged, runtime_checkable |

## Parking Lot

- Native httpx/REST adapters → Phase 2, swap behind same protocol for CI/server environments
- Additional MCP adapters (GitHub, SonarQube, Grafana, Slack, Snyk, Terraform, K8s, AWS, Azure DevOps) → separate epics, each is a thin mapping layer over existing MCP server
- FastMCP Client as alternative to official SDK → evaluate if SDK proves cumbersome
- `atlassian-python-api` direct path → fallback if MCP bridge approach has fundamental issues
- Anthropic filesystem-wrapper pattern (98.7% token reduction, F5) → Phase 2 enhancement
- Sentry subagent bundling pattern (95% token reduction, F6) → Phase 2 for skill optimization
- OTel semantic conventions for agent telemetry (F9) → Phase 2 when standards stabilize
- Bidirectional sync (webhooks, polling) → Phase 2 epic
- Entity properties for sync metadata → Phase 2
- `rai backlog reconcile --dry-run` → Phase 2, Merkle tree comparison
- raise-pro extraction (RAISE-207) → post-MVP
- Custom field mapping → Phase 2, extensible via IssueSpec.metadata
- Server-side agent consuming adapters via Python SDK/HTTP API
- **GTM: MCP governance community** → developers who use MCP servers are natural early adopters. Content angle: "RaiSE turns your MCP servers into governed, observable adapter operations." Post-MVP marketing epic. MCPorter, mcp-cli, FastMCP communities as targets.

## Research Artifacts

| Artifact | Path | Sources |
|----------|------|---------|
| MCP Bridge Strategy — Evidence Catalog | `work/research/mcp-bridge-strategy/evidence-catalog.md` | 16 sources, 4 research streams |
| DevSecOps MCP Ecosystem | SES-298 research stream 5 | 50+ servers cataloged, 25+ sources |

## Implementation Plan

> Added by `/rai-epic-plan` — 2026-02-27
> **Revised:** SES-298 v3 (2026-02-27) — MCP Python SDK bridge (research-grounded).
> Replaces: v1 (httpx-direct), v2 (McpPorterBridge/Node.js).

### Sequencing Strategy

**Walking skeleton** — prove abstract backlog operations E2E against real Jira first
(highest daily friction), then extend to docs. McpBridge is shared infrastructure
built in S301.3 and reused in S301.5 (compounding, PAT-E-442).

### Story Sequence

| Order | Story | Size | Dependencies | Milestone | Rationale |
|:-----:|-------|:----:|--------------|-----------|-----------|
| 1 | S301.1 — Protocols + Models | M | None | M1 | Foundation — unblocks both streams. Done ✓ |
| 2 | S301.2 — `rai backlog` CLI | M | S301.1 | M1 | CLI surface before adapter. Done ✓ |
| 3 | S301.3 — McpBridge + McpJiraAdapter | M | S301.2 | M1 | Bridge infra + first concrete adapter. Proves architecture against real Jira. Done ✓ |
| 4 | S301.4 — `rai docs` CLI | S | S301.1 | M2 | **Parallel with S301.3.** Same pattern as S301.2 but for docs. |
| 5 | S301.5 — McpConfluenceAdapter | S | S301.3, S301.4 | M2 | Reuses McpBridge (compounding). Thin mapping layer only. |
| 6 | S301.6 — Skill auto-sync hooks | S | S301.3 | M3 | **Parallel with S301.5.** Hooks wire lifecycle skills to adapter. |
| 7 | S301.7 — E2E dogfood | S | S301.3, S301.5 | M4 | Integration checkpoint. Full cycle without MCP calls. |

### Milestones

| Milestone | Stories | Success Criteria |
|-----------|---------|------------------|
| **M1: Backlog Walking Skeleton** | S301.1 ✓, S301.2 ✓, S301.3 ✓ | `rai backlog transition RAISE-XXX done` works against Jira Cloud via McpBridge. Telemetry captures call timing. **COMPLETE.** |
| **M2: Docs MVP** | S301.4, S301.5 | `rai docs publish governance/roadmap.md` creates/updates Confluence page. `rai docs get <page-id>` returns markdown. |
| **M3: Automation** | S301.6 | `/rai-story-start` auto-transitions to In Progress. `/rai-story-close` auto-transitions to Done. Graceful no-op when unconfigured. |
| **M4: Epic Complete** | S301.7 + retro | Full story lifecycle with zero raw MCP calls. Token reduction ≥10x validated. Merged to dev. |

### Parallel Work Streams

```
Time →

Stream 1 (Backlog):  S301.1 ✓ ─► S301.2 ✓ ─► S301.3 ✓ (bridge+jira) ─► S301.6 (auto-sync)
                                                ║                          │
                                    ═══════════M1══════                   M3
                                                ║                          │
Stream 2 (Docs):                    S301.4 ─────╫──► S301.5 (confluence) ──┤
                                                ║         │                │
                                               M1    ════M2═══            │
                                                                           ▼
Integration:                                                          S301.7 (E2E)
                                                                      ════M4════
```

### Progress Tracking

| Story | Size | Status | Actual | Velocity | Notes |
|-------|:----:|:------:|:------:|:--------:|-------|
| S301.1 — Protocols + Models | M | Done ✓ | 60min | 1.5x | 4 protocols, 9 models, 2 wrappers, 103 tests. |
| S301.2 — `rai backlog` CLI | M | Done ✓ | ~60min | 1.25x | 7 commands, clean rewrite, 16 tests. |
| S301.3 — McpBridge + McpJiraAdapter | M | Done ✓ | 150min | 0.8x | Bridge + adapter + auto-wrap + smoke test. 44 tests. PAT-E-565/566/567. |
| S301.4 — `rai docs` CLI | S | Pending | — | — | Parallel with S301.3 |
| S301.5 — McpConfluenceAdapter | S | Pending | — | — | Reuses bridge from S301.3 |
| S301.6 — Skill auto-sync hooks | S | Pending | — | — | Parallel with S301.5 |
| S301.7 — E2E dogfood | S | Pending | — | — | Integration checkpoint |

### Sequencing Risks

| Risk | L/I | Mitigation |
|------|:---:|------------|
| McpBridge async complexity | L/M | `_run_sync()` proven in S301.1. Bridge is ~100-150 LOC wrapping ClientSession. |
| MCP server config missing | M/M | Bridge.health() tests connectivity. `rai adapters check` for diagnosis. |
| Parallel streams diverge in patterns | L/L | S301.3 establishes bridge pattern. S301.5 reuses exact same bridge (PAT-E-442). |
