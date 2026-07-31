"""SQLite-backed graph backend over the canonical V68 graph schema."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, cast

import networkx as nx  # type: ignore[import-untyped]

from raise_cli.config.paths import checkout_scope_id
from raise_cli.storage.schema import create_all
from raise_core.graph.backends.models import BackendHealth
from raise_core.graph.engine import Graph
from raise_core.graph.models import GraphNode

JsonDict = dict[str, Any]
NodeRow = tuple[str, str, str, str | None, str, str, str, int, int, str, str | None]
EdgeRow = tuple[str, str, str, str, str, str]
GraphNodeRow = tuple[str, str, str, str | None, str, str]

#: ``checkout_id`` of rows that belong to the repository as a whole rather than
#: to one checkout of it — cartridge nodes, shared by every worktree/clone.
REPO_WIDE = ""

__all__ = ["REPO_WIDE", "SQLiteGraphBackend"]


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
        return (
            self.project_id,
            checkout_id,
            node_id,
            node_type,
            str(attrs.get("content", "")),
            str(source_file),
            json.dumps(metadata, default=str),
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
                       updated_at
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
        ) in node_rows:
            metadata = self._load_json_dict(metadata_json)
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
