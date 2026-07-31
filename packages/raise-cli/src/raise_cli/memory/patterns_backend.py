"""Patterns backend — Protocol + SQLite implementation.

Dual backend behind a Protocol so ``raise_pattern_query`` and
``raise_pattern_add`` run uniformly under both transports:

    stdio (Claude Code local)  → SqlitePatternsBackend
    http  (Rovo multi-tenant)  → PostgresPatternsBackend, scoped by org_id
"""

from __future__ import annotations

import json
import logging
import os
import re
import sqlite3
import sys
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any, Literal, Protocol, runtime_checkable

from raise_cli._agent_session import discover_agent_session_id
from raise_cli.memory.content_hash import content_hash

logger = logging.getLogger(__name__)

_DEFAULT_PATTERNS_PATH = Path(".raise") / "rai" / "memory" / "patterns.jsonl"


class PatternValidationError(Exception):
    """Raised when a pattern fails the quality gate in add()."""

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(reason)


def normalize_pattern_content(content: str) -> str:
    """Normalize pattern content: collapse whitespace, strip, remove trailing period.

    Emits a WARNING for patterns > 500 chars (advisory, not rejection).
    """
    result = content.strip()
    result = re.sub(r"[\t\n\r]+", " ", result)
    result = re.sub(r" {2,}", " ", result)
    result = result.strip()
    if result.endswith(".") and not result.endswith(".."):
        result = result[:-1].rstrip()
    if len(result) > 500:
        logger.warning(
            "Pattern verbose (> 500 chars, consider splitting) — %r", result[:60]
        )
    return result


@dataclass
class PruneCandidate:
    """A pattern eligible for archival."""

    pattern_id: str
    content: str
    created_at: str


@dataclass
class PruneResult:
    """Summary of a prune operation."""

    archived_count: int
    excluded_foundational: int
    excluded_with_evals: int
    total_active: int
    candidates: list[PruneCandidate] = field(default_factory=list)


def prune_stale_patterns(
    conn: sqlite3.Connection,
    project_id: str = "",
    age_days: int = 60,
    dry_run: bool = False,
) -> PruneResult:
    """Archive patterns with 0 evaluations older than age_days.

    Excludes foundational patterns (base=1). Uses strict > for the age threshold.
    """
    eligible = conn.execute(
        "SELECT pattern_id, content, created_at FROM patterns "
        "WHERE project_id = ? AND archived = 0 AND base = 0 AND evaluations = 0 "
        "AND julianday('now') - julianday(created_at) > ?",
        (project_id, age_days),
    ).fetchall()

    candidates = [
        PruneCandidate(pattern_id=r[0], content=r[1], created_at=r[2]) for r in eligible
    ]

    excluded_foundational = conn.execute(
        "SELECT COUNT(*) FROM patterns "
        "WHERE project_id = ? AND archived = 0 AND base = 1",
        (project_id,),
    ).fetchone()[0]

    excluded_with_evals = conn.execute(
        "SELECT COUNT(*) FROM patterns "
        "WHERE project_id = ? AND archived = 0 AND base = 0 AND evaluations > 0",
        (project_id,),
    ).fetchone()[0]

    if not dry_run and candidates:
        conn.execute(
            "UPDATE patterns SET archived = 1, updated_at = ? "
            "WHERE project_id = ? AND archived = 0 AND base = 0 AND evaluations = 0 "
            "AND julianday('now') - julianday(created_at) > ?",
            (date.today().isoformat(), project_id, age_days),
        )
        conn.commit()

    total_active = conn.execute(
        "SELECT COUNT(*) FROM patterns WHERE project_id = ? AND archived = 0",
        (project_id,),
    ).fetchone()[0]

    return PruneResult(
        archived_count=len(candidates),
        excluded_foundational=excluded_foundational,
        excluded_with_evals=excluded_with_evals,
        total_active=total_active,
        candidates=candidates if dry_run else [],
    )


