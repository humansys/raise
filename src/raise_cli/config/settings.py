"""Configuration settings for raise-cli using Pydantic Settings.

Implements configuration cascade with proper precedence:
1. CLI arguments (highest priority)
2. Environment variables (RAISE_* prefix)
3. Project config (pyproject.toml)
4. User config (~/.config/raise/config.toml)
5. Defaults (lowest priority)
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RaiseSettings(BaseSettings):
    """Configuration settings for raise-cli with proper cascade precedence.

    Settings are loaded in order of precedence (highest to lowest):
    1. Constructor arguments (from CLI)
    2. Environment variables (RAISE_* prefix)
    3. Project pyproject.toml [tool.raise] section
    4. User config file (~/.config/raise/config.toml)
    5. Field defaults

    Example:
        >>> # Load with defaults and env vars
        >>> settings = RaiseSettings()
        >>> # Override specific values (e.g., from CLI)
        >>> settings = RaiseSettings(output_format="json", verbosity=2)
    """

    model_config = SettingsConfigDict(
        env_prefix="RAISE_",
        env_file=".env",
        toml_file="pyproject.toml",
        extra="ignore",
    )

    # Output settings
    output_format: Literal["human", "json", "table"] = Field(
        default="human",
        description="Output format for CLI commands",
    )
    color: bool = Field(
        default=True,
        description="Enable colored output",
    )
    verbosity: int = Field(
        default=0,
        ge=-1,
        le=3,
        description="Verbosity level: -1=quiet, 0=normal, 1-3=verbose",
    )

    # Paths (project-level)
    raise_dir: Path = Field(
        default=Path(".raise"),
        description="Directory containing RaiSE framework files",
    )
    governance_dir: Path = Field(
        default=Path("governance"),
        description="Directory containing governance artifacts",
    )
    work_dir: Path = Field(
        default=Path("work"),
        description="Directory containing active work",
    )

    # External tools (graceful degradation handled by core utilities)
    ast_grep_path: str | None = Field(
        default=None,
        description="Path to ast-grep binary (auto-detected if None)",
    )
    ripgrep_path: str | None = Field(
        default=None,
        description="Path to ripgrep binary (auto-detected if None)",
    )

    # Feature flags
    interactive: bool = Field(
        default=False,
        description="Enable interactive prompts",
    )
