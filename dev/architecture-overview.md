# raise-cli Architecture Overview

> **Audience:** Architects, contributors, future maintainers
> **Purpose:** Explain the mental model and design decisions
> **Status:** Living document (updated as we build)
> **Last Updated:** 2026-02-01 (E1 complete, E2 complete)

---

## The Big Picture: What is raise-cli?

**Core Problem:**
RaiSE methodology exists as static markdown files. Engineers and AI assistants can't *execute* governance - they just read and hope to follow it.

**Solution:**
A CLI tool that makes governance *executable* and *deterministic*. Think: "governance as code" that both humans and AI can run.

---

## System Architecture (Mental Model)

### Three-Layer Pattern (Ports & Adapters)

```
┌─────────────────────────────────────────────────┐
│         PRESENTATION (CLI)                      │
│  "How users interact with the system"           │
│  - Commands (kata, gate, context)               │
│  - Output formatting (human/json/table)         │
│  - Error presentation                           │
└───────────────┬─────────────────────────────────┘
                │ calls
┌───────────────▼─────────────────────────────────┐
│         APPLICATION (Handlers)                  │
│  "Orchestration and use case logic"             │
│  - Validate inputs                              │
│  - Coordinate engines                           │
│  - Manage state/metrics                         │
└───────────────┬─────────────────────────────────┘
                │ uses
┌───────────────▼─────────────────────────────────┐
│         DOMAIN (Engines)                        │
│  "Pure business logic - the 'what'"             │
│  - KataEngine: Execute governance katas         │
│  - GateEngine: Validate artifacts               │
│  - SAREngine: Analyze codebases                 │
│  - ContextGenerator: Produce CLAUDE.md          │
└───────────────┬─────────────────────────────────┘
                │ operates on
┌───────────────▼─────────────────────────────────┐
│         CORE (Schemas, Config, State)           │
│  "Shared data structures and utilities"         │
│  - Pydantic models (type-safe)                  │
│  - Configuration system                         │
│  - State persistence                            │
└─────────────────────────────────────────────────┘
```

**Key Insight:** Layers only depend *downward*. Engines never know about CLI. This means:
- Engines can be used by MCP servers, web UI, or direct Python imports
- CLI can change without touching business logic
- Easy to test each layer independently

---

## What We've Built (E1 Foundation)

### F1.1: Project Scaffolding ✓

**What:** Package structure, entry points, dependencies

**Why:** You can't build a house without a foundation. This is the concrete slab.

**Created:**
```
src/raise_cli/          # Package root
├── cli/                # Presentation (empty structure)
├── handlers/           # Application (empty structure)
├── engines/            # Domain (empty structure)
├── schemas/            # Core data models (empty structure)
├── config/             # Configuration (empty structure)
├── output/             # Formatters (empty structure)
└── core/               # Utilities (empty structure)
```

Plus: `pyproject.toml`, tests/, .gitignore, venv setup

**Metaphor:** Built the directory structure and plumbing. Rooms exist but are empty.

---

### F1.2: CLI Skeleton ✓

**What:** Global options infrastructure (--format, -v, -q)

**Why:** Every command needs these options. Set them up once, all future commands inherit them.

**How it works:**
```python
@app.callback()
def main(ctx: typer.Context, format: str, verbose: int, quiet: bool):
    # Store options in context
    ctx.obj["format"] = format
    ctx.obj["verbosity"] = -1 if quiet else min(verbose, 3)

    # Future commands access via: ctx.obj["format"]
```

When we add `raise kata list`, it automatically gets:
- `raise kata list --format json`
- `raise kata list -vvv`
- `raise kata list -q`

**Metaphor:** Installed the electrical panel. Every room will plug into it, but no rooms wired yet.

---

## What's Coming Next (Architecture Preview)

### F1.3: Configuration System

**What:** Pydantic Settings with cascade

**Why:** Users need to configure:
- Where `.raise/` directory is
- Output preferences
- External tool paths (ast-grep, ripgrep)

**Cascade (priority order):**
```
CLI args > Environment vars > pyproject.toml > ~/.config/raise/config.toml > defaults
```

