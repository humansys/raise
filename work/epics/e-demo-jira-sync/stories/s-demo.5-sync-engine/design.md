---
id: "S-DEMO.5"
title: "Sync Engine (Pull + Push)"
epic: "E-DEMO"
size: "L"
estimated_sp: 4
phase: "design"
dependencies: ["S-DEMO.4"]
created: "2026-02-15"
---

# Design: S-DEMO.5 — Sync Engine (Pull + Push)

## Problem

We have the building blocks (OAuth, JIRA client, entity properties) but no orchestration layer. The demo requires a complete workflow:

1. PM creates epic in JIRA
2. Developer pulls epic locally
3. Developer designs stories locally
4. Developer pushes stories to JIRA
5. Team authorizes stories in JIRA
6. Developer pulls authorization status
7. Only authorized stories can be worked on

Without S-DEMO.5, these are disconnected API calls. The sync engine connects them into a coherent workflow with state tracking and idempotency.

## Value

**Demo (tomorrow):** End-to-end bidirectional workflow for Coppel — proves governance at scale.

**Production (weeks):** Foundation for Humansys internal use and client deployments. Same engine, different authorization config.

## Architectural Context

**Module:** `mod-providers` (Integration layer)
**Bounded context:** `bc-external-integration`

**Dependencies (all complete):**
- S-DEMO.2: OAuth → `authenticate()`, `load_token()`
- S-DEMO.3: JIRA Client → `JiraClient.read_epic()`, `.create_story()`, etc.
- S-DEMO.4: Entity Properties → `set_entity_property()`, `get_entity_property()`

**New dependency:**
- `.raise/rai/sync/state.json` — Sync state file (new, created by this story)

---

## Approach

### Core Principle: State-Driven Sync

All sync operations are mediated by a local state file (`state.json`). The sync engine:
1. Reads JIRA → updates state
2. Reads state → creates JIRA issues
3. Never modifies `governance/backlog.md` programmatically

```
JIRA Cloud                    state.json                    Local Files
┌──────────┐   pull    ┌──────────────────┐                ┌──────────┐
│ Epic      │────────▶│ mappings.epics   │                │ (read    │
│ Stories   │         │ mappings.stories │                │  only)   │
│ Statuses  │         │ last_sync_at     │                │          │
└──────────┘         └────────┬─────────┘                └──────────┘
     ▲                        │                                │
     │         push           │ read                           │
     │    ┌───────────────────┘                                │
     │    │                                                    │
     │    ▼                                                    │
     │  Sync Engine reads local story files ◀──────────────────┘
     │  (scope.md, plan.md, story list)
     │    │
     └────┘
      create_story()
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Sync state location | `.raise/rai/sync/state.json` | Separate from knowledge graph (see blast radius doc) |
| backlog.md | NOT modified | Fragile markdown editing; CLI output sufficient for demo |
| Idempotency | Local state.json lookup | No JQL on entity properties (OAuth scope limitations) |
| Epic detection | Explicit `--epic KEY` | Auto-detect needs JQL filter config (post-demo) |
| Authorization | Read state.json offline | No JIRA API call at story-start time |
| ADR-027 amendment | Pull is now MVP | Demo workflow starts with pull |

---

## Components

### New Files

```
src/rai_providers/jira/
├── sync.py                    # Sync engine: pull_epic(), push_stories()
└── sync_state.py              # State management: load, save, update

tests/providers/jira/
├── test_sync.py               # Sync engine tests (mocked client)
└── test_sync_state.py         # State file tests

Runtime (created on first sync):
.raise/rai/sync/
└── state.json                 # Sync mappings
```

### Modified Files

```
src/rai_cli/cli/commands/backlog.py   # Add pull + push commands
src/rai_providers/jira/__init__.py    # Export sync functions
```

---

## Data Structures

### SyncState (Pydantic Model)

```python
class SyncMapping(BaseModel):
    """Mapping between local ID and JIRA key."""
    local_id: str                  # "E-DEMO" or "S-DEMO.1"
    jira_key: str                  # "DEMO-123" or "DEMO-124"
    jira_status: str               # "In Progress", "Approved", "To Do"
    last_sync_at: datetime         # ISO 8601 UTC
    sync_direction: Literal["pull", "push"]

