"""Jira client exceptions.

Hierarchy:
    JiraAdapterError
      ├── JiraAuthError     (401/403)
      ├── JiraNotFoundError (404)
      └── JiraApiError      (everything else incl. post-retry 429)

RAISE-1052 (S1052.1): Separate file so adapter/doctor/discovery can import
exceptions without loading the client or atlassian-python-api.
"""

from __future__ import annotations


class JiraAdapterError(Exception):
    """Base for all Jira client errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class JiraAuthError(JiraAdapterError):
    """401/403 — invalid or missing credentials."""


class JiraNotFoundError(JiraAdapterError):
    """404 — issue, project, or resource not found."""


class JiraApiError(JiraAdapterError):
    """Generic API error (incl. post-retry 429, 5xx, etc)."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        self.status_code = status_code
        super().__init__(message)
