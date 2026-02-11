# Component Catalog

> **Purpose:** Single source of truth for all raise-cli components
> **Audience:** Contributors, GraphRAG, future maintainers
> **Update:** Per feature as components are added
> **Status:** Living document

---

## How to Use This Catalog

**For contributors:** Find what exists, understand dependencies, avoid duplication
**For GraphRAG:** Query "What does X do?", "What uses Y?", "Where is Z?"
**For reviewers:** Verify new components are documented

---

## Engines (Domain Layer)

> Pure business logic - no I/O awareness

*Deprecated per ADR-012. Skills + Toolkit architecture replaced engine approach.*

---

## Handlers (Application Layer)

> Orchestration and use case coordination

*Deprecated per ADR-012. Skills + Toolkit architecture replaced handler approach.*

---

## CLI Commands (Presentation Layer)

> User-facing commands

### Global Options (F1.2, updated F1.3)
- **Location:** `src/rai_cli/cli/main.py`
- **Purpose:** Global options for all commands (format, verbosity, quiet)
- **Added:** F1.2 (Epic E1), integrated with RaiseSettings in F1.3
- **API:**
  - `--format/-f` (human|json|table)
  - `--verbose/-v` (count, up to -vvv)
  - `--quiet/-q` (suppress non-error output)
- **Storage:**
  - `ctx.obj["settings"]` (RaiseSettings instance) - primary
  - `ctx.obj["format"]`, `ctx.obj["verbosity"]`, `ctx.obj["quiet"]` - backward compat
- **Dependencies:** `RaiseSettings` (F1.3)

### Error Handler (F1.4)
- **Location:** `src/rai_cli/cli/error_handler.py`
- **Purpose:** Format and display errors with Rich output or JSON
- **Added:** F1.4 (Epic E1)
- **Public API:**
  - `handle_error(error, output_format) -> int` - Display error, return exit code
  - `get_error_console() -> Console` - Get stderr console singleton
  - `set_error_console(console)` - Override console (for testing)
- **Features:**
  - Rich Panel with error code title and message
  - Details section (key-value pairs)
  - Hint section (cyan text)
  - JSON output mode for `--format json`
- **Dependencies:** `RaiseError` hierarchy, Rich
- **Tests:** 22 unit tests (100% coverage)

---

## Schemas (Data Models)

> Pydantic models for type-safe data structures

### Governance Models (F2.1)
- **Location:** `src/rai_cli/governance/models.py`
- **Purpose:** Pydantic models for concept extraction from governance files
- **Added:** F2.1 (Epic E2)
- **Public API:**
  - `ConceptType(Enum)` - REQUIREMENT, OUTCOME, PRINCIPLE, PATTERN, PRACTICE
  - `Concept(BaseModel)` - Semantic concept with id, type, file, section, lines, content, metadata
  - `ExtractionResult(BaseModel)` - Result with concepts list, total, files_processed, errors
- **Features:**
  - Type-safe concept representation
  - Line range validation (start <= end)
  - Serialization/deserialization support
- **Dependencies:** Pydantic v2
- **Tests:** 11 unit tests (100% coverage)

---

## Governance Module (E2)

> Concept extraction from governance markdown files

### Governance Parsers (F2.1)
- **Location:** `src/rai_cli/governance/parsers/`
- **Purpose:** Extract semantic concepts from governance markdown files
- **Added:** F2.1 (Epic E2)
- **Sub-modules:**
  - `prd.py` - Extract requirements (RF-XX format) from PRD files
  - `vision.py` - Extract outcomes from Vision markdown tables
  - `constitution.py` - Extract principles (§N format) from Constitution
- **Public API:**
  - `extract_requirements(file_path, project_root) -> list[Concept]`
  - `extract_outcomes(file_path, project_root) -> list[Concept]`
  - `extract_principles(file_path, project_root) -> list[Concept]`
- **Features:**
  - Regex-based pattern matching for structured markdown
  - Content truncation (500 chars or 20-30 lines)
  - Graceful handling of missing files, malformed sections
  - ID sanitization for concept identifiers
- **Coverage:** PRD 91%, Vision 95%, Constitution 95%
- **Tests:** 15 (PRD) + 18 (Vision) + 15 (Constitution) = 48 unit tests
- **Related:** ADR-011 (concept-level graph architecture)

