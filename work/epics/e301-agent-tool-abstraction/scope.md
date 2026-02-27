# Epic E301: Agent Tool Abstraction — Scope

> **Status:** IN PROGRESS
> **Release:** MVP (Atlassian Webinar Mar 15)
> **Branch:** `epic/e301/agent-tool-abstraction`
> **Created:** 2026-02-26
> **Absorbs:** RAISE-141 (Platform Adapters), RAISE-208 ([PRO] Jira Adapter)

## Objective

AI agents consume abstract CLI commands (`rai backlog`, `rai docs`) instead of
platform-specific APIs, eliminating the need to know Jira transition IDs,
Confluence page IDs, or adapter implementation details.

**Value:** Reduces agent token consumption ~24x per Jira session (120K → 5K tokens
measured). Eliminates daily friction of manual platform operations. Makes governance
workflows portable across PM/docs platforms. Enables skill auto-sync — lifecycle
skills drive Jira transitions automatically.

## Stories

| ID | Story | Size | Status | Description |
|----|-------|:----:|:------:|-------------|
| S301.1 | Protocols + Models | M | Done ✓ | Extended PM (11 methods) + Docs (5 methods), async primary + sync wrapper, 9 models, `_run_sync()` helper. 103 tests, 1.5x velocity. |
| S301.2 | `rai backlog` CLI group | M | Done ✓ | 7 commands (create, transition, update, link, comment, search, batch-transition). Auto-detect adapter, open-core Pattern B. 16 tests, 1.25x velocity. |
| S301.3 | McpPorterBridge + McpJiraAdapter | M | Pending | Generic McpPorterBridge (subprocess → mcporter CLI → any MCP server) with telemetry (timing, success/fail, call tracing). McpJiraAdapter maps 11 PM protocol methods to Atlassian MCP tools via bridge. Registered as entry point `rai.adapters.pm`. |
| S301.4 | `rai docs` CLI group | S | Pending | Commands: publish, get, search. Compact output. Delegates to DocumentationTarget registry. |
| S301.5 | McpConfluenceAdapter | S | Pending | Maps 5 DocumentationTarget methods to Atlassian MCP tools via McpPorterBridge. Same bridge, thin mapping layer. Registered as entry point `rai.docs.targets`. |
| S301.6 | Skill auto-sync hooks | S | Pending | Lifecycle skills (epic-start, story-start, story-close, epic-close) emit Jira transitions + comments via E248 hook system. Config from `.raise/jira.yaml` lifecycle_mapping. Graceful degradation if unconfigured. |
| S301.7 | E2E dogfood | S | Pending | Full story lifecycle on raise-commons without direct MCP calls: create story in Jira, link to epic, transition, add comments, publish doc to Confluence. Validate token reduction. |

**Total:** 7 stories (2M + 5S) — reduced from (1L + 2M + 4S) by McpPorterBridge strategy

## Scope

**In scope (MUST):**
- `rai backlog` CLI group — create, transition, update, link, comment, search, batch-transition
- `rai docs` CLI group — publish, get, search
- **McpPorterBridge** — generic subprocess bridge that invokes any MCP server tool via `mcporter` CLI, with telemetry (timing, success/fail, call tracing)
- McpJiraAdapter implementing ProjectManagementAdapter via McpPorterBridge + Atlassian MCP
- McpConfluenceAdapter implementing DocumentationTarget via McpPorterBridge + Atlassian MCP
- Compact output format (~200 tokens per operation vs ~8,000 raw MCP JSON)
- Configuration via `.raise/jira.yaml` (existing) for status mapping + mcporter config for MCP server
- Skill auto-sync — lifecycle skills drive Jira transitions automatically

**In scope (SHOULD):**
- `rai adapters check` with health detail per adapter
- `rai adapters setup jira` / `rai adapters setup confluence` — guided config wizard
- Graceful fallback when adapter not configured (log warning, continue)

**Out of scope:**
- Native httpx adapters (direct REST API) → Phase 2, swap behind same protocol when needed
- GitLab/Odoo/Linear/Azure DevOps adapters → separate epic post-validation, Gustavo for AzDO
- Bidirectional sync (webhooks, polling, conflict resolution) → Phase 2
- Custom field mapping → Phase 2
- Offline queue / pending sync for backlog → Phase 2 (pending_sync from E275 covers graph only)
- Entity properties for sync metadata → Phase 2 (E-DEMO prototype exists)
- raise-pro repo separation (RAISE-207) → deferred, adapters live in raise-commons for MVP

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
  ├──→ S301.2 ✓ (rai backlog CLI) ──→ S301.3 (bridge + McpJiraAdapter) ──→ S301.6 (auto-sync)
  │                                      │                                ╲
  └──→ S301.4 (rai docs CLI) ───────────╳──→ S301.5 (McpConfluenceAdapter) ──→ S301.7 (E2E)
                                         │                                   ╱
                                    S301.3 (bridge) ────────────────────────╯
