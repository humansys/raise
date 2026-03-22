# Story Scope: S-DEMO.4 - Entity Properties & Sync Metadata

**Epic:** E-DEMO (JIRA Sync Enabler)
**Size:** S (2 SP)
**Dependencies:** S-DEMO.3 (JIRA bidirectional client)
**Branch:** demo/atlassian-webinar (no separate story branch - S-sized on epic branch)

---

## In Scope

**Entity Property Schema Design:**
- Pydantic models for sync metadata:
  - Epic sync metadata (RaiSE epic ID, JIRA epic ID/key, last sync timestamp, Forge metadata)
  - Story sync metadata (RaiSE story ID, JIRA story ID/key, last sync timestamp, Forge metadata)
- Schema aligned with JIRA entity properties API (key-value pairs per issue)
- Internal ID structure (E-DEMO, S-DEMO.4) for cross-project aggregation (Forge vision)

**Storage/Retrieval Functions:**
- `set_entity_properties(issue_id, properties)` - Store sync metadata on JIRA issue
- `get_entity_properties(issue_id)` - Retrieve sync metadata from JIRA issue
- Integration with existing JiraClient (S-DEMO.3)
- Error handling for entity property operations

**Forge Foundation (V3 Vision):**
- Internal IDs (E-DEMO, S-DEMO.4) enable stable cross-project identifiers
- Entity properties travel with JIRA issues → queryable by Forge
- Metadata schema supports future bidirectional sync (V3)

**Testing:**
- Unit tests for Pydantic models (validation, serialization)
- Unit tests for storage/retrieval functions (mocked JIRA API)
- Integration tests with live JIRA API (manual verification)

---

## Out of Scope

**Deferred to S-DEMO.5 (Sync Engine):**
- ❌ Sync engine logic (pull/push operations)
- ❌ Conflict detection
- ❌ Idempotency guarantees

**Deferred Post-Demo:**
- ❌ Task-level entity properties (epic+story only)
- ❌ Custom field mapping
- ❌ Three-way merge metadata
- ❌ Workflow status mapping

---

## Done Criteria

- [ ] Pydantic models defined (EntityPropertySchema, EpicSyncMetadata, StorySyncMetadata)
- [ ] pyright strict passes (type annotations on all code)
- [ ] Storage functions implemented (set_entity_properties)
- [ ] Retrieval functions implemented (get_entity_properties)
- [ ] Unit tests passing (>90% coverage on story code)
- [ ] Integration tests pass (manual verification with JIRA Cloud)
- [ ] All quality gates pass (ruff, pyright, bandit)
- [ ] ADR created if significant design decisions made
- [ ] Retrospective complete (/rai-story-review)

---

## Context

**From Epic Scope (lines 83-84):**
> S-DEMO.4: Entity properties & sync metadata (S, 2 SP) - JIRA entity properties for sync state (epic/story IDs, timestamps, Forge metadata). Schema design, storage/retrieval.

**From ADR-025 (to be created or referenced):**
- Entity properties chosen over custom fields or external DB
- Key decision: Metadata travels with JIRA issues (Forge-compatible)

**From S-DEMO.3 (JIRA Client):**
- JiraClient class exists with read/write operations
- BacklogProvider interface defined
- Rate limiting in place (10 req/sec)

---

*Story initialized: 2026-02-14*
*Target completion: 2026-02-15 (Sunday PM)*
