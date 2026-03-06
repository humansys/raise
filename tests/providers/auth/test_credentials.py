"""Tests for credentials storage with encryption."""

from pathlib import Path
from typing import Any

import pytest


@pytest.fixture
def credentials_path(tmp_path: Path) -> Path:
    """Provide a temporary credentials file path."""
    return tmp_path / "credentials.json"


@pytest.fixture
def sample_token() -> dict[str, Any]:
    """Provide a sample OAuth token."""
    return {
        "access_token": "fake-access-token-for-testing",
        "refresh_token": "fake-refresh-token-for-testing",
        "token_type": "Bearer",
        "expires_at": 1234567890,
    }


class TestCredentialsStorage:
    """Test credentials storage and encryption."""

    def test_store_token_creates_encrypted_file(
        self, credentials_path: Path, sample_token: dict[str, Any]
    ) -> None:
        """Store token creates encrypted credentials file."""
        from rai_pro.providers.auth.credentials import store_token

        store_token("jira", sample_token, credentials_path)

        assert credentials_path.exists()
        # File should contain encrypted data, not plaintext token
        raw_content = credentials_path.read_text(encoding="utf-8")
        assert (
            "fake-access-token-for-testing" not in raw_content
        )  # Access token not in plaintext
        assert (
            "fake-refresh-token-for-testing" not in raw_content
        )  # Refresh token not in plaintext

    def test_load_token_decrypts_successfully(
        self, credentials_path: Path, sample_token: dict[str, Any]
    ) -> None:
        """Load token decrypts stored credentials."""
        from rai_pro.providers.auth.credentials import load_token, store_token

        store_token("jira", sample_token, credentials_path)
        loaded_token = load_token("jira", credentials_path)

        assert loaded_token == sample_token
        assert loaded_token["access_token"] == "fake-access-token-for-testing"
        assert loaded_token["refresh_token"] == "fake-refresh-token-for-testing"

    def test_load_token_returns_none_when_file_missing(
        self, credentials_path: Path
    ) -> None:
        """Load token returns None when credentials file doesn't exist."""
        from rai_pro.providers.auth.credentials import load_token

        result = load_token("jira", credentials_path)

        assert result is None

    def test_load_token_returns_none_when_provider_not_found(
        self, credentials_path: Path, sample_token: dict[str, Any]
    ) -> None:
        """Load token returns None when provider not in credentials."""
        from rai_pro.providers.auth.credentials import load_token, store_token

        store_token("jira", sample_token, credentials_path)
        result = load_token("gitlab", credentials_path)  # Different provider

        assert result is None

    def test_store_token_updates_existing_provider(
        self, credentials_path: Path, sample_token: dict[str, Any]
    ) -> None:
        """Store token updates existing provider credentials."""
        from rai_pro.providers.auth.credentials import load_token, store_token

        # Store initial token
        store_token("jira", sample_token, credentials_path)

        # Update with new token
        updated_token = {**sample_token, "access_token": "new_token_abc123"}
        store_token("jira", updated_token, credentials_path)

        loaded_token = load_token("jira", credentials_path)
        assert loaded_token["access_token"] == "new_token_abc123"

    def test_multiple_providers_stored_independently(
        self, credentials_path: Path, sample_token: dict[str, Any]
    ) -> None:
        """Multiple providers can be stored in same credentials file."""
        from rai_pro.providers.auth.credentials import load_token, store_token

        jira_token = sample_token
        gitlab_token = {**sample_token, "access_token": "gitlab_token_xyz"}

        store_token("jira", jira_token, credentials_path)
        store_token("gitlab", gitlab_token, credentials_path)

        assert (
            load_token("jira", credentials_path)["access_token"]
            == "fake-access-token-for-testing"
        )
        assert (
            load_token("gitlab", credentials_path)["access_token"] == "gitlab_token_xyz"
        )

    def test_encryption_key_derivation_is_deterministic(
        self, credentials_path: Path, sample_token: dict[str, Any]
    ) -> None:
        """Encryption key derivation produces same key for same input."""
        from rai_pro.providers.auth.credentials import load_token, store_token

        # Store token twice in different sessions
        store_token("jira", sample_token, credentials_path)
        first_load = load_token("jira", credentials_path)

        # Simulate new session - should still decrypt
        second_load = load_token("jira", credentials_path)

        assert first_load == second_load == sample_token

    def test_credentials_file_has_restricted_permissions(
        self, credentials_path: Path, sample_token: dict[str, Any]
    ) -> None:
        """Credentials file is created with user-only permissions (0600)."""
        from rai_pro.providers.auth.credentials import store_token

        store_token("jira", sample_token, credentials_path)

        # Check file permissions (owner read/write only)
        stat_info = credentials_path.stat()
        permissions = oct(stat_info.st_mode)[-3:]
        assert permissions == "600", f"Expected 600, got {permissions}"
