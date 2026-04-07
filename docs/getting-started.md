---
title: Getting Started
description: Understand what RaiSE is, install it, and run your first AI-assisted engineering session.
---

RaiSE is a methodology and toolkit for **reliable AI software engineering**. It turns AI coding assistants from unpredictable generators into disciplined collaborators — through governance, memory, and structured workflows.

## The Triad

RaiSE works through three collaborating parts:

```
    You (Strategy, Judgment, Ownership)
         │
         │ collaborates with
         ▼
      Rai (AI Partner — Execution + Memory)
         │
         │ governed by
         ▼
      RaiSE (Methodology + Toolkit)
```

**You** decide *what* to build and *why*. **Rai** executes with accumulated memory and calibrated judgment. **RaiSE** provides the discipline — skills, governance, and quality gates — that makes the collaboration reliable.

The result: AI that learns from your project, follows your rules, and compounds knowledge across sessions instead of starting fresh every time.

## Prerequisites

- **Python 3.12 or 3.13** (3.14 is not yet supported — many dependencies lack wheels)
- **Git** initialized in your project
- An AI assistant with RaiSE skills: [Claude Code](https://claude.ai/claude-code) (recommended), Cursor, or Windsurf

## Install

The recommended method is **pipx** (isolates RaiSE in its own environment):

```bash
pipx install raise-cli
```

Alternatives:

```bash
# With pip (use a virtual environment)
pip install raise-cli

# With uv
uv tool install raise-cli
```

**macOS note:** Do not use the system Python that ships with macOS. Install Python 3.12 or 3.13 via [Homebrew](https://brew.sh/) (`brew install python@3.13`) or [pyenv](https://github.com/pyenv/pyenv) first.

**Windows:** Use WSL (Ubuntu/Debian):

```bash
sudo apt update && sudo apt install pipx -y
pipx ensurepath
# Close and reopen terminal
pipx install raise-cli
```

Verify:

```bash
rai --version
```

### Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| Build errors during install | Python 3.14 or missing C compiler | Use Python 3.12 or 3.13 |
| `command not found: rai` | pipx/pip bin not in PATH | Run `pipx ensurepath` or add `~/.local/bin` to PATH |
| Permission errors | Installing to system Python | Use `pipx` instead of `pip`, or use a virtual environment |

## Initialize a project

Navigate to your project directory first — `rai init` works on the **current directory**:

```bash
cd your-project    # You MUST be in the project root
rai init
```

This creates the `.raise/` directory with governance templates, memory structure, and a project manifest. For existing codebases, add `--detect` to analyze your conventions automatically:

```bash
rai init --detect
```

## Your first session

Open your AI assistant (Claude Code) in the project directory. For first-time setup, run the welcome skill:

```
/rai-welcome
```

This creates your developer profile, builds the knowledge graph, and verifies everything works.

After that, start every session with:

```
/rai-session-start
```

This loads your context, memory, patterns, and proposes focused work. You work **through skills** — they orchestrate the CLI for you.

## The story lifecycle

This is the core rhythm of working with RaiSE. Every piece of work follows six steps:

```
/rai-story-start     → Scope: what are we building?
/rai-story-design    → Spec: how will it work?
/rai-story-plan      → Tasks: what are the steps?
/rai-story-implement → Build: test, code, verify, commit
/rai-story-review    → Reflect: what did we learn?
/rai-story-close     → Merge: clean up and ship
```

Each step produces an artifact that feeds the next. The review feeds memory, which feeds future sessions. This is how learning compounds — not through magic, but through disciplined repetition.

Start with a small feature (XS or S sized). Get the rhythm first, then scale up.

→ **[Walk through the full lifecycle](guides/first-story.md)** for a step-by-step guide.

## End a session

When you're done working, close the session to capture what happened:

```
/rai-session-close
```

This reflects on outcomes, persists patterns, and records session data for continuity.

## Build your memory

As you work, RaiSE accumulates knowledge — patterns, calibration data, governance. Build the unified memory index to make it queryable:

```bash
rai graph build
```

Then query it:

```bash
rai graph query "testing patterns"
```

## What's next

- **[Your First Story](guides/first-story.md)** — Full story lifecycle walkthrough
- **[Setting Up a Project](guides/setting-up.md)** — Greenfield and brownfield setup in depth
- **[CLI Reference](cli/index.md)** — All commands, flags, and examples
- **[Core Concepts](concepts/index.md)** — Memory, Skills, Governance, Knowledge Graph
