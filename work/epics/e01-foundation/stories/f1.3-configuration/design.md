---
story_id: "F1.3"
title: "Configuration System"
epic_ref: "E1 Core Foundation"
story_points: 5
complexity: "moderate"
status: "draft"
version: "1.0"
created: "2026-01-31"
updated: "2026-01-31"
template: "lean-feature-spec-v2"
---

# Feature: Configuration System

> **Epic**: E1 - Core Foundation
> **Complexity**: moderate | **SP**: 5

---

## 1. What & Why

**Problem**: raise-cli needs a centralized configuration system that allows users to set preferences at multiple levels (CLI args, environment, project file, user file) without conflicts or confusion about which value takes precedence.

**Value**: Users can configure raise-cli behavior consistently across different contexts (local dev, CI, team projects) with clear, predictable precedence rules. Reduces friction and supports both interactive and automated use cases.

---

## 2. Approach

**How we'll solve it** (high-level):

Implement Pydantic Settings-based configuration system with standard cascade precedence (CLI > env > project config > user config > defaults). Use XDG directory standard for user config location to be a good Unix citizen.

**Components affected**:
- **src/rai_cli/config/settings.py**: Create `RaiseSettings` class (Pydantic BaseSettings)
- **src/rai_cli/config/paths.py**: Create XDG directory helpers (`get_config_dir()`, `get_cache_dir()`, `get_data_dir()`)
- **src/rai_cli/cli/main.py**: Integrate settings with CLI context
- **tests/config/**: Create test suite for cascade precedence and XDG paths

---

## 3. Interface / Examples

> **IMPORTANT**: These examples show the expected behavior of the configuration cascade

### API Usage

```python
# In CLI code or application code
from raise_cli.config import RaiseSettings

# Default usage - reads from all sources with proper cascade
settings = RaiseSettings()

# Override specific values (e.g., from CLI args)
settings = RaiseSettings(output_format="json", verbosity=2)

# Access settings
print(settings.output_format)  # "json"
print(settings.raise_dir)      # Path(".raise")
```

### Configuration Cascade Behavior

```python
# Priority 1: CLI arguments (passed to RaiseSettings constructor)
settings = RaiseSettings(output_format="json")
assert settings.output_format == "json"

# Priority 2: Environment variables
# $ export RAISE_OUTPUT_FORMAT=table
settings = RaiseSettings()  # No CLI override
assert settings.output_format == "table"

# Priority 3: Project config (pyproject.toml)
# [tool.raise]
# output_format = "human"
settings = RaiseSettings()  # No CLI or env
assert settings.output_format == "human"

# Priority 4: User config (~/.config/raise/config.toml)
# [raise]
# output_format = "json"
settings = RaiseSettings()  # No CLI, env, or project config
assert settings.output_format == "json"

# Priority 5: Defaults
settings = RaiseSettings()  # No overrides anywhere
assert settings.output_format == "human"  # hardcoded default
```

### XDG Directory Helpers

```python
from raise_cli.config.paths import get_config_dir, get_cache_dir, get_data_dir

# Standard XDG locations
config_dir = get_config_dir()  # ~/.config/raise/ (or $XDG_CONFIG_HOME/raise/)
cache_dir = get_cache_dir()    # ~/.cache/raise/ (or $XDG_CACHE_HOME/raise/)
data_dir = get_data_dir()      # ~/.local/share/raise/ (or $XDG_DATA_HOME/raise/)

# Respects XDG environment variables
# $ export XDG_CONFIG_HOME=/custom/config
config_dir = get_config_dir()  # /custom/config/raise/
```

### Data Structures

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path
from typing import Literal

class RaiseSettings(BaseSettings):
    """Configuration for raise-cli with proper precedence."""

    model_config = SettingsConfigDict(
        env_prefix="RAISE_",
        env_file=".env",
        toml_file="pyproject.toml",
        extra="ignore"
    )

    # Output settings
    output_format: Literal["human", "json", "table"] = "human"
    color: bool = True
    verbosity: int = Field(default=0, ge=-1, le=3)  # -1=quiet, 0=normal, 1-3=verbose

    # Paths (project-level)
    raise_dir: Path = Path(".raise")
    governance_dir: Path = Path("governance")
    work_dir: Path = Path("work")

    # External tools (graceful degradation handled elsewhere)
    ast_grep_path: str | None = None
    ripgrep_path: str | None = None

    # Feature flags
    interactive: bool = False
```

### Config File Formats

```toml
# pyproject.toml (project-level)
[tool.raise]
output_format = "human"
color = true
verbosity = 0
raise_dir = ".raise"

# ~/.config/raise/config.toml (user-level)
[raise]
output_format = "json"  # Override for CI/scripts
color = false
verbosity = -1
```

---

## 4. Acceptance Criteria

> **MUST** = Required for feature completion
> **SHOULD** = Nice-to-have, defer if time-constrained
> **MUST NOT** = Explicit anti-requirements

### Must Have

- [ ] `RaiseSettings` class implemented with Pydantic BaseSettings
- [ ] Configuration cascade works correctly: CLI > env > pyproject.toml > user config > defaults
- [ ] XDG directory helpers (`get_config_dir()`, `get_cache_dir()`, `get_data_dir()`) respect XDG env vars
- [ ] All settings fields from design spec present with correct types and defaults
- [ ] Test coverage >90% on configuration cascade precedence
- [ ] Tests verify XDG environment variable override behavior
- [ ] CLI integration: `ctx.obj` populated with `RaiseSettings` instance
- [ ] Component catalog updated with `RaiseSettings` and XDG helpers

### Should Have

- [ ] User config file auto-creation on first run (with commented defaults)
- [ ] Validation errors provide clear messages (e.g., "Invalid output_format: 'xml'. Must be one of: human, json, table")

### Must NOT

- [ ] **DO NOT** store secrets or credentials in config files (only user preferences)
- [ ] **DO NOT** create config directories without user consent (lazy creation on write, not on read)
- [ ] **DO NOT** fail hard if user config file is malformed (warn and fall back to defaults)

---

## References

**Related ADRs**:
- [ADR-004: XDG Directory Standard](../../../dev/decisions/framework/004-xdg-directories.md)
- [ADR-002: Pydantic for Data Validation](../../../dev/decisions/framework/002-pydantic-validation.md)

**Related Features**:
- F1.2: CLI Skeleton (provides `ctx.obj` infrastructure)
- F1.4: Exception Hierarchy (will use settings for error formatting)
- F1.5: Output Module (will use settings for format selection)

**External Docs**:
- [Pydantic Settings Documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) - Settings precedence behavior
- [XDG Base Directory Specification](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html) - Directory standards

**Dependencies**:
- F1.2 CLI Skeleton must be complete (provides CLI context infrastructure)
- Pydantic v2 and pydantic-settings installed

---

**Template Version**: 2.0 (Lean Feature Spec)
**Created**: 2026-01-31
**Last Updated**: 2026-01-31
**Based on**: Research `work/research/lean-feature-specs/` + Project Design Section 3

---

## Design Notes

### Complexity Assessment

| Criterion | Rating | Notes |
|-----------|--------|-------|
| Components touched | 3-4 | settings.py, paths.py, main.py, tests |
| Story points | 5 | Moderate |
| External integrations | 1 | Pydantic Settings |
| Algorithm complexity | Moderate | Cascade precedence logic |
| State management | Stateless | Configuration is read-only after init |
| Error scenarios | 2-3 | Malformed config, missing paths, invalid values |

**Conclusion**: MODERATE complexity → Core sections + minimal optional content

### Why This Approach

**Pydantic Settings chosen because**:
- Handles cascade precedence automatically (env vars, TOML files)
- Type validation built-in (prevents invalid config values)
- Consistent with existing Pydantic usage (ADR-002)
- Well-documented, stable, widely used

**XDG compliance chosen because**:
- Unix/Linux best practice (ADR-004)
- Keeps user home directory clean
- Standard expectations for CLI tools
- Cross-platform with graceful fallbacks

### Implementation Guidance for AI

**IMPORTANT**: Focus on getting the cascade precedence correct. This is the most critical aspect.

**MUST**: Test all five precedence levels in integration tests, not just unit tests.

**DO NOT**: Add complex config merging logic - Pydantic Settings handles this. Keep it simple.
