---
type: architecture_domain_model
project: raise-cli
status: current
bounded_contexts:
  - name: governance
    modules: [governance]
    description: "Extract structured knowledge from markdown governance documents"
  - name: discovery
    modules: [discovery]
    description: "Scan codebases to extract structural knowledge from source code, including convention detection"
  - name: ontology
    modules: [context, memory]
    description: "Persist, integrate, and query accumulated knowledge — the ontological backbone of RaiSE"
  - name: skills
    modules: [skills]
    description: "Skill parsing, location, validation, and scaffolding — process knowledge infrastructure"
  - name: experience
    modules: [onboarding, output]
    description: "First-run setup, developer profiles, and presentation"
  - name: observability
    modules: [telemetry]
    description: "Local signal collection for process improvement"
  - name: integrations
    modules: []
    description: "External platform adapters (Jira, Confluence, Rovo) — V3 scope, not yet implemented"
    status: planned
shared_kernel:
  modules: [config, core, schemas]
  description: "Foundation utilities shared across all contexts"
application_layer:
  modules: [cli]
  description: "Thin orchestration shell — depends on everything, nothing depends on it"
distribution:
  modules: [rai_base, skills_base]
  description: "Packaged content for pip distribution — no runtime logic"
---

# Domain Model

> DDD-informed domain boundaries, communication patterns, and design decision guidance.

This document captures the **intentional domain structure** of raise-cli. It answers: where does new functionality belong, how do domains communicate, and what constitutes a domain boundary violation.

## Bounded Contexts

raise-cli has seven bounded contexts (one planned), a shared kernel, and an application layer. Each context has its own vocabulary, its own aggregate roots, and evolves independently.

