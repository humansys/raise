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

**See also:** [`rai session start`](#rai-session-start), [`rai signal emit-session`](cli/signal.md)