class SyncState(BaseModel):
    """Persistent sync state between RaiSE and JIRA."""
    provider: str = "jira"
    cloud_id: str                  # Atlassian cloud ID
    project_key: str               # "DEMO"
    epics: dict[str, SyncMapping] = {}    # local_id → mapping
    stories: dict[str, SyncMapping] = {}  # local_id → mapping
    last_sync_at: datetime | None = None  # Global last sync

    model_config = ConfigDict(extra="forbid")
```

### state.json (Runtime Example)

```json
{
  "provider": "jira",
  "cloud_id": "abc-123-def",
  "project_key": "DEMO",
  "epics": {
    "E-DEMO": {
      "local_id": "E-DEMO",
      "jira_key": "DEMO-1",
      "jira_status": "In Progress",
      "last_sync_at": "2026-02-15T10:00:00Z",
      "sync_direction": "pull"
    }
  },
  "stories": {
    "S-DEMO.1": {
      "local_id": "S-DEMO.1",
      "jira_key": "DEMO-2",
      "jira_status": "Approved",
      "last_sync_at": "2026-02-15T11:00:00Z",
      "sync_direction": "push"
    },
    "S-DEMO.2": {
      "local_id": "S-DEMO.2",
      "jira_key": "DEMO-3",
      "jira_status": "To Do",
      "last_sync_at": "2026-02-15T11:00:00Z",
      "sync_direction": "push"
    }
  },
  "last_sync_at": "2026-02-15T11:00:00Z"
}
```

---

## Operations

### 1. Pull Epic (`rai backlog pull --source jira --epic DEMO-1`)

```python
def pull_epic(
    client: JiraClient,
    epic_key: str,
    state: SyncState,
    dry_run: bool = False,
) -> PullResult:
    """
    Pull epic and its stories from JIRA, update sync state.

    Steps:
    1. Read epic from JIRA (via JiraClient.read_epic)
    2. Check if epic already in state (update vs create)
    3. Read stories for epic (via JiraClient.read_stories_for_epic)
    4. Update state.json with epic + story mappings
    5. Set entity property on epic in JIRA (mark as synced)
    6. Return PullResult with summary

    Idempotency:
    - If epic already in state: update status only
    - If story already in state: update status only
    - New items get new local IDs assigned

    Args:
        client: Authenticated JIRA client
        epic_key: JIRA epic key (e.g., "DEMO-1")
        state: Current sync state (mutated in place)
        dry_run: If True, show what would happen without executing

    Returns:
        PullResult with imported/updated items
    """
```

**Pull output (CLI):**
```
Pulling from JIRA...

Epic: DEMO-1 "Product Governance Initiative" [In Progress]
  → Mapped to local: E-DEMO

Stories:
  DEMO-2: "Define governance principles" [Approved] → S-DEMO.1
  DEMO-3: "Create compliance checklist" [Approved] → S-DEMO.2
  DEMO-4: "Build approval workflow" [To Do] → S-DEMO.3

Summary: 1 epic, 3 stories synced.
State saved to .raise/rai/sync/state.json
```

### 2. Push Stories (`rai backlog push --source jira --epic E-DEMO`)

```python
def push_stories(
    client: JiraClient,
    epic_id: str,
    stories: list[LocalStory],
    state: SyncState,
    dry_run: bool = False,
) -> PushResult:
    """
    Push local stories to JIRA under mapped epic.

    Steps:
    1. Look up epic JIRA key from state (must exist from prior pull)
    2. For each local story:
       a. Check if already in state (skip if exists — idempotent)
       b. Create JIRA story under epic (via JiraClient.create_story)
       c. Set entity property on created story (RaiSyncMetadata)
       d. Update state.json with new mapping
    3. Return PushResult with created items

    Idempotency:
    - If story_id already in state.stories: skip (already pushed)
    - Entity properties set on new JIRA issues for cross-project visibility

    Args:
        client: Authenticated JIRA client
        epic_id: Local epic ID (e.g., "E-DEMO")
        stories: List of local stories to push
        state: Current sync state (mutated in place)
        dry_run: If True, show what would happen without executing

    Returns:
        PushResult with created/skipped items
    """
