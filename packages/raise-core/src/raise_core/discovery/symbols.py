"""Symbols loader for the context graph (S2162.1).

Scans the project for public code symbols (functions, classes, methods)
and emits typed ``SymbolNode`` entries plus ``implements_symbol`` edges
from owning modules. Edge types ``calls`` and ``inherits_from`` are
added by follow-up extraction (S2162.1 T4).

Policy (ADR-E2162-1):
    - Only public symbols are ingested (name without leading underscore).
    - Private symbols remain in scanner output for non-graph consumers.
"""

from __future__ import annotations

import ast
import enum
import time
import tomllib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

from raise_core.discovery.scanner import Symbol, scan_directory
from raise_core.graph.models import GraphEdge, GraphNode, SymbolNode

# Edge type constants (flat string registry per E2162 design)
EDGE_IMPLEMENTS_SYMBOL = "implements_symbol"
EDGE_CALLS = "calls"
EDGE_INHERITS_FROM = "inherits_from"

# AST node types that represent a branching decision point for McCabe complexity.
# Baseline 1 is added by _count_branches (linear function = 1).
# Resolved in ADR-E2162-4: 5-node set (If, For, While, ExceptHandler, BoolOp).
# ast.With and ast.comprehension deliberately excluded — see ADR-E2162-4.
_BRANCH_NODES: tuple[type[ast.AST], ...] = (
    ast.If,
    ast.For,
    ast.While,
    ast.ExceptHandler,
    ast.BoolOp,
)


def _count_branches(body_node: ast.AST) -> int:
    """McCabe branch count for a function/method body (baseline 1).

    Counts structural decision points in the AST and adds the baseline
    of 1 (a linear function with no branches has complexity 1).
    """
    return 1 + sum(1 for n in ast.walk(body_node) if isinstance(n, _BRANCH_NODES))


# Heuristic source directories to scan when no manifest is available.
_HEURISTIC_SRC_DIRS: tuple[str, ...] = ("src", "lib", "app")


def _resolve_source_roots(project_root: Path) -> list[tuple[str, Path]]:  # noqa: C901
    """Resolve source roots to scan from manifest or heuristics.

    Priority:
    1. manifest.yaml apps[].path + /src (monorepo with apps)
    2. manifest.yaml single-project with src/ convention
    3. Heuristic: src/, lib/, app/ at project root
    4. Final fallback: project root itself (flat layout)
    """
    manifest_path = project_root / ".raise" / "manifest.yaml"
    if manifest_path.exists():
        try:
            data: dict[str, Any] = (
                yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
            )
            project = data.get("project", {})
            apps: list[dict[str, Any]] = project.get("apps", [])
            if apps:
                roots: list[tuple[str, Path]] = []
                for app in apps:
                    app_path = app.get("path", "")
                    if not app_path:
                        continue
                    src_dir = project_root / app_path / "src"
                    if src_dir.exists():
                        rel = f"{app_path}/src"
                        roots.append((rel, src_dir))
                    elif (project_root / app_path).exists():
                        roots.append((app_path, project_root / app_path))
                if roots:
                    return roots
        except (yaml.YAMLError, OSError):
            pass

    for dirname in _HEURISTIC_SRC_DIRS:
        candidate = project_root / dirname
        if candidate.exists() and candidate.is_dir():
            return [(dirname, candidate)]

    # Monorepo without manifest: packages/*/src pattern
    packages_dir = project_root / "packages"
    if packages_dir.exists():
        roots: list[tuple[str, Path]] = []
        for pkg in sorted(packages_dir.iterdir()):
            src_dir = pkg / "src"
            if src_dir.exists() and src_dir.is_dir():
                rel = f"packages/{pkg.name}/src"
                roots.append((rel, src_dir))
        if roots:
            return roots
        return [("packages", packages_dir)]

    return [(".", project_root)]


class IngestReport(BaseModel):
    """Observability report for a single ``load_symbols`` invocation."""

    symbols_ingested: int = 0
    edges_created: dict[str, int] = Field(default_factory=dict)
    total_nodes_after: int = 0
    skipped_private: int = 0
    stub_modules_created: int = 0
    elapsed_ms: float = 0.0


# Scanner ``kind`` values that represent callable / definable surface.
# ``module`` entries are dropped because dedicated ModuleNodes already
# cover that concern and same-named function/module pairs collide on id.
_SYMBOL_KINDS: frozenset[str] = frozenset({"function", "class", "method"})

