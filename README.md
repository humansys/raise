# RaiSE

AI coding assistants are fast, but their context resets between sessions, quality checks are opt-in, and decision history is scattered across tool logs. RaiSE persists workflow state, runs your validation commands between phases, and records the artifacts behind each change.

```bash
# Install the global binary (recommended — no Python required)
curl -fsSL https://github.com/humansys/raise/releases/latest/download/install.sh | bash
cd your-project && rai init --detect
```

> Works with **Claude Code** · **Cursor** · **Aider** · **Cline** · **Devin** · **Kimi** — CLI works alongside any assistant; full workflow integration varies by tool.

---

## Why This Exists

Most agent workflows rely on prompt instructions like "NEVER skip steps." The LLM skips them anyway — prompt instructions are requests, not constraints. The quality gate that catches this can't be another AI opinion. It has to be code.

CI validates a commit *after* work has been produced. RaiSE runs the same checks *before* the workflow advances, and retains the design and decision artifacts used to produce the change — `scope.md`, `design.md`, `plan.md`, gate results — creating versioned evidence that supports SOC 2, ISO 27001, and EU AI Act traceability requirements.

Within a RaiSE pipeline, a phase cannot advance when a configured gate fails. Not "I checked myself and I'm good" — actual test suites, linters, and type checkers that run as code.

**What's enforced vs. guided:** skills are instructions — an agent can deviate from them, like any prompt. What it can't do is fake a gate result: pipeline state and gate outcomes are produced by real command runs and stored in versioned files under `.raise/`. If work bypassed the pipeline, the artifact trail shows the gap — and CI can require a clean trail before merge, closing the loop with the same enforcement you already trust.

---

## What RaiSE Adds to Your AI Tool

RaiSE is not another coding assistant. It's the governance layer that coordinates what your tools already do.

| Concern | Existing pieces | RaiSE contribution |
|---|---|---|
| **Workflow state** | Plans, issues, tool-specific history | A persisted, resumable workflow state machine |
| **Validation** | CI, pre-commit, tests, lint, types | Runs checks at workflow phase boundaries (design → plan → implement → review), not just at commit or push |
| **Traceability** | Git, issues, ADRs, logs | Links scope → design → implementation → review → gate results in versioned artifacts |
| **Context** | Tool memory, AST/LSP indexes | Repo-local persistent memory plus an AST-derived dependency graph |
| **Portability** | Tool-specific configuration (CLAUDE.md, .cursorrules) | Shared governance artifacts across tools with integration-specific adapters |
| **Backlog & docs** | Manual Jira updates, Confluence copy-paste | `rai backlog` syncs Jira status; `rai docs publish` pushes artifacts to Confluence |

---

## Quick Start

### Install

```bash
# Recommended: global binary (no Python required)
curl -fsSL https://github.com/humansys/raise/releases/latest/download/install.sh | bash

# Windows (PowerShell)
irm https://github.com/humansys/raise/releases/latest/download/install.ps1 | iex
```

Fully functional on its own — sessions, graph, gates, pipelines, backlog adapters — with no server and no account. Project state stays under `.raise/` in your repo; developer config under `~/.rai/`. RaiSE sends no data unless you configure an external adapter.

<details>
<summary>Alternative install methods (per-project venv, pip, pipx)</summary>

```bash
# Isolated CLI install (requires Python 3.12+)
uv tool install raise-cli
# or
pipx install raise-cli

# pip
pip install raise-cli

# Per-project venv one-liner
curl -LsSf https://docs.raiseframework.ai/install.sh | bash
```

