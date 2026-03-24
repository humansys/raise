"""Tests for scoring functions and retrieve() orchestrator."""

from __future__ import annotations

from typing import Any

import pytest

from rai_agent.knowledge.retrieval.engine import (
    W_ATTR,
    W_DOMAIN,
    W_SA,
    attribute_match,
    composite_score,
    retrieve,
    spreading_activation,
)
from rai_agent.knowledge.retrieval.models import (
    DomainHints,
    ScoredNode,
    TraversalAdvice,
)
from raise_core.graph.engine import Graph
from raise_core.graph.models import GraphEdge, GraphNode

# --- Fixtures ---


def _make_node(node_id: str, content: str = "test", **kwargs: Any) -> GraphNode:
    return GraphNode(id=node_id, content=content, created="2026-01-01", **kwargs)


def _build_chain_graph() -> Graph:
    """A → B → C chain with typed edges."""
    g = Graph()
    g.add_concept(_make_node("A", "node A"))
    g.add_concept(_make_node("B", "node B"))
    g.add_concept(_make_node("C", "node C"))
    g.add_relationship(GraphEdge(source="A", target="B", type="requires", weight=1.0))
    g.add_relationship(GraphEdge(source="B", target="C", type="feeds_into", weight=1.0))
    return g


# --- Spreading Activation ---


class TestSpreadingActivation:
    def test_seed_gets_initial_activation(self) -> None:
        g = _build_chain_graph()
        scores = spreading_activation(g, seed_ids=["A"])
        assert scores["A"] == pytest.approx(1.0)

    def test_decay_over_hops(self) -> None:
        g = _build_chain_graph()
        scores = spreading_activation(g, seed_ids=["A"], decay=0.5, max_depth=2)
        # A=1.0, B=0.5 (1 hop * 0.5), C=0.25 (2 hops * 0.5^2)
        assert scores["B"] == pytest.approx(0.5)
        assert scores["C"] == pytest.approx(0.25)

    def test_edge_weights_affect_propagation(self) -> None:
        g = _build_chain_graph()
        edge_weights = {"requires": 0.9, "feeds_into": 0.5}
        scores = spreading_activation(
            g, seed_ids=["A"], decay=1.0, max_depth=2, edge_weights=edge_weights
        )
        # A=1.0, B = 1.0 * 0.9 = 0.9, C = 0.9 * 0.5 = 0.45
        assert scores["B"] == pytest.approx(0.9)
        assert scores["C"] == pytest.approx(0.45)

    def test_empty_graph_returns_empty(self) -> None:
        g = Graph()
        scores = spreading_activation(g, seed_ids=["X"])
        assert scores == {}

    def test_multiple_seeds(self) -> None:
        g = _build_chain_graph()
        scores = spreading_activation(g, seed_ids=["A", "C"], decay=0.5, max_depth=1)
        assert scores["A"] == pytest.approx(1.0)
        assert scores["C"] == pytest.approx(1.0)
        # B reachable from both A and C at 1 hop
        assert scores["B"] == pytest.approx(0.5)  # max of the two paths


# --- Attribute Match ---


class TestAttributeMatch:
    def test_full_match(self) -> None:
        node = _make_node("n1", "cash flow tools for startups")
        score = attribute_match(node, keywords=["cash", "flow", "tools"])
        assert score == pytest.approx(1.0)

    def test_partial_match(self) -> None:
        node = _make_node("n1", "cash flow analysis")
        score = attribute_match(node, keywords=["cash", "tools"])
        assert score == pytest.approx(0.5)

    def test_no_match(self) -> None:
        node = _make_node("n1", "people management")
        score = attribute_match(node, keywords=["cash", "flow"])
        assert score == pytest.approx(0.0)

    def test_empty_keywords(self) -> None:
        node = _make_node("n1", "anything")
        score = attribute_match(node, keywords=[])
        assert score == pytest.approx(0.0)


# --- Composite Score ---


class TestCompositeScore:
    def test_weighted_sum(self) -> None:
        result = composite_score(sa=1.0, attr=1.0, domain=1.0)
        assert result == pytest.approx(W_SA + W_ATTR + W_DOMAIN)
        assert result == pytest.approx(1.0)

    def test_partial_scores(self) -> None:
        result = composite_score(sa=0.8, attr=0.6, domain=0.4)
        expected = W_SA * 0.8 + W_ATTR * 0.6 + W_DOMAIN * 0.4
        assert result == pytest.approx(expected)

    def test_zero_scores(self) -> None:
        assert composite_score(sa=0.0, attr=0.0, domain=0.0) == pytest.approx(0.0)