_DEPTH_KINDS: dict[str, frozenset[str]] = {
    "classes": frozenset({"class"}),
    "functions": frozenset({"function", "class"}),
    "full": frozenset({"function", "class", "method"}),
}


class SymbolDepth(str, enum.Enum):
    """Controls which symbol kinds are included in the graph index."""

    NONE = "none"
    CLASSES = "classes"
    FUNCTIONS = "functions"
    FULL = "full"


def _is_symbol_kind(symbol: Symbol) -> bool:
    """True if the scanner entry is a callable/class surface, not a module."""
    return symbol.kind in _SYMBOL_KINDS


def _is_public(symbol: Symbol) -> bool:
    """Public-API filter: name does not start with an underscore."""
    return not symbol.name.startswith("_")


def _find_package_root_index(parts: tuple[str, ...]) -> int | None:
    """Find the index of the Python package root directory in a path.

    Heuristic: the first directory after 'src/' that looks like a Python
    package (contains underscore or is a common package pattern), or if no
    'src/' exists, the first directory that looks like a package name
    (not a common structural dir like packages/, lib/, app/).
    """
    structural = {"packages", "src", "lib", "app", "tests", "test"}
    # Prefer: segment right after 'src'
    for i, part in enumerate(parts):
        if part == "src" and i + 1 < len(parts):
            candidate = parts[i + 1]
            if not candidate.endswith(".py"):
                return i + 1
    # Fallback: first non-structural directory
    for i, part in enumerate(parts):
        if part not in structural and not part.endswith(".py") and "." not in part:
            return i
    return None


def _module_id_from_file(file: str) -> str | None:
    """Derive ``mod-<name>`` id from a repo-relative source path.

    Finds the package root and uses the first subdirectory after it as the
    module name. Returns None for top-level files (no module subfolder).

    Examples:
        ``packages/raise-cli/src/raise_cli/discovery/scanner.py`` -> ``mod-discovery``
        ``src/myapp/core/models.py``                               -> ``mod-core``
        ``src/myapp/main.py``                                      -> None
    """
    parts = Path(file).parts
    pkg_idx = _find_package_root_index(parts)
    if pkg_idx is None:
        return None
    if pkg_idx + 1 >= len(parts):
        return None
    candidate = parts[pkg_idx + 1]
    if candidate.endswith(".py"):
        return None
    return f"mod-{candidate}"


def _file_discriminator(file: str) -> str:
    """Dotted subpath from the package root, extension stripped.

    Produces enough path information to disambiguate public symbols that
    share a bare filestem but live in different sub-directories.
    Falls back to the bare stem when no package root is found.
    """
    parts = Path(file).parts
    pkg_idx = _find_package_root_index(parts)
    if pkg_idx is not None:
        tail = parts[pkg_idx + 1 :]
        if not tail:
            return ""
        last = Path(tail[-1]).stem
        sub = [*tail[:-1], last]
        return ".".join(p for p in sub if p and p != "__init__")
    return Path(file).stem


def _symbol_node_id(symbol: Symbol) -> str:
    """Deterministic SymbolNode id: ``sym-<dotted-subpath>.<parent>.<name>``.

    The dotted subpath (``cli.commands.doctor``) disambiguates same-named
    public symbols across files — including files that share a filestem
    but live in sibling sub-directories that collapse into the same
    ``mod-*`` (e.g. ``api/v1/members.py`` vs ``api/v2/members.py``).
    Without it the loader silently drops all but the first symbol during
    graph dedup. The owning ``module_id`` is resolved separately for the
    ``implements_symbol`` edge source; it is not encoded in the id.
    """
    parts: list[str] = []
    disc = _file_discriminator(symbol.file)
    if disc:
        parts.append(disc)
    if symbol.parent:
        parts.append(symbol.parent)
    parts.append(symbol.name)
    return "sym-" + ".".join(parts)


