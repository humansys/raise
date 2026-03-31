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


# ── T3: Search + transitions + relationships ─────────────────────────


class TestJql:
    """jql delegates to self._client.jql and returns issues list."""

    def test_returns_issues_list(self) -> None:
        client, backend = _make_client()
        backend.jql.return_value = {
            "issues": [
                {"key": "RAISE-1", "fields": {"summary": "First"}},
                {"key": "RAISE-2", "fields": {"summary": "Second"}},
            ],
            "total": 2,
        }

        result = client.jql("project = RAISE", limit=10)

        assert len(result) == 2
        assert result[0]["key"] == "RAISE-1"
        backend.jql.assert_called_once_with("project = RAISE", limit=10)

    def test_returns_empty_list(self) -> None:
        client, backend = _make_client()
        backend.jql.return_value = {"issues": [], "total": 0}

        result = client.jql("project = EMPTY")

        assert result == []

    def test_error_mapped(self) -> None:
        from atlassian.errors import ApiError

        from raise_cli.adapters.jira_exceptions import JiraApiError

        client, backend = _make_client()
        backend.jql.side_effect = ApiError("400")

        with pytest.raises(JiraApiError, match="jql"):
            client.jql("bad query")


class TestGetTransitions:
    """get_transitions delegates to self._client.get_issue_transitions."""

    def test_returns_transitions_list(self) -> None:
        client, backend = _make_client()
        backend.get_issue_transitions.return_value = [
            {"id": "11", "name": "To Do"},
            {"id": "21", "name": "In Progress"},
        ]

        result = client.get_transitions("RAISE-1")

        assert len(result) == 2
        assert result[0]["id"] == "11"
        backend.get_issue_transitions.assert_called_once_with("RAISE-1")

    def test_error_mapped(self) -> None:
        from atlassian.errors import ApiNotFoundError

        from raise_cli.adapters.jira_exceptions import JiraNotFoundError

        client, backend = _make_client()
        backend.get_issue_transitions.side_effect = ApiNotFoundError("404")

        with pytest.raises(JiraNotFoundError):
            client.get_transitions("RAISE-99999")


class TestTransitionIssue:
    """transition_issue delegates to self._client.set_issue_status."""

    def test_delegates_to_set_issue_status(self) -> None:
        client, backend = _make_client()
        backend.set_issue_status.return_value = None

        client.transition_issue("RAISE-1", "21")

        backend.set_issue_status.assert_called_once_with("RAISE-1", "21")

    def test_error_mapped(self) -> None:
        from atlassian.errors import ApiError

        from raise_cli.adapters.jira_exceptions import JiraApiError

        client, backend = _make_client()
        backend.set_issue_status.side_effect = ApiError("400")

        with pytest.raises(JiraApiError, match="transition_issue"):
            client.transition_issue("RAISE-1", "99")


class TestCreateLink:
    """create_link delegates to self._client.create_issue_link."""

    def test_delegates_with_correct_data(self) -> None:
        client, backend = _make_client()
        backend.create_issue_link.return_value = None

        client.create_link("RAISE-1", "RAISE-2", "Blocks")

        backend.create_issue_link.assert_called_once_with({
            "type": {"name": "Blocks"},
            "inwardIssue": {"key": "RAISE-1"},
            "outwardIssue": {"key": "RAISE-2"},
        })

    def test_error_mapped(self) -> None:
        from atlassian.errors import ApiError

        from raise_cli.adapters.jira_exceptions import JiraApiError

        client, backend = _make_client()
        backend.create_issue_link.side_effect = ApiError("400")

        with pytest.raises(JiraApiError, match="create_link"):
            client.create_link("RAISE-1", "RAISE-2", "Blocks")


class TestSetParent:
    """set_parent calls update_issue with parent field."""

    def test_delegates_to_update_issue(self) -> None:
        client, backend = _make_client()
        backend.update_issue.return_value = {"key": "RAISE-2"}

        client.set_parent("RAISE-2", "RAISE-1")

        backend.update_issue.assert_called_once_with(
            "RAISE-2", {"parent": {"key": "RAISE-1"}}
        )


# ── T4: Comments + health + from_config factory ──────────────────────


class TestAddComment:
    """add_comment delegates to self._client.issue_add_comment."""

    def test_adds_and_returns_raw_dict(self) -> None:
        client, backend = _make_client()
        backend.issue_add_comment.return_value = {
            "id": "10001",
            "body": "Test comment",
        }

        result = client.add_comment("RAISE-1", "Test comment")

        assert result["id"] == "10001"
        backend.issue_add_comment.assert_called_once_with("RAISE-1", "Test comment")

    def test_error_mapped(self) -> None:
        from atlassian.errors import ApiNotFoundError

        from raise_cli.adapters.jira_exceptions import JiraNotFoundError

        client, backend = _make_client()
        backend.issue_add_comment.side_effect = ApiNotFoundError("404")

        with pytest.raises(JiraNotFoundError):
            client.add_comment("RAISE-99999", "comment")


