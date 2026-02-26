"""Tests for rai_server.config — ServerConfig via pydantic-settings."""

from __future__ import annotations

import pytest


class TestServerConfigDefaults:
    """ServerConfig loads with sensible defaults when DATABASE_URL is set."""

    def test_loads_with_database_url(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("RAI_DATABASE_URL", "postgresql+asyncpg://u:p@h/db")
        from rai_server.config import ServerConfig

        config = ServerConfig()
        assert config.database_url == "postgresql+asyncpg://u:p@h/db"

    def test_default_log_level(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("RAI_DATABASE_URL", "postgresql+asyncpg://u:p@h/db")
        from rai_server.config import ServerConfig

        config = ServerConfig()
        assert config.log_level == "INFO"

    def test_default_host_and_port(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("RAI_DATABASE_URL", "postgresql+asyncpg://u:p@h/db")
        from rai_server.config import ServerConfig

        config = ServerConfig()
        assert config.host == "0.0.0.0"
        assert config.port == 8000

    def test_default_hash_algorithm(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("RAI_DATABASE_URL", "postgresql+asyncpg://u:p@h/db")
        from rai_server.config import ServerConfig

        config = ServerConfig()
        assert config.api_key_hash_algorithm == "sha256"


class TestServerConfigOverrides:
    """Environment variables override defaults."""

    def test_override_log_level(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("RAI_DATABASE_URL", "postgresql+asyncpg://u:p@h/db")
        monkeypatch.setenv("RAI_LOG_LEVEL", "DEBUG")
        from rai_server.config import ServerConfig

        config = ServerConfig()
        assert config.log_level == "DEBUG"

    def test_override_port(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("RAI_DATABASE_URL", "postgresql+asyncpg://u:p@h/db")
        monkeypatch.setenv("RAI_PORT", "9000")
        from rai_server.config import ServerConfig

        config = ServerConfig()
        assert config.port == 9000


class TestServerConfigValidation:
    """Missing required fields fail fast."""

    def test_missing_database_url_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("RAI_DATABASE_URL", raising=False)
        # Also clear any leftover env that pydantic-settings might pick up
        monkeypatch.delenv("DATABASE_URL", raising=False)
        from rai_server.config import ServerConfig

        with pytest.raises(Exception):  # ValidationError
            ServerConfig()