### Governance Extractor (F2.1)
- **Location:** `src/rai_cli/governance/extractor.py`
- **Purpose:** Orchestrate concept extraction from all governance files
- **Added:** F2.1 (Epic E2)
- **Public API:**
  - `GovernanceExtractor(project_root)` - Initialize extractor
  - `.extract_from_file(file_path, concept_type) -> list[Concept]` - Extract from single file
  - `.extract_all() -> list[Concept]` - Extract from all standard locations
  - `.extract_with_result() -> ExtractionResult` - Extract with metadata
- **Standard Locations:**
  - `governance/prd.md` (requirements)
  - `governance/vision.md` (outcomes)
  - `framework/reference/constitution.md` (principles)
- **Features:**
  - Automatic concept type inference from file path
  - Error collection without crashing
  - Logging of extraction progress
- **Dependencies:** All parsers (prd, vision, constitution)
- **Coverage:** 78% (logger statements and exception paths untested)
- **Tests:** 14 unit + integration tests
- **Related:** ADR-011

### Graph Module (F2.2)
- **Location:** `src/rai_cli/governance/graph/`
- **Purpose:** Build and query concept-level directed graphs from extracted concepts
- **Added:** F2.2 (Epic E2)
- **Sub-modules:**
  - `models.py` - Pydantic models for ConceptGraph and Relationship
  - `relationships.py` - Rule-based relationship inference (4 rules)
  - `traversal.py` - BFS graph traversal with depth limits
  - `builder.py` - GraphBuilder orchestrator
- **Public API:**
  - `ConceptGraph(BaseModel)` - Graph with nodes dict, edges list, metadata
  - `Relationship(BaseModel)` - Directed edge with source, target, type, metadata
  - `RelationshipType` - Literal type (implements, governed_by, depends_on, related_to, validates)
  - `GraphBuilder().build(concepts) -> ConceptGraph` - Build graph from concepts
  - `traverse_bfs(graph, start_id, edge_types, max_depth) -> list[Concept]` - BFS traversal
- **Relationship Inference Rules:**
  1. `implements` - Requirement → Outcome (keyword matching in content)
  2. `governed_by` - Requirement/Outcome → Principle (§N references)
  3. `depends_on` - Concept → Concept (explicit "depends on RF-XX")
  4. `related_to` - Concept ↔ Concept (>3 shared keywords)
- **Features:**
  - JSON serialization/deserialization (to_json/from_json)
  - Graph query methods (get_node, get_outgoing_edges, get_incoming_edges)
  - Build metadata (timestamp, version, edge statistics)
  - Cycle handling in BFS (visited set)
  - Keyword extraction with stopword filtering
- **Performance:**
  - Build <2s for 50 concepts (measured)
  - BFS <100ms for 50-node graph (measured)
- **Coverage:** models 100%, relationships 86%, traversal 100%, builder 92%
- **Tests:** 14 (models) + 19 (relationships) + 11 (traversal) + 9 (builder) + 10 (integration) = 63 tests
- **Dependencies:** F2.1 Concept models
- **Related:** ADR-011 (concept-level graph architecture)

### Graph CLI Commands (F2.1, F2.2)
- **Location:** `src/rai_cli/cli/commands/graph.py`
- **Purpose:** CLI interface for concept graph operations (extract, build, validate)
- **Added:** F2.1 (extract), F2.2 (build, validate) - Epic E2
- **Commands:**
  - `rai graph extract [FILE_PATH]` - Extract concepts from governance files
  - `rai graph build` - Build concept graph with relationship inference
  - `rai graph validate` - Validate graph structure and relationships
- **Options (extract):**
  - `--format/-f` (human|json) - Output format
- **Options (build):**
  - `--concepts/-c PATH` - Custom concepts JSON file (default: `.raise/cache/concepts.json`)
  - `--output/-o PATH` - Custom output location (default: `.raise/cache/graph.json`)
- **Options (validate):**
  - `--graph/-g PATH` - Custom graph file to validate (default: `.raise/cache/graph.json`)
- **Features:**
  - Human-readable output with Rich formatting (✓ checkmarks, colors, statistics)
  - JSON output for machine processing (extract)
  - Auto-extraction if concepts not cached (build)
  - Graph validation (all edges valid, cycle detection, reachability)
  - Automatic cache directory creation
