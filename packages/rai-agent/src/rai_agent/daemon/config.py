"""Daemon configuration with env var + YAML support.

Uses plain Pydantic BaseModel (no pydantic-settings dependency).
Env vars are loaded explicitly in __init__. YAML loading via classmethod.

Design decisions (S2.8):
  D1: Plain Pydantic — avoids pydantic-settings dependency
  D2: Env vars read in __init__ via os.environ — explicit, testable with monkeypatch
  D3: from_yaml() loads YAML then overlays env vars — env always wins
  D4: TELEGRAM_ALLOWED_USERS parsed as comma-separated ints
  D5: Validation via Pydantic validators — consistent with codebase
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path

from pydantic import BaseModel, model_validator


def _parse_allowed_users(raw: str) -> list[int]:
    """Parse comma-separated user IDs string into list of ints."""
    stripped = raw.strip()
    if not stripped:
        return []
    return [int(uid.strip()) for uid in stripped.split(",")]


def _env_overrides() -> dict[str, Any]:
    """Collect daemon config values from environment variables."""
    overrides: dict[str, Any] = {}

    if "TELEGRAM_BOT_TOKEN" in os.environ:
        overrides["telegram_bot_token"] = os.environ["TELEGRAM_BOT_TOKEN"]
    if "ANTHROPIC_API_KEY" in os.environ:
        overrides["anthropic_api_key"] = os.environ["ANTHROPIC_API_KEY"]
    if "RAI_DAEMON_HOST" in os.environ:
        overrides["host"] = os.environ["RAI_DAEMON_HOST"]
    if "RAI_DAEMON_PORT" in os.environ:
        overrides["port"] = int(os.environ["RAI_DAEMON_PORT"])
    if "RAI_DAEMON_DB_URL" in os.environ:
        overrides["db_url"] = os.environ["RAI_DAEMON_DB_URL"]
    if "TELEGRAM_ALLOWED_USERS" in os.environ:
        overrides["allowed_user_ids"] = _parse_allowed_users(
            os.environ["TELEGRAM_ALLOWED_USERS"]
        )
    if "RAI_DAEMON_BRIEFING_CHAT_ID" in os.environ:
        overrides["briefing_chat_id"] = int(
            os.environ["RAI_DAEMON_BRIEFING_CHAT_ID"]
        )
    if "RAI_DAEMON_BRIEFING_CRON" in os.environ:
        overrides["briefing_cron"] = os.environ["RAI_DAEMON_BRIEFING_CRON"]
    if "RAI_DAEMON_VERBOSE_LOGGING" in os.environ:
        overrides["verbose_logging"] = os.environ[
            "RAI_DAEMON_VERBOSE_LOGGING"
        ] in ("1", "true", "True", "yes")
    if "RAI_DAEMON_MAX_SESSIONS" in os.environ:
        overrides["max_sessions_per_chat"] = int(
            os.environ["RAI_DAEMON_MAX_SESSIONS"],
        )

    return overrides


class DaemonConfig(BaseModel):
    """Configuration for the Rai daemon.

    Required: telegram_bot_token, anthropic_api_key.
    Optional fields have sensible defaults.

    Env vars are read at construction time. Use from_yaml() for
    YAML-first config with env var overrides.
    """

    telegram_bot_token: str = ""
    anthropic_api_key: str = ""
    host: str = "127.0.0.1"
    port: int = 8000
    db_url: str = "sqlite+aiosqlite:///daemon.db"
    allowed_user_ids: list[int] = []
    briefing_chat_id: int | None = None
    briefing_cron: str = "0 8 * * *"
    verbose_logging: bool = False
    max_sessions_per_chat: int = 10

    def __init__(self, *, _skip_env: bool = False, **data: Any) -> None:
        """Load env vars, then overlay with explicit kwargs.

        Args:
            _skip_env: If True, skip env var loading (used by from_yaml
                which handles env merging itself).
        """
        if _skip_env:
            super().__init__(**data)
        else:
            env = _env_overrides()
            # Explicit kwargs win over env vars
            merged = {**env, **data}
            super().__init__(**merged)

    @model_validator(mode="after")
    def _check_required(self) -> DaemonConfig:
        """Validate that required fields are non-empty."""
        if not self.telegram_bot_token:
            msg = "telegram_bot_token is required"
            raise ValueError(msg)
        return self

    @classmethod
    def from_yaml(cls, path: Path) -> DaemonConfig:
        """Load config from a YAML file, with env vars taking priority.

        Args:
            path: Path to YAML config file.

        Returns:
            DaemonConfig with YAML values + env var overrides.

        Raises:
            FileNotFoundError: If the YAML file does not exist.
        """
        import yaml  # type: ignore[import-untyped]

        if not path.exists():
            msg = f"Config file not found: {path}"
            raise FileNotFoundError(msg)

        with path.open() as f:
            yaml_data: dict[str, Any] = yaml.safe_load(f) or {}

        # YAML as base, env vars on top (env always wins)
        env = _env_overrides()
        merged = {**yaml_data, **env}

        # Skip env loading in __init__ since we already merged here
        return cls(_skip_env=True, **merged)
