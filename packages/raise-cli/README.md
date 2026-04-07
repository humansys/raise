# RaiSE CLI

**Reliable AI Software Engineering** — a lean methodology and deterministic CLI toolkit that turns AI coding assistants into disciplined collaborators.

[![PyPI](https://img.shields.io/pypi/v/raise-cli)](https://pypi.org/project/raise-cli/)
[![Python](https://img.shields.io/pypi/pyversions/raise-cli)](https://pypi.org/project/raise-cli/)
[![License](https://img.shields.io/pypi/l/raise-cli)](https://github.com/humansys/raise/blob/main/LICENSE)

## What is RaiSE?

RaiSE provides **governance, memory, and structured workflows** for AI-assisted software engineering. You decide *what* to build. Rai (your AI partner) executes with accumulated memory and calibrated judgment. RaiSE provides the discipline that makes the collaboration reliable.

The result: AI that learns from your project, follows your rules, and compounds knowledge across sessions instead of starting fresh every time.

## Install

```bash
pip install raise-cli
```

Optional integrations:

```bash
# Jira + Confluence adapters
pip install "raise-cli[jira,confluence]"

# MCP server support
pip install "raise-cli[mcp]"

# All extras
pip install "raise-cli[jira,confluence,mcp,csharp,observability]"
```

Requires Python 3.12 or 3.13.

## Quick start

```bash
# Initialize a project
rai init

# Start a session (loads context, memory, proposes work)
rai session start --project . --context

# Build the knowledge graph
rai graph build
```

Then work through skills in your AI assistant (Claude Code, Cursor, Windsurf):

```
/rai-session-start       → Load context, propose focused work
/rai-story-start         → Scope a piece of work
/rai-story-plan          → Decompose into tasks
/rai-story-implement     → TDD: test, code, verify, commit
/rai-story-review        → Extract learnings
/rai-story-close         → Merge and clean up
/rai-session-close       → Capture session outcomes
```

## Key features

### Structured workflows
44 skills covering the full SDLC — epic, story, bugfix, discovery, session management, documentation, and release.

### Knowledge graph
Project context, patterns, and cross-session memory — queryable and persistent.

```bash
rai graph query "testing patterns" --types pattern --limit 5
```

### Backlog management
Built-in adapters for Jira and filesystem-backed backlogs.

```bash
rai backlog search "project = MYPROJECT AND status = 'In Progress'"
rai backlog create "Fix pagination bug" -p MYPROJECT -t Bug
rai backlog transition MYPROJECT-123 done
```

### Documentation publishing
Publish to Confluence, local filesystem, or both (dual-write).

```bash
rai docs publish adr --title "ADR-045: Auth Architecture"
```

### Quality gates
Automated checks before commits and releases.

```bash
rai gate check --all        # Run all gates
rai release check           # 10-point release checklist
```

### Session continuity
Memory that compounds across sessions — patterns, calibration, coaching corrections.

```bash
rai session start --context  # Loads everything from prior sessions
rai pattern add "Always validate frontmatter before writing"
```

### Multi-language discovery
Scan codebases and build knowledge graphs from: Python, TypeScript, JavaScript, C#, PHP, Dart, Svelte.

```bash
rai discover scan src/ --language python --output summary
```

## CLI commands

72 subcommands across 17 groups:

| Group | Commands |
|-------|----------|
| `init` | Initialize project governance |
| `session` | start, close, context, journal, doctor |
| `graph` | build, query, context |
| `pattern` | add, query |
| `backlog` | create, get, search, transition, update, link, comment |
| `docs` | publish, get, search |
| `skill` | list, validate, check-name, scaffold |
| `discover` | scan |
| `adapter` | list, check, validate, status |
| `mcp` | list, health, tools, call, install, scaffold |
| `gate` | list, check |
| `doctor` | diagnostics with --fix auto-remediation |
| `release` | check, publish |

## Documentation

- **[Getting Started](https://docs.raiseframework.ai/)** — Install and run your first session
- **[Guides](https://docs.raiseframework.ai/guides/first-story/)** — Your First Story, Configuring Integrations, Bugfix Lifecycle
- **[CLI Reference](https://docs.raiseframework.ai/cli/)** — Every command, flag, and option
- **[Concepts](https://docs.raiseframework.ai/concepts/)** — Memory, Skills, Governance, Knowledge Graph

## License

Apache 2.0 — see [LICENSE](https://github.com/humansys/raise/blob/main/LICENSE).
