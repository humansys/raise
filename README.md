# RaiSE

**Reliable AI Software Engineering** — Ship quality software at AI speed.

> *Raise your craft, feature by feature.*

---

## What is RaiSE?

RaiSE is a methodology + toolkit for professional developers who use AI assistants. It solves the problem of AI-generated code that's fast but inconsistent: governance that works naturally, validation at every step, and memory that persists across sessions.

**The RaiSE Triad:**

```
        RaiSE Engineer
        (You - Strategy, Judgment, Ownership)
              │
              │ collaborates with
              ▼
           Rai
   (AI Partner - Execution + Memory)
              │
              │ governed by
              ▼
           RaiSE
    (Methodology + Toolkit)
```

**Rai** is your AI collaborator — not a generic assistant, but a partner trained in the discipline of reliable AI software engineering. Rai remembers your patterns, calibrates to your velocity, and maintains coherence across sessions.

---

## Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- [Claude Code](https://claude.ai/claude-code) CLI

### Installation

```bash
# Clone the repository
git clone https://gitlab.com/humansys-demos/product/raise1/raise-commons.git
cd raise-commons

# Install in development mode
uv pip install -e .

# Verify installation
uv run raise --help
```

### First Steps

1. **Start a session** — Run `/session-start` in Claude Code to load context and memory
2. **Explore skills** — Use `/help` to see available skills like `/feature-design`, `/research`
3. **Read the constitution** — `framework/reference/constitution.md` defines the principles

---

## Available Skills

Skills are structured processes that guide AI-assisted development:

| Skill | Purpose |
|-------|---------|
| `/session-start` | Begin a session with memory and context loaded |
| `/session-close` | End a session, persist learnings to memory |
| `/feature-design` | Create lean specs for complex features |
| `/feature-plan` | Decompose features into atomic tasks |
| `/feature-implement` | Execute implementation with validation gates |
| `/feature-review` | Retrospective to extract learnings |
| `/research` | Epistemologically rigorous research |
| `/epic-design` | Design multi-feature epics |
| `/epic-plan` | Sequence features into executable plans |
| `/debug` | Root cause analysis (5 Whys, Ishikawa) |

---

## CLI Commands

The `raise` CLI provides deterministic operations:

```bash
# Build concept graph from governance artifacts
uv run raise graph build

# Query governance concepts (MVC - Minimum Viable Context)
uv run raise context query "validation"

# Query Rai's memory
uv run raise memory query "velocity patterns"

# Dump memory for inspection
uv run raise memory dump --format md
```

---

## Repository Structure

```
raise-commons/
├── framework/           # Public textbook (concepts, reference)
│   ├── reference/       #   Constitution, glossary, philosophy
│   ├── concepts/        #   Core concepts (katas, gates, artifacts)
│   └── getting-started/ #   Greenfield/brownfield guides
│
├── .raise/              # Framework engine
│   ├── katas/           #   Process definitions (the HOW)
│   ├── gates/           #   Validation criteria (the QUALITY)
│   ├── templates/       #   Artifact scaffolds (the WHAT)
│   └── skills/          #   Atomic operations
│
├── .rai/                # Rai's identity and memory
│   ├── identity/        #   Core values, perspective, boundaries
│   └── memory/          #   Patterns, calibration, session history
│
├── .claude/skills/      # Claude Code skills (11 skills)
│
├── governance/          # Project governance
│   ├── solution/        #   Vision, guardrails, business case
│   └── projects/        #   Project-level artifacts, backlog
│
├── src/raise_cli/       # CLI toolkit (Python)
│
└── dev/                 # Framework maintenance
    ├── decisions/       #   ADRs (Architecture Decision Records)
    └── sessions/        #   Session logs
```

---

## Core Concepts

| Concept | Description |
|---------|-------------|
| **RaiSE Engineer** | You — the human who directs AI-assisted development |
| **Rai** | AI partner with memory, calibration, and accumulated judgment |
| **Kata** | Structured process definition for a methodology phase |
| **Validation Gate** | Quality checkpoint with specific criteria |
| **Guardrail** | Constraint that guides AI behavior |
| **MVC** | Minimum Viable Context — query what's relevant, not everything |

See the full [Glossary](framework/reference/glossary.md) for canonical terminology.

---

## Key Principles

From the [Constitution](framework/reference/constitution.md):

1. **Humans Define, Machines Execute** — Specs are source of truth
2. **Governance as Code** — Standards versioned in Git
3. **Validation Gates** — Quality checked at each phase
4. **Observable Workflow** — Every decision traceable
5. **Jidoka** — Stop on defects, don't accumulate errors

---

## For F&F Users

This is a pre-release (v2.0.0-alpha). We value your feedback:

- **Questions?** Open an [issue](https://gitlab.com/humansys-demos/product/raise1/raise-commons/-/issues)
- **Found a bug?** Open an [issue](https://gitlab.com/humansys-demos/product/raise1/raise-commons/-/issues) with reproduction steps
- **Ideas?** We want to hear them — open an issue or reach out directly

---

## License

[MIT](LICENSE)

---

*RaiSE — Reliable AI Software Engineering*
*Neither is complete alone.*
