"""Unified context graph for cross-domain knowledge retrieval.

This module provides the unified context graph that merges governance,
memory, and work graphs into a single queryable structure.

Components:
    - models: ConceptNode, ConceptEdge, NodeType, EdgeType
    - graph: UnifiedGraph class wrapping NetworkX
    - query: UnifiedQueryEngine for context retrieval
    - diff: Graph diffing for change detection
"""

from __future__ import annotations

from rai_cli.context.builder import UnifiedGraphBuilder
from rai_cli.context.diff import GraphDiff, NodeChange, diff_graphs
from rai_cli.context.graph import UnifiedGraph
from rai_cli.context.models import (
    ConceptEdge,
    ConceptNode,
    CoreEdgeTypes,
    EdgeType,
    GraphEdge,
    GraphNode,
    NodeType,
)
from rai_cli.context.query import (
    UnifiedQuery,
    UnifiedQueryEngine,
    UnifiedQueryMetadata,
    UnifiedQueryResult,
    UnifiedQueryStrategy,
)

__all__ = [
    "ConceptEdge",
    "ConceptNode",
    "CoreEdgeTypes",
    "EdgeType",
    "GraphDiff",
    "GraphEdge",
    "GraphNode",
    "NodeChange",
    "NodeType",
    "UnifiedGraph",
    "UnifiedGraphBuilder",
    "diff_graphs",
    "UnifiedQuery",
    "UnifiedQueryEngine",
    "UnifiedQueryMetadata",
    "UnifiedQueryResult",
    "UnifiedQueryStrategy",
]
