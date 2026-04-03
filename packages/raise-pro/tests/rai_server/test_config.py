"""Tests for raise_server.config — ServerConfig via pydantic-settings."""

from __future__ import annotations

import pytest
from pydantic import ValidationError
from raise_server.config import ServerConfig

_DB_URL = "postgresql+asyncpg://u:p@h/db"


class TestServerConfigDefaults:
    """ServerConfig loads with sensible defaults when database_url is provided."""

    def test_loads_with_database_url(self) -> None:
        config = ServerConfig(database_url=_DB_URL)
        assert config.database_url == _DB_URL

    def test_default_log_level(self) -> None:
        config = ServerConfig(database_url=_DB_URL)
        assert config.log_level == "INFO"

    def test_default_host_and_port(self) -> None:
        config = ServerConfig(database_url=_DB_URL)
        assert config.host == "0.0.0.0"
        assert config.port == 8000


class TestServerConfigOverrides:
    """Explicit values override defaults."""

    def test_override_log_level(self) -> None:
        config = ServerConfig(database_url=_DB_URL, log_level="DEBUG")
        assert config.log_level == "DEBUG"

    def test_override_port(self) -> None:
        config = ServerConfig(database_url=_DB_URL, port=9000)
        assert config.port == 9000


class TestServerConfigFromEnv:
    """Environment variables are read with RAI_ prefix."""

    def test_reads_database_url_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("RAI_DATABASE_URL", _DB_URL)
        config = ServerConfig()  # type: ignore[call-arg]
        assert config.database_url == _DB_URL

    def test_env_overrides_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("RAI_DATABASE_URL", _DB_URL)
        monkeypatch.setenv("RAI_LOG_LEVEL", "WARNING")
        config = ServerConfig()  # type: ignore[call-arg]
        assert config.log_level == "WARNING"


class TestServerConfigValidation:
    """Missing required fields fail fast."""

    def test_missing_database_url_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("RAI_DATABASE_URL", raising=False)
        monkeypatch.delenv("DATABASE_URL", raising=False)
        with pytest.raises(ValidationError):
            ServerConfig()  # type: ignore[call-arg]
