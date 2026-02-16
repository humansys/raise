---
story_id: "RAISE-138"
title: "Per-Session State Isolation"
epic_ref: "RAISE-127 Session Instance Isolation"
story_points: 3
complexity: "moderate"
status: "draft"
version: "1.0"
created: "2026-02-15"
updated: "2026-02-15"
template: "lean-feature-spec-v2"
---

# Feature: Per-Session State Isolation

> **Epic**: RAISE-127 - Session Instance Isolation
> **Complexity**: moderate | **SP**: 3

---

## 1. What & Why

**Problem**: Session state (`session-state.yaml`) and telemetry (`signals.jsonl`) are shared flat files. When two agents run concurrently, they overwrite each other's state and interleave telemetry signals. RAISE-137 gave us session tokens, but state still writes to the same files.

**Value**: Each session gets its own directory, making concurrent sessions produce independent, correct state. This is the core isolation mechanism — without it, session tokens are identifiers with no isolation.

---

## 2. Approach

**How we'll solve it**: Each session gets a directory at `.raise/rai/personal/sessions/{SES-NNN}/` containing its own `state.yaml` and `signals.jsonl`. Session start creates the directory; session close cleans it up. The shared session ledger (`sessions/index.jsonl`) uses fcntl locking for concurrent appends.

**Architectural Context**:
- **Primary module**: `mod-session` (state.py, close.py, bundle.py)
- **Secondary**: `mod-config` (paths.py — leaf layer, shared kernel)
- **Tertiary**: `mod-telemetry` (writer.py — emit to per-session dir)
- **Layer rule**: config is leaf (no internal deps) → session depends on config → telemetry depends on config
- **ADR**: ADR-029 (Session Instance Isolation)

**Components affected**:
- **`src/rai_cli/config/paths.py`**: Modify — add `get_session_dir(session_id, project_root)` path helper
- **`src/rai_cli/session/state.py`**: Modify — `load/save_session_state` use per-session dir, add migration from flat layout
- **`src/rai_cli/session/close.py`**: Modify — cleanup session directory after close, write state to per-session dir
- **`src/rai_cli/session/bundle.py`**: Modify — load state from per-session dir
- **`src/rai_cli/telemetry/writer.py`**: Modify — accept optional `session_id` param, write to per-session signals.jsonl
- **`src/rai_cli/cli/commands/session.py`**: Modify — wire session dir creation on start, pass session_id to telemetry

---

## 3. Interface / Examples

### Directory Layout (after)

```
.raise/rai/personal/
├── sessions/
│   ├── index.jsonl              # Shared ledger (fcntl-locked, unchanged)
│   ├── SES-177/                 # Session instance 1
│   │   ├── state.yaml           # This session's working state
│   │   └── signals.jsonl        # This session's telemetry
│   ├── SES-178/                 # Session instance 2
│   │   ├── state.yaml
│   │   └── signals.jsonl
├── telemetry/
│   └── signals.jsonl            # Legacy (migrated, then removed)
└── session-state.yaml           # Legacy (migrated, then removed)
```

### Path Helper

```python
# In config/paths.py
def get_session_dir(session_id: str, project_root: Path | None = None) -> Path:
    """Get per-session directory: .raise/rai/personal/sessions/{SES-NNN}/"""
    return get_personal_dir(project_root) / SESSIONS_DIR / session_id
```

### Session State (per-session)

```python
# state.py — updated signatures
def get_session_state_path(project_path: Path, session_id: str) -> Path:
    """Get path: .raise/rai/personal/sessions/{session_id}/state.yaml"""
    return get_session_dir(session_id, project_path) / "state.yaml"

def load_session_state(project_path: Path, session_id: str | None = None) -> SessionState | None:
    """Load state from per-session dir. Falls back to flat file for migration."""

def save_session_state(project_path: Path, state: SessionState, session_id: str | None = None) -> None:
    """Save state to per-session dir. Creates dir if needed."""
```

### Telemetry (per-session)

```python
# telemetry/writer.py — updated emit
def emit(
    signal: Signal,
    *,
    base_path: Path | None = None,
    session_id: str | None = None,   # NEW: write to per-session dir
) -> EmitResult:
    """If session_id provided, writes to sessions/{session_id}/signals.jsonl.
    Otherwise falls back to personal/telemetry/signals.jsonl (legacy)."""
```

### Migration (flat → per-session)

```python
def migrate_flat_to_session(project_path: Path, session_id: str) -> bool:
    """One-time migration on first session start with new code.

    Moves:
    - personal/session-state.yaml → personal/sessions/{session_id}/state.yaml
    - personal/telemetry/signals.jsonl → personal/sessions/{session_id}/signals.jsonl

    Returns True if migration occurred, False if nothing to migrate.
    """
```

**IMPORTANT**: Migration runs during `rai session start` when old flat files exist and the session directory doesn't. The last session ID from index.jsonl determines which session dir receives the migrated files.

### Session Close (cleanup)

```python
# close.py — after all writes complete
def cleanup_session_dir(project_path: Path, session_id: str) -> None:
    """Remove per-session directory after close.

    Only removes if session_id matches a real session dir.
    Does NOT remove shared files (index.jsonl, memory/).
    """
```

### CLI Wiring (session start)

```bash
# On `rai session start`:
# 1. Generate session ID (existing from RAISE-137)
# 2. Create session directory: .raise/rai/personal/sessions/SES-NNN/
# 3. Run migration if flat files exist
# 4. Add to active_sessions in developer.yaml (existing from RAISE-137)
# 5. Return session ID

# On `rai session close --session SES-NNN`:
# 1. Write final state to per-session dir
# 2. Record in index.jsonl (existing)
# 3. Cleanup session directory
# 4. Remove from active_sessions (existing from RAISE-137)
```

---

## 4. Acceptance Criteria

### Must Have

- [ ] `get_session_dir(session_id)` returns `.raise/rai/personal/sessions/{SES-NNN}/`
- [ ] `rai session start` creates the per-session directory
- [ ] `save_session_state` writes to per-session `state.yaml` when session_id provided
- [ ] `load_session_state` reads from per-session `state.yaml` when session_id provided
- [ ] Telemetry `emit()` writes to per-session `signals.jsonl` when session_id provided
- [ ] Two concurrent sessions produce independent state directories (no cross-write)
- [ ] Migration from flat layout (`session-state.yaml`, `telemetry/signals.jsonl`) works without data loss
- [ ] `rai session close` removes the session directory after finalizing
- [ ] Shared session ledger (`index.jsonl`) continues using fcntl locking

### Should Have

- [ ] Legacy flat files removed after successful migration
- [ ] Graceful fallback if session_id not provided (backward compat for non-session-aware callers)

### Must NOT

- [ ] **MUST NOT** modify shared memory files (`patterns.jsonl`, `calibration.jsonl`) — those stay shared
- [ ] **MUST NOT** break existing `rai session start --context` output
- [ ] **MUST NOT** touch CWD validation (RAISE-139 scope)

---

## References

**Related ADRs**:
- [ADR-029: Session Instance Isolation](../../../../dev/decisions/adr-029-agent-isolation-strategy.md)
- [ADR-024: Deterministic Session Protocol](../../../../dev/decisions/adr-024-deterministic-session-protocol.md)

**Related Stories**:
- RAISE-137: Session Token Protocol (prerequisite, done)
- RAISE-139: CWD Poka-yoke (depends on this)

**Dependencies**:
- RAISE-137 (session token protocol) — provides session ID generation, resolver, active_sessions

---

**Template Version**: 2.0 (Lean Feature Spec)
**Created**: 2026-02-15