- **Example Output (build):**
  ```
  Building concept graph...
    ✓ Loaded 24 concepts
    ✓ Inferred 33 relationships
      - related_to: 33
    ✓ Saved to .raise/cache/graph.json

  Graph: 23 nodes, 33 edges
  ```
- **Example Output (validate):**
  ```
  Validating graph...
    ✓ All relationships valid
    ✓ No cycles detected
    ✓ 23/23 concepts reachable

  Graph is valid.
  ```
- **Dependencies:** GovernanceExtractor, GraphBuilder, ConceptGraph, Rich
- **Tests:** 8 (extract) + 4 (build) + 4 (validate) = 16 CLI integration tests
- **Related:** ADR-011

### MVC Query Engine (F2.3)
- **Location:** `src/rai_cli/governance/query/`
- **Purpose:** Extract Minimum Viable Context (MVC) from concept graph, achieving >90% token savings vs loading full files
- **Added:** F2.3 (Epic E2)
- **Type:** Query orchestrator with 4 strategies, multiple output formats
- **Public API:**
  - `ContextQueryEngine(graph)` - Initialize with concept graph
  - `ContextQueryEngine.from_cache(path) -> ContextQueryEngine` - Load from cached graph JSON
  - `engine.query(ContextQuery) -> ContextResult` - Execute query and return results
  - `ContextQuery(query, strategy, max_depth, filters)` - Query parameters
  - `ContextResult(concepts, metadata)` - Query results with metadata
  - `result.to_json() -> str` - Serialize to JSON
  - `result.to_file(path, format)` - Save to file (markdown or json)
- **Query Strategies:**
  1. `CONCEPT_LOOKUP` - Direct ID lookup + 1-hop dependencies (governed_by, implements)
  2. `KEYWORD_SEARCH` - Keyword matching with optional type filter
  3. `RELATIONSHIP_TRAVERSAL` - Follow specific edge types via BFS
  4. `RELATED_CONCEPTS` - Semantic similarity via shared keywords (>2 shared)
- **Output Formats:**
  - **Markdown:** AI-optimized with headers, relationship annotations, token estimates
  - **JSON:** Structured output with concepts array + metadata object
- **Metadata Tracked:**
  - Token estimate (words * 1.3 heuristic, spike-validated)
  - Execution time (ms)
  - Relationship paths (for explainability)
  - Traversal depth (actual vs max)
- **Features:**
  - Reuses F2.2 BFS traversal (no duplication)
  - Simple keyword matching (no NLP dependencies)
  - Relationship path tracing for "why this concept?" explanations
  - Token savings estimation vs manual file loading
- **Performance:**
  - Direct lookup: <50ms (target)
  - Keyword search: <200ms (target)
  - BFS traversal: <100ms (target)
  - Token savings: >90% (measured vs ~6,000 token baseline)
- **Coverage:** models 100%, strategies 98%, engine 98%, formatters 100%
- **Tests:** 14 (models) + 27 (strategies) + 22 (engine) + 17 (formatters) + 8 (CLI) + 11 (integration) = 99 tests
- **Dependencies:** F2.1 Concept models, F2.2 ConceptGraph + BFS traversal
- **Related:** ADR-011 (97% token savings validated)

### Context CLI Commands (F2.3)
- **Location:** `src/rai_cli/cli/commands/context.py`
- **Purpose:** CLI interface for querying concept graph and retrieving MVC
- **Added:** F2.3 (Epic E2)
- **Commands:**
  - `rai context query <QUERY>` - Query concept graph for Minimum Viable Context
- **Options:**
  - `--format/-f (markdown|json)` - Output format (default: markdown)
  - `--output/-o PATH` - Save to file instead of stdout
  - `--strategy/-s STRATEGY` - Explicit strategy selection
  - `--max-depth/-d INT` - Maximum traversal depth (0-5, default: 1)
  - `--edge-types/-e TYPES` - Comma-separated edge types to follow (e.g., "governed_by,implements")
  - `--type/-t TYPE` - Filter by concept type (requirement, principle, outcome)
- **Examples:**
  ```bash
  # Query by concept ID
  raise context query "req-rf-05"

  # Keyword search in requirements only
  raise context query "validation" --type requirement

  # Traverse relationships
  raise context query "req-rf-05" --strategy relationship_traversal --edge-types governed_by

  # Save to file as JSON
  raise context query "req-rf-05" --output context.json --format json
  ```
