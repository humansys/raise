# ADR-004: XDG Directory Compliance

**Date:** 2026-01-30
**Status:** Accepted
**Deciders:** Emilio Osorio, Rai

---

## Context

raise-cli needs to store:
- User configuration (settings, preferences)
- State files (kata execution state, resume points)
- Cache data (metrics, temporary files)

On Unix-like systems (Linux, macOS), there's a standard for where user applications store data: **XDG Base Directory Specification**.

Question: Should we follow XDG standard or use custom paths like `~/.raise/`?

---

## Decision

**Follow XDG Base Directory Specification** for all user data.

**Directory mapping:**
```
~/.config/raise/       # Configuration (RaiseSettings)
~/.local/share/raise/  # Persistent state (kata state, metrics)
~/.cache/raise/        # Temporary cache (if needed)
```

**Respect environment variables:**
- `XDG_CONFIG_HOME` → config location
- `XDG_DATA_HOME` → state/metrics location
- `XDG_CACHE_HOME` → cache location

**Implementation:**
```python
# config/paths.py
import os
from pathlib import Path

def get_config_dir() -> Path:
    xdg = os.environ.get("XDG_CONFIG_HOME")
    base = Path(xdg) if xdg else Path.home() / ".config"
    return base / "raise"

def get_data_dir() -> Path:
    xdg = os.environ.get("XDG_DATA_HOME")
    base = Path(xdg) if xdg else Path.home() / ".local" / "share"
    return base / "raise"
```

---

## Alternatives Considered

### Alternative 1: Single ~/.raise/ directory
**Rejected because:**
- Mixes concerns (config, state, cache all together)
- Not respecting user's XDG environment variables
- Makes backup/sync harder (user might want to sync config but not cache)
- Violates platform conventions (Linux/macOS best practices)

### Alternative 2: Platform-specific locations
**Rejected because:**
- More complex to maintain (different code per platform)
- XDG works fine on macOS (many tools use it)
- Windows not MVP target (defer until needed)
- Adding platform support later doesn't require breaking changes

### Alternative 3: Let users configure everything
**Rejected because:**
- Users expect sensible defaults
- Most users won't customize
- XDG provides sensible defaults already
- Advanced users can set XDG_* environment variables

---

## Consequences

### Positive
- **Standard compliance:** Follows XDG specification (respected by most Linux/macOS tools)
- **User control:** Users can set XDG_* variables to customize locations
- **Separation of concerns:** Config vs state vs cache clearly separated
- **Backup-friendly:** Users can backup `~/.config/raise/` without including cache
- **Security:** Secrets in config can have different permissions than state files
- **Tools compatibility:** Other XDG-compliant tools can find our data

### Negative
- **More directories:** Data spread across 2-3 locations instead of 1
- **Discoverability:** Users might not know where to find config files
- **Documentation burden:** Need to document where files are stored

### Mitigations
- **Discoverability:** `rai config show-paths` command to show locations
- **Documentation:** README clearly documents XDG paths with examples
- **Defaults:** Works out of box, most users don't need to know about XDG

---

## Examples

### Finding configuration
```bash
# Default location
~/.config/raise/config.toml

# Custom location (user sets XDG_CONFIG_HOME)
export XDG_CONFIG_HOME=~/my-configs
# Now: ~/my-configs/raise/config.toml
```

### State files
```bash
# Kata execution state
~/.local/share/raise/state/katas.json

# Metrics
~/.local/share/raise/metrics.json
```

### Cache (if needed)
```bash
# Temporary cache
~/.cache/raise/temp.json
```

---

## Platform Support

**MVP (v2.0):** Linux, macOS
- Both support XDG pattern
- macOS doesn't enforce XDG but respects it
- Fallback to `~/.config/`, `~/.local/share/` if XDG_* not set

**Future (post-v2.0):** Windows
- Use Windows-specific paths (AppData/Local, AppData/Roaming)
- Abstraction layer already in place (`get_config_dir()`)
- No changes needed to engines/handlers

---

## References

- XDG Base Directory Specification: https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
- Design: `governance/projects/raise-cli/design.md` (Section 3.3)
- Examples: Git, Neovim, VS Code (all use XDG on Linux)

---

*ADR-004 - XDG directory compliance*
