---
story_id: S-DEMO.3
title: JIRA Client (Bidirectional)
epic: E-DEMO
status: design
owner: Emilio + Rai
created: 2026-02-14
story_points: 3
complexity: moderate
---

# Design: JIRA Client (Bidirectional)

## Problem

Enable bidirectional workflow orchestration between RaiSE and JIRA by providing a clean, type-safe client that can:
- **Read** epics and stories from JIRA (pull operations)
- **Write** stories to JIRA under a parent epic (push operations)
- Handle OAuth authentication, rate limiting, and field filtering

Without this client, the demo workflow cannot function end-to-end (JIRA epic → Rai design → JIRA stories → status sync).

## Value

**For demo (March 14):**
- Proves AI-assisted product management workflow to Coppel
- Validates RaiSE as governance tool at scale (bidirectional sync)
- Demonstrates JIRA integration for Atlassian partnership

**For framework:**
- Foundation for RaiSE PRO (commercial offering)
- Port/adapter pattern enables future providers (GitLab, Odoo)
- Reusable infrastructure for external tool integration

## Architectural Context

**Module:** `mod-providers` (NEW)
**Domain:** `bc-external-integration` (NEW)
**Layer:** Integration
**Dependencies:**
- `mod-config` (provider credentials and settings)
- S-DEMO.2 OAuth module (token management)

**Key constraints from mod-config:**
- Type annotations on all code (`pyright --strict`)
- >90% test coverage
- Pydantic models for all schemas
- No secrets in code (use OAuth tokens)

**Architecture position:**
```
┌─────────────────┐
│  mod-cli        │  (Orchestration - commands)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  mod-providers  │ ← NEW (this story)
│  (Integration)  │   JIRA adapter implementation
└────────┬────────┘
         │
         ├─→ mod-config (credentials)
         └─→ S-DEMO.2 OAuth (tokens)
```

## Approach

Create a bidirectional JIRA client wrapper over `atlassian-python-api` that provides:

1. **Read operations** (JIRA → Local):
   - `read_epic(key: str) -> JiraEpic` - Get epic with filtered fields
   - `read_stories_for_epic(epic_key: str) -> list[JiraStory]` - Get stories under epic
   - `read_epic_status(key: str) -> str` - Get current epic status
   - `read_story_status(key: str) -> str` - Get current story status

2. **Write operations** (Local → JIRA):
   - `create_story(epic_key: str, story: StoryCreate) -> JiraStory` - Create story under epic
   - Story includes: summary, description, labels

3. **Infrastructure:**
   - Rate limiting: 10 requests/second (JIRA Cloud limit)
   - Field filtering: Return only required fields (mitigates March 2 API changes)
   - OAuth integration: Use S-DEMO.2 token management (automatic refresh)
   - Error handling: User-friendly messages with JIRA context

**Components affected:**
- **CREATE:** `src/rai_providers/` (new package)
- **CREATE:** `src/rai_providers/jira/client.py` (JIRA client)
- **CREATE:** `src/rai_providers/jira/models.py` (Pydantic models)
- **CREATE:** `src/rai_providers/base.py` (BacklogProvider interface for future)
- **MODIFY:** S-DEMO.2 OAuth module (if token refresh integration needed)

## Examples

### 1. Read Epic

```python
from rai_providers.jira.client import JiraClient
from rai_providers.jira.oauth import get_jira_token

# Initialize client
token = get_jira_token()  # From S-DEMO.2
client = JiraClient(
    cloud_id="your-cloud-id",
    access_token=token.access_token
)

# Read epic with filtered fields
epic = client.read_epic("DEMO-123")

print(epic.key)          # "DEMO-123"
print(epic.summary)      # "Product Governance Initiative"
print(epic.description)  # Full description text
print(epic.status)       # "In Progress"
print(epic.labels)       # ["governance", "mvp"]
```

### 2. Read Stories for Epic

```python
# Get all stories under an epic
stories = client.read_stories_for_epic("DEMO-123")

for story in stories:
    print(f"{story.key}: {story.summary} [{story.status}]")

# Output:
# DEMO-124: Define governance principles [To Do]
# DEMO-125: Create compliance checklist [In Progress]
# DEMO-126: Build approval workflow [Done]
```

### 3. Create Story

```python
from rai_providers.jira.models import StoryCreate

# Create new story under epic
story_data = StoryCreate(
    summary="Implement value metrics",
    description="Design and implement value measurement framework...",
    labels=["governance", "metrics"]
)

new_story = client.create_story(
    epic_key="DEMO-123",
    story=story_data
)

print(new_story.key)      # "DEMO-127" (assigned by JIRA)
print(new_story.status)   # "To Do" (default status)
```

### 4. Rate Limiting (Automatic)

```python
# Client automatically enforces 10 req/sec limit
for i in range(100):
    epic = client.read_epic(f"DEMO-{i}")
    # Automatic delay if exceeding rate limit
    # No manual sleep needed
```

### 5. Error Handling

```python
from rai_providers.jira.exceptions import JiraAuthError, JiraNotFoundError

try:
    epic = client.read_epic("INVALID-999")
except JiraNotFoundError as e:
    print(f"Epic not found: {e.message}")
    # Output: "Epic not found: INVALID-999 does not exist or you don't have permission"
except JiraAuthError as e:
    print(f"Authentication failed: {e.message}")
    # Token automatically refreshed by OAuth layer
```

## Data Structures

### JiraEpic (Pydantic Model)