- **Features:**
  - Human-readable markdown output (default) optimized for AI consumption
  - JSON output for tool integration
  - Error handling with helpful messages (graph not found → suggests `rai graph build`)
  - Token estimate and savings displayed in output
  - Execution time tracking
- **Dependencies:** ContextQueryEngine, ConceptGraph, Rich
- **Tests:** 8 CLI integration tests
- **Related:** ADR-011

---

## Configuration (Core Layer)

### RaiseSettings (F1.3)
- **Location:** `src/rai_cli/config/settings.py`
- **Purpose:** Centralized configuration with 5-level cascade precedence
- **Added:** F1.3 (Epic E1)
- **Type:** Pydantic BaseSettings with custom TOML sources
- **Cascade Precedence:**
  1. CLI arguments (constructor) - highest priority
  2. Environment variables (`RAISE_*` prefix)
  3. Project config (`pyproject.toml` `[tool.raise]`)
  4. User config (`~/.config/raise/config.toml` `[raise]`)
  5. Defaults - lowest priority
- **Public API:**
  - `output_format: Literal["human", "json", "table"]` (default: "human")
  - `color: bool` (default: True)
  - `verbosity: int` (default: 0, range: -1 to 3)
  - `raise_dir: Path` (default: ".raise")
  - `governance_dir: Path` (default: "governance")
  - `work_dir: Path` (default: "work")
  - `ast_grep_path: str | None` (default: None)
  - `ripgrep_path: str | None` (default: None)
  - `interactive: bool` (default: False)
- **Dependencies:** `TomlConfigSource` (custom), `get_config_dir()` from paths
- **Related ADRs:** ADR-002 (Pydantic validation), ADR-004 (XDG directories)
- **Tests:** 24 unit tests + 11 integration tests (cascade)

### XDG Directory Helpers (F1.3)
- **Location:** `src/rai_cli/config/paths.py`
- **Purpose:** XDG Base Directory compliant path resolution
- **Added:** F1.3 (Epic E1)
- **Specification:** [XDG Base Directory Spec](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html)
- **Public API:**
  - `get_config_dir() -> Path` - Returns `~/.config/raise/` (or `$XDG_CONFIG_HOME/raise/`)
  - `get_cache_dir() -> Path` - Returns `~/.cache/raise/` (or `$XDG_CACHE_HOME/raise/`)
  - `get_data_dir() -> Path` - Returns `~/.local/share/raise/` (or `$XDG_DATA_HOME/raise/`)
