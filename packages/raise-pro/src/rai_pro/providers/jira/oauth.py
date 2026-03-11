"""JIRA OAuth 2.0 Authorization Code + PKCE flow implementation.

This module implements the OAuth 2.0 Authorization Code flow with PKCE (Proof Key
for Code Exchange) for secure authentication with JIRA Cloud. The flow includes:

1. Generate PKCE code verifier and challenge
2. Build authorization URL and redirect user to JIRA
3. Start local callback server to receive authorization code
4. Exchange authorization code for access token
5. Store encrypted credentials

References:
- RFC 7636 (PKCE): https://tools.ietf.org/html/rfc7636
- Atlassian OAuth 2.0: https://developer.atlassian.com/cloud/jira/platform/oauth-2-3lo-apps/
"""

import hashlib
import http.server
import secrets
import socketserver
import time
import webbrowser
from base64 import urlsafe_b64encode
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse

import requests

from rai_pro.providers.auth.credentials import store_token


class OAuthError(Exception):
    """OAuth flow error."""

    pass


# Default OAuth endpoints for Atlassian
ATLASSIAN_AUTH_URL = "https://auth.atlassian.com/authorize"
ATLASSIAN_TOKEN_URL = "https://auth.atlassian.com/oauth/token"  # nosec B105
DEFAULT_SCOPES = [
    "read:jira-work",
    "write:jira-work",
    "read:jira-user",
    "read:me",  # Required for /me endpoint
    "offline_access",  # Required for refresh token
]


def _generate_code_verifier() -> str:
    """Generate PKCE code verifier.

    Creates a cryptographically random string of 43-128 characters,
    using URL-safe characters (A-Z, a-z, 0-9, -, ., _, ~).

    Returns:
        Random code verifier string (128 characters).
    """
    # Generate 96 random bytes (128 characters when base64url encoded)
    random_bytes = secrets.token_bytes(96)
    verifier = urlsafe_b64encode(random_bytes).rstrip(b"=").decode("ascii")
    return verifier


def _generate_code_challenge(verifier: str) -> str:
    """Generate PKCE code challenge from verifier.

    Creates SHA256 hash of the verifier and encodes it as base64url,
    per RFC 7636 specification.

    Args:
        verifier: PKCE code verifier string.

    Returns:
        Base64url-encoded SHA256 hash of verifier (without padding).
    """
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return challenge


def _generate_state() -> str:
    """Generate random state parameter for CSRF protection.

    Returns:
        Random state string (32 characters).
    """
    return secrets.token_urlsafe(24)


def build_authorization_url(
    client_id: str,
    redirect_uri: str,
    authorization_url: str = ATLASSIAN_AUTH_URL,
    scopes: list[str] | None = None,
) -> tuple[str, str, str]:
    """Build OAuth authorization URL with PKCE parameters.

    Args:
        client_id: OAuth client ID from Atlassian app.
        redirect_uri: Callback URL (e.g., http://localhost:8080/callback).
        authorization_url: OAuth authorization endpoint URL.
        scopes: List of OAuth scopes to request.

    Returns:
        Tuple of (authorization_url, state, code_verifier) for OAuth flow.
    """
    if scopes is None:
        scopes = DEFAULT_SCOPES

    # Generate PKCE parameters
    code_verifier = _generate_code_verifier()
    code_challenge = _generate_code_challenge(code_verifier)

    # Generate state for CSRF protection
    state = _generate_state()

    # Build authorization URL
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": " ".join(scopes),
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "audience": "api.atlassian.com",  # Required for Atlassian
        "prompt": "consent",  # Force consent screen to ensure refresh token
    }

    url = f"{authorization_url}?{urlencode(params)}"

    return url, state, code_verifier


def _validate_state(expected: str, actual: str) -> None:
    """Validate OAuth state parameter to prevent CSRF attacks.

    Args:
        expected: Expected state value from initial request.
        actual: Actual state value from callback.

    Raises:
        OAuthError: If state values don't match (possible CSRF attack).
    """
    if expected != actual:
        raise OAuthError(
            f"State mismatch: expected '{expected}', got '{actual}'. "
            "Possible CSRF attack detected."
        )