def load_symbols(  # noqa: C901 — scan/filter/emit pipeline, extraction would obscure flow
    project_root: Path,
    depth: SymbolDepth = SymbolDepth.FULL,
) -> tuple[list[GraphNode], list[GraphEdge], IngestReport]:
    """Scan ``project_root`` and build SymbolNode + edges.

    Args:
        project_root: Repository root to scan.
        depth: Which symbol kinds to include (none/classes/functions/full).

    Returns:
        Tuple of (nodes, edges, report). Safe to extend ``all_nodes`` and
        ``structural_edges`` in :class:`GraphBuilder.build`.
    """
    if depth == SymbolDepth.NONE:
        return [], [], IngestReport(elapsed_ms=0.0)

    allowed_kinds = _DEPTH_KINDS[depth.value]

    start = time.perf_counter()
    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []
    skipped_private = 0

    created_iso = datetime.now(tz=UTC).isoformat()

    # Resolve source roots from manifest or heuristics, then scan.
    # Re-prefix symbol.file with the scan root so it is repo-relative.
    all_symbols: list[Symbol] = []
    scan_plan = _resolve_source_roots(project_root)

    for rel, root in scan_plan:
        result = scan_directory(root)
        for sym in result.symbols:
            sym.file = f"{rel}/{sym.file}"
            all_symbols.append(sym)

    for symbol in all_symbols:
        if not _is_symbol_kind(symbol):
            continue
        if symbol.kind not in allowed_kinds:
            continue
        if not _is_public(symbol):
            skipped_private += 1
            continue

        module_id = _module_id_from_file(symbol.file)
        node_id = _symbol_node_id(symbol)

        # branch_count default 1 (linear function baseline); overwritten during
        # AST walk for functions/methods with actual branching nodes (S2162.2 T1).
        # Classes always remain at 1 — they are containers, not callables.
        node = SymbolNode(
            id=node_id,
            content=symbol.signature or symbol.name,
            source_file=symbol.file,
            created=created_iso,
            metadata={
                "module": module_id or "",
                "kind": symbol.kind,
                "signature": symbol.signature,
                "public": True,
                "file": symbol.file,
                "line": symbol.line,
                "parent": symbol.parent or "",
                "branch_count": 1,
            },
        )
        nodes.append(node)

        if module_id is not None:
            edges.append(
                GraphEdge(
                    source=module_id,
                    target=node_id,
                    type=EDGE_IMPLEMENTS_SYMBOL,
                    weight=1.0,
                )
            )

    # Emit stub ModuleNodes for mod-* IDs referenced by edges (S2674.1).
    # Builder dedup (RAISE-648) ensures YAML-defined modules take precedence.
    referenced_mod_ids: set[str] = set()
    for edge in edges:
        if edge.type == EDGE_IMPLEMENTS_SYMBOL:
            referenced_mod_ids.add(edge.source)

    stub_nodes: list[GraphNode] = []
    for mod_id in sorted(referenced_mod_ids):
        stub_nodes.append(
            GraphNode(
                id=mod_id,
                type="module",
                content=f"Auto-generated from code scan ({mod_id.removeprefix('mod-')})",
                source_file=None,
                created=created_iso,
            )
        )

    # Stubs before symbols so they're available for edge validation in builder
    nodes = stub_nodes + nodes

    # Python-only call/inherits extraction (T4). TS/JS/PHP deferred — see ADR.
    call_edges, inherits_edges = _extract_python_edges(project_root, nodes)
    edges.extend(call_edges)
    edges.extend(inherits_edges)

    elapsed_ms = (time.perf_counter() - start) * 1000.0
    report = IngestReport(
        symbols_ingested=len(nodes) - len(stub_nodes),
        edges_created={
            EDGE_IMPLEMENTS_SYMBOL: sum(
                1 for e in edges if e.type == EDGE_IMPLEMENTS_SYMBOL
            ),
            EDGE_CALLS: len(call_edges),
            EDGE_INHERITS_FROM: len(inherits_edges),
        },
        total_nodes_after=0,  # populated by builder after graph.add_concept
        skipped_private=skipped_private,
        stub_modules_created=len(stub_nodes),
        elapsed_ms=elapsed_ms,
    )
    return nodes, edges, report


