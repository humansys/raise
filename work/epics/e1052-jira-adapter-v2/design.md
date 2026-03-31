# E1052: Jira Adapter v2 — Design

## Gemba (Current State)

### Files to CREATE (raise-cli)

```
packages/raise-cli/src/raise_cli/adapters/
├── jira_client.py          # ~150 LOC — wraps atlassian.Jira
├── jira_config.py          # ~80 LOC — Pydantic for jira.yaml
├── jira_adapter.py         # ~200 LOC — PythonApiJiraAdapter
└── jira_exceptions.py      # ~30 LOC — typed exception hierarchy

packages/raise-cli/src/raise_cli/hooks/
└── backlog_sync.py         # ~40 LOC — generalized lifecycle hook
```

### Files to DELETE

```
packages/raise-pro/src/rai_pro/adapters/
├── acli_jira.py            # 417 LOC
└── acli_bridge.py          # 210 LOC

packages/raise-pro/src/rai_pro/hooks/
└── jira_sync.py            # 128 LOC

packages/raise-pro/src/rai_pro/providers/jira/
├── __init__.py             # exports
├── client.py               # ~200 LOC (OAuth, rate limiter)
├── models.py               # ~100 LOC (JiraEpic, JiraStory)
├── exceptions.py           # ~50 LOC
├── properties.py           # ~80 LOC (entity properties)
└── sync_state.py           # ~80 LOC (bidirectional sync state)
```

### Files to MODIFY

```
packages/raise-cli/pyproject.toml       # [atlassian] extra, entry points
packages/raise-pro/pyproject.toml       # remove jira entry point, hook, deps
packages/raise-cli/src/raise_cli/adapters/__init__.py  # exports
```

## Target Components

### JiraClient (`jira_client.py`)

Pattern: identical to `confluence_client.py` (E1051 S1051.1).

```python
class JiraClient:
    """Thin wrapper over atlassian.Jira with auth, errors, multi-instance."""

    def __init__(self, url: str, username: str, token: str) -> None: ...

    # Issue CRUD
    def get_issue(self, key: str) -> dict[str, Any]: ...
    def create_issue(self, fields: dict[str, Any]) -> dict[str, Any]: ...
    def update_issue(self, key: str, fields: dict[str, Any]) -> dict[str, Any]: ...
    def transition_issue(self, key: str, transition_id: str) -> None: ...
    def get_transitions(self, key: str) -> list[dict[str, Any]]: ...

    # Search
    def jql(self, query: str, limit: int = 50) -> list[dict[str, Any]]: ...

    # Relationships
    def create_link(self, source: str, target: str, link_type: str) -> None: ...
    def set_parent(self, child: str, parent: str) -> None: ...

    # Comments
    def add_comment(self, key: str, body: str) -> dict[str, Any]: ...
    def get_comments(self, key: str, limit: int = 10) -> list[dict[str, Any]]: ...

    # Health
    def server_info(self) -> dict[str, Any]: ...

    @classmethod
    def from_config(cls, config: JiraConfig, instance: str | None = None) -> JiraClient: ...
```

**Auth resolution:** `JIRA_URL`, `JIRA_USERNAME`, `JIRA_API_TOKEN` from env.
Config has `instances[name].site` for URL; email in env or config.

**Error normalization:** `atlassian.errors` → `JiraApiError`, `JiraAuthError`, `JiraNotFoundError`.

**Key pattern (from E1051):** `backoff_and_retry=True` on the `atlassian.Jira` constructor.

### JiraConfig (`jira_config.py`)

```python
class JiraInstance(BaseModel, frozen=True):
    site: str
    email: str = ""

class JiraProject(BaseModel, frozen=True):
    instance: str
    name: str = ""
    category: str = ""
    components: list[str] = []

class JiraConfig(BaseModel, frozen=True):
    default_instance: str
    instances: dict[str, JiraInstance]
    projects: dict[str, JiraProject] = {}

    @classmethod
    def load(cls, root: Path | None = None) -> JiraConfig: ...

    def resolve_instance(self, project_key: str) -> JiraInstance: ...
    def resolve_site(self, project_key: str) -> str: ...
```

**Backwards compat:** Accepts current `jira.yaml` format. Fields like `workflow`,
`team`, `issue_types` ignored by config model (read by other consumers).

### PythonApiJiraAdapter (`jira_adapter.py`)

