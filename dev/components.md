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

### [No engines yet - E2 will add KataEngine, E3 will add GateEngine]

---

## Handlers (Application Layer)

> Orchestration and use case coordination

### [No handlers yet - E2 will add KataHandler, E3 will add GateHandler]

---

## CLI Commands (Presentation Layer)

> User-facing commands

### Global Options (F1.2, updated F1.3)
- **Location:** `src/raise_cli/cli/main.py`
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
- **Location:** `src/raise_cli/cli/error_handler.py`
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

### [No schemas yet - will be added as engines are built]

---

## Configuration (Core Layer)

### RaiseSettings (F1.3)
- **Location:** `src/raise_cli/config/settings.py`
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
- **Location:** `src/raise_cli/config/paths.py`
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
- **Location:** `src/raise_cli/config/settings.py` (private class)
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
- **Location:** `src/raise_cli/exceptions.py`
- **Purpose:** Centralized exceptions with exit codes, error codes, hints
- **Added:** F1.4 (Epic E1)
- **Export:** All exceptions exported from `raise_cli` package root
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
- **Location:** `src/raise_cli/output/console.py`
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

### [No utilities yet - F1.6 will add subprocess wrappers]

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
  - `feature-design/` - Lean feature specifications
  - `feature-plan/` - Implementation planning
  - `feature-implement/` - Task execution
  - `feature-review/` - Retrospective & learning
  - `research/` - Evidence-based investigation
  - `debug/` - Root cause analysis
  - `scripts/` - Shared telemetry scripts
- **Invocation:** `/feature-plan`, `/debug`, `/research`, etc.
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

---

## Metadata

- **Started:** 2026-01-31 (E1 foundation)
- **Last Updated:** 2026-01-31 (F1.5 Output Module)
- **Components:** 12 (7 raise-cli + 5 skills infrastructure)
- **Next:** F1.6 Core Utilities

---

*Component catalog - updated per feature completion*
