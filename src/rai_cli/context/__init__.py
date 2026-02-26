"""Context module for cross-domain knowledge retrieval.

Re-exports graph domain types from rai_core and local context components.
"""

from __future__ import annotations

from rai_cli.context.builder import GraphBuilder
from rai_cli.context.diff import GraphDiff, NodeChange, diff_graphs
from rai_core.graph.engine import Graph
from rai_core.graph.models import (
    CoreEdgeTypes,
    EdgeType,
    GraphEdge,
    GraphNode,
    NodeType,
)
from rai_core.graph.query import (
    Query,
    QueryEngine,
    QueryMetadata,
    QueryResult,
    QueryStrategy,
)

__all__ = [
    "CoreEdgeTypes",
    "EdgeType",
    "Graph",
    "GraphDiff",
    "GraphEdge",
    "GraphNode",
    "NodeChange",
    "NodeType",
    "Query",
    "QueryEngine",
    "QueryMetadata",
    "QueryResult",
    "QueryStrategy",
    "GraphBuilder",
    "diff_graphs",
]