def _extract_python_edges(
    project_root: Path, nodes: list[GraphNode]
) -> tuple[list[GraphEdge], list[GraphEdge]]:
    """Second pass: parse each Python source file and derive edges.

    Returns (calls, inherits_from) edge lists. Dynamic/getattr-style calls
    and calls to non-ingested (private, external) names are silently dropped —
    a v1 limitation documented in ADR-E2162-1.

    Also writes accurate ``branch_count`` into each callable SymbolNode's
    metadata (overwriting the default 1 set at construction time). S2162.2 T1.
    Annotates contract surface nodes (RAISE-15253) — Protocol, ABC,
    entry-point, and Pydantic BaseModel subclasses.
    """
    # Index by (file, symbol_name) → node_id for local resolution,
    # and by name alone for cross-file fallback (last-write-wins).
    by_file_name: dict[tuple[str, str], str] = {}
    by_name: dict[str, str] = {}
    # node_by_id: maps node_id → mutable GraphNode so _walk_python_tree can
    # write branch_count directly into node.metadata (S2162.2 T1).
    node_by_id: dict[str, GraphNode] = {}
    for node in nodes:
        if node.type != "symbol":
            continue
        file = node.metadata.get("file", "")
        name = node.id.rsplit(".", 1)[-1]  # tail of sym-<module>.<parent>.<name>
        by_file_name[(file, name)] = node.id
        by_name[name] = node.id
        node_by_id[node.id] = node

    entry_point_set = _load_entry_point_pairs(project_root)

    call_edges: list[GraphEdge] = []
    inherits_edges: list[GraphEdge] = []

    # Collect unique files from ingested symbols so we parse each once.
    files = sorted({node.metadata.get("file", "") for node in nodes})
    for rel_file in files:
        if not rel_file.endswith(".py"):
            continue
        path = project_root / rel_file
        if not path.exists():
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=rel_file)
        except (SyntaxError, UnicodeDecodeError):
            continue

        _walk_python_tree(
            tree=tree,
            rel_file=rel_file,
            by_file_name=by_file_name,
            by_name=by_name,
            node_by_id=node_by_id,
            call_edges=call_edges,
            inherits_edges=inherits_edges,
            entry_point_set=entry_point_set,
        )

    _apply_pydantic_transitive_contracts(node_by_id, inherits_edges)
    return call_edges, inherits_edges


def _resolve_name(
    name: str,
    rel_file: str,
    by_file_name: dict[tuple[str, str], str],
    by_name: dict[str, str],
) -> str | None:
    """Lookup a bare name against file-scoped index first, then global."""
    return by_file_name.get((rel_file, name)) or by_name.get(name)


def _callable_name(expr: ast.expr) -> str | None:
    """Extract the callee/base name from an ast.Call.func or ClassDef.base."""
    if isinstance(expr, ast.Name):
        return expr.id
    if isinstance(expr, ast.Attribute):
        return expr.attr
    return None


# ---------------------------------------------------------------------------
# Contract surface detection (RAISE-15253)
# ---------------------------------------------------------------------------


def _is_protocol_base(base: ast.expr) -> bool:
    """True if the base expression refers to Protocol (bare, subscripted, or attributed)."""
    if isinstance(base, ast.Name):
        return base.id == "Protocol"
    if isinstance(base, ast.Attribute):
        return base.attr == "Protocol"
    if isinstance(base, ast.Subscript):
        return _is_protocol_base(base.value)
    return False


def _is_abc_base(base: ast.expr) -> bool:
    """True if base refers to the ABC convenience class."""
    if isinstance(base, ast.Name):
        return base.id == "ABC"
    if isinstance(base, ast.Attribute):
        return base.attr == "ABC"
    return False


def _is_pydantic_base(base: ast.expr) -> bool:
    """True if base refers to Pydantic BaseModel."""
    if isinstance(base, ast.Name):
        return base.id == "BaseModel"
    if isinstance(base, ast.Attribute):
        return base.attr == "BaseModel"
    return False


def _has_metaclass_abcmeta(cls: ast.ClassDef) -> bool:
    """True if ClassDef declares metaclass=ABCMeta."""
    for kw in cls.keywords:
        if kw.arg != "metaclass":
            continue
        v = kw.value
        if isinstance(v, ast.Name) and v.id == "ABCMeta":
            return True
        if isinstance(v, ast.Attribute) and v.attr == "ABCMeta":
            return True
    return False


def _has_abstractmethod(cls: ast.ClassDef) -> bool:
    """True if any direct method carries @abstractmethod."""
    for item in cls.body:
        if not isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
            continue
        for dec in item.decorator_list:
            if isinstance(dec, ast.Name) and dec.id == "abstractmethod":
                return True
            if isinstance(dec, ast.Attribute) and dec.attr == "abstractmethod":
                return True
    return False


