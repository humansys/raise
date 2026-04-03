"""Tests for retrieval models and DomainAdapter protocol."""

from __future__ import annotations

import pytest

from rai_agent.knowledge.retrieval.models import (
    DomainAdapter,
    DomainHints,
    RetrievalResult,
    ScoredNode,
    TraversalAdvice,
)
from raise_core.graph.models import GraphNode

# --- DomainHints ---


class TestDomainHints:
    def test_basic_construction(self) -> None:
        hints = DomainHints(domain="test")
        assert hints.domain == "test"

    def test_extra_fields_allowed(self) -> None:
        hints = DomainHints(domain="test", custom_field="value", score=42)
        assert hints.model_extra is not None
        assert hints.model_extra["custom_field"] == "value"
        assert hints.model_extra["score"] == 42

    def test_domain_required(self) -> None:
        with pytest.raises(Exception):  # noqa: B017
            DomainHints()  # type: ignore[call-arg]


# --- TraversalAdvice ---


class TestTraversalAdvice:
    def test_defaults(self) -> None:
        advice = TraversalAdvice()
        assert advice.start_node_ids == []
        assert advice.edge_type_filter is None
        assert advice.node_type_filter is None
        assert advice.max_depth == 2

    def test_custom_values(self) -> None:
        advice = TraversalAdvice(
            start_node_ids=["node-1", "node-2"],
            edge_type_filter=["requires", "feeds_into"],
            node_type_filter=["tool"],
            max_depth=3,
        )
        assert advice.start_node_ids == ["node-1", "node-2"]
        assert advice.edge_type_filter == ["requires", "feeds_into"]
        assert advice.node_type_filter == ["tool"]
        assert advice.max_depth == 3


# --- ScoredNode ---


class TestScoredNode:
    @pytest.fixture
    def sample_node(self) -> GraphNode:
        return GraphNode(id="n1", content="Test node", created="2026-01-01")

    def test_construction(self, sample_node: GraphNode) -> None:
        scored = ScoredNode(node=sample_node, score=0.85, explanation="test")
        assert scored.node.id == "n1"
        assert scored.score == 0.85
        assert scored.explanation == "test"

    def test_sorting_by_score_descending(self, sample_node: GraphNode) -> None:
        low = ScoredNode(node=sample_node, score=0.3, explanation="low")
        mid = ScoredNode(node=sample_node, score=0.6, explanation="mid")
        high = ScoredNode(node=sample_node, score=0.9, explanation="high")

        sorted_nodes = sorted([low, high, mid], reverse=True)
        assert [n.score for n in sorted_nodes] == [0.9, 0.6, 0.3]

    def test_default_explanation_empty(self, sample_node: GraphNode) -> None:
        scored = ScoredNode(node=sample_node, score=0.5)
        assert scored.explanation == ""


# --- RetrievalResult ---


class TestRetrievalResult:
    def test_construction(self) -> None:
        result = RetrievalResult(nodes=[], query="test query")
        assert result.nodes == []
        assert result.query == "test query"
        assert result.hints is None

    def test_with_hints(self) -> None:
        hints = DomainHints(domain="scaleup")
        result = RetrievalResult(nodes=[], query="test", hints=hints)
        assert result.hints is not None
        assert result.hints.domain == "scaleup"


# --- DomainAdapter Protocol ---


class TestDomainAdapterProtocol:
    """Verify structural subtyping works — a class with the right methods satisfies the Protocol."""

    def test_structural_conformance(self) -> None:
        class FakeAdapter:
            def interpret_query(self, query: str) -> DomainHints:
                return DomainHints(domain="fake")

            def advise_traversal(
                self, hints: DomainHints, available_types: frozenset[str]
            ) -> TraversalAdvice:
                return TraversalAdvice()

            def annotate_results(
                self, nodes: list[GraphNode], hints: DomainHints
            ) -> list[ScoredNode]:
                return []

        adapter: DomainAdapter = FakeAdapter()  # type: ignore[assignment]
        # If this line doesn't raise, structural subtyping works
        assert adapter.interpret_query("test").domain == "fake"
