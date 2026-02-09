---
type: module
name: memory
purpose: "Manage Rai's persistent memory — patterns, calibration, and sessions stored as JSONL"
status: current
depends_on: [config]
depended_by: [cli, context, session]
entry_points:
  - "raise memory add"
  - "raise memory emit"
  - "raise memory emit-work"
public_api:
  - "append_pattern"
  - "append_calibration"
  - "append_session"
  - "PatternInput"
  - "CalibrationInput"
  - "SessionInput"
  - "MemoryScope"
  - "MemoryConcept"
components: 30
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
/story-review  → append_pattern() → .raise/rai/memory/patterns.jsonl
                → append_calibration() → .raise/rai/memory/calibration.jsonl
                                                    ↓
                              raise memory build → UnifiedGraphBuilder
                                                    ↓
                              raise memory query → results
```

## Key Files

- **`models.py`** — Pydantic models for memory concepts: `MemoryConcept`, `MemoryScope` (global/project/personal), `PatternSubType` (process/codebase/universal), relationship types.
- **`writer.py`** — Append-only JSONL writers: `append_pattern()`, `append_calibration()`, `append_session()`. Each takes a typed input model and returns a `WriteResult`. Handles ID generation and timestamp creation.
- **`loader.py`** — Read and parse JSONL files. Used by the graph builder to load memory into the unified graph.
- **`migration.py`** — Migration utilities for the v1→v2 data model change (sessions moved from project to personal directory).

## Dependencies

| Depends On | Why |
|-----------|-----|
| `config` | Directory resolution for three-tier paths |

## Conventions

- JSONL is append-only — never edit or delete lines in place
- New fields use backward-compatible pattern: read new key first, fall back to old key (PAT-153)
- IDs are auto-generated with sequential numbering (PAT-001, CAL-001, SES-001)
- Session data is always personal-scoped (developer-specific)
- Pattern and calibration data defaults to project-scoped (shared)