def validate_pattern_add(
    content: str,
    context_tags: list[str],
) -> str:
    """Normalize content and validate quality gate. Returns normalized content."""
    normalized_content = normalize_pattern_content(content)
    if len(normalized_content) < 20:
        logger.warning(
            "Pattern rejected: too short (< 20 chars) — %r", normalized_content[:60]
        )
        raise PatternValidationError("too short (< 20 chars)")
    if len(normalized_content) > 1000:
        logger.warning(
            "Pattern rejected: too long (> 1000 chars) — %r", normalized_content[:60]
        )
        raise PatternValidationError("too long (> 1000 chars)")
    if not any(t.strip() for t in context_tags):
        logger.warning(
            "Pattern rejected: at least 1 context keyword required — %r",
            normalized_content[:60],
        )
        raise PatternValidationError("at least 1 context keyword required")
    # Dedup retired from here (S14056.3 DD-5): the LOWER(TRIM(content))
    # project-scoped check never saw the project_id='' sync-shadow rows
    # (S14056.2's root cause). Dedup now happens in `upsert_pattern`
    # (on_conflict="reject"), keyed by content_hash — normalization-robust
    # AND project-id-consistent.
    return normalized_content


@runtime_checkable
class PatternsBackend(Protocol):
    """Read + write contract for learned-patterns access."""

    async def query(self, keywords: list[str], limit: int) -> list[dict[str, Any]]:
        """Return patterns matching any keyword (content or context tag)."""
        ...

    async def add(
        self,
        content: str,
        context_tags: list[str],
        pattern_type: str = "technical",
        from_story: str = "",
    ) -> dict[str, Any]:
        """Add a new pattern. Returns ``{pattern_id: str}``."""
        ...

    async def reinforce(
        self,
        pattern_id: str,
        vote: int = 1,
        from_story: str = "",
    ) -> dict[str, Any]:
        """Reinforce a pattern with a vote signal. Returns status dict."""
        ...


def _log_returned_patterns(
    conn: sqlite3.Connection,
    project_id: str,
    pattern_ids: list[str],
    query_keywords: str,
) -> None:
    """Log returned pattern IDs for the current agent session.

    Silently skips when no agent session is active or on any DB error.
    Uses INSERT OR IGNORE to deduplicate across multiple queries.
    """
    if not pattern_ids:
        return
    session_id = discover_agent_session_id()
    if not session_id:
        return
    now = datetime.now(tz=UTC).isoformat()
    try:
        conn.executemany(
            "INSERT OR IGNORE INTO session_pattern_queries "
            "(project_id, session_id, pattern_id, query_keywords, returned_at) "
            "VALUES (?, ?, ?, ?, ?)",
            [(project_id, session_id, pid, query_keywords, now) for pid in pattern_ids],
        )
        conn.commit()
    except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        logger.debug("Failed to log returned patterns", exc_info=True)


