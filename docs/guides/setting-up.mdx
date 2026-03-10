---
title: Setting Up a Project
description: Configure a RaiSE project from scratch or onboard an existing codebase — governance, memory, and skills.
---

This guide covers how to set up a RaiSE project — whether you're starting from scratch (greenfield) or adding RaiSE to an existing codebase (brownfield).

## Greenfield: New Project

### Initialize

```bash
mkdir my-project && cd my-project
git init
rai init --name my-project
```

This creates the `.raise/` directory:

```
.raise/
├── manifest.yaml          # Project metadata
└── rai/
    ├── memory/
    │   ├── patterns.jsonl  # Learned patterns
    │   └── index.json      # Unified memory index
    ├── session-state.yaml  # Current session state
    ├── identity/
    │   ├── core.md         # Rai's identity
    │   └── perspective.md  # Rai's perspective
    └── personal/           # Your private data (gitignored)
        ├── sessions/
        └── telemetry/
```

### Set Up Governance

RaiSE creates a `governance/` directory with templates:

```
governance/
├── constitution.md     # Your principles
├── prd.md              # Your requirements
├── guardrails.md       # Your rules
├── backlog.md          # Your work items
└── architecture/
    ├── system-context.md
    └── system-design.md
```

Fill these in with your project's specifics:

1. **Constitution** — What are your non-negotiable principles? "Type annotations on all code." "Tests before implementation." Write 5-10 of these.

2. **PRD** — What are you building? Define 3-5 requirements at the feature level.

3. **Guardrails** — What rules must your code follow? Use MUST for non-negotiable, SHOULD for recommended. Link each guardrail to a requirement.

You don't need to fill everything at once. Start with a few principles and guardrails. Add more as you learn what matters for your project.

### Set Up Skills

Skills live in `.claude/skills/`. RaiSE comes with a standard set of lifecycle skills. To see what's available:

```bash
rai skill list
```

You can create project-specific skills:

```bash
rai skill scaffold my-custom-skill --lifecycle utility
```

### Build Memory

After filling governance files, build the memory index:

```bash
rai graph build
```

This creates the unified knowledge graph from all your governance documents, making them queryable and loadable into your AI's context.

### First Session

Open your AI assistant (Claude Code) in the project directory and run:

```
/rai-session-start
```

This loads your project's governance, memory, and skills into context. You're ready to work. From here, you interact through **skills** (`/rai-story-start`, `/rai-story-plan`, etc.) — they orchestrate the CLI for you.

## Brownfield: Existing Project

### Initialize with Detection

For existing codebases, use `--detect` to analyze conventions:

```bash
cd existing-project
rai init --detect
```

This does everything `rai init` does, plus:
- Scans your source code for patterns
- Identifies coding conventions (naming, formatting, imports)
- Detects testing patterns and frameworks
- Generates guardrails from detected conventions

Review the generated `governance/guardrails.md` — it's a starting point, not gospel. Adjust to match your team's actual standards.

### Discovery Scan

For deeper analysis, run the discovery pipeline:

```bash
# Scan source code
rai discover scan src/ --language python

# Analyze with confidence scoring
rai discover scan src/ -l python -o json | rai discover analyze

# Check for architectural drift later
rai discover drift
```

Discovery extracts your codebase's structure — classes, functions, modules — and builds a component map. This feeds into the knowledge graph, giving your AI partner architectural awareness.

### Integrate with Existing Workflow

RaiSE adds structure alongside your existing tools:

- **Git**: RaiSE uses standard Git branching. Story branches are created from your development branch (`dev`). Epics are logical containers (directories), not branches.
- **CI/CD**: RaiSE doesn't touch your pipeline. Guardrails are enforced at the AI level, not the CI level.
- **Editor**: Skills are invoked through your AI assistant (e.g., `/rai-story-start` in Claude Code). No editor plugin needed.

## Project Structure Reference

A fully set up RaiSE project looks like:

```
my-project/
├── .raise/                    # RaiSE runtime
│   ├── manifest.yaml
│   └── rai/
│       ├── memory/            # Shared memory (committed)
│       ├── personal/          # Private data (gitignored)
│       ├── session-state.yaml
│       └── identity/
├── .claude/
│   └── skills/                # Skill definitions
│       ├── session-start/
│       ├── story-start/
│       └── ...
├── governance/                # Project governance
│   ├── constitution.md
│   ├── prd.md
│   ├── guardrails.md
│   └── architecture/
├── work/                      # Work tracking
│   └── epics/
│       └── e01-my-epic/
│           ├── SCOPE.md
│           └── stories/
├── src/                       # Your code
└── tests/                     # Your tests
```

## What to Commit

| Directory | Commit? | Why |
|-----------|---------|-----|
| `.raise/rai/memory/` | Yes | Shared patterns and calibration |
| `.raise/rai/personal/` | No | Developer-specific, gitignored |
| `.raise/manifest.yaml` | Yes | Project metadata |
| `governance/` | Yes | Shared governance documents |
| `.claude/skills/` | Yes | Shared skill definitions |
| `work/epics/` | Yes | Work tracking and retrospectives |
