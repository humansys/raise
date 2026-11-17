"""OAuth token model and credential errors for Carril B (ADR-112, S9869.4).

Carril B principles (ADR-112):
  - Token never exposed to LLM (brokered pattern — Composio-style)
  - Fail loud: CredentialNotFoundError / CredentialExpiredError — no silent fallback
  - identity_map lives in raise-server, not in raise-cli
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class OAuthToken(BaseModel):
    """Per-user Jira OAuth token stored in raise-server identity_map."""

    user_key: str
    access_token: str
    token_type: str = "Bearer"  # noqa: S105
    expires_at: datetime | None = None

    def is_expired(self) -> bool:
        """True if the token has a known expiry and it has passed."""
        if self.expires_at is None:
            return False
        from datetime import UTC

        return datetime.now(UTC) >= self.expires_at


class CredentialNotFoundError(Exception):
    """Raised when no OAuth token is stored for the requested user (ADR-112).

    Never fall back to service account — raise and surface the error to the caller.
    """

    def __init__(self, user_key: str) -> None:
        super().__init__(
            f"No Jira OAuth token found for user '{user_key}'. "
            "Run 'rai backlog connect --user' to authorize."
        )
        self.user_key = user_key


class CredentialExpiredError(Exception):
    """Raised when the stored OAuth token has expired (ADR-112).

    Never fall back to service account — raise and surface the error to the caller.
    """

    def __init__(self, user_key: str, expires_at: datetime | None = None) -> None:
        super().__init__(
            f"Jira OAuth token for user '{user_key}' has expired"
            + (f" at {expires_at.isoformat()}" if expires_at else "")
            + ". Run 'rai backlog connect --user' to re-authorize."
        )
        self.user_key = user_key
        self.expires_at = expires_at
