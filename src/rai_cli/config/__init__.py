"""Configuration module for raise-cli.

Provides configuration settings and XDG-compliant directory helpers.
"""

from __future__ import annotations

from rai_cli.config.paths import get_cache_dir, get_config_dir, get_data_dir
from rai_cli.config.settings import RaiSettings

__all__ = ["get_config_dir", "get_cache_dir", "get_data_dir", "RaiSettings"]