```

**Push output (CLI):**
```
Pushing stories to JIRA...

Epic: E-DEMO → DEMO-1 "Product Governance Initiative"

Stories:
  ✓ S-DEMO.1: "Define governance principles" → Created DEMO-2
  ✓ S-DEMO.2: "Create compliance checklist" → Created DEMO-3
  ✓ S-DEMO.3: "Build approval workflow" → Created DEMO-4
  - S-DEMO.4: Already synced (DEMO-5) — skipped

Summary: 3 created, 1 skipped.
State saved to .raise/rai/sync/state.json
```

### 3. Check Authorization (`rai backlog status --epic E-DEMO`)

```python
def check_authorization(
    state: SyncState,
    story_id: str,
    authorized_statuses: list[str] | None = None,
) -> AuthResult:
    """
    Check if story is authorized to work on (reads state.json only, no API call).

    Args:
        state: Current sync state
        story_id: Local story ID (e.g., "S-DEMO.1")
        authorized_statuses: JIRA statuses that mean "authorized"
                            Default: ["Approved", "Ready", "In Progress"]

    Returns:
        AuthResult with authorized flag and message
    """
```

**Status output (CLI):**
```
Authorization status for E-DEMO:

  ✓ S-DEMO.1: Approved (DEMO-2)           — Ready to work
  ✓ S-DEMO.2: Approved (DEMO-3)           — Ready to work
  ✗ S-DEMO.3: To Do (DEMO-4)              — Awaiting authorization
  ✗ S-DEMO.4: To Do (DEMO-5)              — Awaiting authorization
  - S-DEMO.5: Not synced                   — No JIRA mapping

Last sync: 2026-02-15 11:00 UTC (2 hours ago)
Run 'rai backlog pull --source jira' to refresh.
```

---

## LocalStory — Input for Push

The push operation needs to know what stories exist locally. For the demo, this is a simple list provided as input. Post-demo, this could read from epic scope/plan files.

```python
class LocalStory(BaseModel):
    """Local story data for push to JIRA."""
    story_id: str         # "S-DEMO.1"
    title: str            # "Define governance principles"
    description: str = "" # Optional description
    labels: list[str] = []
```

**For the demo:** Stories are passed explicitly to `push_stories()`. The CLI command reads them from a simple source (scope.md table, or hardcoded for demo rehearsal).

**Post-demo:** CLI parses epic scope.md or plan.md to extract story list automatically.

---

## CLI Commands

### `rai backlog pull`

```python
@backlog_app.command()
def pull(
    source: str = typer.Option(..., "--source", "-s", help="Provider (jira)"),
    epic: str = typer.Option(..., "--epic", "-e", help="JIRA epic key (e.g., DEMO-1)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without executing"),
    project: str = typer.Option(".", "--project", "-p", help="Project root path"),
) -> None:
    """Pull epic and stories from JIRA to local sync state."""
```

### `rai backlog push`

```python
@backlog_app.command()
def push(
    source: str = typer.Option(..., "--source", "-s", help="Provider (jira)"),
    epic: str = typer.Option(..., "--epic", "-e", help="Local epic ID (e.g., E-DEMO)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without executing"),
    project: str = typer.Option(".", "--project", "-p", help="Project root path"),
) -> None:
    """Push local stories to JIRA under mapped epic."""
```

### `rai backlog status`

```python
@backlog_app.command()
def status(
    epic: str = typer.Option(..., "--epic", "-e", help="Local epic ID"),
    project: str = typer.Option(".", "--project", "-p", help="Project root path"),
) -> None:
    """Show sync and authorization status for epic stories."""
```

---

## Testing Strategy

### Unit Tests (mocked JIRA client)

```python
# test_sync.py