class SqlitePatternsBackend:
    """SQLite-backed pattern storage. Drop-in for PatternsBackend Protocol.

    Query delegates to the graph engine (QueryEngine) with Wilson + recency
    scoring. The graph is built once per instance (lazy singleton).
    """

    def __init__(
        self,
        conn: sqlite3.Connection,
        project_id: str = "",
        project_root: Path | None = None,
    ) -> None:
        self._conn = conn
        self._pid = project_id
        self._project_root = project_root
        self._query_engine: Any = None

    def _get_query_engine(self) -> Any:
        """Build or return cached QueryEngine (lazy singleton)."""
        if self._query_engine is None:
            from raise_cli.context.builder import GraphBuilder
            from raise_core.graph.query import QueryEngine

            builder = GraphBuilder(project_root=self._project_root)
            graph = builder.build()
            self._query_engine = QueryEngine(graph)
        return self._query_engine

    @staticmethod
    def _node_to_dict(node: Any) -> dict[str, Any]:
        """Map a GraphNode to the legacy response shape."""
        metadata = node.metadata or {}
        return {
            "id": node.id,
            "type": node.type if isinstance(node.type, str) else node.type.value,
            "content": node.content,
            "context": metadata.get("context", []),
            "learned_from": metadata.get("learned_from", ""),
        }

    async def query(self, keywords: list[str], limit: int) -> list[dict[str, Any]]:
        """Return knowledge matching keywords, ranked by relevance score."""
        terms = [k for k in keywords if k]
        if not terms:
            return []
        try:
            from raise_core.graph.query import Query

            engine = self._get_query_engine()
            result = engine.query(Query(query=" ".join(terms), limit=limit))
            results = [self._node_to_dict(c) for c in result.concepts]
            _log_returned_patterns(
                self._conn, self._pid, [r["id"] for r in results], " ".join(terms)
            )
            return results
        except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
            logger.warning("pattern query via graph engine failed", exc_info=True)
            return []

    async def add(
        self,
        content: str,
        context_tags: list[str],
        pattern_type: str = "technical",
        from_story: str = "",
    ) -> dict[str, Any]:
        """Insert a new pattern into local SQLite and return its ID.

        Patterns are local-only until explicitly promoted to team scope
        via ``rai pattern promote --to team``.
        """
        normalized = validate_pattern_add(content, context_tags)
        result = upsert_pattern(
            self._conn,
            project_id=self._pid,
            content=normalized,
            pattern_type=pattern_type,
            context=context_tags,
            learned_from=from_story,
            on_conflict="reject",
        )
        self._query_engine = None

        return {"pattern_id": result.pattern_id}

    async def reinforce(
        self,
        pattern_id: str,
        vote: int = 1,
        from_story: str = "",  # noqa: ARG002
    ) -> dict[str, Any]:
        """Update reinforcement counters for a pattern."""
        if vote == 0:
            return {"status": "skipped", "pattern_id": pattern_id}
        pos_delta = 1 if vote == 1 else 0
        neg_delta = 1 if vote == -1 else 0
        # last_evaluated is a human-facing date; updated_at must be a full
        # ISO instant — a date-only value floors client_updated_at to
        # midnight and can lose an LWW race against a same-day server row
        # with a full timestamp (RAISE-11074 Q1).
        today = date.today().isoformat()
        now = datetime.now(UTC).isoformat()
        cur = self._conn.execute(
            "UPDATE patterns SET "
            "positives = positives + ?, negatives = negatives + ?, "
            "evaluations = evaluations + 1, last_evaluated = ?, "
            "updated_at = ? "
            "WHERE pattern_id = ?",
            (pos_delta, neg_delta, today, now, pattern_id),
        )
        self._conn.commit()
        if cur.rowcount == 0:
            return {"error": f"Pattern '{pattern_id}' not found"}
        row = self._conn.execute(
            "SELECT positives, negatives, evaluations FROM patterns WHERE pattern_id = ?",
            (pattern_id,),
        ).fetchone()
        return {
            "status": "updated",
            "pattern_id": pattern_id,
            "positives": row[0],
            "negatives": row[1],
            "evaluations": row[2],
        }


def next_pattern_id(conn: sqlite3.Connection, prefix: str = "PAT") -> str:
    """Generate the next sequential pattern ID from the patterns table."""
    row = conn.execute(
        "SELECT MAX(CAST(SUBSTR(pattern_id, LENGTH(?) + 2) AS INTEGER)) "
        "FROM patterns WHERE pattern_id LIKE ?",
        (prefix, f"{prefix}-%"),
    ).fetchone()
    max_n = row[0] if row and row[0] is not None else 0
    return f"{prefix}-{max_n + 1}"


# ---------------------------------------------------------------------------
# JSONL → SQLite one-shot migration
# ---------------------------------------------------------------------------


