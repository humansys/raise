# Implementation Plan: S-DEMO.4 - Entity Properties & Sync Metadata

## Overview

- **Story:** S-DEMO.4
- **Epic:** E-DEMO (JIRA Sync Enabler)
- **Story Points:** 2 SP
- **Feature Size:** S
- **Created:** 2026-02-14
- **Branch:** demo/atlassian-webinar (no separate story branch)
- **Design:** design.md (interactive decisions: full schema, no cache, strict validation)

**Scope:** Pydantic models + storage/retrieval functions for JIRA entity properties (ADR-028 schema).

---

## Tasks

### Task 1: Pydantic Models & Schema Validation

**Description:**
Define Pydantic models for entity properties matching ADR-028 schema exactly. Implement strict validation to fail fast on malformed data.

**Files to create/modify:**
- `src/rai_providers/jira/models.py` (modify - add EntityProperty models)
- `tests/providers/jira/test_models.py` (create or modify - model validation tests)

**TDD Cycle:**
1. **RED:** Write failing tests for RaiSyncMetadata validation
   - Test valid metadata (all required fields)
   - Test invalid metadata (missing fields, wrong types)
   - Test strict mode (reject unknown fields)
   - Test optional fields (task_id, task_status, etc.)
2. **GREEN:** Implement RaiSyncMetadata and EntityProperty models
   - All fields from ADR-028
   - `strict=True`, `extra="forbid"`
   - Proper type hints (datetime, Literal types)
3. **REFACTOR:** Clean up field definitions, add docstrings

**Implementation notes:**
- Use `from datetime import datetime` (not string timestamps)
- Use `Literal` types for enums (task_status, sync_direction, last_modified_by)
- Set defaults: `sync_version="1"`, `sync_direction="push"`, `last_modified_by="rai"`
- Optional fields: `epic_id`, `story_id`, `task_id`, `task_status`, `task_blocked`, `estimated_sp`
- Required fields: `last_sync_at`, `rai_branch`, `local_path`

**Verification:**
```bash
# Tests pass
pytest tests/providers/jira/test_models.py -v

# Type checking passes
pyright src/rai_providers/jira/models.py

# Coverage check
pytest --cov=src/rai_providers/jira/models tests/providers/jira/test_models.py
```

**Expected test count:** ~8-10 unit tests (valid cases, invalid cases, strict validation)

**Size:** M (30-60 min - complex Pydantic models with many fields)

**Dependencies:** None (foundation task)

**Design validation checkpoint (PAT-E-165):**
After this task completes, pause for user review. Validate:
- Schema matches ADR-028 exactly
- Strict validation behavior is correct
- Field types and defaults are appropriate

---

### Task 2: Storage & Retrieval Functions

**Description:**
Implement functions to store and retrieve entity properties from JIRA. Query JIRA every time (no caching per design decision).

**Files to create/modify:**
- `src/rai_providers/jira/properties.py` (create - storage/retrieval operations)
- `tests/providers/jira/test_properties.py` (create - function tests with mocked client)
- `src/rai_providers/jira/__init__.py` (modify if needed - exports)

**TDD Cycle:**
1. **RED:** Write failing tests with mocked JiraClient
   - `test_set_entity_property_success()` - verify API call
   - `test_get_entity_property_success()` - verify deserialization
   - `test_get_entity_property_not_found()` - 404 returns None
   - `test_get_entity_property_validation_error()` - malformed data raises error
   - `test_has_rai_metadata_true()` - property exists
   - `test_has_rai_metadata_false()` - property missing
2. **GREEN:** Implement functions
   - `set_entity_property(client, issue_key, metadata)`
   - `get_entity_property(client, issue_key)` → Optional[RaiSyncMetadata]
   - `has_rai_metadata(client, issue_key)` → bool
   - Use property key: `PROPERTY_KEY = "com.humansys.raise.sync"`
3. **REFACTOR:** Extract common patterns, improve error messages

**Implementation notes:**
- API endpoints:
  - PUT `/rest/api/3/issue/{issueIdOrKey}/properties/{propertyKey}` (set)
  - GET `/rest/api/3/issue/{issueIdOrKey}/properties/{propertyKey}` (get)
- Error handling:
  - 404 on GET → return None (not an error)
  - Other errors → raise JiraApiError with clear message
  - Validation errors → let Pydantic raise (fail fast)
- Serialization: `EntityProperty(rai_sync=metadata).model_dump(mode="json")`
- Deserialization: `EntityProperty.model_validate(response.json())`

