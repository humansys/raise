"""Transparent pattern sync — outbox push + session-start pull (ADR-069).

Invisible to callers of PatternsBackend. When RAISE_SERVER_URL is
configured, writes enqueue to outbox and attempt immediate push.
Session start triggers pull + outbox drain.
"""

from __future__ import annotations

import json
import logging
import sqlite3
from pathlib import Path
from typing import Any

import httpx

from raise_cli.config.repo_binding import get_bound_repo
from raise_cli.memory.content_hash import content_hash
from raise_cli.storage.connection import get_project_id

logger = logging.getLogger(__name__)


_UUID_LEN = 36


def _as_server_id(original_id: str | None) -> str | None:
    """Return original_id only if it looks like a UUID, else None."""
    if not original_id or len(original_id) != _UUID_LEN or original_id.count("-") != 4:
        return None
    try:
        int(original_id.replace("-", ""), 16)
    except ValueError:
        return None
    return original_id


def _normalize_timestamp(ts: str | None) -> str:
    """Ensure timestamp is full ISO 8601 (server rejects date-only)."""
    if not ts:
        return "1970-01-01T00:00:00Z"
    if "T" not in ts:
        return f"{ts}T00:00:00Z"
    return ts


_PUSH_ENDPOINT = "/api/v2/patterns/push"
_PULL_ENDPOINT = "/api/v2/patterns/pull"
_MAX_RETRIES = 5
_BATCH_SIZE = 100


def _server_config() -> tuple[str, str] | None:
    """Return (server_url, api_key) or None if not configured."""
    from raise_cli.config.server import get_server_credentials

    return get_server_credentials()


def _get_client(server_url: str, api_key: str) -> httpx.Client:
    return httpx.Client(
        base_url=server_url,
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=httpx.Timeout(connect=5.0, read=30.0, write=30.0, pool=5.0),
    )


# ---------------------------------------------------------------------------
# Outbox: enqueue + drain
# ---------------------------------------------------------------------------


def enqueue_push(conn: sqlite3.Connection, pattern_id: str) -> None:
    """Enqueue a pattern for push to server."""
    conn.execute(
        "INSERT INTO sync_outbox (pattern_id, operation) VALUES (?, 'push')",
        (pattern_id,),
    )
    conn.commit()


def attempt_immediate_push(conn: sqlite3.Connection, pattern_id: str) -> bool:
    """Try to push a single pattern immediately. Returns True on success."""
    cfg = _server_config()
    if cfg is None:
        return False

    row = conn.execute(
        "SELECT pattern_id, type, content, context_json, scope, learned_from, "
        "positives, negatives, evaluations, updated_at, original_id, project_id "
        "FROM patterns WHERE pattern_id = ?",
        (pattern_id,),
    ).fetchone()
    if row is None:
        return False

    context = json.loads(row[3])
    chash = content_hash(row[2], row[1], context)
    server_id = _as_server_id(row[10])

    bound = get_bound_repo(Path.cwd())
    payload: dict[str, object] = {
        "patterns": [
            {
                "content": row[2],
                "type": row[1],
                "context": context,
                "scope": row[4],
                "learned_from": row[5],
                "project_id": row[11] or get_project_id(Path.cwd()),
                "positives": row[6],
                "negatives": row[7],
                "evaluations": row[8],
                "content_hash": chash,
                "server_id": server_id,
                "client_updated_at": _normalize_timestamp(row[9]),
            }
        ],
        "repo_id": bound[1] if bound else None,
    }

    try:
        client = _get_client(*cfg)
        resp = client.post(_PUSH_ENDPOINT, json=payload)
        resp.raise_for_status()
        data = resp.json()
        client.close()

        results = data.get("results", [])
        if results:
            r = results[0]
            sid = r.get("server_id")
            status = r.get("status")
            if sid and status in ("created", "updated"):
                conn.execute(
                    "UPDATE patterns SET original_id = ? WHERE pattern_id = ?",
                    (sid, pattern_id),
                )
            # Mark outbox as synced
            conn.execute(
                "UPDATE sync_outbox SET status = 'synced' "
                "WHERE pattern_id = ? AND status = 'pending'",
                (pattern_id,),
            )
            # Update sync cursor
            server_time = data.get("server_time")
            if server_time:
                _set_sync_state(conn, "patterns_last_push", server_time)
            conn.commit()
            return True
    except (httpx.HTTPError, Exception) as exc:  # noqa: BLE001
        logger.debug("Pattern push failed (will retry): %s", exc)
        conn.execute(
            "UPDATE sync_outbox SET retries = retries + 1, "
            "last_attempt = strftime('%Y-%m-%dT%H:%M:%SZ', 'now'), "
            "error_message = ? "
            "WHERE pattern_id = ? AND status = 'pending'",
            (str(exc)[:500], pattern_id),
        )
        conn.commit()
    return False


