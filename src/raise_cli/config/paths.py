"""XDG Base Directory compliant path helpers for raise-cli.

Follows XDG Base Directory Specification:
https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
"""

from __future__ import annotations

import os
from pathlib import Path


def get_config_dir() -> Path:
    """Get the XDG config directory for raise-cli.

    Returns the directory where user configuration files should be stored.
    Respects XDG_CONFIG_HOME environment variable if set.

    Returns:
        Path to config directory (e.g., ~/.config/raise/ or $XDG_CONFIG_HOME/raise/)

    Example:
        >>> config_dir = get_config_dir()
        >>> config_file = config_dir / "config.toml"
    """
    xdg_config = os.environ.get("XDG_CONFIG_HOME")
    base = Path(xdg_config) if xdg_config else Path.home() / ".config"
    return base / "raise"


def get_cache_dir() -> Path:
    """Get the XDG cache directory for raise-cli.

    Returns the directory where cached data should be stored.
    Respects XDG_CACHE_HOME environment variable if set.

    Returns:
        Path to cache directory (e.g., ~/.cache/raise/ or $XDG_CACHE_HOME/raise/)

    Example:
        >>> cache_dir = get_cache_dir()
        >>> cache_file = cache_dir / "downloaded_katas.json"
    """
    xdg_cache = os.environ.get("XDG_CACHE_HOME")
    base = Path(xdg_cache) if xdg_cache else Path.home() / ".cache"
    return base / "raise"


def get_data_dir() -> Path:
    """Get the XDG data directory for raise-cli.

    Returns the directory where user data files should be stored.
    Respects XDG_DATA_HOME environment variable if set.

    Returns:
        Path to data directory (e.g., ~/.local/share/raise/ or $XDG_DATA_HOME/raise/)

    Example:
        >>> data_dir = get_data_dir()
        >>> state_file = data_dir / "session_state.json"
    """
    xdg_data = os.environ.get("XDG_DATA_HOME")
    base = Path(xdg_data) if xdg_data else Path.home() / ".local" / "share"
    return base / "raise"
