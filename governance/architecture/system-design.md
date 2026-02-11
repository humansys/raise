---
type: architecture_design
project: rai-cli
status: current
layers:
  - name: leaf
    modules: [core, config, schemas]
    description: "Zero internal dependencies — foundation utilities"
  - name: domain
    modules: [governance, discovery, skills, telemetry]
    description: "Independent domain logic — no cross-domain imports"
  - name: integration
    modules: [context, memory, onboarding, output]
    description: "Combines domains into unified capabilities"
  - name: orchestration
    modules: [cli]
    description: "User-facing entry points — depends on everything, nothing depends on it"
distribution:
  - name: rai_base
    description: "Base identity and patterns for pip distribution"
  - name: skills_base
    description: "18 distributable SKILL.md files"
architectural_decisions:
  - "ADR-012: Skills + Toolkit (no monolithic engines)"
  - "ADR-019: Unified graph with NetworkX"
  - "ADR-020: Extended node types (module, component, depends_on)"
  - "ADR-022: Distribution architecture (rai_base + skills_base)"
guardrails_reference: "governance/guardrails.md"
constitution_reference: "framework/reference/constitution.md"
---

# System Design

> C4 Level 2 — How rai-cli is structured internally, its constraints, and what constitutes drift.

## Layered Hub-and-Spoke Architecture

rai-cli follows a **strictly layered, acyclic** dependency structure. Every module lives in exactly one layer, and dependencies only flow downward.

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 4: ORCHESTRATION                                      │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  cli — Typer commands, entry points                    │  │
│  │  Depends on: everything. Nothing depends on cli.       │  │
│  └───────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  Layer 3: INTEGRATION                                        │
│  ┌──────────┐ ┌──────────┐ ┌────────────┐ ┌──────────┐    │
│  │ context  │ │ memory   │ │ onboarding │ │ output   │    │
│  │ (graph   │ │ (JSONL   │ │ (init,     │ │ (format  │    │
│  │  hub)    │ │  mgmt)   │ │  profile)  │ │  output) │    │
│  └──────────┘ └──────────┘ └────────────┘ └──────────┘    │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: DOMAIN                                             │
│  ┌────────────┐ ┌───────────┐ ┌────────┐ ┌───────────┐    │
│  │ governance │ │ discovery │ │ skills │ │ telemetry │    │
│  │ (extract   │ │ (scan,    │ │ (parse,│ │ (local    │    │
│  │  concepts) │ │  analyze) │ │  find) │ │  signals) │    │
│  └────────────┘ └───────────┘ └────────┘ └───────────┘    │
├─────────────────────────────────────────────────────────────┤
│  Layer 1: LEAF                                               │
│  ┌────────┐ ┌────────┐ ┌─────────┐                         │
│  │  core  │ │ config │ │ schemas │                         │
│  │ (git,  │ │ (XDG,  │ │ (shared │                         │
│  │  rg)   │ │  env)  │ │  types) │                         │
│  └────────┘ └────────┘ └─────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

**Maximum dependency depth:** 4 levels (cli → context → governance → core).

## Data Flows

### Flow 1: Knowledge Graph Construction

The core value pipeline — building the unified graph from all knowledge sources.

```
                    ┌──────────────────────────────────────┐
Governance .md ──→  │ GovernanceExtractor                  │──→ concept nodes
                    │ (Markdown → sections → terms/reqs)   │
                    └──────────────────────────────────────┘
                                                                    │
JSONL memory ────→  MemoryLoader ──→ pattern/calibration nodes      │
                                                                    ├──→ UnifiedGraph
Epic/story .md ──→  WorkParser ──→ work tracking nodes              │     (NetworkX)
                                                                    │        │
components.json ──→ ComponentLoader ──→ component nodes             │        │
                                                                    │        ▼
architecture/ ───→  ArchitectureLoader ──→ module nodes ────────────┘   raise memory
                    (YAML frontmatter → depends_on edges)                  query
```

**Graph stats (current):** ~900+ concepts, ~5500+ relationships, 24 dependency edges, 345 components across 94 Python files.

### Flow 2: Codebase Discovery

Extracting structural knowledge from source code.