def drain_outbox(conn: sqlite3.Connection, project_id: str = "") -> dict[str, int]:  # noqa: C901
    """Batch-push pending outbox entries for *project_id*. Returns summary counts.

    When *project_id* is given, only patterns belonging to that project are
    re-enqueued, resolved, and pushed.  An empty string disables the filter
    (legacy behaviour, kept for backward compatibility).
    """
    cfg = _server_config()
    if cfg is None:
        return {"pushed": 0, "failed": 0, "skipped": 0}

    project_filter = " AND p.project_id = ?" if project_id else ""
    project_params: tuple[object, ...] = (project_id,) if project_id else ()

    # Auto re-enqueue: patterns without UUID and no pending/synced outbox entry (RAISE-6143)
    conn.execute(
        "INSERT INTO sync_outbox (pattern_id, operation) "  # noqa: S608  # nosec B608
        "SELECT p.pattern_id, 'push' FROM patterns p "
        "WHERE p.archived = 0 "
        "AND (p.original_id IS NULL OR p.original_id = '' OR LENGTH(p.original_id) < ?) "
        + project_filter
        + " AND NOT EXISTS ("
        "  SELECT 1 FROM sync_outbox o WHERE o.pattern_id = p.pattern_id "
        "  AND o.status IN ('pending', 'synced')"
        ")",
        (_UUID_LEN, *project_params),
    )
    conn.commit()

    # Auto-resolve outbox entries for patterns already linked to server
    conn.execute(
        "UPDATE sync_outbox SET status = 'synced' "  # noqa: S608  # nosec B608
        "WHERE status = 'pending' AND pattern_id IN ("
        "  SELECT o.pattern_id FROM sync_outbox o "
        "  JOIN patterns p ON o.pattern_id = p.pattern_id "
        "  WHERE o.status = 'pending' "
        "  AND p.original_id IS NOT NULL AND LENGTH(p.original_id) >= ?"
        + project_filter
        + ")",
        (_UUID_LEN, *project_params),
    )
    conn.commit()

    rows = conn.execute(
        "SELECT o.pattern_id, p.type, p.content, p.context_json, p.scope, "  # nosec B608
        "p.learned_from, p.positives, p.negatives, p.evaluations, "
        "p.updated_at, p.original_id, p.project_id "
        "FROM sync_outbox o JOIN patterns p ON o.pattern_id = p.pattern_id "
        "WHERE o.status = 'pending' AND o.retries < ?"
        + project_filter
        + " ORDER BY o.created_at ASC LIMIT ?",
        (_MAX_RETRIES, *project_params, _BATCH_SIZE),
    ).fetchall()

    if not rows:
        # Mark exhausted retries as failed
        conn.execute(
            "UPDATE sync_outbox SET status = 'failed' "
            "WHERE status = 'pending' AND retries >= ?",
            (_MAX_RETRIES,),
        )
        conn.commit()
        return {"pushed": 0, "failed": 0, "skipped": 0}

    current_slug = get_project_id(Path.cwd())
    patterns = []
    pattern_ids = []
    for r in rows:
        context = json.loads(r[3])
        chash = content_hash(r[2], r[1], context)
        server_id = _as_server_id(r[10])
        patterns.append(
            {
                "content": r[2],
                "type": r[1],
                "context": context,
                "scope": r[4],
                "learned_from": r[5],
                "project_id": r[11] or current_slug,
                "positives": r[6],
                "negatives": r[7],
                "evaluations": r[8],
                "content_hash": chash,
                "server_id": server_id,
                "client_updated_at": _normalize_timestamp(r[9]),
            }
        )
        pattern_ids.append(r[0])

    bound = get_bound_repo(Path.cwd())
    pushed = 0
    failed = 0
    try:
        client = _get_client(*cfg)
        resp = client.post(
            _PUSH_ENDPOINT,
            json={"patterns": patterns, "repo_id": bound[1] if bound else None},
        )
        resp.raise_for_status()
        data = resp.json()
        client.close()

        for result in data.get("results", []):
            idx = result.get("index", 0)
            sid = result.get("server_id")
            status = result.get("status")
            if idx < len(pattern_ids):
                pid = pattern_ids[idx]
                if status in ("created", "updated"):
                    if sid:
                        conn.execute(
                            "UPDATE patterns SET original_id = ? WHERE pattern_id = ?",
                            (sid, pid),
                        )
                    conn.execute(
                        "UPDATE sync_outbox SET status = 'synced' "
                        "WHERE pattern_id = ? AND status = 'pending'",
                        (pid,),
                    )
                    pushed += 1
                elif status == "skipped_duplicate":
                    existing_sid = result.get("existing_server_id") or sid
                    if existing_sid:
                        conn.execute(
                            "UPDATE patterns SET original_id = ? WHERE pattern_id = ?",
                            (existing_sid, pid),
                        )
                    conn.execute(
                        "UPDATE sync_outbox SET status = 'synced' "
                        "WHERE pattern_id = ? AND status = 'pending'",
                        (pid,),
                    )
                    pushed += 1
                else:
                    conn.execute(
                        "UPDATE sync_outbox SET retries = retries + 1, "
                        "last_attempt = strftime('%Y-%m-%dT%H:%M:%SZ', 'now') "
                        "WHERE pattern_id = ? AND status = 'pending'",
                        (pid,),
                    )
                    failed += 1

        server_time = data.get("server_time")
        if server_time:
            _set_sync_state(conn, "patterns_last_push", server_time)
        conn.commit()
    except (httpx.HTTPError, Exception) as exc:  # noqa: BLE001
        logger.debug("Outbox drain failed: %s", exc)
        for pid in pattern_ids:
            conn.execute(
                "UPDATE sync_outbox SET retries = retries + 1, "
                "last_attempt = strftime('%Y-%m-%dT%H:%M:%SZ', 'now'), "
                "error_message = ? "
                "WHERE pattern_id = ? AND status = 'pending'",
                (str(exc)[:500], pid),
            )
        conn.commit()
        failed = len(pattern_ids)

    return {"pushed": pushed, "failed": failed, "skipped": 0}


