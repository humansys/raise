"""SQLite-backed graph backend over the canonical V68 graph schema."""

from __future__ import annotations

import json
import logging
import sqlite3
import time
from pathlib import Path
from typing import Any, cast

import networkx as nx  # type: ignore[import-untyped]

from raise_cli.config.paths import checkout_scope_id
from raise_cli.storage.schema import create_all
from raise_core.graph.backends.models import BackendHealth
from raise_core.graph.engine import Graph
from raise_core.graph.models import GraphNode

JsonDict = dict[str, Any]
NodeRow = tuple[
    str, str, str, str | None, str, str, str, int, int, str, str | None, str
]
EdgeRow = tuple[str, str, str, str, str, str]
GraphNodeRow = tuple[str, str, str, str | None, str, str]
#: node_id, node_type, content, source_file, metadata_json, created_at, updated_at
BacklogNodeRow = tuple[str, str, str, str | None, str, str, str]

#: ``checkout_id`` of rows that belong to the repository as a whole rather than
#: to one checkout of it — cartridge nodes, shared by every worktree/clone.
REPO_WIDE = ""

#: Backlog issue-instance node types surfaced in the session-context
#: "backlog" section (RAISE-16427 / RAISE-16402 cartridge generator).
#: Length must match the literal ``(?, ?, ?, ?)`` placeholder count in
#: ``_fetch_backlog_item_rows`` — kept as literals there (not an f-string)
#: to avoid a SQL-injection lint false-positive on dynamic placeholder count.
_BACKLOG_NODE_PREFIX = "backlog."
_BACKLOG_MODEL_TYPES = frozenset(
    {
        "backlog.custom_field",
        "backlog.business_rule",
        "backlog.workflow_state",
        "backlog.issue_type",
    }
)

__all__ = ["AUTHORITY_ORDER", "REPO_WIDE", "SQLiteGraphBackend"]

logger = logging.getLogger(__name__)

#: Authority ladder for DDD annotation precedence (D3, ADR-148, RAISE-16850).
#: A write with authority rank <= the existing row's rank is rejected (no-op).
#: Rank 0 is reserved for unknown/missing ddd_source values (lowest authority).
#: ratified > yaml-derived > pass2 > propagated > pass1 > (unknown=0)
AUTHORITY_ORDER: dict[str, int] = {
    "ratified": 50,
    "yaml-derived": 40,
    "pass2": 30,
    "propagated": 20,
    "pass1": 10,
}


