---
story_id: S-DEMO.5
title: "Sync Engine (Pull + Push)"
epic: E-DEMO
phase: implement
created: "2026-02-15"
---

# Plan: S-DEMO.5 — Sync Engine

## Tasks (6 total, ~4.5 hours)

### Task 1: Sync State Management (45 min)
**Files:** `src/rai_providers/jira/sync_state.py`, `tests/providers/jira/test_sync_state.py`
**What:** Pydantic models (SyncMapping, SyncState) + file I/O (load/save state.json)
**Verify:** `pytest tests/providers/jira/test_sync_state.py -v && pyright src/rai_providers/jira/sync_state.py`

### Task 2: Pull Operation (60 min)
**Files:** `src/rai_providers/jira/sync.py`, `tests/providers/jira/test_sync.py`
**What:** `pull_epic()` — reads JIRA epic+stories, updates state.json, sets entity properties
**Depends on:** Task 1
**Verify:** `pytest tests/providers/jira/test_sync.py::TestPullEpic -v && pyright src/rai_providers/jira/sync.py`

### Task 3: Push Operation (60 min)
**Files:** `sync.py` (extend), `test_sync.py` (extend)
**What:** `push_stories()` — creates JIRA stories, idempotent via state.json, sets entity properties
**Depends on:** Task 1, Task 2
**Verify:** `pytest tests/providers/jira/test_sync.py::TestPushStories -v`

### Task 4: Authorization Check (30 min)
**Files:** `sync.py` (extend), `test_sync.py` (extend)
**What:** `check_authorization()` — reads state.json offline, returns auth status
**Depends on:** Task 1
**Verify:** `pytest tests/providers/jira/test_sync.py::TestCheckAuthorization -v`

### Task 5: CLI Commands (45 min)
**Files:** `src/rai_cli/cli/commands/backlog.py` (modify)
**What:** Add `pull`, `push`, `status` commands to `rai backlog`
**Depends on:** Tasks 2, 3, 4
**Verify:** `rai backlog pull --help && rai backlog push --help && rai backlog status --help`

### Task 6: Integration Test (30 min)
**Files:** integration test script
**What:** End-to-end test with live JIRA
**Depends on:** Task 5
**Verify:** Manual execution against test JIRA project