```
┌─────────────────────────────────────────────────────────────────────────┐
│  APPLICATION LAYER                                                       │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  cli — Thin command wrappers, routes to domain logic              │  │
│  └───────────────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────────────┤
│  BOUNDED CONTEXTS                                                        │
│                                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────────┐  │
│  │  GOVERNANCE   │  │  DISCOVERY   │  │  ONTOLOGY                    │  │
│  │              │  │              │  │  ┌─────────┐ ┌────────────┐  │  │
│  │  governance/  │  │  discovery/  │  │  │ context │ │  memory    │  │  │
│  │              │  │  (+ future   │  │  │ (graph  │ │  (JSONL    │  │  │
│  │  Markdown →  │  │  convention  │  │  │  hub)   │ │  storage)  │  │  │
│  │  concepts    │  │  detection)  │  │  └─────────┘ └────────────┘  │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────────┘  │
│                                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │  SKILLS      │  │  EXPERIENCE  │  │ OBSERVABILITY│                  │
│  │              │  │  ┌─────────┐ │  │              │                  │
│  │  skills/     │  │  │onboard- │ │  │  telemetry/  │                  │
│  │  (parse,     │  │  │ing      │ │  │  JSONL       │                  │
│  │   locate,    │  │  ├─────────┤ │  │  signals     │                  │
│  │   validate)  │  │  │ output  │ │  │              │                  │
│  └──────────────┘  │  └─────────┘ │  └──────────────┘                  │
│                     └──────────────┘                                     │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  INTEGRATIONS (V3 — planned)                                     │   │
│  │  Jira, Confluence, Rovo adapters — own vocabulary, own auth      │   │
│  └──────────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────────┤
│  SHARED KERNEL                                                           │
│  ┌────────┐ ┌────────┐ ┌─────────┐                                     │
│  │  core  │ │ config │ │ schemas │                                     │
│  └────────┘ └────────┘ └─────────┘                                     │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1. Governance Context

**What it owns:** Extracting structured knowledge from human-authored markdown governance documents (constitution, PRD, vision, guardrails, ADRs, glossary, backlog, epics/stories).

**Aggregate root:** `GovernanceExtractor`
- Entry point: `extract_all(project_root) → list[Concept]`
- Each governance file format has a dedicated parser
- Output: `Concept` objects with id, type, content, source reference

**Domain vocabulary:**

| Term | Meaning in this context |
|------|------------------------|
| Concept | A discrete unit of governance knowledge (principle, requirement, guardrail, term) |
| Extraction | Deterministic pattern-matching to find concepts in markdown |
| Section | A markdown heading that bounds a concept |
| Source reference | File path + line range for traceability |

**Invariants:**
- Extraction is deterministic — same input always produces same output
- One parser per governance file format
- Concepts carry source references (file, section, line range)
- No AI inference — pure pattern matching

**Does NOT own:** Storing concepts (that's Ontology), displaying concepts (that's Experience/output).

---

### 2. Discovery Context

**What it owns:** Extracting structural knowledge from source code — symbols, components, modules, and detecting drift from documented architecture.

**Aggregate roots:**
- `scan_directory() → ScanResult` — raw symbol extraction via Python AST
- `Analyzer.analyze() → AnalysisResult` — component grouping with confidence tiers
- `detect_drift() → list[DriftWarning]` — comparing current code against documented architecture

**Domain vocabulary:**

| Term | Meaning in this context |
|------|------------------------|
| Symbol | A named code element (class, function, constant) extracted from AST |
| Component | A validated, human-approved symbol with description and purpose |
| Module | A top-level package directory under `src/` |
| Drift | Divergence between documented architecture and actual code structure |
| Confidence tier | High/medium/low certainty of auto-generated descriptions |

**Invariants:**
- All analysis is deterministic — no AI inference in CLI
- Scanner uses Python AST (stdlib), not external parsers
- Components require human validation before entering the graph
- Independent of Governance context — no cross-imports

**Does NOT own:** Persisting components in the graph (that's Ontology), generating architecture docs (that's a skill, not CLI logic).

**Future:** Convention detection (currently in onboarding) belongs here — it's codebase analysis. Move when refactoring.

---

### 3. Ontology Context

**What it owns:** Persisting, integrating, and querying all accumulated knowledge. This is the **ontological backbone** of RaiSE — it pulls from Governance, Discovery, Skills, and Memory to build a unified queryable graph. RaiSE is fundamentally ontology-guided software development; this context is where that manifests.

**Two modules, one context:**
- **context** — Graph construction and querying (the "read" + "merge" side)
- **memory** — JSONL storage for patterns, calibration, sessions (the "write" side)

**Aggregate roots:**
- `UnifiedGraphBuilder.build() → UnifiedGraph` — orchestrates all loaders
- `UnifiedQueryEngine.query() → QueryResult` — BFS keyword search
- `append_pattern() / append_calibration() / append_session()` — write to JSONL

**Domain vocabulary:**

| Term | Meaning in this context |
|------|------------------------|
| ConceptNode | Universal node in the unified graph — any type of knowledge |
| ConceptEdge | Directed relationship between concepts |
| NodeType | Closed set of concept types (pattern, module, component, etc.) |
| EdgeType | Closed set of relationship types (depends_on, learned_from, etc.) |
| Three-tier memory | Global (~/.rai) > Project (.raise/) > Personal (.raise/rai/personal/) |
| Memory scope | Which tier a piece of knowledge belongs to |

**Invariants:**
- Graph is rebuilt from scratch on every `raise memory build` — no incremental updates
- NodeType is a Literal type — adding new types is a **schema change** (PAT-152)
- JSONL is append-only — never edit historical entries
- Backward compatibility: readers handle both old and new JSONL schemas (PAT-153)
- Queries use BFS traversal, not full-text search

**Does NOT own:** Extracting governance concepts (that's Governance), scanning code (that's Discovery), displaying results (that's Experience).

---

### 4. Skills Context

**What it owns:** Skill file infrastructure — parsing SKILL.md files, locating skills on disk, validating frontmatter, and scaffolding new skills. Has its own vocabulary and will grow (marketplace, versioning, composition).

**Aggregate roots:**
- `list_skills() → list[Skill]` — find all skills on disk
- `parse_skill() → Skill` — parse SKILL.md frontmatter and body
- `SkillLocator` — resolve skill names to file paths

**Domain vocabulary:**

| Term | Meaning in this context |
|------|------------------------|
| Skill | A process guide (SKILL.md) that Rai reads and executes |
| Frontmatter | YAML metadata: name, description, inputs, outputs, hooks |
| Skill location | Resolution order: project `.claude/skills/` → base package |
| Scaffolding | Creating a new SKILL.md from template via `/skill-create` |

**Invariants:**
- Skills are markdown, not executable code
- YAML frontmatter required for graph integration
- Ontology naming convention (verb-noun, kebab-case)
- Skills are parsed deterministically — no AI inference in parsing

**Does NOT own:** Executing skills (that's Rai, the AI partner), storing skill nodes in graph (that's Ontology).

---

### 5. Experience Context

**What it owns:** First-run developer experience and output formatting.

**Two modules, one context:**
- **onboarding** — Project initialization, developer profiles, skill installation
- **output** — Format-agnostic presentation (human, JSON, table)

**Note:** Convention detection currently lives in onboarding but belongs in Discovery. It will move in a future refactoring.

**Aggregate roots:**
- `bootstrap() → ProjectManifest` — creates .raise/ structure
- `detect_project_type() → DetectionResult` — language/framework detection
- `OutputConsole` singleton — all CLI output goes through this

**Domain vocabulary:**

| Term | Meaning in this context |
|------|------------------------|
| DeveloperProfile | Persistent developer state (ShuHaRi level, preferences, sessions) |
| Bootstrap | Creating the .raise/ directory structure from templates |
| OutputFormat | Presentation mode: human (rich), JSON (machine), table (tabular) |

**Invariants:**
- Must work on fresh repos with zero RaiSE artifacts
- Profile is global (`~/.rai/developer.yaml`), not per-project
- All CLI output through `OutputConsole` — never raw `print()`
- Formatters are pure functions (model → string)

**Does NOT own:** Domain logic for any other context — onboarding orchestrates domain modules but doesn't contain domain logic. Convention detection belongs in Discovery (pending move).

---

### 6. Observability Context

**What it owns:** Local signal collection for process improvement and observable workflow.

**Aggregate root:** `emit()` — fire-and-forget JSONL append

**Domain vocabulary:**

| Term | Meaning in this context |
|------|------------------------|
| Signal | A structured event recording process activity |
| Signal type | Discriminated union: command_usage, skill_event, work_lifecycle, session_event, calibration_event, error_event |
| Emission | Appending a signal to the local JSONL file |

**Invariants:**
- Append-only JSONL — never reads its own output
- Emission never raises exceptions — fire-and-forget
- No network transmission — local only, privacy-first
- Follows OpenTelemetry semantic conventions for future export

**Does NOT own:** Analyzing signals (future — deferred to post-F&F), displaying signals (that's Experience).

---

### Shared Kernel

**Modules:** `core`, `config`, `schemas`

These provide foundation utilities used by 3+ contexts. They have **zero internal dependencies** and are the stable base of the system.

| Module | What it provides | Used by |
|--------|-----------------|---------|
| `core` | Subprocess wrappers for git, ripgrep, ast-grep | governance, context, onboarding |
| `config` | Settings cascade, XDG directory resolution, three-tier paths | memory, telemetry, onboarding, context, cli |
| `schemas` | Shared Pydantic models (minimal — most types stay in owning module) | Reserved for cross-context types |

**Key rule:** Types belong in the module that owns them. `schemas` is only for types needed by 3+ modules. Don't move types to `schemas` prematurely.

---

## Context Map

How bounded contexts communicate with each other.

```
  GOVERNANCE ──────────────────────┐
  (extracts concepts)              │
                                   │ produces concepts
  DISCOVERY ──────────────────────┤
  (extracts components)            │ produces components
                                   │
  SKILLS ─────────────────────────┤
  (parses skill metadata)          │ produces skill nodes
                                   │
                                   ▼
                            ┌─────────────┐
                            │  ONTOLOGY   │  ← Integration Hub
                            │  (context   │     (Anti-Corruption Layer)
                            │   + memory) │
                            └──────┬──────┘
                                   │
                            queries │ results
                                   │
                                   ▼
                            ┌──────────────┐
                            │     CLI      │  ← Application Layer
                            │  (routing)   │
                            └──────────────┘
                              │          │
                     formats  │          │ records
                              ▼          ▼
                         EXPERIENCE   OBSERVABILITY
                         (output)     (telemetry)
