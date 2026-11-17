"""RAISE-16419-S1 — deterministic edge inventory on ``grimp.ImportGraph``.

Read-only evidence generator for the raise_cli layer model (RAISE-16340).
Builds the import graph once via grimp, aggregates it into cross-package
edges/fan metrics, and prints a JSON document to stdout. It never writes a
file and never enables grimp's on-disk cache (``cache_dir=None`` on every
``build_graph`` call) — S1's design pins this as a hard purity constraint
(D-S1-3, D-S1-6).

Metric definition (pinned for S3/S4 citations, design §2.3):

* ``fan_in_edges(P)``    — count of module -> module direct-import edges
  whose source package != P and target package == P.
* ``fan_in_packages(P)`` — number of distinct source packages in those edges.
* ``fan_out_edges``/``fan_out_packages`` are the symmetric counterparts.

grimp's defaults match the enforcement semantics used by ``lint-imports``:
type-checking imports are INCLUDED (``exclude_type_checking_imports=False``).

Invoke directly for CI evidence (arch job, D-S1-7):

    uv run python -m tests.pkg_meta.edge_inventory
"""

from __future__ import annotations

import json
import tomllib
from pathlib import Path
from typing import Any, cast

import grimp
from grimp import ImportGraph

# RAISE-19422: inlined from test_layer_contract.py so edge_inventory.py is
# self-contained on the public mirror (test_layer_contract.py is private).
# The value already appears verbatim in the public pyproject.toml (line 410).
_CONTRACT_NAME = "RAISE-16340 raise_cli 5-layer model"

_REPO_ROOT = Path(__file__).resolve().parents[4]
_ROOT_PYPROJECT = _REPO_ROOT / "pyproject.toml"


def build_project_graph(package: str = "raise_cli") -> ImportGraph:
    """Build the import graph for ``package`` with caching disabled.

    ``cache_dir=None`` is load-bearing: grimp's default writes an on-disk
    cache directory, which would violate this tool's read-only contract.
    """
    # grimp's own `build_graph` carries an unannotated `package_name`
    # parameter internally, which pyright strict surfaces as a partially
    # unknown member type on the *call*, not on anything we control here.
    return grimp.build_graph(  # pyright: ignore[reportUnknownMemberType]
        package, cache_dir=None
    )


def _package_of(module: str) -> str | None:
    """Second dotted segment of a module name, or ``None`` for the root.

    e.g. ``"raise_cli.storage.backend"`` -> ``"storage"``;
    ``"raise_cli.__main__"`` -> ``"__main__"`` (a single-file module counts
    as its own package, matching the design's own unclassified rankings);
    ``"raise_cli"`` -> ``None`` (the root has no package of its own).
    """
    parts = module.split(".")
    if len(parts) < 2:
        return None
    return parts[1]


def collect_edges(graph: ImportGraph) -> dict[tuple[str, str], int]:
    """Cross-package module-level direct edges, keyed ``(src_pkg, dst_pkg)``."""
    edges: dict[tuple[str, str], int] = {}
    for module in graph.modules:
        src_pkg = _package_of(module)
        if src_pkg is None:
            continue
        for imported in graph.find_modules_directly_imported_by(module):
            dst_pkg = _package_of(imported)
            if dst_pkg is None or dst_pkg == src_pkg:
                continue
            key = (src_pkg, dst_pkg)
            edges[key] = edges.get(key, 0) + 1
    return edges