The global binary is the recommended method. These alternatives require
Python 3.12+ and are kept for environments where the binary is not an option.
See the [Migration Guide](https://docs.raiseframework.ai/latest/guides/migration-venv-to-binary/)
if upgrading from one of these.

</details>

### Initialize

```bash
$ rai init --detect                        # illustrative output
✓ Detected: Python 3.12, pytest, ruff, pyright
✓ Created .raise/ with project governance
✓ Registered 4 validation gates (tests, lint, format, types)
Ready. Run /rai-welcome in your AI coding tool.
```

Works on existing codebases. `--detect` reads your stack and configures gates from what's already there — no greenfield scaffolding required.

### First Session (Claude Code example)

```
/rai-welcome              # One-time onboarding — creates your developer profile
/rai-session-start        # Loads prior context, memory, and proposes focus
```

Then work using the governed lifecycle:

```
/rai-story-start          # Branch + scope
/rai-story-design         # Design the approach (optional for small changes)
/rai-story-plan           # Break into tasks
/rai-story-implement      # TDD execution — gates block advancement on failure
/rai-story-review         # Retrospective, capture patterns
/rai-story-close          # Merge + cleanup
/rai-session-close        # Persist learnings for next session
```

After close, your repo contains `scope.md`, `design.md`, `plan.md`, passing gate results, and captured patterns — every decision traceable for audits or onboarding new contributors.

Need to work on multiple stories at once? `/rai-worktree-open` gives each story its own isolated branch, pipeline state, and memory scope.

> Using Cursor or Aider? The `rai` CLI works standalone: `rai session start`, `rai gate check gate-tests`. Skills are portable markdown — they work in any tool that supports custom instructions.

> **Full guide:** [Getting Started](https://docs.raiseframework.ai/latest/getting-started/) · [Installation](https://docs.raiseframework.ai/latest/installation/) · [First Story](https://docs.raiseframework.ai/latest/guides/first-story/)

---

## How It Works

### Deterministic Pipeline Coordinator

Each phase of your workflow is a **skill** — a structured set of steps. The pipeline coordinator blocks phase transitions when a configured gate fails.

```
story-start → design → plan → implement → review → close
                                  │
                          ┌───────┴────────┐
                          │  Gate: tests   │  ← deterministic,
                          │  Gate: lint    │    not AI opinion
                          │  Gate: types   │
                          │  Gate: format  │
                          └────────────────┘
```

Gates are configurable per project via YAML. Failed gates stop the workflow — no accumulating errors.

### Knowledge Graph

RaiSE builds an AST-derived call and dependency graph of your codebase — not keyword similarity, but actual import chains, call sites, and inheritance relationships.

```bash
$ rai graph build                          # illustrative output
✓ Scanned 847 symbols across 12 modules
✓ Built 2,341 edges (calls, imports, inherits, implements)

$ rai graph query "auth flow"
→ mod-auth: AuthService.authenticate → TokenStore.issue → AuditLog.record
  3 cross-module dependencies, 2 governance rules apply
```

Your agent gets the component that's actually being called — not the one with the closest name.

### Persistent Memory

| What persists | Where it lives | How it helps |
|---|---|---|
| **Patterns** | `.raise/rai/memory/` | Learned from your work — recurring failure patterns become suggested guardrails for future stories |
| **Session history** | `.raise/rai/personal/` | Decisions made, items deferred, context restored |
| **Knowledge graph** | `.raise/rai/memory/index.json` | Project architecture and dependency relationships |
| **Calibration** | `.raise/rai/personal/` | Your velocity and working patterns |

Project state stays under `.raise/` in your repo; developer-level config under `~/.rai/`. Memory is portable across AI tools — switch from Claude Code to Cursor and your governance context follows.

### Autonomy Levels

Your level of trust dictates how much the agent does unsupervised:

| Level | Behavior | For |
|---|---|---|
| **Supervised** | Pauses at every gate for review | New to RaiSE or high-risk repos |
| **Delegated** | Autonomous on routine, pauses on novel decisions | Day-to-day development |
| **Autonomous** | Fully autonomous, pauses only on design decisions or persistent errors | Senior developers, trusted codebases |

---

## Packages

| Package | Description | Install |
|---|---|---|
| **raise-cli** | `rai` CLI — sessions, graph, gates, pipelines, backlog | Global binary (see [Install](#install)) or `pip install raise-cli` |
| **raise-core** | Core library — graph, memory, patterns, discovery | Bundled with the binary, or `pip install raise-core` |

Open Core (Apache-2.0). Fully functional on its own — no server, no account. [RaiSE Pro](https://raiseframework.ai) adds team governance, shared services, and hosted runners for organizations that need them.

---

## CLI Reference

```bash
rai init --detect              # Initialize RaiSE on your project
rai session start              # Start a working session
rai session close              # End session, persist learnings
rai graph build                # Build the knowledge graph
rai graph query "auth flow"    # Query project architecture
rai gate check gate-tests      # Run validation gates
rai skill list                 # List available skills
rai doctor                     # Diagnostics and health check
```

> **Full CLI reference:** [docs.raiseframework.ai/latest/cli](https://docs.raiseframework.ai/latest/cli/)

---

## Skills

Skills are structured workflows — portable markdown files that guide AI-assisted development. They work in any tool that supports custom instructions.

| Category | Skills |
|---|---|
| **Session** | `rai-welcome` · `rai-session-start` · `rai-session-close` |
| **Story** | `rai-story-start` · `rai-story-design` · `rai-story-plan` · `rai-story-implement` · `rai-story-review` · `rai-story-close` |
| **Epic** | `rai-epic-start` · `rai-epic-design` · `rai-epic-plan` · `rai-epic-close` |
| **Quality** | `rai-quality-review` · `rai-architecture-review` · `rai-debug` |
| **Research** | `rai-research` · `rai-problem-shape` |
| **Project** | `rai-project-create` · `rai-project-onboard` · `rai-discover` |

---

## Background

RaiSE has been in development since late 2023, born from a practical problem: a team that lost its developers and had to ship production software using AI assistants — software that had to pass financial regulatory review, CI pipelines, SonarQube, and security audits. RAG wasn't enough. Prompt engineering wasn't enough. What worked was a deterministic governance layer with an AST-derived knowledge graph.

Developed and used in production environments since 2023. Built by [HumanSys](https://humansys.ai).

---

## Documentation

- [Getting Started](https://docs.raiseframework.ai/latest/getting-started/)
- [Installation Guide](https://docs.raiseframework.ai/latest/installation/)
- [Concepts Overview](https://docs.raiseframework.ai/latest/concepts/)
- [CLI Reference](https://docs.raiseframework.ai/latest/cli/)
- [Pipeline Quickstart](https://docs.raiseframework.ai/latest/guides/pipeline-quickstart/)

---

## Status

Current release: **v3.1.0** (GA, 2026-09-01). Install the [global binary](https://github.com/humansys/raise/releases/latest), or `pip install raise-cli`.

- **Questions or bugs?** [Open an issue](https://github.com/humansys/raise/issues) (GitHub)
- **Want to try it?** `curl -fsSL https://github.com/humansys/raise/releases/latest/download/install.sh | bash && rai init --detect`

---

## Support

Release lines, lifecycle stages, EOL dates, and how to get help are in the
[Support & Lifecycle Policy](docs/support-policy.md). GitHub Issues is the
primary channel; security vulnerabilities go to the contact in
[SECURITY.md](SECURITY.md).

---

## License

[Apache-2.0](LICENSE)
