"""Integration tests for Jira client wrapper (S1052.1 / RAISE-1052).

These tests hit the live Jira Cloud API and are skipped when
JIRA_API_TOKEN is not set in the environment.
"""

from __future__ import annotations

import os

import pytest

_skip_no_creds = pytest.mark.skipif(
    not os.environ.get("JIRA_API_TOKEN"),
    reason="No Jira credentials — set JIRA_API_TOKEN to run",
)


@_skip_no_creds
class TestJiraClientIntegration:
    """Live Jira API tests — require JIRA_API_TOKEN env var."""

    def _make_live_client(self) -> object:
        """Create a JiraClient from environment variables."""
        from raise_cli.adapters.jira_client import JiraClient

        url = os.environ.get("JIRA_URL", "https://humansys.atlassian.net")
        username = os.environ.get("JIRA_USERNAME", "")
        token = os.environ.get("JIRA_API_TOKEN", "")
        return JiraClient(url=url, username=username, token=token)

    def test_server_info(self) -> None:
        from raise_cli.adapters.jira_client import JiraClient

        client: JiraClient = self._make_live_client()  # type: ignore[assignment]
        info = client.server_info()
        assert isinstance(info, dict)
        assert "baseUrl" in info

    def test_get_issue(self) -> None:
        from raise_cli.adapters.jira_client import JiraClient

        client: JiraClient = self._make_live_client()  # type: ignore[assignment]
        issue = client.get_issue("RAISE-1052")
        assert "fields" in issue
        assert "summary" in issue["fields"]

    def test_jql_search(self) -> None:
        from raise_cli.adapters.jira_client import JiraClient

        client: JiraClient = self._make_live_client()  # type: ignore[assignment]
        issues = client.jql("project = RAISE ORDER BY created DESC", limit=3)
        assert isinstance(issues, list)
