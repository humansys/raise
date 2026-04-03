---
title: Memory
description: How RaiSE remembers across sessions — patterns, calibration, and session history that compound over time.
---

Memory is what makes your AI partner learn. Without it, every session starts from zero. With RaiSE memory, your AI carries forward patterns it learned, calibration data from past work, and a full session history — so it gets better the more you work together.

## The Three Scopes

Memory lives in three places, each with a different purpose:

| Scope | Location | Visibility | What goes here |
|-------|----------|------------|----------------|
| **Global** | `~/.rai/` | All projects | Universal patterns that apply everywhere |
| **Project** | `.raise/rai/memory/` | Shared (committed to repo) | Project-specific patterns, calibration, team knowledge |
| **Personal** | `.raise/rai/personal/` | You only (gitignored) | Your session history, telemetry, personal learnings |

When the same concept exists in multiple scopes, **personal overrides project, project overrides global**. This means a team can share project patterns while each developer keeps their own session history.

## The Three Types

### Patterns

Patterns are learnings captured during development. They represent what worked, what didn't, and what to remember next time.

```bash
rai pattern add "Use fixtures for database setup in tests" \
  -t technical -c "pytest,testing" --from S3.5
```

Patterns have sub-types:
- **Process** — workflow and collaboration patterns (e.g., "commit after each task")
- **Technical** — code techniques and gotchas (e.g., "use capsys for stdout tests")
- **Architecture** — design decisions and module patterns
- **Codebase** — project-specific conventions

### Calibration

Calibration tracks how long stories actually take versus estimates. Over time, this builds a velocity profile that helps predict future work more accurately.

```bash
rai signal emit-calibration S3.5 --name "Auth Module" -s M -a 45 -e 60
```

This records: story S3.5 was estimated at 60 minutes (size M) but actually took 45 — a velocity of 1.33x.

### Sessions

Sessions are a chronological record of what happened. Each session captures: what you worked on, what you accomplished, and what patterns you learned.

```bash
rai signal emit-session "S3.5 Auth Module" -t story -o "JWT setup,Middleware,Tests"
```

## Pattern Scoring

Not all patterns are equal. Patterns that have been validated through real implementation should surface before untested ones. RaiSE uses a **composite score** to rank patterns in every query:

```
score = (0.3 × recency + 0.7 × keyword_relevance) × wilson_modifier
```

**Recency** decays over time using a 30-day half-life — a pattern from yesterday scores higher than one from 3 months ago, all else equal. **Foundational patterns** (marked `foundational: true`) are exempt from decay and always score on keyword relevance alone.

**Wilson modifier** adjusts the score based on reinforcement history. Patterns with many positive evaluations get a boost; patterns that have been contradicted in practice rank lower.

### Reinforcement Loop

At every story-review, evaluate the patterns that were loaded at session start:

```bash
rai pattern reinforce PAT-001 --vote 1 --from S101   # applied
rai pattern reinforce PAT-002 --vote 0 --from S101   # N/A
rai pattern reinforce PAT-003 --vote -1 --from S101  # contradicted
```

Vote `0` (N/A) does not count toward evaluations — use it freely. The system is deliberately conservative with small sample sizes: a pattern with 1 positive evaluation scores ~0.21, not 1.0. Confidence builds gradually through real usage.

## How Memory Compounds

This is the key insight: memory creates a **compounding effect**.

1. **Session 1**: You discover that fixtures are better than inline setup for database tests
2. **Pattern captured**: "Use fixtures for database setup" (technical pattern)
3. **Session 5**: Your AI partner applies this pattern automatically — it's in the context bundle
4. **Session 20**: Your velocity has improved because patterns eliminate repeated discovery

The more sessions you run, the smarter the system gets. This isn't ML or fine-tuning — it's structured knowledge that flows into your AI's context at session start.

## The Memory Index

All memory sources merge into a single queryable index:

```bash
# Build the unified index
rai graph build

# Query it
rai graph query "testing patterns" --types pattern

# List all concepts
rai graph list --memory-only
```

The index is a JSON file (`.raise/rai/memory/index.json`) that combines patterns, calibration, sessions, governance, work tracking, and skills into one graph. See [Knowledge Graph](knowledge-graph.md/ for how this graph works.

## Key Commands

| Command | What it does |
|---------|-------------|
| `rai graph build` | Build unified index from all sources |
| `rai graph query` | Search memory for relevant concepts |
| `rai graph query --format compact` | High-density output for AI context windows |
| `rai pattern reinforce --vote 1\|0\|-1` | Record reinforcement signal for a pattern |
| `rai graph list` | List all concepts in the index |
| `rai pattern add` | Record a learned pattern |
| `rai signal emit-calibration` | Record story timing data |
| `rai signal emit-session` | Record a session |
| `rai graph validate` | Check index integrity |

See the [CLI Reference](../cli/index.md/ for full details on each command.
