---
type: module
name: memory
purpose: "Manage Rai's persistent memory — patterns, calibration, and sessions stored as JSONL"
status: current
depends_on: [config]
depended_by: [cli, context, session]
entry_points:
  - "rai pattern add"
  - "rai pattern reinforce"
  - "rai memory emit"
  - "rai memory emit-work"
  - "rai memory add-pattern (deprecated → rai pattern add)"
  - "rai memory reinforce (deprecated → rai pattern reinforce)"
public_api:
  - "CalibrationInput"
  - "MemoryConcept"
  - "MemoryConceptType"
  - "MemoryRelationship"
  - "MemoryRelationshipType"
  - "MemoryScope"
  - "MigrationResult"
  - "PatternInput"
  - "PatternSubType"
  - "SessionInput"
  - "WriteResult"
  - "append_calibration"
  - "append_pattern"
  - "append_session"
  - "get_memory_dir_for_scope"
  - "migrate_to_personal"
  - "needs_migration"
components: 34
constraints:
  - "JSONL files are append-only — no in-place edits"
  - "Three-tier architecture: global > project > personal"
  - "Backward compatibility: reader handles both old and new schemas (PAT-153)"
---

## Purpose

The memory module is how Rai learns across sessions. It manages three types of memory stored as JSONL files: **patterns** (learned insights like "TDD catches integration bugs early"), **calibration** (estimation data like "this M-sized story took 45 minutes"), and **sessions** (what happened in each working session). Together, they form Rai's accumulated judgment.

The three-tier architecture (global `~/.rai/`, project `.raise/rai/memory/`, personal `.raise/rai/personal/`) enables multi-developer repos without conflicts — each developer has their own session history while sharing project-level patterns.

## Architecture

```
/session-close → append_session() → .raise/rai/personal/sessions/index.jsonl
/story-review  → append_pattern() → .raise/rai/memory/patterns.jsonl (PAT-{X}-NNN)
                → append_calibration() → .raise/rai/personal/calibration.jsonl
                                                    ↓
                              rai memory build → UnifiedGraphBuilder
                                                    ↓
                              rai memory query → results
```

## Key Files

- **`models.py`** — Pydantic models for memory concepts: `MemoryConcept`, `MemoryScope` (global/project/personal), `PatternSubType` (process/codebase/universal), relationship types.
- **`writer.py`** — Append-only JSONL writers: `append_pattern()`, `append_calibration()`, `append_session()`. Each takes a typed input model and returns a `WriteResult`. Handles ID generation (with optional developer prefix for multi-dev safety) and timestamp creation.
- **`loader.py`** — Read and parse JSONL files. Used by the graph builder to load memory into the unified graph.
- **`migration.py`** — Migration utilities for the v1→v2 data model change (sessions moved from project to personal directory).

## Dependencies

| Depends On | Why |
|-----------|-----|
| `config` | Directory resolution for three-tier paths |

## Conventions

- JSONL is append-only — never edit or delete lines in place
- New fields use backward-compatible pattern: read new key first, fall back to old key (PAT-153)
- Pattern IDs use developer prefix: PAT-{X}-NNN (e.g., PAT-A-001 for Alice, PAT-B-001 for Bob)
- Calibration and session IDs remain sequential: CAL-001, SES-001
- Session and calibration data is personal-scoped (developer-specific, gitignored)
- Pattern data is project-scoped (shared, committed) with developer-prefixed IDs to prevent collisions