def _detect_contract_kind(cls: ast.ClassDef) -> str | None:
    """Return contract_kind for a ClassDef, or None if it is not a contract.

    Priority order: protocol > abc > pydantic_schema.
    Entry-point detection is handled separately (not AST-derivable here).
    """
    for base in cls.bases:
        if _is_protocol_base(base):
            return "protocol"
    for base in cls.bases:
        if _is_abc_base(base):
            return "abc"
    if _has_metaclass_abcmeta(cls) or _has_abstractmethod(cls):
        return "abc"
    for base in cls.bases:
        if _is_pydantic_base(base):
            return "pydantic_schema"
    return None


def _collect_entry_point_refs(data: dict[str, Any]) -> list[str]:
    """Extract all entry-point reference strings from a parsed pyproject.toml."""
    refs: list[str] = []
    project = data.get("project", {})
    refs.extend(project.get("scripts", {}).values())
    for group in project.get("entry-points", {}).values():
        refs.extend(group.values())
    tool = data.get("tool", {})
    refs.extend(tool.get("poetry", {}).get("scripts", {}).values())
    return refs


def _load_entry_point_pairs(project_root: Path) -> frozenset[tuple[str, str]]:
    """Parse pyproject.toml files and return (file_suffix, callable_name) pairs.

    Searches ``project_root/pyproject.toml`` and all ``packages/*/pyproject.toml``
    files (monorepo layout). For each entry-point ``"module.path:callable"``,
    the module path is converted to a slash-separated file suffix
    (``module/path.py``) for suffix-matching against repo-relative paths.

    Returns an empty frozenset when no pyproject.toml is found or all are malformed.
    """
    candidates: list[Path] = [project_root / "pyproject.toml"]
    packages_dir = project_root / "packages"
    if packages_dir.is_dir():
        candidates.extend(packages_dir.glob("*/pyproject.toml"))

    all_refs: list[str] = []
    for pyproject in candidates:
        if not pyproject.exists():
            continue
        try:
            data: dict[str, Any] = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        except (tomllib.TOMLDecodeError, OSError):
            continue
        all_refs.extend(_collect_entry_point_refs(data))

    pairs: set[tuple[str, str]] = set()
    for ref in all_refs:
        if ":" not in ref:
            continue
        module_path, callable_name = ref.split(":", 1)
        name = callable_name.split(".")[-1].strip()
        file_suffix = module_path.replace(".", "/") + ".py"
        pairs.add((file_suffix, name))
    return frozenset(pairs)


def _apply_pydantic_transitive_contracts(
    node_by_id: dict[str, GraphNode],
    inherits_edges: list[GraphEdge],
) -> None:
    """Propagate pydantic_schema contract kind transitively via inherits_from edges.

    Any class that inherits (directly or transitively) from a node already
    marked ``contract_kind="pydantic_schema"`` is also marked as a schema.
    Uses BFS on the reversed inherits_from graph.
    """
    # Build child → parents map
    children_of: dict[str, list[str]] = {}
    for edge in inherits_edges:
        if edge.type != EDGE_INHERITS_FROM:
            continue
        children_of.setdefault(edge.target, []).append(edge.source)

    # Seed: all nodes already marked pydantic_schema (direct BaseModel subclasses)
    queue = [
        nid
        for nid, node in node_by_id.items()
        if node.metadata.get("contract_kind") == "pydantic_schema"
    ]
    visited: set[str] = set(queue)
    while queue:
        parent_id = queue.pop()
        for child_id in children_of.get(parent_id, []):
            if child_id in visited:
                continue
            visited.add(child_id)
            child = node_by_id.get(child_id)
            if child is not None and child.type == "symbol":
                # Respect priority: never downgrade protocol/abc to pydantic_schema
                existing = child.metadata.get("contract_kind")
                if existing not in {"protocol", "abc"}:
                    child.metadata["is_contract"] = True
                    child.metadata["contract_kind"] = "pydantic_schema"
            queue.append(child_id)


def _emit_calls_from_body(
    *,
    owner_id: str,
    body_node: ast.AST,
    rel_file: str,
    by_file_name: dict[tuple[str, str], str],
    by_name: dict[str, str],
    call_edges: list[GraphEdge],
) -> None:
    """Walk a function/method body and emit calls edges for resolvable callees."""
    for child in ast.walk(body_node):
        if not isinstance(child, ast.Call):
            continue
        callee = _callable_name(child.func)
        if not callee or callee.startswith("_"):
            continue
        target_id = _resolve_name(callee, rel_file, by_file_name, by_name)
        if target_id and target_id != owner_id:
            call_edges.append(
                GraphEdge(
                    source=owner_id,
                    target=target_id,
                    type=EDGE_CALLS,
                    weight=1.0,
                )
            )


