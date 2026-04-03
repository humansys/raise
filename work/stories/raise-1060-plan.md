# RAISE-1060: Adapter Models Restructure — Plan

## Tasks

### T1: RED — Tests for new structure (TDD gate)
- Write test that imports from `raise_cli.adapters.models.pm` → should fail (module doesn't exist)
- Write test that imports from `raise_cli.adapters.models.docs` → should fail
- Write test that imports `SpaceInfo` from `raise_cli.adapters.models` → should fail
- Write test that imports `BacklogItem` from `raise_cli.adapters.filesystem_models` → should fail
- **Expected: all 4 fail**

### T2: GREEN — Create models/ package with per-protocol modules
- Create `models/` directory
- Create `models/pm.py` — move IssueSpec, IssueRef, IssueDetail, IssueSummary, Comment, CommentRef, FailureDetail, BatchResult + shared field descriptions
- Create `models/docs.py` — move PageContent, PageSummary, PublishResult + add SpaceInfo
- Create `models/governance.py` — move CoreArtifactType, ArtifactLocator
- Create `models/health.py` — move AdapterHealth
- Create `models/__init__.py` — re-export all public names
- Delete `models.py`
- **Gate: T1 tests pass (except BacklogItem which is T3)**

### T3: GREEN — Extract filesystem internals
- Create `filesystem_models.py` — move BacklogItem, BacklogLink, BacklogComment
- Update `filesystem.py` imports
- Update `tests/adapters/test_filesystem.py` imports
- **Gate: T1 BacklogItem test passes**

### T4: GREEN — Update adapters/__init__.py
- Add SpaceInfo to imports and __all__
- Verify import path works

### T5: REFACTOR — Verify zero regressions
- Run full pytest for raise-cli
- Run pyright
- Run ruff check + format
- **Gate: all green, zero changes to any test logic**

### T6: Commit
- One clean commit for the restructure

## Sequence
T1 → T2 → T3 → T4 → T5 → T6
All sequential — each depends on the previous.
