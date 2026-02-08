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
    description: "Scan codebases to extract structural knowledge from source code"
  - name: knowledge
    modules: [context, memory]
    description: "Persist, integrate, and query accumulated knowledge"
  - name: experience
    modules: [onboarding, output]
    description: "First-run setup, developer profiles, and presentation"
  - name: observability
    modules: [telemetry]
    description: "Local signal collection for process improvement"
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

raise-cli has five bounded contexts, a shared kernel, and an application layer. Each context has its own vocabulary, its own aggregate roots, and evolves independently.

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
│  │  GOVERNANCE   │  │  DISCOVERY   │  │  KNOWLEDGE                   │  │
│  │              │  │              │  │  ┌─────────┐ ┌────────────┐  │  │
│  │  governance/  │  │  discovery/  │  │  │ context │ │  memory    │  │  │
│  │              │  │              │  │  │ (graph  │ │  (JSONL    │  │  │
│  │  Markdown →  │  │  Python →   │  │  │  hub)   │ │  storage)  │  │  │
│  │  concepts    │  │  components  │  │  └─────────┘ └────────────┘  │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────────┘  │
│                                                                          │
│  ┌──────────────────────────┐  ┌───────────────────────────────────┐   │
│  │  EXPERIENCE              │  │  OBSERVABILITY                     │   │
│  │  ┌───────────┐ ┌───────┐│  │                                    │   │
│  │  │onboarding │ │output ││  │  telemetry/                        │   │
│  │  │(init,     │ │(format││  │  Append-only JSONL signals         │   │
│  │  │ profile)  │ │ ters) ││  │                                    │   │
│  │  └───────────┘ └───────┘│  └───────────────────────────────────┘   │
│  └──────────────────────────┘                                           │
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

**Does NOT own:** Storing concepts (that's Knowledge), displaying concepts (that's Experience/output).

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

**Does NOT own:** Persisting components in the graph (that's Knowledge), generating architecture docs (that's a skill, not CLI logic).

---

### 3. Knowledge Context

**What it owns:** Persisting, integrating, and querying all accumulated knowledge. This is the **integration hub** — it pulls from Governance, Discovery, and Memory to build a unified queryable graph.

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

### 4. Experience Context

**What it owns:** First-run developer experience and output formatting.

**Two modules, one context:**
- **onboarding** — Project initialization, developer profiles, convention detection, skill installation
- **output** — Format-agnostic presentation (human, JSON, table)

**Aggregate roots:**
- `bootstrap() → ProjectManifest` — creates .raise/ structure
- `detect_project_type() → DetectionResult` — language/framework detection
- `OutputConsole` singleton — all CLI output goes through this

**Domain vocabulary:**

| Term | Meaning in this context |
|------|------------------------|
| DeveloperProfile | Persistent developer state (ShuHaRi level, preferences, sessions) |
| Convention | Detected coding pattern (naming, structure, testing) with confidence |
| Bootstrap | Creating the .raise/ directory structure from templates |
| OutputFormat | Presentation mode: human (rich), JSON (machine), table (tabular) |

**Invariants:**
- Must work on fresh repos with zero RaiSE artifacts
- Profile is global (`~/.rai/developer.yaml`), not per-project
- All CLI output through `OutputConsole` — never raw `print()`
- Formatters are pure functions (model → string)
- Convention detection is heuristic with explicit confidence levels

**Does NOT own:** Domain logic for any other context — onboarding orchestrates domain modules but doesn't contain domain logic.

---

### 5. Observability Context

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
  (extracts components)            │  produces components
                                   │
                                   ▼
                            ┌─────────────┐
                            │  KNOWLEDGE  │  ← Integration Hub
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
| Governance → Knowledge | **Supplier-Consumer** | Context calls `GovernanceExtractor`, transforms `Concept` into `ConceptNode` |
| Discovery → Knowledge | **File-based integration** | Discovery writes `components-validated.json`, Context reads it |
| Memory → Knowledge | **Shared data** | Memory writes JSONL, Context reads JSONL — same files, different access patterns |
| CLI → all contexts | **Application Layer** | Thin wrappers call domain functions directly |
| CLI → Experience | **Delegation** | Commands call `OutputConsole` for all display |
| CLI → Observability | **Fire-and-forget** | Commands emit signals after completing |
| Onboarding → Distribution | **Copy-on-init** | Reads `rai_base` and `skills_base` via `importlib.resources`, copies to project |

### Anti-Corruption Layer: Context Module

The `context` module acts as the **anti-corruption layer** between domains. Each domain has its own vocabulary (Governance speaks "Concept", Discovery speaks "Symbol/Component", Memory speaks "Pattern/Calibration"), but the graph normalizes everything into `ConceptNode` with a `NodeType` discriminator.

```
Governance.Concept ──→ context.load_governance() ──→ ConceptNode(type="requirement")
Discovery.Component ──→ context.load_components() ──→ ConceptNode(type="component")
Memory.Pattern     ──→ context.load_memory()     ──→ ConceptNode(type="pattern")
Architecture.Module──→ context.load_architecture()──→ ConceptNode(type="module")
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
| A new node type for the graph | `context/models.py` (NodeType) + new loader in `builder.py` | Knowledge owns the graph schema |
| A new memory storage format | `memory/` | Memory owns JSONL persistence |
| A new CLI command | `cli/commands/` + the relevant domain module | CLI is thin — logic stays in domain |
| A new output format | `output/` | Experience owns presentation |
| A new signal type | `telemetry/` | Observability owns signal definitions |
| A new onboarding step | `onboarding/` | Experience owns first-run flow |
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

## Open Questions for Human Validation

These are areas where the domain model may need refinement based on intent that can't be inferred from code:

1. **Should `skills` be its own bounded context?** Currently it's part of no context — it parses SKILL.md files but doesn't execute them. Is skill management a domain or just infrastructure?

2. **Is the Knowledge context too broad?** `context` (graph) and `memory` (JSONL) serve different purposes but are tightly coupled. Should they be two contexts with a published language between them?

3. **Where does architecture documentation generation belong?** Currently it's a skill (AI-driven), not CLI logic. Is that the right boundary, or should `raise discover describe` be a CLI command?

4. **Should onboarding own convention detection?** Convention detection (naming patterns, testing structure) feels closer to Discovery than Experience. Should it move?

5. **What's the governance boundary for external integrations?** When Jira/Confluence integration comes (V3), does it get its own bounded context or extend Governance?
