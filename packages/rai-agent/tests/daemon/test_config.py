# pyright: reportPrivateUsage=false, reportUnusedFunction=false
"""Tests for DaemonConfig — env-based configuration with YAML fallback."""

from __future__ import annotations

import textwrap
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path

from rai_agent.daemon.config import DaemonConfig

_CONFIG_ENV_VARS = [
    "TELEGRAM_BOT_TOKEN",
    "ANTHROPIC_API_KEY",
    "RAI_DAEMON_HOST",
    "RAI_DAEMON_PORT",
    "RAI_DAEMON_DB_URL",
    "TELEGRAM_ALLOWED_USERS",
    "RAI_DAEMON_BRIEFING_CHAT_ID",
    "RAI_DAEMON_BRIEFING_CRON",
    "RAI_DAEMON_VERBOSE_LOGGING",
    "RAI_DAEMON_MAX_SESSIONS",
]


@pytest.fixture(autouse=True)
def _clean_config_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Remove all daemon config env vars before each test for isolation."""
    for var in _CONFIG_ENV_VARS:
        monkeypatch.delenv(var, raising=False)


class TestDaemonConfigDefaults:
    """DaemonConfig optional fields have sensible defaults."""

    def test_host_defaults_to_localhost(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "tok")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "key")
        cfg = DaemonConfig()
        assert cfg.host == "127.0.0.1"

    def test_port_defaults_to_8000(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "tok")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "key")
        cfg = DaemonConfig()
        assert cfg.port == 8000

    def test_db_url_defaults_to_sqlite(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "tok")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "key")
        cfg = DaemonConfig()
        assert cfg.db_url == "sqlite+aiosqlite:///daemon.db"

    def test_allowed_user_ids_defaults_to_empty(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "tok")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "key")
        cfg = DaemonConfig()
        assert cfg.allowed_user_ids == []


class TestDaemonConfigEnvVars:
    """DaemonConfig loads values from environment variables."""

    def test_loads_required_fields_from_env(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "my-token")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "my-key")
        cfg = DaemonConfig()
        assert cfg.telegram_bot_token == "my-token"
        assert cfg.anthropic_api_key == "my-key"

    def test_loads_optional_fields_from_env(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "tok")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "key")
        monkeypatch.setenv("RAI_DAEMON_HOST", "0.0.0.0")
        monkeypatch.setenv("RAI_DAEMON_PORT", "9000")
        monkeypatch.setenv("RAI_DAEMON_DB_URL", "postgresql://localhost/rai")
        cfg = DaemonConfig()
        assert cfg.host == "0.0.0.0"
        assert cfg.port == 9000
        assert cfg.db_url == "postgresql://localhost/rai"

    def test_comma_separated_allowed_user_ids(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "tok")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "key")
        monkeypatch.setenv("TELEGRAM_ALLOWED_USERS", "111,222,333")
        cfg = DaemonConfig()
        assert cfg.allowed_user_ids == [111, 222, 333]

    def test_single_allowed_user_id(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "tok")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "key")
        monkeypatch.setenv("TELEGRAM_ALLOWED_USERS", "42")
        cfg = DaemonConfig()
        assert cfg.allowed_user_ids == [42]

    def test_empty_allowed_users_string(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "tok")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "key")
        monkeypatch.setenv("TELEGRAM_ALLOWED_USERS", "")
        cfg = DaemonConfig()
        assert cfg.allowed_user_ids == []


class TestDaemonConfigValidation:
    """DaemonConfig validates required fields."""

    def test_missing_telegram_token_raises(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("ANTHROPIC_API_KEY", "key")
        monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
        with pytest.raises(ValueError):
            DaemonConfig()

    def test_missing_anthropic_key_does_not_raise(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """anthropic_api_key is optional — ClaudeRuntime uses Claude Code CLI."""
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "tok")
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        cfg = DaemonConfig()
        assert cfg.anthropic_api_key == ""


class TestDaemonConfigYaml:
    """DaemonConfig.from_yaml() loads from YAML files."""

    def test_loads_from_yaml(self, tmp_path: Path) -> None:
        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text(
            textwrap.dedent("""\
            telegram_bot_token: yaml-token
            anthropic_api_key: yaml-key
            host: "0.0.0.0"
            port: 9999
            """)
        )
        cfg = DaemonConfig.from_yaml(yaml_file)
        assert cfg.telegram_bot_token == "yaml-token"
        assert cfg.anthropic_api_key == "yaml-key"
        assert cfg.host == "0.0.0.0"
        assert cfg.port == 9999

    def test_env_vars_override_yaml(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text(
            textwrap.dedent("""\
            telegram_bot_token: yaml-token
            anthropic_api_key: yaml-key
            host: "192.168.1.1"
            """)
        )
        monkeypatch.setenv("RAI_DAEMON_HOST", "10.0.0.1")
        cfg = DaemonConfig.from_yaml(yaml_file)
        assert cfg.host == "10.0.0.1"
        # YAML values still used when env not set
        assert cfg.telegram_bot_token == "yaml-token"

    def test_yaml_with_allowed_users(self, tmp_path: Path) -> None:
        yaml_file = tmp_path / "config.yaml"
        yaml_file.write_text(
            textwrap.dedent("""\
            telegram_bot_token: tok
            anthropic_api_key: key
            allowed_user_ids:
              - 100
              - 200
            """)
        )
        cfg = DaemonConfig.from_yaml(yaml_file)
        assert cfg.allowed_user_ids == [100, 200]

    def test_nonexistent_yaml_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            DaemonConfig.from_yaml(tmp_path / "nope.yaml")


class TestDaemonConfigBriefing:
    """DaemonConfig briefing fields have correct defaults and env loading."""

    def test_briefing_chat_id_defaults_to_none(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "tok")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "key")
        cfg = DaemonConfig()
        assert cfg.briefing_chat_id is None

    def test_briefing_cron_defaults_to_8am(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "tok")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "key")
        cfg = DaemonConfig()
        assert cfg.briefing_cron == "0 8 * * *"

    def test_env_var_briefing_chat_id(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "tok")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "key")
        monkeypatch.setenv("RAI_DAEMON_BRIEFING_CHAT_ID", "12345")
        cfg = DaemonConfig()
        assert cfg.briefing_chat_id == 12345

    def test_env_var_briefing_cron(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "tok")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "key")
        monkeypatch.setenv("RAI_DAEMON_BRIEFING_CRON", "30 9 * * 1-5")
        cfg = DaemonConfig()
        assert cfg.briefing_cron == "30 9 * * 1-5"


class TestDaemonConfigVerboseLogging:
    """DaemonConfig verbose_logging flag is opt-in via field and env var."""

    def test_verbose_logging_default_false(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "tok")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "key")
        cfg = DaemonConfig()
        assert cfg.verbose_logging is False

    def test_verbose_logging_from_env(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "tok")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "key")
        monkeypatch.setenv("RAI_DAEMON_VERBOSE_LOGGING", "1")
        cfg = DaemonConfig()
        assert cfg.verbose_logging is True


class TestDaemonConfigMaxSessions:
    """T6: max_sessions_per_chat config field + env override."""

    def test_default_is_10(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "tok")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "key")
        cfg = DaemonConfig()
        assert cfg.max_sessions_per_chat == 10

    def test_env_override(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "tok")
        monkeypatch.setenv("ANTHROPIC_API_KEY", "key")
        monkeypatch.setenv("RAI_DAEMON_MAX_SESSIONS", "5")
        cfg = DaemonConfig()
        assert cfg.max_sessions_per_chat == 5
