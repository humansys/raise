"""Tests for Confluence client wrapper (S1051.1 / RAISE-1054)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError


# ── T1: Exceptions + Config ──────────────────────────────────────────


class TestConfluenceExceptions:
    """Exception hierarchy: 3 classes, isinstance-based."""

    def test_base_error_has_message(self) -> None:
        from raise_cli.adapters.confluence_exceptions import ConfluenceError

        err = ConfluenceError("something broke")
        assert err.message == "something broke"
        assert str(err) == "something broke"

    def test_auth_error_is_confluence_error(self) -> None:
        from raise_cli.adapters.confluence_exceptions import (
            ConfluenceAuthError,
            ConfluenceError,
        )

        err = ConfluenceAuthError("bad token")
        assert isinstance(err, ConfluenceError)
        assert err.message == "bad token"

    def test_not_found_error_is_confluence_error(self) -> None:
        from raise_cli.adapters.confluence_exceptions import (
            ConfluenceError,
            ConfluenceNotFoundError,
        )

        err = ConfluenceNotFoundError("page gone")
        assert isinstance(err, ConfluenceError)

    def test_api_error_has_optional_status_code(self) -> None:
        from raise_cli.adapters.confluence_exceptions import (
            ConfluenceApiError,
            ConfluenceError,
        )

        err = ConfluenceApiError("server error", status_code=500)
        assert isinstance(err, ConfluenceError)
        assert err.status_code == 500
        assert err.message == "server error"

    def test_api_error_status_code_defaults_none(self) -> None:
        from raise_cli.adapters.confluence_exceptions import ConfluenceApiError

        err = ConfluenceApiError("unknown")
        assert err.status_code is None


class TestConfluenceInstanceConfig:
    """Minimal Pydantic config — S1051.3 extends later."""

    def test_required_fields(self) -> None:
        from raise_cli.adapters.confluence_config import ConfluenceInstanceConfig

        config = ConfluenceInstanceConfig(
            url="https://humansys.atlassian.net/wiki",
            username="emilio@humansys.ai",
            space_key="RaiSE1",
        )
        assert config.url == "https://humansys.atlassian.net/wiki"
        assert config.username == "emilio@humansys.ai"
        assert config.space_key == "RaiSE1"
        assert config.instance_name == "default"

    def test_custom_instance_name(self) -> None:
        from raise_cli.adapters.confluence_config import ConfluenceInstanceConfig

        config = ConfluenceInstanceConfig(
            url="https://x.atlassian.net/wiki",
            username="u@x.com",
            space_key="DEV",
            instance_name="humansys",
        )
        assert config.instance_name == "humansys"

    def test_missing_url_raises(self) -> None:
        from raise_cli.adapters.confluence_config import ConfluenceInstanceConfig

        with pytest.raises(ValidationError):
            ConfluenceInstanceConfig(
                username="u@x.com", space_key="DEV"
            )  # type: ignore[call-arg]

    def test_missing_username_raises(self) -> None:
        from raise_cli.adapters.confluence_config import ConfluenceInstanceConfig

        with pytest.raises(ValidationError):
            ConfluenceInstanceConfig(
                url="https://x.atlassian.net/wiki", space_key="DEV"
            )  # type: ignore[call-arg]

    def test_missing_space_key_raises(self) -> None:
        from raise_cli.adapters.confluence_config import ConfluenceInstanceConfig

        with pytest.raises(ValidationError):
            ConfluenceInstanceConfig(
                url="https://x.atlassian.net/wiki", username="u@x.com"
            )  # type: ignore[call-arg]

    def test_roundtrip(self) -> None:
        from raise_cli.adapters.confluence_config import ConfluenceInstanceConfig

        config = ConfluenceInstanceConfig(
            url="https://x.atlassian.net/wiki",
            username="u@x.com",
            space_key="DEV",
            instance_name="prod",
        )
        rebuilt = ConfluenceInstanceConfig.model_validate(config.model_dump())
        assert rebuilt == config


# ── T2: Auth resolution ──────────────────────────────────────────────


class TestAuthResolution:
    """Token resolution: instance-specific → generic → error."""

    def test_instance_specific_token(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from raise_cli.adapters.confluence_client import ConfluenceClient

        monkeypatch.setenv("CONFLUENCE_API_TOKEN_HUMANSYS", "instance-secret")
        monkeypatch.delenv("CONFLUENCE_API_TOKEN", raising=False)

        token = ConfluenceClient._resolve_token("humansys")
        assert token == "instance-secret"

    def test_generic_token_fallback(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from raise_cli.adapters.confluence_client import ConfluenceClient

        monkeypatch.delenv("CONFLUENCE_API_TOKEN_HUMANSYS", raising=False)
        monkeypatch.setenv("CONFLUENCE_API_TOKEN", "generic-secret")

        token = ConfluenceClient._resolve_token("humansys")
        assert token == "generic-secret"

    def test_instance_specific_takes_precedence(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from raise_cli.adapters.confluence_client import ConfluenceClient

        monkeypatch.setenv("CONFLUENCE_API_TOKEN_HUMANSYS", "instance-secret")
        monkeypatch.setenv("CONFLUENCE_API_TOKEN", "generic-secret")

        token = ConfluenceClient._resolve_token("humansys")
        assert token == "instance-secret"

    def test_missing_token_raises_auth_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from raise_cli.adapters.confluence_client import ConfluenceClient
        from raise_cli.adapters.confluence_exceptions import ConfluenceAuthError

        monkeypatch.delenv("CONFLUENCE_API_TOKEN_HUMANSYS", raising=False)
        monkeypatch.delenv("CONFLUENCE_API_TOKEN", raising=False)

        with pytest.raises(ConfluenceAuthError, match="CONFLUENCE_API_TOKEN"):
            ConfluenceClient._resolve_token("humansys")

    def test_instance_name_uppercased(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from raise_cli.adapters.confluence_client import ConfluenceClient

        monkeypatch.setenv("CONFLUENCE_API_TOKEN_MY_PROD", "secret")

        token = ConfluenceClient._resolve_token("my-prod")
        assert token == "secret"