**Verification:**
```bash
# Tests pass
pytest tests/providers/jira/test_properties.py -v

# Type checking
pyright src/rai_providers/jira/properties.py

# Coverage check (>90% target)
pytest --cov=src/rai_providers/jira/properties tests/providers/jira/test_properties.py --cov-report=term-missing
```

**Expected test count:** ~6-8 unit tests (success paths, error paths, edge cases)

**Size:** M (30-60 min - three functions with error handling)

**Dependencies:** Task 1 (needs Pydantic models)

---

### Task 3: Integration Tests (Manual)

**Description:**
Validate storage/retrieval functions against live JIRA Cloud instance. Manual execution with environment variables.

**Files to create/modify:**
- `tests/providers/jira/test_properties_integration.py` (create - integration tests)
- `work/epics/e-demo-jira-sync/stories/s-demo.4-entity-properties/integration-test-results.md` (create - test log)

**Test cases:**
1. **Roundtrip test:**
   - Create RaiSyncMetadata with known values
   - Set entity property on test JIRA issue
   - Get entity property from same issue
   - Assert retrieved metadata matches original

2. **404 handling:**
   - Query entity property from issue that doesn't have one
   - Assert returns None (not exception)

3. **Validation error handling:**
   - Manually corrupt entity property data in JIRA (if possible)
   - Or mock a malformed response
   - Assert Pydantic raises ValidationError

4. **Idempotency check:**
   - Use `has_rai_metadata()` on synced issue (should return True)
   - Use `has_rai_metadata()` on new issue (should return False)

**Implementation notes:**
- Requires environment variables:
  - `JIRA_CLOUD_ID` (from S-DEMO.2 OAuth)
  - `JIRA_API_TOKEN` (OAuth access token)
  - `JIRA_TEST_ISSUE_KEY` (e.g., "DEMO-123" - manually created test issue)
- Mark as `@pytest.mark.integration` for optional execution
- Document results in integration-test-results.md with screenshots/logs

**Verification:**
```bash
# Manual execution (not in CI)
export JIRA_CLOUD_ID="your-cloud-id"
export JIRA_API_TOKEN="your-token"
export JIRA_TEST_ISSUE_KEY="DEMO-123"

pytest tests/providers/jira/test_properties_integration.py -v -s

# Document results
cat work/epics/e-demo-jira-sync/stories/s-demo.4-entity-properties/integration-test-results.md
```

**Expected output:**
- All 4 test cases pass
- Entity property visible in JIRA via API query (not UI)
- Results documented with timestamps and JIRA issue keys

**Size:** S (15-30 min - straightforward manual testing)

**Dependencies:** Task 2 (needs storage/retrieval functions)

---

### Task 4: Manual Integration Test (Final Validation)

**Description:**
End-to-end validation of entity property operations in a realistic sync scenario. Demonstrate that S-DEMO.4 enables idempotent sync operations (preview of S-DEMO.5).

**Test scenario:**
1. Create a mock story metadata (epic_id, story_id, timestamps)
2. Push metadata to JIRA test issue
3. Retrieve metadata and verify correctness
4. Push again (idempotency check via `has_rai_metadata`)
5. Query JIRA API directly to inspect entity property JSON

**Verification:**
```bash
# Interactive Python session or script
python -c "
from src.rai_providers.jira.client import JiraClient
from src.rai_providers.jira.properties import set_entity_property, get_entity_property
from src.rai_providers.jira.models import RaiSyncMetadata
from datetime import datetime, UTC

# Setup
client = JiraClient(cloud_id='...', token='...')
metadata = RaiSyncMetadata(
    epic_id='E-DEMO',
    story_id='S-DEMO.4',
    last_sync_at=datetime.now(UTC),
    rai_branch='demo/atlassian-webinar',
    local_path='/home/emilio/Code/raise-commons'
)

# Set property
await set_entity_property(client, 'DEMO-123', metadata)

# Get property
retrieved = await get_entity_property(client, 'DEMO-123')
print(f'Retrieved: {retrieved}')

# Idempotency check
has_meta = await has_rai_metadata(client, 'DEMO-123')
print(f'Has metadata: {has_meta}')
"
```

**Expected outcome:**
- Entity property successfully stored
- Retrieved metadata matches original
- `has_rai_metadata` returns True
- Demonstrates S-DEMO.4 is ready for S-DEMO.5 (sync engine integration)

**Size:** XS (<15 min - demo/validation only)

**Dependencies:** Task 3 (all implementation and integration tests complete)

---

## Execution Order

**Sequential path (no parallelism):**

1. **Task 1** - Pydantic Models (foundation, required by all others)
   - HITL checkpoint: Design validation (PAT-E-165)

2. **Task 2** - Storage & Retrieval Functions (depends on Task 1 models)

