"""Tests for JIRA OAuth 2.0 Authorization Code + PKCE flow."""

import hashlib
import secrets
from base64 import urlsafe_b64encode
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, Mock, patch
from urllib.parse import parse_qs, urlparse

import pytest


@pytest.fixture
def oauth_config() -> dict[str, str]:
    """Provide OAuth configuration for JIRA."""
    return {
        "client_id": "test-client-id",
        "client_secret": "test-client-secret",
        "redirect_uri": "http://localhost:8080/callback",
        "authorization_url": "https://auth.atlassian.com/authorize",
        "token_url": "https://auth.atlassian.com/oauth/token",
        "scopes": ["read:jira-work", "write:jira-work", "read:jira-user"],
    }


@pytest.fixture
def mock_credentials_path(tmp_path: Path) -> Path:
    """Provide temporary credentials path."""
    return tmp_path / "credentials.json"


class TestPKCEGeneration:
    """Test PKCE code verifier and challenge generation."""

    def test_generate_code_verifier_length(self) -> None:
        """Code verifier should be 43-128 characters."""
        from rai_providers.jira.oauth import _generate_code_verifier

        verifier = _generate_code_verifier()

        assert 43 <= len(verifier) <= 128
        # Should be URL-safe (alphanumeric + -._~)
        assert all(c.isalnum() or c in "-._~" for c in verifier)

    def test_generate_code_verifier_randomness(self) -> None:
        """Code verifier should be random (different each time)."""
        from rai_providers.jira.oauth import _generate_code_verifier

        verifier1 = _generate_code_verifier()
        verifier2 = _generate_code_verifier()

        assert verifier1 != verifier2

    def test_generate_code_challenge_from_verifier(self) -> None:
        """Code challenge should be SHA256 hash of verifier, base64url encoded."""
        from rai_providers.jira.oauth import _generate_code_challenge

        verifier = "test-verifier-12345678901234567890123456"

        challenge = _generate_code_challenge(verifier)

        # Verify it's base64url encoded SHA256
        expected_hash = hashlib.sha256(verifier.encode()).digest()
        expected_challenge = urlsafe_b64encode(expected_hash).rstrip(b"=").decode()

        assert challenge == expected_challenge

    def test_code_challenge_deterministic(self) -> None:
        """Same verifier produces same challenge."""
        from rai_providers.jira.oauth import _generate_code_challenge

        verifier = "consistent-verifier-value"

        challenge1 = _generate_code_challenge(verifier)
        challenge2 = _generate_code_challenge(verifier)

        assert challenge1 == challenge2


class TestAuthorizationURL:
    """Test OAuth authorization URL construction."""

    def test_build_authorization_url_structure(
        self, oauth_config: dict[str, str]
    ) -> None:
        """Authorization URL contains required OAuth parameters."""
        from rai_providers.jira.oauth import build_authorization_url

        url, state, verifier = build_authorization_url(
            client_id=oauth_config["client_id"],
            redirect_uri=oauth_config["redirect_uri"],
            authorization_url=oauth_config["authorization_url"],
            scopes=oauth_config["scopes"],
        )

        parsed = urlparse(url)
        params = parse_qs(parsed.query)

        assert parsed.scheme == "https"
        assert parsed.netloc == "auth.atlassian.com"
        assert parsed.path == "/authorize"

        # Required OAuth parameters
        assert params["client_id"][0] == oauth_config["client_id"]
        assert params["redirect_uri"][0] == oauth_config["redirect_uri"]
        assert params["response_type"][0] == "code"
        assert params["scope"][0] == " ".join(oauth_config["scopes"])

        # PKCE parameters
        assert "code_challenge" in params
        assert params["code_challenge_method"][0] == "S256"

        # CSRF protection
        assert "state" in params

    def test_build_authorization_url_returns_state_and_verifier(
        self, oauth_config: dict[str, str]
    ) -> None:
        """Authorization URL returns state and verifier for later validation."""
        from rai_providers.jira.oauth import build_authorization_url

        url, state, verifier = build_authorization_url(
            client_id=oauth_config["client_id"],
            redirect_uri=oauth_config["redirect_uri"],
            authorization_url=oauth_config["authorization_url"],
            scopes=oauth_config["scopes"],
        )

        # State should be random string
        assert len(state) >= 16
        assert state.replace("-", "").replace("_", "").isalnum()

        # Verifier should be PKCE-compliant
        assert 43 <= len(verifier) <= 128