- **Behavior:**
  - Respects XDG environment variables if set
  - Falls back to standard locations if not
  - Returns Path objects (doesn't create directories)
- **Dependencies:** None (stdlib only)
- **Related ADRs:** ADR-004 (XDG directories)
- **Tests:** 9 unit tests (defaults + env var overrides)

### TomlConfigSource (F1.3 - Internal)
- **Location:** `src/rai_cli/config/settings.py` (private class)
- **Purpose:** Custom Pydantic settings source for TOML file loading
- **Added:** F1.3 (Epic E1)
- **Type:** `PydanticBaseSettingsSource` subclass
- **Supports:**
  - `pyproject.toml` with `[tool.raise]` section
  - User config with `[raise]` section
  - Graceful degradation for malformed/missing TOML
- **Python Compatibility:** Uses `tomllib` (3.11+) or `tomli` (3.10)
- **Tests:** Covered by cascade integration tests

---

## Exceptions (Core Layer)

> Centralized error hierarchy with exit codes

### RaiseError Hierarchy (F1.4)
- **Location:** `src/rai_cli/exceptions.py`
- **Purpose:** Centralized exceptions with exit codes, error codes, hints
- **Added:** F1.4 (Epic E1)
- **Export:** All exceptions exported from `rai_cli` package root
- **Base Class:** `RaiseError`
  - `exit_code: int` - Process exit code
  - `error_code: str` - Unique identifier (E000-E010)
  - `message: str` - Human-readable description
  - `hint: str | None` - Resolution suggestion
  - `details: dict` - Structured debugging data
  - `to_dict() -> dict` - JSON serialization
- **Exception Classes:**

| Exception | Exit Code | Error Code | Use Case |
|-----------|-----------|------------|----------|
| `RaiseError` | 1 | E000 | General errors |
| `ConfigurationError` | 2 | E001 | Config file issues |
| `KataNotFoundError` | 3 | E002 | Missing kata |
| `GateNotFoundError` | 3 | E003 | Missing gate |
| `ArtifactNotFoundError` | 4 | E004 | Missing artifact file |
| `DependencyError` | 5 | E005 | External tool unavailable |
| `StateError` | 6 | E006 | Corrupted state file |
| `ValidationError` | 7 | E007 | Schema/artifact validation |
| `GateFailedError` | 10 | E010 | Gate criteria not met |

- **Related ADRs:** Design §4 (Error Handling)
- **Tests:** 43 unit tests (100% coverage)

---

## Output Formatters (Core Layer)

> Format-aware output for CLI commands

### OutputConsole (F1.5)
- **Location:** `src/rai_cli/output/console.py`
- **Purpose:** Unified output interface respecting `--format` flag
- **Added:** F1.5 (Epic E1)
- **Export:** `raise_cli.output`
- **Formats Supported:**
  - `human` - Rich styling (colors, checkmarks, tables, trees)
  - `json` - Valid JSON to stdout (parseable by `jq`)
  - `table` - Rich Table for structured lists
- **Public API:**
  - `OutputConsole(format, verbosity, color)` - Constructor
  - `print_message(message, style)` - Simple text output
  - `print_success(message, details)` - Green checkmark + optional details
  - `print_warning(message, details)` - Yellow warning symbol
  - `print_data(data, title)` - Dict → tree/json/key-value table
  - `print_list(items, columns, title)` - List → bullets/json array/table
- **Module Functions:**
  - `get_console()` - Get singleton instance
  - `set_console(console)` - Override singleton (for testing)
  - `configure_console(format, verbosity, color)` - Configure and return singleton
- **Verbosity:**
  - `-1` (quiet): Suppresses all non-error output
  - `0` (normal): Standard output
  - `1-3` (verbose): Reserved for future use
- **Dependencies:** Rich
- **Tests:** 40 unit tests (95% coverage)

---

## Utilities (Core Layer)

### Tool Wrappers (F1.6)
- **Location:** `src/rai_cli/core/tools.py`
- **Purpose:** Typed subprocess wrappers for external tools
- **Added:** F1.6 (Epic E1)
- **Export:** `raise_cli.core`
- **Tools Wrapped:**
  - `git` - Version control operations
  - `rg` (ripgrep) - Fast text search
  - `sg` (ast-grep) - AST-based code search
- **Public API:**
  - `check_tool(name) -> bool` - Check if tool is available
  - `require_tool(name)` - Raise `DependencyError` if missing
  - `run_tool(args, cwd, check) -> ToolResult` - Run command and capture output
  - `git_root(cwd) -> Path` - Get git repository root
  - `git_branch(cwd) -> str` - Get current branch name
  - `git_status(cwd) -> GitStatus` - Structured git status (staged, modified, untracked)
  - `git_diff(staged, cwd) -> str` - Get diff output
  - `rg_search(pattern, path, glob, ignore_case) -> list[SearchMatch]` - Search with ripgrep
  - `sg_search(pattern, path, lang) -> list[SearchMatch]` - Search with ast-grep
- **Data Classes:**
  - `ToolResult` - returncode, stdout, stderr, success property
  - `GitStatus` - staged, modified, untracked, branch
  - `SearchMatch` - path, line, text
- **Error Handling:** Raises `DependencyError` with install hints for missing tools
- **Dependencies:** None (stdlib subprocess, shutil)
- **Tests:** 34 unit tests (100% coverage)

---

## RaiSE Skills Infrastructure

> Agent Skills format adoption for methodology delivery (ADR-005)

### Skills Directory Structure
- **Location:** `.claude/skills/`
- **Purpose:** RaiSE methodology delivered as Agent Skills (open standard)
- **Added:** 2026-01-31 (Skills Architecture Decision)
- **Format:** Agent Skills spec (agentskills.io)
- **Structure:** **Flat directories** (required for Claude Code discovery)
- **Skills:**
  - `story-design/` - Lean story specifications
  - `story-plan/` - Implementation planning
  - `story-implement/` - Task execution
  - `story-review/` - Retrospective & learning
  - `research/` - Evidence-based investigation
  - `debug/` - Root cause analysis
  - `scripts/` - Shared telemetry scripts
- **Invocation:** `/story-plan`, `/debug`, `/research`, etc.
- **Related ADRs:** ADR-005 (Skills format adoption)

### Debug Skill
- **Location:** `.claude/skills/debug/SKILL.md`
- **Purpose:** Systematic root cause analysis using lean methods
- **Added:** 2026-01-31 (Jidoka application)
- **Version:** 1.0.0
- **Methods:**
  - 5 Whys - Single causal chain analysis
  - Ishikawa (Fishbone) - Multiple potential causes
  - Gemba - Go and see the actual problem
  - A3 - Complex problem documentation
- **Hooks:**
  - `PostToolUse:Write` → logs artifact creation
  - `Stop` → logs skill completion
- **Output:** `work/debug/{issue-name}/analysis.md`

### Research Skill
- **Location:** `.claude/skills/research/SKILL.md`
- **Purpose:** Evidence-based investigation for informed decisions
- **Added:** 2026-01-31 (pilot migration from kata format)
- **Version:** 1.2.0
- **Features:**
  - Full research methodology (7 steps)
  - ShuHaRi mastery levels
  - Evidence catalog templates
  - Observable Workflow hooks
- **Hooks:**
  - `PostToolUse:Write` → logs artifact creation
  - `Stop` → logs skill completion
- **References:** `references/research-prompt-template.md`

### Session Start Skill
- **Location:** `.claude/skills/session-start/SKILL.md`
- **Purpose:** Begin sessions with context loading, progress analysis, and prioritization
- **Added:** 2026-01-31 (continuity loop completion)
- **Version:** 1.0.0
- **Features:**
  - Memory loading (patterns, learnings, calibration)
  - Progress analysis (epic %, deadlines, velocity)
  - Improvement signal detection (stale items, drift, blockers)
  - Session goal proposal with rationale
  - Parking lot review
- **Hooks:**
  - `Stop` → logs skill completion
- **Output:** Session start summary with proposed focus
- **Complement:** `/session-close`

### Session Close Skill
- **Location:** `.claude/skills/session-close/SKILL.md`
- **Purpose:** Preserve learnings and maintain continuity between sessions
- **Added:** 2026-01-31 (F1.5 retrospective action item)
- **Version:** 1.0.0
- **Features:**
  - Memory file updates (memory.md, calibration.md, session-index.md)
  - Session log creation (optional)
  - Context file updates (CLAUDE.local.md)
  - Parking lot capture for tangents
  - Next session handoff
- **Hooks:**
  - `PostToolUse:Write` → logs artifact creation
  - `Stop` → logs skill completion
- **Output:** Updated `.claude/rai/` files, optional session log
- **Complement:** `/session-start`

### Telemetry Scripts
- **Location:** `.claude/skills/scripts/`
- **Purpose:** Shared scripts for Observable Workflow telemetry
- **Added:** 2026-01-31
- **Scripts:**
  - `log-skill-start.sh` - Logs skill_started event
  - `log-skill-complete.sh` - Logs skill_completed event
  - `log-artifact-created.sh` - Logs artifact_created event
- **Output:** `.raise/telemetry/events.jsonl`
- **Environment:**
  - `RAISE_SKILL_NAME` - Set by skill hooks
  - `CLAUDE_PROJECT_DIR` - Set by Claude Code

### Telemetry Storage
- **Location:** `.raise/telemetry/`
- **Purpose:** Local storage for Observable Workflow events
- **Added:** 2026-01-31
- **Files:**
  - `events.jsonl` - Skill lifecycle events (gitignored)
  - `README.md` - Documentation
- **Event Types:**
  - `skill_started` - Skill execution began
  - `skill_completed` - Skill execution finished
  - `artifact_created` - File written during skill
- **Privacy:** Local only, no PII, gitignored

### Rai's Memory System
- **Location:** `.claude/rai/`
- **Purpose:** Persistent memory for AI agent continuity across sessions
- **Added:** 2026-01-31 (F1.5 retrospective)
- **Files:**
  - `memory.md` - Accumulated learnings (patterns, process, collaboration, technical)
  - `calibration.md` - Velocity data for T-shirt size calibration
  - `session-index.md` - Quick reference to session logs
- **Usage:**
  - Read at session start to recall learnings
  - Update via `/session-close` skill
  - Reduces token waste by persisting knowledge
- **Instructions:** Documented in `.claude/RAI.md` (Session Start/End Protocols)
- **Related:** `/session-close` skill

---

## Discovery Module (E13)

> Codebase understanding for consistent reuse and drift detection

### Scanner (F13.2)
- **Location:** `src/rai_cli/discovery/scanner.py`
- **Purpose:** Extract code symbols (classes, functions, methods) from source files
- **Added:** F13.2 (Epic E13)
- **Languages:** Python (ast), TypeScript/JavaScript (tree-sitter)
- **Public API:**
  - `Symbol(BaseModel)` - Extracted code symbol with name, kind, file, line, signature, docstring
  - `ScanResult(BaseModel)` - Scan results with symbols list, files_scanned, errors
  - `scan_directory(path, language, pattern, exclude_patterns) -> ScanResult`
  - `extract_python_symbols(source, file_path) -> list[Symbol]`
  - `extract_typescript_symbols(source, file_path) -> list[Symbol]`
  - `detect_language(file_path) -> Language | None`
- **Tests:** 49 unit tests
- **Dependencies:** ast (stdlib), tree-sitter (optional for TS/JS)

### Drift Detection (F13.5)
- **Location:** `src/rai_cli/discovery/drift.py`
- **Purpose:** Detect architectural drift between new code and established patterns
- **Added:** F13.5 (Epic E13)
- **Public API:**
  - `DriftWarning(BaseModel)` - Warning with file, issue, severity, suggestion
  - `DriftSeverity` - Literal type ("info", "warning", "error")
  - `detect_drift(baseline, scanned) -> list[DriftWarning]`
- **Detection Rules:**
  1. **Location drift** - Files in unexpected directories
  2. **Naming drift** - Classes not PascalCase, functions not following patterns
  3. **Docstring drift** - Missing docs when baseline has them
- **Internal Helpers:**
  - `_normalize_path(path) -> str` - Normalize paths for comparison (strips `src/` prefix, trailing slashes). Use when comparing paths from different sources where one may be relative to project root and another relative to scan directory.
  - `_extract_directory_patterns(baseline) -> dict[str, set[str]]` - Extract valid directories by kind
  - `_extract_naming_patterns(baseline) -> dict[str, dict[str, int]]` - Extract naming prefixes with counts
  - `_check_location_drift(symbol, patterns) -> DriftWarning | None`
  - `_check_naming_drift(symbol, patterns) -> DriftWarning | None`
  - `_check_docstring_drift(symbol, has_docstrings) -> DriftWarning | None`
- **Tests:** 10 unit tests (94% coverage)
- **Dependencies:** Scanner module (Symbol)

### Discovery CLI Commands (F13.2, F13.5)
- **Location:** `src/rai_cli/cli/commands/discover.py`
- **Purpose:** CLI interface for codebase discovery and drift detection
- **Added:** F13.2 (scan, build), F13.5 (drift) - Epic E13
- **Commands:**
  - `rai discover scan [PATH]` - Scan directory for code symbols
  - `rai discover build` - Build unified graph with discovered components
  - `rai discover drift [PATH]` - Check for architectural drift
- **Options (scan):**
  - `--language/-l` - Language filter (python, typescript, javascript)
  - `--output/-o` - Output format (human, json, summary)
  - `--pattern/-p` - Glob pattern for files
  - `--exclude/-e` - Patterns to exclude
- **Options (drift):**
  - `--project-root/-r` - Project root directory
  - `--output/-o` - Output format (human, json, summary)
- **Features:**
  - Baseline size warning when <10 components
  - Exit code 0 (clean) or 1 (drift found)
  - JSON output for CI integration
- **Tests:** 16 CLI integration tests
- **Dependencies:** Scanner, Drift modules, UnifiedGraphBuilder

---

## Metadata

- **Started:** 2026-01-31 (E1 foundation)
- **Last Updated:** 2026-02-04 (E13 Discovery complete)
- **Components:** 19 (11 raise-cli + 8 skills/memory infrastructure)
- **Next:** E13 complete → E7 Onboarding

---

*Component catalog - updated per story completion*