class SQLiteGraphBackend:
    """Graph backend that stores checkout-scoped graph rows in SQLite.

    Rows are keyed by ``(project_id, checkout_id, ...)``. ``project_id`` comes
    from ``.raise/manifest.yaml``, which is git-tracked and therefore identical
    in every worktree and every clone of a repo — on its own it is NOT an
    isolation key (RAISE-15607). ``checkout_id`` is the resolved checkout root
    path and separates one working tree's index from another's.

    ``checkout_id`` is assigned by the WRITER, never inferred from a node's
    type: ``persist()`` / ``upsert_nodes()`` write this backend's checkout
    scope, ``upsert_cartridge_nodes()`` always writes ``REPO_WIDE``.

    Reads return ``checkout_id IN (REPO_WIDE, self.checkout_id)``; when the same
    ``node_id`` exists in both scopes the checkout row wins.

    ``checkout_id`` defaults to ``REPO_WIDE`` so cartridge-only call sites need
    no argument. A backend left on that default persists into the repo-wide
    partition — production scan writers must pass ``resolve_checkout_root()``.
    """

    def __init__(
        self, project_id: str, db_path: Path, checkout_id: str = REPO_WIDE
    ) -> None:
        if not project_id:
            raise ValueError("project_id cannot be empty")
        self.project_id = project_id
        self.db_path = db_path
        self.checkout_id = checkout_scope_id(checkout_id)
        # RAISE-16611: names of the metadata keys that _load_from_connection()
        # merged in from graph_node_annotations, per node_id. Populated by the
        # most recent load() on this instance; consulted by
        # _node_column_values() so a subsequent persist()/upsert_nodes() never
        # writes annotation-sourced keys back into graph_nodes.metadata_json.
        self._annotation_keys_by_node: dict[str, set[str]] = {}
        # RAISE-16612: partition provenance for each node loaded by the most
        # recent load() on this instance. Stores the winning checkout_id for
        # each node_id ('' for REPO_WIDE-only nodes, self.checkout_id when the
        # checkout row wins the merge). Used by persist()/upsert_nodes() to
        # route nodes back to their origin partition instead of blindly writing
        # everything to self.checkout_id — which would duplicate REPO_WIDE
        # cartridge nodes into the checkout partition on every round trip.
        self._node_origin_checkout: dict[str, str] = {}

    @property
    def _visible_scopes(self) -> tuple[str, str, str]:
        """Bind params for ``project_id = ? AND checkout_id IN ('', ?)``."""
        return (self.project_id, REPO_WIDE, self.checkout_id)

    def backend_name(self) -> str:
        """Return the backend display name."""
        return "sqlite"

    def storage_location(self) -> str:
        """Return the SQLite database path."""
        return str(self.db_path)

    def _open(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=5000")
        create_all(conn)
        return conn

    def _load_json_dict(self, value: str | None) -> JsonDict:
        try:
            loaded = json.loads(value or "{}")
        except json.JSONDecodeError:
            return {}
        if isinstance(loaded, dict):
            return cast("JsonDict", loaded)
        return {}

    def _node_metadata(self, attrs: JsonDict) -> JsonDict:
        metadata = attrs.get("metadata")
        if isinstance(metadata, dict):
            return cast("JsonDict", metadata)
        return {}

    def _strip_annotation_keys(self, node_id: str, metadata: JsonDict) -> JsonDict:
        """Remove annotation-sourced keys before serializing to metadata_json.

        RAISE-16611: ``_load_from_connection()`` merges ``graph_node_annotations``
        payloads into ``node.metadata`` to give consumers one flat read view
        (RAISE-16596), with no marker distinguishing annotation-sourced keys
        from structural ones. Writing that merged dict straight back into
        ``metadata_json`` re-denormalizes annotation state into the structural
        table: retracting or narrowing an annotation then silently no-ops
        because a stale copy is baked into ``graph_nodes``. Only the keys
        recorded here — per ``node_id``, during the most recent ``load()`` on
        this backend instance — are stripped; everything else (structural
        facts, or metadata from a node this instance never loaded) passes
        through unchanged.
        """
        annotation_keys = self._annotation_keys_by_node.get(node_id)
        if not annotation_keys:
            return metadata
        return {k: v for k, v in metadata.items() if k not in annotation_keys}

    def _node_column_values(
        self, node_id: str, attrs: JsonDict, checkout_id: str
    ) -> tuple[object, ...]:
        metadata = self._node_metadata(attrs)
        node_type = str(attrs.get("type", ""))
        source_file = attrs.get("source_file")
        if source_file is None:
            source_file = ""
        module_id = ""
        if node_type == "module":
            module_id = node_id
        elif isinstance(metadata.get("module"), str):
            module_id = str(metadata["module"])
        stored_metadata = self._strip_annotation_keys(node_id, metadata)
        return (
            self.project_id,
            checkout_id,
            node_id,
            node_type,
            str(attrs.get("content", "")),
            str(source_file),
            json.dumps(stored_metadata, default=str),
            str(metadata.get("release_id", "")),
            module_id,
            1 if metadata.get("always_on") is True else 0,
            1 if metadata.get("foundational") is True else 0,
            str(attrs.get("created", "")),
        )

    def upsert_cartridge_nodes(
        self, cartridge_name: str, nodes: list[GraphNode]
    ) -> int:
        """Insert cartridge nodes, replacing any previous nodes for this cartridge.

        Cartridge nodes are REPO_WIDE (``checkout_id = ''``): they are installed
        once per repository and visible from every checkout. The scope is set
        here by the writer and never taken from ``self.checkout_id``, so a
        backend constructed for a checkout cannot accidentally fork the
        cartridge partition (RAISE-15607).

        Scoped delete: only removes repo-wide nodes whose metadata_json contains
        this cartridge_name. Other cartridges, every checkout partition, and
        non-cartridge nodes are untouched.
        """
        conn = self._open()
        try:
            with conn:
                conn.execute(
                    """
                    DELETE FROM graph_nodes
                    WHERE project_id = ?
                      AND checkout_id = ?
                      AND json_extract(metadata_json, '$.cartridge_name') = ?
                    """,
                    (self.project_id, REPO_WIDE, cartridge_name),
                )
                for node in nodes:
                    metadata = dict(node.metadata)
                    metadata["cartridge_name"] = cartridge_name
                    attrs: JsonDict = {
                        "type": node.type,
                        "content": node.content,
                        "source_file": node.source_file,
                        "metadata": metadata,
                        "created": node.created,
                    }
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO graph_nodes (
                            project_id, checkout_id, node_id, node_type, content,
                            source_file, metadata_json, release_id, module_id,
                            always_on, foundational, created_at
                        ) VALUES (
                            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                            COALESCE(NULLIF(?, ''), strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
                        )
                        """,
                        self._node_column_values(node.id, attrs, REPO_WIDE),
                    )
            return len(nodes)
        finally:
            conn.close()

    def upsert_annotations(
        self,
        namespace: str,
        payloads: dict[str, JsonDict],
        *,
        checkout_id: str | None = None,
    ) -> None:
        """Write durable node annotations (RAISE-16596).

        Structurally separate from ``graph_nodes``: ``persist()`` and
        ``upsert_nodes()`` never touch ``graph_node_annotations``, so a
        structural rebuild (``GraphAutoUpdateHook``, or any future
        ``GraphBuilder.build()`` -> ``persist()`` call) cannot destroy an
        annotation written here, regardless of call-site discipline
        elsewhere.

        ``checkout_id`` defaults to ``self.checkout_id`` — no implicit
        ``REPO_WIDE``. A caller must explicitly pass ``checkout_id=REPO_WIDE``
        to share a namespace across worktrees (e.g. DDD classification,
        which is a property of the symbol's content, not the worktree).

        For the ``"ddd"`` namespace, enforces the authority ladder (D3,
        ADR-148, RAISE-16850): ratified > yaml-derived > pass2 > propagated
        > pass1. A write at lower authority than the existing row is rejected
        with a warning log — the existing row is never degraded. The ladder
        is enforced here, not at call-sites, so no code path can bypass it.

        All writes record provenance columns (D4, ADR-148, RAISE-16850):
        ``written_by_checkout`` and ``written_at_ms`` (epoch milliseconds).
        """
        scope = (
            checkout_scope_id(checkout_id)
            if checkout_id is not None
            else self.checkout_id
        )
        now_ms = int(time.time() * 1000)
        conn = self._open()
        try:
            with conn:
                for node_id, payload in payloads.items():
                    if namespace == "ddd":
                        # Authority ladder: read existing row's ddd_source before write.
                        existing_row = conn.execute(
                            """
                            SELECT payload_json FROM graph_node_annotations
                            WHERE project_id = ? AND checkout_id = ?
                              AND node_id = ? AND namespace = ?
                            """,
                            (self.project_id, scope, node_id, namespace),
                        ).fetchone()
                        if existing_row is not None:
                            try:
                                existing_payload: JsonDict = json.loads(
                                    existing_row[0] or "{}"
                                )
                            except json.JSONDecodeError:
                                existing_payload = {}
                            existing_source = str(
                                existing_payload.get("ddd_source", "")
                            )
                            new_source = str(payload.get("ddd_source", ""))
                            existing_rank = AUTHORITY_ORDER.get(existing_source, 0)
                            new_rank = AUTHORITY_ORDER.get(new_source, 0)
                            if new_rank < existing_rank:
                                logger.warning(
                                    "upsert_annotations: rejected lower-authority write for "
                                    "node=%r (existing=%r rank=%d, attempted=%r rank=%d) "
                                    "in namespace=%r scope=%r",
                                    node_id,
                                    existing_source,
                                    existing_rank,
                                    new_source,
                                    new_rank,
                                    namespace,
                                    scope,
                                )
                                continue  # no-op: existing row has higher authority

                    conn.execute(
                        """
                        INSERT INTO graph_node_annotations (
                            project_id, checkout_id, node_id, namespace,
                            payload_json, updated_at,
                            written_by_checkout, written_at_ms
                        ) VALUES (
                            ?, ?, ?, ?, ?, strftime('%Y-%m-%dT%H:%M:%SZ', 'now'),
                            ?, ?
                        )
                        ON CONFLICT(project_id, checkout_id, node_id, namespace)
                        DO UPDATE SET
                            payload_json        = excluded.payload_json,
                            updated_at          = excluded.updated_at,
                            written_by_checkout = excluded.written_by_checkout,
                            written_at_ms       = excluded.written_at_ms
                        """,
                        (
                            self.project_id,
                            scope,
                            node_id,
                            namespace,
                            json.dumps(payload, default=str),
                            scope,
                            now_ms,
                        ),
                    )
        finally:
            conn.close()

    def load_annotations(self, namespace: str) -> dict[str, JsonDict]:
        """Read durable node annotations for ``namespace``.

        Same REPO_WIDE-then-checkout scope precedence as node reads: when a
        node_id has both a repo-wide and a checkout-scoped annotation row for
        this namespace, the checkout-scoped row wins.
        """
        conn = self._open()
        try:
            rows = conn.execute(
                """
                SELECT node_id, payload_json
                FROM graph_node_annotations
                WHERE project_id = ?
                  AND checkout_id IN (?, ?)
                  AND namespace = ?
                ORDER BY node_id, checkout_id
                """,
                (*self._visible_scopes, namespace),
            ).fetchall()
        finally:
            conn.close()
        result: dict[str, JsonDict] = {}
        for node_id, payload_json in rows:
            result[str(node_id)] = self._load_json_dict(payload_json)
        return result

    def list_cartridge_installations(
        self,
    ) -> list[tuple[str, str, str, int, str, str]]:
        """Return installed cartridges.

        Tuples are (name, source, status, node_count, installed_at, policy).
        """
        conn = self._open()
        try:
            rows = conn.execute(
                """
                SELECT cartridge_name, source, status, node_count, installed_at,
                       policy
                FROM cartridge_installations
                WHERE project_id = ?
                ORDER BY cartridge_name
                """,
                (self.project_id,),
            ).fetchall()
            return [
                (str(r[0]), str(r[1]), str(r[2]), int(r[3]), str(r[4]), str(r[5]))
                for r in rows
            ]
        finally:
            conn.close()

    def cartridge_node_counts(self, cartridge_names: list[str]) -> dict[str, int]:
        """Return live graph-node counts for cartridges visible to this checkout.

        Installation metadata keeps the size observed at install time. This
        query deliberately reads ``graph_nodes`` instead, so callers presenting
        active-checkout evidence do not confuse historical size with live data.
        It recognizes both server-install (``cartridge_name``) and filesystem
        cartridge (``cartridge``) provenance. Requested cartridges without live
        nodes are included with a zero count.
        """
        names = list(dict.fromkeys(cartridge_names))
        counts = dict.fromkeys(names, 0)
        if not names:
            return counts

        conn = self._open()
        try:
            rows = conn.execute(
                """
                WITH visible AS (
                    SELECT metadata_json,
                           ROW_NUMBER() OVER (
                               PARTITION BY node_id
                               ORDER BY CASE
                                            WHEN checkout_id = ? THEN 0
                                            ELSE 1
                                        END
                           ) AS scope_precedence
                    FROM graph_nodes
                    WHERE project_id = ?
                      AND checkout_id IN (?, ?)
                ),
                attributed AS (
                    SELECT CASE
                               WHEN NOT json_valid(metadata_json) THEN NULL
                               WHEN json_type(
                                        metadata_json, '$.cartridge_name'
                                    ) = 'text'
                               THEN json_extract(
                                        metadata_json, '$.cartridge_name'
                                    )
                               WHEN json_type(
                                        metadata_json, '$.cartridge'
                                    ) = 'text'
                               THEN json_extract(metadata_json, '$.cartridge')
                               ELSE NULL
                           END AS cartridge
                    FROM visible
                    WHERE scope_precedence = 1
                )
                SELECT cartridge, COUNT(*)
                FROM attributed
                WHERE cartridge IS NOT NULL
                GROUP BY cartridge
                """,
                (self.checkout_id, *self._visible_scopes),
            ).fetchall()
            for cartridge_name, node_count in rows:
                if isinstance(cartridge_name, str) and cartridge_name in counts:
                    counts[cartridge_name] = int(node_count)
            return counts
        finally:
            conn.close()

    def register_cartridge_installation(
        self,
        cartridge_name: str,
        source: str,
        server_url: str | None,
        node_count: int,
        policy: str = "optional",
    ) -> None:
        """Register or update a cartridge installation record.

        On re-install, policy is updated so a server-side policy change
        (e.g. optional → required) propagates on the next sync.
        """
        from datetime import UTC, datetime

        now = datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        conn = self._open()
        try:
            with conn:
                conn.execute(
                    """
                    INSERT INTO cartridge_installations
                        (project_id, cartridge_name, source, status, server_url,
                         node_count, installed_at, updated_at, policy)
                    VALUES (?, ?, ?, 'enabled', ?, ?, ?, ?, ?)
                    ON CONFLICT(project_id, cartridge_name) DO UPDATE SET
                        node_count = excluded.node_count,
                        updated_at = excluded.updated_at,
                        policy = excluded.policy
                    """,
                    (
                        self.project_id,
                        cartridge_name,
                        source,
                        server_url,
                        node_count,
                        now,
                        now,
                        policy,
                    ),
                )
        finally:
            conn.close()

    def set_cartridge_status(self, cartridge_name: str, status: str) -> bool:
        """Set installation status ('enabled'/'disabled'). False if not installed."""
        from datetime import UTC, datetime

        now = datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        conn = self._open()
        try:
            with conn:
                cursor = conn.execute(
                    """
                    UPDATE cartridge_installations
                    SET status = ?, updated_at = ?
                    WHERE project_id = ? AND cartridge_name = ?
                    """,
                    (status, now, self.project_id, cartridge_name),
                )
                return cursor.rowcount > 0
        finally:
            conn.close()

    def replace_node_by_backlog_key(self, backlog_key: str, graph: Graph) -> None:
        """Atomically delete+upsert a node by backlog key (RAISE-16742).

        Single transaction: if the upsert fails, the delete rolls back too —
        no window where 0 rows exist for this key.

        Matches both ``$.key`` and the pre-rename ``$.jira_key`` (RAISE-16940):
        rows written before the rename would otherwise survive the DELETE and
        the INSERT would leave two rows for one issue.
        """
        conn = self._open()
        try:
            with conn:
                conn.execute(
                    """
                    DELETE FROM graph_nodes
                    WHERE project_id = ?
                      AND checkout_id = ?
                      AND COALESCE(
                            json_extract(metadata_json, '$.key'),
                            json_extract(metadata_json, '$.jira_key')
                          ) = ?
                    """,
                    (self.project_id, self.checkout_id, backlog_key),
                )
                for node_id, attrs in graph.graph.nodes(data=True):
                    col_vals = self._node_column_values(
                        str(node_id), cast("JsonDict", attrs), self.checkout_id
                    )
                    updated_at = attrs.get("updated_at") if attrs else None
                    conn.execute(
                        """
                        INSERT INTO graph_nodes (
                            project_id, checkout_id, node_id, node_type, content,
                            source_file, metadata_json, release_id, module_id,
                            always_on, foundational, created_at, updated_at
                        ) VALUES (
                            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                            COALESCE(NULLIF(?, ''), strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
                            COALESCE(?, strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
                        )
                        ON CONFLICT(project_id, checkout_id, node_id) DO UPDATE SET
                            node_type    = excluded.node_type,
                            content      = excluded.content,
                            source_file  = excluded.source_file,
                            metadata_json= excluded.metadata_json,
                            release_id   = excluded.release_id,
                            module_id    = excluded.module_id,
                            always_on    = excluded.always_on,
                            foundational = excluded.foundational,
                            updated_at   = excluded.updated_at
                        """,
                        (*col_vals, updated_at),
                    )
        finally:
            conn.close()

    def delete_cartridge_nodes(self, cartridge_name: str) -> int:
        """Delete the repo-wide graph nodes of a cartridge. Returns count deleted."""
        conn = self._open()
        try:
            with conn:
                cursor = conn.execute(
                    """
                    DELETE FROM graph_nodes
                    WHERE project_id = ?
                      AND checkout_id = ?
                      AND json_extract(metadata_json, '$.cartridge_name') = ?
                    """,
                    (self.project_id, REPO_WIDE, cartridge_name),
                )
                return cursor.rowcount
        finally:
            conn.close()

    def remove_cartridge_installation(self, cartridge_name: str) -> bool:
        """Remove a cartridge installation record. Returns True if deleted."""
        conn = self._open()
        try:
            with conn:
                cursor = conn.execute(
                    """
                    DELETE FROM cartridge_installations
                    WHERE project_id = ? AND cartridge_name = ?
                    """,
                    (self.project_id, cartridge_name),
                )
                return cursor.rowcount > 0
        finally:
            conn.close()

    def get_cartridge_installation(
        self, cartridge_name: str
    ) -> dict[str, str | int | None] | None:
        """Return installation record or None if not installed.

        server_url is None for local installs — the value type is honest
        about that.
        """
        conn = self._open()
        try:
            row = conn.execute(
                """
                SELECT source, status, server_url, node_count, installed_at,
                       policy
                FROM cartridge_installations
                WHERE project_id = ? AND cartridge_name = ?
                """,
                (self.project_id, cartridge_name),
            ).fetchone()
            if row is None:
                return None
            return {
                "source": row[0],
                "status": row[1],
                "server_url": row[2],
                "node_count": row[3],
                "installed_at": row[4],
                "policy": row[5],
            }
        finally:
            conn.close()

    def persist(self, graph: Graph) -> None:
        """Replace this CHECKOUT's graph rows. Other checkouts are untouched.

        Both DELETEs are scoped by ``checkout_id`` — that scoping IS the fix for
        RAISE-15607. An unscoped ``DELETE ... WHERE project_id = ?`` deleted
        every other worktree's nodes on every ``rai graph build``, and scoping
        the primary key alone would have left that DELETE fully destructive.

        Repo-wide rows (``checkout_id = ''``: server- and locally-installed
        cartridge nodes, which live SQLite-only and are never re-hydrated by a
        filesystem rebuild) are protected structurally by the scope. This
        replaces the RAISE-15388 ``NOT EXISTS`` preservation guard, which
        filtered on ``metadata_json.cartridge_name`` matching a ``source =
        'server'`` installation: zero live rows carried that key, so the
        predicate was always true and the DELETE removed everything regardless.
        """
        conn = self._open()
        try:
            with conn:
                conn.execute(
                    "DELETE FROM graph_edges WHERE project_id = ? AND checkout_id = ?",
                    (self.project_id, self.checkout_id),
                )
                conn.execute(
                    "DELETE FROM graph_nodes WHERE project_id = ? AND checkout_id = ?",
                    (self.project_id, self.checkout_id),
                )
                for node_id, attrs in graph.graph.nodes(data=True):
                    # RAISE-16612: skip nodes that originated from REPO_WIDE when
                    # this backend is checkout-scoped. They must stay in the REPO_WIDE
                    # partition; writing them here would create a duplicate checkout
                    # row that silently overwrites shared cartridge/classification data.
                    if (
                        self._node_origin_checkout.get(str(node_id), self.checkout_id)
                        == REPO_WIDE
                        and self.checkout_id != REPO_WIDE
                    ):
                        continue
                    conn.execute(
                        """
                        INSERT INTO graph_nodes (
                            project_id, checkout_id, node_id, node_type, content,
                            source_file, metadata_json, release_id, module_id,
                            always_on, foundational, created_at
                        ) VALUES (
                            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                            COALESCE(NULLIF(?, ''), strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
                        )
                        """,
                        self._node_column_values(
                            str(node_id), cast("JsonDict", attrs), self.checkout_id
                        ),
                    )
                for source, target, key, edge_attrs in graph.graph.edges(
                    keys=True, data=True
                ):
                    conn.execute(
                        """
                        INSERT INTO graph_edges (
                            project_id, checkout_id, source_node_id, target_node_id,
                            edge_type, edge_key, metadata_json, source_file
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            self.project_id,
                            self.checkout_id,
                            str(source),
                            str(target),
                            str(edge_attrs.get("type", "")),
                            str(key),
                            json.dumps(edge_attrs, default=str),
                            str(edge_attrs.get("source_file", "")),
                        ),
                    )
        finally:
            conn.close()

    def upsert_nodes(self, graph: Graph) -> None:
        """Upsert nodos y aristas del graph sin destruir filas existentes (S-KS.1).

        Nodos: INSERT INTO ... ON CONFLICT DO UPDATE — actualiza todos los campos.
        Aristas: INSERT OR IGNORE — no-destructivo; no elimina aristas existentes
        ni sobreescribe aristas con la misma clave compuesta
        (project_id, source_node_id, target_node_id, edge_type, edge_key).

        Contraste con persist(): que hace DELETE total antes de insertar.

        Escribe en el scope de ESTE checkout (``self.checkout_id``) — el scope
        lo asigna el writer, nunca el ``node_type`` (RAISE-15607).
        """
        conn = self._open()
        try:
            with conn:
                for node_id, attrs in graph.graph.nodes(data=True):
                    # RAISE-16612: skip nodes that originated from REPO_WIDE when
                    # this backend is checkout-scoped. They must stay in the REPO_WIDE
                    # partition; writing them here would create a duplicate checkout
                    # row that silently overwrites shared cartridge/classification data.
                    if (
                        self._node_origin_checkout.get(str(node_id), self.checkout_id)
                        == REPO_WIDE
                        and self.checkout_id != REPO_WIDE
                    ):
                        continue
                    col_vals = self._node_column_values(
                        str(node_id), cast("JsonDict", attrs), self.checkout_id
                    )
                    # updated_at viene del campo del nodo (puede ser None → DEFAULT)
                    updated_at = attrs.get("updated_at") if attrs else None
                    conn.execute(
                        """
                        INSERT INTO graph_nodes (
                            project_id, checkout_id, node_id, node_type, content,
                            source_file, metadata_json, release_id, module_id,
                            always_on, foundational, created_at, updated_at
                        ) VALUES (
                            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                            COALESCE(NULLIF(?, ''), strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
                            COALESCE(?, strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
                        )
                        ON CONFLICT(project_id, checkout_id, node_id) DO UPDATE SET
                            node_type    = excluded.node_type,
                            content      = excluded.content,
                            source_file  = excluded.source_file,
                            metadata_json= excluded.metadata_json,
                            release_id   = excluded.release_id,
                            module_id    = excluded.module_id,
                            always_on    = excluded.always_on,
                            foundational = excluded.foundational,
                            updated_at   = excluded.updated_at
                        """,
                        (*col_vals, updated_at),
                    )
                # Upsert de aristas: no-destructivo (INSERT OR IGNORE) — Q-C2
                for source, target, key, edge_attrs in graph.graph.edges(
                    keys=True, data=True
                ):
                    conn.execute(
                        """
                        INSERT OR IGNORE INTO graph_edges (
                            project_id, checkout_id, source_node_id, target_node_id,
                            edge_type, edge_key, metadata_json, source_file
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            self.project_id,
                            self.checkout_id,
                            str(source),
                            str(target),
                            str(edge_attrs.get("type", "")),
                            str(key),
                            json.dumps(edge_attrs, default=str),
                            str(edge_attrs.get("source_file", "")),
                        ),
                    )
        finally:
            conn.close()

    def upsert_bc_assignments(self, graph: Graph) -> None:
        """Persist BC-* nodes and belongs_to→BC-* edges to the REPO_WIDE partition.

        RAISE-16852 fix: BC-* nodes (BoundedContextNode, type='bounded_context')
        and their incoming belongs_to edges from SymbolNodes are stored with
        ``checkout_id=REPO_WIDE`` (empty string) instead of the checkout-scoped
        partition.  This means a structural ``persist()`` call (``rai graph
        build``) — which only DELETEs ``checkout_id=self.checkout_id`` rows —
        never touches BC assignments.  The same durability contract that cartridge
        nodes enjoy (they also live in REPO_WIDE) now applies to BC assignments.

        The write is scoped: only nodes with ``type='bounded_context'`` and
        ``node_id LIKE 'BC-%'`` are extracted, and only edges whose
        ``target_node_id LIKE 'BC-%'`` and ``edge_type='belongs_to'`` are
        extracted.  All other graph content is ignored.

        Idempotency: existing REPO_WIDE BC-* rows are replaced on each call so
        that re-running ``rai graph assign-bcs`` reflects the latest clustering
        result rather than accumulating stale assignments.
        """
        bc_node_ids: set[str] = set()
        bc_node_rows: list[tuple[object, ...]] = []
        for node_id, attrs in graph.graph.nodes(data=True):
            node_id_str = str(node_id)
            if (
                not node_id_str.startswith("BC-")
                or str((attrs or {}).get("type", "")) != "bounded_context"
            ):
                continue
            bc_node_ids.add(node_id_str)
            bc_node_rows.append(
                self._node_column_values(
                    node_id_str, cast("JsonDict", attrs or {}), REPO_WIDE
                )
            )

        bc_edge_rows: list[tuple[object, ...]] = []
        for source, target, key, edge_attrs in graph.graph.edges(keys=True, data=True):
            target_str = str(target)
            if (
                target_str not in bc_node_ids
                or str((edge_attrs or {}).get("type", "")) != "belongs_to"
            ):
                continue
            bc_edge_rows.append(
                (
                    self.project_id,
                    REPO_WIDE,
                    str(source),
                    target_str,
                    "belongs_to",
                    str(key),
                    json.dumps(edge_attrs, default=str),
                    str((edge_attrs or {}).get("source_file", "")),
                )
            )

        if not bc_node_rows:
            return  # nothing to write

        conn = self._open()
        try:
            with conn:
                # Replace existing REPO_WIDE BC assignments for this project.
                # Scoped deletes prevent touching non-BC REPO_WIDE content
                # (cartridge nodes, etc.).
                conn.execute(
                    "DELETE FROM graph_nodes "
                    "WHERE project_id = ? AND checkout_id = ? "
                    "  AND node_id LIKE 'BC-%' AND node_type = 'bounded_context'",
                    (self.project_id, REPO_WIDE),
                )
                conn.execute(
                    "DELETE FROM graph_edges "
                    "WHERE project_id = ? AND checkout_id = ? "
                    "  AND edge_type = 'belongs_to' AND target_node_id LIKE 'BC-%'",
                    (self.project_id, REPO_WIDE),
                )
                for row in bc_node_rows:
                    conn.execute(
                        """
                        INSERT INTO graph_nodes (
                            project_id, checkout_id, node_id, node_type, content,
                            source_file, metadata_json, release_id, module_id,
                            always_on, foundational, created_at
                        ) VALUES (
                            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                            COALESCE(NULLIF(?, ''), strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
                        )
                        """,
                        row,
                    )
                for row in bc_edge_rows:
                    conn.execute(
                        """
                        INSERT INTO graph_edges (
                            project_id, checkout_id, source_node_id, target_node_id,
                            edge_type, edge_key, metadata_json, source_file
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        row,
                    )
        finally:
            conn.close()

    def load(self) -> Graph:
        """Load the graph for this project."""
        conn = self._open()
        try:
            return self._load_from_connection(conn)
        finally:
            conn.close()

    def _load_from_connection(self, conn: sqlite3.Connection) -> Graph:
        instance = Graph()
        # Visible scopes: this checkout + the repo-wide partition. ORDER BY
        # checkout_id puts the repo-wide row ('' sorts first) before the
        # checkout row, so the checkout row is applied last and WINS on a
        # node_id collision. Without a rule here the MultiDiGraph load would be
        # order-dependent and non-deterministic (RAISE-15607).
        node_rows = cast(
            "list[NodeRow]",
            conn.execute(
                """
                SELECT node_id, node_type, content, source_file, metadata_json,
                       release_id, module_id, always_on, foundational, created_at,
                       updated_at, checkout_id
                FROM graph_nodes
                WHERE project_id = ?
                  AND checkout_id IN (?, ?)
                  AND NOT EXISTS (
                      SELECT 1 FROM cartridge_installations ci
                      WHERE ci.project_id = graph_nodes.project_id
                        AND ci.status = 'disabled'
                        AND ci.cartridge_name =
                            json_extract(graph_nodes.metadata_json, '$.cartridge_name')
                  )
                ORDER BY node_id, checkout_id
                """,
                self._visible_scopes,
            ).fetchall(),
        )

        # RAISE-16596: merge durable annotations into node metadata at load
        # time. Structurally separate table from graph_nodes — a rebuild
        # (persist()/upsert_nodes()) never touches it, so this merge is the
        # only place annotations and structural facts come back together.
        #
        # Two distinct merge rules, not one:
        #   1. Within a single namespace, a checkout-scoped payload WHOLLY
        #      REPLACES a repo-wide payload for the same node_id — a
        #      checkout-specific write is a complete reassignment, not a
        #      partial override (matches load_annotations()'s semantics;
        #      QR RAISE-16596 caught these two paths disagreeing).
        #   2. Across different namespaces (ddd, future review/ownership/
        #      security, ...), payloads are additive — each namespace owns
        #      its own keys and all namespaces contribute to the final
        #      node.metadata.
        # ORDER BY checkout_id applies the checkout-scoped row last within
        # each (node_id, namespace) group, so step 1's "last write wins"
        # falls out of plain dict assignment — no key-level update needed.
        annotation_rows = conn.execute(
            """
            SELECT node_id, namespace, payload_json
            FROM graph_node_annotations
            WHERE project_id = ?
              AND checkout_id IN (?, ?)
            ORDER BY node_id, namespace, checkout_id
            """,
            self._visible_scopes,
        ).fetchall()
        payload_by_node_and_namespace: dict[tuple[str, str], JsonDict] = {}
        for node_id, namespace, payload_json in annotation_rows:
            payload_by_node_and_namespace[(str(node_id), str(namespace))] = (
                self._load_json_dict(payload_json)
            )
        annotations_by_node: dict[str, JsonDict] = {}
        for (node_id, _namespace), payload in payload_by_node_and_namespace.items():
            annotations_by_node.setdefault(node_id, {}).update(payload)

        # RAISE-16611: record which metadata keys came from the annotations
        # table (as opposed to metadata_json) so a later persist()/
        # upsert_nodes() on this same instance can strip them back out
        # before writing metadata_json — see _strip_annotation_keys().
        self._annotation_keys_by_node = {
            node_id: set(payload.keys())
            for node_id, payload in annotations_by_node.items()
        }

        # RAISE-16612: reset provenance map before re-populating from this load.
        self._node_origin_checkout = {}

        for (
            node_id,
            node_type,
            content,
            source_file,
            metadata_json,
            _release_id,
            _module_id,
            _always_on,
            _foundational,
            created_at,
            updated_at,
            row_checkout_id,
        ) in node_rows:
            metadata = self._load_json_dict(metadata_json)
            metadata.update(annotations_by_node.get(node_id, {}))
            instance.graph.add_node(
                node_id,
                id=node_id,
                type=node_type,
                content=content,
                source_file=source_file or None,
                created=created_at,
                updated_at=updated_at,
                metadata=metadata,
            )
            # Record the winning partition for this node. ORDER BY checkout_id
            # puts '' (REPO_WIDE) before any checkout path, so a checkout-scoped
            # row overwrites the REPO_WIDE entry here — matching the in-memory
            # merge winner. persist()/upsert_nodes() use this to route nodes
            # back to their origin partition (RAISE-16612).
            self._node_origin_checkout[str(node_id)] = str(row_checkout_id)

        edge_rows = cast(
            "list[EdgeRow]",
            conn.execute(
                """
                SELECT source_node_id, target_node_id, edge_key, edge_type,
                       metadata_json, source_file
                FROM graph_edges
                WHERE project_id = ?
                  AND checkout_id IN (?, ?)
                ORDER BY source_node_id, target_node_id, edge_type, edge_key,
                         checkout_id
                """,
                self._visible_scopes,
            ).fetchall(),
        )
        for (
            source,
            target,
            edge_key,
            edge_type,
            metadata_json,
            source_file,
        ) in edge_rows:
            edge_attrs = self._load_json_dict(metadata_json)
            edge_attrs["type"] = edge_type
            if source_file:
                edge_attrs["source_file"] = source_file
            instance.graph.add_edge(source, target, key=edge_key, **edge_attrs)
        return instance

    def _row_to_node(self, row: GraphNodeRow) -> GraphNode:
        node_id, node_type, content, source_file, metadata_json, created_at = row
        return GraphNode.model_validate(
            {
                "id": node_id,
                "type": node_type,
                "content": content,
                "source_file": source_file or None,
                "created": created_at,
                "metadata": self._load_json_dict(metadata_json),
            }
        )

    def _fetch_foundational_pattern_rows(self) -> list[GraphNodeRow]:
        conn = self._open()
        try:
            return cast(
                "list[GraphNodeRow]",
                conn.execute(
                    """
                    SELECT node_id, node_type, content, source_file,
                           metadata_json, created_at
                    FROM graph_nodes
                    WHERE project_id = ?
                      AND checkout_id IN (?, ?)
                      AND node_type = 'pattern'
                      AND foundational = 1
                    ORDER BY node_id, checkout_id
                    """,
                    self._visible_scopes,
                ).fetchall(),
            )
        finally:
            conn.close()

    def _fetch_always_on_rows(self) -> list[GraphNodeRow]:
        conn = self._open()
        try:
            return cast(
                "list[GraphNodeRow]",
                conn.execute(
                    """
                    SELECT node_id, node_type, content, source_file,
                           metadata_json, created_at
                    FROM graph_nodes
                    WHERE project_id = ?
                      AND checkout_id IN (?, ?)
                      AND always_on = 1
                    ORDER BY node_id, checkout_id
                    """,
                    self._visible_scopes,
                ).fetchall(),
            )
        finally:
            conn.close()

    def get_module_ids(self) -> list[str]:
        """Return all module node IDs for this project."""
        conn = self._open()
        try:
            rows = cast(
                "list[tuple[str]]",
                conn.execute(
                    """
                    SELECT DISTINCT node_id
                    FROM graph_nodes
                    WHERE project_id = ?
                      AND checkout_id IN (?, ?)
                      AND node_type = 'module'
                    ORDER BY node_id
                    """,
                    self._visible_scopes,
                ).fetchall(),
            )
            return [node_id for (node_id,) in rows]
        finally:
            conn.close()

    def _dedupe_rows(self, rows: list[GraphNodeRow]) -> list[GraphNode]:
        """Collapse rows to one node per node_id — the checkout row wins.

        Rows arrive ordered by ``(node_id, checkout_id)``, so the repo-wide row
        ('' sorts first) is overwritten by the checkout row when both exist.
        """
        by_id: dict[str, GraphNode] = {}
        for row in rows:
            by_id[row[0]] = self._row_to_node(row)
        return list(by_id.values())

    def get_foundational_patterns(self) -> list[GraphNode]:
        """Return foundational pattern nodes."""
        return self._dedupe_rows(self._fetch_foundational_pattern_rows())

    def get_always_on_nodes(self) -> list[GraphNode]:
        """Return always-on nodes across node types."""
        return self._dedupe_rows(self._fetch_always_on_rows())

    def find_release_for_epic(self, epic_node_id: str) -> GraphNode | None:
        """Return release node reached via a part_of edge from the given epic node."""
        conn = self._open()
        try:
            row = cast(
                "GraphNodeRow | None",
                conn.execute(
                    """
                    SELECT n.node_id, n.node_type, n.content, n.source_file,
                           n.metadata_json, n.created_at
                    FROM graph_edges e
                    JOIN graph_nodes n
                      ON n.project_id = e.project_id
                     AND n.node_id = e.target_node_id
                    WHERE e.project_id = ?
                      AND e.checkout_id IN (?, ?)
                      AND n.checkout_id IN (?, ?)
                      AND e.source_node_id = ?
                      AND e.edge_type = 'part_of'
                      AND n.node_type = 'release'
                    ORDER BY n.node_id, n.checkout_id DESC
                    LIMIT 1
                    """,
                    (*self._visible_scopes, *self._visible_scopes[1:], epic_node_id),
                ).fetchone(),
            )
            if row is None:
                return None
            return self._row_to_node(row)
        finally:
            conn.close()

    def _fetch_backlog_item_rows(self) -> list[BacklogNodeRow]:
        """Fetch all backlog.* rows (dynamic types, RAISE-16727).

        Separate row shape from ``GraphNodeRow`` — includes ``updated_at``,
        which the always-on/foundational fast paths above don't need but the
        backlog session-context section does (recency filter + sort, D-S5.5).

        Uses LIKE prefix instead of IN(…) so new issue types (capability,
        research-item, etc.) are included automatically.
        """
        conn = self._open()
        try:
            return cast(
                "list[BacklogNodeRow]",
                conn.execute(
                    """
                    SELECT node_id, node_type, content, source_file,
                           metadata_json, created_at, updated_at
                    FROM graph_nodes
                    WHERE project_id = ?
                      AND checkout_id IN (?, ?)
                      AND node_type LIKE ?
                      AND node_type NOT IN (?, ?, ?, ?)
                    ORDER BY node_id, checkout_id
                    """,
                    (
                        *self._visible_scopes,
                        _BACKLOG_NODE_PREFIX + "%",
                        *_BACKLOG_MODEL_TYPES,
                    ),
                ).fetchall(),
            )
        finally:
            conn.close()

    def _row_to_backlog_node(self, row: BacklogNodeRow) -> GraphNode:
        (
            node_id,
            node_type,
            content,
            source_file,
            metadata_json,
            created_at,
            updated_at,
        ) = row
        return GraphNode.model_validate(
            {
                "id": node_id,
                "type": node_type,
                "content": content,
                "source_file": source_file or None,
                "created": created_at,
                "updated_at": updated_at,
                "metadata": self._load_json_dict(metadata_json),
            }
        )

    def _dedupe_backlog_rows(self, rows: list[BacklogNodeRow]) -> list[GraphNode]:
        """Collapse rows to one node per node_id — the checkout row wins."""
        by_id: dict[str, GraphNode] = {}
        for row in rows:
            by_id[row[0]] = self._row_to_backlog_node(row)
        return list(by_id.values())

    def get_backlog_item_nodes(self) -> list[GraphNode]:
        """Return backlog.{epic,story,bug,task} nodes (RAISE-16427)."""
        return self._dedupe_backlog_rows(self._fetch_backlog_item_rows())

    def ego_subgraph(self, node_id: str, depth: int = 2) -> Graph:
        """Return all nodes within depth hops of node_id using bidirectional traversal."""
        if depth < 0:
            raise ValueError(f"depth must be >= 0, got {depth}")
        graph = self.load()
        result = Graph()
        if node_id not in graph.graph.nodes:
            return result
        if depth == 0:
            result.graph.add_node(node_id, **dict(graph.graph.nodes[node_id]))
            return result

        undirected = graph.graph.to_undirected(as_view=True)
        node_ids = set(
            nx.single_source_shortest_path_length(undirected, node_id, cutoff=depth)
        )
        for found_id in sorted(node_ids):
            result.graph.add_node(found_id, **dict(graph.graph.nodes[found_id]))
        for source, target, key, attrs in graph.graph.edges(keys=True, data=True):
            if source in node_ids and target in node_ids:
                result.graph.add_edge(source, target, key=key, **dict(attrs))
        return result

    def neighbors(
        self, node_id: str, direction: str = "outgoing"
    ) -> list[tuple[str, str]]:
        """Return direct neighbors as (neighbor_id, edge_type) pairs."""
        if direction not in ("outgoing", "incoming", "both"):
            raise ValueError(
                f"direction must be 'outgoing', 'incoming', or 'both', got {direction!r}"
            )
        graph = self.load()
        if node_id not in graph.graph.nodes:
            return []

        results: list[tuple[str, str]] = []
        if direction in ("outgoing", "both"):
            for _source, target, attrs in graph.graph.out_edges(node_id, data=True):
                results.append((target, str(attrs.get("type", ""))))
        if direction in ("incoming", "both"):
            for source, _target, attrs in graph.graph.in_edges(node_id, data=True):
                results.append((source, str(attrs.get("type", ""))))
        return results

    def path(self, src: str, dst: str) -> list[str] | None:
        """Return the shortest directed path from src to dst."""
        if src == dst:
            return [src]
        graph = self.load()
        try:
            path = nx.shortest_path(graph.graph, src, dst)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None
        return [str(node_id) for node_id in path]

    def health(self) -> BackendHealth:
        """Check backend health."""
        return BackendHealth(
            status="healthy",
            message="SQLite graph backend operational",
            metadata={
                "backend": "sqlite",
                "db_path": str(self.db_path),
                "project_id": self.project_id,
                "checkout_id": self.checkout_id,
            },
        )
