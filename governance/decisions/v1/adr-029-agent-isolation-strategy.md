---
id: ADR-029
title: Session Instance Isolation — Concurrent Multi-Agent Sessions
status: proposed
date: 2026-02-15
epic: RAISE-127
relates_to:
  - RAISE-134 (context leak bug)
  - RAISE-137 (session token protocol)
  - RAISE-138 (per-session state)
  - RAISE-139 (CWD poka-yoke)
  - ADR-024 (deterministic session protocol)
---

# ADR-029: Session Instance Isolation

## Context

Developers use multiple IDEs/agents concurrently on the same project. The real-world scenario is not just "Claude Code vs Cursor" — it's 3 Claude Code terminals + 3 Gemini tasks, all running as Rai with the same skills. The isolation unit must be the **session instance**, not the agent type.

Current architecture assumes a single active session per developer per project:

- `~/.rai/developer.yaml` tracks ONE `current_session`
- `.raise/rai/personal/session-state.yaml` is a single file (no concurrency)
- `.raise/rai/personal/sessions/index.jsonl` is a single sequence
- No mechanism to identify which session instance is calling the CLI
- CWD-based project detection allows cross-project writes (RAISE-134)

This causes session corruption when any two instances run `rai session start/close` on the same project, regardless of whether they're the same or different agent types.

## Decision

**Use session-instance tokens with per-session directories. Agent type is metadata, not the isolation key.**

The design follows a REST-like token model: `rai session start` returns a session token, and all subsequent commands pass it back. The CLI is stateless regarding "which session am I" — the caller always identifies themselves.

### 1. Session Token Protocol (RAISE-137)

`rai session start` generates a session instance ID and returns it to the caller.

```python
def resolve_session_id(
    session_flag: str | None,    # --session SES-177
    env_var: str | None,         # RAI_SESSION_ID
) -> str:
    """Resolve the active session ID.

    Priority:
    1. --session flag (explicit, per-command)
    2. RAI_SESSION_ID env var (per-terminal/process)
    3. Error: no session context
    """
```

**Session start returns the token:**
```
$ rai session start --project /path/to/project --agent claude-code
▶ Session SES-177 started (claude-code)
```

**Subsequent commands pass it:**
```
$ rai memory emit-work story S1 --event start --session SES-177
$ rai session close --session SES-177 --summary "..."
```

**AI agents** naturally remember the session ID from start output and pass it on every call. This is platform agnostic — works for Claude Code, Gemini, Cursor, Copilot, or any future agent.

**Human CLI users** can set `export RAI_SESSION_ID=SES-177` in their terminal or pass `--session` each time.

**Agent type** is optional metadata captured at session start via `--agent <name>`. It's stored in the session record for telemetry and observability, but plays no role in isolation.

### 2. Per-Session State Directories (RAISE-138)

Each session instance gets its own directory:

```
.raise/rai/personal/
├── sessions/
│   ├── index.jsonl           # Shared ledger of all sessions (fcntl-locked)
│   ├── SES-177/
│   │   ├── state.yaml        # What this session is working on
│   │   └── signals.jsonl     # Telemetry from this session
│   ├── SES-178/
│   │   └── ...
│   └── SES-179/
│       └── ...
└── (legacy session-state.yaml removed after migration)
```

**Per-session (isolated):**
- `state.yaml` — current work context (epic, story, phase, branch, narrative)
- `signals.jsonl` — telemetry signals emitted during this session

**Shared (concurrent access via fcntl):**
- `sessions/index.jsonl` — ledger of all sessions (append-only, locked)
- `.raise/rai/memory/patterns.jsonl` — project patterns (already fcntl-locked)
- `.raise/rai/memory/calibration.jsonl` — project calibration

**Developer profile (`~/.rai/developer.yaml`):**
- `current_session` field becomes `active_sessions: list[ActiveSession]`
- Each entry: `{session_id, started_at, project, agent}`
- Orphan detection: sessions older than 24h are flagged as stale

**Migration:** On first run with new protocol:
1. Check if `personal/session-state.yaml` exists (old layout)
2. If yes, move its contents to `personal/sessions/SES-{last_id}/state.yaml`
3. Move `personal/telemetry/signals.jsonl` to the same session directory
4. Remove old files

### 3. Project-Scoped Writes (RAISE-139)

Before any write to `.raise/`, validate the project root:

```python
def validate_project_root(project_root: Path) -> Path:
    """Ensure project_root is a valid RaiSE project.

    Checks:
    1. Path is absolute
    2. .raise/ directory exists
    3. .raise/manifest.yaml exists

    Raises RaiProjectNotFoundError if invalid.
    """
```

The `--project` flag on session commands becomes **required** when CWD doesn't contain `.raise/`. This is the poka-yoke for RAISE-134.

## Consequences

### Positive
- Any number of agents/terminals can run concurrently without corruption
- Platform agnostic — no IDE detection required, works with any AI agent
- Token model is a familiar pattern (REST APIs, database transactions)
- Agent type is metadata, not architecture — future agents work without code changes
- Backward compatible — existing setups auto-migrate

### Negative
- Every CLI command needs `--session` flag plumbing
- AI agents must remember and pass session ID (natural for conversational AI, but a contract)
- Session directories accumulate — need cleanup strategy (gc on session close, or periodic)
- `developer.yaml` schema change for `active_sessions` (list vs single value)

### Neutral
- Session IDs remain globally sequential per project (SES-NNN from shared index.jsonl)
- Pattern emission stays shared (all sessions contribute to same project patterns)
- Telemetry becomes per-session (aggregation is a future concern)

## Alternatives Considered

### A. Agent-type namespacing (original ADR-029 v1)
Namespace by agent type (`personal/claude-code/`, `personal/cursor/`). Rejected: doesn't solve the core problem — 3 Claude Code terminals still corrupt each other. Agent type is the wrong isolation key.

### B. Process tree / PID detection
Use parent PID to identify the calling terminal. Rejected: fragile across platforms, PIDs aren't stable across `rai` invocations (each is a new process), unreliable in containers/SSH.

### C. File-level locking instead of isolation
Lock shared files during writes. Rejected: locking is a concurrency control, not an isolation mechanism. Two sessions still overwrite each other's state between lock acquisitions.

### D. Automatic session detection (no token)
CLI auto-detects "which session am I" from context. Rejected: no reliable, platform-agnostic mechanism exists. The caller is the only entity that knows which session it belongs to.

### E. Separate developer profiles per session
Each session gets its own profile. Rejected: over-isolation. Profile is about the developer (coaching, trust, experience), not the session.
