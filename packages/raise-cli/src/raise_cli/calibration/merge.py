"""Merge logic for shared calibration sync (S-KS.3).

Append-only by design: no LWW, no updates to existing entries.
Deduplication by "id" field (e.g. "CAL-001", "CAL-E-007").

Pure function — no I/O, fully testable.
"""

from __future__ import annotations

from typing import Any


def merge_calibration(
    local_entries: list[dict[str, Any]],
    server_entries: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Merge local and server calibration entries by ID.

    Args:
        local_entries: Entries from the local calibration.jsonl file.
        server_entries: Entries downloaded from the server.

    Returns:
        A tuple (merged_local, to_push_server) where:
        - merged_local: local_entries + server entries not already in local
        - to_push_server: local entries not already on the server
    """
    local_ids = {e["id"] for e in local_entries}
    server_ids = {e["id"] for e in server_entries}

    to_add_locally = [e for e in server_entries if e["id"] not in local_ids]
    to_push = [e for e in local_entries if e["id"] not in server_ids]

    return local_entries + to_add_locally, to_push
