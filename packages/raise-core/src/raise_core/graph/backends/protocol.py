"""Protocol contract for graph backend implementations.

Architecture: ADR-036 (Graph Backend)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from rai_core.graph.backends.models import BackendHealth

if TYPE_CHECKING:
    from rai_core.graph.engine import Graph


@runtime_checkable
class KnowledgeGraphBackend(Protocol):
    """ADR-036: Graph storage abstraction.

    Implementations: FilesystemGraphBackend (built-in), ApiGraphBackend (PRO).
    """

    def persist(self, graph: Graph) -> None: ...

    def load(self) -> Graph: ...

    def health(self) -> BackendHealth: ...
