# Epic Design: Session Identity Fix

> **Epic:** E654
> **Jira:** RAISE-654

---

## Gemba Summary

**Current state** (from code analysis, SES-355):

| Component | File | Lines | Role |
|-----------|------|-------|------|
| Path constants | `config/paths.py` | 383 | Directory structure, `get_session_dir()` |
| Session resolver | `session/resolver.py` | 127 | `SES-NNN` normalization, flag/env resolution |
| Session CLI | `cli/commands/session.py` | 582 | `start`, `close`, `journal`, `list` commands |
| Session close | `session/close.py` | 270 | Structured close, pattern extraction |
| Session state | `session/state.py` | 206 | State persistence (YAML read/write) |
| Session journal | `session/journal.py` | 119 | Journal entries (JSONL) |
| Context bundle | `session/bundle.py` | 820 | Orientation bundle assembly |
| Memory writer | `memory/writer.py` | 609 | `get_next_id()`, session ID generation |
| Developer profile | `onboarding/profile.py` | 622 | `~/.rai/developer.yaml`, `ActiveSession` model |

**Current storage layout:**
```
~/.rai/developer.yaml                          ← global, active_sessions list
.raise/rai/personal/sessions/                   ← gitignored
  ├── index.jsonl                               ← session ledger (per-project counter)
  └── SES-NNN/                                  ← per-session working state
      ├── state.yaml
      ├── signals.jsonl
      └── journal.jsonl
```

**Failure modes identified:** F1 (no auto env export), F2 (no terminal binding), F3 (stale active_sessions), F4 (counter diverges across environments), F5 (flat state overwrite), F6 (no cleanup), F7 (no agent tracking).

## Target Architecture

```
~/.rai/developer.yaml                          ← global (unchanged: name, prefix, active_sessions)

.raise/rai/sessions/                            ← IN GIT (new, committed)
  ├── prefixes.yaml                             ← developer prefix registry
  └── {prefix}/                                 ← per-developer directory
      └── index.jsonl                           ← session ledger (timestamp IDs)

.raise/rai/personal/                            ← GITIGNORED (unchanged location)
  ├── active-session                            ← current session pointer (new)
  └── sessions/
      └── SES-{prefix}-{YYYYMMDD}T{HHMM}/      ← per-session working state
          ├── state.yaml
          ├── signals.jsonl
          └── journal.jsonl
```

### Key Contracts

**Session ID format:**
```
SES-{prefix}-{YYYYMMDD}T{HHMM}
Example: SES-E-20260322T1430
```

**Index entry (JSONL, one line per session):**
```json
{"id": "SES-E-20260322T1430", "name": "gemba session identity", "started": "2026-03-22T14:30:22", "closed": "2026-03-22T18:45:11", "type": "research", "summary": "...", "outcomes": [...], "branch": "dev"}
```

**Prefix registry (`prefixes.yaml`):**
```yaml
E: {name: "Emilio Osorio", registered: "2026-03-22"}
J: {name: "Juan Pérez", registered: "2026-03-25"}
```

**Active session pointer (plain text file):**
```
SES-E-20260322T1430
```

### Affected Components (change summary)

| Component | Change type | Impact |
|-----------|------------|--------|
| `config/paths.py` | Add new path constants | New: `SHARED_SESSIONS_DIR`, `PREFIXES_FILE`, `ACTIVE_SESSION_FILE` |
| `session/resolver.py` | Rewrite normalization | Support new `SES-{prefix}-{timestamp}` format + backward compat for `SES-NNN` |
| `memory/writer.py` | Rewrite `get_next_id()` for sessions | Timestamp-based, no counter read needed |
| `cli/commands/session.py` | Update start/close/list | `--name` required on start, index write on close, new list format |
| `session/close.py` | Write to shared index | Append to `.raise/rai/sessions/{prefix}/index.jsonl` |
| `onboarding/profile.py` | Minor | ActiveSession model uses new ID format |
| `session/bundle.py` | Read from shared index | Context bundle reads shared index for history |
| `session/state.py` | Minor | Path changes for working state |
| `session/journal.py` | Unchanged | Still writes to local per-session dir |
| NEW: `session/migration.py` | New module | One-time migration of old `SES-NNN` → new format |
| NEW: `session/prefix.py` | New module | Prefix registry management |

## Stories

### S654.1 — Session ID Model & Prefix Registry (S)

New session identity model: timestamp-based IDs, prefix registry, path constants.

**Delivers:** `SES-{prefix}-{YYYYMMDD}T{HHMM}` generation, `prefixes.yaml` management, updated path helpers.
**Modules:** `config/paths.py`, new `session/prefix.py`, `memory/writer.py` (session ID generation)
**Dependencies:** None (foundation)

### S654.2 — Shared Session Index (M)

Move session index from gitignored personal dir to committed shared dir, per-developer subdirectories.

**Delivers:** `.raise/rai/sessions/{prefix}/index.jsonl` (committed), read/write operations, active session pointer.
**Modules:** `session/close.py`, `session/state.py`, `config/paths.py`
**Dependencies:** S654.1

### S654.3 — CLI Adaptation (M)

Update all `rai session` commands to work with new identity model and shared index.

**Delivers:** `--name` on start (required), updated `list` output (shows names), `close` writes to shared index, resolver handles new format.
**Modules:** `cli/commands/session.py`, `session/resolver.py`
**Dependencies:** S654.1, S654.2

### S654.4 — Context Bundle & Orientation (S)

Update session bundle assembly to read from shared index for session history and continuity.

**Delivers:** `rai session start --context` reads shared index, cross-environment session history visible.
**Modules:** `session/bundle.py`
**Dependencies:** S654.2, S654.3

### S654.5 — Migration (S)

One-time auto-migration of existing `SES-NNN` sessions to new format.

**Delivers:** `session/migration.py` — detects old format, converts index entries, moves working state directories. Runs automatically on first `session start` after upgrade.
**Modules:** New `session/migration.py`, called from `cli/commands/session.py`
**Dependencies:** S654.1, S654.2 (needs new format defined and storage ready)

## Dependency Graph

```
S654.1 (ID model + prefix)
  ├── S654.2 (shared index) ──┐
  │     └── S654.4 (bundle)   │
  └── S654.3 (CLI) ───────────┘
        └── S654.5 (migration)
```

No cycles. S654.1 is the foundation. S654.4 and S654.5 are leaf stories that can run in parallel after their dependencies.

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Migration corrupts existing session data | Low | High | Backup before migration, dry-run mode, rollback path |
| Git merge conflicts on shared index | Low | Medium | Per-developer directories eliminate multi-dev conflicts; same-dev JSONL append-only merges cleanly |
| Breaking `rai session` CLI contract | Medium | High | TDD against current CLI behavior, backward-compatible resolver |

## Parking Lot

- **Session cleanup command** — `rai session cleanup` to remove old local working state directories. Promote when disk usage is a complaint.
- **Session search/filter** — `rai session list --filter "gemba"` fuzzy search. Promote after new format stabilizes.
- **Git auto-commit on session close** — automatically commit the index update. Promote if manual commit is friction.