```

**External:**
- `.raise/jira.yaml` — exists, has lifecycle_mapping + team identifiers + transition IDs
- **mcporter** (npm) — MCP-to-CLI bridge, `npx mcporter call --json <server>.<tool> ...`
- **Atlassian MCP server** — must be configured (same config as Claude Code / IDE MCP setup)
- E248 hook system — exists, used for auto-sync wiring

**New dependency (vs v1):** Node.js + npx + mcporter. Replaces direct Jira/Confluence REST API dependency.

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

2. **McpPorterBridge over httpx** (revised SES-298) — instead of implementing OAuth, pagination, rate limiting from scratch, leverage existing MCP servers via `mcporter` CLI as subprocess bridge. Auth, pagination, error handling are the MCP server's responsibility. Adapters become thin mapping layers: protocol method → MCP tool name + param/response transformation. Trade-off: requires Node.js/npx + mcporter + configured MCP server. Acceptable for MVP (controlled environments). Native httpx adapters are Phase 2 swap-in behind the same protocol.

3. **Extend existing protocols** — don't create new ones. `ProjectManagementAdapter` and `DocumentationTarget` already exist in `src/rai_cli/adapters/protocols.py`. Add methods, don't fork.

4. **Hook system for auto-sync** — E248 hooks are the right mechanism for cross-cutting concerns. Skills don't call Jira directly; they emit events, hooks handle transitions.

5. **McpPorterBridge as generic reusable infrastructure** (new, SES-298) — the bridge is not Jira/Confluence-specific. Any MCP server can be wrapped into a RaiSE adapter via the same bridge. This enables: (a) fast adapter development for any MCP-available platform, (b) built-in telemetry on all MCP calls, (c) community/marketing angle — MCPorter users are natural RaiSE early adopters.

**Bridge architecture:**
```
rai backlog transition RAISE-301 done
    │
    ▼
resolve_adapter() → McpJiraAdapter (entry point: rai.adapters.pm)
    │
    ▼
McpPorterBridge.call("atlassian", "jira_transition_issue", {issue_key, transition_id})
    │  ← telemetry: timing, success/fail, call trace
    ▼
subprocess: npx mcporter call --json atlassian.jira_transition_issue ...
    │
    ▼
Atlassian MCP server → Jira REST API
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

### New Models

```python
class IssueDetail(IssueRef):
    summary: str
    description: str
    status: str
    issue_type: str
    parent_key: str | None = None
    labels: list[str] = []
    assignee: str | None = None
    priority: str | None = None
    created: str = ""
    updated: str = ""

class IssueSummary(BaseModel):
    key: str
    summary: str
    status: str
    issue_type: str
    parent_key: str | None = None

class Comment(BaseModel):
    id: str
    body: str
    author: str
    created: str

class CommentRef(BaseModel):
    id: str
    url: str = ""

class BatchResult(BaseModel):
    succeeded: list[IssueRef] = []
    failed: list[str] = []  # key + error message

class PageContent(BaseModel):
    id: str
    title: str
    content: str  # markdown
    url: str = ""
    space_key: str = ""
    version: int = 1

class PageSummary(BaseModel):
    id: str
    title: str
    url: str = ""
    space_key: str = ""
    updated: str = ""

class AdapterHealth(BaseModel):
    name: str
    healthy: bool
    message: str = ""
    latency_ms: int | None = None
```

## Risks

| Risk | L/I | Mitigation |
|------|:---:|------------|
| Node.js/npx required for McpPorterBridge | M/M | Acceptable for MVP (dev machines). Phase 2 native httpx adapters remove this dependency. Document requirement clearly. |
| mcporter CLI interface changes | L/H | Pin mcporter version. Bridge wraps subprocess — easy to update parsing. `--json` flag provides stable structured output. |
| Subprocess overhead per MCP call | L/M | Acceptable for CLI (human-speed). Batch operations reduce call count. Phase 2 httpx eliminates overhead. |
| MCP server config must exist for adapter to work | M/M | Health check validates MCP server reachability. `rai adapters check` reports status. Clear error messages with setup guidance. |
| Rate limits still apply (MCP server → Jira API) | M/H | MCP server handles rate limiting internally. Bridge telemetry captures latency for monitoring. |
| Config complexity for new users | M/M | Sensible defaults, setup wizard (SHOULD), graceful degradation if unconfigured |
| Protocol extension breaks existing code | L/H | Backward-compatible: new methods only, existing 4 methods unchanged, runtime_checkable |

## Parking Lot

- Native httpx adapters (HttpxJiraAdapter, HttpxConfluenceAdapter) → Phase 2, swap behind same protocol for CI/server environments
- GitLab adapter via McpPorterBridge → separate epic, community contribution welcome (just mapping layer if GitLab MCP exists)
- Odoo adapter → separate epic, INVEX/InterWare use case
- Azure DevOps adapter → Gustavo (community), share ADR-033 when published
- Bidirectional sync (webhooks, polling) → Phase 2 epic, research complete in `work/research/`
- Entity properties for sync metadata → Phase 2, E-DEMO prototype available
- `rai backlog reconcile --dry-run` → Phase 2, Merkle tree comparison
- raise-pro extraction (RAISE-207) → post-MVP, when commercial packaging decided
- Custom field mapping → Phase 2, extensible via IssueSpec.metadata
- Server-side agent consuming adapters via Python SDK/HTTP API → propio agent con inferencia propia, mismos protocolos, diferente interfaz de invocación
- **GTM: MCPorter community** → users who already understand token economy are natural early adopters. Content angle: "RaiSE turns your MCP servers into governed, observable adapter operations." Post-MVP marketing epic.

