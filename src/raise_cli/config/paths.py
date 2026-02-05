"""Path helpers for raise-cli.

Includes:
- XDG Base Directory paths (global user config/cache/data)
- Per-project directory structure constants

Directory Structure (per-project):
    .raise/                    # RaiSE framework presence
    ├── manifest.yaml          # Project metadata
    ├── config.yaml            # Project configuration
    ├── graph/                 # Context graph cache
    └── rai/                   # AI partner state
        ├── identity/          # Rai's identity
        ├── memory/            # Patterns, calibration, sessions
        └── telemetry/         # Signals
"""

from __future__ import annotations

import os
from pathlib import Path

# =============================================================================
# Per-Project Directory Constants
# =============================================================================

# Root directory for RaiSE in a project
RAISE_PROJECT_DIR = ".raise"

# Subdirectory for Rai (AI partner) state within .raise/
RAI_SUBDIR = "rai"

# Common subdirectories
MEMORY_SUBDIR = "memory"
TELEMETRY_SUBDIR = "telemetry"
IDENTITY_SUBDIR = "identity"
GRAPH_SUBDIR = "graph"

# File names
MANIFEST_FILE = "manifest.yaml"
CONFIG_FILE = "config.yaml"
PATTERNS_FILE = "patterns.jsonl"
CALIBRATION_FILE = "calibration.jsonl"
SESSIONS_DIR = "sessions"
SIGNALS_FILE = "signals.jsonl"


def get_raise_dir(project_root: Path | None = None) -> Path:
    """Get the .raise/ directory for a project.

    Args:
        project_root: Project root path. Defaults to current directory.

    Returns:
        Path to .raise/ directory.
    """
    root = project_root or Path.cwd()
    return root / RAISE_PROJECT_DIR


def get_rai_dir(project_root: Path | None = None) -> Path:
    """Get the .raise/rai/ directory for AI partner state.

    Args:
        project_root: Project root path. Defaults to current directory.

    Returns:
        Path to .raise/rai/ directory.
    """
    return get_raise_dir(project_root) / RAI_SUBDIR


def get_memory_dir(project_root: Path | None = None) -> Path:
    """Get the .raise/rai/memory/ directory.

    Args:
        project_root: Project root path. Defaults to current directory.

    Returns:
        Path to memory directory.
    """
    return get_rai_dir(project_root) / MEMORY_SUBDIR


def get_telemetry_dir(project_root: Path | None = None) -> Path:
    """Get the .raise/rai/telemetry/ directory.

    Args:
        project_root: Project root path. Defaults to current directory.

    Returns:
        Path to telemetry directory.
    """
    return get_rai_dir(project_root) / TELEMETRY_SUBDIR


def get_graph_dir(project_root: Path | None = None) -> Path:
    """Get the .raise/graph/ directory.

    Args:
        project_root: Project root path. Defaults to current directory.

    Returns:
        Path to graph directory.
    """
    return get_raise_dir(project_root) / GRAPH_SUBDIR


# =============================================================================
# Global User Directory (XDG)
# =============================================================================

# Global Rai directory in user home (for developer profile)
GLOBAL_RAI_DIR = ".rai"


def _get_xdg_dir(env_var: str, fallback: str) -> Path:
    """Get an XDG directory for raise-cli.

    Args:
        env_var: XDG environment variable name (e.g., "XDG_CONFIG_HOME").
        fallback: Fallback path relative to home (e.g., ".config").

    Returns:
        Path to the raise subdirectory within the XDG directory.
    """
    xdg_value = os.environ.get(env_var)
    base = Path(xdg_value) if xdg_value else Path.home() / fallback
    return base / "raise"


def get_config_dir() -> Path:
    """Get the XDG config directory for raise-cli.

    Returns:
        Path to config directory (e.g., ~/.config/raise/ or $XDG_CONFIG_HOME/raise/)

    Example:
        >>> config_dir = get_config_dir()
        >>> config_file = config_dir / "config.toml"
    """
    return _get_xdg_dir("XDG_CONFIG_HOME", ".config")


def get_cache_dir() -> Path:
    """Get the XDG cache directory for raise-cli.

    Returns:
        Path to cache directory (e.g., ~/.cache/raise/ or $XDG_CACHE_HOME/raise/)

    Example:
        >>> cache_dir = get_cache_dir()
        >>> cache_file = cache_dir / "downloaded_katas.json"
    """
    return _get_xdg_dir("XDG_CACHE_HOME", ".cache")


def get_data_dir() -> Path:
    """Get the XDG data directory for raise-cli.

    Returns:
        Path to data directory (e.g., ~/.local/share/raise/ or $XDG_DATA_HOME/raise/)

    Example:
        >>> data_dir = get_data_dir()
        >>> state_file = data_dir / "session_state.json"
    """
    return _get_xdg_dir("XDG_DATA_HOME", ".local/share")
