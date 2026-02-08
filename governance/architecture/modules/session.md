---
type: module
name: session
purpose: "Session lifecycle — state persistence, context bundle assembly, and close orchestration for deterministic session continuity"
status: current
depends_on: [memory, onboarding, schemas, context]
depended_by: [cli]
entry_points:
  - "raise session start"
  - "raise session close"
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
components: 12
constraints:
  - "Session records are always personal-scoped (developer-specific, gitignored)"
  - "Session state is project-scoped (committed, shared across developers)"
  - "Context bundle is deterministic — same inputs produce same output"
  - "Close writes are atomic — all-or-nothing via single orchestrator"
---

## Purpose

The session module manages the lifecycle of working sessions — starting them (loading context), and closing them (persisting state). It ensures continuity across sessions by assembling a deterministic context bundle on start and writing structured state on close.

Key distinction: **session records** (what happened) are personal data in `.raise/rai/personal/sessions/`, while **session state** (current work focus) is project data in `.raise/rai/session-state.yaml`.

## Architecture

```
/session-start → assemble_context_bundle()
                    ├── ~/.rai/developer.yaml (profile + coaching)
                    ├── .raise/rai/session-state.yaml (current work)
                    ├── .raise/rai/memory/index.json (graph primes)
                    └── .raise/rai/personal/sessions/index.jsonl (recent sessions)

/session-close → process_session_close()
                    ├── .raise/rai/personal/sessions/index.jsonl (append session record)
                    ├── .raise/rai/memory/patterns.jsonl (append patterns)
                    ├── ~/.rai/developer.yaml (update coaching + clear current_session)
                    └── .raise/rai/session-state.yaml (update current work state)
```

## Key Files

- **`bundle.py`** — Context bundle assembly for session start. Reads from four sources (profile, session state, graph, recent sessions) and produces a token-optimized bundle (~600 tokens) for the AI partner.
- **`close.py`** — Session close orchestrator. Processes structured session output (patterns, corrections, coaching, state) and performs all writes atomically. Entry point: `process_session_close()`.
- **`state.py`** — Session state persistence. Simple YAML read/write for `SessionState` model at `.raise/rai/session-state.yaml`.

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
| Session state | Project | `.raise/rai/session-state.yaml` | Shared work focus, committed |
| Patterns | Project | `.raise/rai/memory/patterns.jsonl` | Shared learnings, committed |
| Developer profile | Global | `~/.rai/developer.yaml` | Cross-project identity |

## Conventions

- Context bundle is read-only — it gathers but never writes
- Close orchestrator is write-only — it persists but never reads context
- Session IDs are sequential (SES-001, SES-002, ...) within personal scope
- The skill layer (`/session-start`, `/session-close`) handles inference; the module handles data plumbing