## Implementation Plan

> Added by `/rai-epic-plan` — 2026-02-27
> **Revised:** SES-298 (2026-02-27) — McpPorterBridge strategy replaces httpx-direct.
> Rationale: leverage existing MCP servers via subprocess bridge, reduce S301.3 from L→M,
> S301.5 from M→S. Enables faster MVP validation + community/GTM angle.

### Sequencing Strategy

**Walking skeleton** — prove abstract backlog operations E2E against real Jira first
(highest daily friction), then extend to docs. McpPorterBridge is shared infrastructure
built in S301.3 and reused in S301.5 (compounding, PAT-E-442).

### Story Sequence

| Order | Story | Size | Dependencies | Milestone | Rationale |
|:-----:|-------|:----:|--------------|-----------|-----------|
| 1 | S301.1 — Protocols + Models | M | None | M1 | Foundation — unblocks both streams. Done ✓ |
| 2 | S301.2 — `rai backlog` CLI | M | S301.1 | M1 | CLI surface before adapter. Done ✓ |
| 3 | S301.3 — McpPorterBridge + McpJiraAdapter | M | S301.2 | M1 | Bridge infra + first concrete adapter. Proves architecture against real Jira. |
| 4 | S301.4 — `rai docs` CLI | S | S301.1 | M2 | **Parallel with S301.3.** Same pattern as S301.2 but for docs. |
| 5 | S301.5 — McpConfluenceAdapter | S | S301.3, S301.4 | M2 | Reuses McpPorterBridge (compounding). Thin mapping layer only. |
| 6 | S301.6 — Skill auto-sync hooks | S | S301.3 | M3 | **Parallel with S301.5.** Hooks wire lifecycle skills to adapter. Config in jira.yaml. |
| 7 | S301.7 — E2E dogfood | S | S301.3, S301.5 | M4 | Integration checkpoint. Full cycle without MCP calls. Validates seams. |

### Milestones

| Milestone | Stories | Success Criteria |
|-----------|---------|------------------|
| **M1: Backlog Walking Skeleton** | S301.1 ✓, S301.2 ✓, S301.3 | `rai backlog transition RAISE-XXX done` works against Jira Cloud via McpPorterBridge. `rai backlog search "project=RAISE AND status=Done"` returns compact output. McpPorterBridge telemetry captures call timing. |
| **M2: Docs MVP** | S301.4, S301.5 | `rai docs publish governance/roadmap.md` creates/updates Confluence page via McpConfluenceAdapter. `rai docs get <page-id>` returns markdown content. |
| **M3: Automation** | S301.6 | `/rai-story-start` auto-transitions Jira issue to In Progress. `/rai-story-close` auto-transitions to Done + adds retrospective comment. Graceful no-op when Jira unconfigured. |
| **M4: Epic Complete** | S301.7 + retro | Agent completes full story lifecycle with zero raw MCP calls. Token reduction ≥10x validated. Epic retrospective done. Merged to dev. |

### Parallel Work Streams

```
Time →

Stream 1 (Backlog):  S301.1 ✓ ─► S301.2 ✓ ─► S301.3 (bridge+jira) ─► S301.6 (auto-sync)
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

**Key change from v1:** S301.5 now depends on S301.3 (needs McpPorterBridge). S301.4 remains
independent and can start in parallel with S301.3.

### Progress Tracking

| Story | Size | Status | Actual | Velocity | Notes |
|-------|:----:|:------:|:------:|:--------:|-------|
| S301.1 — Protocols + Models | M | Done ✓ | 60min | 1.5x | 4 protocols, 9 models, 2 wrappers, 103 tests. |
| S301.2 — `rai backlog` CLI | M | Done ✓ | ~60min | 1.25x | 7 commands, clean rewrite, 16 tests. |
| S301.3 — McpPorterBridge + McpJiraAdapter | M | Pending | — | — | Bridge infra + Jira mapping |
| S301.4 — `rai docs` CLI | S | Pending | — | — | Parallel with S301.3 |
| S301.5 — McpConfluenceAdapter | S | Pending | — | — | Reuses bridge from S301.3 |
| S301.6 — Skill auto-sync hooks | S | Pending | — | — | Parallel with S301.5 |
| S301.7 — E2E dogfood | S | Pending | — | — | Integration checkpoint |

### Sequencing Risks

| Risk | L/I | Mitigation |
|------|:---:|------------|
| mcporter not installed / Node.js missing | M/M | Health check in bridge validates prereqs. Clear error message with install command. |
| MCP server config missing or broken | M/M | Bridge.health() tests connectivity before first real call. `rai adapters check` for diagnosis. |
| Parallel streams diverge in patterns | L/L | S301.3 establishes bridge pattern. S301.5 reuses exact same bridge (compounding, PAT-E-442). Risk lower than v1 because bridge is shared code. |
