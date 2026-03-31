"""Tests for Jira client wrapper (S1052.1 / RAISE-1052)."""

from __future__ import annotations

import sys
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# ── T1: Exceptions + Constructor + Auth + Import Guard ────────────────


class TestJiraExceptions:
    """Exception hierarchy: 4 classes, isinstance-based."""

    def test_base_error_has_message(self) -> None:
        from raise_cli.adapters.jira_exceptions import JiraAdapterError

        err = JiraAdapterError("something broke")
        assert err.message == "something broke"
        assert str(err) == "something broke"

    def test_auth_error_is_adapter_error(self) -> None:
        from raise_cli.adapters.jira_exceptions import (
            JiraAdapterError,
            JiraAuthError,
        )

        err = JiraAuthError("bad token")
        assert isinstance(err, JiraAdapterError)
        assert err.message == "bad token"

    def test_not_found_error_is_adapter_error(self) -> None:
        from raise_cli.adapters.jira_exceptions import (
            JiraAdapterError,
            JiraNotFoundError,
        )

        err = JiraNotFoundError("issue gone")
        assert isinstance(err, JiraAdapterError)

    def test_api_error_has_optional_status_code(self) -> None:
        from raise_cli.adapters.jira_exceptions import (
            JiraAdapterError,
            JiraApiError,
        )

        err = JiraApiError("server error", status_code=500)
        assert isinstance(err, JiraAdapterError)
        assert err.status_code == 500
        assert err.message == "server error"

    def test_api_error_status_code_defaults_none(self) -> None:
        from raise_cli.adapters.jira_exceptions import JiraApiError

        err = JiraApiError("unknown")
        assert err.status_code is None

    def test_exceptions_importable_without_atlassian(self) -> None:
        """AC8: jira_exceptions.py must not depend on atlassian-python-api."""
        with patch.dict(sys.modules, {"atlassian": None}):
            # Force re-import
            if "raise_cli.adapters.jira_exceptions" in sys.modules:
                del sys.modules["raise_cli.adapters.jira_exceptions"]
            from raise_cli.adapters.jira_exceptions import (
                JiraAdapterError,
                JiraApiError,
                JiraAuthError,
                JiraNotFoundError,
            )

            assert issubclass(JiraAuthError, JiraAdapterError)
            assert issubclass(JiraNotFoundError, JiraAdapterError)
            assert issubclass(JiraApiError, JiraAdapterError)


