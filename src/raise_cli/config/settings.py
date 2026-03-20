"""Configuration settings for raise-cli using Pydantic Settings.

Implements configuration cascade with proper precedence:
1. CLI arguments (highest priority)
2. Environment variables (RAI_* prefix)
3. Project config (pyproject.toml)
4. User config (~/.config/rai/config.toml)
5. Defaults (lowest priority)
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any, Literal

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

if sys.version_info >= (3, 11):  # noqa: UP036
    import tomllib
else:
    import tomli as tomllib

from raise_cli.config.paths import get_config_dir

logger = logging.getLogger(__name__)


class TomlConfigSource(PydanticBaseSettingsSource):
    """Custom settings source for TOML configuration files."""

    def __init__(
        self,
        settings_cls: type[BaseSettings],
        toml_file: Path | None = None,
        toml_table: str = "rai",
    ) -> None:
        """Initialize TOML config source.

        Args:
            settings_cls: The settings class
            toml_file: Path to TOML file (None = auto-detect)
            toml_table: Table name in TOML file (default: "rai")
        """
        super().__init__(settings_cls)
        self.toml_file = toml_file
        self.toml_table = toml_table

    def get_field_value(self, field: Any, field_name: str) -> tuple[Any, str, bool]:
        """Get field value from TOML file."""
        # Not used in newer pydantic-settings
        return None, "", False

    def __call__(self) -> dict[str, Any]:
        """Load settings from TOML file."""
        if self.toml_file is None or not self.toml_file.exists():
            return {}

        try:
            with open(self.toml_file, "rb") as f:
                data = tomllib.load(f)

            # Handle pyproject.toml with [tool.rai] section
            if self.toml_file.name == "pyproject.toml":
                return data.get("tool", {}).get(self.toml_table, {})
            # Handle user config with [rai] section
            return data.get(self.toml_table, {})
        except Exception as e:
            logger.debug("Failed to parse TOML config %s: %s", self.toml_file, e)
            return {}


class RaiSettings(BaseSettings):
    """Configuration settings for raise-cli with proper cascade precedence.

    Settings are loaded in order of precedence (highest to lowest):
    1. Constructor arguments (from CLI)
    2. Environment variables (RAI_* prefix)
    3. Project pyproject.toml [tool.rai] section
    4. User config file (~/.config/rai/config.toml)
    5. Field defaults

    Example:
        >>> # Load with defaults and env vars
        >>> settings = RaiSettings()
        >>> # Override specific values (e.g., from CLI)
        >>> settings = RaiSettings(output_format="json", verbosity=2)
    """

    model_config = SettingsConfigDict(
        env_prefix="RAI_",
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

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,  # noqa: ARG003 -- required by Pydantic BaseSettings override
        file_secret_settings: PydanticBaseSettingsSource,  # noqa: ARG003 -- required by Pydantic BaseSettings override
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Customize settings sources to include TOML files.

        Order (highest to lowest priority):
        1. init_settings (constructor args / CLI)
        2. env_settings (environment variables)
        3. project_toml (pyproject.toml)
        4. user_toml (~/.config/rai/config.toml)
        5. file defaults (from Field definitions)
        """
        # Project-level config
        project_toml = TomlConfigSource(
            settings_cls, toml_file=Path("pyproject.toml"), toml_table="rai"
        )

        # User-level config
        user_config_file = get_config_dir() / "config.toml"
        user_toml = TomlConfigSource(
            settings_cls, toml_file=user_config_file, toml_table="rai"
        )

        return (
            init_settings,  # CLI args (highest priority)
            env_settings,  # Environment variables
            project_toml,  # pyproject.toml
            user_toml,  # User config
            # Field defaults are always last (implicit)
        )
