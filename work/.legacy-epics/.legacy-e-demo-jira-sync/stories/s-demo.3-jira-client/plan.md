# Implementation Plan: S-DEMO.3 JIRA Client (Bidirectional)

## Overview
- **Story:** S-DEMO.3
- **Story Points:** 3 SP (M-sized)
- **Epic:** E-DEMO (JIRA Sync Enabler)
- **Created:** 2026-02-14
- **Dependencies:** S-DEMO.2 (OAuth) ✅

## Context

**Architectural Position:**
- **New Module:** `mod-providers` (Integration layer)
- **Domain:** `bc-external-integration` (NEW)
- **Dependencies:** mod-config (credentials), S-DEMO.2 OAuth (tokens)

**Key Constraints (from mod-config):**
- Type annotations on all code (`pyright --strict`)
- >90% test coverage
- Pydantic models for all schemas
- No secrets in code

**Relevant Patterns:**
- PAT-E-013: Task granularity scales with SP (M = 3-5 tasks)
- PAT-E-028: Commit after each task
- PAT-E-070: TDD cycle RED-GREEN-REFACTOR
- PAT-E-165: Design validation after first task

---

## Tasks

### Task 1: Package Structure + Pydantic Models + Exceptions

**Description:**
Create the `rai_providers` package foundation with type-safe models and custom exceptions.

**TDD Cycle:**
- **RED:** Write tests for Pydantic model validation (valid/invalid inputs)
- **GREEN:** Implement models with field validation
- **REFACTOR:** Ensure models are clean and well-documented

**Files to create:**
- `src/rai_providers/__init__.py` (package init)
- `src/rai_providers/jira/__init__.py` (JIRA subpackage)
- `src/rai_providers/jira/models.py` (Pydantic models)
- `src/rai_providers/jira/exceptions.py` (custom exceptions)
- `tests/providers/__init__.py`
- `tests/providers/jira/__init__.py`
- `tests/providers/jira/test_models.py` (model validation tests)

**Implementation Details:**

**Models to create:**
```python
# src/rai_providers/jira/models.py
class JiraEpic(BaseModel):
    key: str
    summary: str
    description: str | None = None
    status: str
    labels: list[str] = Field(default_factory=list)

class JiraStory(BaseModel):
    key: str
    summary: str
    description: str | None = None
    status: str
    labels: list[str] = Field(default_factory=list)
    epic_key: str | None = None

class StoryCreate(BaseModel):
    summary: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    labels: list[str] = Field(default_factory=list)
```

**Exceptions to create:**
```python
# src/rai_providers/jira/exceptions.py
class JiraError(Exception):
    """Base exception for JIRA operations."""
    pass

class JiraAuthError(JiraError):
    """Authentication/authorization failed."""
    pass

class JiraNotFoundError(JiraError):
    """Resource not found (epic, story)."""
    pass

class JiraRateLimitError(JiraError):
    """Rate limit exceeded."""
    pass
```

**Verification:**
```bash
pytest tests/providers/jira/test_models.py -v
pyright src/rai_providers/ --strict
```

**Size:** S (30-45 min)
**Dependencies:** None

---

### Task 2: JIRA Client - Read Operations + Rate Limiting

**Description:**
Implement bidirectional read operations with rate limiting and OAuth integration.

**TDD Cycle:**
- **RED:** Write failing tests for each read operation (mock atlassian-python-api)
- **GREEN:** Implement read_epic(), read_stories_for_epic(), status methods
- **REFACTOR:** Extract common patterns, clean up

**Files to create:**
- `src/rai_providers/jira/client.py` (JiraClient class)
- `tests/providers/jira/test_client.py` (client tests with mocks)

**Implementation Details:**

**Client structure:**
```python
# src/rai_providers/jira/client.py
from atlassian import Jira
from rai_providers.jira.oauth import get_jira_token
from rai_providers.jira.models import JiraEpic, JiraStory
from rai_providers.jira.exceptions import *
import time
from collections import deque

class JiraClient:
    """Bidirectional JIRA client with rate limiting."""

    def __init__(self, cloud_id: str, access_token: str):
        self._jira = Jira(url=f"https://api.atlassian.com/ex/jira/{cloud_id}", token=access_token)
        self._rate_limiter = RateLimiter(max_requests=10, window_seconds=1.0)

    def read_epic(self, key: str) -> JiraEpic:
        """Read epic with filtered fields."""
        self._rate_limiter.wait_if_needed()
        # Implementation with error handling

    def read_stories_for_epic(self, epic_key: str) -> list[JiraStory]:
        """Read all stories under an epic."""
        self._rate_limiter.wait_if_needed()
        # Implementation with JQL query

    def read_epic_status(self, key: str) -> str:
        """Get epic status."""
        # Reuse read_epic, return status field

    def read_story_status(self, key: str) -> str:
        """Get story status."""
        # Similar to epic status
```

