# pyright: reportPrivateUsage=false
"""Tests for Ed25519 key management."""

from __future__ import annotations

from typing import TYPE_CHECKING

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from rai_agent.daemon.keys import (
    KeyPair,
    generate_keys,
    load_keys,
    load_or_generate_keys,
    save_keys,
)

if TYPE_CHECKING:
    from pathlib import Path


class TestGenerateKeys:
    """generate_keys returns a valid Ed25519 KeyPair."""

    def test_returns_keypair(self) -> None:
        kp = generate_keys()
        assert isinstance(kp, KeyPair)

    def test_private_key_type(self) -> None:
        kp = generate_keys()
        assert isinstance(kp.private_key, Ed25519PrivateKey)

    def test_public_key_type(self) -> None:
        kp = generate_keys()
        assert isinstance(kp.public_key, Ed25519PublicKey)


class TestSaveKeys:
    """save_keys writes two PEM files."""

    def test_writes_private_key_file(self, tmp_path: Path) -> None:
        kp = generate_keys()
        save_keys(kp, tmp_path)
        assert (tmp_path / "daemon.key").exists()

    def test_writes_public_key_file(self, tmp_path: Path) -> None:
        kp = generate_keys()
        save_keys(kp, tmp_path)
        assert (tmp_path / "daemon.pub").exists()

    def test_private_key_file_is_pem(self, tmp_path: Path) -> None:
        kp = generate_keys()
        save_keys(kp, tmp_path)
        content = (tmp_path / "daemon.key").read_text()
        assert "PRIVATE KEY" in content

    def test_public_key_file_is_pem(self, tmp_path: Path) -> None:
        kp = generate_keys()
        save_keys(kp, tmp_path)
        content = (tmp_path / "daemon.pub").read_text()
        assert "PUBLIC KEY" in content

    def test_private_key_has_restricted_permissions(
        self, tmp_path: Path
    ) -> None:
        kp = generate_keys()
        save_keys(kp, tmp_path)
        mode = (tmp_path / "daemon.key").stat().st_mode & 0o777
        assert mode == 0o600


class TestLoadKeys:
    """load_keys reads PEM files back correctly (roundtrip)."""

    def test_roundtrip(self, tmp_path: Path) -> None:
        original = generate_keys()
        save_keys(original, tmp_path)
        loaded = load_keys(tmp_path)

        # Verify by signing with original and verifying with loaded
        message = b"test-roundtrip"
        signature = original.private_key.sign(message)
        loaded.public_key.verify(signature, message)  # raises on failure

    def test_roundtrip_sign_with_loaded(self, tmp_path: Path) -> None:
        original = generate_keys()
        save_keys(original, tmp_path)
        loaded = load_keys(tmp_path)

        # Verify by signing with loaded and verifying with original
        message = b"test-loaded-sign"
        signature = loaded.private_key.sign(message)
        original.public_key.verify(signature, message)  # raises on failure


class TestLoadOrGenerateKeys:
    """load_or_generate_keys creates or reuses keys."""

    def test_creates_directory_and_files(self, tmp_path: Path) -> None:
        key_dir = tmp_path / ".rai"
        kp = load_or_generate_keys(key_dir)
        assert isinstance(kp.private_key, Ed25519PrivateKey)
        assert (key_dir / "daemon.key").exists()
        assert (key_dir / "daemon.pub").exists()

    def test_reuses_existing_keys(self, tmp_path: Path) -> None:
        key_dir = tmp_path / ".rai"
        first = load_or_generate_keys(key_dir)
        second = load_or_generate_keys(key_dir)

        # Same key: sign with first, verify with second
        message = b"reuse-check"
        signature = first.private_key.sign(message)
        second.public_key.verify(signature, message)  # raises on failure