# ---------------------------------------------------------------------------
# Pull: fetch server patterns, merge locally (LWW: server wins)
# ---------------------------------------------------------------------------


def pull_patterns(
    conn: sqlite3.Connection,
    project_id: str = "",
    scope: str | None = None,
) -> dict[str, int]:
    """Pull patterns from server and merge into local SQLite. Returns summary."""
    cfg = _server_config()
    if cfg is None:
        return {"pulled": 0, "new": 0, "updated": 0}

    since = _get_sync_state(conn, "patterns_last_pull")
    new_count = 0
    updated_count = 0
    total_pulled = 0

    try:
        client = _get_client(*cfg)
        offset = 0
        while True:
            params: dict[str, Any] = {"limit": _BATCH_SIZE, "offset": offset}
            if since:
                params["since"] = since
            if project_id:
                params["project_id"] = project_id
            if scope is not None:
                params["scope"] = scope
            resp = client.get(_PULL_ENDPOINT, params=params)
            resp.raise_for_status()
            data = resp.json()

            patterns = data.get("patterns", [])
            for p in patterns:
                n, u = _merge_pattern(conn, p, project_id=project_id)
                new_count += n
                updated_count += u
                total_pulled += 1

            server_time = data.get("server_time")
            if server_time:
                _set_sync_state(conn, "patterns_last_pull", server_time)
            conn.commit()

            if len(patterns) < _BATCH_SIZE:
                break
            offset += _BATCH_SIZE

        client.close()
    except (httpx.HTTPError, Exception) as exc:  # noqa: BLE001
        logger.debug("Pattern pull failed: %s", exc)

    return {"pulled": total_pulled, "new": new_count, "updated": updated_count}


