"""Tests for Confluence client wrapper (S1051.1 / RAISE-1054)."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

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


# ── T3: Constructor + import guard ───────────────────────────────────


class TestClientConstructor:
    """Client wires atlassian.Confluence with correct params."""

    def test_constructor_creates_client(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from unittest.mock import MagicMock, patch

        from raise_cli.adapters.confluence_client import ConfluenceClient
        from raise_cli.adapters.confluence_config import ConfluenceInstanceConfig

        monkeypatch.setenv("CONFLUENCE_API_TOKEN", "test-token")
        config = ConfluenceInstanceConfig(
            url="https://test.atlassian.net/wiki",
            username="u@test.com",
            space_key="TEST",
        )

        mock_confluence_cls = MagicMock()
        with patch(
            "raise_cli.adapters.confluence_client.ConfluenceClient.__init__.__module__",
            create=True,
        ):
            # Patch at the import point inside __init__
            with patch.dict(
                "sys.modules",
                {"atlassian": MagicMock(Confluence=mock_confluence_cls)},
            ):
                client = ConfluenceClient(config)

        mock_confluence_cls.assert_called_once_with(
            url="https://test.atlassian.net/wiki",
            username="u@test.com",
            password="test-token",
            cloud=True,
            backoff_and_retry=True,
            max_backoff_retries=5,
            backoff_factor=1.0,
        )
        assert client._config is config

    def test_import_guard_raises_on_missing_dep(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        import sys
        from unittest.mock import patch

        from raise_cli.adapters.confluence_config import ConfluenceInstanceConfig

        monkeypatch.setenv("CONFLUENCE_API_TOKEN", "test-token")
        config = ConfluenceInstanceConfig(
            url="https://test.atlassian.net/wiki",
            username="u@test.com",
            space_key="TEST",
        )

        # Simulate atlassian not installed
        with patch.dict(sys.modules, {"atlassian": None}):
            from raise_cli.adapters.confluence_client import ConfluenceClient

            with pytest.raises(ImportError, match="raise-cli\\[confluence\\]"):
                ConfluenceClient(config)


# ── Shared fixture ───────────────────────────────────────────────────


def _make_client(monkeypatch: pytest.MonkeyPatch) -> tuple[Any, Any]:
    """Create a ConfluenceClient with mocked atlassian backend.

    Returns (client, mock_backend) where mock_backend is the
    mocked atlassian.Confluence instance.
    """
    from raise_cli.adapters.confluence_client import ConfluenceClient
    from raise_cli.adapters.confluence_config import ConfluenceInstanceConfig

    monkeypatch.setenv("CONFLUENCE_API_TOKEN", "test-token")
    config = ConfluenceInstanceConfig(
        url="https://test.atlassian.net/wiki",
        username="u@test.com",
        space_key="TEST",
    )
    client = ConfluenceClient(config)
    mock_backend = MagicMock()
    client._client = mock_backend
    return client, mock_backend


# ── T4: Publishing methods ───────────────────────────────────────────


class TestCreatePage:
    """create_page → PageContent."""

    def test_create_page_returns_page_content(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from raise_cli.adapters.models.docs import PageContent

        client, backend = _make_client(monkeypatch)
        backend.create_page.return_value = {
            "id": "456",
            "title": "ADR-015",
            "body": {"storage": {"value": "<p>content</p>"}},
            "_links": {"base": "https://test.atlassian.net/wiki", "webui": "/spaces/TEST/pages/456"},
            "version": {"number": 1},
            "space": {"key": "TEST"},
        }

        result = client.create_page("ADR-015", "<p>content</p>", parent_id="123")

        assert isinstance(result, PageContent)
        assert result.id == "456"
        assert result.title == "ADR-015"
        backend.create_page.assert_called_once_with(
            space="TEST",
            title="ADR-015",
            body="<p>content</p>",
            parent_id="123",
            type="page",
        )

    def test_create_page_uses_space_override(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        client, backend = _make_client(monkeypatch)
        backend.create_page.return_value = {
            "id": "1", "title": "T", "body": {"storage": {"value": ""}},
            "_links": {"base": "", "webui": ""}, "version": {"number": 1},
            "space": {"key": "OTHER"},
        }

        client.create_page("T", "<p>b</p>", space="OTHER")

        backend.create_page.assert_called_once()
        call_kwargs = backend.create_page.call_args
        assert call_kwargs[1]["space"] == "OTHER" or call_kwargs[0][0] == "OTHER"


class TestUpdatePage:
    """update_page → PageContent."""

    def test_update_page_returns_page_content(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from raise_cli.adapters.models.docs import PageContent

        client, backend = _make_client(monkeypatch)
        backend.update_page.return_value = {
            "id": "456",
            "title": "ADR-015 v2",
            "body": {"storage": {"value": "<p>new</p>"}},
            "_links": {"base": "https://test.atlassian.net/wiki", "webui": "/spaces/TEST/pages/456"},
            "version": {"number": 2},
            "space": {"key": "TEST"},
        }

        result = client.update_page("456", "ADR-015 v2", "<p>new</p>")

        assert isinstance(result, PageContent)
        assert result.id == "456"
        assert result.version == 2


class TestGetPageById:
    """get_page_by_id → PageContent."""

    def test_returns_page_content(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from raise_cli.adapters.models.docs import PageContent

        client, backend = _make_client(monkeypatch)
        backend.get_page_by_id.return_value = {
            "id": "456",
            "title": "ADR-015",
            "body": {"storage": {"value": "<p>content</p>"}},
            "_links": {"base": "https://test.atlassian.net/wiki", "webui": "/spaces/TEST/pages/456"},
            "version": {"number": 1},
            "space": {"key": "TEST"},
        }

        result = client.get_page_by_id("456")

        assert isinstance(result, PageContent)
        assert result.id == "456"


class TestGetPageByTitle:
    """get_page_by_title → PageContent | None."""

    def test_returns_page_when_found(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from raise_cli.adapters.models.docs import PageContent

        client, backend = _make_client(monkeypatch)
        backend.get_page_by_title.return_value = {
            "id": "456",
            "title": "ADR-015",
            "body": {"storage": {"value": "<p>content</p>"}},
            "_links": {"base": "https://test.atlassian.net/wiki", "webui": "/spaces/TEST/pages/456"},
            "version": {"number": 1},
            "space": {"key": "TEST"},
        }

        result = client.get_page_by_title("ADR-015")

        assert isinstance(result, PageContent)
        assert result.title == "ADR-015"

    def test_returns_none_when_not_found(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        client, backend = _make_client(monkeypatch)
        backend.get_page_by_title.return_value = None

        result = client.get_page_by_title("nonexistent")

        assert result is None

    def test_uses_config_space_by_default(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        client, backend = _make_client(monkeypatch)
        backend.get_page_by_title.return_value = None

        client.get_page_by_title("X")

        backend.get_page_by_title.assert_called_once_with(space="TEST", title="X")

    def test_uses_space_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        client, backend = _make_client(monkeypatch)
        backend.get_page_by_title.return_value = None

        client.get_page_by_title("X", space="OTHER")

        backend.get_page_by_title.assert_called_once_with(space="OTHER", title="X")


class TestErrorMapping:
    """isinstance-based error mapping from atlassian exceptions."""

    def test_permission_error_maps_to_auth(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from atlassian.errors import ApiPermissionError

        from raise_cli.adapters.confluence_exceptions import ConfluenceAuthError

        client, backend = _make_client(monkeypatch)
        backend.get_page_by_id.side_effect = ApiPermissionError("403 Forbidden")

        with pytest.raises(ConfluenceAuthError):
            client.get_page_by_id("123")

    def test_not_found_error_maps(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from atlassian.errors import ApiNotFoundError

        from raise_cli.adapters.confluence_exceptions import ConfluenceNotFoundError

        client, backend = _make_client(monkeypatch)
        backend.get_page_by_id.side_effect = ApiNotFoundError("404 Not Found")

        with pytest.raises(ConfluenceNotFoundError):
            client.get_page_by_id("123")

    def test_generic_api_error_maps(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from atlassian.errors import ApiError

        from raise_cli.adapters.confluence_exceptions import ConfluenceApiError

        client, backend = _make_client(monkeypatch)
        backend.get_page_by_id.side_effect = ApiError("500 Server Error")

        with pytest.raises(ConfluenceApiError):
            client.get_page_by_id("123")

    def test_unexpected_error_maps_to_api_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from raise_cli.adapters.confluence_exceptions import ConfluenceApiError

        client, backend = _make_client(monkeypatch)
        backend.get_page_by_id.side_effect = RuntimeError("connection lost")

        with pytest.raises(ConfluenceApiError, match="unexpected"):
            client.get_page_by_id("123")