def exchange_code_for_token(
    authorization_code: str,
    code_verifier: str,
    client_id: str,
    client_secret: str,
    redirect_uri: str,
    token_url: str = ATLASSIAN_TOKEN_URL,
) -> dict[str, Any]:
    """Exchange authorization code for access token using PKCE.

    Args:
        authorization_code: Authorization code from callback.
        code_verifier: PKCE code verifier from authorization request.
        client_id: OAuth client ID.
        client_secret: OAuth client secret.
        redirect_uri: Callback URL (must match authorization request).
        token_url: OAuth token endpoint URL.

    Returns:
        Token dictionary with access_token, refresh_token, expires_at, etc.

    Raises:
        OAuthError: If token exchange fails.
    """
    data = {
        "grant_type": "authorization_code",
        "code": authorization_code,
        "code_verifier": code_verifier,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
    }

    response = requests.post(token_url, data=data, timeout=30)

    if response.status_code != 200:
        error_data = response.json()
        error_code = error_data.get("error", "unknown_error")
        error_desc = error_data.get("error_description", "Unknown error")
        raise OAuthError(f"Token exchange failed: {error_code} - {error_desc}")

    token_data = response.json()

    # Add expiry timestamp
    if "expires_in" in token_data:
        token_data["expires_at"] = int(time.time()) + token_data["expires_in"]

    return token_data  # type: ignore[no-any-return]


