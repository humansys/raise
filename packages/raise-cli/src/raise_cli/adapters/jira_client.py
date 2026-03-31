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

    # ── Search ───────────────────────────────────────────────────────

    def jql(self, query: str, limit: int = 50) -> list[dict[str, Any]]:
        """Run a JQL query. Returns list of issue dicts."""
        try:
            raw: dict[str, Any] = self._client.jql(query, limit=limit)  # type: ignore[no-untyped-call]
            return list(raw.get("issues", []))
        except JiraAdapterError:
            raise
        except Exception as e:
            raise self._map_error(e, f"jql({query!r})") from e

    # ── Transitions ──────────────────────────────────────────────────

    def get_transitions(self, key: str) -> list[dict[str, Any]]:
        """Get available transitions for an issue."""
        try:
            result: list[dict[str, Any]] = self._client.get_issue_transitions(key)  # type: ignore[no-untyped-call]
            return result
        except JiraAdapterError:
            raise
        except Exception as e:
            raise self._map_error(e, f"get_transitions({key})") from e

    def transition_issue(self, key: str, transition_id: str) -> None:
        """Transition an issue to a new status."""
        try:
            self._client.set_issue_status(key, transition_id)  # type: ignore[no-untyped-call]
        except JiraAdapterError:
            raise
        except Exception as e:
            raise self._map_error(e, f"transition_issue({key}, {transition_id})") from e

    # ── Relationships ────────────────────────────────────────────────

    def create_link(self, source: str, target: str, link_type: str) -> None:
        """Create an issue link between two issues."""
        try:
            self._client.create_issue_link({  # type: ignore[no-untyped-call]
                "type": {"name": link_type},
                "inwardIssue": {"key": source},
                "outwardIssue": {"key": target},
            })
        except JiraAdapterError:
            raise
        except Exception as e:
            raise self._map_error(e, f"create_link({source}, {target})") from e

    def set_parent(self, child: str, parent: str) -> None:
        """Set the parent of an issue."""
        self.update_issue(child, {"parent": {"key": parent}})

    # ── Comments ─────────────────────────────────────────────────────

    def add_comment(self, key: str, body: str) -> dict[str, Any]:
        """Add a comment to an issue."""
        try:
            result: dict[str, Any] = self._client.issue_add_comment(key, body)  # type: ignore[no-untyped-call]
            return result
        except JiraAdapterError:
            raise
        except Exception as e:
            raise self._map_error(e, f"add_comment({key})") from e

    def get_comments(self, key: str, limit: int = 10) -> list[dict[str, Any]]:
        """Get comments on an issue."""
        try:
            raw: dict[str, Any] = self._client.issue_get_comments(key)  # type: ignore[no-untyped-call]
            comments: list[dict[str, Any]] = raw.get("comments", [])
            return comments[:limit]
        except JiraAdapterError:
            raise
        except Exception as e:
            raise self._map_error(e, f"get_comments({key})") from e

    # ── Health ───────────────────────────────────────────────────────

    def server_info(self) -> dict[str, Any]:
        """Get Jira server info for health checks."""
        try:
            result: dict[str, Any] = self._client.get_server_info()  # type: ignore[no-untyped-call]
            return result
        except JiraAdapterError:
            raise
        except Exception as e:
            raise self._map_error(e, "server_info") from e

    # ── Factory ──────────────────────────────────────────────────────

    @classmethod
    def from_config(cls, config: Any, instance: str | None = None) -> JiraClient:
        """Create a JiraClient from config and environment.

        Args:
            config: Object with .default_instance and .instances dict.
                    Each instance has .site and optional .email.
            instance: Instance name. Uses config.default_instance if None.
        """
        instance_name = instance or config.default_instance
        instances: dict[str, Any] = config.instances
        if instance_name not in instances:
            raise JiraApiError(
                f"Instance {instance_name!r} not found in config. "
                f"Available: {list(instances.keys())}"
            )

        inst = instances[instance_name]
        url = f"https://{inst.site}"
        token = cls._resolve_token(instance_name)
        email: str | None = getattr(inst, "email", None)
        username = email or cls._resolve_username(instance_name)

        return cls(url=url, username=username, token=token)

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