class TestClientConstructor:
    """Client wires atlassian.Jira with correct params."""

    def test_constructor_creates_jira_client(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from raise_cli.adapters.jira_client import JiraClient

        mock_jira_cls = MagicMock()
        with patch.dict(
            sys.modules,
            {"atlassian": MagicMock(Jira=mock_jira_cls)},
        ):
            client = JiraClient(
                url="https://humansys.atlassian.net",
                username="emilio@humansys.com",
                token="test-token",
            )

        mock_jira_cls.assert_called_once_with(
            url="https://humansys.atlassian.net",
            username="emilio@humansys.com",
            password="test-token",
            cloud=True,
            backoff_and_retry=True,
            max_backoff_retries=5,
            backoff_factor=1.0,
        )
        assert client._url == "https://humansys.atlassian.net"

    def test_import_guard_raises_on_missing_dep(self) -> None:
        with patch.dict(sys.modules, {"atlassian": None}):
            if "raise_cli.adapters.jira_client" in sys.modules:
                del sys.modules["raise_cli.adapters.jira_client"]
            from raise_cli.adapters.jira_client import JiraClient

            with pytest.raises(ImportError, match="raise-cli\\[jira\\]"):
                JiraClient(
                    url="https://x.atlassian.net",
                    username="u@x.com",
                    token="t",
                )


class TestTokenResolution:
    """Token resolution: instance-specific -> generic -> error."""

    def test_instance_specific_token(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from raise_cli.adapters.jira_client import JiraClient

        monkeypatch.setenv("JIRA_API_TOKEN_HUMANSYS", "instance-secret")
        monkeypatch.delenv("JIRA_API_TOKEN", raising=False)

        token = JiraClient._resolve_token("humansys")
        assert token == "instance-secret"

    def test_generic_token_fallback(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from raise_cli.adapters.jira_client import JiraClient

        monkeypatch.delenv("JIRA_API_TOKEN_HUMANSYS", raising=False)
        monkeypatch.setenv("JIRA_API_TOKEN", "generic-secret")

        token = JiraClient._resolve_token("humansys")
        assert token == "generic-secret"

    def test_instance_specific_takes_precedence(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from raise_cli.adapters.jira_client import JiraClient

        monkeypatch.setenv("JIRA_API_TOKEN_HUMANSYS", "instance-secret")
        monkeypatch.setenv("JIRA_API_TOKEN", "generic-secret")

        token = JiraClient._resolve_token("humansys")
        assert token == "instance-secret"

    def test_missing_token_raises_auth_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from raise_cli.adapters.jira_client import JiraClient
        from raise_cli.adapters.jira_exceptions import JiraAuthError

        monkeypatch.delenv("JIRA_API_TOKEN_HUMANSYS", raising=False)
        monkeypatch.delenv("JIRA_API_TOKEN", raising=False)

        with pytest.raises(JiraAuthError, match="JIRA_API_TOKEN"):
            JiraClient._resolve_token("humansys")

    def test_instance_name_uppercased_and_hyphens_replaced(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from raise_cli.adapters.jira_client import JiraClient

        monkeypatch.setenv("JIRA_API_TOKEN_MY_PROD", "secret")

        token = JiraClient._resolve_token("my-prod")
        assert token == "secret"


class TestUsernameResolution:
    """Username resolution: instance-specific -> generic -> error."""

    def test_instance_specific_username(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from raise_cli.adapters.jira_client import JiraClient

        monkeypatch.setenv("JIRA_USERNAME_HUMANSYS", "inst@x.com")
        monkeypatch.delenv("JIRA_USERNAME", raising=False)

        username = JiraClient._resolve_username("humansys")
        assert username == "inst@x.com"

    def test_generic_username_fallback(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from raise_cli.adapters.jira_client import JiraClient

        monkeypatch.delenv("JIRA_USERNAME_HUMANSYS", raising=False)
        monkeypatch.setenv("JIRA_USERNAME", "generic@x.com")

        username = JiraClient._resolve_username("humansys")
        assert username == "generic@x.com"

    def test_missing_username_raises_auth_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from raise_cli.adapters.jira_client import JiraClient
        from raise_cli.adapters.jira_exceptions import JiraAuthError

        monkeypatch.delenv("JIRA_USERNAME_HUMANSYS", raising=False)
        monkeypatch.delenv("JIRA_USERNAME", raising=False)

        with pytest.raises(JiraAuthError, match="JIRA_USERNAME"):
            JiraClient._resolve_username("humansys")


# ── Shared fixture ───────────────────────────────────────────────────


def _make_client() -> tuple[Any, MagicMock]:
    """Create a JiraClient with mocked atlassian backend.

    Returns (client, mock_backend) where mock_backend is the
    mocked atlassian.Jira instance.
    """
    from raise_cli.adapters.jira_client import JiraClient

    client = JiraClient(
        url="https://test.atlassian.net",
        username="u@test.com",
        token="test-token",
    )
    mock_backend = MagicMock()
    client._client = mock_backend
    return client, mock_backend


# ── T2: CRUD methods + error mapping ────────────────────────────────


class TestErrorMapping:
    """isinstance-based error mapping from atlassian exceptions."""

    def test_permission_error_maps_to_auth(self) -> None:
        from atlassian.errors import ApiPermissionError

        from raise_cli.adapters.jira_client import JiraClient
        from raise_cli.adapters.jira_exceptions import JiraAuthError

        result = JiraClient._map_error(
            ApiPermissionError("403 Forbidden"), "get_issue(RAISE-1)"
        )
        assert isinstance(result, JiraAuthError)
        assert "get_issue(RAISE-1)" in result.message

    def test_not_found_error_maps(self) -> None:
        from atlassian.errors import ApiNotFoundError

        from raise_cli.adapters.jira_client import JiraClient
        from raise_cli.adapters.jira_exceptions import JiraNotFoundError

        result = JiraClient._map_error(
            ApiNotFoundError("404 Not Found"), "get_issue(RAISE-99999)"
        )
        assert isinstance(result, JiraNotFoundError)
        assert "RAISE-99999" in result.message

    def test_generic_api_error_maps(self) -> None:
        from atlassian.errors import ApiError

        from raise_cli.adapters.jira_client import JiraClient
        from raise_cli.adapters.jira_exceptions import JiraApiError

        result = JiraClient._map_error(
            ApiError("500 Server Error"), "create_issue"
        )
        assert isinstance(result, JiraApiError)
        assert "create_issue" in result.message

    def test_unexpected_error_maps_to_api_error(self) -> None:
        from raise_cli.adapters.jira_client import JiraClient
        from raise_cli.adapters.jira_exceptions import JiraApiError

        result = JiraClient._map_error(
            RuntimeError("connection lost"), "get_issue(X)"
        )
        assert isinstance(result, JiraApiError)
        assert "unexpected" in result.message


class TestGetIssue:
    """get_issue delegates to self._client.issue and returns raw dict."""

    def test_returns_raw_dict(self) -> None:
        client, backend = _make_client()
        backend.issue.return_value = {
            "key": "RAISE-1",
            "fields": {"summary": "Test issue"},
        }

        result = client.get_issue("RAISE-1")

        assert result["key"] == "RAISE-1"
        assert result["fields"]["summary"] == "Test issue"
        backend.issue.assert_called_once_with("RAISE-1")

    def test_not_found_raises_jira_not_found(self) -> None:
        from atlassian.errors import ApiNotFoundError

        from raise_cli.adapters.jira_exceptions import JiraNotFoundError

        client, backend = _make_client()
        backend.issue.side_effect = ApiNotFoundError("404")

        with pytest.raises(JiraNotFoundError, match="RAISE-99999"):
            client.get_issue("RAISE-99999")

    def test_permission_error_raises_auth(self) -> None:
        from atlassian.errors import ApiPermissionError

        from raise_cli.adapters.jira_exceptions import JiraAuthError

        client, backend = _make_client()
        backend.issue.side_effect = ApiPermissionError("403")

        with pytest.raises(JiraAuthError):
            client.get_issue("RAISE-1")


class TestCreateIssue:
    """create_issue delegates to self._client.create_issue."""

    def test_creates_and_returns_raw_dict(self) -> None:
        client, backend = _make_client()
        fields = {"project": {"key": "RAISE"}, "summary": "New", "issuetype": {"name": "Task"}}
        backend.create_issue.return_value = {"key": "RAISE-100", "id": "10100"}

        result = client.create_issue(fields)

        assert result["key"] == "RAISE-100"
        backend.create_issue.assert_called_once_with(fields)

    def test_error_mapped(self) -> None:
        from atlassian.errors import ApiError

        from raise_cli.adapters.jira_exceptions import JiraApiError

        client, backend = _make_client()
        backend.create_issue.side_effect = ApiError("400 Bad Request")

        with pytest.raises(JiraApiError, match="create_issue"):
            client.create_issue({"summary": "X"})


class TestUpdateIssue:
    """update_issue delegates to self._client.update_issue."""

    def test_updates_and_returns_raw_dict(self) -> None:
        client, backend = _make_client()
        fields = {"summary": "Updated"}
        backend.update_issue.return_value = {"key": "RAISE-1"}

        result = client.update_issue("RAISE-1", fields)

        assert result["key"] == "RAISE-1"
        backend.update_issue.assert_called_once_with("RAISE-1", fields)

    def test_error_mapped(self) -> None:
        from atlassian.errors import ApiNotFoundError

        from raise_cli.adapters.jira_exceptions import JiraNotFoundError

        client, backend = _make_client()
        backend.update_issue.side_effect = ApiNotFoundError("404")

        with pytest.raises(JiraNotFoundError, match="RAISE-99"):
            client.update_issue("RAISE-99", {"summary": "X"})
