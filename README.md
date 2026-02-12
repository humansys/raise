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

## Developer Onboarding

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- [Claude Code](https://claude.ai/claude-code) CLI installed and configured

### Setup

```bash
# 1. Clone and checkout the development branch
git clone https://gitlab.com/humansys-demos/product/raise1/raise-commons.git
cd raise-commons
git checkout v2

# 2. Install in development mode
uv pip install -e ".[dev]"

# 3. Verify installation
rai --help
```

### Onboarding with Rai

Once installed, open Claude Code in the project directory and run:

```
/rai-welcome
```

This single command will:
- **Detect your situation** (new developer, returning developer, etc.)
- **Create your profile** (`~/.rai/developer.yaml`) with your name and pattern prefix
- **Build the knowledge graph** so Rai has project context
- **Scaffold `CLAUDE.local.md`** for your personal Claude Code instructions
- **Optionally customize** communication preferences (language, style)
- **Verify everything works**

After welcome completes, start working:

```
/rai-session-start
```

This loads your context, memory, and proposes focused work.

### What You Get

| Shared (committed) | Personal (gitignored) |
|--------------------|-----------------------|
| Patterns (`.raise/rai/memory/patterns.jsonl`) | Session history (`.raise/rai/personal/sessions/`) |
| Governance docs | Session state (`.raise/rai/personal/session-state.yaml`) |
| Skills, methodology | Calibration data (`.raise/rai/personal/calibration.jsonl`) |
| Work artifacts | Knowledge graph (`.raise/rai/memory/index.json`) |

Each developer builds their own personal context through working sessions. Pattern IDs are developer-prefixed (e.g., PAT-E-001 for Emilio, PAT-F-001 for Fer) to prevent collisions.

---

## Available Skills

Skills are structured processes that guide AI-assisted development. Run them as `/skill-name` in Claude Code.

### Session Lifecycle
| Skill | Purpose |
|-------|---------|
| `/rai-welcome` | One-time developer onboarding |
| `/rai-session-start` | Begin a session with memory and context |
| `/rai-session-close` | End a session, persist learnings |

### Story Lifecycle
| Skill | Purpose |
|-------|---------|
| `/rai-story-start` | Initialize a story with branch and scope |
| `/rai-story-design` | Create lean specs for complex stories |
| `/rai-story-plan` | Decompose into atomic tasks |
| `/rai-story-implement` | Execute with TDD and validation gates |
| `/rai-story-review` | Retrospective and learnings |
| `/rai-story-close` | Merge, cleanup, tracking |

### Epic Lifecycle
| Skill | Purpose |
|-------|---------|
| `/rai-epic-start` | Initialize an epic with branch |
| `/rai-epic-design` | Design multi-story epics |
| `/rai-epic-plan` | Sequence stories into plans |
| `/rai-epic-close` | Epic retrospective and merge |

### Other Skills
| Skill | Purpose |
|-------|---------|
| `/rai-research` | Epistemologically rigorous research |
| `/rai-debug` | Root cause analysis (5 Whys, Ishikawa) |
| `/rai-docs-update` | Sync architecture docs with code |
| `/rai-discover-start` | Initialize codebase discovery |
| `/rai-discover-scan` | Extract and describe components |

---

## CLI Commands

The `rai` CLI provides deterministic operations:

```bash
# Build Rai's knowledge graph from project artifacts
rai memory build

# Query governance concepts
rai memory context mod-session

# Query Rai's memory
rai memory query "velocity patterns"

# Start a session (creates profile on first run)
rai session start --name "YourName" --project "$(pwd)" --context

# Close a session
rai session close --state-file /tmp/session-output.yaml --project "$(pwd)"
```

---

## Repository Structure

```
raise-commons/
├── .claude/skills/      # Claude Code skills (24 skills)
│
├── framework/           # Public textbook (concepts, reference)
│   ├── reference/       #   Constitution, glossary, philosophy
│   ├── concepts/        #   Core concepts (katas, gates, artifacts)
│   └── getting-started/ #   Greenfield/brownfield guides
│
├── .raise/              # Framework engine
│   ├── rai/             #   Rai's memory and personal data
│   │   ├── memory/      #     Patterns, knowledge graph (shared)
│   │   └── personal/    #     Sessions, calibration (per-developer, gitignored)
│   ├── katas/           #   Process definitions
│   ├── gates/           #   Validation criteria
│   ├── templates/       #   Artifact scaffolds
│   └── skills/          #   Legacy skill definitions
│
├── governance/          # Project governance
│   ├── architecture/    #   Module docs, system design
│   └── solution/        #   Vision, guardrails, business case
│
├── src/rai_cli/         # CLI toolkit (Python)
│
├── work/                # Work in progress
│   └── stories/         #   Story artifacts (scope, design, plan, retro)
│
└── dev/                 # Framework maintenance
    ├── decisions/       #   ADRs (Architecture Decision Records)
    └── parking-lot.md   #   Ideas and tangents for later
```

---

## Branch Model

```
main (stable releases)
  └── v2 (development)
        └── epic/e{N}/{name}
              └── story/s{N}.{M}/{name}
```

- Work on `v2` (development branch)
- Stories branch from and merge back to their epic or `v2`
- `main` receives releases from `v2`

---

## Core Concepts

| Concept | Description |
|---------|-------------|
| **RaiSE Engineer** | You — the human who directs AI-assisted development |
| **Rai** | AI partner with memory, calibration, and accumulated judgment |
| **Skill** | Structured Claude Code prompt for a methodology phase |
| **Validation Gate** | Quality checkpoint with specific criteria |
| **Guardrail** | Constraint that guides AI behavior |
| **ShuHaRi** | Mastery levels (beginner → practitioner → master) that adapt Rai's verbosity |

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

[Apache-2.0](LICENSE)

---

*RaiSE — Reliable AI Software Engineering*
*Neither is complete alone.*