def _merge_pattern(
    conn: sqlite3.Connection,
    server_pattern: dict[str, Any],
    *,
    project_id: str = "",
) -> tuple[int, int]:
    """Merge a single server pattern into local SQLite. Returns (new, updated)."""
    server_id = server_pattern["server_id"]

    # Match by original_id (server_id already linked)
    row = conn.execute(
        "SELECT pattern_id FROM patterns WHERE original_id = ?",
        (server_id,),
    ).fetchone()

    if row is not None:
        # LWW: server wins — update local
        conn.execute(
            "UPDATE patterns SET content = ?, type = ?, context_json = ?, "
            "scope = ?, learned_from = ?, "
            "positives = ?, negatives = ?, evaluations = ?, updated_at = ? "
            "WHERE pattern_id = ?",
            (
                server_pattern["content"],
                server_pattern["type"],
                json.dumps(server_pattern.get("context", [])),
                server_pattern.get("scope", "project"),
                server_pattern.get("learned_from", ""),
                server_pattern.get("positives", 0),
                server_pattern.get("negatives", 0),
                server_pattern.get("evaluations", 0),
                server_pattern.get("updated_at", ""),
                row[0],
            ),
        )
        return 0, 1

    # Match by content_hash — indexed lookup (idx_patterns_content_hash),
    # not an O(n) scan recomputing content_hash() per row (S14056.3 Task 2).
    # The server already sends content_hash in the payload (ADR-069, shared
    # canonical hash) so no local recompute is needed to find the link.
    ch = server_pattern.get("content_hash", "")
    local_pid = project_id or get_project_id(Path.cwd())
    if ch:
        match = conn.execute(
            "SELECT pattern_id FROM patterns "
            "WHERE content_hash = ? AND project_id = ? AND archived = 0 LIMIT 1",
            (ch, local_pid),
        ).fetchone()
        if match is not None:
            # Link and update
            conn.execute(
                "UPDATE patterns SET original_id = ?, "
                "positives = ?, negatives = ?, evaluations = ?, updated_at = ? "
                "WHERE pattern_id = ?",
                (
                    server_id,
                    server_pattern.get("positives", 0),
                    server_pattern.get("negatives", 0),
                    server_pattern.get("evaluations", 0),
                    server_pattern.get("updated_at", ""),
                    match[0],
                ),
            )
            return 0, 1

    # No match — insert new (ROOT FIX, S14056.3 Task 2). Routes through the
    # canonical upsert_pattern writer instead of a manual next_pattern_id()+
    # INSERT — the old INSERT wrote project_id='' (no local keying, RAISE-13467)
    # and never populated content_hash, which is exactly the sync-shadow
    # duplication S14056.2 had to collapse after the fact. Keying by the
    # LOCAL project_id here does not break the sync round-trip: server
    # linkage identity is `original_id` (matched above, first branch), never
    # `project_id` — no code path treats `project_id == ''` as a
    # server-origin sentinel (verified in story design).
    from raise_cli.memory.patterns_backend import upsert_pattern

    result = upsert_pattern(
        conn,
        project_id=local_pid,
        content=server_pattern["content"],
        pattern_type=server_pattern.get("type", "process"),
        context=server_pattern.get("context", []),
        learned_from=server_pattern.get("learned_from", ""),
        scope=server_pattern.get("scope", "project"),
        positives=server_pattern.get("positives", 0),
        negatives=server_pattern.get("negatives", 0),
        evaluations=server_pattern.get("evaluations", 0),
        original_id=server_id,
        created_at=server_pattern.get("created_at")
        or server_pattern.get("updated_at", ""),
        on_conflict="merge_max",
    )
    return (1, 0) if result.action == "inserted" else (0, 1)


# ---------------------------------------------------------------------------
# Initial backfill: enqueue pre-existing local patterns to outbox
# ---------------------------------------------------------------------------


