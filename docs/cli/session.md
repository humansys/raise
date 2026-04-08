---
title: rai session
description: Manage working sessions — start, close, context loading, and journaling.
---

Manage working sessions. Sessions track developer activity, enable context loading for AI agents, and capture incremental decisions via the journal.

## `rai session start`

Start a new working session. Increments the session counter and sets active session state. Checks for orphaned sessions and warns if found.

With `--context`, outputs a token-optimized context bundle (~150 tokens) from the developer profile, session state, and knowledge graph.

| Flag | Short | Description |
|------|-------|-------------|
| `--name` | `-n` | Your name (required for first-time setup) |
| `--project` | `-p` | Project path to associate with this session |
| `--agent` | | Agent type (e.g., `claude-code`, `cursor`). Default: `unknown` |
| `--context` | | Output a context bundle for AI consumption |

```bash
# First-time setup
rai session start --name "Alice" --project .

# Start session with context bundle
rai session start --project . --context

# Simple start
rai session start
```

---

## `rai session close`

End the current working session. With `--summary` or `--state-file`, performs a full structured close — records session, patterns, corrections, and updates state. All writes are atomic.

| Flag | Short | Description |
|------|-------|-------------|
| `--summary` | `-s` | Session summary |
| `--type` | `-t` | Session type (`feature`, `research`, `maintenance`, etc.) |
| `--pattern` | | Pattern description to record |
| `--correction` | | Coaching correction observed |
| `--correction-lesson` | | Lesson from the correction |
| `--state-file` | | YAML file with full structured session output |
| `--session` | | Session ID to close (e.g., `SES-177`). Falls back to `RAI_SESSION_ID` env var |
| `--project` | `-p` | Project path |

```bash
# Simple close
rai session close

# Close with summary
rai session close --summary "Implemented auth module" --type feature

# Close with pattern learned
rai session close --summary "Refactored tests" --type maintenance \
  --pattern "Use fixtures for database setup"
```

---

## `rai session context`

Load task-relevant context priming sections. Use after `rai session start --context` to load detailed priming for a specific work type.

Available sections: `governance`, `behavioral`, `coaching`, `deadlines`, `progress`.

| Flag | Short | Description |
|------|-------|-------------|
| `--sections` | `-s` | Comma-separated section names to load (**required**) |
| `--project` | `-p` | Project path (**required**) |

```bash
# Feature work: governance + behavioral patterns
rai session context -s governance,behavioral -p .

# Near a deadline: check urgency
rai session context -s deadlines,progress -p .
```

---

## `rai session journal add`

Add a journal entry to the current session. Entries capture decisions, insights, and completed tasks incrementally.

| Argument | Description |
|----------|-------------|
| `CONTENT` | Content to persist (**required**) |

| Flag | Short | Description |
|------|-------|-------------|
| `--type` | `-t` | Entry type: `decision`, `insight`, `task_done`, `note`. Default: `note` |
| `--tags` | | Comma-separated tags (e.g., `arch,spike`) |
| `--project` | `-p` | Project path |

```bash
# Record a decision
rai session journal add "Use JSONL for journal" --type decision

# Record completed task
rai session journal add "T1 complete" --type task_done

# Record an insight with tags
rai session journal add "Compaction loses rationale" --type insight --tags "compaction,memory"
```

---

## `rai session journal show`

Show journal entries for the current session.

| Flag | Short | Description |
|------|-------|-------------|
| `--last` | `-n` | Show only the last N entries |
| `--compact` | | Output compact format for context injection |
| `--project` | `-p` | Project path |

```bash
# Show all entries
rai session journal show

# Show last 5 entries
rai session journal show --last 5

# Compact format for post-compaction restore
rai session journal show --compact
```

---

## Session Identity (v2.3.0)

Starting with v2.3.0, sessions use a deterministic, timestamp-based ID format tied to the developer who started them.

### Session ID Format

```
S-{prefix}-{YYMMDD}-{HHMM}
```

For example, a session started by developer `E` on March 23, 2026 at 11:00 produces `S-E-260323-1100`. The format is 16 characters, requires no coordination between developers, and is unique per developer at minute granularity. Same-minute collision is prevented by the active session check — you cannot start a new session while one is already active.

### Developer Prefix Registry

Each developer has a short prefix (typically their first initial) registered in `.raise/rai/prefixes.yaml`:

```yaml
E: {name: "Emilio Osorio", registered: "2026-03-22"}
J: {name: "Juan Pérez", registered: "2026-03-25"}
```

Prefixes auto-register on first `rai session start`. If two developers share the same initial, collision detection suggests an extended prefix (e.g., `E` is taken by Emilio, so Elena gets `EG`). This file is committed to git so the whole team can see registered prefixes.

### Per-Project Session Storage

Session data is stored per-project in `.raise/rai/personal/` (gitignored):

| Path | Purpose |
|------|---------|
| `.raise/rai/personal/active-session` | Current session pointer (JSON) |
| `.raise/rai/personal/sessions/{prefix}/index.jsonl` | Session ledger per developer |
| `.raise/rai/personal/sessions/{session-id}/` | Per-session working state |

Only `.raise/rai/prefixes.yaml` is committed to git. All session data stays local by default. Teams can opt-in to sharing session indexes by modifying `.gitignore`.

The active session pointer carries metadata (ID, name, start timestamp) from start to close, so the close command does not need to reconstruct state.

:::caution[Breaking Change — Session Data Path]
Session data storage moved from the global `~/.rai/developer.yaml` to per-project `.raise/rai/personal/`. There is no automatic migration.

**Before (v2.2.x):** Session state stored globally in `~/.rai/developer.yaml`. Session IDs used `SES-NNN` format with a per-project counter.

**After (v2.3.0):** Session state stored per-project in `.raise/rai/personal/`. Session IDs use `S-{prefix}-{YYMMDD}-{HHMM}` format.

Old `SES-NNN` sessions remain readable, but new sessions use the new format exclusively. To preserve old session data, keep your existing `~/.rai/developer.yaml` — it is not modified or deleted.
:::

---

**See also:** [`rai session start`](#rai-session-start), [`rai signal emit-session`](signal.md/