**Rate limiter:**
```python
class RateLimiter:
    """Token bucket rate limiter (10 req/sec)."""

    def __init__(self, max_requests: int = 10, window_seconds: float = 1.0):
        self._max_requests = max_requests
        self._window = window_seconds
        self._requests: deque[float] = deque()

    def wait_if_needed(self) -> None:
        """Block if rate limit would be exceeded."""
        now = time.time()
        # Remove requests outside window
        while self._requests and self._requests[0] < now - self._window:
            self._requests.popleft()

        # If at limit, wait
        if len(self._requests) >= self._max_requests:
            sleep_time = self._window - (now - self._requests[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
                now = time.time()

        self._requests.append(now)
```

**Field filtering:**
- Use `fields` parameter in JIRA API calls
- Only request: `key,summary,description,status,labels` for epics
- Only request: `key,summary,description,status,labels,parent` for stories

**OAuth integration:**
```python
# Get token from S-DEMO.2
from rai_providers.jira.oauth import get_jira_token

token = get_jira_token()
client = JiraClient(cloud_id="...", access_token=token.access_token)
```

**Error handling:**
- 401 → JiraAuthError (token expired, should trigger refresh)
- 404 → JiraNotFoundError (epic/story doesn't exist)
- 429 → JiraRateLimitError (server-side rate limit)
- 500 → JiraError (generic server error)

**Verification:**
```bash
pytest tests/providers/jira/test_client.py::test_read_epic -v
pytest tests/providers/jira/test_client.py::test_read_stories_for_epic -v
pytest tests/providers/jira/test_client.py::test_rate_limiting -v
pyright src/rai_providers/ --strict
```

**Size:** M (45-60 min)
**Dependencies:** Task 1

**Design Validation Checkpoint (PAT-E-165):**
After completing this task, pause for user review. Validate:
- Rate limiting approach works as expected
- Field filtering reduces response size
- OAuth integration is clean
- Error handling is comprehensive

---

### Task 3: JIRA Client - Write Operations

**Description:**
Implement story creation under parent epic with field filtering.

**TDD Cycle:**
- **RED:** Write failing test for create_story() (mock JIRA API response)
- **GREEN:** Implement create_story() with proper payload
- **REFACTOR:** Clean up, ensure consistent error handling

**Files to modify:**
- `src/rai_providers/jira/client.py` (add create_story method)
- `tests/providers/jira/test_client.py` (add create_story tests)

**Implementation Details:**

**Method signature:**
```python
def create_story(self, epic_key: str, story: StoryCreate) -> JiraStory:
    """Create a JIRA story under a parent epic.

    Args:
        epic_key: Parent epic key (e.g., "DEMO-123")
        story: Story data to create

    Returns:
        Created story with JIRA-assigned key

    Raises:
        JiraNotFoundError: Epic doesn't exist
        JiraAuthError: Invalid credentials
        JiraError: Other errors
    """
    self._rate_limiter.wait_if_needed()

    # Build payload
    payload = {
        "fields": {
            "project": {"key": self._extract_project_key(epic_key)},
            "summary": story.summary,
            "description": story.description or "",
            "issuetype": {"name": "Story"},
            "parent": {"key": epic_key},  # Link to epic
            "labels": story.labels,
        }
    }

    # Create via API
    try:
        response = self._jira.create_issue(fields=payload["fields"])
        # Parse response into JiraStory
        return JiraStory(
            key=response["key"],
            summary=story.summary,
            description=story.description,
            status=response["fields"]["status"]["name"],
            labels=story.labels,
            epic_key=epic_key,
        )
    except Exception as e:
        # Map to custom exceptions
        raise self._map_error(e)
```

**Helper methods:**
```python
def _extract_project_key(self, issue_key: str) -> str:
    """Extract project key from issue key (DEMO-123 → DEMO)."""
    return issue_key.split("-")[0]

def _map_error(self, error: Exception) -> JiraError:
    """Map atlassian-python-api errors to custom exceptions."""
    # 401 → JiraAuthError
    # 404 → JiraNotFoundError
    # 429 → JiraRateLimitError
    # else → JiraError
```

**Field filtering on create:**
- Only send required fields (minimize payload)
- Don't send optional fields if None/empty

**Verification:**
```bash
pytest tests/providers/jira/test_client.py::test_create_story -v
pytest tests/providers/jira/test_client.py::test_create_story_error_handling -v
pyright src/rai_providers/ --strict
ruff check src/rai_providers/
```

**Size:** S (30-45 min)
**Dependencies:** Task 2

---

### Task 4: BacklogProvider Interface (Future Extensibility)

**Description:**
Define abstract BacklogProvider interface for future GitLab/Odoo adapters.

**TDD Cycle:**
- **RED:** Write test that JiraClient implements BacklogProvider
- **GREEN:** Define interface, make JiraClient inherit
- **REFACTOR:** Ensure interface is clean and minimal

**Files to create:**
- `src/rai_providers/base.py` (BacklogProvider ABC)

**Files to modify:**
- `src/rai_providers/jira/client.py` (implement interface)
- `tests/providers/test_base.py` (interface tests)

**Implementation Details:**

**Interface definition:**
```python
# src/rai_providers/base.py
from abc import ABC, abstractmethod
from typing import Any

class BacklogProvider(ABC):
    """Abstract interface for backlog providers (JIRA, GitLab, Odoo, Local).

    This interface defines the contract for bidirectional sync operations.
    Implementations should handle provider-specific details (auth, API calls, etc.).
    """

    @abstractmethod
    def read_epic(self, key: str) -> Any:
        """Read an epic from the provider.

        Args:
            key: Provider-specific epic identifier

        Returns:
            Epic data (provider-specific model)
        """
        pass

    @abstractmethod
    def read_stories_for_epic(self, epic_key: str) -> list[Any]:
        """Read all stories under an epic.

        Args:
            epic_key: Parent epic identifier

        Returns:
            List of story data (provider-specific models)
        """
        pass

    @abstractmethod
    def create_story(self, epic_key: str, story: Any) -> Any:
        """Create a story under a parent epic.

        Args:
            epic_key: Parent epic identifier
            story: Story data (provider-specific input model)

        Returns:
            Created story data (provider-specific model)
        """
        pass
```

**JiraClient implementation:**
```python
# src/rai_providers/jira/client.py
from rai_providers.base import BacklogProvider

class JiraClient(BacklogProvider):
    """JIRA implementation of BacklogProvider."""

    # All methods already implemented in Tasks 2-3
    # Just add inheritance and docstring references to interface
```

**Verification:**
```bash
pytest tests/providers/test_base.py -v
pytest tests/providers/jira/test_client.py::test_implements_interface -v
pyright src/rai_providers/ --strict
```

**Size:** XS (15 min)
**Dependencies:** Task 3

---

### Task 5: Manual Integration Test with Real JIRA API

**Description:**
Validate the client works end-to-end with a real JIRA Cloud instance.

**Test Scenario:**
1. Set up OAuth token (using S-DEMO.2)
2. Read an existing epic from JIRA test project
3. Create a new story under that epic
4. Read stories for epic (verify created story appears)
5. Verify rate limiting over 20 requests (~2s minimum)
6. Clean up: Delete created test story

**Files to create:**
- `tests/providers/jira/test_integration.py` (manual integration test)

**Test Structure:**
```python
# tests/providers/jira/test_integration.py
import pytest
from rai_providers.jira.client import JiraClient
from rai_providers.jira.oauth import get_jira_token
from rai_providers.jira.models import StoryCreate

@pytest.mark.integration
@pytest.mark.skip(reason="Manual test - requires real JIRA instance")
def test_jira_client_integration():
    """Manual integration test with real JIRA API.

    Prerequisites:
    - JIRA Cloud test instance
    - OAuth token configured (via S-DEMO.2)
    - Test epic exists (e.g., DEMO-1)

    Run with: pytest -m integration --no-skip tests/providers/jira/test_integration.py
    """
    # Get OAuth token
    token = get_jira_token()

    # Initialize client
    cloud_id = "your-test-cloud-id"
    client = JiraClient(cloud_id=cloud_id, access_token=token.access_token)

    # Test 1: Read epic
    epic = client.read_epic("DEMO-1")
    assert epic.key == "DEMO-1"
    assert epic.summary
    assert epic.status
    print(f"✓ Read epic: {epic.key} - {epic.summary}")

    # Test 2: Read stories for epic
    stories_before = client.read_stories_for_epic("DEMO-1")
    print(f"✓ Found {len(stories_before)} existing stories")

    # Test 3: Create story
    story_data = StoryCreate(
        summary="[TEST] Integration test story - DELETE ME",
        description="Created by automated integration test",
        labels=["test", "automation"]
    )
    created_story = client.create_story("DEMO-1", story_data)
    assert created_story.key
    assert created_story.summary == story_data.summary
    print(f"✓ Created story: {created_story.key}")

    # Test 4: Verify story appears in epic
    stories_after = client.read_stories_for_epic("DEMO-1")
    assert len(stories_after) == len(stories_before) + 1
    assert any(s.key == created_story.key for s in stories_after)
    print(f"✓ Story appears under epic")

    # Test 5: Rate limiting
    import time
    start = time.time()
    for i in range(20):
        client.read_epic_status("DEMO-1")
    elapsed = time.time() - start
    assert elapsed >= 1.8  # 20 requests / 10 req/sec = 2s minimum
    print(f"✓ Rate limiting working: 20 requests in {elapsed:.2f}s")

    # Cleanup: Delete test story
    # (JIRA API delete via atlassian-python-api)
    client._jira.delete_issue(created_story.key)
    print(f"✓ Cleaned up test story: {created_story.key}")
```

**Manual Execution:**
```bash
# Export OAuth credentials
export JIRA_CLOUD_ID="your-test-cloud-id"

# Run integration test (manual - not in CI)
pytest -m integration tests/providers/jira/test_integration.py -v -s
```

**Verification:**
- All assertions pass
- Story created and visible in JIRA web UI
- Rate limiting enforced (20 requests ~2s)
- Test story cleaned up after test

**Size:** S (30 min)
**Dependencies:** Task 1, 2, 3, 4 (all previous tasks)

---

## Execution Order

1. **Task 1** (Foundation - models + exceptions)
2. **Task 2** (Read operations + rate limiting)
   - **CHECKPOINT:** Design validation (PAT-E-165)
3. **Task 3** (Write operations)
4. **Task 4** (Interface for future extensibility)
5. **Task 5** (Manual integration test - final validation)

**Parallelization:** None - all tasks sequential due to dependencies.

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| **Rate limiting logic complex** | Start with simple token bucket, test thoroughly with mock time |
| **OAuth token refresh during operations** | Rely on S-DEMO.2 automatic refresh; retry on 401 |
| **JIRA API response parsing errors** | Pydantic validation catches issues early; comprehensive error handling |
| **Integration test brittle** | Use dedicated test project; clear setup instructions; manual only (not CI) |

---

## Duration Tracking

| Task | Size | Estimated | Actual | Notes |
|------|------|-----------|--------|-------|
| 1. Models + Exceptions | S | 30-45 min | -- | Foundation |
| 2. Read + Rate Limiting | M | 45-60 min | -- | Core functionality + checkpoint |
| 3. Write Operations | S | 30-45 min | -- | Story creation |
| 4. BacklogProvider Interface | XS | 15 min | -- | Future extensibility |
| 5. Integration Test | S | 30 min | -- | Manual validation |
| **Total** | **3 SP** | **~3h** | **--** | M-sized story |

---

## Quality Gates

**Per-task gates:**
- [ ] Tests pass (`pytest`)
- [ ] Type checks pass (`pyright --strict`)
- [ ] Linting passes (`ruff check`)
- [ ] Code formatted (`ruff format --check`)
- [ ] Coverage >90% (`pytest --cov`)

**Story-level gates:**
- [ ] All 5 tasks complete
- [ ] Integration test passes (manual)
- [ ] Design validation checkpoint passed (after Task 2)
- [ ] Retrospective complete (`/rai-story-review`)

---

## Next Steps

After plan approval:
1. `/rai-story-implement` - Execute tasks with TDD
2. HITL checkpoints after each task (PAT-E-025)
3. Design validation after Task 2 (PAT-E-165)
4. Commit after each task (PAT-E-028)

---

*Plan created: 2026-02-14*
*Ready for implementation*
