# RaiSE CLI

**Reliable AI Software Engineering** — governance, memory, and structured workflows for AI-assisted development.

[![PyPI](https://img.shields.io/pypi/v/raise-cli)](https://pypi.org/project/raise-cli/)
[![Python](https://img.shields.io/pypi/pyversions/raise-cli)](https://pypi.org/project/raise-cli/)
[![License](https://img.shields.io/pypi/l/raise-cli)](https://github.com/humansys/raise/blob/main/LICENSE)

---

AI coding assistants are powerful. They're also unreliable. They forget your conventions between sessions. They don't know your architecture decisions. They optimize for speed over correctness. Left ungoverned, they produce code that *looks* right but subtly isn't.

RaiSE fixes this through three collaborating parts:

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

**You** decide what to build and why. **Rai** executes with accumulated memory and calibrated judgment. **RaiSE** provides the discipline — skills, governance, and quality gates — that makes the collaboration reliable.

The result: AI that learns from your project, follows your rules, and compounds knowledge across sessions instead of starting fresh every time.

## Install

### Quick install (recommended)

Per-project isolation — each project gets its own version:

```bash
cd your-project
curl -LsSf https://docs.raiseframework.ai/install.sh | bash
```

Windows (PowerShell):

```powershell
cd your-project
powershell -ExecutionPolicy ByPass -c "irm https://docs.raiseframework.ai/install.ps1 | iex"
```

### Manual install

```bash
pip install raise-cli        # latest stable
pip install raise-cli --pre  # latest pre-release
```

Requires **Python 3.12 or 3.13**. See the [Installation Guide](https://docs.raiseframework.ai/3.0/installation/) for platform-specific notes and troubleshooting.

## Getting started

```bash
cd your-project
rai init           # create .raise/ governance structure
```

Open your AI assistant ([Claude Code](https://claude.ai/claude-code), Cursor, or Windsurf) in the project directory and run:

```
/rai-welcome          → First-time setup: developer profile + knowledge graph
/rai-session-start    → Load context, memory, and propose focused work
```

## The story lifecycle

Every piece of work follows six steps — the core rhythm of RaiSE:

```
/rai-story-start     → Scope: what are we building?
/rai-story-design    → Spec: how will it work?
/rai-story-plan      → Tasks: decompose into steps
/rai-story-implement → Build: test, code, verify, commit
/rai-story-review    → Reflect: what did we learn?
/rai-story-close     → Ship: merge and clean up
```

Each step produces an artifact that feeds the next. Reviews capture patterns into memory. Memory feeds future sessions. This is how learning compounds — not through magic, but through disciplined repetition.

## What's inside

**Governance** — Layered rules (principles → requirements → guardrails → code) loaded at session start and enforced throughout. Everything traceable, everything in Markdown.

**Memory** — Patterns, calibration data, and session history that persist across sessions. Session 1 is discovery. Session 50 is expertise.

**Knowledge Graph** — Connects governance, memory, skills, and code into a queryable structure. The CLI traverses this graph to deliver the right context for your current work.

**Skills** — 44 structured workflows covering epics, stories, bugfixes, discovery, documentation, and releases. Each adapts to your experience level (Shu-Ha-Ri).

**Quality Gates** — Automated verification at every step. Tests, types, lint, coverage, architectural drift detection, and release readiness checks.

**Integrations** — Jira, Confluence, and filesystem adapters. MCP server for AI tool orchestration. Multi-language code discovery (Python, TypeScript, JavaScript, C#, PHP, Dart, Svelte).

## Documentation

- **[Getting Started](https://docs.raiseframework.ai/3.0/getting-started/)** — Install, initialize, and run your first session
- **[Your First Story](https://docs.raiseframework.ai/3.0/guides/first-story/)** — Walk through the full story lifecycle
- **[Core Concepts](https://docs.raiseframework.ai/3.0/concepts/)** — Memory, Skills, Governance, Knowledge Graph
- **[CLI Reference](https://docs.raiseframework.ai/3.0/cli/)** — Every command, flag, and option
- **[Guides](https://docs.raiseframework.ai/3.0/guides/)** — Integrations, pipelines, extending RaiSE

## License

Apache 2.0 — see [LICENSE](https://github.com/humansys/raise/blob/main/LICENSE).
