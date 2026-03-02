"""Declarative MCP adapter framework.

Enables integration of any MCP server via YAML config instead of Python code.

Architecture: ADR-041, E337
"""

from rai_cli.adapters.declarative.adapter import DeclarativeMcpAdapter
from rai_cli.adapters.declarative.expressions import ExpressionEvaluator
from rai_cli.adapters.declarative.schema import (
    AdapterMeta,
    DeclarativeAdapterConfig,
    MethodMapping,
    ResponseMapping,
    ServerConfig,
)

__all__ = [
    "AdapterMeta",
    "DeclarativeAdapterConfig",
    "DeclarativeMcpAdapter",
    "ExpressionEvaluator",
    "MethodMapping",
    "ResponseMapping",
    "ServerConfig",
]
