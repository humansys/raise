"""XDG Base Directory compliant path helpers for raise-cli.

Follows XDG Base Directory Specification:
https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
"""

from __future__ import annotations

import os
from pathlib import Path


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
