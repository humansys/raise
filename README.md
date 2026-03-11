# RaiSE

[![CI](https://github.com/humansys/raise/actions/workflows/ci.yml/badge.svg)](https://github.com/humansys/raise/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/raise-cli)](https://pypi.org/project/raise-cli/)
[![Python](https://img.shields.io/pypi/pyversions/raise-cli)](https://pypi.org/project/raise-cli/)
[![License](https://img.shields.io/github/license/humansys/raise)](LICENSE)

**Reliable AI Software Engineering** — A governance framework that makes AI-assisted development predictable, traceable, and improvable.

```
You define what to build.  Rai executes with discipline.  RaiSE keeps it honest.
```

---

## The Problem

AI coding assistants are fast but inconsistent. Without structure, you get code that works today and breaks tomorrow — no traceability, no learning, no accumulated judgment. Every session starts from zero.

## The Solution

RaiSE gives your AI assistant **methodology, memory, and gates**:

- **37 skills** that guide the full SDLC — from epic planning to story implementation to release
- **Validation gates** at every phase — tests, types, lint, architecture review, quality review
- **Cross-session memory** — patterns learned, velocity calibrated, decisions preserved
- **Governance as code** — constitution, guardrails, ADRs, all versioned in Git
- **TDD by default** — RED-GREEN-REFACTOR, no exceptions

## What It Looks Like

```bash
# Start your day
/rai-session-start
# → Loads memory, shows pending work, proposes focus

# Run a full story lifecycle in one command
/rai-story-run S42.1
# → start → design → plan → implement → architecture review → quality review → retrospective → merge

# Or step through manually
/rai-story-start S42.1        # Branch + scope
/rai-story-plan S42.1         # Decompose into tasks
/rai-story-implement S42.1    # TDD execution with gates
/rai-story-close S42.1        # Merge + cleanup

# End your day
/rai-session-close
# → Captures learnings, updates memory for next session
```

Every story produces: scope commit, implementation with tests, retrospective, and patterns for next time.

---

## Quick Start

### Install

```bash
# Recommended
pipx install raise-cli

# Alternatives
pip install raise-cli
uv tool install raise-cli
```

Requires **Python 3.12+** and [Claude Code](https://claude.ai/claude-code).

### Initialize

```bash
cd your-project
rai init --detect       # Scaffolds .raise/, detects conventions
```

Then open Claude Code and run:

```
/rai-welcome            # One-time setup: profile, graph, preferences
/rai-session-start      # Start working
```

---

## Features

### Structured Lifecycles

Epics, stories, and sessions — each with a defined lifecycle, validation gates, and artifact trail.

```
Epic:    /rai-epic-start → design → plan → [stories] → close
Story:   /rai-story-start → design → plan → implement → review → close
Session: /rai-session-start → [work] → /rai-session-close
```

### Knowledge Graph

`rai graph build` indexes your project: modules, governance docs, patterns, guardrails. Rai queries it for context instead of re-reading your entire codebase.

### Multi-Language Discovery

Automatically extracts and describes components from: **Python, TypeScript, JavaScript, C#, PHP, Dart, Svelte**.

### Adapters & Plugins

Extensible via entry points. Community ships with a filesystem adapter. Enterprise adapters (Jira, Confluence) available via [raise-pro](https://raiseframework.ai).

### Doctor

```bash
rai doctor              # Diagnose project health
rai doctor --fix        # Auto-remediate common issues
```

### 37 Skills

Session, story, epic, discovery, research, debug, bugfix, quality review, architecture review, publishing, MCP management, and more. Run `rai skill list` for the full catalog.

---

## CLI

```bash
rai graph build                    # Build knowledge graph
rai graph query "auth patterns"    # Query Rai's memory
rai pattern list                   # View learned patterns
rai adapter list                   # Show registered adapters
rai gate check --all               # Run all quality gates
rai release check                  # Pre-publish quality check
rai doctor                         # Diagnose setup issues
```

17 command groups, 72 subcommands. See the [CLI reference](https://docs.raiseframework.ai/cli/).

---

## Core Principles

1. **Humans Define, Machines Execute** — You own the specs, AI executes with discipline
2. **Governance as Code** — Standards versioned in Git, not tribal knowledge
3. **Jidoka** — Stop on defects. Never accumulate errors.
4. **Observable Workflow** — Every decision traceable to an artifact
5. **Kaizen** — Each session teaches Rai something. Patterns compound.

---

## Documentation

- **Docs site:** [docs.raiseframework.ai](https://docs.raiseframework.ai)
- **Framework:** [Constitution](framework/reference/constitution.md) · [Glossary](framework/reference/glossary.md) · [Philosophy](framework/reference/philosophy.md)
- **Getting started:** [Greenfield guide](docs/getting-started.mdx) · [Brownfield guide](docs/guides/)

---

## Contributing

```bash
git clone https://github.com/humansys/raise.git
cd raise && git checkout dev
uv sync --extra dev
rai doctor              # Verify setup
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for branch model, testing, and PR guidelines.

---

## License

[Apache-2.0](LICENSE)

*RaiSE — Ship quality software at AI speed.*