```python
class PythonApiJiraAdapter:
    """Jira adapter via atlassian-python-api.

    Implements AsyncProjectManagementAdapter (structural typing).
    """

    def __init__(self, project_root: Path | None = None) -> None:
        config = JiraConfig.load(project_root)
        self._config = config
        self._clients: dict[str, JiraClient] = {}  # lazy per-instance

    def _client_for(self, project_key: str) -> JiraClient:
        """Lazy client resolution: project_key → instance → cached client."""
        ...

    # 11 protocol methods delegating to JiraClient
    async def create_issue(self, project_key: str, issue: IssueSpec) -> IssueRef: ...
    async def get_issue(self, key: str) -> IssueDetail: ...
    async def update_issue(self, key: str, fields: dict[str, Any]) -> IssueRef: ...
    async def transition_issue(self, key: str, status: str) -> IssueRef: ...
    async def batch_transition(self, keys: list[str], status: str) -> BatchResult: ...
    async def search(self, query: str, limit: int = 50) -> list[IssueSummary]: ...
    async def link_to_parent(self, child_key: str, parent_key: str) -> None: ...
    async def link_issues(self, source: str, target: str, link_type: str) -> None: ...
    async def add_comment(self, key: str, body: str) -> CommentRef: ...
    async def get_comments(self, key: str, limit: int = 10) -> list[Comment]: ...
    async def health(self) -> AdapterHealth: ...
```

**Lazy client cache:** One `JiraClient` per instance, created on first use.
Multi-instance routing: `project_key → config.resolve_instance() → cached client`.

**Status resolution:** `transition_issue` receives a status name ("in-progress"),
queries `get_transitions()` to find the matching transition ID, then executes.
No hardcoded IDs — always live lookup.

**Response parsing:** Jira REST API returns nested format (`fields.summary`,
`fields.status.name`). Same parsing as current `_extract_issue_fields()`.

### JiraExceptions (`jira_exceptions.py`)

```python
class JiraAdapterError(Exception): ...
class JiraApiError(JiraAdapterError):
    status_code: int
class JiraAuthError(JiraAdapterError): ...
class JiraNotFoundError(JiraAdapterError): ...
```

Pattern: identical to `confluence_exceptions.py`.

### BacklogSyncHook (`backlog_sync.py`)

```python
_CONVENTION: dict[str, str] = {
    "story_start": "in-progress",
    "story_close": "done",
    "epic_start": "in-progress",
    "epic_close": "done",
    "bug_start": "in-progress",
    "bug_close": "done",
}

class BacklogSyncHook:
    events: ClassVar[list[str]] = ["work:start", "work:close"]
    priority: ClassVar[int] = -10

    def handle(self, event: HookEvent) -> HookResult:
        if not isinstance(event, (WorkStartEvent, WorkCloseEvent)):
            return HookResult(status="ok")
        if not event.issue_key:
            return HookResult(status="ok")
        action = "start" if isinstance(event, WorkStartEvent) else "close"
        key = f"{event.work_type}_{action}"
        status = _CONVENTION.get(key)
        if not status:
            return HookResult(status="ok")
        adapter = resolve_adapter(None)
        adapter.transition_issue(event.issue_key, status)
        return HookResult(status="ok")
```

~40 LOC. No config file. No Jira import. Works with any PM adapter.

## Entry Points Migration

### raise-cli/pyproject.toml

```toml
[project.optional-dependencies]
atlassian = ["atlassian-python-api>=3.41.0"]

[project.entry-points."rai.adapters.pm"]
jira = "raise_cli.adapters.jira_adapter:PythonApiJiraAdapter"

[project.entry-points."rai.hooks"]
backlog-sync = "raise_cli.hooks.backlog_sync:BacklogSyncHook"
```

### raise-pro/pyproject.toml (removals)

```diff
-[project.entry-points."rai.adapters.pm"]
-jira = "rai_pro.adapters.acli_jira:AcliJiraAdapter"

-[project.entry-points."rai.hooks"]
-jira-sync = "rai_pro.hooks.jira_sync:JiraSyncHook"
```

## Key Patterns Carried Forward

| Pattern | Source | Applied in |
|---------|--------|------------|
| `backoff_and_retry=True` | PAT-E-589 (E1051) | JiraClient constructor |
| `from_config()` classmethod | ConfluenceClient | JiraClient |
| Module-level Path constant as test seam | PAT-E-589 | JiraConfig.load() |
| Typed exceptions with isinstance dispatch | PAT (E1051) | JiraExceptions |
| Lazy client cache per instance | New (multi-instance perf) | PythonApiJiraAdapter |

## Architecture Review Pre-Check (H1-H16)

| Heuristic | Status | Notes |
|-----------|--------|-------|
| H1 Single Implementation | OK | Second PM adapter (alongside FilesystemPMAdapter) |
| H2 Wrapper Without Logic | OK | JiraClient adds auth, errors, multi-instance |
| H6 Indirection Depth | IMPROVED | 4 layers → 3 (removed subprocess) |
| H7 Abstraction-to-LOC | OK | ~500 LOC logic, ~30 LOC scaffolding |
| H8 Config Over Convention | OK | Hook uses convention; adapter uses live lookup |
| H9 Semantic Duplication | FIXED | Unified `[atlassian]` dep |
| H10 Pattern Duplication | FIXED | Same pattern as Confluence |
| H13 Orphaned Abstractions | OK | No new protocols; consuming existing ones |
