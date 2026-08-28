"""Local-first outbox for work_items Jira sync — S10 (RAISE-14649).

WorkItemsOutbox queues work_item changes (e.g. status transitions) to push
to Jira on reconnect. Modelled after memory/sync.py's sync_outbox pattern
but for a different entity and with simpler retry semantics.

Drain is explicit/on-demand only (no background thread — single-writer SQLite).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from raise_cli.adapters.resolve import resolve_pm_adapter
from raise_cli.storage.connection import get_project_db
from raise_cli.storage.schema import create_all

_log = logging.getLogger(__name__)

_NETWORK_ERRORS = (ConnectionError, OSError, TimeoutError)


class WorkItemsOutbox:
    """Queue and drain local work_item changes to Jira.

    Uses the ``work_items_outbox`` table created by schema V56 (_apply_v56).
    """

    def __init__(self, project: Path) -> None:
        self._conn = get_project_db(project)
        self._conn.row_factory = __import__("sqlite3").Row
        create_all(self._conn)

    def enqueue(
        self,
        work_item_id: str,
        jira_key: str | None,
        operation: str,
        payload: dict[str, object],
    ) -> None:
        """Add a pending outbox entry for the given work_item_id."""
        self._conn.execute(
            "INSERT INTO work_items_outbox (work_item_id, jira_key, operation, payload_json) "
            "VALUES (?, ?, ?, ?)",
            (work_item_id, jira_key, operation, json.dumps(payload)),
        )
        self._conn.commit()

    def pending_count(self) -> int:
        """Return the number of rows with status='pending'."""
        row = self._conn.execute(
            "SELECT COUNT(*) FROM work_items_outbox WHERE status = 'pending'"
        ).fetchone()
        return int(row[0]) if row else 0

    def drain(self) -> dict[str, int]:  # noqa: C901 — linear dispatch, not complex
        """Push pending rows to Jira adapter. Returns summary counts.

        - sent: rows successfully pushed (marked status='sent')
        - failed: rows that exhausted max_retries (marked status='failed')
        - skipped: rows without jira_key that cannot be sent (marked status='sent')

        Connection/network errors keep rows as pending (offline is not a failure).
        Other errors increment retries; exhausted rows are marked 'failed'.
        """
        rows = self._conn.execute(
            "SELECT id, work_item_id, jira_key, operation, payload_json, retries, max_retries "
            "FROM work_items_outbox WHERE status = 'pending'"
        ).fetchall()

        sent = failed = skipped = 0

        for row in rows:
            row_id: int = row["id"]
            jira_key: str | None = row["jira_key"]
            operation: str = row["operation"]
            payload: dict[str, object] = json.loads(row["payload_json"])
            retries: int = row["retries"]
            max_retries: int = row["max_retries"]

            if jira_key is None:
                self._conn.execute(
                    "UPDATE work_items_outbox SET status = 'sent' WHERE id = ?",
                    (row_id,),
                )
                skipped += 1
                continue

            try:
                adapter = resolve_pm_adapter(None)
                if operation == "transition" and "status" in payload:
                    adapter.transition_issue(jira_key, str(payload["status"]))
                self._conn.execute(
                    "UPDATE work_items_outbox SET status = 'sent' WHERE id = ?",
                    (row_id,),
                )
                sent += 1
            except _NETWORK_ERRORS:
                _log.warning(
                    "work_items_outbox drain: network error for %s — row stays pending",
                    jira_key,
                )
            except Exception as exc:  # noqa: BLE001
                new_retries = retries + 1
                if new_retries >= max_retries:
                    self._conn.execute(
                        "UPDATE work_items_outbox SET status = 'failed', "
                        "retries = ?, error_message = ? WHERE id = ?",
                        (new_retries, str(exc), row_id),
                    )
                    failed += 1
                else:
                    self._conn.execute(
                        "UPDATE work_items_outbox SET retries = ? WHERE id = ?",
                        (new_retries, row_id),
                    )

        self._conn.commit()
        return {"sent": sent, "failed": failed, "skipped": skipped}
