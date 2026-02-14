---
name: rai-discover-document
description: >
  Generate architecture documentation from discovery data. Produces
  system-level docs (C4 Context + Container), per-module docs with
  YAML frontmatter, and a compact index for AI context loading.

license: MIT

metadata:
  raise.work_cycle: discovery
  raise.frequency: per-project
  raise.fase: "5"
  raise.prerequisites: discover-validate
  raise.next: ""
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "1.0.0"
---

# Discover Document

## Purpose

Generate architecture documentation from discovery data. Produces a complete documentation set: high-level system docs (C4 Context + Container), per-module docs with YAML frontmatter, and a compact index for AI context loading.

## Mastery Levels (ShuHaRi)

**Shu**: Generate all levels, explain each section.
**Ha**: Generate with targeted updates for changed modules.
**Ri**: Incremental regeneration, preserve human sections.

## Context

**When to use:**
- After `rai discover scan` + `rai discover analyze` pipeline
- When architecture has changed significantly
- When onboarding new contributors

**When to skip:**
- Minor code changes that don't affect module structure
- Within same epic unless modules added/removed

**Inputs required:**
- `work/discovery/components-validated.json` — validated component catalog
- Source tree at `src/rai_cli/` — module structure and imports
- Module `__init__.py` docstrings — self-described purpose
- `governance/guardrails.md` — quality constraints (for system-design doc)
- `framework/reference/constitution.md` — design principles (for system-design doc)
- `governance/vision.md` — system identity (for system-context doc)

**Output:**
- `governance/architecture/system-context.md` — C4 Context level (what, who, why)
- `governance/architecture/system-design.md` — C4 Container level (how, constraints, drift)
- `governance/architecture/domain-model.md` — DDD bounded contexts, context map, decision guidance
- `governance/architecture/index.md` — compact index (<2K tokens)
- `governance/architecture/modules/*.md` — per-module docs with YAML frontmatter

## Steps

### Step 1: Load Discovery Data

Read `work/discovery/components-validated.json` and count components per module.

### Step 2: Analyze Module Structure

For each directory under `src/<package>/` with `__init__.py`:
1. Read `__init__.py` docstring for self-described purpose
2. Scan imports to build dependency map (`from <package>.X import`)
3. Count components from validated JSON
4. Identify entry points (CLI commands that import this module)
5. List key files and public API

### Step 3: Generate Module Docs

For each module, write `governance/architecture/modules/<name>.md` with:

**YAML frontmatter** (machine-parseable):
```yaml
---
type: module
name: <module_name>
purpose: "<one-line purpose>"
status: current
depends_on: [<list of module names>]
depended_by: [<list of module names>]
components: <count>
---
```

**Markdown body** (human-readable):
- **Purpose** — What this module does and why it exists (2-3 sentences)
- **Architecture** — How it works internally, key data flows
- **Key Files** — Important files with one-line descriptions
- **Dependencies** — Table of what it depends on and why
- **Conventions** — Module-specific patterns and rules

Write genuine explanatory prose. A new contributor should understand the module's role, constraints, and how to work with it.

### Step 4: Generate Compact Index

Write `governance/architecture/index.md` with:
- System overview (2-3 sentences)
- Module map table (name, purpose, depends_on, components)
- Data flow diagram (text-based)
- Key constraints

Target: under 2K tokens for session-loadable context.

### Step 5: Generate High-Level Architecture Docs

After module docs are complete, generate the C4 Context and Container docs. These ground both humans and AI on the system's identity, boundaries, and constraints.

#### 5a: System Context (`system-context.md`)

Read `governance/vision.md` and `framework/reference/constitution.md`. Write `governance/architecture/system-context.md` with:

**YAML frontmatter:**
```yaml
---
type: architecture_context
project: <project_name>
version: <current_version>
status: current
tech_stack: { ... }
external_dependencies: [...]
users: [...]
governed_by: [...]
---
```

**Markdown body:**
- **What Is <project>** — 2-3 sentences: identity, what it does, what it is NOT
- **The RaiSE Triad** — How this system fits in the human-AI-methodology collaboration
- **Who Uses It** — Table of actors and how they interact
- **External Systems** — Diagram showing system boundary and integrations
- **What It Does** — Command domains with brief descriptions
- **What It Does NOT Do** — Explicit non-goals (prevents scope creep and drift)
- **Design Philosophy** — Constitution principles that shape this system
- **Quality Attributes** — Measurable targets from guardrails
- **Governance Traceability** — Links to source governance docs

#### 5b: System Design (`system-design.md`)

Read `governance/guardrails.md`, module docs (for dependency data), and relevant ADRs. Write `governance/architecture/system-design.md` with:

**YAML frontmatter:**
```yaml
---
type: architecture_design
project: <project_name>
status: current
layers: [...]
architectural_decisions: [...]
guardrails_reference: "governance/guardrails.md"
constitution_reference: "framework/reference/constitution.md"
---
```