**Example:**
```python
# User runs: raise kata list --format json
# With RAISE_OUTPUT_FORMAT=table in env
# Result: Uses "json" (CLI wins)

settings = RaiseSettings()  # Auto-loads with cascade
# settings.output_format
# settings.raise_dir
# settings.verbosity
```

**Why now:** Handlers (F2+) need to know where `.raise/` is, what format to output, etc.

---

### F1.4: Exception Hierarchy

**What:** Structured errors with exit codes

**Why:** Different errors need different exit codes for scripting:
```bash
raise kata run discovery || echo "Kata failed with code $?"
# Exit 3 = not found
# Exit 10 = gate failed
# Exit 5 = dependency missing
```

**Structure:**
```python
RaiseError (base)
├── ConfigurationError (exit 2)
├── KataNotFoundError (exit 3)
├── GateFailedError (exit 10)
└── DependencyError (exit 5)
```

Plus: Rich formatting for human-readable errors with hints.

---

### F1.5: Output Module ✓

**What:** OutputConsole class with format-aware output

**Why:** Handlers need to output results. Format based on `--format` flag.

**How it works:**
```python
from raise_cli.output import get_console, configure_console

# Configure once (usually in CLI callback)
console = configure_console(format="human", verbosity=0, color=True)

# Use anywhere
console.print_success("Kata completed", details={"steps": 5})
console.print_data({"name": "discovery", "status": "done"})
console.print_list(["item1", "item2"], title="Results")
```

**Formats:** human (Rich styling), json (parseable), table (Rich tables)

---

### F1.6: Core Utilities ✓

**What:** Typed subprocess wrappers for git, ast-grep, ripgrep

**Why:** Engines need to:
- Check git status, branch, diff
- Run ast-grep for AST patterns (SAR)
- Run ripgrep for text search (SAR)

**How it works:**
```python
from raise_cli.core import git_status, rg_search, check_tool

# Check if tools available
if check_tool("rg"):
    matches = rg_search("TODO", Path("."), glob="*.py")

# Get git info
status = git_status()
print(f"On {status.branch}, {len(status.staged)} staged files")
```

**Error handling:** Raises `DependencyError` with install hints if tools missing

---

## What We've Built (E2 Governance Toolkit)

### Architecture Decision: Skills + Toolkit Pattern

**Major pivot from original design:**
- **Original plan:** Monolithic engines (KataEngine, GateEngine, SAREngine)
- **Actual delivery:** Skills + CLI Toolkit pattern (ADR-011, ADR-012)

**Why the change:**
- Concept-level graph provides 97% token savings (vs 27% file-level)
- Skills execute processes by reading markdown guides (AI-friendly)
- CLI toolkit provides deterministic data extraction (machine-friendly)
- 85% scope reduction (60 SP → 9 SP → 7 SP delivered)

**The Pattern:**
```
┌──────────────────────────────────────────────────┐
│   CLAUDE (AI Partner)                            │
│   - Reads Skills (process guides in markdown)    │
│   - Calls CLI Toolkit for deterministic ops      │
│   - Uses Concept Graph for context               │
└──────────────────┬───────────────────────────────┘
                   │ orchestrates
┌──────────────────▼───────────────────────────────┐
│   CLI TOOLKIT (Deterministic Operations)         │
│   - raise governance extract                     │
│   - raise graph build                            │
│   - raise graph validate                         │
│   - raise context query                          │
└──────────────────┬───────────────────────────────┘
                   │ operates on
┌──────────────────▼───────────────────────────────┐
│   GOVERNANCE FILES (Markdown)                    │
│   - Constitution, Vision, PRD, Guardrails        │
│   - Versioned in Git                             │
│   - Human-readable, machine-parseable            │
└──────────────────────────────────────────────────┘
```

**Key insight:** Don't build "engines" that try to be smart. Build dumb tools + smart context.

---

### F2.1: Concept Extraction ✓

**What:** Parse governance markdown files into structured concept data

**Why:** Transform static docs into queryable knowledge graph

**Created:**
```
src/raise_cli/governance/extraction/
├── parsers.py          # Constitution, Vision, Guardrails parsers
└── models.py           # Concept, Component, Guardrail models

CLI: raise governance extract [--output FILE] [--format json|markdown]
```