```
Source tree ──→ Scanner (Python AST) ──→ symbols (class, function, constant)
                                              │
                                              ▼
                                         Analyzer ──→ module grouping, purpose inference
                                              │
                                              ▼
                                     components-validated.json ──→ graph (via complete)
                                              │
                                              ▼
                                     UnifiedGraphBuilder.load_code_structure()
                                          (context/analyzers/PythonAnalyzer)
                                              │
                                              ▼
                                     Enriched module nodes with imports, exports, counts
```

**Pipeline:** `rai discover start` → `scan` → `analyze` → `validate` (human) → `complete` → `describe`

**Code-aware graph:** Since S16.1, `load_code_structure()` enriches module nodes with AST-extracted data: imports, exports, component counts. The `context/analyzers/` subpackage provides `PythonAnalyzer` (concrete implementation) and `CodeAnalyzer` Protocol for extensibility.

### Flow 3: Session Lifecycle

How Rai maintains continuity across sessions.

```
/session-start ──→ raise profile show ──→ developer context
                   rai memory query  ──→ relevant patterns
                   CLAUDE.local.md     ──→ human notes, deadlines
                        │
                        ▼
                   Session work (skills, tools, commits)
                        │
                        ▼
/session-close ──→ rai session close ──→ pattern extraction
                   memory update        ──→ JSONL append
                   CLAUDE.local.md      ──→ updated notes
```

## Architectural Constraints

These are **intentional design decisions**. Violating them is architectural drift.

### Structural Constraints

| Constraint | Rationale | Verification |
|-----------|-----------|--------------|
| No circular imports | Layered architecture requires acyclic graph | `pyright` import analysis |
| `cli` depends on everything, nothing depends on `cli` | Clean separation: UI is a shell over logic | Import grep |
| `governance` and `discovery` are independent | Domain isolation — different concerns, different evolution rates | No cross-imports |
| `core`, `config`, `schemas` have zero internal deps | Leaf modules are the stable foundation | Import analysis |
| All CLI output through `output` formatters | Consistent UX, testability | Code review |

### Design Constraints (from ADRs)

| Constraint | Source | Implication |
|-----------|--------|-------------|
| No AI inference in CLI | ADR-012 | All CLI operations are deterministic; Rai handles synthesis |
| Pydantic models for all data | MUST-ARCH-002 | No raw dicts, no TypedDict — Pydantic BaseModel everywhere |
| Skills are markdown, not code | ADR-012 | Process guides read by AI, not executed by engine |
| Graph rebuilt from scratch | ADR-019 | No incremental updates — simplicity over performance |
| NetworkX over external DB | ADR-019 | No Neo4j, no external dependencies — sufficient at our scale |

### Quality Constraints (Guardrails)

These guardrails from `governance/guardrails.md` are **architectural** — they shape how code is written and structured:

| Guardrail | Level | What It Means Architecturally |
|-----------|-------|------------------------------|
| MUST-CODE-001 | MUST | Complete type annotations — `pyright --strict` must pass |
| MUST-CODE-002 | MUST | Ruff linting and formatting — consistent code style |
| MUST-TEST-001 | MUST | >90% test coverage — tests mirror `src/` structure in `tests/` |
| MUST-SEC-001 | MUST | No secrets in code — `detect-secrets` + `bandit` pass |
| MUST-ARCH-002 | MUST | Pydantic models for all schemas — validated, documented data |
| SHOULD-CLI-001 | SHOULD | Explicit `--path` parameters — testability without mocking `cwd()` |
| SHOULD-CODE-002 | SHOULD | Clear names over acronyms — readability for humans and AI |

### Constitution Constraints

From `framework/reference/constitution.md`, these principles constrain all architectural decisions:

| Principle | Constraint on Architecture |
|-----------|---------------------------|
| §1 Humans Define, Machines Execute | CLI extracts and structures — never decides |
| §2 Governance as Code | All rules versioned in Git; no external config stores |
| §3 Platform Agnosticism | No GitHub/GitLab-specific APIs; Git-native only |
| §4 Validation Gates | Quality checked at each phase — `rai discover drift` enables this |
| §7 Lean / Jidoka | Stop on defects — CLI validates and reports, never silently skips |
| §8 Observable Workflow | Local JSONL telemetry; every skill emits signals |

