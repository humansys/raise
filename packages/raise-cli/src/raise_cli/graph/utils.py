"""Helpers puros para operaciones con grafos locales.

Canónico para parseo de payload server→Graph y merge LWW.
Reutilizado por `rai graph pull` y `_pull_knowledge_sync` (S-KS.1).
"""

from __future__ import annotations

from typing import Any

from raise_core.graph.engine import Graph
from raise_core.graph.models import GraphEdge, GraphNode

__all__ = ["build_graph_from_payload"]


def build_graph_from_payload(payload: dict[str, Any]) -> Graph:
    """Construye un Graph desde el payload de export del server.

    Único punto de parseo node/edge → Graph. Reutilizado por:
    - `rai graph pull` (extracción de lógica inline en graph.py)
    - `_pull_knowledge_sync` en init.py (S-KS.1)

    Args:
        payload: Diccionario con claves 'nodes' y 'edges' del endpoint export.

    Returns:
        Graph con todos los nodos y aristas del payload.
    """
    graph = Graph()

    for n in payload.get("nodes", []):
        graph.add_concept(
            GraphNode(
                id=n["node_id"],
                type=n["node_type"],
                content=n["content"],
                created="",
                source_file=n.get("source_file"),
                metadata=n.get("properties", {}),
                updated_at=n.get("updated_at"),  # S-KS.1: mapear timestamp LWW
            )
        )

    for e in payload.get("edges", []):
        graph.add_relationship(
            GraphEdge(
                source=e["source_node_id"],
                target=e["target_node_id"],
                type=e["edge_type"],
                weight=e.get("weight", 1.0),
                metadata=e.get("properties", {}),
            )
        )

    return graph
