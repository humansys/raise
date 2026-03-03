---
epic_id: "E347"
title: "Backlog Automation — deterministic CLI sync, complete hook wiring"
status: "draft"
created: "2026-03-03"
---

# Epic Brief: Backlog Automation

## Hypothesis
For RaiSE developers who manage work items across Jira and local file-based backlogs,
the Backlog Automation epic is a deterministic sync and hook-wiring layer
that ensures both adapters (McpJiraAdapter and FileAdapter) work reliably and consistently.
Unlike the current state where Jira sync is ad-hoc and FileAdapter has gaps,
our solution provides a unified `rai backlog` experience regardless of backend.

## Success Metrics
- **Leading:** Both adapters pass the same integration test suite for CRUD operations
- **Lagging:** Zero manual Jira/file edits needed during a full epic lifecycle

## Appetite
M — 5-7 stories

## Scope Boundaries
### In (MUST)
- FileAdapter parity with McpJiraAdapter for core operations (create, search, get, transition, comment, link, update)
- Deterministic hook wiring for backlog lifecycle events (story start/close, epic start/close)
- `rai backlog` CLI works identically regardless of adapter selection
- Adapter protocol compliance validation

### In (SHOULD)
- Batch operations support on FileAdapter
- Status mapping consistency between adapters
- Error handling and user feedback improvements

### No-Gos
- No new adapter types (GitHub Issues, Linear, etc.) — that's a separate epic
- No UI/dashboard for backlog visualization
- No real-time sync or webhooks — CLI-driven only

### Rabbit Holes
- Over-engineering a generic sync framework — keep it simple, two adapters
- Trying to make FileAdapter match every Jira feature — focus on what `rai backlog` actually uses
