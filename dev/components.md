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

### Global Options (F1.2, updated F1.4)
- **Location:** `src/raise_cli/cli/main.py`
- **Purpose:** Global options for all commands (format, verbosity, quiet)
- **Added:** F1.2 (Epic E1), integrated with RaiseSettings in F1.4
- **API:**
  - `--format/-f` (human|json|table)
  - `--verbose/-v` (count, up to -vvv)
  - `--quiet/-q` (suppress non-error output)
- **Storage:**
  - `ctx.obj["settings"]` (RaiseSettings instance) - primary
  - `ctx.obj["format"]`, `ctx.obj["verbosity"]`, `ctx.obj["quiet"]` - backward compat
- **Dependencies:** `RaiseSettings` (F1.3)

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

## Output Formatters (Core Layer)

### [No formatters yet - F1.5 will add human/json/table formatters]

---

## Utilities (Core Layer)

### [No utilities yet - F1.6 will add subprocess wrappers]

---

## Metadata

- **Started:** 2026-01-31 (E1 foundation)
- **Last Updated:** 2026-01-31 (F1.3 complete)
- **Components:** 4 (Global Options, RaiseSettings, XDG helpers, TomlConfigSource)
- **Next:** F1.4 Exception Hierarchy

---

*Component catalog - updated per feature completion*
