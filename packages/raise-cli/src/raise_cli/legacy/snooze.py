"""Snooze-hash utilities shared by ``rai clean`` and session advisory (S4).

Extracted from ``clean.py`` private helpers (D1) to avoid layering inversion
(session service must not import CLI command modules) and silent hash-drift
(D2 — both sides must hash bit-for-bit identically).

The snooze payload carries two hashes (D2, F1 fix):
- ``set_hash``: SHA256 over ALL residues (project + global), for backward-compat
  with ``rai clean --json`` output.
- ``project_set_hash``: SHA256 over project-only residues. The session advisory
  compares against this key exclusively, because session open runs only
  ``scan_project()`` (epic latency constraint).

Architecture: Epic RAISE-16227 design §S4, D1-D2.
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import UTC, datetime
from pathlib import Path

from raise_cli.config.paths import get_personal_dir
from raise_cli.legacy.models import Residue

_log = logging.getLogger(__name__)

SNOOZE_FILENAME = "legacy-scan.json"


def compute_set_hash(residues: list[Residue]) -> str:
    """SHA256 of sorted ``kind:path`` pairs.

    Moved verbatim from ``clean.py:_compute_set_hash`` (D1).
    """
    items = sorted(f"{r.kind}:{r.path}" for r in residues)
    return hashlib.sha256("\n".join(items).encode()).hexdigest()


def snooze_path(root: Path) -> Path:
    """Return the snooze file location inside the personal dir."""
    return get_personal_dir(root) / SNOOZE_FILENAME


def write_snooze(root: Path, *, set_hash: str, project_set_hash: str) -> None:
    """Write snooze file with both hash keys (best-effort).

    Extended payload (D2): ``project_set_hash`` is the project-only hash
    consumed by the session advisory; ``set_hash`` is the full project+global
    hash for backward-compat.
    """
    try:
        sp = snooze_path(root)
        sp.parent.mkdir(parents=True, exist_ok=True)
        sp.write_text(
            json.dumps({
                "set_hash": set_hash,
                "project_set_hash": project_set_hash,
                "seen_at": datetime.now(tz=UTC).isoformat(),
            })
        )
    except Exception:  # noqa: BLE001
        _log.debug("failed to write snooze file", exc_info=True)


def read_acknowledged_project_hash(root: Path) -> str | None:
    """Read the project-only hash from the snooze file.

    Returns ``None`` on: missing file, unreadable, invalid JSON,
    missing ``project_set_hash`` key, non-str value.
    """
    try:
        data = json.loads(snooze_path(root).read_text())
        value = data.get("project_set_hash")
        return value if isinstance(value, str) else None
    except Exception:  # noqa: BLE001
        return None