```python
from pydantic import BaseModel, Field

class JiraEpic(BaseModel):
    """JIRA Epic with filtered fields only."""

    key: str = Field(..., description="Epic key (e.g., DEMO-123)")
    summary: str = Field(..., description="Epic title")
    description: str | None = Field(None, description="Epic description")
    status: str = Field(..., description="Status name (e.g., 'In Progress')")
    labels: list[str] = Field(default_factory=list, description="Epic labels")

    # Internal field for sync tracking (added in S-DEMO.4)
    # jira_id: str  # Deferred to entity properties story
```

### JiraStory (Pydantic Model)

```python
class JiraStory(BaseModel):
    """JIRA Story/Issue with filtered fields only."""

    key: str = Field(..., description="Story key (e.g., DEMO-124)")
    summary: str = Field(..., description="Story title")
    description: str | None = Field(None, description="Story description")
    status: str = Field(..., description="Status name (e.g., 'To Do')")
    labels: list[str] = Field(default_factory=list, description="Story labels")
    epic_key: str | None = Field(None, description="Parent epic key")
```

### StoryCreate (Input Model)

```python
class StoryCreate(BaseModel):
    """Data required to create a JIRA story."""

    summary: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None)
    labels: list[str] = Field(default_factory=list)
```

### BacklogProvider (Interface - Future)

```python
from abc import ABC, abstractmethod

class BacklogProvider(ABC):
    """Interface for backlog providers (JIRA, GitLab, Odoo, Local)."""

    @abstractmethod
    def read_epic(self, key: str) -> Any:
        """Read epic from provider."""
        pass

    @abstractmethod
    def create_story(self, epic_key: str, story: Any) -> Any:
        """Create story under epic in provider."""
        pass

    # Note: Defined in this story but only JiraClient implements it
    # GitLab/Odoo adapters deferred to post-demo
```

## Acceptance Criteria

### MUST

- [ ] Can read a JIRA epic by key, returns `JiraEpic` with filtered fields (key, summary, description, status, labels)
- [ ] Can read stories for an epic, returns `list[JiraStory]` with filtered fields
- [ ] Can create a JIRA story under an epic, returns created `JiraStory` with JIRA-assigned key
- [ ] Rate limiting enforced: max 10 requests/second (no bursts exceeding limit)
- [ ] Field filtering applied: API requests use `fields` parameter to return only required fields
- [ ] OAuth token integration: Uses S-DEMO.2 token management, handles 401 with automatic refresh
- [ ] Type annotations complete: `pyright --strict` passes with zero errors
- [ ] Test coverage >90%: Unit tests + integration test with real JIRA API
- [ ] All quality checks pass: `pytest`, `ruff check`, `bandit` all exit 0

### SHOULD

- [ ] Rate limiting provides helpful logs when throttling (e.g., "Rate limit: waiting 0.1s")
- [ ] Error messages include JIRA context (epic key, error code, response body)
- [ ] Client supports dry-run mode (log what would happen without API calls)

### MUST NOT

- [ ] Must NOT store secrets in code (credentials, tokens)
- [ ] Must NOT implement sync logic (that's S-DEMO.5 - this is a client only)
- [ ] Must NOT add entity properties handling (that's S-DEMO.4)
- [ ] Must NOT implement task-level operations (deferred post-demo)

## Constraints

### Performance
- Rate limiting: 10 req/sec max (JIRA Cloud limit)
- Response time: <2s per API call (acceptable for demo)

### Security
- No secrets in code (OAuth tokens from S-DEMO.2)
- Token refresh automatic (handled by OAuth layer)
- HTTPS only (JIRA Cloud enforces)

### Compatibility
- JIRA Cloud API v3 (not Server/Data Center)
- Python 3.11+
- Works with `atlassian-python-api` library

### Architectural
- Clean separation: client (this story) vs sync engine (S-DEMO.5)
- Port/adapter pattern: JiraClient implements future BacklogProvider interface
- Field filtering from day 1 (mitigates March 2 API changes)

## Testing Approach

### Unit Tests
- Mock `atlassian-python-api` responses
- Test rate limiting logic (mock time, verify delays)
- Test field filtering (verify API call parameters)
- Test error handling (404, 401, 500 responses)
- Test Pydantic model validation

### Integration Test
- **Real JIRA API test** (using test project):
  - Create test epic in JIRA manually
  - Read epic via client → verify fields returned
  - Create story via client → verify appears in JIRA
  - Read stories for epic → verify list includes created story
  - Verify rate limiting over 20 requests (should take ~2s minimum)

- **Test data cleanup:** Delete created story after test

### Coverage Target
- >90% line coverage
- 100% coverage on error handling paths
- 100% coverage on rate limiting logic

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **JIRA API rate limits hit during test** | Medium | Medium | Implement rate limiting from day 1; use field filtering to reduce calls |
| **API changes (March 2)** | Low | High | Field filtering implemented early; monitor Atlassian changelog |
| **Token refresh during operations** | Low | Medium | Use S-DEMO.2 automatic refresh; retry on 401 |
| **Complex response parsing** | Low | Medium | Pydantic models validate responses; comprehensive tests |

## Related Decisions

- **ADR-012:** Skills orchestrate, CLI provides data → Client is data layer, not orchestration
- **ADR-015:** File-first design → OAuth tokens stored in files (S-DEMO.2)
- S-DEMO.1 research synthesis: Local-first sync, hub-and-spoke, field filtering

## Dependencies

**Requires:**
- S-DEMO.2 (OAuth authentication) ✅ - COMPLETE

**Enables:**
- S-DEMO.4 (Entity properties) - needs client to read/write JIRA
- S-DEMO.5 (Sync engine) - orchestrates client operations

## Next Steps

After design approval:
1. `/rai-story-plan` - Decompose into TDD tasks
2. Implementation with RED-GREEN-REFACTOR
3. Integration test with real JIRA API
4. `/rai-story-review` - Retrospective

---

*Design created: 2026-02-14*
*Next: `/rai-story-plan`*
