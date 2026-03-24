"""Tests for JIRA OAuth 2.0 Authorization Code + PKCE flow."""

import hashlib
import time
from base64 import urlsafe_b64encode
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch
from urllib.parse import parse_qs, urlparse

import pytest


@pytest.fixture
def oauth_config() -> dict[str, str]:
    """Provide OAuth configuration for JIRA."""
    return {
        "client_id": "test-client-id",
        "client_secret": "fake-client-secret-for-testing",
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
        from rai_pro.providers.jira.oauth import _generate_code_verifier

        verifier = _generate_code_verifier()

        assert 43 <= len(verifier) <= 128
        # Should be URL-safe (alphanumeric + -._~)
        assert all(c.isalnum() or c in "-._~" for c in verifier)

    def test_generate_code_verifier_randomness(self) -> None:
        """Code verifier should be random (different each time)."""
        from rai_pro.providers.jira.oauth import _generate_code_verifier

        verifier1 = _generate_code_verifier()
        verifier2 = _generate_code_verifier()

        assert verifier1 != verifier2

    def test_generate_code_challenge_from_verifier(self) -> None:
        """Code challenge should be SHA256 hash of verifier, base64url encoded."""
        from rai_pro.providers.jira.oauth import _generate_code_challenge

        verifier = "test-verifier-12345678901234567890123456"

        challenge = _generate_code_challenge(verifier)

        # Verify it's base64url encoded SHA256
        expected_hash = hashlib.sha256(verifier.encode()).digest()
        expected_challenge = urlsafe_b64encode(expected_hash).rstrip(b"=").decode()

        assert challenge == expected_challenge

    def test_code_challenge_deterministic(self) -> None:
        """Same verifier produces same challenge."""
        from rai_pro.providers.jira.oauth import _generate_code_challenge

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
        from rai_pro.providers.jira.oauth import build_authorization_url

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
        from rai_pro.providers.jira.oauth import build_authorization_url

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
        from rai_pro.providers.jira.oauth import exchange_code_for_token

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
        from rai_pro.providers.jira.oauth import OAuthError, exchange_code_for_token

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
    @patch("rai_pro.providers.jira.oauth._start_callback_server")
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
        from rai_pro.providers.jira.oauth import authenticate

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
        with patch("rai_pro.providers.jira.oauth._generate_state") as mock_state:
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
        from rai_pro.providers.jira.oauth import OAuthError, _validate_state

        with pytest.raises(OAuthError) as exc_info:
            _validate_state(expected="state_123", actual="state_456")

        assert "state mismatch" in str(exc_info.value).lower()
        assert "CSRF" in str(exc_info.value) or "csrf" in str(exc_info.value).lower()


class TestTokenRefresh:
    """Test automatic token refresh logic."""

    def test_is_token_expired_returns_true_when_expired(self) -> None:
        """Token is considered expired when expires_at is in the past."""
        from rai_pro.providers.jira.oauth import is_token_expired

        # Token expired 1 hour ago
        expired_token = {
            "access_token": "old_token",
            "expires_at": int(time.time()) - 3600,
        }

        assert is_token_expired(expired_token) is True

    def test_is_token_expired_returns_false_when_valid(self) -> None:
        """Token is valid when expires_at is in the future."""
        from rai_pro.providers.jira.oauth import is_token_expired

        # Token expires in 1 hour
        valid_token = {
            "access_token": "valid_token",
            "expires_at": int(time.time()) + 3600,
        }

        assert is_token_expired(valid_token) is False

    def test_is_token_expired_with_buffer(self) -> None:
        """Token refresh considers safety buffer (refresh 5 min early)."""
        from rai_pro.providers.jira.oauth import is_token_expired

        # Token expires in 4 minutes (within 5-minute buffer)
        near_expiry_token = {
            "access_token": "soon_to_expire",
            "expires_at": int(time.time()) + 240,
        }

        assert is_token_expired(near_expiry_token, buffer_seconds=300) is True

    def test_is_token_expired_handles_missing_expires_at(self) -> None:
        """Token without expires_at is considered expired (safe default)."""
        from rai_pro.providers.jira.oauth import is_token_expired

        token_without_expiry = {"access_token": "token_123"}

        assert is_token_expired(token_without_expiry) is True

    @patch("requests.post")
    def test_refresh_access_token_success(
        self, mock_post: Mock, oauth_config: dict[str, str]
    ) -> None:
        """Refresh token exchanges refresh_token for new access_token."""
        from rai_pro.providers.jira.oauth import refresh_access_token

        # Mock successful refresh response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "new_access_token_abc",
            "refresh_token": "new_refresh_token_xyz",
            "token_type": "Bearer",
            "expires_in": 3600,
        }
        mock_post.return_value = mock_response

        old_token = {
            "access_token": "old_token",
            "refresh_token": "refresh_token_123",
            "expires_at": int(time.time()) - 100,
        }

        refreshed_token = refresh_access_token(
            token=old_token,
            client_id=oauth_config["client_id"],
            client_secret=oauth_config["client_secret"],
            token_url=oauth_config["token_url"],
        )

        # Verify refresh request
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[1]["data"]["grant_type"] == "refresh_token"
        assert call_args[1]["data"]["refresh_token"] == "refresh_token_123"
        assert call_args[1]["data"]["client_id"] == oauth_config["client_id"]

        # Verify refreshed token
        assert refreshed_token["access_token"] == "new_access_token_abc"
        assert refreshed_token["refresh_token"] == "new_refresh_token_xyz"
        assert "expires_at" in refreshed_token

    @patch("requests.post")
    def test_refresh_access_token_failure(
        self, mock_post: Mock, oauth_config: dict[str, str]
    ) -> None:
        """Refresh token handles invalid refresh_token errors."""
        from rai_pro.providers.jira.oauth import OAuthError, refresh_access_token

        # Mock error response (refresh token expired/revoked)
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": "invalid_grant",
            "error_description": "Refresh token expired",
        }
        mock_post.return_value = mock_response

        token = {
            "access_token": "old_token",
            "refresh_token": "expired_refresh_token",
        }

        with pytest.raises(OAuthError) as exc_info:
            refresh_access_token(
                token=token,
                client_id=oauth_config["client_id"],
                client_secret=oauth_config["client_secret"],
                token_url=oauth_config["token_url"],
            )

        assert "invalid_grant" in str(exc_info.value)

    def test_refresh_access_token_no_refresh_token(
        self, oauth_config: dict[str, str]
    ) -> None:
        """Refresh fails gracefully when token has no refresh_token."""
        from rai_pro.providers.jira.oauth import OAuthError, refresh_access_token

        token_without_refresh = {"access_token": "token_123"}

        with pytest.raises(OAuthError) as exc_info:
            refresh_access_token(
                token=token_without_refresh,
                client_id=oauth_config["client_id"],
                client_secret=oauth_config["client_secret"],
                token_url=oauth_config["token_url"],
            )

        assert "refresh_token" in str(exc_info.value).lower()