def fan_metrics(edges: dict[tuple[str, str], int]) -> dict[str, dict[str, int]]:
    """Per-package fan-in/fan-out edge and distinct-counterparty counts."""
    metrics: dict[str, dict[str, int]] = {}

    def _entry(pkg: str) -> dict[str, int]:
        return metrics.setdefault(
            pkg,
            {
                "fan_in_edges": 0,
                "fan_out_edges": 0,
                "fan_in_packages": 0,
                "fan_out_packages": 0,
            },
        )

    fan_in_sources: dict[str, set[str]] = {}
    fan_out_targets: dict[str, set[str]] = {}

    for (src, dst), count in edges.items():
        _entry(src)["fan_out_edges"] += count
        _entry(dst)["fan_in_edges"] += count
        fan_out_targets.setdefault(src, set()).add(dst)
        fan_in_sources.setdefault(dst, set()).add(src)

    for pkg, sources in fan_in_sources.items():
        _entry(pkg)["fan_in_packages"] = len(sources)
    for pkg, targets in fan_out_targets.items():
        _entry(pkg)["fan_out_packages"] = len(targets)

    return metrics


def contract_layer_packages(pyproject: Path = _ROOT_PYPROJECT) -> frozenset[str]:
    """Flatten the RAISE-16340 ``layers`` contract into a package name set.

    Parses ``pyproject.toml`` at runtime so this stays a single source of
    truth with ``test_layer_contract.py`` (D-S1-5) — no duplicated layer list.
    """
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    importlinter = cast("dict[str, Any]", data["tool"]["importlinter"])
    contracts = cast("list[dict[str, Any]]", importlinter.get("contracts", []))
    for contract in contracts:
        if contract.get("name") == _CONTRACT_NAME:
            layers = cast("list[str]", contract["layers"])
            packages: set[str] = set()
            for layer in layers:
                packages.update(part.strip() for part in layer.split(":"))
            return frozenset(packages)
    msg = f"contract {_CONTRACT_NAME!r} not declared in {pyproject}"
    raise ValueError(msg)


def rank_unclassified(
    graph: ImportGraph, contract_layers: frozenset[str]
) -> list[tuple[str, int]]:
    """Unclassified packages ranked by ``(-fan_in_edges, name)``.

    Restricted to packages that actually appear in the edge set (i.e. have
    fan metrics), so every entry here also exists in ``packages`` — a fully
    isolated module contributes no evidence and is not "ranked".
    """
    edges = collect_edges(graph)
    metrics = fan_metrics(edges)
    unclassified = [pkg for pkg in metrics if pkg not in contract_layers]
    return sorted(
        ((pkg, metrics[pkg]["fan_in_edges"]) for pkg in unclassified),
        key=lambda pair: (-pair[1], pair[0]),
    )


def package_chains(
    graph: ImportGraph, source_pkg: str, target_pkg: str
) -> list[tuple[str, ...]]:
    """Shortest module-level chains from ``source_pkg`` to ``target_pkg``.

    Wraps ``ImportGraph.find_shortest_chains(..., as_packages=True)`` —
    package-level chain prediction including indirect intermediates. Queried
    on demand for specific pairs S3/S4 care about; not precomputed for all
    pairs (design §2.3 — unused precomputation is waste).
    """
    chains = graph.find_shortest_chains(
        f"raise_cli.{source_pkg}", f"raise_cli.{target_pkg}", as_packages=True
    )
    return sorted(chains)


def build_inventory(graph: ImportGraph) -> dict[str, Any]:
    """Assemble the JSON-ready inventory document (schema_version 1)."""
    contract_layers = contract_layer_packages()
    edges = collect_edges(graph)
    metrics = fan_metrics(edges)
    ranking = rank_unclassified(graph, contract_layers)

    return {
        "schema_version": 1,
        "package": "raise_cli",
        "module_count": len(graph.modules),
        "direct_import_count": graph.count_imports(),
        "edges": {f"{src} -> {dst}": count for (src, dst), count in edges.items()},
        "packages": {
            pkg: {**values, "classified": pkg in contract_layers}
            for pkg, values in metrics.items()
        },
        "unclassified_ranking": [[name, fan_in] for name, fan_in in ranking],
    }


def main() -> None:
    """Build the graph and print the deterministic JSON inventory to stdout."""
    graph = build_project_graph()
    inventory = build_inventory(graph)
    print(json.dumps(inventory, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