def _extract_developer_prefix(original_id: str) -> str:
    """Extract developer prefix from a pattern ID.

    'PAT-E-001'  → 'PAT-E'
    'PAT-DU-003' → 'PAT-DU'
    'BASE-001'   → 'BASE'
    'pat-123456' → 'pat'
    """
    parts = original_id.rsplit("-", 1)
    if len(parts) == 2 and parts[1].isdigit():
        return parts[0]
    return original_id


@dataclass
class UpsertResult:
    """Outcome of `upsert_pattern` — which pattern_id survived and how."""

    pattern_id: str
    action: Literal["inserted", "merged", "skipped"]


def upsert_pattern(  # noqa: PLR0913 — canonical writer, one call-site per param need
    conn: sqlite3.Connection,
    *,
    project_id: str,
    content: str,
    pattern_type: str,
    context: list[str],
    learned_from: str = "",
    mission_id: str = "",
    scope: str = "project",
    base: int = 0,
    version: int = 1,
    positives: int = 0,
    negatives: int = 0,
    evaluations: int = 0,
    last_evaluated: str | None = None,
    original_id: str = "",
    developer_prefix: str = "",
    created_at: str | None = None,
    id_prefix: str = "PAT",
    on_conflict: Literal["reject", "merge_max", "skip"] = "merge_max",
) -> UpsertResult:
    """Canonical write path for the `patterns` table (S14056.3, RAISE-14580).

    The ONLY function that INSERTs into `patterns` (AC4) — every call-site
    (interactive add, sync pull, JSONL migration, bootstrap seed) converges
    here. Computes `content_hash` (ADR-069, reused not reimplemented) and
    keys by the LOCAL `project_id` the caller resolved via
    `storage.connection.get_project_id()` — NEVER `''` and NEVER
    `get_server_slug()` (RAISE-13467). This is the root fix for the
    `project_id=''` sync-shadow duplication S14056.2 had to clean up.

    Lookup + write happen inside one transaction (`with conn:`); a
    concurrent-insert race that trips the V52 partial UNIQUE index
    (`idx_patterns_content_hash_unique`) is caught and resolved by
    re-SELECTing and applying the same `on_conflict` policy — never a
    double-insert.

    `on_conflict` is the policy applied when an active row already shares
    `(project_id, content_hash)`: `"reject"` raises
    `PatternValidationError("duplicate detected")` (preserves the
    interactive `add()` contract); `"skip"` returns the existing row
    unmodified (bootstrap seed — base patterns are the fixed source of
    truth); `"merge_max"` (default) MAX-merges `positives`/`negatives`/
    `evaluations` into the existing row — never SUM, these are re-imported
    copies of the same reinforcement history (S14056.2 DD-3) — and fills
    `original_id` if not already set. Used by sync pull and JSONL
    migration, both idempotent re-runs.
    """
    chash = content_hash(content, pattern_type, context)
    now_date = created_at or date.today().isoformat()

    with conn:
        existing = conn.execute(
            "SELECT pattern_id, positives, negatives, evaluations, original_id "
            "FROM patterns WHERE project_id = ? AND content_hash = ? AND archived = 0",
            (project_id, chash),
        ).fetchone()

        if existing is not None:
            return _resolve_conflict(
                conn,
                existing,
                positives,
                negatives,
                evaluations,
                original_id,
                on_conflict,
            )

        pattern_id = next_pattern_id(conn, id_prefix)
        try:
            conn.execute(
                "INSERT INTO patterns "
                "(pattern_id, type, content, context_json, learned_from, mission_id, "
                "scope, base, version, positives, negatives, evaluations, last_evaluated, "
                "created_at, updated_at, original_id, developer_prefix, project_id, content_hash) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    pattern_id,
                    pattern_type,
                    content,
                    json.dumps(context),
                    learned_from,
                    mission_id,
                    scope,
                    base,
                    version,
                    positives,
                    negatives,
                    evaluations,
                    last_evaluated,
                    now_date,
                    now_date,
                    original_id,
                    developer_prefix,
                    project_id,
                    chash,
                ),
            )
        except sqlite3.IntegrityError:
            # Concurrent insert won the race under the V52 partial UNIQUE
            # index — re-SELECT and apply the same conflict policy rather
            # than double-inserting.
            existing = conn.execute(
                "SELECT pattern_id, positives, negatives, evaluations, original_id "
                "FROM patterns WHERE project_id = ? AND content_hash = ? AND archived = 0",
                (project_id, chash),
            ).fetchone()
            if existing is None:
                raise
            return _resolve_conflict(
                conn,
                existing,
                positives,
                negatives,
                evaluations,
                original_id,
                on_conflict,
            )

    logger.info(
        "pattern upsert: action=inserted pattern_id=%s content_hash=%s project_id=%s",
        pattern_id,
        chash,
        project_id,
    )
    return UpsertResult(pattern_id=pattern_id, action="inserted")