class TestGetComments:
    """get_comments delegates to self._client.issue_get_comments."""

    def test_returns_comments_list(self) -> None:
        client, backend = _make_client()
        backend.issue_get_comments.return_value = {
            "comments": [
                {"id": "10001", "body": "First"},
                {"id": "10002", "body": "Second"},
            ],
            "total": 2,
        }

        result = client.get_comments("RAISE-1")

        assert len(result) == 2
        assert result[0]["id"] == "10001"
        backend.issue_get_comments.assert_called_once_with("RAISE-1")

    def test_returns_empty_list(self) -> None:
        client, backend = _make_client()
        backend.issue_get_comments.return_value = {"comments": [], "total": 0}

        result = client.get_comments("RAISE-1")

        assert result == []

    def test_error_mapped(self) -> None:
        from atlassian.errors import ApiError

        from raise_cli.adapters.jira_exceptions import JiraApiError

        client, backend = _make_client()
        backend.issue_get_comments.side_effect = ApiError("500")

        with pytest.raises(JiraApiError, match="get_comments"):
            client.get_comments("RAISE-1")


class TestServerInfo:
    """server_info delegates to self._client.get_server_info."""

    def test_returns_raw_dict(self) -> None:
        client, backend = _make_client()
        backend.get_server_info.return_value = {
            "baseUrl": "https://humansys.atlassian.net",
            "version": "1001.0.0",
        }

        result = client.server_info()

        assert result["baseUrl"] == "https://humansys.atlassian.net"
        backend.get_server_info.assert_called_once()

    def test_error_mapped(self) -> None:
        from atlassian.errors import ApiPermissionError

        from raise_cli.adapters.jira_exceptions import JiraAuthError

        client, backend = _make_client()
        backend.get_server_info.side_effect = ApiPermissionError("401")

        with pytest.raises(JiraAuthError):
            client.server_info()


class TestFromConfig:
    """from_config factory resolves instance from config + env."""

    def test_creates_client_for_named_instance(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from types import SimpleNamespace

        from raise_cli.adapters.jira_client import JiraClient

        monkeypatch.setenv("JIRA_API_TOKEN_HUMANSYS", "test-token")
        config = SimpleNamespace(
            default_instance="humansys",
            instances={
                "humansys": SimpleNamespace(
                    site="humansys.atlassian.net",
                    email="emilio@humansys.com",
                ),
            },
        )

        mock_jira_cls = MagicMock()
        with patch.dict(
            sys.modules,
            {"atlassian": MagicMock(Jira=mock_jira_cls)},
        ):
            client = JiraClient.from_config(config, instance="humansys")

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

    def test_uses_default_instance_when_none(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from types import SimpleNamespace

        from raise_cli.adapters.jira_client import JiraClient

        monkeypatch.setenv("JIRA_API_TOKEN_HUMANSYS", "test-token")
        config = SimpleNamespace(
            default_instance="humansys",
            instances={
                "humansys": SimpleNamespace(
                    site="humansys.atlassian.net",
                    email="emilio@humansys.com",
                ),
            },
        )

        mock_jira_cls = MagicMock()
        with patch.dict(
            sys.modules,
            {"atlassian": MagicMock(Jira=mock_jira_cls)},
        ):
            client = JiraClient.from_config(config, instance=None)

        assert client._url == "https://humansys.atlassian.net"

    def test_missing_instance_raises_api_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from types import SimpleNamespace

        from raise_cli.adapters.jira_client import JiraClient
        from raise_cli.adapters.jira_exceptions import JiraApiError

        config = SimpleNamespace(
            default_instance="humansys",
            instances={},
        )

        with pytest.raises(JiraApiError, match="humansys"):
            JiraClient.from_config(config, instance="humansys")

    def test_resolves_username_from_env_when_no_email(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from types import SimpleNamespace

        from raise_cli.adapters.jira_client import JiraClient

        monkeypatch.setenv("JIRA_API_TOKEN_HUMANSYS", "test-token")
        monkeypatch.setenv("JIRA_USERNAME_HUMANSYS", "env@humansys.com")
        config = SimpleNamespace(
            default_instance="humansys",
            instances={
                "humansys": SimpleNamespace(
                    site="humansys.atlassian.net",
                    email=None,
                ),
            },
        )

        mock_jira_cls = MagicMock()
        with patch.dict(
            sys.modules,
            {"atlassian": MagicMock(Jira=mock_jira_cls)},
        ):
            JiraClient.from_config(config, instance="humansys")

        call_kwargs = mock_jira_cls.call_args
        assert call_kwargs[1]["username"] == "env@humansys.com"