# --- retrieve() orchestrator ---


class _FakeAdapter:
    """Minimal adapter for testing the retrieve flow."""

    def __init__(
        self,
        hints: DomainHints | None = None,
        advice: TraversalAdvice | None = None,
        fail_interpret: bool = False,
        fail_advise: bool = False,
        fail_annotate: bool = False,
    ) -> None:
        self._hints = hints or DomainHints(domain="test")
        self._advice = advice or TraversalAdvice()
        self._fail_interpret = fail_interpret
        self._fail_advise = fail_advise
        self._fail_annotate = fail_annotate
        self.interpret_called = False
        self.advise_called = False
        self.annotate_called = False

    def interpret_query(self, query: str) -> DomainHints:
        self.interpret_called = True
        if self._fail_interpret:
            raise ValueError("interpret failed")
        return self._hints

    def advise_traversal(
        self, hints: DomainHints, available_types: frozenset[str]
    ) -> TraversalAdvice:
        self.advise_called = True
        if self._fail_advise:
            raise ValueError("advise failed")
        return self._advice

    def annotate_results(
        self, nodes: list[GraphNode], hints: DomainHints
    ) -> list[ScoredNode]:
        self.annotate_called = True
        if self._fail_annotate:
            raise ValueError("annotate failed")
        return [
            ScoredNode(node=n, score=0.7, explanation="fake annotation")
            for n in nodes
        ]


class TestRetrieve:
    def test_three_step_flow(self) -> None:
        g = _build_chain_graph()
        adapter = _FakeAdapter(
            advice=TraversalAdvice(start_node_ids=["A"], max_depth=2),
        )
        result = retrieve(g, "test query", adapter)
        assert adapter.interpret_called
        assert adapter.advise_called
        assert adapter.annotate_called
        assert len(result.nodes) > 0

    def test_empty_graph_returns_empty(self) -> None:
        g = Graph()
        adapter = _FakeAdapter(
            advice=TraversalAdvice(start_node_ids=["X"]),
        )
        result = retrieve(g, "test", adapter)
        assert result.nodes == []

    def test_top_k_limiting(self) -> None:
        g = _build_chain_graph()
        adapter = _FakeAdapter(
            advice=TraversalAdvice(start_node_ids=["A"], max_depth=2),
        )
        result = retrieve(g, "test", adapter, top_k=1)
        assert len(result.nodes) <= 1

    def test_fallback_on_interpret_failure(self) -> None:
        g = _build_chain_graph()
        adapter = _FakeAdapter(
            fail_interpret=True,
            advice=TraversalAdvice(start_node_ids=["A"], max_depth=1),
        )
        result = retrieve(g, "test", adapter)
        # Should not raise, should use fallback hints
        assert result.hints is not None
        assert result.hints.domain == "unknown"

    def test_fallback_on_advise_failure(self) -> None:
        g = _build_chain_graph()
        adapter = _FakeAdapter(fail_advise=True)
        result = retrieve(g, "node A", adapter)
        # Should fall back to keyword search — "node A" matches node A's content
        assert len(result.nodes) > 0
        node_ids = [n.node.id for n in result.nodes]
        assert "A" in node_ids

    def test_fallback_on_annotate_failure(self) -> None:
        g = _build_chain_graph()
        adapter = _FakeAdapter(
            advice=TraversalAdvice(start_node_ids=["A"], max_depth=1),
            fail_annotate=True,
        )
        result = retrieve(g, "test", adapter)
        # Should return nodes with score=0.0
        assert all(n.score >= 0.0 for n in result.nodes)

    def test_results_sorted_descending(self) -> None:
        g = _build_chain_graph()
        adapter = _FakeAdapter(
            advice=TraversalAdvice(start_node_ids=["A"], max_depth=2),
        )
        result = retrieve(g, "test", adapter)
        scores = [n.score for n in result.nodes]
        assert scores == sorted(scores, reverse=True)

    def test_query_preserved_in_result(self) -> None:
        g = Graph()
        adapter = _FakeAdapter()
        result = retrieve(g, "my specific query", adapter)
        assert result.query == "my specific query"