class _CallbackHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler for OAuth callback."""

    callback_data: dict[str, str] | None = None

    def do_GET(self) -> None:  # noqa: N802
        """Handle GET request with authorization code."""
        # Parse query parameters
        parsed_path = urlparse(self.path)
        params = parse_qs(parsed_path.query)

        # Extract authorization code and state
        code = params.get("code", [None])[0]
        state = params.get("state", [None])[0]
        error = params.get("error", [None])[0]

        if error:
            error_desc = params.get("error_description", ["Unknown error"])[0]
            self.send_response(400)
            self.end_headers()
            self.wfile.write(
                f"<h1>Authorization Failed</h1><p>{error_desc}</p>".encode()
            )
            _CallbackHandler.callback_data = {"error": error_desc}
            return

        if code and state:
            # Success - send response to browser
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(
                b"<h1>Authorization Successful!</h1>"
                b"<p>You can close this window and return to the terminal.</p>"
            )

            # Store callback data for main thread
            _CallbackHandler.callback_data = {"code": code, "state": state}
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"<h1>Missing authorization code or state</h1>")

    def log_message(self, format: str, *args: Any) -> None:  # noqa: ARG002
        """Suppress log messages from callback server."""
        pass


def _start_callback_server(port: int = 8080, timeout: int = 300) -> dict[str, str]:
    """Start local HTTP server to receive OAuth callback.

    Args:
        port: Port to listen on (default: 8080).
        timeout: Maximum wait time in seconds (default: 300).

    Returns:
        Dictionary with 'code' and 'state' from callback, or 'error'.

    Raises:
        OAuthError: If callback times out or fails.
    """
    _CallbackHandler.callback_data = None

    # Allow address reuse to avoid "Address already in use" errors
    socketserver.TCPServer.allow_reuse_address = True

    with socketserver.TCPServer(("localhost", port), _CallbackHandler) as httpd:
        # Set timeout and handle single request
        httpd.timeout = 1  # Check every second

        start_time = time.time()
        while _CallbackHandler.callback_data is None:
            httpd.handle_request()

            # Check timeout
            if time.time() - start_time > timeout:
                raise OAuthError(f"OAuth callback timeout after {timeout} seconds")

    if (
        _CallbackHandler.callback_data is None
        or "error" in _CallbackHandler.callback_data
    ):
        error = (
            _CallbackHandler.callback_data.get("error", "Unknown error")
            if _CallbackHandler.callback_data
            else "No callback data received"
        )
        raise OAuthError(f"OAuth authorization failed: {error}")

    return _CallbackHandler.callback_data


def authenticate(
    client_id: str,
    client_secret: str,
    redirect_uri: str = "http://localhost:8080/callback",
    credentials_path: Path | None = None,
    scopes: list[str] | None = None,
) -> dict[str, Any]:
    """Complete OAuth 2.0 Authorization Code + PKCE flow for JIRA.

    This function orchestrates the complete OAuth flow:
    1. Build authorization URL with PKCE
    2. Open browser for user authorization
    3. Start callback server to receive code
    4. Exchange code for token
    5. Store encrypted credentials

    Args:
        client_id: OAuth client ID from Atlassian app.
        client_secret: OAuth client secret from Atlassian app.
        redirect_uri: Callback URL (default: http://localhost:8080/callback).
        credentials_path: Path to store credentials (default: ~/.rai/credentials.json).
        scopes: OAuth scopes to request (default: read/write jira-work, offline_access).

    Returns:
        Token dictionary with access_token, refresh_token, expires_at.

    Raises:
        OAuthError: If any step of the OAuth flow fails.
    """
    # Build authorization URL
    auth_url, expected_state, code_verifier = build_authorization_url(
        client_id=client_id,
        redirect_uri=redirect_uri,
        scopes=scopes,
    )

    # Open browser for user authorization
    print("Opening browser for JIRA authorization...")
    print(f"If browser doesn't open, visit: {auth_url}")
    webbrowser.open(auth_url)

    # Start callback server
    print("Waiting for authorization callback...")
    callback_data = _start_callback_server(port=8080)

    # Validate state
    _validate_state(expected_state, callback_data["state"])

    # Exchange code for token
    print("Exchanging authorization code for token...")
    token = exchange_code_for_token(
        authorization_code=callback_data["code"],
        code_verifier=code_verifier,
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
    )

    # Store credentials if path provided
    if credentials_path:
        store_token("jira", token, credentials_path)

    return token


def is_token_expired(token: dict[str, Any], buffer_seconds: int = 300) -> bool:
    """Check if OAuth token is expired or near expiry.

    Args:
        token: Token dictionary with expires_at timestamp.
        buffer_seconds: Safety buffer to refresh before actual expiry (default: 5 min).

    Returns:
        True if token is expired or within buffer window, False otherwise.
    """
    # If no expires_at field, consider expired (safe default)
    if "expires_at" not in token:
        return True

    # Check if token is expired or within safety buffer
    current_time = int(time.time())
    expires_at = token["expires_at"]

    return current_time >= (expires_at - buffer_seconds)


def refresh_access_token(
    token: dict[str, Any],
    client_id: str,
    client_secret: str,
    token_url: str = ATLASSIAN_TOKEN_URL,
) -> dict[str, Any]:
    """Refresh OAuth access token using refresh token.

    Args:
        token: Current token dictionary with refresh_token.
        client_id: OAuth client ID.
        client_secret: OAuth client secret.
        token_url: OAuth token endpoint URL.

    Returns:
        New token dictionary with refreshed access_token and expires_at.

    Raises:
        OAuthError: If refresh fails (no refresh_token, network error, invalid token).
    """
    # Verify refresh_token exists
    if "refresh_token" not in token:
        raise OAuthError(
            "Cannot refresh token: no refresh_token found. Re-authentication required."
        )

    # Exchange refresh token for new access token
    data = {
        "grant_type": "refresh_token",
        "refresh_token": token["refresh_token"],
        "client_id": client_id,
        "client_secret": client_secret,
    }

    response = requests.post(token_url, data=data, timeout=30)

    if response.status_code != 200:
        error_data = response.json()
        error_code = error_data.get("error", "unknown_error")
        error_desc = error_data.get("error_description", "Unknown error")
        raise OAuthError(f"Token refresh failed: {error_code} - {error_desc}")

    refreshed_token = response.json()

    # Add expiry timestamp
    if "expires_in" in refreshed_token:
        refreshed_token["expires_at"] = int(time.time()) + refreshed_token["expires_in"]

    return refreshed_token  # type: ignore[no-any-return]


def get_current_user(access_token: str) -> dict[str, Any]:
    """Get current authenticated user information from JIRA.

    Args:
        access_token: OAuth access token.

    Returns:
        User information dictionary with emailAddress, displayName, etc.

    Raises:
        OAuthError: If API request fails.
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }

    response = requests.get(
        "https://api.atlassian.com/me",
        headers=headers,
        timeout=10,
    )

    if response.status_code != 200:
        error_detail = response.text if response.text else "No error details"
        raise OAuthError(
            f"Failed to get user info: HTTP {response.status_code}. "
            f"Details: {error_detail}"
        )

    return response.json()  # type: ignore[no-any-return]
