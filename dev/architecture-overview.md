# raise-cli Architecture Overview

> **Audience:** Architects, contributors, future maintainers
> **Purpose:** Explain the mental model and design decisions
> **Status:** Living document (updated as we build)
> **Last Updated:** 2026-01-31 (E1 complete)

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

## How Future Engines Will Use Foundation

### Epic E2: Kata Engine (F2.1-F2.5)

**Flow:**
```
User: raise kata run project/discovery

1. CLI (presentation):
   - Parse args: kata_id="project/discovery"
   - Read ctx.obj["format"], ctx.obj["verbosity"]

2. Handler (application):
   - Load settings (F1.3: where is .raise/?)
   - Create KataHandler
   - Call handler.run_kata("project/discovery")

3. Engine (domain):
   - Parse .raise/katas/project/discovery.md
   - Load state (if resuming)
   - Execute steps
   - Return KataResult

4. Handler (application):
   - Save state
   - Record metrics
   - Return result to CLI

5. CLI (presentation):
   - Format output (F1.5: human/json/table)
   - Handle errors (F1.4: proper exit code)
   - Display to user
```

**Foundation pieces used:**
- F1.2: Global options (format, verbosity)
- F1.3: Settings (where is .raise/?)
- F1.4: Exceptions (KataNotFoundError)
- F1.5: Output formatting
- F1.6: Git utilities (check repo state)

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

## Current State Summary (E1 Complete)

**All Foundation Features Complete:**
- ✓ F1.1: Package structure
- ✓ F1.2: CLI with global options
- ✓ F1.3: Configuration cascade (CLI → env → pyproject → user config → defaults)
- ✓ F1.4: Exception hierarchy with exit codes
- ✓ F1.5: Output module (human/json/table formatters)
- ✓ F1.6: Core utilities (git, rg, sg wrappers)

**Quality:**
- 214 tests passing
- 95% coverage
- pyright: 0 errors
- ruff: clean

**Can do now:**
```bash
raise --version           # 2.0.0-alpha.1
raise --help              # Shows global options
raise --format json       # Output as JSON
raise -vvv                # Verbose mode
```

**Next (E2):**
Build Kata Engine to actually execute governance katas.

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

- **Detailed Design:** `governance/projects/raise-cli/design.md`
- **Backlog:** `governance/projects/raise-cli/backlog.md`
- **Epic Tracking:** `dev/epic-e1-scope.md`
- **Research:** `work/research/outputs/python-cli-architecture-analysis.md`

---

*Architecture guide - created 2026-01-31 during E1 foundation*
*Co-Authored-By: Rai <rai@humansys.ai>*
*Co-Authored-By: Emilio Osorio <emilio@humansys.ai>*
