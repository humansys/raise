---
story_id: "RAISE-137"
title: "Session Token Protocol"
epic_ref: "RAISE-127 Session Instance Isolation"
story_points: 2
complexity: "moderate"
status: "draft"
version: "1.0"
created: "2026-02-15"
updated: "2026-02-15"
template: "lean-feature-spec-v2"
---

# Feature: Session Token Protocol

> **Epic**: RAISE-127 - Session Instance Isolation
> **Complexity**: moderate | **SP**: 2

---

## 1. What & Why

**Problem**: `rai session start` assumes one active session per project. When multiple terminals call it concurrently, they overwrite each other's `current_session` in `developer.yaml`. There's no way for a command to know which session instance is calling it.

**Value**: Foundation for all session isolation. Without a token protocol, per-session directories (RAISE-138) and CWD poka-yoke (RAISE-139) have nothing to key on. This unblocks the entire epic.

---

## 2. Approach

**How we'll solve it**: `rai session start` returns a session token (SES-NNN). All subsequent commands accept `--session` flag or `RAI_SESSION_ID` env var to identify which session they belong to. The CLI is stateless — the caller always identifies itself.

**Architectural Context**:
- **Module**: `mod-session` (domain layer)
- **Dependencies**: mod-schemas, mod-cli, mod-onboarding, mod-memory
- **ADR**: ADR-029 (Session Instance Isolation)

**Components affected**:
- **`src/rai_cli/session/resolver.py`**: Create — `resolve_session_id()` function
- **`src/rai_cli/cli/commands/session.py`**: Modify — add `--session` and `--agent` flags to start/close
- **`src/rai_cli/onboarding/profile.py`**: Modify — `current_session` → `active_sessions` list, add/remove session helpers
- **`src/rai_cli/schemas/session_state.py`**: Modify — add `ActiveSession` model if needed

---

## 3. Interface / Examples

### CLI Usage

```bash
# Start a new session — returns token
$ rai session start --project /path/to/project --agent claude-code
▶ Session SES-177 started (claude-code)

# Start another session (different terminal)
$ rai session start --project /path/to/project --agent claude-code
▶ Session SES-178 started (claude-code)

# Close a specific session
$ rai session close --session SES-177 --project /path/to/project --summary "..."
▶ Session SES-177 closed

# Use env var instead of --session flag
$ export RAI_SESSION_ID=SES-178
$ rai session close --project /path/to/project --summary "..."
▶ Session SES-178 closed
```

### Resolution Logic

```python
def resolve_session_id(
    session_flag: str | None,    # --session SES-177 or --session 177
    env_var: str | None,         # RAI_SESSION_ID
) -> str:
    """Resolve session ID from flag or environment.

    Priority:
    1. --session flag (explicit, per-command)
    2. RAI_SESSION_ID env var (per-terminal)
    3. RaiSessionNotFoundError

    Accepts both "SES-177" and "177" (normalizes to "SES-177").
    """
```

### Data Structures

```python
# In profile.py — replaces CurrentSession
class ActiveSession(BaseModel):
    session_id: str          # "SES-177"
    started_at: datetime     # UTC
    project: str             # Absolute path
    agent: str = "unknown"   # Optional metadata

    def is_stale(self, hours: int = 24) -> bool:
        delta = datetime.now(UTC) - self.started_at
        return delta.total_seconds() > hours * 3600

# In DeveloperProfile — replaces current_session
class DeveloperProfile(BaseModel):
    # ... existing fields ...
    active_sessions: list[ActiveSession] = Field(default_factory=list)
    # current_session removed (backward compat migration reads it)
```

### Session Start Output (with --context)

```
# Session Context

Developer: Emilio (ri)
...

Session: SES-177
...
```

**IMPORTANT**: The session ID **MUST** appear in the `--context` output so the AI agent can capture it and pass `--session SES-177` on subsequent calls.

### Backward Compatibility

```python
# When loading developer.yaml:
# If old format has current_session (dict), migrate to active_sessions (list)
# If current_session exists and is not None:
#   → Convert to ActiveSession, add to active_sessions
#   → Remove current_session field
#   → Save profile
```

---

## 4. Acceptance Criteria

### Must Have

- [ ] `rai session start` returns a session ID (SES-NNN) in its output
- [ ] `rai session start` accepts `--agent <name>` flag (default: "unknown")
- [ ] `rai session close` accepts `--session <id>` flag
- [ ] `resolve_session_id()` resolves: `--session` flag > `RAI_SESSION_ID` env var > error
- [ ] `developer.yaml` stores `active_sessions: list[ActiveSession]` instead of `current_session`
- [ ] `rai session start` adds entry to `active_sessions`; `rai session close` removes it
- [ ] Backward compat: old `current_session` format auto-migrates to `active_sessions` on load
- [ ] Session ID appears in `--context` bundle output

### Should Have

- [ ] Stale session warning when `active_sessions` contains entries >24h old
- [ ] `resolve_session_id()` accepts both "SES-177" and "177" (normalizes)

### Must NOT

- [ ] **MUST NOT** break existing `rai session start --context` output format (additive only)
- [ ] **MUST NOT** require `--session` on `rai session start` (it generates the ID)
- [ ] **MUST NOT** add `--session` to non-session commands yet (RAISE-138 scope)

---

## References

**Related ADRs**:
- [ADR-029: Session Instance Isolation](../../../../dev/decisions/adr-029-agent-isolation-strategy.md) — **VALIDATED** by RES-SESSION-ISO-001
- [ADR-024: Deterministic Session Protocol](../../../../dev/decisions/adr-024-deterministic-session-protocol.md)

**Related Stories**:
- RAISE-138: Per-Session State Isolation (depends on this)
- RAISE-139: CWD Poka-yoke (depends on RAISE-138)

**Research**:
- [RES-SESSION-ISO-001: Session Isolation Patterns](../../../../work/research/session-isolation-patterns/README.md) — Industry validation: Claude Code, SWE-agent, OpenCode, tmux all converge on env var + per-session directories. No design changes needed.

**Dependencies**:
- None — this is the foundation story

---

**Template Version**: 2.0 (Lean Feature Spec)
**Created**: 2026-02-15
**Validated**: 2026-02-15 (research RES-SESSION-ISO-001)
