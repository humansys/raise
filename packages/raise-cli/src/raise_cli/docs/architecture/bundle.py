"""Bundle assembly — the entire LLM input, assembled in-process (D-S5).

Two gemba findings force this design:

1. ``rai graph context mod-graph --format json`` is rich-console rendered
   and, under a narrow ``COLUMNS``, line-wraps mid-string and fails
   ``json.loads`` (reproduced: "Invalid control character at line 5 column
   76"). Shelling out and re-parsing is a latent CI break. ``build_bundle``
   therefore calls the in-process graph read path (``QueryEngine`` over a
   loaded ``Graph``) instead — no subprocess, no re-parse, no wrap.
2. The allowlist itself lives in ``models.SynthesisBundle`` (see that
   module's docstring) — this function is the one place responsible for
   never copying a volatile field (``created``, ``updated_at``, ...) onto
   the bundle.
"""

from __future__ import annotations

from pathlib import Path

from raise_cli.config.paths import get_memory_dir
from raise_cli.docs.architecture.fingerprint import fingerprint
from raise_cli.docs.architecture.models import SymbolSummary, SynthesisBundle
from raise_cli.graph.backends import get_active_backend
from raise_core.graph.engine import Graph
from raise_core.graph.models import GraphNode
from raise_core.graph.query import QueryEngine

_INDEX_FILENAME = "index.json"


class ModuleNotFoundInGraphError(LookupError):
    """Raised when ``module_id`` has no corresponding node in the graph."""


def _default_index_path(project_root: Path | None = None) -> Path:
    return get_memory_dir(project_root) / _INDEX_FILENAME


def load_graph(
    index_path: Path | None = None, project_root: Path | None = None
) -> Graph:
    """Load the graph via the in-process backend — never a subprocess.

    Mirrors ``rai graph context``'s own loading path (``cli/commands/
    graph.py::context_cmd``) so this stays consistent with the one other
    place that reads a single module's context, without depending on that
    CLI module (layering: CLI depends on docs/, not the reverse).

    ``project_root`` is threaded into ``get_active_backend`` so backend
    resolution (``resolve_checkout_root()``'s fallback, when neither
    ``index_path`` nor ``project_root`` is given) scopes to the caller's
    intended root rather than silently defaulting to process CWD — R3: in
    a multi-worktree setup where a gate's ``working_dir`` differs from
    process CWD, an unthreaded default cross-wires one repo's docs
    against a different repo's graph.

    Public (no leading underscore) so multi-module/multi-region callers —
    e.g. ``ArchitectureDocsFreshGate`` — can call this once and pass the
    result into ``build_bundle(graph=...)`` for every region instead of
    re-reading the index from disk per region (R9).
    """
    resolved = index_path or _default_index_path(project_root)
    backend = get_active_backend(
        resolved, explicit_path=index_path is not None, project_root=project_root
    )
    return backend.load()


def _bare_symbol_name(node: GraphNode) -> str:
    """Extract the bare identifier name for a ``symbol`` node (R4).

    ``node.content`` is NOT a bare name in production: ``raise_core.
    discovery.symbols.load_symbols`` sets it to ``symbol.signature or
    symbol.name``, and ``signature`` is always populated for real
    function/class/method scans (e.g. ``"def foo(x: list[str]) -> bool"``).
    Using it directly as ``SymbolSummary.name`` would leak the whole
    signature — including ``[``/``]`` from generics — into the synthesis
    bundle (also the root cause behind C1's bracket-corruption risk at the
    CLI's JSON-printing boundary).

    ``node.id`` is reliably ``"sym-" + ".".join([*disc?, *parent?, name])``
    (``raise_core.discovery.symbols._symbol_node_id``) — the last dotted
    segment is always the bare ``symbol.name``. ``removeprefix("sym-")``
    covers the no-dot case (a top-level symbol with no discriminator or
    parent yields ``id == "sym-name"``, which has no dot to split on).
    """
    return node.id.rsplit(".", 1)[-1].removeprefix("sym-")


def build_bundle(
    module_id: str,
    *,
    graph: Graph | None = None,
    index_path: Path | None = None,
    project_root: Path | None = None,
) -> SynthesisBundle:
    """Assemble the complete, deterministic synthesis input for one module.

    Args:
        module_id: e.g. ``"mod-graph"``.
        graph: Pre-loaded ``Graph`` to query directly (test injection point
            — bypasses disk I/O entirely). Production callers omit this.
        index_path: Explicit graph index path, forwarded to the backend
            when ``graph`` is not supplied. ``None`` uses the project
            default (``.raise/rai/memory/index.json``).
        project_root: Root to resolve the active backend against (SQLite/
            Dual/Api checkout scoping) when ``graph`` is not supplied.
            ``None`` uses ``get_active_backend``'s own default
            (``resolve_checkout_root()``, CWD-based). Callers that operate
            against a directory other than process CWD (e.g. a workflow
            gate's ``context.working_dir``) must pass this explicitly.

    Returns:
        A ``SynthesisBundle`` with ``fingerprint`` already computed.

    Raises:
        ModuleNotFoundInGraphError: no node ``module_id`` in the graph.
    """
    active_graph = graph if graph is not None else load_graph(index_path, project_root)
    engine = QueryEngine(active_graph)

    ctx = engine.get_architectural_context(module_id)
    if ctx is None:
        raise ModuleNotFoundInGraphError(
            f"module not found in graph: {module_id} "
            "(run 'rai graph build' first, or check the module id)"
        )

    module = ctx.module
    metadata = module.metadata

    symbols = [
        SymbolSummary(
            name=_bare_symbol_name(node),
            kind=str(node.metadata.get("kind", "")),
            file=str(node.metadata.get("file", "")),
        )
        for node in active_graph.get_concepts_by_type("symbol")
        if node.metadata.get("module") == module_id
    ]

    bundle = SynthesisBundle(
        module_id=module_id,
        name=module_id.removeprefix("mod-"),
        purpose=module.content,
        depends_on=list(metadata.get("depends_on", [])),
        depended_by=list(metadata.get("depended_by", [])),
        public_api=list(metadata.get("public_api", [])),
        entry_points=list(metadata.get("entry_points", [])),
        code_imports=list(metadata.get("code_imports", [])),
        code_exports=list(metadata.get("code_exports", [])),
        code_components=int(metadata.get("code_components", 0)),
        symbols=symbols,
    )
    bundle.fingerprint = fingerprint(bundle)
    return bundle