def maybe_backfill_outbox(conn: sqlite3.Connection) -> dict[str, Any]:
    """One-time backfill: enqueue local patterns without server UUID to outbox.

    Runs once per installation. After first connect, existing local patterns
    need to be pushed to the server. This enqueues them; drain_outbox() handles
    the actual push in batches.
    """
    cfg = _server_config()
    if cfg is None:
        return {"enqueued": 0, "reason": "not_configured"}

    if _get_sync_state(conn, "initial_backfill_done") == "true":
        return {"enqueued": 0, "reason": "already_done"}

    rows = conn.execute(
        "SELECT pattern_id FROM patterns "
        "WHERE archived = 0 "
        "AND (original_id = '' OR original_id IS NULL "
        "OR LENGTH(original_id) < ?)",
        (_UUID_LEN,),
    ).fetchall()

    enqueued = 0
    for (pattern_id,) in rows:
        already = conn.execute(
            "SELECT 1 FROM sync_outbox WHERE pattern_id = ?",
            (pattern_id,),
        ).fetchone()
        if not already:
            conn.execute(
                "INSERT INTO sync_outbox (pattern_id, operation) VALUES (?, 'push')",
                (pattern_id,),
            )
            enqueued += 1

    _set_sync_state(conn, "initial_backfill_done", "true")
    conn.commit()
    logger.info("Backfill: enqueued %d patterns for initial push", enqueued)
    return {"enqueued": enqueued}


# ---------------------------------------------------------------------------
# Governance: fetch from v2 session context, persist locally
# ---------------------------------------------------------------------------

_SESSION_CONTEXT_ENDPOINT = "/api/v2/session/context"


def pull_governance(conn: sqlite3.Connection, project_id: str) -> dict[str, Any]:
    """Pull governance from v2 session context endpoint and cache in SQLite."""
    cfg = _server_config()
    if cfg is None:
        return {"synced": False, "reason": "not_configured"}

    try:
        client = _get_client(*cfg)
        resp = client.get(
            _SESSION_CONTEXT_ENDPOINT,
            params={"project_id": project_id},
        )
        resp.raise_for_status()
        data = resp.json()
        client.close()
    except (httpx.HTTPError, Exception) as exc:  # noqa: BLE001
        logger.debug("Governance pull failed: %s", exc)
        return {"synced": False, "reason": str(exc)[:200]}

    gov = data.get("governance", {})
    governed_projects: list[object] = gov.get("governed_projects", [])
    evaluation_rules: list[object] = gov.get("evaluation_rules", [])
    scanner_fields: list[str] = gov.get("scanner_relevant_fields", [])

    conn.execute(
        "INSERT INTO governance_cache "
        "(project_id, governed_projects, evaluation_rules, "
        "scanner_relevant_fields, fetched_at) "
        "VALUES (?, ?, ?, ?, strftime('%Y-%m-%dT%H:%M:%SZ', 'now')) "
        "ON CONFLICT(project_id) DO UPDATE SET "
        "governed_projects = excluded.governed_projects, "
        "evaluation_rules = excluded.evaluation_rules, "
        "scanner_relevant_fields = excluded.scanner_relevant_fields, "
        "fetched_at = excluded.fetched_at",
        (
            project_id,
            json.dumps(governed_projects),
            json.dumps(evaluation_rules),
            json.dumps(scanner_fields),
        ),
    )
    conn.commit()
    return {
        "synced": True,
        "projects": len(governed_projects),
        "rules": len(evaluation_rules),
    }


# ---------------------------------------------------------------------------
# Sync state helpers
# ---------------------------------------------------------------------------


def _get_sync_state(conn: sqlite3.Connection, key: str) -> str | None:
    row = conn.execute("SELECT value FROM sync_state WHERE key = ?", (key,)).fetchone()
    return row[0] if row else None


def _set_sync_state(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute(
        "INSERT INTO sync_state (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value, "
        "updated_at = strftime('%Y-%m-%dT%H:%M:%SZ', 'now')",
        (key, value),
    )


def sync_status(conn: sqlite3.Connection) -> dict[str, Any]:
    """Return outbox status for diagnostics."""
    pending = conn.execute(
        "SELECT COUNT(*) FROM sync_outbox WHERE status = 'pending'"
    ).fetchone()[0]
    failed = conn.execute(
        "SELECT COUNT(*) FROM sync_outbox WHERE status = 'failed'"
    ).fetchone()[0]
    synced = conn.execute(
        "SELECT COUNT(*) FROM sync_outbox WHERE status = 'synced'"
    ).fetchone()[0]
    last_push = _get_sync_state(conn, "patterns_last_push")
    last_pull = _get_sync_state(conn, "patterns_last_pull")
    return {
        "pending": pending,
        "failed": failed,
        "synced": synced,
        "last_push": last_push,
        "last_pull": last_pull,
        "server_configured": _server_config() is not None,
    }