class TestPullEpic:
    def test_pull_new_epic(self, mock_client, empty_state):
        """Pull epic that doesn't exist in state → creates mapping."""

    def test_pull_existing_epic_updates_status(self, mock_client, state_with_epic):
        """Pull epic already in state → updates status only."""

    def test_pull_with_stories(self, mock_client, empty_state):
        """Pull epic with 3 stories → all mapped in state."""

    def test_pull_dry_run_no_state_change(self, mock_client, empty_state):
        """Dry run → state unchanged, output shows what would happen."""

    def test_pull_assigns_local_ids(self, mock_client, empty_state):
        """Pulled items get sequential local IDs (E-DEMO, S-DEMO.1, etc.)."""


class TestPushStories:
    def test_push_new_stories(self, mock_client, state_with_epic):
        """Push stories not in state → creates JIRA issues."""

    def test_push_existing_stories_skipped(self, mock_client, state_with_stories):
        """Push stories already in state → skipped (idempotent)."""

    def test_push_sets_entity_properties(self, mock_client, state_with_epic):
        """Each created JIRA story gets entity property set."""

    def test_push_dry_run_no_jira_calls(self, mock_client, state_with_epic):
        """Dry run → no JIRA API calls, state unchanged."""

    def test_push_without_epic_mapping_raises(self, mock_client, empty_state):
        """Push for unmapped epic → clear error message."""


class TestCheckAuthorization:
    def test_authorized_story(self, state_with_approved):
        """Story with 'Approved' status → authorized."""

    def test_unauthorized_story(self, state_with_todo):
        """Story with 'To Do' status → not authorized."""

    def test_unsynced_story(self, empty_state):
        """Story not in state → no JIRA mapping, no gate."""

    def test_custom_authorized_statuses(self, state_with_custom_status):
        """Custom status list overrides default."""
```

### Unit Tests (sync state)

```python
# test_sync_state.py

class TestSyncState:
    def test_load_nonexistent_returns_empty(self, tmp_path):
        """Load from missing file → empty state."""

    def test_save_and_load_roundtrip(self, tmp_path):
        """Save state → load state → identical."""

    def test_add_epic_mapping(self, empty_state):
        """Add epic → state.epics updated."""

    def test_add_story_mapping(self, state_with_epic):
        """Add story → state.stories updated."""

    def test_state_file_permissions(self, tmp_path):
        """State file created with 0644 permissions."""

    def test_creates_directory_if_missing(self, tmp_path):
        """Save creates .raise/rai/sync/ if missing."""
```

### Integration Test (live JIRA, manual)

```bash
# Run against test JIRA project
# Requires: JIRA OAuth credentials configured

# 1. Pull test epic
rai backlog pull --source jira --epic DEMO-1

# 2. Verify state.json created
cat .raise/rai/sync/state.json

# 3. Push test stories
rai backlog push --source jira --epic E-DEMO

# 4. Verify stories in JIRA (manual check)

# 5. Change status in JIRA (manual)

# 6. Pull again → verify status updated
rai backlog pull --source jira --epic DEMO-1

