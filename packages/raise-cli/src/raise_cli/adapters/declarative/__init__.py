"""Declarative MCP adapter framework.

Enables integration of any MCP server via YAML config instead of Python code.

Architecture: ADR-041, E337
"""

from raise_cli.adapters.declarative.adapter import DeclarativeMcpAdapter
from raise_cli.adapters.declarative.expressions import ExpressionEvaluator
from raise_cli.adapters.declarative.schema import (
    AdapterMeta,
    DeclarativeAdapterConfig,
    MethodMapping,
    ResponseMapping,
)
from raise_cli.mcp.schema import ServerConnection

__all__ = [
    "AdapterMeta",
    "DeclarativeAdapterConfig",
    "DeclarativeMcpAdapter",
    "ExpressionEvaluator",
    "MethodMapping",
    "ResponseMapping",
    "ServerConnection",
]
