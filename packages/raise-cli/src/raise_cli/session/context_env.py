"""Unified reader/writer for per-session ``context.env`` files.

All mutations to ``.raise/rai/sessions/<id>/context.env`` MUST go through
:func:`write_context_env` to guarantee line-replace semantics — adding or
updating one key never destroys others.

All reads MUST go through :func:`read_context_env` so the path construction
and line-parse logic live in one place.
"""

from __future__ import annotations

import re
from pathlib import Path

from raise_cli.core.files import atomic_write
from raise_cli.exceptions import ConfigurationError

_KEY_RE = re.compile(r"^RAISE_SESSION_[A-Z_]+$")


def read_context_env(project: Path, session_id: str, key: str) -> str | None:
    """Read *key* from the per-session ``context.env``.

    Returns the value string, or ``None`` if the file or key is absent.
    """
    ctx_file = project / ".raise" / "rai" / "sessions" / session_id / "context.env"
    if not ctx_file.exists():
        return None
    for line in ctx_file.read_text(encoding="utf-8").splitlines():
        if line.startswith(f"{key}="):
            return line.split("=", 1)[1].strip() or None
    return None


def write_context_env(
    project: Path,
    session_id: str,
    key: str,
    value: str,
) -> None:
    """Write *key=value* to the per-session ``context.env``, preserving other keys."""
    if not _KEY_RE.match(key):
        msg = f"key must match {_KEY_RE.pattern!r}, got {key!r}"
        raise ConfigurationError(msg)
    if not value:
        msg = "value must not be empty"
        raise ConfigurationError(msg)
    if "\n" in value:
        msg = "value must not contain newlines"
        raise ConfigurationError(msg)

    ctx_dir = project / ".raise" / "rai" / "sessions" / session_id
    ctx_file = ctx_dir / "context.env"

    lines: list[str] = []
    if ctx_file.exists():
        lines = [
            ln
            for ln in ctx_file.read_text(encoding="utf-8").splitlines()
            if ln and not ln.startswith(f"{key}=")
        ]
    lines.append(f"{key}={value}")
    ctx_dir.mkdir(parents=True, exist_ok=True)
    atomic_write(ctx_file, "\n".join(lines) + "\n")
