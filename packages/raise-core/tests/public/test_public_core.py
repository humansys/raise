"""Public raise-core smoke tests that require no private repo fixtures."""

from __future__ import annotations

import raise_core
from raise_core.graph.models import GraphNode, PatternNode


def test_public_core_version_and_graph_contract() -> None:
    """The wheel exposes its version and its primary typed graph contract."""
    assert raise_core.__version__.startswith("3.1.")

    node = PatternNode(
        id="PAT-1",
        content="Prefer observable release gates.",
        created="2026-07-28T00:00:00Z",
    )

    assert node.type == "pattern"
    assert GraphNode.resolve("pattern") is PatternNode
