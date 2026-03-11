---
type: module
name: session
purpose: "Session lifecycle — state persistence, context bundle assembly, and close orchestration for deterministic session continuity"
status: current
depends_on: [context, memory, onboarding, schemas]
depended_by: [cli]
entry_points:
  - "rai session start"
  - "rai session close"
public_api:
  - "assemble_context_bundle"
  - "get_foundational_patterns"
  - "get_always_on_primes"
  - "process_session_close"
  - "load_state_file"
  - "CloseInput"
  - "CloseResult"
  - "load_session_state"
  - "save_session_state"
components: 21
constraints:
  - "Session records are always personal-scoped (developer-specific, gitignored)"
  - "Session state is personal-scoped (per-developer, gitignored in .raise/rai/personal/)"
  - "Context bundle is deterministic — same inputs produce same output"
  - "Close writes are atomic — all-or-nothing via single orchestrator"
---

## Purpose

The session module manages the lifecycle of working sessions — starting them (loading context), and closing them (persisting state). It ensures continuity across sessions by assembling a deterministic context bundle on start and writing structured state on close.

Key distinction: **session records** (what happened) and **session state** (current work focus) are both personal data in `.raise/rai/personal/`, gitignored per-developer. Patterns are shared project data.

## Architecture

```
/session-start → assemble_context_bundle()
                    ├── ~/.rai/developer.yaml (profile + coaching + pattern_prefix)
                    ├── .raise/rai/personal/session-state.yaml (current work)
                    ├── .raise/rai/memory/index.json (graph primes, gitignored)
                    └── .raise/rai/personal/sessions/index.jsonl (recent sessions)

/session-close → process_session_close()
                    ├── .raise/rai/personal/sessions/index.jsonl (append session record)
                    ├── .raise/rai/memory/patterns.jsonl (append patterns with PAT-{X}-NNN)
                    ├── ~/.rai/developer.yaml (update coaching + clear current_session)
                    └── .raise/rai/personal/session-state.yaml (update current work state)
```

## Key Files

- **`bundle.py`** — Context bundle assembly for session start. Reads from four sources (profile, session state, graph, recent sessions) and produces a token-optimized bundle (~600 tokens) for the AI partner.
- **`close.py`** — Session close orchestrator. Processes structured session output (patterns, corrections, coaching, state) and performs all writes atomically. Entry point: `process_session_close()`.
- **`state.py`** — Session state persistence. Simple YAML read/write for `SessionState` model at `.raise/rai/personal/session-state.yaml`. Includes auto-migration from legacy `.raise/rai/session-state.yaml` path.

## Dependencies

| Depends On | Why |
|-----------|-----|
| `memory` | `append_session()`, `append_pattern()` for JSONL writes |
| `onboarding` | Profile management: `save_developer_profile()`, `update_coaching()`, `add_correction()` |
| `schemas` | `SessionState` Pydantic model |
| `context` | `UnifiedGraph` for querying foundational patterns and always-on primes |

## Data Flow & Scoping

| Data | Scope | Path | Why |
|------|-------|------|-----|
| Session records | Personal | `.raise/rai/personal/sessions/index.jsonl` | Developer-specific history, gitignored |
| Session state | Personal | `.raise/rai/personal/session-state.yaml` | Per-developer work focus, gitignored |
| Patterns | Project | `.raise/rai/memory/patterns.jsonl` | Shared learnings, committed. IDs: PAT-{X}-NNN |
| Calibration | Personal | `.raise/rai/personal/calibration.jsonl` | Per-developer coaching data, gitignored |
| Developer profile | Global | `~/.rai/developer.yaml` | Cross-project identity + pattern_prefix |

## Conventions

- Context bundle is read-only — it gathers but never writes
- Close orchestrator is write-only — it persists but never reads context
- Session IDs are sequential (SES-001, SES-002, ...) within personal scope
- The skill layer (`/session-start`, `/session-close`) handles inference; the module handles data plumbing
