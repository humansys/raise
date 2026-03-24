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

### Quick Install

```bash
pipx install rai-cli
rai --version
```

> **Detailed instructions** for macOS, Linux, and Windows (WSL) — including known pitfalls and troubleshooting — are in the **[Installation Guide](docs/installation.md)**.

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

Each developer builds their own personal context through working sessions. Pattern IDs are developer-prefixed (e.g., PAT-A-001 for Alice, PAT-B-001 for Bob) to prevent collisions in shared repositories.

---

## Usage

### Initialize RaiSE on Your Project

```bash
# Navigate to your existing project
cd your-project

# Initialize RaiSE governance structure
rai init --detect

# Open Claude Code and run onboarding
/rai-welcome
```

This scaffolds the `.raise/` directory, detects your project's conventions (language, testing framework, linting), and builds the knowledge graph.

### Daily Workflow

A typical session follows this pattern:

```
1. /rai-session-start          # Load context, see what's pending
2. /rai-story-start             # Create branch, define scope
3. /rai-story-design            # Design the approach (recommended)
4. /rai-story-plan              # Break into atomic tasks
5. /rai-story-implement         # TDD execution with validation gates
6. /rai-story-review            # Retrospective, capture patterns
7. /rai-story-close             # Merge, cleanup
8. /rai-session-close           # Persist learnings for next session
```

You don't need to complete all steps in one session — Rai remembers where you left off.

### What Rai Remembers

- **Patterns** — Reusable insights learned from your work (e.g., "always validate config at boundaries")
- **Calibration** — Your velocity, strengths, growth edges
- **Session history** — What you worked on, decisions made, items deferred
- **Coaching corrections** — Mistakes Rai made and learned from

Each session builds on the last. Over time, Rai becomes a more effective collaborator for your specific codebase and working style.

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

### Discovery Skills
| Skill | Purpose |
|-------|---------|
| `/rai-discover-start` | Initialize codebase discovery |
| `/rai-discover-scan` | Extract and describe components |
| `/rai-discover-validate` | Validate synthesized descriptions with human review |
| `/rai-discover-document` | Generate architecture docs from discovery data |

### Project Skills
| Skill | Purpose |
|-------|---------|
| `/rai-welcome` | One-time developer onboarding |
| `/rai-project-create` | Guide greenfield project setup |
| `/rai-project-onboard` | Guide brownfield project onboarding |

### Analysis & Quality
| Skill | Purpose |
|-------|---------|
| `/rai-research` | Epistemologically rigorous research |
| `/rai-debug` | Root cause analysis (5 Whys, Ishikawa) |
| `/rai-quality-review` | Critical code review with external auditor perspective |
| `/rai-architecture-review` | Evaluate design proportionality and necessity |
| `/rai-problem-shape` | Guided problem definition at portfolio level |

### Maintenance
| Skill | Purpose |
|-------|---------|
| `/rai-docs-update` | Sync architecture docs with code |
| `/rai-framework-sync` | Sync framework files across locations |
| `/rai-publish` | Structured release workflow with quality gates |

---

## CLI Commands

The `rai` CLI provides deterministic operations:

```bash
# Build Rai's knowledge graph from project artifacts
rai graph build

# Query governance concepts
rai graph context mod-session

# Query Rai's memory
rai graph query "velocity patterns"

# Validate the memory graph (structural + completeness)
rai graph validate

# Visualize the memory graph as interactive HTML
rai graph viz                    # Opens in browser
rai graph viz --output graph.html  # Custom output path

# List releases and their associated epics
rai release list

# Start a session (creates profile on first run)
rai session start --name "YourName" --project "$(pwd)" --context

# Close a session
rai session close --state-file /tmp/session-output.yaml --project "$(pwd)"
```

---

## Project Structure

This is a **uv workspace monorepo** with 5 packages:

| Package | Description | PyPI |
|---------|-------------|------|
| **raise-core** | Graph, memory, patterns, discovery engine | `pip install raise-core` |
| **raise-cli** | `rai` CLI toolkit (session, graph, backlog, gates) | `pip install raise-cli` |
| **rai-agent** | Autonomous agent daemon (Telegram, cron, Claude Code) | `pip install rai-agent` |
| **raise-pro** | Enterprise integrations (Jira, Confluence) | Private |
| **raise-server** | REST API + PostgreSQL backend | Private |

```
raise-commons/
├── packages/
│   ├── raise-core/        # Core library (graph, memory, patterns)
│   ├── raise-cli/         # CLI toolkit
│   ├── rai-agent/         # Agent daemon + Dockerfile
│   ├── raise-pro/         # Enterprise integrations (private)
│   └── raise-server/      # API server (private)
│
├── .claude/skills/        # Claude Code skills (27 skills)
├── framework/             # Public textbook (concepts, reference)
├── .raise/                # Framework engine (memory, gates, templates)
├── governance/            # Architecture docs, guardrails
├── work/                  # Epics and story artifacts
└── docker-compose.yml     # Local dev + rai-agent deployment
```

## Running rai-agent with Docker

The fastest way to run rai-agent (Telegram bot + daemon):

```bash
git clone https://github.com/humansys/raise.git
cd raise
cp .env.example .env   # Edit: add your auth + Telegram bot token
docker compose up rai-agent
```

See `.env.example` for all supported authentication methods:
- Claude subscription (Pro/Max) via `claude setup-token`
- Anthropic API key (BYOK, pay-as-you-go)
- AWS Bedrock, Google Vertex AI, Azure Foundry
- LLM Proxy / Gateway

---

## Branch Model

```
main (stable releases)
  └── dev (development)
        └── story/s{N}.{M}/{name}
```

- Stories branch from and merge to `dev`
- Epics are logical containers (directory + tracker), not branches
- `main` receives releases from `dev`

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

## Status

Current stable release: `v2.1.0`. The framework is being used in production.

We value your feedback:

- **Questions?** Open an [issue](https://gitlab.com/humansys-demos/product/raise1/raise-commons/-/issues)
- **Found a bug?** Open an [issue](https://gitlab.com/humansys-demos/product/raise1/raise-commons/-/issues) with reproduction steps
- **Ideas?** We want to hear them — open an issue or reach out directly

---

## License

[Apache-2.0](LICENSE)

---

*RaiSE — Reliable AI Software Engineering*
*Neither is complete alone.*