def _resolve_conflict(
    conn: sqlite3.Connection,
    existing: sqlite3.Row | tuple[str, int, int, int, str],
    positives: int,
    negatives: int,
    evaluations: int,
    original_id: str,
    on_conflict: Literal["reject", "merge_max", "skip"],
) -> UpsertResult:
    """Apply the `on_conflict` policy against an already-existing active row."""
    existing_id = existing[0]
    if on_conflict == "reject":
        logger.warning(
            "Pattern rejected: duplicate detected — pattern_id=%s", existing_id
        )
        raise PatternValidationError("duplicate detected")
    if on_conflict == "skip":
        logger.info("pattern upsert: action=skipped pattern_id=%s", existing_id)
        return UpsertResult(pattern_id=existing_id, action="skipped")

    # merge_max
    merged_pos = max(existing[1], positives)
    merged_neg = max(existing[2], negatives)
    merged_eval = max(existing[3], evaluations)
    merged_original = existing[4] or original_id
    now = datetime.now(UTC).isoformat()
    conn.execute(
        "UPDATE patterns SET positives = ?, negatives = ?, evaluations = ?, "
        "original_id = ?, updated_at = ? WHERE pattern_id = ?",
        (merged_pos, merged_neg, merged_eval, merged_original, now, existing_id),
    )
    logger.info("pattern upsert: action=merged pattern_id=%s", existing_id)
    return UpsertResult(pattern_id=existing_id, action="merged")


def migrate_patterns_to_sqlite(
    conn: sqlite3.Connection,
    jsonl_path: Path | None = None,
    project_id: str = "",
) -> int:
    """Migrate patterns.jsonl to SQLite. Returns count of migrated records.

    Idempotent: skips when the source JSONL has already been renamed to
    ``.jsonl.migrated``. Safe to call with a pre-populated DB (global DB
    may already contain patterns from other projects).

    All records are imported (including ID collisions from counter resets).
    New sequential IDs are assigned in chronological order. The original ID
    is preserved in original_id and developer_prefix is extracted for
    future sync and attribution.
    """
    path = jsonl_path or _DEFAULT_PATTERNS_PATH
    if not path.exists():
        return 0

    records: list[dict[str, Any]] = []
    skipped = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            skipped += 1
            print(
                f"raise: skipping malformed pattern line: {line[:80]}", file=sys.stderr
            )

    if not records:
        return 0

    # Sort chronologically before assigning new IDs
    records.sort(key=lambda r: r.get("created") or r.get("date") or "")

    inserted_count = 0
    for rec in records:
        original_id = rec.get("id", "")
        dev_prefix = _extract_developer_prefix(original_id) if original_id else ""
        context: list[str] = rec.get("context", []) or []
        content = rec.get("content") or rec.get("pattern") or ""
        learned_from = (
            rec.get("learned_from") or rec.get("source") or rec.get("from") or ""
        )
        created = rec.get("created") or rec.get("date") or date.today().isoformat()
        upsert_pattern(
            conn,
            project_id=project_id,
            content=content,
            pattern_type=rec.get("type", "process"),
            context=context,
            learned_from=learned_from,
            mission_id=rec.get("mission_id") or "",
            scope=rec.get("scope", "project"),
            base=1 if rec.get("base") else 0,
            version=rec.get("version", 1) or 1,
            positives=rec.get("positives", 0) or 0,
            negatives=rec.get("negatives", 0) or 0,
            evaluations=rec.get("evaluations", 0) or 0,
            last_evaluated=rec.get("last_evaluated"),
            original_id=original_id,
            developer_prefix=dev_prefix,
            created_at=created,
            id_prefix=dev_prefix or "PAT",
            on_conflict="merge_max",
        )
        inserted_count += 1

    migrated_path = path.with_suffix(".jsonl.migrated")
    path.rename(migrated_path)
    suffix = f", {skipped} malformed skipped" if skipped else ""
    print(
        f"raise: migrated {path} → SQLite ({inserted_count} patterns{suffix})",
        file=sys.stderr,
    )
    return inserted_count


