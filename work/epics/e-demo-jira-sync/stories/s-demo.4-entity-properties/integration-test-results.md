# Integration Test Results: S-DEMO.4 - Entity Properties

## Overview
Manual integration tests against live JIRA Cloud instance to validate entity property storage and retrieval.

**Test file:** `tests/providers/jira/test_properties_integration.py`
**Execution date:** TBD (awaiting manual execution)
**JIRA instance:** TBD
**Test issue:** TBD

---

## Prerequisites

### Environment Variables
```bash
export JIRA_CLOUD_ID="<cloud-id-from-oauth>"
export JIRA_API_TOKEN="<oauth-access-token>"
export JIRA_TEST_ISSUE_KEY="<test-issue-key>"  # e.g., "DEMO-123"
```

### Test Issue Setup
- Create a test JIRA issue manually in JIRA Cloud
- Note the issue key (e.g., DEMO-123)
- Issue can be of any type (Story, Task, etc.)
- Ensure OAuth token has read/write permissions on the issue

---

## Test Execution

### Command
```bash
pytest tests/providers/jira/test_properties_integration.py -v -s
```

### Expected Test Cases
1. **test_roundtrip_entity_property** - Create, set, get, verify metadata roundtrip
2. **test_404_handling** - Verify graceful handling of missing properties
3. **test_has_rai_metadata_true** - Verify idempotency helper (synced issue)
4. **test_has_rai_metadata_false** - Verify idempotency helper (unsynced issue)
5. **test_idempotency** - Verify multiple writes are idempotent

---

## Test Results

### Summary
- **Total tests:** 5
- **Passed:** TBD
- **Failed:** TBD
- **Skipped:** TBD
- **Duration:** TBD

### Detailed Results

#### Test 1: test_roundtrip_entity_property
**Status:** TBD
**Duration:** TBD

**Expected behavior:**
- Create RaiSyncMetadata with known values
- Set entity property on test JIRA issue
- Retrieve entity property from same issue
- All fields match original metadata

**Actual behavior:**
TBD

**Evidence:**
TBD (API response logs, JIRA issue property inspection)

---

#### Test 2: test_404_handling
**Status:** TBD
**Duration:** TBD

**Expected behavior:**
- Query entity property from non-existent issue
- Returns None (not exception)

**Actual behavior:**
TBD

**Evidence:**
TBD

---

#### Test 3: test_has_rai_metadata_true
**Status:** TBD
**Duration:** TBD

**Expected behavior:**
- Set metadata on test issue
- `has_rai_metadata()` returns True

**Actual behavior:**
TBD

**Evidence:**
TBD

---

#### Test 4: test_has_rai_metadata_false
**Status:** TBD
**Duration:** TBD

**Expected behavior:**
- Query unsynced issue
- `has_rai_metadata()` returns False

**Actual behavior:**
TBD

**Evidence:**
TBD

---

#### Test 5: test_idempotency
**Status:** TBD
**Duration:** TBD

**Expected behavior:**
- Set property twice with different timestamps
- Both writes succeed
- Second write updates timestamp

**Actual behavior:**
TBD

**Evidence:**
TBD

---

## JIRA API Verification

### Direct API Query
Verify entity property is visible via JIRA REST API:

```bash
curl -X GET \
  "https://api.atlassian.com/ex/jira/{cloudId}/rest/api/3/issue/{issueKey}/properties/com.humansys.raise.sync" \
  -H "Authorization: Bearer {token}" \
  -H "Accept: application/json"
```

**Expected response:**
```json
{
  "key": "com.humansys.raise.sync",
  "value": {
    "rai_sync": {
      "epic_id": "E-DEMO",
      "story_id": "S-DEMO.4",
      "last_sync_at": "2026-02-14T...",
      "rai_branch": "demo/atlassian-webinar",
      "local_path": "/home/emilio/Code/raise-commons",
      "sync_version": "1",
      "sync_direction": "push",
      "last_modified_by": "rai"
    }
  }
}
```

**Actual response:**
TBD

---

## Issues Encountered

### Issue 1: TBD
**Description:** TBD
**Resolution:** TBD

---

## Conclusion

**Status:** TBD (awaiting manual execution)

**Next steps:**
- [ ] Set up environment variables
- [ ] Create test JIRA issue
- [ ] Execute integration tests
- [ ] Document results
- [ ] Verify via direct API query
- [ ] Proceed to Task 4 (Manual Integration Test)

---

**Tested by:** TBD
**Date:** TBD
**JIRA Cloud ID:** TBD
**Test Issue:** TBD
