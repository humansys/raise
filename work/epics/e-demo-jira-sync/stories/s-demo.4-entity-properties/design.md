---
id: "S-DEMO.4"
title: "Entity Properties & Sync Metadata"
epic: "E-DEMO"
size: "S"
estimated_sp: 2
phase: "design"
dependencies: ["S-DEMO.3"]
created: "2026-02-14"
---

# Design: S-DEMO.4 - Entity Properties & Sync Metadata

## Problem

Sync operations need persistent metadata to track what's been synced, when, and by whom. Without this:
- Can't detect if a JIRA issue is already synced (duplicate creation risk)
- Can't determine last sync timestamp (unnecessary re-sync)
- Can't support Forge intelligence (no cross-project IDs or metadata aggregation)

**Gap**: S-DEMO.3 provides JIRA read/write operations but no metadata persistence layer.

## Value

**Immediate (Demo):**
- Enables idempotent sync operations (safe to re-run `push`/`pull`)
- Tracks sync state per epic/story (know what's synced vs pending)
- Foundation for S-DEMO.5 (sync engine depends on metadata)

**Strategic (Forge Vision - V3):**
- Cross-project intelligence via stable internal IDs (E-DEMO, S-DEMO.4)
- Metadata aggregation across JIRA projects (velocity patterns, blocker detection)
- Conflict detection via `last_modified_by` field (who changed what)

**Evidence**: Research synthesis (32 sources, HIGH confidence) + ADR-028 recommend entity properties as industry best practice.

---

## Architectural Context

**Module:** mod-providers (new, Integration layer)
**Bounded Context:** bc-external-integration
**Dependencies:**
- mod-providers/jira/client.py (S-DEMO.3) - JIRA API client
- Pydantic (validation)

**Layer constraints (Integration):**
- ✓ Can depend on: Leaf layer (Pydantic, config)
- ✓ Can be used by: Orchestration layer (CLI, sync engine)
- ✗ Must not depend on: Domain or orchestration layers

**Applicable guardrails:**
- MUST-CODE-001: Type hints on all code (pyright strict)
- MUST-CODE-003: No type errors (pyright reports 0 errors)
- MUST-TEST-001: >90% test coverage
- MUST-ARCH-002: Pydantic models for all schemas

---

## Approach

**WHAT we're building:**
Pydantic models + storage/retrieval functions for JIRA entity properties, implementing the schema from ADR-028.

**Key design decisions (interactive session results):**

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Schema scope** | Full schema (epic+story+task fields) | Matches ADR-028 exactly. Future-proof for post-demo task sync. Operations use epic+story subset for now. |
| **Caching strategy** | Query JIRA every time (no cache) | Simple, always fresh data. Manual sync operations tolerate latency. No cache invalidation complexity. |
| **Validation strictness** | Fail fast (Pydantic strict mode) | Catch data quality issues early. Clear error messages. |

**WHY this approach:**
- **ADR-028 defines the contract** - Full schema with `sync_version: "1"` for evolution
- **Lean principle** - Simple operations (get/set), no caching muda
- **Forge-ready** - Internal IDs + metadata enable V3 intelligence
- **Research-backed** - Entity properties are industry standard (Exalate, Unito use same pattern)

---

## Components

**New files (create):**

```
src/rai_providers/jira/
├── models.py              # Modified (add EntityProperty models)
└── properties.py          # New (storage/retrieval operations)

tests/providers/jira/
└── test_properties.py     # New (unit + integration tests)
```

**Modified:**
- `src/rai_providers/jira/models.py` - Add entity property Pydantic models
- Imports in `src/rai_providers/jira/__init__.py` if needed

---

## Examples

### 1. Pydantic Models (Data Structures)

```python
# src/rai_providers/jira/models.py

from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field

class RaiSyncMetadata(BaseModel):
    """Base sync metadata for all JIRA entities (from ADR-028)."""

    # Internal IDs (stable cross-project)
    epic_id: Optional[str] = Field(None, description="RaiSE epic ID (e.g., E-DEMO)")
    story_id: Optional[str] = Field(None, description="RaiSE story ID (e.g., S-DEMO.4)")
    task_id: Optional[str] = Field(None, description="RaiSE task ID (e.g., T-DEMO.4.1)")

    # Sync tracking
    last_sync_at: datetime = Field(description="Last sync timestamp (ISO 8601)")
    sync_version: str = Field(default="1", description="Schema version for evolution")
    rai_branch: str = Field(description="Git branch (e.g., demo/atlassian-webinar)")
    local_path: str = Field(description="Local project path")

    # Task-specific metadata (for subtasks, optional for epic/story)
    task_status: Optional[Literal["pending", "in_progress", "done"]] = Field(
        None, description="Task workflow state"
    )
    task_blocked: Optional[bool] = Field(None, description="Is task blocked?")
    estimated_sp: Optional[float] = Field(None, description="Story points estimate")

    # Forge-ready fields (V3)
    sync_direction: Literal["push", "pull", "bidirectional"] = Field(
        default="push", description="Sync direction"
    )
    last_modified_by: Literal["rai", "jira"] = Field(
        default="rai", description="Who last modified (conflict detection)"
    )

class EntityProperty(BaseModel):
    """JIRA entity property wrapper (ADR-028)."""

    rai_sync: RaiSyncMetadata = Field(description="RaiSE sync metadata")

    class Config:
        """Pydantic config for strict validation."""
        strict = True  # Fail fast on invalid data
        extra = "forbid"  # Reject unknown fields
```

### 2. Storage Functions (API Usage)

```python
# src/rai_providers/jira/properties.py

from typing import Optional
from .client import JiraClient
from .models import EntityProperty, RaiSyncMetadata

PROPERTY_KEY = "com.humansys.raise.sync"  # Namespaced key from ADR-028

async def set_entity_property(
    client: JiraClient,
    issue_key: str,
    metadata: RaiSyncMetadata
) -> None:
    """
    Store sync metadata on JIRA issue via entity properties.

    Args:
        client: Authenticated JIRA client
        issue_key: JIRA issue key (e.g., "DEMO-123")
        metadata: RaiSE sync metadata to store

    Raises:
        JiraApiError: If JIRA API call fails

    Example:
        >>> metadata = RaiSyncMetadata(
        ...     epic_id="E-DEMO",
        ...     story_id="S-DEMO.4",
        ...     last_sync_at=datetime.now(UTC),
        ...     rai_branch="demo/atlassian-webinar",
        ...     local_path="/home/emilio/Code/raise-commons"
        ... )
        >>> await set_entity_property(client, "DEMO-123", metadata)
    """
    property_data = EntityProperty(rai_sync=metadata)

    # PUT /rest/api/3/issue/{issueIdOrKey}/properties/{propertyKey}
    await client.put(
        f"/rest/api/3/issue/{issue_key}/properties/{PROPERTY_KEY}",
        json=property_data.model_dump(mode="json")
    )

async def get_entity_property(
    client: JiraClient,
    issue_key: str
) -> Optional[RaiSyncMetadata]:
    """
    Retrieve sync metadata from JIRA issue entity properties.

    Args:
        client: Authenticated JIRA client
        issue_key: JIRA issue key (e.g., "DEMO-123")

    Returns:
        RaiSyncMetadata if found, None if not set

    Raises:
        JiraApiError: If JIRA API call fails (except 404)
        ValidationError: If stored data doesn't match schema (fail fast)

    Example:
        >>> metadata = await get_entity_property(client, "DEMO-123")
        >>> if metadata:
        ...     print(f"Last synced: {metadata.last_sync_at}")
        ...     print(f"Epic: {metadata.epic_id}, Story: {metadata.story_id}")
    """
    # GET /rest/api/3/issue/{issueIdOrKey}/properties/{propertyKey}
    try:
        response = await client.get(
            f"/rest/api/3/issue/{issue_key}/properties/{PROPERTY_KEY}"
        )
    except JiraApiError as e:
        if e.status_code == 404:
            # Property not set yet (not an error for new issues)
            return None
        raise

    # Strict validation (fail fast on malformed data)
    property_data = EntityProperty.model_validate(response.json())
    return property_data.rai_sync

async def has_rai_metadata(
    client: JiraClient,
    issue_key: str
) -> bool:
    """
    Check if JIRA issue has RaiSE sync metadata (idempotency check).

    Args:
        client: Authenticated JIRA client
        issue_key: JIRA issue key

    Returns:
        True if metadata exists, False otherwise

    Example:
        >>> if await has_rai_metadata(client, "DEMO-123"):
        ...     print("Issue already synced from RaiSE")
    """
    metadata = await get_entity_property(client, issue_key)
    return metadata is not None
```

### 3. Usage in Sync Engine (S-DEMO.5 Preview)

```python
# Preview: How S-DEMO.5 will use entity properties

from datetime import datetime, UTC
from rai_providers.jira.properties import set_entity_property, get_entity_property

async def push_story_to_jira(story_id: str, jira_client: JiraClient) -> str:
    """Push local story to JIRA (with idempotency via entity properties)."""

    # Check if already synced (idempotency)
    existing = await get_entity_property(jira_client, expected_key)
    if existing and existing.story_id == story_id:
        print(f"Story {story_id} already synced to {expected_key}")
        return expected_key

    # Create JIRA issue
    jira_key = await jira_client.create_issue(
        project="DEMO",
        summary=story_title,
        description=story_description,
        issue_type="Story"
    )

    # Store sync metadata
    metadata = RaiSyncMetadata(
        epic_id="E-DEMO",
        story_id=story_id,
        last_sync_at=datetime.now(UTC),
        rai_branch=get_current_branch(),
        local_path=get_project_root(),
        sync_direction="push",
        last_modified_by="rai"
    )
    await set_entity_property(jira_client, jira_key, metadata)

    return jira_key
```

---

## Acceptance Criteria

### MUST (Required for Story Completion)

- [ ] **Pydantic models defined** matching ADR-028 schema exactly:
  - `RaiSyncMetadata` with all fields (epic_id, story_id, task_id, timestamps, Forge fields)
  - `EntityProperty` wrapper class
  - Strict validation enabled (`strict=True`, `extra="forbid"`)

- [ ] **Storage function** (`set_entity_property`) implemented:
  - Accepts `JiraClient`, `issue_key`, `RaiSyncMetadata`
  - Uses property key `com.humansys.raise.sync` (ADR-028)
  - Calls JIRA API: `PUT /rest/api/3/issue/{key}/properties/{propertyKey}`
  - Handles API errors with clear exception messages

- [ ] **Retrieval function** (`get_entity_property`) implemented:
  - Returns `Optional[RaiSyncMetadata]` (None if not set)
  - Returns None on 404 (property not set), raises on other errors
  - Strict validation (Pydantic raises `ValidationError` on malformed data)

- [ ] **Idempotency helper** (`has_rai_metadata`) implemented:
  - Returns `bool` indicating if entity property exists
  - Used for duplicate detection in sync engine

- [ ] **Unit tests** passing (>90% coverage):
  - Model validation tests (valid data, invalid data, missing fields)
  - Storage/retrieval with mocked JIRA client
  - Error handling (API failures, malformed data)

- [ ] **Integration tests** passing (manual verification):
  - Set entity property on live JIRA issue
  - Retrieve entity property from same issue
  - Verify data round-trips correctly
  - Test 404 handling (property not set)

- [ ] **All quality gates pass**:
  - `pyright --strict` reports 0 errors
  - `ruff check .` exits 0
  - `pytest --cov` shows >90% coverage
  - `bandit -r src/` exits 0

### SHOULD (Nice-to-Have)

- [ ] **Bulk operations** (if time permits):
  - `get_entity_properties_bulk(issue_keys: list[str])` for efficient multi-issue retrieval
  - Uses JIRA batch API if available

- [ ] **Property deletion** (cleanup):
  - `delete_entity_property(issue_key: str)` for testing/cleanup

- [ ] **Schema version validation**:
  - Log warning if `sync_version != "1"` (future migration signal)

### MUST NOT

- ❌ **Cache entity properties locally** - Query JIRA every time (design decision)
- ❌ **Implement sync engine logic** - That's S-DEMO.5 scope
- ❌ **Add custom fields** - Entity properties only (ADR-028)
- ❌ **Lenient validation** - Strict mode enforced (fail fast)

---

## Testing Strategy

**Unit Tests (mocked JIRA client):**
```python
# tests/providers/jira/test_properties.py

@pytest.fixture
def mock_jira_client():
    """Mock JiraClient for unit tests."""
    return Mock(spec=JiraClient)

async def test_set_entity_property_success(mock_jira_client):
    """Test successful property storage."""
    metadata = RaiSyncMetadata(
        epic_id="E-DEMO",
        story_id="S-DEMO.4",
        last_sync_at=datetime(2026, 2, 14, 10, 0, 0, tzinfo=UTC),
        rai_branch="demo/atlassian-webinar",
        local_path="/test/path"
    )

    await set_entity_property(mock_jira_client, "DEMO-123", metadata)

    # Verify API call
    mock_jira_client.put.assert_called_once()
    args = mock_jira_client.put.call_args
    assert "DEMO-123" in args[0][0]
    assert "com.humansys.raise.sync" in args[0][0]

async def test_get_entity_property_not_found(mock_jira_client):
    """Test retrieval when property not set (404)."""
    mock_jira_client.get.side_effect = JiraApiError(status_code=404, message="Not found")

    result = await get_entity_property(mock_jira_client, "DEMO-999")

    assert result is None  # 404 returns None, not exception

async def test_get_entity_property_validation_error(mock_jira_client):
    """Test strict validation on malformed data."""
    mock_jira_client.get.return_value = Mock(
        json=lambda: {"rai_sync": {"invalid_field": "value"}}  # Missing required fields
    )

    with pytest.raises(ValidationError):
        await get_entity_property(mock_jira_client, "DEMO-123")
```

**Integration Tests (manual, live JIRA):**
```bash
# Run against test JIRA Cloud instance
# Requires: JIRA_API_TOKEN, JIRA_EMAIL, JIRA_CLOUD_ID in env

pytest tests/providers/jira/test_properties.py::test_entity_property_roundtrip -v
```

**Coverage target:** >90% on `properties.py` (MUST-TEST-001)

---

## Constraints

**Performance:**
- Entity property operations add ~100-200ms per JIRA API call
- Acceptable for manual sync operations (not real-time)
- No caching = always fresh data, no stale reads

**Security:**
- Entity properties visible only to JIRA admins via API (not in UI)
- Property key namespaced: `com.humansys.raise.sync` (no collision risk)
- No secrets in metadata (JIRA tokens managed by OAuth, not stored here)

**Scalability:**
- 32 KB limit per entity property (ADR-028 schema ~200 bytes, well within limit)
- JQL queries on entity properties scale to JIRA Cloud limits

**Error Handling:**
- Fail fast on validation errors (strict Pydantic mode)
- Clear error messages for API failures (include issue_key, status_code)
- 404 treated as "not set" (not an error for new issues)

---

## References

**Architecture Decisions:**
- ADR-028: Entity Schema Design (full schema, property key, Forge vision)
- ADR-027: Sync Engine Architecture (local-first, hub-and-spoke)
- ADR-026: OAuth Provider Choice (JIRA Cloud authentication)

**Research Foundation:**
- `/work/research/jira-bidirectional-sync/synthesis.md` - Claim 2 (entity properties best practice, 32 sources)
- [Jira entity properties](https://developer.atlassian.com/cloud/jira/platform/jira-entity-properties/) - Official docs

**Dependencies:**
- S-DEMO.3: JIRA bidirectional client (JiraClient class, API operations)
- Enables: S-DEMO.5 (sync engine uses entity properties for idempotency + state tracking)

**Next Steps:**
- `/rai-story-plan` - Decompose into atomic tasks
- Consider: ADR-028 schema matches implementation (no drift check needed, already aligned)

---

**Design completed:** 2026-02-14
**Interactive decisions:** Schema scope (full), caching (none), validation (strict)
**Estimated implementation:** 2 SP (4-6 hours with TDD)