**How it works:**
```python
from raise_cli.governance.extraction import extract_concepts

# Extract from raise-commons governance
concepts = extract_concepts(
    constitution_path=Path("framework/reference/constitution.md"),
    vision_path=Path("governance/solution/vision.md"),
    guardrails_path=Path("governance/solution/guardrails.md")
)

# Result: 23 concepts extracted
# - 8 principles (from Constitution)
# - 9 components (from Vision)
# - 6 guardrails (from Guardrails)
```

**Parsers:**
- **Constitution:** Regex-based extraction of principles (§N format)
- **Vision:** Component extraction with dependencies
- **Guardrails:** Rule extraction with verification commands

**Metaphor:** Built the librarian that catalogs all books in the governance library.

---

### F2.2: Graph Builder ✓

**What:** Build concept graph with relationships and traversal

**Why:** Enable semantic navigation and dependency analysis

**Created:**
```
src/raise_cli/governance/graph/
├── models.py           # ConceptGraph, Edge, RelationshipType
├── builder.py          # Graph construction from concepts
├── traversal.py        # BFS traversal with cycle detection
└── relationships.py    # Relationship inference rules

CLI: raise graph build [--output FILE] [--validate]
CLI: raise graph validate [--graph FILE]
```

**How it works:**
```python
from raise_cli.governance.graph import ConceptGraphBuilder

# Build graph from extracted concepts
builder = ConceptGraphBuilder()
graph = builder.build_from_concepts(concepts)

# Graph structure:
# - 23 concepts (nodes)
# - 47 edges (relationships)
# - 5 relationship types: governed_by, implements, validates, depends_on, related_to

# Serialize to JSON for caching
graph_json = graph.to_json()
# Save to: .raise/cache/graph.json
```

**Relationship types:**
- `governed_by`: Concept adheres to principle/rule
- `implements`: Feature implements requirement
- `validates`: Gate validates artifact
- `depends_on`: Technical dependency
- `related_to`: Semantic relationship

**Traversal:**
```python
from raise_cli.governance.graph import traverse_bfs

# Find all concepts within 2 hops of REQ-RF-05
context = traverse_bfs(
    graph=graph,
    start_id="req-rf-05",
    max_depth=2,
    edge_types=["governed_by", "implements"]
)
```

**Metaphor:** Built the map showing how all governance concepts connect.

---

### F2.3: MVC Query Engine ✓

**What:** Query concept graph for Minimum Viable Context (MVC)

**Why:** 97% token savings for AI context queries

**Created:**
```
src/raise_cli/governance/query/
├── models.py           # ContextQuery, ContextResult
├── strategies.py       # 4 query strategies
├── engine.py           # ContextQueryEngine orchestrator
└── formatters.py       # Markdown, JSON output + token estimation

CLI: raise context query QUERY [--strategy STRATEGY] [--format FORMAT]
```

**How it works:**
```python
from raise_cli.governance.query import ContextQueryEngine, ContextQuery, QueryStrategy

# Load graph from cache
engine = ContextQueryEngine.from_cache()

# Query for concept
query = ContextQuery(
    query="req-rf-05",
    strategy=QueryStrategy.CONCEPT_LOOKUP,
    max_depth=1
)

result = engine.query(query)

# Result:
# - 1 concept found
# - 67 tokens (vs 2000+ for full file)
# - 97% token savings
# - <1ms query time
```

**Query strategies:**
1. **concept_lookup:** Find exact concept by ID
2. **keyword_search:** Find concepts containing keywords (stopword filtering)
3. **relationship_traversal:** BFS from concept following relationships
4. **related_concepts:** Find semantically related concepts

**Output formats:**
- **Markdown:** Human-readable with headers, sections
- **JSON:** Machine-parseable with full metadata

**Token estimation:**
```python
# Simple heuristic (spike-validated):
tokens = len(text.split()) * 1.3

# Accurate enough for MVC queries
# No ML/NLP needed
```

**Performance:**
- Query speed: <1ms (0.01-0.17ms measured)
- Token savings: 97-99% (single concept), 97% average
- Graph build: <1s for 23 concepts

**Metaphor:** Built the reference librarian who finds exactly what you need, not the whole library.

---

### E2 Architecture Summary

