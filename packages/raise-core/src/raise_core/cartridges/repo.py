"""Repo cartridge generator — snapshot graph-native code + structure.

RAISE-13378: the snapshot captures graph-native (``metadata.cartridge``
unset) code + structural nodes only. Governance/ontology/backlog nodes are
ingested from their own cartridges and live in the graph as first-class
citizens (``cartridge`` set to their own name) — they are excluded here so
they are never relabeled ``cartridge='repo'``. Governance is not snapshotted
by this module; its source of truth is the governance cartridge, built
separately (since S10328.7 / RAISE-13379).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import yaml

from raise_core.graph.engine import Graph

logger = logging.getLogger(__name__)

REPO_NODE_TYPES: frozenset[str] = frozenset(
    {
        "module",
        "component",
        "symbol",
        "guardrail",
        "principle",
        "requirement",
        "outcome",
        "term",
        "decision",
        "architecture",
        "bounded_context",
    }
)

# Below this prior node count, count swings are normal for small/new
# cartridges — the collapse guard does not engage.
_MIN_PRIOR_NODE_COUNT_FOR_GUARD = 20

# New node count must fall below this fraction of the prior count to trip
# the collapse guard (ordinary shrinkage from deleting a handful of modules
# will not cross this line).
_COLLAPSE_RATIO_THRESHOLD = 0.5


class RepoCartridgeCollapseError(RuntimeError):
    """Raised when a repo cartridge write would collapse the node count.

    Signals a suspiciously large drop in node count relative to the prior
    snapshot on disk (e.g. `rai graph build` run from a subdirectory that
    only sees a fraction of the repo). The prior `repo.json` is left
    untouched so the last-known-good cartridge is not silently destroyed.
    """


def _read_prior_symbol_depth(manifest_path: Path) -> str | None:
    """Read the symbol_depth recorded in a prior CARTRIDGE.yaml, if any."""
    if not manifest_path.exists():
        return None
    try:
        prior_manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        return None
    if isinstance(prior_manifest, dict):
        return prior_manifest.get("symbol_depth")
    return None


def _check_collapse_guard(
    repo_json_path: Path,
    new_count: int,
    output_dir: Path,
    *,
    depth_changed: bool,
) -> None:
    """Raise RepoCartridgeCollapseError on a real collapse; skip on depth change.

    A prior snapshot built with a different --depth has a node count that is
    not comparable to this build's — --depth none legitimately omits most
    symbols, which would otherwise look like a collapse (RAISE-16241).
    """
    if not repo_json_path.exists():
        return
    try:
        prior_nodes = json.loads(repo_json_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        logger.warning(
            "Prior repo cartridge at %s was unreadable; skipping collapse "
            "guard and writing normally.",
            repo_json_path,
        )
        return

    prior_count = len(prior_nodes) if isinstance(prior_nodes, list) else 0
    collapsed = (
        prior_count >= _MIN_PRIOR_NODE_COUNT_FOR_GUARD
        and new_count < prior_count * _COLLAPSE_RATIO_THRESHOLD
    )
    if not collapsed:
        return
    if depth_changed:
        logger.warning(
            "Repo cartridge node count dropped from %d to %d, but "
            "symbol_depth changed — counts are not comparable across "
            "depths, skipping collapse guard.",
            prior_count,
            new_count,
        )
        return

    logger.error(
        "Refusing to write repo cartridge at %s: node count "
        "collapsed from %d to %d (below %.0f%% of prior count). "
        "Prior snapshot preserved.",
        output_dir,
        prior_count,
        new_count,
        _COLLAPSE_RATIO_THRESHOLD * 100,
    )
    raise RepoCartridgeCollapseError(
        f"Refusing to write repo cartridge at {output_dir}: "
        f"node count collapsed from {prior_count} to {new_count} "
        f"(below {_COLLAPSE_RATIO_THRESHOLD:.0%} of prior count). "
        "Prior snapshot preserved."
    )


def generate_repo_cartridge(
    graph: Graph,
    output_dir: Path,
    *,
    cartridge_name: str = "repo",
    symbol_depth: str | None = None,
) -> Path:
    """Generate a repo cartridge from the existing graph.

    Filters the graph to graph-native code + structural node types (a type
    allow-list — ``REPO_NODE_TYPES`` — is a *ceiling*, not the real gate) and
    writes instances/*.json + CARTRIDGE.yaml. Nodes get
    ``metadata["cartridge"]`` set to *cartridge_name*.

    Excludes any node whose ``metadata.cartridge`` is already set: those are
    foreign nodes ingested from another cartridge (governance/ontology/
    backlog), present in the same build graph this function iterates
    (RAISE-13378 Option B). Only cartridge-unset natives — produced by
    ``load_symbols``/``load_components``/``extract_bounded_contexts``/
    ``extract_layers``, none of which route through ``ingest_cartridge`` — are
    ever captured, so this never drops a legitimate native node.
    """
    cartridge_dir = output_dir / cartridge_name
    cartridge_dir.mkdir(parents=True, exist_ok=True)
    instances_dir = cartridge_dir / "instances"
    instances_dir.mkdir(exist_ok=True)

    nodes: list[dict[str, object]] = []
    for concept in graph.iter_concepts():
        if concept.type not in REPO_NODE_TYPES:
            continue
        if concept.metadata.get("cartridge") is not None:
            continue  # foreign node ingested from another cartridge — keep its provenance
        data = concept.model_dump(mode="json")
        if not isinstance(data.get("metadata"), dict):
            data["metadata"] = {}
        data["metadata"]["cartridge"] = cartridge_name  # type: ignore[index]
        nodes.append(data)

    manifest_path = cartridge_dir / "CARTRIDGE.yaml"
    prior_symbol_depth = _read_prior_symbol_depth(manifest_path)
    depth_changed = (
        prior_symbol_depth is not None
        and symbol_depth is not None
        and prior_symbol_depth != symbol_depth
    )

    repo_json_path = instances_dir / "repo.json"
    new_count = len(nodes)
    _check_collapse_guard(
        repo_json_path, new_count, output_dir, depth_changed=depth_changed
    )

    repo_json_path.write_text(
        json.dumps(nodes, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    manifest = {
        "name": cartridge_name,
        "display_name": "Repository Knowledge",
        "version": "1.0.0",
        "schema": {
            "module": "raise_core.graph.models",
            "class_name": "GraphNode",
        },
        "source": {
            "type": "derived",
            "authority": "local",
            "generator": "raise_core.cartridges.repo:generate_repo_cartridge",
            "refresh": "signal",
        },
        # RAISE-13378 Option A: marks this cartridge as a snapshot of the
        # build graph itself — GraphBuilder.load_cartridges skips re-ingesting
        # it, so stale nodes from a prior build never feed the next one.
        "snapshot": True,
        "symbol_depth": symbol_depth,
    }
    manifest_path.write_text(
        yaml.dump(manifest, default_flow_style=False),
        encoding="utf-8",
    )

    return cartridge_dir
