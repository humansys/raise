"""Ed25519 key management for the Rai daemon.

Generates, saves, and loads Ed25519 keypairs used for WebSocket
authentication (challenge-response). Keys are stored as PEM files.

Design decisions (S2.9):
  D1: Separate module from __main__ for testability
  D2: NamedTuple for KeyPair — immutable, lightweight
  D3: PEM format — standard, interoperable
  D4: Default directory ~/.rai/ — user-level, git-ignored
"""

from __future__ import annotations

from pathlib import Path
from typing import NamedTuple

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
    load_pem_private_key,
    load_pem_public_key,
)

_PRIVATE_KEY_FILE = "daemon.key"
_PUBLIC_KEY_FILE = "daemon.pub"


class KeyPair(NamedTuple):
    """Ed25519 keypair for daemon authentication."""

    private_key: Ed25519PrivateKey
    public_key: Ed25519PublicKey


def generate_keys() -> KeyPair:
    """Generate a new Ed25519 keypair."""
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    return KeyPair(private_key=private_key, public_key=public_key)


def save_keys(keys: KeyPair, directory: Path) -> None:
    """Write keypair as PEM files (daemon.key, daemon.pub).

    Args:
        keys: The keypair to save.
        directory: Directory to write PEM files into.
    """
    directory.mkdir(parents=True, exist_ok=True)

    private_pem = keys.private_key.private_bytes(
        encoding=Encoding.PEM,
        format=PrivateFormat.PKCS8,
        encryption_algorithm=NoEncryption(),
    )
    private_path = directory / _PRIVATE_KEY_FILE
    private_path.write_bytes(private_pem)
    private_path.chmod(0o600)

    public_pem = keys.public_key.public_bytes(
        encoding=Encoding.PEM,
        format=PublicFormat.SubjectPublicKeyInfo,
    )
    (directory / _PUBLIC_KEY_FILE).write_bytes(public_pem)


def load_keys(directory: Path) -> KeyPair:
    """Read keypair from PEM files (daemon.key, daemon.pub).

    Args:
        directory: Directory containing PEM files.

    Returns:
        Loaded KeyPair.

    Raises:
        FileNotFoundError: If PEM files do not exist.
    """
    private_pem = (directory / _PRIVATE_KEY_FILE).read_bytes()
    private_key = load_pem_private_key(private_pem, password=None)
    if not isinstance(private_key, Ed25519PrivateKey):
        msg = f"Expected Ed25519PrivateKey, got {type(private_key).__name__}"
        raise TypeError(msg)

    public_pem = (directory / _PUBLIC_KEY_FILE).read_bytes()
    public_key = load_pem_public_key(public_pem)
    if not isinstance(public_key, Ed25519PublicKey):
        msg = f"Expected Ed25519PublicKey, got {type(public_key).__name__}"
        raise TypeError(msg)

    return KeyPair(private_key=private_key, public_key=public_key)


def load_or_generate_keys(directory: Path | None = None) -> KeyPair:
    """Load keys if they exist, otherwise generate and save new ones.

    Args:
        directory: Directory for PEM files. Defaults to ``~/.rai/``.

    Returns:
        Loaded or newly generated KeyPair.
    """
    if directory is None:
        directory = Path.home() / ".rai"

    private_path = directory / _PRIVATE_KEY_FILE
    public_path = directory / _PUBLIC_KEY_FILE

    if private_path.exists() and public_path.exists():
        return load_keys(directory)

    keys = generate_keys()
    save_keys(keys, directory)
    return keys
