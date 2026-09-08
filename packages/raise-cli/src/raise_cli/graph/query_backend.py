"""Knowledge-graph read backend for MCP tools — S1962.8 + S-HFNR.2.

Three backends behind a Protocol so ``raise_graph_query`` /
``raise_graph_context`` can run uniformly across transports:

    stdio (Claude Code local)  → RetrievalGraphBackend (hybrid retrieve())
                                  fallback: FilesystemGraphBackend (subprocess)
    http  (Rovo multi-tenant)  → PostgresGraphBackend, scoped by JWT.org_id

RetrievalGraphBackend (S-HFNR.2) loads the graph in-process and runs
``retrieve()`` — the 4-signal hybrid engine with candidate union — instead
of shelling out to ``rai graph query`` which uses the simpler QueryEngine.
Falls back to FilesystemGraphBackend when the graph index is missing.

The resolver ``get_graph_backend()`` picks by transport (env var
``RAISE_MCP_TRANSPORT`` set by ``mcp_mount``). HTTP without a valid JWT
raises — never silent filesystem fallback (PAT-F-118).

Write-side graph backend (``raise_core.graph.backends.KnowledgeGraphBackend``)
is a separate concern (ADR-036, discovery).
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Any, Protocol, cast, runtime_checkable

from raise_cli.compat import get_rai_executable
from raise_cli.graph.exceptions import GraphQueryError
from raise_core.graph.filters import GraphFilter

logger = logging.getLogger(__name__)


@runtime_checkable
class GraphReadBackend(Protocol):
    """Read contract for knowledge-graph access from MCP tools."""

    async def query(
        self,
        query: str,
        limit: int,
        filters: GraphFilter | None = None,
    ) -> dict[str, Any]:
        """Return the parsed graph-query result dict (shape mirrors CLI)."""
        ...

    async def context(self, module_id: str) -> dict[str, Any]:
        """Return the parsed module-context result dict (shape mirrors CLI)."""
        ...


class FilesystemGraphBackend:
    """stdio-mode backend — shells out to ``rai graph`` (current CLI path).

    Behavior is identical to the inline code ``raise_graph_query`` /
    ``raise_graph_context`` used before S1962.8. Relocating it here
    keeps the tool body uniform across transports.

    ``root`` anchors the subprocess to the caller's checkout (S15457.2);
    None preserves the legacy process-CWD behavior for CLI callers.
    """

    def __init__(self, root: Path | None = None) -> None:
        self._root = root

    async def query(
        self,
        query: str,
        limit: int,
        filters: GraphFilter | None = None,
    ) -> dict[str, Any]:
        """Delegate to ``rai graph query --format json`` (stdio behavior).

        When filters are present, loads the graph in-process and uses
        QueryEngine directly — avoids lossy CLI token serialization.
        """
        if filters is not None:
            return self._query_with_filters(query, limit, filters)
        args = [
            "graph",
            "query",
            query,
            "--format",
            "json",
            "--limit",
            str(limit),
        ]
        code, out, err = _run_rai(*args, cwd=self._root)
        if code != 0:
            raise GraphQueryError(err.strip() or "Graph query failed")
        return _parse_json(out)

    def _query_with_filters(
        self, query: str, limit: int, filters: GraphFilter
    ) -> dict[str, Any]:
        """Run filtered query in-process via QueryEngine."""
        from raise_cli.config.paths import get_memory_dir
        from raise_cli.graph.backends import get_active_backend
        from raise_core.graph.query import Query, QueryEngine, QueryStrategy

        index_path = get_memory_dir(self._root) / "index.json"
        backend = get_active_backend(index_path, explicit_path=False)
        graph = backend.load()
        engine = QueryEngine(graph)
        q = Query(
            query=query,
            strategy=QueryStrategy.KEYWORD_SEARCH_FORCED,
            limit=limit,
            filters=filters,
        )
        result = engine.query(q)
        nodes: list[dict[str, Any]] = []
        for concept in result.concepts:
            node_dict: dict[str, Any] = {
                "node_id": concept.id,
                "node_type": concept.type,
                "content": concept.content,
                "rank": 0.0,
            }
            if concept.source_file:
                node_dict["source_file"] = concept.source_file
            if concept.metadata:
                node_dict["properties"] = concept.metadata
            nodes.append(node_dict)
        return {"results": nodes, "total": result.metadata.total_available}

    async def context(self, module_id: str) -> dict[str, Any]:
        """Delegate to ``rai graph context <id> --format json``."""
        code, out, err = _run_rai(
            "graph", "context", module_id, "--format", "json", cwd=self._root
        )
        if code != 0:
            raise GraphQueryError(err.strip() or "Graph context failed")
        return _parse_json(out)


class NeutralDomainAdapter:
    """Minimal domain adapter for MCP queries — no domain-specific scoring."""

    def interpret_query(  # noqa: D102
        self,
        query: str,
    ) -> Any:
        from raise_core.graph.retrieval.models import DomainHints

        return DomainHints(domain="mcp")

    def advise_traversal(  # noqa: D102
        self,
        hints: Any,
        available_types: frozenset[str],
    ) -> Any:
        return None

    def annotate_results(  # noqa: D102
        self,
        nodes: list[Any],
        hints: Any,
    ) -> list[Any]:
        from raise_core.graph.retrieval.models import ScoredNode

        return [ScoredNode(node=n, score=0.0, explanation="neutral") for n in nodes]


def _find_all_embeddings_dirs(cwd: Path | None = None) -> list[Path]:
    """Scan cartridge roots + the graph-nodes memory dir for embeddings dirs.

    Scans both ``.raise/cartridges/*/instances/`` (repo-local) and
    ``$RAI_HOME/cartridges/*/instances/`` (external — RAISE-13911 DD-2 (b),
    the memory cartridge lives outside the repo) via the shared
    ``get_external_cartridge_roots()`` helper — a second, divergent parse of
    ``$RAI_HOME`` here would repeat the class of bug this repo's "Canonical
    Resolver Callers" convention exists to prevent.

    Also appends ``get_memory_dir(cwd)/embeddings`` when present — the fused
    generation written by ``_auto_embed_graph_nodes`` for non-cartridge
    ``pattern``/``symbol``/``document`` nodes (RAISE-16087). Same legacy/
    manifest format as cartridge dirs, so callers need no format branching.

    Args:
        cwd: Root directory to search from (defaults to Path.cwd()).
    """
    from raise_cli.config.paths import get_external_cartridge_roots, get_memory_dir

    found: list[Path] = []
    for cartridges_root in get_external_cartridge_roots(cwd or Path.cwd()):
        if not cartridges_root.exists():
            continue
        found.extend(
            instances_dir
            for instances_dir in sorted(cartridges_root.glob("*/instances"))
            if (instances_dir / "embeddings.npy").exists()
            or (instances_dir / "manifest.json").exists()
        )

    graph_dir = get_memory_dir(cwd) / "embeddings"
    if (graph_dir / "embeddings.npy").exists() or (
        graph_dir / "manifest.json"
    ).exists():
        found.append(graph_dir)

    return found


class RetrievalGraphBackend:
    """In-process backend using the hybrid retrieval engine (S-HFNR.2).

    Loads the graph from the local index and runs ``retrieve()`` with
    4-signal composite scoring + candidate union when a SemanticScorer
    is available.  Falls back to ``context()`` via the CLI subprocess
    (same as FilesystemGraphBackend).
    """

    def __init__(self, root: Path | None = None) -> None:
        from raise_cli.config.paths import get_memory_dir
        from raise_cli.graph.backends import get_active_backend

        self._root = root
        index_path = get_memory_dir(root) / "index.json"
        backend = get_active_backend(index_path, explicit_path=False)
        self._graph = backend.load()
        self._adapter = NeutralDomainAdapter()
        self._scorer = self._resolve_scorer()

    @staticmethod
    def _resolve_scorer() -> Any:
        from raise_cli.config.server import get_server_credentials
        from raise_core.graph.scorers import (
            NumpySemanticScorer,
            resolve_semantic_scorer,
        )

        creds = get_server_credentials()
        server_url = creds[0] if creds else None
        api_key = creds[1] if creds else None

        scorer = resolve_semantic_scorer(
            embeddings_dirs=_find_all_embeddings_dirs(),
            server_url=server_url,
            api_key=api_key,
        )
        if scorer is not None:
            return scorer

        embeddings_dirs = _find_all_embeddings_dirs()
        if not embeddings_dirs:
            return None
        try:
            from raise_cli.embeddings.provider import get_default_provider

            provider = get_default_provider()
            return NumpySemanticScorer(embeddings_dirs, provider)
        except (ImportError, RuntimeError):
            return None

    async def query(
        self,
        query: str,
        limit: int,
        filters: GraphFilter | None = None,
    ) -> dict[str, Any]:
        """Run the federation orchestrator and format results to CLI JSON shape.

        ``federated_retrieve_from_graph`` (ADR-103) federates across cartridges
        when the graph holds >1, and falls back to single-cartridge ``retrieve()``
        otherwise — so single-cartridge behavior is unchanged.
        """
        if filters is not None:
            return self._query_with_filters(query, limit, filters)
        from raise_core.graph.retrieval.federation import (
            federated_retrieve_from_graph,
        )

        result = federated_retrieve_from_graph(
            self._graph,
            query,
            self._adapter,
            top_k=limit,
            semantic_scorer=self._scorer,
        )

        nodes: list[dict[str, Any]] = []
        for sn in result.nodes:
            node_dict: dict[str, Any] = {
                "node_id": sn.node.id,
                "node_type": sn.node.type,
                "content": sn.node.content,
                "rank": sn.score,
            }
            if sn.node.source_file:
                node_dict["source_file"] = sn.node.source_file
            if sn.node.metadata:
                node_dict["properties"] = sn.node.metadata
            if sn.source_cartridge:
                node_dict["source_cartridge"] = sn.source_cartridge
            nodes.append(node_dict)

        return {"results": nodes, "total": len(nodes)}

    def _query_with_filters(
        self, query: str, limit: int, filters: GraphFilter
    ) -> dict[str, Any]:
        """Fall back to QueryEngine for filtered queries.

        The retrieval engine (federated_retrieve) uses semantic scoring that
        does not support structured filters. The graph is already loaded in
        memory, so we build a QueryEngine and run the keyword-search path
        with filters applied — same evaluator the CLI uses.
        """
        from raise_core.graph.query import Query, QueryEngine, QueryStrategy

        engine = QueryEngine(self._graph)
        q = Query(
            query=query,
            strategy=QueryStrategy.KEYWORD_SEARCH_FORCED,
            limit=limit,
            filters=filters,
        )
        result = engine.query(q)
        nodes: list[dict[str, Any]] = []
        for concept in result.concepts:
            node_dict: dict[str, Any] = {
                "node_id": concept.id,
                "node_type": concept.type,
                "content": concept.content,
                "rank": 0.0,
            }
            if concept.source_file:
                node_dict["source_file"] = concept.source_file
            if concept.metadata:
                node_dict["properties"] = concept.metadata
            nodes.append(node_dict)
        return {"results": nodes, "total": result.metadata.total_available}

    async def context(self, module_id: str) -> dict[str, Any]:
        """Delegate context to CLI subprocess (same as FilesystemGraphBackend)."""
        code, out, err = _run_rai(
            "graph", "context", module_id, "--format", "json", cwd=self._root
        )
        if code != 0:
            raise GraphQueryError(err.strip() or "Graph context failed")
        return _parse_json(out)


def _run_rai(
    *args: str, timeout: int = 30, cwd: Path | None = None
) -> tuple[int, str, str]:
    """Run ``rai ...`` via get_rai_executable(); mirrors ``mcp_server._run_cli`` exactly.

    ``cwd`` anchors the subprocess to the caller's checkout (S15457.2);
    None preserves the legacy process-CWD behavior.
    """
    result = subprocess.run(
        [*get_rai_executable(), *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
        env=os.environ.copy(),
        cwd=cwd,
    )
    return result.returncode, result.stdout, result.stderr


def _parse_json(text: str) -> dict[str, Any]:
    """Parse JSON tolerating the CLI's log-line preamble.

    Verbatim copy of ``raise_cli.pipeline.mcp_server._parse_json`` so
    stdio behavior is byte-identical to the pre-refactor inline code.
    """
    for i, ch in enumerate(text):
        if ch in ("{", "["):
            text = text[i:]
            break
    data: Any = json.loads(text, strict=False)
    if isinstance(data, dict):
        return cast("dict[str, Any]", data)
    return {"results": data}


# ---------------------------------------------------------------------------
# Transport-based resolver — PAT-F-118
# ---------------------------------------------------------------------------


def _is_http_request() -> bool:
    return os.environ.get("RAISE_MCP_TRANSPORT", "").lower() == "http"


def get_graph_backend(root: Path | None = None) -> GraphReadBackend:
    """Resolve the right backend for the current context.

    Tri-state resolver (ADR-075):
    - RAISE_SERVER_URL set → ApiGraphReadBackend (thin HTTP client).
    - RAISE_MCP_TRANSPORT=http → PostgresGraphBackend (server in-process).
    - Neither → FilesystemGraphBackend (local CLI subprocess).

    ``root`` anchors local backends to the caller's checkout (S15457.2);
    ignored for API/Postgres backends and for legacy CLI callers (None).
    """
    from raise_cli.config.server import get_server_credentials

    creds = get_server_credentials()
    if creds is not None:
        from raise_cli.graph.api_graph_read_backend import ApiGraphReadBackend

        server_url, api_key = creds
        return ApiGraphReadBackend(server_url=server_url, api_key=api_key)

    if _is_http_request():
        from mcp.server.auth.middleware.auth_context import get_access_token
        from raise_server.graph.query_backend_db import PostgresGraphBackend
        from raise_server.mcp_mount import get_mcp_session_factory

        token: Any = get_access_token()
        if token is None:
            raise RuntimeError(
                "graph tool invoked via HTTP without valid JWT — "
                "no filesystem fallback allowed on server",
            )
        return PostgresGraphBackend(get_mcp_session_factory(), org_id=token.org_id)  # type: ignore[return-value]  # server backend not yet widened (RAISE-16890)

    try:
        return RetrievalGraphBackend(root)
    except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        logger.debug(
            "RetrievalGraphBackend unavailable, falling back to CLI subprocess"
        )
        return FilesystemGraphBackend(root)