**Markdown body:**
- **Layered Architecture** — Diagram of all layers with modules in each
- **Data Flows** — The 3 core flows: Knowledge Graph Construction, Codebase Discovery, Session Lifecycle
- **Architectural Constraints** — Tables of structural, design, quality, and constitution constraints
- **Key Patterns** — Recurring patterns: Extract→Structure→Query, YAML frontmatter as schema, three-tier memory, skills+toolkit
- **What Constitutes Drift** — Explicit table of drift types, examples, and detection methods
- **Directory Layout** — Annotated tree with layer assignments
- **Governance Traceability** — Links to ADRs, guardrails, constitution

**Why this matters:** These docs are the **intentional architecture**. Deviating from them is drift. Guardrails are not just code quality rules — they are architectural constraints that shape how every module is written. The constitution principles are not aspirational — they constrain every design decision.

#### 5c: Domain Model (`domain-model.md`)

Using module docs (dependency data, purposes, public APIs), component catalog, and import analysis, write `governance/architecture/domain-model.md` with:

**YAML frontmatter:**
```yaml
---
type: architecture_domain_model
project: <project_name>
status: current
bounded_contexts: [...]
shared_kernel: { modules: [...] }
application_layer: { modules: [...] }
---
```

**Markdown body:**
- **Bounded Contexts** — Diagram showing all contexts and their modules. For each context:
  - What it owns (and what it does NOT own)
  - Aggregate roots (main entry point classes/functions)
  - Domain vocabulary table (terms with context-specific meanings)
  - Invariants (rules that must always hold)
- **Context Map** — How contexts communicate: diagram + pattern table (supplier-consumer, file-based integration, anti-corruption layer, fire-and-forget)
- **Design Decision Guidance** — "If you're adding X, it belongs in Y because Z" table. Include guidance for: when to create a new module, when to add a new NodeType/EdgeType
- **Domain Boundaries to Protect** — Table of intentional boundaries and what crossing them prevents
- **Open Questions** — Areas where intent can't be inferred from code — flag for human validation

**How to derive this:** The module docs provide dependency data and public APIs. The component catalog provides internal structure. Import analysis reveals actual communication patterns. The domain model synthesizes this structural data into DDD concepts. **Humans validate the intent** — especially bounded context naming, boundary rationale, and decision guidance.

### Step 6: Validate

- All modules documented
- System-context and system-design docs exist and are current
- YAML frontmatter parses cleanly
- Index under 2K tokens
- Dependency map is accurate (cross-check with imports)
- Guardrails referenced in system-design match current `guardrails.md`
- Constitution principles referenced match current `constitution.md`

### Step 7: Rebuild Graph

```bash
rai memory build
```

Verify module nodes appear in graph:
```bash
rai memory query "module dependencies"
```

## YAML Frontmatter Schema

### Module Docs

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| type | string | Yes | Always "module" |
| name | string | Yes | Module name (directory name) |
| purpose | string | Yes | One-line purpose description |
| status | string | No | "current", "deprecated", or "planned" |
| depends_on | list[str] | Yes | Module names this depends on |
| depended_by | list[str] | No | Module names that depend on this |
| entry_points | list[str] | No | CLI commands using this module |
| public_api | list[str] | No | Key exported symbols |
| components | int | No | Component count from discovery |
| constraints | list[str] | No | Architectural constraints |

### System Context

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| type | string | Yes | Always "architecture_context" |
| project | string | Yes | Project name |
| version | string | No | Current version |
| status | string | Yes | "current" or "deprecated" |
| tech_stack | object | Yes | Technology stack map |
| external_dependencies | list[str] | Yes | External systems |
| users | list[str] | Yes | Who uses this system |
| governed_by | list[str] | Yes | Paths to governance docs |

### System Design

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| type | string | Yes | Always "architecture_design" |
| project | string | Yes | Project name |
| status | string | Yes | "current" or "deprecated" |
| layers | list[object] | Yes | Layer definitions with modules |
| architectural_decisions | list[str] | No | ADR references |
| guardrails_reference | string | Yes | Path to guardrails doc |
| constitution_reference | string | Yes | Path to constitution doc |

### Domain Model

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| type | string | Yes | Always "architecture_domain_model" |
| project | string | Yes | Project name |
| status | string | Yes | "current" or "deprecated" |
| bounded_contexts | list[object] | Yes | Context definitions (name, modules, description) |
| shared_kernel | object | Yes | Shared kernel modules |
| application_layer | object | Yes | Application layer modules |

## Notes

- **No AI inference in CLI** — the CLI graph builder parses frontmatter deterministically
- **AI synthesizes prose** — this skill generates the human-readable sections
- **Preserve human edits** — on re-run, check for sections not in template and append them
- **Skip placeholders** — modules with no real code (engines, handlers) can be omitted
- **High-level docs are intentional architecture** — deviating from them is drift
- **Guardrails are architectural** — they shape code structure, not just code style
- **Dual-purpose docs** — serve human onboarding AND AI grounding; both must understand the system from these docs alone

## References

- Graph builder: `src/rai_cli/context/builder.py` (`load_architecture()`)
- Components: `work/discovery/components-validated.json`
- Design: `work/stories/discover-document/design.md`
- Research: `work/research/architecture-knowledge-layer/`
- Constitution: `framework/reference/constitution.md`
- Guardrails: `governance/guardrails.md`
- Vision: `governance/vision.md`
