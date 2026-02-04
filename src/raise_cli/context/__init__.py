"""Unified context graph for cross-domain knowledge retrieval.

This module provides the unified context graph that merges governance,
memory, and work graphs into a single queryable structure.

Components:
    - models: ConceptNode, ConceptEdge, NodeType, EdgeType
    - graph: UnifiedGraph class wrapping NetworkX
    - query: UnifiedQueryEngine for context retrieval
"""

from __future__ import annotations

from raise_cli.context.builder import UnifiedGraphBuilder
from raise_cli.context.graph import UnifiedGraph
from raise_cli.context.models import ConceptEdge, ConceptNode, EdgeType, NodeType
from raise_cli.context.query import (
    UnifiedQuery,
    UnifiedQueryEngine,
    UnifiedQueryMetadata,
    UnifiedQueryResult,
    UnifiedQueryStrategy,
)

__all__ = [
    "ConceptEdge",
    "ConceptNode",
    "EdgeType",
    "NodeType",
    "UnifiedGraph",
    "UnifiedGraphBuilder",
    "UnifiedQuery",
    "UnifiedQueryEngine",
    "UnifiedQueryMetadata",
    "UnifiedQueryResult",
    "UnifiedQueryStrategy",
]
