"""Tests for Query model subtypes filter."""

from __future__ import annotations

from raise_core.graph.engine import Graph
from raise_core.graph.models import GraphEdge, GraphNode
from raise_core.graph.query import Query, QueryEngine, QueryStrategy


def _make_graph_with_patterns() -> Graph:
    """Create a graph with patterns of various subtypes."""
    g = Graph()
    g.add_concept(
        GraphNode(
            id="PAT-001",
            type="pattern",
            content="Use dependency injection for testability",
            created="2026-01-01",
            metadata={"sub_type": "approach"},
        )
    )
    g.add_concept(
        GraphNode(
            id="PAT-002",
            type="pattern",
            content="Avoid circular imports risk in large modules",
            created="2026-01-01",
            metadata={"sub_type": "risk"},
        )
    )
    g.add_concept(
        GraphNode(
            id="PAT-003",
            type="pattern",
            content="Singleton pattern for configuration",
            created="2026-01-01",
            metadata={"sub_type": "codebase"},
        )
    )
    g.add_concept(
        GraphNode(
            id="PAT-004",
            type="pattern",
            content="TDD process for testability",
            created="2026-01-01",
            metadata={"sub_type": "process"},
        )
    )
    g.add_concept(
        GraphNode(
            id="MOD-001",
            type="module",
            content="Memory module for pattern storage",
            created="2026-01-01",
            metadata={},
        )
    )
    return g


class TestQuerySubtypesField:
    """Tests for the subtypes field on Query model."""

    def test_subtypes_defaults_to_none(self) -> None:
        """Subtypes defaults to None when not specified."""
        q = Query(query="test")
        assert q.subtypes is None

    def test_subtypes_accepts_list(self) -> None:
        """Subtypes accepts a list of strings."""
        q = Query(query="test", subtypes=["approach", "risk"])
        assert q.subtypes == ["approach", "risk"]


class TestKeywordSearchSubtypesFilter:
    """Tests for subtypes filter in keyword_search strategy."""

    def test_no_subtypes_returns_all_matching(self) -> None:
        """Without subtypes filter, all matching patterns are returned."""
        engine = QueryEngine(_make_graph_with_patterns())
        result = engine.query(Query(query="testability", types=["pattern"]))
        assert len(result.concepts) == 2  # PAT-001 (approach) and PAT-004 (process)

    def test_subtypes_filters_to_approach(self) -> None:
        """Subtypes filter restricts to approach patterns only."""
        engine = QueryEngine(_make_graph_with_patterns())
        result = engine.query(
            Query(query="testability", types=["pattern"], subtypes=["approach"])
        )
        assert len(result.concepts) == 1
        assert result.concepts[0].id == "PAT-001"

    def test_subtypes_filters_to_risk(self) -> None:
        """Subtypes filter restricts to risk patterns only."""
        engine = QueryEngine(_make_graph_with_patterns())
        result = engine.query(
            Query(query="risk", types=["pattern"], subtypes=["risk"])
        )
        assert len(result.concepts) == 1
        assert result.concepts[0].id == "PAT-002"

    def test_subtypes_multiple_values(self) -> None:
        """Subtypes filter with multiple values includes both."""
        engine = QueryEngine(_make_graph_with_patterns())
        result = engine.query(
            Query(query="pattern", types=["pattern"], subtypes=["approach", "risk"])
        )
        ids = {c.id for c in result.concepts}
        assert "PAT-001" in ids
        assert "PAT-002" in ids
        assert "PAT-003" not in ids

    def test_subtypes_without_type_filter(self) -> None:
        """Subtypes filter works without type filter, skips non-pattern nodes."""
        engine = QueryEngine(_make_graph_with_patterns())
        result = engine.query(
            Query(query="pattern", subtypes=["codebase"])
        )
        # PAT-003 has sub_type=codebase; MOD-001 has no sub_type so excluded
        ids = {c.id for c in result.concepts}
        assert "PAT-003" in ids
        assert "MOD-001" not in ids

    def test_subtypes_no_matches(self) -> None:
        """Subtypes filter with no matching patterns returns empty."""
        engine = QueryEngine(_make_graph_with_patterns())
        result = engine.query(
            Query(query="testability", subtypes=["nonexistent"])
        )
        assert len(result.concepts) == 0


class TestConceptLookupSubtypesFilter:
    """Tests for subtypes filter in concept_lookup strategy."""

    def test_concept_lookup_respects_subtypes(self) -> None:
        """Concept lookup filters main concept by subtype."""
        engine = QueryEngine(_make_graph_with_patterns())
        # PAT-001 has sub_type=approach, looking for risk should exclude it
        result = engine.query(
            Query(
                query="PAT-001",
                strategy=QueryStrategy.CONCEPT_LOOKUP,
                subtypes=["risk"],
            )
        )
        assert len(result.concepts) == 0

    def test_concept_lookup_includes_matching_subtype(self) -> None:
        """Concept lookup includes concept when subtype matches."""
        engine = QueryEngine(_make_graph_with_patterns())
        result = engine.query(
            Query(
                query="PAT-001",
                strategy=QueryStrategy.CONCEPT_LOOKUP,
                subtypes=["approach"],
            )
        )
        assert len(result.concepts) == 1
        assert result.concepts[0].id == "PAT-001"

    def test_concept_lookup_filters_neighbors_by_subtype(self) -> None:
        """Concept lookup with depth > 0 filters neighbors by subtype (QR-R3)."""
        g = _make_graph_with_patterns()
        # PAT-001 (approach) -> PAT-002 (risk) and PAT-003 (codebase)
        g.add_relationship(
            GraphEdge(source="PAT-001", target="PAT-002", type="related_to")
        )
        g.add_relationship(
            GraphEdge(source="PAT-001", target="PAT-003", type="related_to")
        )
        engine = QueryEngine(g)
        # Lookup PAT-001 with depth=1, filter to approach+risk only
        result = engine.query(
            Query(
                query="PAT-001",
                strategy=QueryStrategy.CONCEPT_LOOKUP,
                max_depth=1,
                subtypes=["approach", "risk"],
            )
        )
        ids = {c.id for c in result.concepts}
        assert "PAT-001" in ids  # approach — matches
        assert "PAT-002" in ids  # risk — matches
        assert "PAT-003" not in ids  # codebase — filtered out
