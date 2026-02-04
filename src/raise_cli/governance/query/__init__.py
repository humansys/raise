"""Query engine for extracting Minimum Viable Context (MVC) from concept graphs.

This module provides a query interface for retrieving relevant governance
concepts from the concept graph, enabling AI agents to access only the
context they need instead of loading entire files.

Examples:
    >>> from raise_cli.governance.query import ContextQueryEngine, ContextQuery
    >>> engine = ContextQueryEngine.from_cache()
    >>> result = engine.query(ContextQuery(query="req-rf-05"))
    >>> print(f"Tokens: {result.metadata.token_estimate}")
"""

from raise_cli.governance.query.engine import ContextQueryEngine
from raise_cli.governance.query.models import (
    ContextMetadata,
    ContextQuery,
    ContextResult,
    QueryStrategy,
)

__all__ = [
    "ContextQueryEngine",
    "ContextQuery",
    "ContextResult",
    "ContextMetadata",
    "QueryStrategy",
]
