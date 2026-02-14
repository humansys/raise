"""Tests for `rai backlog auth` CLI command."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from typer.testing import CliRunner

from rai_cli.cli.main import app

runner = CliRunner()


@pytest.fixture
def mock_credentials_path(tmp_path: Path) -> Path:
    """Provide temporary credentials path."""
    return tmp_path / "credentials.json"


class TestBacklogAuthCommand:
    """Test `rai backlog auth` command."""

    @patch("rai_providers.jira.oauth.authenticate")
    @patch("rai_cli.config.paths.get_credentials_path")
    def test_auth_jira_success(
        self,
        mock_get_creds_path: Mock,
        mock_authenticate: Mock,
        mock_credentials_path: Path,
    ) -> None:
        """Authenticate with JIRA provider successfully."""
        # Mock credentials path
        mock_get_creds_path.return_value = mock_credentials_path

        # Mock successful authentication
        mock_authenticate.return_value = {
            "access_token": "at_test123",
            "refresh_token": "rt_test456",
            "expires_at": 1234567890,
        }

        # Mock getting user info (email)
        with patch("rai_providers.jira.oauth.get_current_user") as mock_get_user:
            mock_get_user.return_value = {"email": "user@example.com"}

            result = runner.invoke(app, ["backlog", "auth", "--provider", "jira"])

        # Verify success
        assert result.exit_code == 0
        assert "Authenticated" in result.stdout or "authenticated" in result.stdout
        assert "user@example.com" in result.stdout

        # Verify OAuth flow was called
        mock_authenticate.assert_called_once()

    @patch("rai_providers.jira.oauth.authenticate")
    def test_auth_jira_with_custom_credentials(
        self,
        mock_authenticate: Mock,
        tmp_path: Path,
    ) -> None:
        """Authenticate with custom client credentials via env vars."""
        # Mock successful authentication
        mock_authenticate.return_value = {
            "access_token": "at_custom",
            "refresh_token": "rt_custom",
        }

        with patch("rai_providers.jira.oauth.get_current_user") as mock_get_user:
            mock_get_user.return_value = {"email": "custom@example.com"}

            # Set env vars for custom credentials
            import os

            os.environ["JIRA_CLIENT_ID"] = "custom-client-id"
            os.environ["JIRA_CLIENT_SECRET"] = "custom-client-secret"

            try:
                result = runner.invoke(app, ["backlog", "auth", "--provider", "jira"])

                assert result.exit_code == 0
                assert "custom@example.com" in result.stdout

                # Verify custom credentials were used
                call_args = mock_authenticate.call_args
                assert call_args[1]["client_id"] == "custom-client-id"
                assert call_args[1]["client_secret"] == "custom-client-secret"

            finally:
                # Cleanup env vars
                del os.environ["JIRA_CLIENT_ID"]
                del os.environ["JIRA_CLIENT_SECRET"]

    def test_auth_unsupported_provider(self) -> None:
        """Reject unsupported providers with helpful message."""
        result = runner.invoke(app, ["backlog", "auth", "--provider", "gitlab"])

        assert result.exit_code != 0
        assert "not supported" in result.stdout.lower() or "not supported" in str(
            result.exception
        ).lower()

    def test_auth_missing_provider(self) -> None:
        """Require --provider flag."""
        result = runner.invoke(app, ["backlog", "auth"])

        # Typer will show help or error about missing required option
        assert result.exit_code != 0

    @patch("rai_providers.jira.oauth.authenticate")
    def test_auth_oauth_failure(
        self,
        mock_authenticate: Mock,
    ) -> None:
        """Handle OAuth failures gracefully with error message."""
        from rai_providers.jira.oauth import OAuthError

        # Mock OAuth failure
        mock_authenticate.side_effect = OAuthError("User denied authorization")

        result = runner.invoke(app, ["backlog", "auth", "--provider", "jira"])

        assert result.exit_code != 0
        assert "denied" in result.stdout.lower() or "error" in result.stdout.lower()

    @patch("rai_providers.jira.oauth.authenticate")
    @patch("rai_cli.config.paths.get_credentials_path")
    def test_auth_network_error(
        self,
        mock_get_creds_path: Mock,
        mock_authenticate: Mock,
        mock_credentials_path: Path,
    ) -> None:
        """Handle network errors gracefully."""
        mock_get_creds_path.return_value = mock_credentials_path

        # Mock network error
        import requests

        mock_authenticate.side_effect = requests.RequestException("Network error")

        result = runner.invoke(app, ["backlog", "auth", "--provider", "jira"])

        assert result.exit_code != 0
        assert (
            "network" in result.stdout.lower() or "error" in result.stdout.lower()
        )
