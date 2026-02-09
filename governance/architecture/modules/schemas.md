---
type: module
name: schemas
purpose: "Shared Pydantic models for cross-module data structures — currently contains SessionState for session continuity"
status: current
depends_on: []
depended_by: [session]
entry_points: []
public_api:
  - "SessionState"
  - "CurrentWork"
  - "LastSession"
  - "PendingItems"
  - "EpicProgress"
components: 5
constraints:
  - "No internal dependencies — leaf module"
  - "Only types needed by 3+ modules should live here"
  - "Module-specific types stay in their owning module"
---

## Purpose

The schemas module holds shared Pydantic models needed by multiple modules to avoid circular dependencies. Currently it contains the `SessionState` model and related types (CurrentWork, LastSession, PendingItems, EpicProgress) used by the session module for state persistence and by the CLI for session commands.

Most data models live in their owning modules (e.g., `discovery.scanner.Symbol`, `memory.models.MemoryConcept`) — this module is for types that genuinely need to be shared across module boundaries.

## Key Files

- **`__init__.py`** — Module stub. Exports nothing (types imported directly from submodules).
- **`session_state.py`** — `SessionState` and related models for project-level working state persistence in `.raise/rai/session-state.yaml`.

## Dependencies

None — leaf module by design.

## Conventions

- Only types needed by 2+ modules should live here to avoid circular dependencies
- Module-specific types stay in their owning module (don't prematurely extract)
- All models use Pydantic BaseModel for validation and serialization
- Follow progressive directory structure (PAT-158): start minimal, grow when needed
