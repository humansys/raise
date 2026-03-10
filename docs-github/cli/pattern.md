---
title: rai pattern
description: Manage learned patterns — add, reinforce, and promote.
---

Manage learned patterns. Patterns capture learnings from development — process improvements, technical discoveries, and architectural decisions.

## `rai pattern add`

Add a new pattern to memory.

| Argument | Description |
|----------|-------------|
| `CONTENT` | Pattern description (**required**) |

| Flag | Short | Description |
|------|-------|-------------|
| `--context` | `-c` | Context keywords (comma-separated) |
| `--type` | `-t` | Pattern type: `codebase`, `process`, `architecture`, `technical`. Default: `process` |
| `--from` | `-f` | Story/session where learned |
| `--scope` | `-s` | Memory scope: `global`, `project`, `personal`. Default: `personal` |
| `--memory-dir` | `-m` | Memory directory path (overrides scope) |

```bash
# Add a process pattern
rai pattern add "HITL before commits" -c "git,workflow"

# Add a technical pattern with source
rai pattern add "Use capsys for stdout tests" -t technical -c "pytest,testing"

# Add with source reference
rai pattern add "BFS reuse across modules" -t architecture --from S2.3
```

---

## `rai pattern reinforce`

Record a reinforcement signal for a pattern. Called at story-review to indicate whether a pattern was applied (`1`), not relevant (`0`), or contradicted (`-1`). Vote `0` (N/A) does not count toward the evaluation total.

| Argument | Description |
|----------|-------------|
| `PATTERN_ID` | Pattern ID to reinforce, e.g. `PAT-E-183` (**required**) |

| Flag | Short | Description |
|------|-------|-------------|
| `--vote` | `-v` | Vote: `1` (applied), `0` (N/A), `-1` (contradicted) (**required**) |
| `--from` | `-f` | Story ID for traceability |
| `--scope` | `-s` | Memory scope: `global`, `project`, `personal`. Default: `project` |
| `--memory-dir` | `-m` | Memory directory path (overrides scope) |

```bash
# Pattern was applied
rai pattern reinforce PAT-E-183 --vote 1 --from RAISE-170

# Pattern not relevant
rai pattern reinforce PAT-E-151 --vote 0 --from RAISE-170

# Pattern contradicted
rai pattern reinforce PAT-E-094 --vote -1 --from RAISE-170
```

---

## `rai pattern promote`

Promote a pattern from personal scope to project scope. Moves the pattern entry from personal `patterns.jsonl` to project `patterns.jsonl`. The pattern ID is preserved.

| Argument | Description |
|----------|-------------|
| `PATTERN_ID` | Pattern ID to promote, e.g. `PAT-E-123` (**required**) |

| Flag | Short | Description |
|------|-------|-------------|
| `--memory-dir` | `-m` | Memory directory path (overrides default) |

```bash
rai pattern promote PAT-E-123
```

**See also:** [`rai graph query`](cli/graph.md), [`rai signal emit-work`](cli/signal.md)