def _emit_inherits(
    *,
    cls: ast.ClassDef,
    class_id: str,
    rel_file: str,
    by_file_name: dict[tuple[str, str], str],
    by_name: dict[str, str],
    inherits_edges: list[GraphEdge],
) -> None:
    for base in cls.bases:
        bname = _callable_name(base)
        if not bname or bname.startswith("_"):
            continue
        base_id = _resolve_name(bname, rel_file, by_file_name, by_name)
        if base_id and base_id != class_id:
            inherits_edges.append(
                GraphEdge(
                    source=class_id,
                    target=base_id,
                    type=EDGE_INHERITS_FROM,
                    weight=1.0,
                )
            )


def _walk_python_tree(  # noqa: C901 — tree walker pipeline, extraction would obscure flow
    *,
    tree: ast.AST,
    rel_file: str,
    by_file_name: dict[tuple[str, str], str],
    by_name: dict[str, str],
    node_by_id: dict[str, GraphNode],
    call_edges: list[GraphEdge],
    inherits_edges: list[GraphEdge],
    entry_point_set: frozenset[tuple[str, str]] = frozenset(),
) -> None:
    """Walk a parsed AST, emitting calls + inherits_from edges and contract tags.

    Also writes accurate ``branch_count`` into each callable SymbolNode's
    metadata, overwriting the default 1 set during first-pass construction.
    Nodes that cannot be resolved keep the default value of 1. (S2162.2 T1)

    Contract detection (RAISE-15253): annotates SymbolNodes with
    ``is_contract=True`` and ``contract_kind`` for Protocol, ABC, entry-point,
    and Pydantic BaseModel subclasses.
    """

    def _annotate_contract(node: GraphNode, kind: str) -> None:
        node.metadata["is_contract"] = True
        node.metadata["contract_kind"] = kind

    def _is_entry_point(name: str) -> bool:
        if not entry_point_set:
            return False
        for ep_suffix, ep_name in entry_point_set:
            if ep_name != name:
                continue
            if rel_file == ep_suffix or rel_file.endswith("/" + ep_suffix):
                return True
        return False

    for top in ast.iter_child_nodes(tree):
        if isinstance(top, ast.FunctionDef | ast.AsyncFunctionDef):
            fn_id = _resolve_name(top.name, rel_file, by_file_name, by_name)
            if fn_id is not None:
                _emit_calls_from_body(
                    owner_id=fn_id,
                    body_node=top,
                    rel_file=rel_file,
                    by_file_name=by_file_name,
                    by_name=by_name,
                    call_edges=call_edges,
                )
                fn_node = node_by_id.get(fn_id)
                if fn_node is not None:
                    fn_node.metadata["branch_count"] = _count_branches(top)
                    if _is_entry_point(top.name):
                        _annotate_contract(fn_node, "entry_point")
        elif isinstance(top, ast.ClassDef):
            class_id = _resolve_name(top.name, rel_file, by_file_name, by_name)
            if class_id is not None:
                _emit_inherits(
                    cls=top,
                    class_id=class_id,
                    rel_file=rel_file,
                    by_file_name=by_file_name,
                    by_name=by_name,
                    inherits_edges=inherits_edges,
                )
                class_node = node_by_id.get(class_id)
                if class_node is not None:
                    # Entry-point check takes lowest priority (specific > general)
                    # Contract kind detection (protocol > abc > pydantic_schema)
                    kind = _detect_contract_kind(top)
                    if kind is not None:
                        _annotate_contract(class_node, kind)
                    elif _is_entry_point(top.name):
                        _annotate_contract(class_node, "entry_point")
            for item in top.body:
                if not isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                    continue
                method_id = by_file_name.get((rel_file, item.name))
                if method_id is None:
                    continue
                _emit_calls_from_body(
                    owner_id=method_id,
                    body_node=item,
                    rel_file=rel_file,
                    by_file_name=by_file_name,
                    by_name=by_name,
                    call_edges=call_edges,
                )
                method_node = node_by_id.get(method_id)
                if method_node is not None:
                    method_node.metadata["branch_count"] = _count_branches(item)
