"""Protocol contract for graph backend implementations.

Architecture: ADR-036 (Graph Backend)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from raise_core.graph.backends.models import BackendHealth

if TYPE_CHECKING:
    from raise_core.graph.engine import Graph
    from raise_core.graph.models import GraphNode


@runtime_checkable
class KnowledgeGraphBackend(Protocol):
    """ADR-036: Graph storage abstraction.

    Implementations: FilesystemGraphBackend (built-in), ApiGraphBackend (PRO).
    """

    def persist(self, graph: Graph) -> None: ...  # noqa: D102

    def load(self) -> Graph: ...  # noqa: D102

    def health(self) -> BackendHealth: ...  # noqa: D102


@runtime_checkable
class GraphBundleQueryBackend(Protocol):
    """Optimized graph queries used by session bundle assembly."""

    def get_foundational_patterns(self) -> list[GraphNode]: ...  # noqa: D102

    def get_always_on_nodes(self) -> list[GraphNode]: ...  # noqa: D102

    def find_release_for_epic(  # noqa: D102
        self, epic_node_id: str
    ) -> GraphNode | None: ...


@runtime_checkable
class GraphTraversalBackend(Protocol):
    """Optimized graph traversal capability."""

    def get_module_ids(self) -> list[str]: ...  # noqa: D102

    def ego_subgraph(self, node_id: str, depth: int = 2) -> Graph: ...  # noqa: D102

    def neighbors(  # noqa: D102
        self, node_id: str, direction: str = "outgoing"
    ) -> list[tuple[str, str]]: ...  # noqa: D102

    def path(self, src: str, dst: str) -> list[str] | None: ...  # noqa: D102


@runtime_checkable
class GraphBackendMetadata(Protocol):
    """Display and diagnostics metadata for graph backends."""

    def backend_name(self) -> str: ...  # noqa: D102

    def storage_location(self) -> str: ...  # noqa: D102
