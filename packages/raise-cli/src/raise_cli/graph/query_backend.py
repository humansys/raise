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

logger = logging.getLogger(__name__)


@runtime_checkable
class GraphReadBackend(Protocol):
    """Read contract for knowledge-graph access from MCP tools."""

    async def query(self, query: str, limit: int) -> dict[str, Any]:
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

    async def query(self, query: str, limit: int) -> dict[str, Any]:
        """Delegate to ``rai graph query --format json`` (stdio behavior)."""
        code, out, err = _run_rai(
            "graph",
            "query",
            query,
            "--format",
            "json",
            "--limit",
            str(limit),
            cwd=self._root,
        )
        if code != 0:
            raise GraphQueryError(err.strip() or "Graph query failed")
        return _parse_json(out)

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

    def interpret_query(  # noqa: PLR6301, D102
        self,
        query: str,  # noqa: ARG002
    ) -> Any:
        from raise_core.graph.retrieval.models import DomainHints

        return DomainHints(domain="mcp")

    def advise_traversal(  # noqa: PLR6301, D102
        self,
        hints: Any,  # noqa: ARG002
        available_types: frozenset[str],  # noqa: ARG002
    ) -> Any:
        return None

    def annotate_results(  # noqa: PLR6301, D102
        self,
        nodes: list[Any],
        hints: Any,  # noqa: ARG002
    ) -> list[Any]:
        from raise_core.graph.retrieval.models import ScoredNode

        return [ScoredNode(node=n, score=0.0, explanation="neutral") for n in nodes]


def _find_all_embeddings_dirs(cwd: Path | None = None) -> list[Path]:
    """Scan cartridge roots for dirs containing embeddings (legacy or manifest format).

    Scans both ``.raise/cartridges/*/instances/`` (repo-local) and
    ``$RAI_HOME/cartridges/*/instances/`` (external — RAISE-13911 DD-2 (b),
    the memory cartridge lives outside the repo) via the shared
    ``get_external_cartridge_roots()`` helper — a second, divergent parse of
    ``$RAI_HOME`` here would repeat the class of bug this repo's "Canonical
    Resolver Callers" convention exists to prevent.

    Args:
        cwd: Root directory to search from (defaults to Path.cwd()).
    """
    from raise_cli.config.paths import get_external_cartridge_roots

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
        from raise_core.graph.scorers import resolve_semantic_scorer

        creds = get_server_credentials()
        server_url = creds[0] if creds else None
        api_key = creds[1] if creds else None

        return resolve_semantic_scorer(
            embeddings_dirs=_find_all_embeddings_dirs(),
            server_url=server_url,
            api_key=api_key,
        )

    async def query(self, query: str, limit: int) -> dict[str, Any]:
        """Run the federation orchestrator and format results to CLI JSON shape.

        ``federated_retrieve_from_graph`` (ADR-103) federates across cartridges
        when the graph holds >1, and falls back to single-cartridge ``retrieve()``
        otherwise — so single-cartridge behavior is unchanged.
        """
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
        return PostgresGraphBackend(get_mcp_session_factory(), org_id=token.org_id)

    try:
        return RetrievalGraphBackend(root)
    except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        logger.debug(
            "RetrievalGraphBackend unavailable, falling back to CLI subprocess"
        )
        return FilesystemGraphBackend(root)