class TestTokenExchange:
    """Test OAuth token exchange."""

    @patch("requests.post")
    def test_exchange_code_for_token_success(
        self,
        mock_post: Mock,
        oauth_config: dict[str, str],
        mock_credentials_path: Path,
    ) -> None:
        """Exchange authorization code for access token using PKCE verifier."""
        from rai_providers.jira.oauth import exchange_code_for_token

        # Mock successful token response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "at_abc123",
            "refresh_token": "rt_xyz789",
            "token_type": "Bearer",
            "expires_in": 3600,
        }
        mock_post.return_value = mock_response

        authorization_code = "auth_code_12345"
        code_verifier = "test-verifier-43chars-minimum-length-required"

        token = exchange_code_for_token(
            authorization_code=authorization_code,
            code_verifier=code_verifier,
            client_id=oauth_config["client_id"],
            client_secret=oauth_config["client_secret"],
            redirect_uri=oauth_config["redirect_uri"],
            token_url=oauth_config["token_url"],
        )

        # Verify token exchange request
        mock_post.assert_called_once()
        call_args = mock_post.call_args

        assert call_args[0][0] == oauth_config["token_url"]
        assert call_args[1]["data"]["grant_type"] == "authorization_code"
        assert call_args[1]["data"]["code"] == authorization_code
        assert call_args[1]["data"]["code_verifier"] == code_verifier
        assert call_args[1]["data"]["client_id"] == oauth_config["client_id"]
        assert call_args[1]["data"]["redirect_uri"] == oauth_config["redirect_uri"]

        # Verify returned token
        assert token["access_token"] == "at_abc123"
        assert token["refresh_token"] == "rt_xyz789"
        assert token["token_type"] == "Bearer"
        assert "expires_at" in token  # Should add expiry timestamp

    @patch("requests.post")
    def test_exchange_code_for_token_failure(
        self, mock_post: Mock, oauth_config: dict[str, str]
    ) -> None:
        """Token exchange handles error responses."""
        from rai_providers.jira.oauth import OAuthError, exchange_code_for_token

        # Mock error response
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": "invalid_grant",
            "error_description": "Authorization code expired",
        }
        mock_post.return_value = mock_response

        with pytest.raises(OAuthError) as exc_info:
            exchange_code_for_token(
                authorization_code="expired_code",
                code_verifier="verifier",
                client_id=oauth_config["client_id"],
                client_secret=oauth_config["client_secret"],
                redirect_uri=oauth_config["redirect_uri"],
                token_url=oauth_config["token_url"],
            )

        assert "invalid_grant" in str(exc_info.value)


class TestOAuthFlow:
    """Test complete OAuth flow integration."""

    @patch("webbrowser.open")
    @patch("rai_providers.jira.oauth._start_callback_server")
    @patch("requests.post")
    def test_complete_oauth_flow(
        self,
        mock_post: Mock,
        mock_callback_server: Mock,
        mock_browser: Mock,
        oauth_config: dict[str, str],
        mock_credentials_path: Path,
    ) -> None:
        """Complete OAuth flow: authorize → callback → token exchange → store."""
        from rai_providers.jira.oauth import authenticate

        # Mock callback server returning authorization code and state
        mock_callback_server.return_value = {
            "code": "auth_code_from_jira",
            "state": "mock_state_value",
        }

        # Mock token exchange response
        mock_token_response = MagicMock()
        mock_token_response.status_code = 200
        mock_token_response.json.return_value = {
            "access_token": "at_complete_flow",
            "refresh_token": "rt_complete_flow",
            "token_type": "Bearer",
            "expires_in": 3600,
        }
        mock_post.return_value = mock_token_response

        # Run complete flow
        with patch("rai_providers.jira.oauth._generate_state") as mock_state:
            mock_state.return_value = "mock_state_value"

            token = authenticate(
                client_id=oauth_config["client_id"],
                client_secret=oauth_config["client_secret"],
                redirect_uri=oauth_config["redirect_uri"],
                credentials_path=mock_credentials_path,
            )

        # Verify browser was opened with authorization URL
        mock_browser.assert_called_once()
        auth_url = mock_browser.call_args[0][0]
        assert "auth.atlassian.com" in auth_url
        assert "code_challenge" in auth_url

        # Verify callback server was started
        mock_callback_server.assert_called_once()

        # Verify token was returned
        assert token["access_token"] == "at_complete_flow"
        assert token["refresh_token"] == "rt_complete_flow"

    def test_state_mismatch_raises_error(self) -> None:
        """OAuth flow validates state parameter to prevent CSRF."""
        from rai_providers.jira.oauth import OAuthError, _validate_state

        with pytest.raises(OAuthError) as exc_info:
            _validate_state(expected="state_123", actual="state_456")

        assert "state mismatch" in str(exc_info.value).lower()
        assert "CSRF" in str(exc_info.value) or "csrf" in str(exc_info.value).lower()
