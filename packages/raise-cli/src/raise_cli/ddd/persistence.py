"""DDD classification persistence — content hash, incremental filter, BC assignment persistence."""

from __future__ import annotations

import hashlib
import logging
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel

from raise_cli.ddd.clustering import BCMap
from raise_core.graph.engine import Graph
from raise_core.graph.models import (
    BoundedContextNode,
    CoreEdgeTypes,
    GraphEdge,
    SymbolNode,
    bc_node_id,
)

# ---------------------------------------------------------------------------
# BC persistence models
# ---------------------------------------------------------------------------

logger = logging.getLogger(__name__)

_SKIP_BC_NAMES: frozenset[str] = frozenset({"uncertain", "shared_kernel"})


class PersistenceResult(BaseModel):
    """Result summary from persist_bc_assignments()."""

    edges_written: int = 0
    edges_skipped: int = 0
    nodes_created: int = 0
    uncertain_skipped: int = 0
    shared_kernel_skipped: int = 0


def _ddd_content_hash(*, signature: str, module: str, kind: str) -> str:
    """Deterministic SHA-256 of the symbol's identity triple.

    Inputs are (signature, module, kind). ``module`` is derived from the file
    path (``raise_core.discovery.symbols._module_id_from_file``), so a move
    across modules changes the hash; the file name within a module and the line
    number are not inputs.

    RAISE-17923 S3: the signature is whitespace-normalized before hashing.
    ADR-148's residual-risk note observed the hash "unstable between
    branches" — a signature re-flowed by a formatter (e.g. `def
    foo(x:int)->str` vs `def foo(x: int) -> str`, or a line-wrap change) is
    the same symbol shape but previously hashed differently, forcing a
    needless reclassification (LLM cost) on every such cosmetic diff across
    worktrees on different branches. Whitespace carries no DDD-relevant
    information, so collapsing it here removes that specific source of
    churn; this does not eliminate every source of cross-branch
    instability, only the whitespace-driven one.
    """
    normalized_signature = "".join(signature.split())
    payload = f"{normalized_signature}\0{module}\0{kind}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def should_classify(
    node: SymbolNode,
    *,
    repo_wide_meta: dict[str, Any] | None = None,
) -> bool:
    """Incremental filter: decide whether a symbol needs (re)classification.

    Rules (D7, ADR-DG2, RAISE-16851 D4):
      - ratified → NEVER reclassify (human authority is sacred, rank 50)
      - yaml-derived → NEVER reclassify (module-level human decision, rank 40)
      - proposed + unchanged hash → skip (stable)
      - proposed + changed hash → reclassify
      - no ddd_layer → classify (new symbol)

    ``repo_wide_meta`` (RAISE-16612 Path 2): when provided, the "ratified" /
    "yaml-derived" gate uses this dict instead of ``node.metadata``. Pass the
    REPO_WIDE-only annotation for this node so that a checkout-scoped annotation
    cannot suppress REPO_WIDE classification.
    The hash/layer checks continue to use the merged ``node.metadata`` because
    those are incremental state comparisons, not partition-gating decisions.
    """
    gate_meta: dict[str, Any] = (
        repo_wide_meta if repo_wide_meta is not None else node.metadata
    )
    meta = node.metadata
    if gate_meta.get("ddd_source") in ("ratified", "yaml-derived"):
        return False
    if meta.get("ddd_layer") is None:
        return True
    return meta.get("ddd_content_hash") != content_hash_for(node)


def content_hash_for(node: SymbolNode) -> str:
    """Compute the content hash for a SymbolNode — single-path helper.

    Both ``should_classify`` and ``apply_classification`` use this to avoid
    hash-computation drift between reader and writer.
    """
    meta = node.metadata
    return _ddd_content_hash(
        signature=str(meta.get("signature", "")),
        module=str(meta.get("module", "")),
        kind=str(meta.get("kind", "")),
    )


def apply_classification(
    node: SymbolNode,
    *,
    ddd_layer: str,
    confidence: float,
    ddd_source: str = "proposed",
) -> None:
    """Write DDD classification metadata to a SymbolNode (in-place mutation)."""
    node.metadata["ddd_layer"] = ddd_layer
    node.metadata["ddd_source"] = ddd_source
    node.metadata["ddd_content_hash"] = content_hash_for(node)
    node.metadata["ddd_confidence"] = confidence


# ---------------------------------------------------------------------------
# BC persistence
# ---------------------------------------------------------------------------


def _count_skipped_name(result: PersistenceResult, bc_name: str) -> None:
    """Account for an assignment skipped because its name is never persisted."""
    result.edges_skipped += 1
    if bc_name == "uncertain":
        result.uncertain_skipped += 1
    else:
        result.shared_kernel_skipped += 1


def persist_bc_assignments(
    bcmap: BCMap,
    graph: Graph,
) -> PersistenceResult:
    """Persist BCMap as belongs_to edges in the knowledge graph.

    Creates BoundedContextNode for each unique bc_name in bcmap (ID: BC-{bc_name}).
    Writes belongs_to edges from each SymbolNode to its BoundedContextNode.
    Skips uncertain and shared_kernel assignments.
    Idempotent: updates existing edge metadata in-place rather than creating duplicates.

    Args:
        bcmap: BCMap from cluster_symbols() mapping symbol_id → BCAssignment.
        graph: Live Graph instance to persist nodes and edges into.

    Returns:
        PersistenceResult with counts of edges written, edges skipped, nodes created.
    """
    result = PersistenceResult()

    if not bcmap.assignments:
        return result

    # Phase 1: collect unique bc_names (excluding skipped)
    unique_bc_names: set[str] = {
        a.bc_name for a in bcmap.assignments.values() if a.bc_name not in _SKIP_BC_NAMES
    }

    # Phase 2: ensure BoundedContextNode exists for each unique bc_name
    for bc_name in unique_bc_names:
        node_id = bc_node_id(bc_name)
        if graph.get_concept(node_id) is None:
            bc_node = BoundedContextNode(
                id=node_id,
                type="bounded_context",
                content=bc_name,
                created=datetime.now(tz=UTC).isoformat(),
            )
            graph.add_concept(bc_node)
            result.nodes_created += 1
            logger.debug("Created BoundedContextNode %r", node_id)

    # Phase 3: write belongs_to edges
    for symbol_id, assignment in bcmap.assignments.items():
        if assignment.bc_name in _SKIP_BC_NAMES:
            _count_skipped_name(result, assignment.bc_name)
            continue

        target_id = bc_node_id(assignment.bc_name)
        edge_metadata: dict[str, Any] = {
            "confidence": assignment.confidence,
            "reasoning": assignment.reasoning,
        }

        if symbol_id not in graph.graph:
            logger.warning("Symbol %r not found in graph — skipping BC edge", symbol_id)
            result.edges_skipped += 1
            continue

        # Idempotency: check for existing belongs_to edge to the same BC node
        existing_key: int | None = None
        for _src, tgt, key, data in graph.graph.out_edges(
            symbol_id, keys=True, data=True
        ):
            if data.get("type") == CoreEdgeTypes.BELONGS_TO and tgt == target_id:
                existing_key = key
                break

        if existing_key is not None:
            # Update metadata in-place on the existing edge
            edge_data = graph.graph.edges[symbol_id, target_id, existing_key]
            edge_data.update(edge_metadata)
            result.edges_skipped += 1
        else:
            graph.add_relationship(
                GraphEdge(
                    source=symbol_id,
                    target=target_id,
                    type=CoreEdgeTypes.BELONGS_TO,
                    metadata=edge_metadata,
                )
            )
            result.edges_written += 1

    return result
