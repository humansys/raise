"""Secure credentials storage with encryption for OAuth tokens.

This module provides encrypted storage for OAuth tokens using Fernet symmetric
encryption. Credentials are stored per-provider in ~/.rai/credentials.json with
user-only read/write permissions (0600).
"""

import base64
import hashlib
import json
import os
from pathlib import Path
from typing import Any, cast

from cryptography.fernet import Fernet  # type: ignore[import-untyped]


def _get_encryption_key() -> bytes:
    """Derive deterministic encryption key for current user.

    Uses a combination of user-specific system identifiers to derive a
    deterministic encryption key. The key is the same across sessions for
    the same user on the same machine.

    Returns:
        32-byte encryption key suitable for Fernet.
    """
    # Use user ID + username as seed for key derivation
    # This makes the key deterministic but user-specific
    seed = f"{os.getuid()}:{os.getenv('USER', 'unknown')}"
    key_material: bytes = hashlib.sha256(seed.encode()).digest()
    return base64.urlsafe_b64encode(key_material)


def store_token(
    provider: str,
    token: dict[str, Any],
    credentials_path: Path,
) -> None:
    """Store OAuth token with encryption for specified provider.

    Creates or updates the credentials file with encrypted token data.
    Multiple providers can be stored in the same file. The file is created
    with user-only permissions (0600) for security.

    Args:
        provider: Provider identifier (e.g., "jira", "gitlab").
        token: OAuth token dictionary containing access_token, refresh_token, etc.
        credentials_path: Path to credentials file (typically ~/.rai/credentials.json).
    """
    # Load existing credentials or start fresh
    if credentials_path.exists():
        credentials = _load_credentials_file(credentials_path)
    else:
        credentials = {}

    # Update provider token
    credentials[provider] = token

    # Encrypt and save
    _save_credentials_file(credentials, credentials_path)


def load_token(
    provider: str,
    credentials_path: Path,
) -> dict[str, Any] | None:
    """Load and decrypt OAuth token for specified provider.

    Args:
        provider: Provider identifier (e.g., "jira", "gitlab").
        credentials_path: Path to credentials file.

    Returns:
        Decrypted token dictionary, or None if file/provider doesn't exist.
    """
    if not credentials_path.exists():
        return None

    credentials = _load_credentials_file(credentials_path)
    return credentials.get(provider)


def _load_credentials_file(credentials_path: Path) -> dict[str, dict[str, Any]]:
    """Load and decrypt credentials file.

    Args:
        credentials_path: Path to encrypted credentials file.

    Returns:
        Decrypted credentials dictionary mapping provider to token.
    """
    fernet = Fernet(_get_encryption_key())  # type: ignore[no-untyped-call]

    encrypted_data: bytes = credentials_path.read_bytes()
    decrypted_data: bytes = fernet.decrypt(encrypted_data)  # type: ignore[no-untyped-call]

    return json.loads(decrypted_data)  # type: ignore[no-any-return]


def _save_credentials_file(
    credentials: dict[str, dict[str, Any]],
    credentials_path: Path,
) -> None:
    """Encrypt and save credentials file with secure permissions.

    Args:
        credentials: Credentials dictionary mapping provider to token.
        credentials_path: Path to credentials file.
    """
    fernet = Fernet(_get_encryption_key())  # type: ignore[no-untyped-call]

    # Serialize and encrypt
    json_data: bytes = json.dumps(credentials).encode()
    # Fernet.encrypt() always returns bytes
    encrypted_data = cast(
        bytes, fernet.encrypt(json_data)  # type: ignore[no-untyped-call]
    )

    # Ensure parent directory exists
    credentials_path.parent.mkdir(parents=True, exist_ok=True)

    # Write with restricted permissions (user-only read/write)
    credentials_path.write_bytes(encrypted_data)
    credentials_path.chmod(0o600)