# ---------------------------------------------------------------------------
# Transport-based resolver
# ---------------------------------------------------------------------------


def is_http_request() -> bool:
    """True when running under the HTTP MCP transport (server in-process)."""
    return os.environ.get("RAISE_MCP_TRANSPORT", "").lower() == "http"


def get_patterns_backend(root: Path | None = None) -> PatternsBackend:
    """Resolve the right backend for the current context.

    Tri-state resolver (ADR-075):
    - RAISE_SERVER_URL set → ApiPatternsBackend (thin HTTP client).
    - RAISE_MCP_TRANSPORT=http → PostgresPatternsBackend (server in-process).
    - Neither → SqlitePatternsBackend (local offline).

    ``root`` anchors the local backend to the caller's checkout (S15457.2);
    ignored for API/Postgres backends and for legacy CLI callers (None).
    """
    from raise_cli.config.server import get_server_credentials

    creds = get_server_credentials()
    if creds is not None:
        from raise_cli.memory.api_patterns_backend import ApiPatternsBackend

        server_url, api_key = creds
        return ApiPatternsBackend(server_url=server_url, api_key=api_key)

    if is_http_request():
        from mcp.server.auth.middleware.auth_context import get_access_token
        from raise_server.mcp_mount import get_mcp_session_factory
        from raise_server.memory.patterns_backend_db import PostgresPatternsBackend

        token: Any = get_access_token()
        if token is None:
            raise RuntimeError(
                "patterns tool invoked via HTTP without valid JWT — "
                "no filesystem fallback allowed on server",
            )
        return PostgresPatternsBackend(get_mcp_session_factory(), org_id=token.org_id)

    return get_local_patterns_backend(root)


def get_local_patterns_backend(root: Path | None = None) -> PatternsBackend:
    """Return the SQLite backend regardless of server credentials.

    Reinforce on local-namespace IDs (PAT-*) must write locally even when
    RAISE_SERVER_URL is configured — the server only knows UUID ids, and
    counters propagate via the sync outbox drain (RAISE-7655).

    ``root`` anchors the backend to the caller's checkout (S15457.2);
    None preserves the legacy process-CWD resolution for CLI callers.
    """
    from raise_cli.config.paths import resolve_checkout_root
    from raise_cli.storage.connection import get_project_db, get_project_id
    from raise_cli.storage.schema import create_all

    project_root = resolve_checkout_root(root)
    conn = get_project_db(project_root)
    create_all(conn)
    local_pid = get_project_id(project_root)
    migrate_patterns_to_sqlite(conn, project_id=local_pid)
    return SqlitePatternsBackend(
        conn,
        project_id=local_pid,
        project_root=project_root,
    )
