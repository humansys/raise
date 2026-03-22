# Story S-DEMO.3: JIRA Client (Bidirectional)

## Story Scope

**Epic:** E-DEMO (JIRA Sync Enabler)
**Size:** M (3 SP)
**Dependencies:** S-DEMO.2 (OAuth authentication) ✅
**Branch:** `story/s-demo.3/jira-client`
**Owner:** Emilio + Rai

---

## In Scope

### Core Functionality

**Read Operations (JIRA → Local):**
- Read JIRA epics with filtered fields (key, summary, description, status, labels)
- Read JIRA stories/issues with filtered fields
- Read epic status (In Progress, Done, etc.)
- Read story status for sync state tracking

**Write Operations (Local → JIRA):**
- Create JIRA stories under a specified epic
- Write story metadata (summary, description, labels)
- Link stories to parent epic

**Client Infrastructure:**
- Bidirectional wrapper over `atlassian-python-api`
- Rate limiting (respect JIRA Cloud limits: 10 req/sec per user)
- Field filtering to minimize data transfer (March 2 deadline mitigation)
- OAuth token integration (use S-DEMO.2 token management)
- Error handling with user-friendly messages
- Type annotations on all code (Pydantic models for JIRA entities)

### Technical Constraints

**MUST guardrails:**
- Type hints on all code (`pyright --strict` passes)
- >90% test coverage
- Pydantic models for all JIRA entity schemas
- No secrets in code (use OAuth tokens from S-DEMO.2)
- Ruff linting passes

**Architecture patterns:**
- Clean separation: client wrapper (this story) vs sync logic (S-DEMO.5)
- Adapter pattern: JIRA-specific implementation, interface for future providers
- Field filtering from day 1 (JIRA API changes March 2)

---

## Out of Scope

**Deferred to Later Stories:**
- ❌ Entity properties integration (S-DEMO.4)
- ❌ Sync engine logic (S-DEMO.5)
- ❌ Task-level operations (deferred post-demo)
- ❌ Conflict resolution (post-demo)
- ❌ Custom field mapping (post-demo)
- ❌ Workflow status mapping (post-demo)

**Never for Demo:**
- ❌ GitLab/Odoo adapters
- ❌ Webhooks or polling
- ❌ Attachment sync
- ❌ Comment sync

---

## Done Criteria

**Functional:**
- [ ] Can read a JIRA epic by key, return filtered fields
- [ ] Can read JIRA stories for an epic, return filtered fields
- [ ] Can create a JIRA story under a specified epic
- [ ] Can read epic status (e.g., "In Progress", "Done")
- [ ] Can read story status for sync state tracking
- [ ] Rate limiting enforced (no >10 req/sec bursts)
- [ ] Field filtering applied (return only required fields, not full JSON)

**Quality:**
- [ ] Type annotations complete (`pyright --strict` passes)
- [ ] >90% test coverage (unit + integration)
- [ ] All tests pass (`pytest` exits 0)
- [ ] Ruff linting passes (`ruff check .` exits 0)
- [ ] Docstrings on all public APIs (Google-style)
- [ ] Integration test with real JIRA API (using test project)

**Process:**
- [ ] TDD followed (RED-GREEN-REFACTOR on all tasks)
- [ ] Design document created (`/rai-story-design`)
- [ ] Implementation plan created (`/rai-story-plan`)
- [ ] Retrospective completed (`/rai-story-review`)

---

## Context

### Strategic Value

This story enables the core demo workflow:
1. Read JIRA epic → local backlog (pull)
2. Create JIRA stories from local design (push)
3. Read story status for prioritization sync

Without this bidirectional client, the demo cannot function.

### Architecture Position

```
┌─────────────────┐
│  S-DEMO.2       │
│  OAuth Auth     │ ← Token management
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  S-DEMO.3       │ ← YOU ARE HERE
│  JIRA Client    │   (Read/Write wrapper)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  S-DEMO.4       │
│  Entity Props   │ ← Metadata tracking
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  S-DEMO.5       │
│  Sync Engine    │ ← Orchestration
└─────────────────┘
```

### Key Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **JIRA API rate limits** | Medium | High | Implement rate limiting from day 1, field filtering |
| **API changes (March 2)** | Low | High | Field filtering implemented early, monitor changelog |
| **Complex response parsing** | Medium | Medium | Pydantic models for validation, comprehensive tests |
| **Token refresh during operations** | Low | Medium | Use S-DEMO.2 automatic refresh, retry on 401 |

---

## Related Documents

- **Epic Scope:** `work/epics/e-demo-jira-sync/scope.md`
- **OAuth Implementation:** S-DEMO.2 (`src/rai_providers/jira/oauth.py`)
- **Research Foundation:** `work/research/jira-bidirectional-sync/`
- **ADR:** ADR-024 (Sync Engine Architecture) - context for client design

---

*Story initialized: 2026-02-14*
*Next: `/rai-story-design`*
