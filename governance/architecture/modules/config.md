---
type: module
name: config
purpose: "Settings cascade and XDG-compliant directory resolution for all raise-cli configuration"
status: current
depends_on: []
depended_by: [cli, context, memory, onboarding, telemetry]
entry_points: []
public_api:
  - "RaiseSettings"
  - "get_config_dir"
  - "get_cache_dir"
  - "get_data_dir"
  - "get_memory_dir"
  - "get_personal_dir"
  - "get_global_rai_dir"
components: 18
constraints:
  - "No internal dependencies — leaf module"
  - "Settings follow cascade: CLI args > env vars > config file > defaults"
  - "Paths follow XDG Base Directory spec on Linux/macOS"
---

## Purpose

The config module resolves where things live and what settings are active. It provides two things: **directory resolution** (where is `.raise/`? where is `~/.rai/`? where do personal files go?) and **settings management** (output format, verbosity, project root).

The directory helpers are critical because raise-cli uses a **three-tier data architecture** — global (`~/.rai/`), project (`.raise/rai/memory/`), and personal (`.raise/rai/personal/`) — and every module that reads or writes data needs to know which directory to target.

## Key Files

- **`paths.py`** — All directory resolution functions. `get_memory_dir()`, `get_personal_dir()`, and `get_global_rai_dir()` implement the three-tier model. Supports `RAI_HOME` env var override for testing.
- **`settings.py`** — `RaiseSettings` Pydantic model with the settings cascade. Singleton pattern via `get_config()`/`set_config()`.

## Dependencies

None — leaf module. Uses only Pydantic and Python stdlib.

## Conventions

- All path functions accept an optional `project_root` parameter, defaulting to cwd
- The `RAI_HOME` environment variable overrides the default `~/.rai/` location
- Settings are immutable once loaded — no runtime mutation
