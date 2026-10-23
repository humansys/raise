"""Google Drive adapter exceptions (S8331.4).

Hierarchy:
    GoogleDriveError
      ├── GoogleDriveAuthError     (401/403 or missing token)
      ├── GoogleDriveNotFoundError (404 or unsupported type)
      └── GoogleDriveApiError      (everything else incl. 5xx, 429)
"""

from __future__ import annotations


class GoogleDriveError(Exception):
    """Base for all Google Drive adapter errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class GoogleDriveAuthError(GoogleDriveError):
    """401/403 — invalid, missing, or expired OAuth token."""


class GoogleDriveNotFoundError(GoogleDriveError):
    """404 — document not found, no permissions, or unsupported mimeType."""


class GoogleDriveApiError(GoogleDriveError):
    """Generic API error (incl. 5xx, 429, etc)."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        self.status_code = status_code
        super().__init__(message)
