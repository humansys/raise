# RaiSE

**Reliable AI Software Engineering** — Governance that makes AI-assisted development actually reliable.

[![PyPI version](https://img.shields.io/pypi/v/rai-cli.svg)](https://pypi.org/project/rai-cli/)
[![Python versions](https://img.shields.io/pypi/pyversions/rai-cli.svg)](https://pypi.org/project/rai-cli/)
[![License](https://img.shields.io/pypi/l/rai-cli.svg)](https://github.com/humansys-ai/raise-commons/blob/main/LICENSE)

---

## What does it look like?

```
$ pip install rai-cli
$ cd your-project
$ rai init --detect

✓ Detected: Python 3.12, pytest, ruff, pyright
✓ Scaffolded .raise/ governance structure
✓ Built knowledge graph (47 components, 12 modules)

# Open Claude Code and start working:

> /rai-session-start

Session: 2026-02-12
Context: your-project → 47 components mapped
Focus: Ready for first story
Signals: None

Go.

> /rai-story-start S1

Branch: story/s1/add-auth-middleware
Scope commit: a1b2c3d

> /rai-story-implement

Task 1/3: Write failing test for auth middleware... ✓
Task 2/3: Implement middleware to pass test... ✓
Task 3/3: Integration test... ✓
All gates passed. Ready for review.
```

Rai remembers your patterns, calibrates to your velocity, and maintains coherence across sessions. Every session builds on the last.

---

## Why RaiSE?

AI coding assistants are fast but unreliable. They generate code without memory, context, or quality discipline. The result: inconsistent output that needs constant human correction.

RaiSE fixes this with three things:

- **Governance as code** — Quality standards, guardrails, and validation gates versioned in your repo. The AI follows them automatically.
- **Persistent memory** — Patterns learned, mistakes corrected, calibration accumulated. Session 50 is better than session 1.
- **Structured workflow** — Story lifecycle from scope to retrospective. TDD enforcement, atomic commits, human-in-the-loop gates.

---

## Features

**24 skills** that guide AI-assisted development through structured workflows:

| Category | Skills | What they do |
|----------|--------|-------------|
| **Session** | `session-start`, `session-close` | Load context, persist learnings between sessions |
| **Story** | `story-start` through `story-close` | Full development lifecycle with TDD and validation gates |
| **Epic** | `epic-start` through `epic-close` | Multi-story planning with milestones and dependencies |
| **Discovery** | `discover-start`, `discover-scan` | Map existing codebases — Python, TypeScript, JavaScript, PHP, Svelte |
| **Research** | `research`, `debug` | Epistemologically rigorous research and root cause analysis |

**Knowledge graph** that gives the AI real context about your codebase — modules, dependencies, architecture decisions, not just file contents.

**Memory system** that accumulates patterns, calibration data, and coaching corrections across sessions. Rai gets better at working with *your* codebase over time.

---

## Quick Start

```bash
# Install
pip install rai-cli

# Initialize on your project
cd your-project
rai init --detect

# Open Claude Code and onboard
claude
> /rai-welcome
```

**Requirements:** Python 3.12+, [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI

After onboarding, start each session with `/rai-session-start` and Rai proposes focused work based on where you left off.

---

## How It Works

```
/rai-session-start          Load context, see what's pending
    ↓
/rai-story-start            Create branch, define scope
    ↓
/rai-story-plan             Break into atomic tasks
    ↓
/rai-story-implement        TDD execution with validation gates
    ↓
/rai-story-review           Retrospective, capture patterns
    ↓
/rai-story-close            Merge, cleanup
    ↓
/rai-session-close          Persist learnings for next session
```

You don't need to complete all steps in one session — Rai remembers where you left off.

---

## Documentation

- [Getting Started Guide](framework/getting-started/)
- [Constitution & Principles](framework/reference/constitution.md)
- [Glossary](framework/reference/glossary.md)
- [Contributing](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)

---

## Community

- [Report a bug](https://github.com/humansys-ai/raise-commons/issues/new?template=bug-report.yml)
- [Request a feature](https://github.com/humansys-ai/raise-commons/issues/new?template=feature-request.yml)
- [Security policy](SECURITY.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)

---

## Status

Pre-release (`v2.0.0-alpha`). Used in production but the API may change. We value your feedback — [open an issue](https://github.com/humansys-ai/raise-commons/issues) or reach out directly.

---

## License

[Apache-2.0](LICENSE)

*RaiSE — Reliable AI Software Engineering. Raise your craft, one story at a time.*
