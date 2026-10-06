"""Confluence client exceptions.

Hierarchy:
    ConfluenceError
      ├── ConfluenceAuthError     (401/403)
      ├── ConfluenceNotFoundError (404)
      └── ConfluenceApiError      (everything else incl. post-retry 429)

RAISE-1054 (S1051.1): Separate file so doctor/discovery can import
exceptions without loading the client or atlassian-python-api.
"""

from __future__ import annotations


class ConfluenceError(Exception):
    """Base for all Confluence client errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class ConfluenceAuthError(ConfluenceError):
    """401/403 — invalid or missing credentials."""


class ConfluenceNotFoundError(ConfluenceError):
    """404 — page, space, or resource not found."""


class ConfluenceApiError(ConfluenceError):
    """Generic API error (incl. post-retry 429, 5xx, etc)."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        self.status_code = status_code
        super().__init__(message)
