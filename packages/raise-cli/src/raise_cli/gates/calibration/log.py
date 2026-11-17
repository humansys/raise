"""Append-only audit log for FF promotion decisions (RAISE-14679).

``promotion-log.json`` is a repo-committed, team-visible governance record
(OQ1) — a JSON array (OQ3: chosen over JSONL since promotions are rare,
steward-invoked events where human-diffability beats write-contention
safety). Read-whole -> append-in-memory -> rewrite-whole on each call.

Intentionally NOT built on ``memory/writer.py``'s JSONL append helper — that
helper's line-oriented format is for high-frequency per-session appends, a
different write profile from this log's rare, whole-array writes. Do not try
to force these two to share an implementation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from raise_cli.adapters.filesystem_adapter import FilesystemAdapter
from raise_cli.config.paths import FITNESS_FUNCTIONS_DIR, PROMOTION_LOG_FILE


def _log_path(project_root: Path) -> Path:
    """Return the absolute path to `promotion-log.json` for `project_root`."""
    return project_root / FITNESS_FUNCTIONS_DIR / PROMOTION_LOG_FILE


def read_promotion_log(project_root: Path) -> list[dict[str, Any]]:
    """Read all promotion-log entries, in insertion order.

    Returns an empty list when the log does not exist yet (fail-open — no
    promotion has ever been attempted for this project).
    """
    path = _log_path(project_root)
    if not path.exists():
        return []
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        msg = f"promotion-log.json is corrupted ({path}); please fix or remove it"
        raise ValueError(msg) from None
    return list(raw)


def append_promotion_entry(project_root: Path, entry: dict[str, Any]) -> None:
    """Append one entry to the promotion log without dropping existing ones.

    Creates `.raise/rai/fitness-functions/` and the log file on first call.
    Existing entries are always read back in full before the new entry is
    appended and the whole array is rewritten atomically (AC: no silent
    overwrites).
    """
    entries = read_promotion_log(project_root)
    entries.append(entry)

    log_path = _log_path(project_root)
    adapter = FilesystemAdapter(root=log_path.parent)
    adapter.write(Path(log_path.name), json.dumps(entries, indent=2) + "\n")
