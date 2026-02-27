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
| S301.1 | Protocols + Models | S | Pending | Extend ProjectManagementAdapter and DocumentationTarget with real-world operations: batch, comments, links, search, read. New models: IssueDetail, IssueSummary, Comment, BatchResult, PageContent, PageSummary. |
| S301.2 | `rai backlog` CLI group | M | Pending | Commands: create, transition, update, link, comment, search, batch-transition. Compact output (~200 tokens vs 8K raw MCP). Delegates to adapter registry. |
| S301.3 | JiraAdapter | L | Pending | Concrete ProjectManagementAdapter using httpx + Jira REST API. Config from `.raise/jira.yaml` (already exists with lifecycle_mapping, team identifiers, transition IDs). Rate limiting, field filtering. |
| S301.4 | `rai docs` CLI group | S | Pending | Commands: publish, get, search. Compact output. Delegates to DocumentationTarget registry. |
| S301.5 | ConfluenceTarget | M | Pending | Concrete DocumentationTarget using httpx + Confluence REST API. Page ID mapping, space routing, template support. Config from `.raise/adapters/confluence.yaml`. |
| S301.6 | Skill auto-sync hooks | S | Pending | Lifecycle skills (epic-start, story-start, story-close, epic-close) emit Jira transitions + comments via E248 hook system. Config from `.raise/jira.yaml` lifecycle_mapping. Graceful degradation if unconfigured. |
| S301.7 | E2E dogfood | S | Pending | Full story lifecycle on raise-commons without direct MCP calls: create story in Jira, link to epic, transition, add comments, publish doc to Confluence. Validate token reduction. |

**Total:** 7 stories (1S + 1L + 2M + 3S)

## Scope

**In scope (MUST):**
- `rai backlog` CLI group — create, transition, update, link, comment, search, batch-transition
- `rai docs` CLI group — publish, get, search
- JiraAdapter implementing extended ProjectManagementAdapter protocol
- ConfluenceTarget implementing extended DocumentationTarget protocol
- Compact output format (~200 tokens per operation vs ~8,000 raw MCP JSON)
- Configuration via `.raise/jira.yaml` (existing) and `.raise/adapters/confluence.yaml` (new)
- Skill auto-sync — lifecycle skills drive Jira transitions automatically

**In scope (SHOULD):**
- `rai adapters check` with health detail per adapter
- `rai adapters setup jira` / `rai adapters setup confluence` — guided config wizard
- Graceful fallback when adapter not configured (log warning, continue)

**Out of scope:**
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
S301.1 (protocols + models)
  ├──→ S301.2 (rai backlog CLI) ──→ S301.3 (JiraAdapter) ──→ S301.6 (auto-sync hooks)
  │                                                      ╲
  └──→ S301.4 (rai docs CLI) ──→ S301.5 (ConfluenceTarget) ──→ S301.7 (E2E dogfood)
                                                           ╱
                                              S301.3 ─────╯
```

**External:**
- `.raise/jira.yaml` — exists, has lifecycle_mapping + team identifiers + transition IDs
- Jira Cloud REST API (v3) — OAuth env vars already configured in `.env`
- Confluence REST API — OAuth env vars already configured in `.env`
- E248 hook system — exists, used for auto-sync wiring

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

2. **httpx over atlassian-python-api** — lighter dependency, full control over rate limiting and field filtering. E-DEMO validated that entity properties API needs raw REST anyway.

3. **Extend existing protocols** — don't create new ones. `ProjectManagementAdapter` and `DocumentationTarget` already exist in `src/rai_cli/adapters/protocols.py`. Add methods, don't fork.

4. **Hook system for auto-sync** — E248 hooks are the right mechanism for cross-cutting concerns. Skills don't call Jira directly; they emit events, hooks handle transitions.

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
| Jira REST API rate limits (points-based, changing Mar 2) | M/H | Field filtering, batch operations, X-RateLimit-Remaining monitoring, token bucket |
| httpx dependency conflicts with existing packages | L/M | httpx already in use (E275 ApiGraphBackend), no new dependency |
| Config complexity for new users | M/M | Sensible defaults, setup wizard (SHOULD), graceful degradation if unconfigured |
| Protocol extension breaks existing code | L/H | Backward-compatible: new methods only, existing 4 methods unchanged, runtime_checkable |

## Parking Lot

- GitLab adapter → separate epic, community contribution welcome
- Odoo adapter → separate epic, INVEX/InterWare use case
- Azure DevOps adapter → Gustavo (community), share ADR-033 when published
- Bidirectional sync (webhooks, polling) → Phase 2 epic, research complete in `work/research/`
- Entity properties for sync metadata → Phase 2, E-DEMO prototype available
- `rai backlog reconcile --dry-run` → Phase 2, Merkle tree comparison
- raise-pro extraction (RAISE-207) → post-MVP, when commercial packaging decided
- Custom field mapping → Phase 2, extensible via IssueSpec.metadata
