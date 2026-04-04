# RaiSE Happy Path — Developer Guide

> Complete workflow reference for RaiSE-powered development.
> Generated from onboarding session, 2026-02-12.

---

## Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) or pip
- [Claude Code](https://claude.ai/claude-code) CLI installed and configured

```bash
# Install raise-cli (alpha — requires --pre flag)
pip install --pre raise-cli
# or: uv pip install --prerelease=allow raise-cli

# Verify
rai --help
```

---

## Phase 0: Project Setup

### Greenfield (new project)

```bash
mkdir my-project && cd my-project
git init
rai init                              # Creates .raise/, manifest.yaml, base structure
```

```
# In Claude Code:
/rai-welcome                          # Developer onboarding (profile, graph, context bundle)
/rai-project-create                   # Guided conversation to fill governance:
                                      #   -> vision.md, prd.md, guardrails.md, constitution
                                      #   -> runs: rai memory build
```

### Brownfield (existing project)

```bash
git clone <repo> && cd <repo>
rai init --detect                     # Detects existing conventions
```

```
# In Claude Code:
/rai-welcome                          # Developer onboarding
/rai-project-onboard                  # Guided conversation:
                                      #   -> Analyzes what already exists
                                      #   -> Fills governance with discovered context
                                      #   -> runs: rai memory build
```

### Codebase Discovery (optional, recommended for brownfield)

```
/rai-discover-start                   # Detect project type, languages, directories
/rai-discover-scan                    # Extract symbols (classes, functions, constants)
/rai-discover-validate                # HITL: human validates descriptions by confidence tier
/rai-discover-document                # Generate architecture docs (C4 Context + Container)
                                      #   -> governance/architecture/modules/*.md
                                      #   -> runs: rai memory build
```

---

## Phase 1: Session Lifecycle (every work block)

```
/rai-session-start                    # Loads: profile + previous state + graph + patterns
                                      # Rai interprets context and proposes focus
                                      # CLI: rai session start --context

    [WORK — see Phases 2-4]

/rai-session-close                    # Structured reflection:
                                      #   -> Patterns discovered -> patterns.jsonl
                                      #   -> Coaching corrections -> developer.yaml
                                      #   -> Work state -> session-state.yaml
                                      #   -> Session record -> personal/sessions/
                                      #   -> Telemetry -> personal/telemetry/
```

### When to close a session

- After finishing your work block (1-3 hours typical)
- When switching context (different epic/story)
- When Rai starts "forgetting" things (context window filling up)
- Always before closing Claude Code

---

## Phase 2: Epic Cycle (large body of work, 3-10 features)

```
/rai-epic-start                       # Initializes epic directory and scope
                                      #   -> Scope commit
                                      #   -> Telemetry: rai memory emit-work epic --phase init

/rai-epic-design                      # Designs the epic:
                                      #   -> Strategic objective -> features
                                      #   -> ADRs for architectural decisions
                                      #   -> May call /rai-research
                                      #   -> Writes: work/stories/E-{N}/epic-design.md

/rai-epic-plan                        # Sequences features:
                                      #   -> Milestones with dependencies
                                      #   -> Story execution order
                                      #   -> Writes: work/stories/E-{N}/epic-plan.md

    [STORY CYCLES — Phase 3, repeat per story]

/rai-epic-close                       # Closes the epic:
                                      #   -> Retrospective + metrics (planned vs actual)
                                      #   -> Updates backlog/tracker
                                      #   -> No branch merge (epics are logical containers)
```

---

## Phase 3: Story Cycle (deliverable unit)

```
/rai-story-start                      # Creates branch: story/sN.M/name
                                      #   -> Always branches from dev
                                      #   -> Scope commit: work/stories/S-NAME/scope.md

/rai-story-design                     # Lean specification (PAT-186: design is NOT optional):
                                      #   -> Integration decisions
                                      #   -> Spec optimized for human + AI
                                      #   -> May call /rai-research for UX-facing stories
                                      #   -> Writes: work/stories/S-NAME/design.md

/rai-story-plan                       # Decomposes into atomic tasks:
                                      #   -> Dependencies between tasks
                                      #   -> Verification criteria per task
                                      #   -> Writes: work/stories/S-NAME/plan.md

/rai-story-implement                  # Executes task by task:
                                      #   -> TDD cycles (red -> green -> refactor)
                                      #   -> Validation gates per task
                                      #   -> Atomic commits per completed task

/rai-story-review                     # Post-implementation retrospective:
                                      #   -> Patterns discovered -> patterns.jsonl
                                      #   -> Calibration (estimated vs actual) -> calibration.jsonl
                                      #   -> Writes: work/stories/S-NAME/retro.md

/rai-story-close                      # Closes the story:
                                      #   -> Final verification (tests, lint, types)
                                      #   -> Runs /rai-docs-update (code<->docs coherence)
                                      #   -> git merge --no-ff to dev
                                      #   -> git branch -D story/sN.M/name
                                      #   -> Updates epic scope
```

### Story Artifacts

```
work/stories/S-NAME/
├── scope.md          <- /rai-story-start
├── design.md         <- /rai-story-design
├── plan.md           <- /rai-story-plan
└── retro.md          <- /rai-story-review
```

---

## Phase 4: Support Skills (as needed)

| Skill | When | What it does |
|-------|------|-------------|
| `/rai-research` | Before ADRs, technology decisions, UX-facing stories | Epistemologically rigorous research with evidence catalog |
| `/rai-debug` | When a defect is detected (Jidoka: stop and fix) | Root cause analysis: 5 Whys, Ishikawa, Gemba |
| `/rai-docs-update` | Called automatically by `/rai-story-close` | Syncs code with governance/architecture/modules/ docs |
| `/rai-framework-sync` | After creating/updating ADRs | Syncs backlog, glossary, ontology, vision |
| `/rai-skill-create` | When adding new workflow automation | Scaffolds, validates, and integrates new skills |

---

## System Maintenance

```bash
# Rebuild knowledge graph (after governance/architecture changes)
rai memory build

# Validate graph integrity
rai memory validate

# Visualize what Rai knows
rai memory viz                        # Generates interactive HTML

# Query memory
rai memory query "velocity patterns"
rai memory context mod-session        # Full context for a module

# View developer profile
rai profile show

# Detect architectural drift
rai discover drift
```

---

## Branch Model

```
main (stable releases)
  └── dev (development)
        ├── story/s18.1/name
        ├── story/s18.2/name
        ├── story/s18.3/name
        └── story/sBF-1/bugfix
```

Stories always branch from and merge to dev. Epics are logical containers (directory + Jira tracker), not branches.

---

## File Map

### Global (per machine, travels with you)

```
~/.rai/
└── developer.yaml                    # Name, coaching, preferences, trust level
```

### Per Project

```
.raise/
├── manifest.yaml                     # Project identity
├── rai/
│   ├── memory/
│   │   ├── patterns.jsonl            # Shared patterns (committed)
│   │   ├── MEMORY.md                 # Pattern documentation (committed)
│   │   └── index.json                # Derived graph (gitignored, rebuild with rai memory build)
│   └── personal/                     # Per-developer (gitignored, created on first session close)
│       ├── sessions/index.jsonl      # Session history
│       ├── session-state.yaml        # Work state between sessions
│       ├── calibration.jsonl         # Estimation calibration
│       ├── telemetry/signals.jsonl   # Lean flow metrics
│       └── last-diff.json            # Last graph rebuild diff
├── katas/                            # Process definitions
├── gates/                            # Validation criteria
├── templates/                        # Artifact scaffolds
└── skills/                           # Legacy (now in .claude/skills/)

.claude/skills/                       # 24 active skills
governance/                           # Project governance (feeds the graph)
  └── architecture/modules/           # One doc per module
framework/                            # Public textbook (constitution, glossary, concepts)
work/stories/                         # Work artifacts (scope, design, plan, retro)
dev/                                  # Maintenance (parking-lot, decisions)
# CLAUDE.local.md removed — session context derived from git (ADR-038)
```

---

## CLI Commands Reference

| Command | Writes to | Reads from |
|---------|-----------|-----------|
| `rai init` | `.raise/` structure | — |
| `rai session start` | `~/.rai/developer.yaml` | profile + graph + session-state |
| `rai session close` | `personal/sessions/`, `personal/session-state.yaml` | active session |
| `rai memory build` | `memory/index.json` | JSONL + governance/ + architecture/ + work/ |
| `rai memory add-pattern` | `memory/patterns.jsonl` | — |
| `rai memory emit-work` | `personal/telemetry/signals.jsonl` | — |
| `rai memory emit-calibration` | `personal/telemetry/signals.jsonl` | — |
| `rai memory query` | — (read-only) | `memory/index.json` |
| `rai memory context` | — (read-only) | `memory/index.json` |
| `rai memory validate` | — (read-only) | `memory/index.json` |
| `rai memory viz` | HTML file | `memory/index.json` |
| `rai discover scan` | stdout (JSON) | source code (AST) |
| `rai discover drift` | stdout | components + architecture docs |
| `rai profile show` | — (read-only) | `~/.rai/developer.yaml` |
| `rai skill list` | — (read-only) | `.claude/skills/` |
| `rai skill validate` | — (read-only) | skill SKILL.md |

---

## What the Skills Handle vs What You Decide

### Skills handle (90%):

- Proposing what to work on (`/rai-session-start`)
- Calling `/rai-docs-update` during story close
- Asking for patterns and calibration during review
- Running `rai memory build` after discovery
- Emitting telemetry at lifecycle transitions

### You decide (10%):

- **When to close a session** — judgment call based on context usage
- **When to run `rai memory build`** — if you edit governance/ docs manually
- **When to use `/rai-research`** — story-design suggests it for UX-facing but doesn't force it
- **When to stop and debug** — Jidoka: you notice the defect, you call `/rai-debug`

---

## Visual Flow

```
[SETUP — once per project]
rai init -> /rai-welcome -> /rai-project-create|onboard -> /rai-discover-*

[EVERY WORK BLOCK]
/rai-session-start
|
|-- /rai-epic-start -> design -> plan
|   |
|   |-- /rai-story-start -> design -> plan -> implement -> review -> close
|   |-- /rai-story-start -> design -> plan -> implement -> review -> close
|   |-- /rai-story-start -> design -> plan -> implement -> review -> close
|   |
|   +-- /rai-epic-close
|
|-- /rai-research (when needed)
|-- /rai-debug (when defect detected)
|
/rai-session-close
```

---

*Generated: 2026-02-12*
*Source: raise-commons onboarding session with Fer*