3. **Task 3** - Integration Tests (depends on Task 2 functions)

4. **Task 4** - Manual Integration Test (final validation, depends on all)

**Rationale:** No parallel tasks due to linear dependencies. Each task builds on previous.

**Critical path:** Task 1 → Task 2 → Task 3 → Task 4 (all sequential)

---

## Quality Gates

**Per-task gates:**
- [ ] All tests pass (`pytest` exits 0)
- [ ] Type checking passes (`pyright --strict` reports 0 errors)
- [ ] Linting passes (`ruff check .` exits 0)
- [ ] Coverage >90% on new code
- [ ] Commit created (one per task, PAT-E-028)

**Story-level gates (before close):**
- [ ] All 4 tasks complete
- [ ] Integration tests documented with results
- [ ] Manual demo successful (Task 4)
- [ ] All acceptance criteria from design.md met
- [ ] Retrospective complete (`/rai-story-review`)

---

## Risks & Mitigations

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| **JIRA API changes** | Low | Entity properties API is stable (GA since 2018). Research validated (32 sources). |
| **Strict validation too brittle** | Medium | Design decision - fail fast preferred. If issues arise, revisit in retrospective. |
| **Integration test environment setup** | Medium | Reuse S-DEMO.3 OAuth tokens. Document env vars clearly. Manual execution acceptable. |
| **Task granularity mismatch** | Low | S-sized story with 3 impl tasks + 1 validation = appropriate per PAT-E-013. |

---

## Duration Tracking

| Task | Size | Estimated | Actual | Notes |
|------|------|-----------|--------|-------|
| 1. Pydantic Models | M | 30-60 min | -- | TDD: tests first, then models. HITL checkpoint after. |
| 2. Storage & Retrieval | M | 30-60 min | -- | Three functions with error handling. |
| 3. Integration Tests | S | 15-30 min | -- | Manual execution, document results. |
| 4. Manual Integration Test | XS | <15 min | -- | Demo validation. |
| **Total** | **2 SP** | **90-165 min** | **--** | *Target: <2 hours per 2 SP estimate* |

**Estimation notes:**
- S-DEMO.3 delivered 1.33x velocity (135 min vs 180 min for 3 SP)
- S-DEMO.4 at same velocity: 2 SP = 120 min actual (vs 90-165 min estimated)
- TDD discipline may slow initial pace but reduces rework
- HITL checkpoints add 5-10 min per task (worth it for alignment)

---

## Acceptance Criteria (from design.md)

### MUST
- [x] Pydantic models defined (Task 1)
  - RaiSyncMetadata with all ADR-028 fields
  - EntityProperty wrapper
  - Strict validation enabled

- [x] Storage function implemented (Task 2)
  - `set_entity_property(client, issue_key, metadata)`
  - Uses `com.humansys.raise.sync` property key
  - Proper error handling

- [x] Retrieval function implemented (Task 2)
  - `get_entity_property(client, issue_key)` → Optional[RaiSyncMetadata]
  - Returns None on 404
  - Strict validation on retrieval

- [x] Idempotency helper implemented (Task 2)
  - `has_rai_metadata(client, issue_key)` → bool

- [x] Unit tests passing >90% coverage (Tasks 1-2)

- [x] Integration tests passing (Task 3)
  - Manual verification documented

- [x] All quality gates pass (all tasks)
  - pyright strict, ruff, pytest, bandit

### SHOULD
- [ ] Schema version validation (if time permits)
  - Log warning if `sync_version != "1"`

### MUST NOT
- ✓ No local caching (design decision: query JIRA every time)
- ✓ No sync engine logic (that's S-DEMO.5)
- ✓ No custom fields (entity properties only)

---

## Pattern Application

| Pattern | Application |
|---------|-------------|
| **PAT-E-013** | Task granularity: S-sized (2 SP) → 3 impl tasks + 1 validation (appropriate) |
| **PAT-E-025** | HITL default: Pause after each task for review |
| **PAT-E-028** | Commit after each task (4 commits expected) |
| **PAT-E-070** | TDD cycle: RED (test) → GREEN (code) → REFACTOR (clean) |
| **PAT-E-165** | Design validation checkpoint after Task 1 (catch misalignments early) |

---

## Next Steps

1. **Start implementation:** `/rai-story-implement`
2. **First task:** Task 1 (Pydantic Models) - foundation for all others
3. **HITL checkpoint:** After Task 1, validate design assumptions before proceeding

---

**Plan completed:** 2026-02-14
**Estimated duration:** 90-165 min (1.5-2.75 hours)
**Tasks:** 4 (3 implementation + 1 validation)
**Critical path:** Sequential (no parallelism)
