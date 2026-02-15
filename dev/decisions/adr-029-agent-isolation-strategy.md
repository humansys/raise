---
id: ADR-029
title: Agent Isolation Strategy — Multi-IDE Concurrent Sessions
status: proposed
date: 2026-02-15
epic: RAISE-127
relates_to:
  - RAISE-134 (context leak bug)
  - RAISE-137 (agent identity)
  - RAISE-138 (namespaced state)
  - RAISE-139 (CWD poka-yoke)
  - ADR-024 (deterministic session protocol)
---

# ADR-029: Agent Isolation Strategy

## Context

Developers use multiple IDEs/agents concurrently on the same project (Claude Code in terminal, Cursor in editor, Windsurf for review). The current architecture assumes a single active session per developer per project:

- `~/.rai/developer.yaml` tracks ONE `current_session`
- `.raise/rai/personal/session-state.yaml` is a single file
- `.raise/rai/personal/sessions/index.jsonl` is a single sequence
- No mechanism to detect which agent is calling the CLI
- CWD-based project detection allows cross-project writes (RAISE-134)

This causes session corruption when two agents run `rai session start/close` on the same project, and context leaks when an agent runs from the wrong directory.

## Decision

**Use environment-variable-based agent identity with per-agent namespaced directories.**

### 1. Agent Identity Detection (RAISE-137)

The CLI reads `RAI_AGENT_ID` environment variable to identify the calling agent.

```python
def get_agent_id() -> str:
    """Detect the agent calling the CLI.

    Priority:
    1. RAI_AGENT_ID env var (explicit, set by IDE integration)
    2. Auto-detect from known IDE env vars (fallback)
    3. "default" (terminal/unknown)
    """
```

Auto-detection heuristics (fallback when `RAI_AGENT_ID` not set):
- `CLAUDE_CODE` or `CLAUDE_CODE_ENTRY_POINT` → `"claude-code"`
- `CURSOR_*` env vars → `"cursor"`
- `WINDSURF_*` env vars → `"windsurf"`
- `TERM_PROGRAM=vscode` → `"vscode"`
- None matched → `"default"`

Agent ID format: lowercase alphanumeric + hyphens, max 32 chars. Normalized from env var.

### 2. Namespaced State (RAISE-138)

Per-agent subdirectories under `personal/`:

```
.raise/rai/personal/
├── claude-code/           # Agent-specific state
│   ├── session-state.yaml
│   ├── sessions/
│   │   └── index.jsonl
│   └── telemetry/
│       └── signals.jsonl
├── cursor/
│   ├── session-state.yaml
│   ├── sessions/
│   │   └── index.jsonl
│   └── telemetry/
│       └── signals.jsonl
└── default/               # Direct CLI / unknown agent
    └── ...
```

**Shared (not namespaced):**
- `.raise/rai/memory/` — project knowledge (patterns, calibration, graph) stays shared
- `~/.rai/developer.yaml` — profile stays global, but `current_session` becomes a dict keyed by agent ID

**Migration:** On first run with agent detection, move existing `personal/` contents into `personal/default/`. Detect by checking if `personal/session-state.yaml` exists (old layout) vs `personal/*/session-state.yaml` (new layout).

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

Applied at the path helper level (`get_personal_dir`, `get_memory_dir`, etc.) via an opt-in validation parameter, or as a guard in session start/close commands.

The `--project` flag on session commands becomes **required** when CWD doesn't contain `.raise/`. This is the poka-yoke for RAISE-134.

## Consequences

### Positive
- Agents can run concurrently without session corruption
- Each agent has its own session history, state, and telemetry
- CWD poka-yoke eliminates cross-project writes
- Backward compatible — existing single-agent setups auto-migrate to `default/`
- No changes to shared memory (patterns, graph) — those are project-level, not agent-level

### Negative
- Session IDs become per-agent (SES-001 in claude-code ≠ SES-001 in cursor)
- `developer.yaml` `current_session` schema changes (dict vs single value)
- Migration code needed for existing personal/ directories
- Auto-detection heuristics may need updates as IDEs evolve

### Neutral
- Telemetry stays per-agent (each agent's signals are isolated, aggregation is a future concern)
- Pattern emission stays shared (all agents contribute to same project patterns.jsonl — fcntl lock already handles concurrency)

## Alternatives Considered

### A. Process tree detection
Inspect parent PIDs to determine IDE. Rejected: fragile across platforms, unreliable in containers/SSH, complex to maintain.

### B. Explicit `--agent-id` flag on every command
User passes agent identity manually. Rejected: high friction, error-prone, bad DX. Environment variables set once per IDE config.

### C. File-level locking instead of namespacing
Lock shared files during writes. Rejected: doesn't solve state isolation (two agents still overwrite each other's session state). Locking is a concurrency control, not an isolation mechanism.

### D. Separate developer profiles per agent
Each agent gets its own `~/.rai/developer-{agent}.yaml`. Rejected: over-isolation. Profile is about the developer, not the agent. Coaching, trust level, experience — these are developer attributes.
