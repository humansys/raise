# Implementation Plan: F7.8 Personal Memory

## Overview

- **Feature:** F7.8 Personal Memory
- **Epic:** E7 Onboarding
- **Story Points:** 2 SP
- **Feature Size:** S
- **Created:** 2026-02-04

## Scope (from /story-start)

**In:**
- `~/.rai/developer.yaml` schema (Pydantic model)
- Read/write functions for personal profile
- Experience level enum (shu/ha/ri)
- Basic fields: name, experience_level, sessions_total

**Out:**
- Skill mastery tracking → F7.7
- Universal patterns → post-F&F
- Auto-progression logic → post-F&F

## Tasks

### Task 1: DeveloperProfile Schema

- **Description:** Create Pydantic model for `~/.rai/developer.yaml` with core fields
- **Files:**
  - `src/raise_cli/onboarding/__init__.py` (new module)
  - `src/raise_cli/onboarding/profile.py` (new)
  - `tests/onboarding/test_profile.py` (new)
- **TDD Cycle:**
  - RED: Test DeveloperProfile validates required fields
  - RED: Test ExperienceLevel enum has shu/ha/ri
  - GREEN: Implement models
  - REFACTOR: Clean up
- **Verification:** `pytest tests/onboarding/test_profile.py -v`
- **Size:** S
- **Dependencies:** None

**Schema (from epic scope):**
```python
class ExperienceLevel(str, Enum):
    SHU = "shu"  # Beginner - explain everything
    HA = "ha"    # Intermediate - explain new concepts
    RI = "ri"    # Expert - minimal ceremony

class DeveloperProfile(BaseModel):
    name: str
    experience_level: ExperienceLevel = ExperienceLevel.SHU
    sessions_total: int = 0
    first_session: date | None = None
    last_session: date | None = None
    projects: list[str] = Field(default_factory=list)
```

### Task 2: Profile Read/Write Functions

- **Description:** Implement load_developer_profile() and save_developer_profile() with ~/.rai/ directory handling
- **Files:**
  - `src/raise_cli/onboarding/profile.py` (extend)
  - `tests/onboarding/test_profile.py` (extend)
- **TDD Cycle:**
  - RED: Test load_developer_profile returns None if file missing
  - RED: Test load_developer_profile returns DeveloperProfile if exists
  - RED: Test save_developer_profile creates ~/.rai/ if missing
  - RED: Test save_developer_profile writes valid YAML
  - GREEN: Implement functions
  - REFACTOR: Error handling, edge cases
- **Verification:** `pytest tests/onboarding/test_profile.py -v`
- **Size:** S
- **Dependencies:** Task 1

**Functions:**
```python
def get_rai_home() -> Path:
    """Get ~/.rai/ directory path."""

def load_developer_profile() -> DeveloperProfile | None:
    """Load developer profile from ~/.rai/developer.yaml."""

def save_developer_profile(profile: DeveloperProfile) -> None:
    """Save developer profile to ~/.rai/developer.yaml."""
```

### Task 3: Manual Integration Test

- **Description:** Validate story works end-to-end with real ~/.rai/ directory
- **Verification:**
  1. Delete ~/.rai/developer.yaml (backup first if exists)
  2. Run Python: `from raise_cli.onboarding.profile import *`
  3. Verify `load_developer_profile()` returns None
  4. Create profile: `save_developer_profile(DeveloperProfile(name="Test"))`
  5. Verify `~/.rai/developer.yaml` exists with correct content
  6. Verify `load_developer_profile()` returns the saved profile
  7. Restore backup
- **Size:** XS
- **Dependencies:** Task 1, Task 2

## Execution Order

1. **Task 1** — Schema (foundation)
2. **Task 2** — Read/Write (depends on 1)
3. **Task 3** — Integration test (final validation)

## Risks

- **YAML library choice:** Use PyYAML (already a dependency) or ruamel.yaml for round-trip
  - **Mitigation:** Check existing dependencies, prefer what's already used

## Duration Tracking

| Task | Size | Estimated | Actual | Notes |
|------|:----:|:---------:|:------:|-------|
| 1. Schema | S | 20 min | — | |
| 2. Read/Write | S | 25 min | — | |
| 3. Integration | XS | 5 min | — | |
| **Total** | S | 50 min | — | |

---

*Plan created: 2026-02-04*
*Next: `/story-implement`*
