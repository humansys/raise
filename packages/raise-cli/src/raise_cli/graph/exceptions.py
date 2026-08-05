"""Graph-specific exceptions."""

from __future__ import annotations


class GraphQueryError(RuntimeError):
    """Raised when a graph query or context lookup fails."""