## Key Patterns

Patterns that pervade the codebase — consistency here prevents drift.

### Pattern: Extract → Structure → Query

Every domain follows the same three-step pattern:

```
Raw source (Markdown, Python, JSONL)
    → Extractor/Loader (deterministic parsing)
        → Concept nodes in UnifiedGraph
            → BFS traversal via rai memory query
```

This is the fundamental data pattern. New knowledge sources follow this same path.

### Pattern: YAML Frontmatter as Schema

Machine-readable metadata lives in YAML frontmatter; human prose lives in Markdown body. This applies to:
- Architecture module docs (`governance/architecture/modules/*.md`)
- Skill definitions (`.claude/skills/*/SKILL.md`)
- Governance documents (section headers parsed as concept boundaries)

### Pattern: Three-Tier Memory

```
Global (~/.rai/)          → Cross-repo developer state (profile, preferences)
Project (.raise/rai/)     → Shared artifacts (patterns, calibration, graph)
Personal (.raise/rai/personal/) → Developer-specific (session log, notes)
```

Precedence: Personal > Project > Global. Stored in metadata, applied at query time.

### Pattern: Skills + Toolkit

```
Skill (markdown)         → Process guide Rai reads and follows
Toolkit (CLI commands)   → Deterministic operations Rai calls from within skills
```

Rai reads the skill, decides what to do, calls CLI tools for data, synthesizes results. The skill provides judgment; the tool provides determinism.

## What Constitutes Drift

**Architectural drift** is any change that violates the constraints above. Specifically:

| Drift Type | Example | Detection |
|-----------|---------|-----------|
| **Layer violation** | Domain module importing from integration module | Import analysis, pyright |
| **Circular dependency** | Module A imports B, B imports A | pyright, `rai discover drift` |
| **Missing types** | Function without type annotations | `pyright --strict` |
| **Raw dicts for data** | Using `dict` instead of Pydantic model | Code review, grep |
| **AI inference in CLI** | CLI command calling an LLM API | Code review |
| **Secrets in code** | Hardcoded API keys or credentials | `detect-secrets`, `bandit` |
| **Untested code** | New module without corresponding test file | Coverage report |
| **Undocumented module** | New `src/rai_cli/X/` without `governance/architecture/modules/X.md` | `rai discover drift` |
| **Guardrail violation** | Any MUST-level guardrail broken | Pre-commit hooks |

**Drift prevention:** Pre-commit hooks catch most violations automatically. `rai discover drift` catches structural changes. Architecture docs catch intent drift through human review.

## Directory Layout

```
src/rai_cli/
├── __init__.py            # Package root, version
├── exceptions.py          # Exception hierarchy with exit codes
├── cli/                   # Layer 4: Orchestration
│   ├── main.py            # Typer app entry point
│   └── commands/          # Command modules
├── config/                # Layer 1: Leaf
├── core/                  # Layer 1: Leaf (git, ripgrep, ast-grep wrappers)
├── schemas/               # Layer 1: Leaf (shared Pydantic models)
├── governance/            # Layer 2: Domain
├── discovery/             # Layer 2: Domain
├── skills/                # Layer 2: Domain
├── telemetry/             # Layer 2: Domain
├── context/               # Layer 3: Integration (graph builder, query engine)
│   └── analyzers/         #   Code analysis subpackage (PythonAnalyzer, Protocol)
├── memory/                # Layer 3: Integration (JSONL management)
├── onboarding/            # Layer 3: Integration (init, profile, bootstrap)
├── output/                # Layer 3: Integration (formatters)
├── rai_base/              # Distribution: base identity + patterns
└── skills_base/           # Distribution: 18 SKILL.md files
```

## Governance Traceability

| This Document | Derives From |
|---------------|-------------|
| Layer structure | ADR-012 (Skills + Toolkit), evolved through E1-E14 |
| Quality constraints | `governance/guardrails.md` (MUST-* guardrails) |
| Design principles | `framework/reference/constitution.md` (§1-§8) |
| Data flow patterns | ADR-019 (Unified Graph), ADR-020 (Extended Node Types) |
| Distribution model | ADR-022 (Distribution Architecture) |