```

### Communication Patterns

| From → To | Pattern | Mechanism |
|-----------|---------|-----------|
| Governance → Ontology | **Supplier-Consumer** | Context calls `GovernanceExtractor`, transforms `Concept` into `ConceptNode` |
| Discovery → Ontology | **File-based integration** | Discovery writes `components-validated.json`, Context reads it |
| Skills → Ontology | **Supplier-Consumer** | Context calls skill extractor, transforms `Skill` into `ConceptNode` |
| Memory → Ontology | **Shared data** | Memory writes JSONL, Context reads JSONL — same files, different access patterns |
| CLI → all contexts | **Application Layer** | Thin wrappers call domain functions directly |
| CLI → Experience | **Delegation** | Commands call `OutputConsole` for all display |
| CLI → Observability | **Fire-and-forget** | Commands emit signals after completing |
| Onboarding → Distribution | **Copy-on-init** | Reads `rai_base` and `skills_base` via `importlib.resources`, copies to project |

### Anti-Corruption Layer: Context Module

The `context` module acts as the **anti-corruption layer** between domains. Each domain has its own vocabulary (Governance speaks "Concept", Discovery speaks "Symbol/Component", Skills speaks "Skill/Frontmatter", Memory speaks "Pattern/Calibration"), but the graph normalizes everything into `ConceptNode` with a `NodeType` discriminator.

```
Governance.Concept  ──→ context.load_governance()  ──→ ConceptNode(type="requirement")
Discovery.Component ──→ context.load_components()  ──→ ConceptNode(type="component")
Skills.Skill        ──→ context.load_skills()      ──→ ConceptNode(type="skill")
Memory.Pattern      ──→ context.load_memory()      ──→ ConceptNode(type="pattern")
Architecture.Module ──→ context.load_architecture()──→ ConceptNode(type="module")
```

This translation happens in the `UnifiedGraphBuilder` loaders. Each loader knows the source domain's vocabulary and translates it to the graph's universal vocabulary.

---

## Design Decision Guidance

When adding new functionality, use this table to determine where it belongs.

### Where Does New Code Go?

| If you're adding... | It belongs in... | Because... |
|---------------------|-----------------|------------|
| A new governance file parser | `governance/` | Governance owns all markdown extraction |
| A new code analysis capability | `discovery/` | Discovery owns all source code analysis |
| A new node type for the graph | `context/models.py` (NodeType) + new loader in `builder.py` | Ontology owns the graph schema |
| A new memory storage format | `memory/` | Ontology/Memory owns JSONL persistence |
| A new CLI command | `cli/commands/` + the relevant domain module | CLI is thin — logic stays in domain |
| A new output format | `output/` | Experience owns presentation |
| A new signal type | `telemetry/` | Observability owns signal definitions |
| A new onboarding step | `onboarding/` | Experience owns first-run flow |
| A new skill capability | `skills/` | Skills context owns skill infrastructure |
| A new convention detector | `discovery/` | Discovery owns all codebase analysis |
| A new external platform adapter | `integrations/` (V3) | Integrations context owns external platform vocabulary |
| A new shared type (3+ modules need it) | `schemas/` | Shared kernel for cross-context types |
| A new external tool wrapper | `core/` | Shared kernel owns subprocess integration |

### When To Create a New Module

Create a new module when:
1. The concept has its **own vocabulary** that doesn't fit existing contexts
2. It would evolve at a **different rate** than existing modules
3. It needs to be **independently testable** without importing other domain logic
4. Three or more other modules would depend on it (→ shared kernel candidate)

Do NOT create a new module when:
- It's just a new file in an existing domain (add to existing module)
- It only serves one other module (keep it internal to that module)
- The vocabulary overlaps significantly with an existing context

### When To Add a New NodeType

Adding a NodeType is a **schema change** (PAT-152). Consider this carefully:
1. Does it represent a genuinely new category of knowledge? (not just a sub-type)
2. Will it have its own `depends_on` or other relationship edges?
3. Is there a loader that can produce these nodes deterministically?
4. Will queries benefit from filtering by this type?

If yes to all four → add the type. If any are no → consider using metadata on existing types.

### When To Add a New EdgeType

Same bar as NodeType. Current edges and their semantics:

| EdgeType | Meaning | Between |
|----------|---------|---------|
| `depends_on` | Module A imports from module B | module ↔ module |
| `learned_from` | Pattern was learned in session X | pattern → session |
| `applies_to` | Calibration applies to scope X | calibration → scope |
| `governed_by` | Implementation governed by requirement | story → requirement |
| `implements` | Feature implements requirement | story → requirement |
| `part_of` | Component belongs to module | component → module |
| `related_to` | Semantic similarity (keyword-based, weight < 1.0) | any ↔ any |
| `needs_context` | Skill requires knowledge about X | skill → topic |

---

## Domain Boundaries to Protect

These boundaries are **intentional**. Crossing them is domain drift.

| Boundary | What it prevents |
|----------|-----------------|
| Governance and Discovery don't import each other | Keeps extraction concerns independent — can evolve parsers without affecting scanners |
| CLI contains no domain logic | Prevents tight coupling — domain logic must be reusable without CLI |
| Memory writes are append-only | Prevents data corruption — no in-place edits of historical knowledge |
| Context is the only module that merges across domains | Prevents knowledge sprawl — one place to understand the full graph |
| All output through OutputConsole | Prevents presentation leaking into domain logic |
| Telemetry emission never raises | Prevents observability from affecting correctness |
| Shared kernel has zero internal deps | Prevents foundation instability |

---

## Resolved Domain Decisions

These questions were raised during domain model creation and resolved through human validation (2026-02-08):

| # | Question | Decision | Rationale |
|---|----------|----------|-----------|
| 1 | Should `skills` be its own bounded context? | **Yes — own context** | Has its own vocabulary (frontmatter, hooks, scaffolding), will grow (marketplace, versioning, composition). Not just infrastructure. |
| 2 | Is the Knowledge context too broad? | **Rename to Ontology, keep unified** | RaiSE is ontology-guided software development. The graph IS the ontological backbone. context + memory serve the same purpose. Splitting adds complexity without benefit at this scale. |
| 3 | Where does architecture doc generation belong? | **Skill only** | Architecture docs require AI synthesis (prose, rationale, domain model). Skills are the right vehicle. No CLI command — the skill calls CLI tools as needed. |
| 4 | Should onboarding own convention detection? | **Move to Discovery** | Convention detection IS codebase analysis — same domain as scanning and analyzing. Cleaner domain boundaries. Pending refactoring. |
| 5 | What's the governance boundary for external integrations? | **New Integrations bounded context (V3)** | External platforms (Jira, Confluence, Rovo) have their own vocabularies, auth models, and evolution rates. Dedicated context with adapters per platform keeps domains clean. |
