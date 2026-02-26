"""Server configuration via pydantic-settings.

All settings read from environment variables with RAI_ prefix.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings


class ServerConfig(BaseSettings):
    """RaiSE server configuration. All fields map to RAI_* env vars."""

    database_url: str
    api_key_hash_algorithm: str = "sha256"
    log_level: str = "INFO"
    host: str = "0.0.0.0"
    port: int = 8000

    model_config = {"env_prefix": "RAI_"}
