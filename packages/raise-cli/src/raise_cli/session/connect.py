"""ConnectDescriptor — SSOT for SSH mobile re-entry.

Provides network discovery (Tailscale-first, LAN fallback) and
~/.rai/mobile.yaml persistence for rai session connect/qr/mobile-setup.

Architecture: E15815 Session Control Plane, S15815.4
"""

from __future__ import annotations

import shutil
import socket
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import yaml
from pydantic import BaseModel


class ConnectDescriptor(BaseModel, frozen=True):
    """SSH connection parameters for mobile re-entry.

    Attributes:
        host: IP address (Tailscale or LAN).
        port: SSH port, default 22.
        alias: Session alias (e.g. calm-finch).
        session_id: Runtime session identifier.
        network: Discovery method — tailscale, lan, or unknown.
        generated_at: UTC timestamp of descriptor generation.
    """

    host: str
    port: int = 22
    alias: str
    session_id: str
    network: str
    generated_at: datetime


def detect_mosh() -> bool:
    """Return True if the mosh binary is available on this host."""
    return shutil.which("mosh") is not None


def discover_tailscale_ip() -> str | None:
    """Return the Tailscale IPv4 address, or None if unavailable."""
    try:
        result = subprocess.run(
            ["tailscale", "ip", "-4"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    ip = result.stdout.strip()
    return ip if ip else None


def discover_lan_ip() -> str | None:
    """Return the primary LAN IPv4 address, or None on error."""
    try:
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)
    except OSError:
        return None


def build_descriptor(
    *,
    alias: str,
    session_id: str,
    prefer_lan: bool = False,
) -> ConnectDescriptor:
    """Build a ConnectDescriptor using the best available network.

    Tailscale is tried first unless prefer_lan is set. Falls back to
    LAN IP. If neither is available, host is set to 'unknown'.

    Args:
        alias: Session alias.
        session_id: Runtime session identifier.
        prefer_lan: Skip Tailscale and use LAN IP directly.

    Returns:
        ConnectDescriptor with the resolved host and network label.
    """
    host: str | None = None
    network = "unknown"

    if not prefer_lan:
        host = discover_tailscale_ip()
        if host:
            network = "tailscale"

    if host is None:
        host = discover_lan_ip()
        if host:
            network = "lan"

    return ConnectDescriptor(
        host=host or "unknown",
        alias=alias,
        session_id=session_id,
        network=network,
        generated_at=datetime.now(tz=UTC),
    )


def _default_mobile_yaml_path() -> Path:
    """Return the default path for mobile.yaml."""
    from raise_cli.config.paths import get_global_rai_dir

    return get_global_rai_dir() / "mobile.yaml"


def persist_descriptor(
    descriptor: ConnectDescriptor,
    *,
    path: Path | None = None,
) -> Path:
    """Write a ConnectDescriptor to YAML.

    Args:
        descriptor: The descriptor to persist.
        path: Override path (default: ~/.rai/mobile.yaml).

    Returns:
        Path where the file was written.
    """
    target = path or _default_mobile_yaml_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    data = descriptor.model_dump(mode="json")
    target.write_text(yaml.safe_dump(data, default_flow_style=False))
    return target


def load_descriptor(
    *,
    path: Path | None = None,
) -> ConnectDescriptor | None:
    """Load a ConnectDescriptor from YAML.

    Args:
        path: Override path (default: ~/.rai/mobile.yaml).

    Returns:
        ConnectDescriptor, or None if the file is missing or invalid.
    """
    target = path or _default_mobile_yaml_path()
    if not target.exists():
        return None
    try:
        data = yaml.safe_load(target.read_text())
        return ConnectDescriptor.model_validate(data)
    except Exception:  # noqa: BLE001
        return None