# 7. Check authorization
rai backlog status --epic E-DEMO
```

**Coverage target:** >90% on sync.py and sync_state.py

---

## Acceptance Criteria

### MUST (Demo Blockers)

- [ ] `rai backlog pull --source jira --epic KEY` reads epic + stories from JIRA
- [ ] Pull creates/updates `.raise/rai/sync/state.json` with mappings
- [ ] Pull sets entity properties on JIRA epic (marks as synced)
- [ ] `rai backlog push --source jira --epic ID` creates stories in JIRA
- [ ] Push is idempotent (re-running doesn't create duplicates)
- [ ] Push sets entity properties on each created story
- [ ] Push updates state.json with new JIRA keys
- [ ] `rai backlog status --epic ID` shows authorization state
- [ ] Status reads state.json only (no JIRA API call)
- [ ] Unit tests pass (>90% coverage)
- [ ] Quality gates: pyright strict, ruff, bandit all pass

### SHOULD (Demo Polish)

- [ ] `--dry-run` flag shows preview without executing
- [ ] Pull updates story statuses on re-run (status sync)
- [ ] Clear error messages when epic not found, auth expired, etc.
- [ ] Rich CLI output (colors, checkmarks, progress)

### MUST NOT

- [ ] Must NOT modify `governance/backlog.md` programmatically
- [ ] Must NOT store sync state in memory graph (`.raise/rai/memory/`)
- [ ] Must NOT call JIRA API from authorization check (offline only)
- [ ] Must NOT auto-detect epics (explicit `--epic` flag required)
- [ ] Must NOT implement webhook/polling (manual triggers only)

---

## Task Decomposition (Atomic, TDD)

### Task 1: Sync State Management (~45 min)
**Files:** `sync_state.py`, `test_sync_state.py`
- Pydantic models: `SyncMapping`, `SyncState`
- Functions: `load_state()`, `save_state()`, `get_sync_dir()`
- Creates `.raise/rai/sync/` directory if missing
- Tests: roundtrip, empty state, directory creation
- **Gate:** Tests pass, pyright clean

### Task 2: Pull Operation (~60 min)
**Files:** `sync.py`, `test_sync.py` (pull tests)
- Function: `pull_epic(client, epic_key, state, dry_run)`
- Reads epic + stories from JIRA
- Updates state with mappings
- Sets entity property on JIRA epic
- Assigns local IDs (E-{name}, S-{name}.{N})
- Tests: new epic, existing epic, with stories, dry run
- **Gate:** Tests pass, pyright clean

### Task 3: Push Operation (~60 min)
**Files:** `sync.py`, `test_sync.py` (push tests)
- Function: `push_stories(client, epic_id, stories, state, dry_run)`
- Reads epic JIRA key from state (error if not mapped)
- Creates JIRA stories (skips if already in state)
- Sets entity properties on created stories
- Updates state with new JIRA keys
- Tests: new stories, idempotency, dry run, no mapping error
- **Gate:** Tests pass, pyright clean

### Task 4: Authorization Check (~30 min)
**Files:** `sync.py`, `test_sync.py` (auth tests)
- Function: `check_authorization(state, story_id, authorized_statuses)`
- Reads state.json (offline, no API call)
- Returns `AuthResult(authorized, message, jira_status)`
- Default authorized statuses: ["Approved", "Ready", "In Progress"]
- Tests: authorized, unauthorized, unsynced, custom statuses
- **Gate:** Tests pass, pyright clean

### Task 5: CLI Commands (~45 min)
**Files:** `backlog.py` (modify)
- Commands: `pull`, `push`, `status`
- OAuth token loading, client initialization
- Calls sync engine functions
- Rich output (console.print with colors)
- Error handling (auth expired, JIRA errors)
- **Gate:** Commands execute, help text correct

### Task 6: Integration Test (~30 min)
**Files:** integration test script
- End-to-end test with live JIRA
- Pull → push → status → verify
- Manual validation checklist
- **Gate:** Full workflow completes against test JIRA project

---

## Estimated Time

| Task | Estimate | Cumulative |
|------|----------|------------|
| Task 1: Sync State | 45 min | 0:45 |
| Task 2: Pull | 60 min | 1:45 |
| Task 3: Push | 60 min | 2:45 |
| Task 4: Auth Check | 30 min | 3:15 |
| Task 5: CLI | 45 min | 4:00 |
| Task 6: Integration | 30 min | 4:30 |

**Total estimate:** 4-5 hours (including TDD overhead)
**Buffer:** 1 hour for unexpected issues

---

## References

- **ADR-027:** Sync engine architecture (local-first, hub-and-spoke)
- **ADR-028:** Entity schema design (entity properties, property key)
- **S-DEMO.3:** JIRA client (`JiraClient`, `read_epic()`, `create_story()`)
- **S-DEMO.4:** Entity properties (`set_entity_property()`, `get_entity_property()`)
- **Blast radius:** `work/epics/e-demo-jira-sync/blast-radius-and-post-demo.md`

---

*Design created: 2026-02-15 05:50 AM*
*Deadline: 2026-02-16 11:00 AM (29 hours remaining)*
*Next: `/rai-story-plan` → `/rai-story-implement`*