**Modules added:**
```
src/raise_cli/governance/
├── extraction/          # F2.1 - Parse governance files
│   ├── parsers.py       # Constitution, Vision, Guardrails parsers
│   └── models.py        # Concept, Component, Guardrail models
├── graph/               # F2.2 - Build concept graph
│   ├── models.py        # ConceptGraph, Edge, RelationshipType
│   ├── builder.py       # Graph construction from concepts
│   ├── traversal.py     # BFS traversal with cycle detection
│   └── relationships.py # Relationship inference rules
└── query/               # F2.3 - Query concept graph
    ├── models.py        # ContextQuery, ContextResult
    ├── strategies.py    # 4 query strategies
    ├── engine.py        # ContextQueryEngine orchestrator
    └── formatters.py    # Markdown, JSON output + token estimation
```

**CLI commands added:**
```bash
raise governance extract  # F2.1
raise graph build         # F2.2
raise graph validate      # F2.2
raise context query       # F2.3
```

**Data flow:**
```
Governance Files (*.md)
        ↓ extract
    Concepts (23)
        ↓ build
   Concept Graph (23 nodes, 47 edges)
        ↓ serialize
   graph.json (.raise/cache/)
        ↓ load + query
   Minimum Viable Context (97% token savings)
```

**Foundation pieces used:**
- F1.2: Global options (--format, -v, -q)
- F1.3: Settings (where is .raise/? where to cache?)
- F1.4: Exceptions (ConceptNotFoundError, GraphValidationError)
- F1.5: Output formatting (human/json/table)
- F1.6: Not used (E2 doesn't need git/rg/sg)

---

## How Future Epics Will Use Governance Toolkit

### Epic E3/E4: Context Generation (Using E2 Output)

**Flow:**
```
User: raise context query "req-rf-05" --format markdown

1. CLI (presentation):
   - Parse args: query="req-rf-05", format="markdown"
   - Read ctx.obj["format"], ctx.obj["verbosity"]

2. CLI command (no handler needed for simple queries):
   - Load graph from cache (.raise/cache/graph.json)
   - Create ContextQueryEngine
   - Create ContextQuery with strategy
   - Call engine.query(query)

3. Query engine (domain):
   - Parse query string
   - Execute strategy (concept_lookup)
   - Format result (markdown formatter)
   - Estimate tokens
   - Return ContextResult

4. CLI (presentation):
   - Format output (F1.5: human/json/table)
   - Handle errors (F1.4: ConceptNotFoundError)
   - Display to user
```

**Foundation pieces used:**
- F1.2: Global options (--format, -v, -q)
- F1.3: Settings (cache directory location)
- F1.4: Exceptions (ConceptNotFoundError, GraphValidationError)
- F1.5: Output formatting (markdown/json)
- F1.6: Not used (E2 doesn't need git/rg/sg)

---

## Key Architectural Decisions

### Why Three Layers?

**Alternative:** CLI → Engine (direct)

**Problem:**
- Engine becomes aware of CLI concerns (formatting, state, metrics)
- Can't reuse engine in MCP server or web UI
- Hard to test business logic

**Our approach:** Handlers orchestrate, engines focus on pure logic

---

### Why Pydantic Everywhere?

**Alternative:** dict, TypedDict, dataclasses

**Why Pydantic:**
- Runtime validation (catch bad data early)
- JSON serialization (for state, metrics, API)
- Settings cascade (F1.3)
- Documentation (auto-generated schemas)

**Example:**
```python
# This fails at parse time, not in engine
kata = KataDefinition(**yaml_data)  # Validates structure
```

---

### Why Rich for Output?

**Alternative:** print() statements

**Why Rich:**
- Color/formatting for humans
- Tables, panels, progress bars
- Terminal detection (auto-disable in CI)
- Consistent UX

---

### Why XDG Directories?

**Alternative:** `~/.raise/` for everything

**Why XDG:**
- Standard on Linux/Mac
- Separates concerns:
  - `~/.config/raise/` - User configuration
  - `~/.cache/raise/` - Temp data
  - `~/.local/share/raise/` - State, metrics
- Respects user environment variables

---

## The Mental Model

Think of raise-cli as **three concentric circles**:

1. **Outer (CLI):** User-facing interface. Changes frequently as we add commands.

2. **Middle (Handlers):** Orchestration. Knows about both CLI and engines. Coordinates workflows.

3. **Inner (Engines):** Pure logic. Stable. Doesn't know about CLI or handlers. Just does the work.

**Foundation (E1):** Building the outer circle infrastructure so when we build engines (E2-E4), they have a solid platform.

---

## What Makes This "Governance as Code"?

**Traditional:**
1. Read governance docs (.md files)
2. Manually follow steps
3. Hope you did it right

**RaiSE CLI:**
1. `raise kata run project/discovery` → Executes governance
2. `raise gate check prd` → Validates you followed governance
3. `raise context generate` → Configures AI with governance

**Deterministic:** Same inputs → same outputs. Auditable. Repeatable.

---

## Current State Summary (E1 + E2 Complete)

**E1 Foundation Features Complete:**
- ✓ F1.1: Package structure
- ✓ F1.2: CLI with global options
- ✓ F1.3: Configuration cascade (CLI → env → pyproject → user config → defaults)
- ✓ F1.4: Exception hierarchy with exit codes
- ✓ F1.5: Output module (human/json/table formatters)
- ✓ F1.6: Core utilities (git, rg, sg wrappers)

**E2 Governance Toolkit Features Complete:**
- ✓ F2.1: Concept Extraction (parse governance files)
- ✓ F2.2: Graph Builder (build concept graph with relationships)
- ✓ F2.3: MVC Query Engine (97% token savings for AI context)

**Quality:**
- 457 tests passing (214 from E1 + 243 from E2)
- 95-100% coverage
- pyright: 0 errors
- ruff: clean
- bandit: clean

**Can do now:**
```bash
# Foundation
raise --version           # 2.0.0-alpha.1
raise --help              # Shows global options
raise --format json       # Output as JSON
raise -vvv                # Verbose mode

# Governance Toolkit
raise governance extract  # Extract 23 concepts from governance files
raise graph build         # Build concept graph (23 nodes, 47 edges)
raise graph validate      # Validate graph structure
raise context query "req-rf-05"  # Query for MVC (97% token savings)
raise context query "authentication" --strategy keyword  # Keyword search
```

**Impact:**
- 23 concepts extracted from raise-commons governance
- 97% token savings for AI context queries (<1ms query time)
- Concept graph ready for E4 (Context Generation)

**Next (E3+):**
Build context generation, skills execution, or continue with backlog features.

---

## For Contributors

**Adding a new engine:**
1. Create domain logic in `engines/` (pure Python, no I/O)
2. Define data models in `schemas/`
3. Create handler in `handlers/` (orchestration)
4. Add CLI commands in `cli/commands/`
5. Write tests at each layer

**The dependency rule:**
- CLI can import handlers, schemas, config
- Handlers can import engines, schemas, config
- Engines can import schemas only
- Nobody imports CLI (except tests)

**Testing strategy:**
- Unit tests: engines (pure logic)
- Integration tests: handlers (orchestration)
- CLI tests: commands (Typer CliRunner)
- E2E tests: full workflows

---

## References

**Epic Tracking:**
- `dev/epic-e1-scope.md` - E1 Core Foundation (complete)
- `dev/epic-e2-scope.md` - E2 Governance Toolkit (complete)
- `dev/epic-e2-retrospective.md` - E2 retrospective with learnings

**Architecture Decisions:**
- `dev/decisions/framework/ADR-011-concept-graph-architecture.md` - 97% token savings
- `dev/decisions/framework/ADR-012-skills-toolkit-pattern.md` - 85% scope reduction

**Design Documents:**
- `governance/projects/raise-cli/design.md` - Original design
- `governance/projects/raise-cli/backlog.md` - Feature backlog
- `work/features/f2.1-concept-extraction/design.md` - F2.1 design
- `work/features/f2.2-graph-builder/design.md` - F2.2 design
- `work/features/f2.3-mvc-query-engine/design.md` - F2.3 design

**Component Catalog:**
- `dev/components.md` - Complete module documentation (E1 + E2)

**Research:**
- `work/research/outputs/python-cli-architecture-analysis.md` - CLI architecture research

---

*Architecture guide - created 2026-01-31 during E1, updated 2026-02-01 for E2*
*Co-Authored-By: Rai <rai@humansys.ai>*
*Co-Authored-By: Emilio Osorio <emilio@humansys.ai>*
