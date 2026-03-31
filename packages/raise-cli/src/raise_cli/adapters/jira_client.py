"""Jira client wrapper over atlassian-python-api.

Concrete class (NOT Protocol) providing methods for issue CRUD,
search, transitions, relationships, comments, and health.
Consumed by PythonApiJiraAdapter — not directly by skills or CLI.

Optional dependency: ``pip install raise-cli[jira]``

RAISE-1052 (S1052.1)
"""

from __future__ import annotations

import os
from typing import Any

from raise_cli.adapters.jira_exceptions import (
    JiraAdapterError,
    JiraApiError,
    JiraAuthError,
    JiraNotFoundError,
)


class JiraClient:
    """Wraps atlassian.Jira with auth resolution and error normalization."""

    def __init__(self, url: str, username: str, token: str) -> None:
        try:
            from atlassian import Jira
        except ImportError as exc:
            raise ImportError(
                "atlassian-python-api required for Jira adapter. "
                "Install with: pip install raise-cli[jira]"
            ) from exc

        self._url = url
        self._client = Jira(
            url=url,
            username=username,
            password=token,
            cloud=True,
            backoff_and_retry=True,
            max_backoff_retries=5,
            backoff_factor=1.0,
        )

    # ── Auth Resolution ──────────────────────────────────────────────

    @staticmethod
    def _resolve_token(instance_name: str) -> str:
        """Resolve API token from environment.

        Order: JIRA_API_TOKEN_{INSTANCE} -> JIRA_API_TOKEN -> error.
        Instance name is uppercased with hyphens replaced by underscores.
        """
        env_suffix = instance_name.upper().replace("-", "_")
        instance_var = f"JIRA_API_TOKEN_{env_suffix}"

        token = os.environ.get(instance_var) or os.environ.get("JIRA_API_TOKEN")
        if not token:
            raise JiraAuthError(
                f"No Jira API token found. Set {instance_var} or "
                "JIRA_API_TOKEN environment variable."
            )
        return token

    @staticmethod
    def _resolve_username(instance_name: str) -> str:
        """Resolve username (email) from environment.

        Order: JIRA_USERNAME_{INSTANCE} -> JIRA_USERNAME -> error.
        """
        env_suffix = instance_name.upper().replace("-", "_")
        instance_var = f"JIRA_USERNAME_{env_suffix}"

        username = os.environ.get(instance_var) or os.environ.get("JIRA_USERNAME")
        if not username:
            raise JiraAuthError(
                f"No Jira username found. Set {instance_var} or "
                "JIRA_USERNAME environment variable, or set email in config."
            )
        return username

    # ── Issue CRUD ───────────────────────────────────────────────────

    def get_issue(self, key: str) -> dict[str, Any]:
        """Get issue by key. Returns full raw dict."""
        try:
            result: dict[str, Any] = self._client.issue(key)  # type: ignore[no-untyped-call]
            return result
        except JiraAdapterError:
            raise
        except Exception as e:
            raise self._map_error(e, f"get_issue({key})") from e

    def create_issue(self, fields: dict[str, Any]) -> dict[str, Any]:
        """Create an issue. Returns raw dict with at least key and id."""
        try:
            result: dict[str, Any] = self._client.create_issue(fields)  # type: ignore[no-untyped-call]
            return result
        except JiraAdapterError:
            raise
        except Exception as e:
            raise self._map_error(e, "create_issue") from e

    def update_issue(self, key: str, fields: dict[str, Any]) -> dict[str, Any]:
        """Update an issue by key. Returns raw response dict."""
        try:
            result: dict[str, Any] = self._client.update_issue(key, fields)  # type: ignore[no-untyped-call]
            return result
        except JiraAdapterError:
            raise
        except Exception as e:
            raise self._map_error(e, f"update_issue({key})") from e

    # ── Internal ─────────────────────────────────────────────────────

    @staticmethod
    def _map_error(error: Exception, context: str) -> JiraAdapterError:
        """Map atlassian exceptions to our hierarchy using isinstance."""
        from atlassian.errors import ApiError, ApiNotFoundError, ApiPermissionError

        if isinstance(error, ApiPermissionError):
            return JiraAuthError(f"{context}: {error}")
        if isinstance(error, ApiNotFoundError):
            return JiraNotFoundError(f"{context}: {error}")
        if isinstance(error, ApiError):
            return JiraApiError(f"{context}: {error}")
        return JiraApiError(f"{context}: unexpected error: {error}")
