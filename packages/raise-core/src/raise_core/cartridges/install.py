"""Cartridge install and uninstall from .cartridge.tar.gz archives."""

from __future__ import annotations

import hashlib
import logging
import shutil
import tarfile
from pathlib import Path

logger = logging.getLogger(__name__)


class CartridgeInstallError(Exception):
    """Raised when cartridge installation or removal fails."""


def install_cartridge(archive_path: Path, target_dir: Path) -> Path:
    """Install a cartridge from a .cartridge.tar.gz archive.

    Returns the path to the installed cartridge directory.

    Raises:
        CartridgeInstallError: On checksum mismatch or if already installed.
    """
    _verify_checksum(archive_path)
    target_dir.mkdir(parents=True, exist_ok=True)

    with tarfile.open(archive_path, "r:gz") as tar:
        members = tar.getnames()
        if not members:
            msg = f"Archive is empty: {archive_path}"
            raise CartridgeInstallError(msg)

        top_level = members[0].split("/")[0]
        cartridge_dir = target_dir / top_level

        if cartridge_dir.exists():
            msg = f"Cartridge '{top_level}' already exists at {cartridge_dir}"
            raise CartridgeInstallError(msg)

        tar.extractall(path=str(target_dir), filter="data")

    return cartridge_dir


def uninstall_cartridge(name: str, target_dir: Path) -> None:
    """Remove an installed cartridge by name.

    Raises:
        CartridgeInstallError: If the cartridge is not found.
    """
    cartridge_dir = target_dir / name
    if not cartridge_dir.exists():
        msg = f"Cartridge '{name}' not found in {target_dir}"
        raise CartridgeInstallError(msg)

    shutil.rmtree(cartridge_dir)


def _verify_checksum(archive_path: Path) -> None:
    """Verify SHA-256 checksum if sidecar file exists."""
    checksum_path = archive_path.parent / f"{archive_path.name}.sha256"
    if not checksum_path.exists():
        logger.warning(
            "No checksum file found for %s — skipping verification", archive_path.name
        )
        return

    expected = checksum_path.read_text().strip().split()[0]
    actual = hashlib.sha256(archive_path.read_bytes()).hexdigest()

    if actual != expected:
        msg = f"Checksum mismatch for {archive_path.name}: expected {expected}, got {actual}"
        raise CartridgeInstallError(msg)
