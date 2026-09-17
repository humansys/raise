"""Harness binary detection (RAISE-17423).

Deterministic PATH probing — no inference, no network. Uses ``shutil.which``
to find installed harness binaries.
"""

from __future__ import annotations

import shutil
from pathlib import Path

KNOWN_HARNESS_BINARIES: tuple[str, ...] = ("claude", "codex", "kimi-k3")


def detect_installed_harnesses() -> dict[str, Path]:
    """Return installed harness binaries found in PATH.

    Probes each known harness name with ``shutil.which()``. Only returns
    entries for binaries that are actually present.
    """
    installed: dict[str, Path] = {}
    for name in KNOWN_HARNESS_BINARIES:
        path = shutil.which(name)
        if path is not None:
            installed[name] = Path(path)
    return installed
