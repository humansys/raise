"""Tests for unified context query module."""

from __future__ import annotations

from pathlib import Path

import pytest

from raise_core.graph.backends.filesystem import FilesystemGraphBackend
from raise_core.graph.engine import Graph
from raise_core.graph.models import GraphEdge, GraphNode
from raise_core.graph.query import (
    Query,
    QueryEngine,
    QueryMetadata,
    QueryResult,
    QueryStrategy,
    calculate_relevance_score,
    wilson_lower_bound,
)

# --- Fixtures ---


@pytest.fixture
def sample_graph() -> Graph:
    """Create a sample graph for testing."""
    graph = Graph()

    # Add pattern nodes
    graph.add_concept(
        GraphNode(
            id="PAT-001",
            type="pattern",
            content="Apply 0.5x multiplier to estimates when using full kata cycle",
            source_file=".raise/rai/memory/patterns.jsonl",
            created="2026-02-01",
            metadata={"sub_type": "process"},
        )
    )
    graph.add_concept(
        GraphNode(
            id="PAT-002",
            type="pattern",
            content="Use singleton pattern with get/set/configure methods",
            source_file=".raise/rai/memory/patterns.jsonl",
            created="2026-01-15",
            metadata={"sub_type": "codebase"},
        )
    )

    # Add calibration nodes
    graph.add_concept(
        GraphNode(
            id="CAL-001",
            type="calibration",
            content="F2.1 Concept Extraction: Size S, Est 180m, Actual 52m, Velocity 3.5x",
            source_file=".raise/rai/memory/calibration.jsonl",
            created="2026-01-31",
            metadata={"story": "F2.1", "velocity": 3.5},
        )
    )

    # Add skill nodes
    graph.add_concept(
        GraphNode(
            id="/story-plan",
            type="skill",
            content="Decompose user stories into atomic executable tasks",
            source_file=".claude/skills/story-plan/SKILL.md",
            created="2026-01-30",
            metadata={"needs_context": ["pattern", "calibration"]},
        )
    )

    # Add session node
    graph.add_concept(
        GraphNode(
            id="SES-001",
            type="session",
            content="E3 Implementation Plan session with epic-plan skill",
            source_file=".raise/rai/memory/sessions/index.jsonl",
            created="2026-02-01",
        )
    )

    return graph


@pytest.fixture
def engine(sample_graph: Graph) -> QueryEngine:
    """Create query engine with sample graph."""
    return QueryEngine(sample_graph)


# --- Model Tests ---


class TestQuery:
    """Tests for Query model."""

    def test_default_strategy(self) -> None:
        """Default strategy is keyword_search."""
        query = Query(query="planning")
        assert query.strategy == QueryStrategy.KEYWORD_SEARCH

    def test_default_max_depth(self) -> None:
        """Default max_depth is 1."""
        query = Query(query="planning")
        assert query.max_depth == 1

    def test_types_filter(self) -> None:
        """Types filter is optional list."""
        query = Query(query="planning", types=["pattern", "calibration"])
        assert query.types == ["pattern", "calibration"]

    def test_max_depth_validation(self) -> None:
        """Max depth must be between 0 and 5."""
        with pytest.raises(ValueError):
            Query(query="test", max_depth=6)

    def test_limit_default(self) -> None:
        """Default limit is 10."""
        query = Query(query="test")
        assert query.limit == 10


class TestQueryMetadata:
    """Tests for QueryMetadata model."""

    def test_types_found_dict(self) -> None:
        """Types found is a dict of type -> count."""
        metadata = QueryMetadata(
            query="test",
            strategy=QueryStrategy.KEYWORD_SEARCH,
            total_concepts=5,
            token_estimate=320,
            execution_time_ms=8.5,
            types_found={"pattern": 2, "calibration": 2, "skill": 1},
        )
        assert metadata.types_found["pattern"] == 2


class TestQueryResult:
    """Tests for QueryResult model."""

    def test_to_json(self, sample_graph: Graph) -> None:
        """Result can be serialized to JSON."""
        concept = sample_graph.get_concept("PAT-001")
        assert concept is not None

        result = QueryResult(
            concepts=[concept],
            metadata=QueryMetadata(
                query="test",
                strategy=QueryStrategy.KEYWORD_SEARCH,
                total_concepts=1,
                token_estimate=50,
                execution_time_ms=5.0,
                types_found={"pattern": 1},
            ),
        )
        json_str = result.to_json()
        assert "PAT-001" in json_str
        assert "pattern" in json_str


# --- Engine Tests ---


class TestQueryEngineKeywordSearch:
    """Tests for keyword search strategy."""

    def test_single_keyword_match(self, engine: QueryEngine) -> None:
        """Single keyword matches content."""
        result = engine.query(Query(query="multiplier"))
        assert len(result.concepts) >= 1
        assert any(c.id == "PAT-001" for c in result.concepts)

    def test_multiple_keywords_match(self, engine: QueryEngine) -> None:
        """Multiple keywords all match."""
        result = engine.query(Query(query="kata cycle"))
        assert len(result.concepts) >= 1
        assert any(c.id == "PAT-001" for c in result.concepts)

    def test_case_insensitive(self, engine: QueryEngine) -> None:
        """Search is case-insensitive."""
        result = engine.query(Query(query="MULTIPLIER"))
        assert len(result.concepts) >= 1
        assert any(c.id == "PAT-001" for c in result.concepts)

    def test_no_match_returns_empty(self, engine: QueryEngine) -> None:
        """No matches returns empty list."""
        result = engine.query(Query(query="xyznonexistent"))
        assert len(result.concepts) == 0

    def test_type_filter(self, engine: QueryEngine) -> None:
        """Type filter limits results."""
        result = engine.query(Query(query="pattern", types=["calibration"]))
        # Should only return calibration nodes, not pattern nodes
        for concept in result.concepts:
            assert concept.type == "calibration"

    def test_limit_results(self, engine: QueryEngine) -> None:
        """Limit caps result count."""
        result = engine.query(Query(query="a", limit=2))
        assert len(result.concepts) <= 2

    def test_type_keyword_matches_node_type(self) -> None:
        """Keyword matching includes node_type so --types + type keyword works (RAISE-310)."""
        graph = Graph()
        graph.add_concept(
            GraphNode(
                id="REQ-001",
                type="requirement",
                content="The system shall support SSO authentication",
                source_file="test",
                created="2026-03-01",
            )
        )
        engine = QueryEngine(graph)
        result = engine.query(Query(query="requirement", types=["requirement"]))
        assert len(result.concepts) == 1
        assert result.concepts[0].id == "REQ-001"

    def test_relevance_scoring(self, engine: QueryEngine) -> None:
        """More keyword hits rank higher."""
        result = engine.query(Query(query="kata cycle multiplier"))
        if len(result.concepts) > 0:
            # PAT-001 has all three keywords, should be first
            assert result.concepts[0].id == "PAT-001"


class TestQueryEngineConceptLookup:
    """Tests for concept lookup strategy."""

    def test_direct_lookup(self, engine: QueryEngine) -> None:
        """Direct ID lookup returns concept."""
        result = engine.query(
            Query(
                query="PAT-001",
                strategy=QueryStrategy.CONCEPT_LOOKUP,
            )
        )
        assert len(result.concepts) >= 1
        assert any(c.id == "PAT-001" for c in result.concepts)

    def test_lookup_not_found(self, engine: QueryEngine) -> None:
        """Non-existent ID returns empty."""
        result = engine.query(
            Query(
                query="NONEXISTENT-999",
                strategy=QueryStrategy.CONCEPT_LOOKUP,
            )
        )
        assert len(result.concepts) == 0

    def test_lookup_with_neighbors(self, sample_graph: Graph) -> None:
        """Lookup with depth > 0 includes neighbors."""
        # Add relationship
        sample_graph.add_relationship(
            GraphEdge(
                source="PAT-001",
                target="SES-001",
                type="learned_from",
            )
        )

        engine = QueryEngine(sample_graph)
        result = engine.query(
            Query(
                query="PAT-001",
                strategy=QueryStrategy.CONCEPT_LOOKUP,
                max_depth=1,
            )
        )
        # Should include PAT-001 and its neighbor SES-001
        ids = [c.id for c in result.concepts]
        assert "PAT-001" in ids
        assert "SES-001" in ids

    def test_concept_lookup_does_not_fallback_to_keyword(
        self, engine: QueryEngine
    ) -> None:
        """concept_lookup with non-existent ID returns empty, no fallback."""
        result = engine.query(
            Query(
                query="singleton",  # exists as keyword but not as ID
                strategy=QueryStrategy.CONCEPT_LOOKUP,
            )
        )
        # Must return empty — no silent fallback to keyword_search
        assert len(result.concepts) == 0
        assert result.metadata.strategy == QueryStrategy.CONCEPT_LOOKUP


class TestQueryEngineEdgeTypeFilter:
    """Tests for edge-type filtering in concept lookup."""

    def test_edge_types_field_default_none(self) -> None:
        """edge_types defaults to None."""
        query = Query(query="test")
        assert query.edge_types is None

    def test_edge_types_field_accepts_list(self) -> None:
        """edge_types accepts a list of EdgeType values."""
        query = Query(
            query="test",
            edge_types=["constrained_by", "depends_on"],
        )
        assert query.edge_types == ["constrained_by", "depends_on"]

    def test_concept_lookup_with_edge_type_filter(self, sample_graph: Graph) -> None:
        """Concept lookup with edge_types only returns neighbors via matching edges."""
        # Add two different edge types from PAT-001
        sample_graph.add_relationship(
            GraphEdge(source="PAT-001", target="SES-001", type="learned_from")
        )
        sample_graph.add_relationship(
            GraphEdge(source="PAT-001", target="/story-plan", type="applies_to")
        )

        engine = QueryEngine(sample_graph)

        # Filter to learned_from only
        result = engine.query(
            Query(
                query="PAT-001",
                strategy=QueryStrategy.CONCEPT_LOOKUP,
                max_depth=1,
                edge_types=["learned_from"],
            )
        )
        ids = {c.id for c in result.concepts}
        assert "PAT-001" in ids  # root node always included
        assert "SES-001" in ids  # connected via learned_from
        assert "/story-plan" not in ids  # connected via applies_to, filtered out

    def test_concept_lookup_with_multiple_edge_types(self, sample_graph: Graph) -> None:
        """Multiple edge types returns neighbors matching any of them."""
        sample_graph.add_relationship(
            GraphEdge(source="PAT-001", target="SES-001", type="learned_from")
        )
        sample_graph.add_relationship(
            GraphEdge(source="PAT-001", target="/story-plan", type="applies_to")
        )

        engine = QueryEngine(sample_graph)

        result = engine.query(
            Query(
                query="PAT-001",
                strategy=QueryStrategy.CONCEPT_LOOKUP,
                max_depth=1,
                edge_types=["learned_from", "applies_to"],
            )
        )
        ids = {c.id for c in result.concepts}
        assert "SES-001" in ids
        assert "/story-plan" in ids

    def test_concept_lookup_without_edge_types_returns_all(
        self, sample_graph: Graph
    ) -> None:
        """No edge_types filter returns all neighbors (backward compat)."""
        sample_graph.add_relationship(
            GraphEdge(source="PAT-001", target="SES-001", type="learned_from")
        )
        sample_graph.add_relationship(
            GraphEdge(source="PAT-001", target="/story-plan", type="applies_to")
        )

        engine = QueryEngine(sample_graph)

        result = engine.query(
            Query(
                query="PAT-001",
                strategy=QueryStrategy.CONCEPT_LOOKUP,
                max_depth=1,
                edge_types=None,
            )
        )
        ids = {c.id for c in result.concepts}
        assert "SES-001" in ids
        assert "/story-plan" in ids


class TestQueryEngineMetadata:
    """Tests for query metadata."""

    def test_token_estimate(self, engine: QueryEngine) -> None:
        """Token estimate is calculated."""
        result = engine.query(Query(query="multiplier"))
        assert result.metadata.token_estimate > 0

    def test_execution_time(self, engine: QueryEngine) -> None:
        """Execution time is recorded."""
        result = engine.query(Query(query="multiplier"))
        assert result.metadata.execution_time_ms >= 0

    def test_types_found(self, engine: QueryEngine) -> None:
        """Types found is populated."""
        result = engine.query(Query(query="pattern singleton"))
        if len(result.concepts) > 0:
            assert len(result.metadata.types_found) > 0

    def test_total_available_equals_total_when_no_truncation(
        self, engine: QueryEngine
    ) -> None:
        """total_available equals total_concepts when results fit within limit."""
        result = engine.query(Query(query="multiplier", limit=50))
        assert result.metadata.total_available == result.metadata.total_concepts

    def test_total_available_exceeds_total_when_truncated(
        self, sample_graph: Graph
    ) -> None:
        """total_available > total_concepts when limit truncates results."""
        # Add extra nodes that share a keyword to guarantee truncation
        sample_graph.add_concept(
            GraphNode(
                id="PAT-EXTRA-1",
                type="pattern",
                content="velocity tracking for estimation",
                source_file="test",
                created="2026-02-01",
            )
        )
        sample_graph.add_concept(
            GraphNode(
                id="PAT-EXTRA-2",
                type="pattern",
                content="velocity calibration method",
                source_file="test",
                created="2026-02-01",
            )
        )
        eng = QueryEngine(sample_graph)
        result = eng.query(Query(query="velocity", limit=1))
        assert result.metadata.total_concepts == 1
        assert result.metadata.total_available >= 2


class TestWilsonLowerBound:
    """Tests for wilson_lower_bound helper."""

    def test_all_positive_high_score(self) -> None:
        """All positive evaluations gives high Wilson score."""
        score = wilson_lower_bound(10, 0)
        assert score > 0.7

    def test_all_negative_low_score(self) -> None:
        """All negative evaluations gives low Wilson score."""
        score = wilson_lower_bound(0, 10)
        assert score < 0.1

    def test_majority_negative_approx(self) -> None:
        """3 pos / 7 neg (design example) gives ~0.10."""
        score = wilson_lower_bound(3, 7)
        assert 0.05 < score < 0.20

    def test_zero_total_raises(self) -> None:
        """Zero total observations raises ValueError."""
        with pytest.raises(ValueError):
            wilson_lower_bound(0, 0)

    def test_single_positive_is_conservative(self) -> None:
        """Single positive is conservative — Wilson lower bound < 0.9."""
        score = wilson_lower_bound(1, 0)
        assert 0 < score < 0.9


class TestCalculateRelevanceScore:
    """Tests for composite relevance scoring (RAISE-170)."""

    def test_foundational_true_exempt_from_decay(self) -> None:
        """foundational=True patterns skip decay — score = keyword_relevance only."""
        score = calculate_relevance_score(
            content="planning estimation calibration",
            keywords=["planning", "estimation"],
            created="2025-01-01",  # ~400 days old, would decay heavily
            metadata={"foundational": True},
        )
        assert score == pytest.approx(1.0, abs=0.01)

    def test_base_true_also_exempt(self) -> None:
        """base=True (writer.py legacy key) also skips decay."""
        score = calculate_relevance_score(
            content="planning estimation calibration",
            keywords=["planning", "estimation"],
            created="2025-01-01",
            metadata={"base": True},
        )
        assert score == pytest.approx(1.0, abs=0.01)

    def test_zero_evaluations_modifier_is_neutral(self) -> None:
        """evaluations=0 → modifier=1.0, no penalty for un-evaluated patterns."""
        from datetime import date

        score = calculate_relevance_score(
            content="planning",
            keywords=["planning"],
            created=date.today().isoformat(),
            metadata={"evaluations": 0},
        )
        # brand new pattern: recency=1.0, relevance=1.0, modifier=1.0
        # base = 0.3*1.0 + 0.7*1.0 = 1.0
        assert score == pytest.approx(1.0, abs=0.01)

    def test_thirty_day_half_life_decay(self) -> None:
        """Pattern at exactly 30d has recency=0.5 (half-life)."""
        from datetime import date, timedelta

        created = (date.today() - timedelta(days=30)).isoformat()
        score = calculate_relevance_score(
            content="planning",
            keywords=["planning"],
            created=created,
            metadata={},
        )
        # recency=0.5, relevance=1.0, modifier=1.0
        # base = 0.3*0.5 + 0.7*1.0 = 0.85
        assert score == pytest.approx(0.85, abs=0.02)

    def test_high_negatives_reduces_score(self) -> None:
        """Wilson modifier significantly reduces score for mostly-negative patterns."""
        from datetime import date

        today = date.today().isoformat()
        score_negative = calculate_relevance_score(
            content="planning",
            keywords=["planning"],
            created=today,
            metadata={"positives": 3, "negatives": 7, "evaluations": 10},
        )
        score_neutral = calculate_relevance_score(
            content="planning",
            keywords=["planning"],
            created=today,
            metadata={"evaluations": 0},
        )
        assert score_negative < score_neutral * 0.5

    def test_no_keyword_hits_pure_recency(self) -> None:
        """No keyword hits → score = w_recency * recency (today = 0.3)."""
        from datetime import date

        score = calculate_relevance_score(
            content="totally unrelated content here",
            keywords=["planning", "estimation"],
            created=date.today().isoformat(),
            metadata={},
        )
        # relevance=0.0, recency=1.0 → base = 0.3*1.0 + 0.7*0.0 = 0.3
        assert score == pytest.approx(0.3, abs=0.05)

    def test_empty_keywords_no_crash(self) -> None:
        """Empty keywords list returns a float without crashing."""
        from datetime import date

        score = calculate_relevance_score(
            content="anything",
            keywords=[],
            created=date.today().isoformat(),
            metadata={},
        )
        assert isinstance(score, float)

    def test_invalid_date_defaults_gracefully(self) -> None:
        """Invalid date string does not crash — defaults to age=0."""
        score = calculate_relevance_score(
            content="planning",
            keywords=["planning"],
            created="not-a-date",
            metadata={},
        )
        assert isinstance(score, float)

    def test_none_metadata_treated_as_empty(self) -> None:
        """None metadata is handled safely."""
        from datetime import date

        score = calculate_relevance_score(
            content="planning",
            keywords=["planning"],
            created=date.today().isoformat(),
            metadata=None,
        )
        assert isinstance(score, float)


class TestKeywordSearchOrdering:
    """Integration tests: query results ordered by composite score (RAISE-170)."""

    def test_foundational_beats_heavily_decayed(self) -> None:
        """Foundational pattern outscores a heavily decayed pattern with same keywords."""
        graph = Graph()
        graph.add_concept(
            GraphNode(
                id="PAT-DECAYED",
                type="pattern",
                content="planning estimation velocity",
                source_file="test",
                created="2025-01-01",
                metadata={},
            )
        )
        graph.add_concept(
            GraphNode(
                id="PAT-FOUND",
                type="pattern",
                content="planning estimation velocity",
                source_file="test",
                created="2025-01-01",
                metadata={"foundational": True},
            )
        )
        engine = QueryEngine(graph)
        result = engine.query(Query(query="planning estimation velocity"))
        ids = [c.id for c in result.concepts]
        assert ids.index("PAT-FOUND") < ids.index("PAT-DECAYED")

    def test_newer_beats_older_same_keywords(self) -> None:
        """Newer pattern outscores older one on same keywords (decay effect)."""
        from datetime import date, timedelta

        today = date.today()
        graph = Graph()
        graph.add_concept(
            GraphNode(
                id="PAT-NEW",
                type="pattern",
                content="planning estimation",
                source_file="test",
                created=today.isoformat(),
                metadata={},
            )
        )
        graph.add_concept(
            GraphNode(
                id="PAT-OLD",
                type="pattern",
                content="planning estimation",
                source_file="test",
                created=(today - timedelta(days=90)).isoformat(),
                metadata={},
            )
        )
        engine = QueryEngine(graph)
        result = engine.query(Query(query="planning estimation"))
        ids = [c.id for c in result.concepts]
        assert ids.index("PAT-NEW") < ids.index("PAT-OLD")


class TestQueryEngineFromFile:
    """Tests for loading engine from persisted file."""

    def test_load_from_file(self, sample_graph: Graph, tmp_path: Path) -> None:
        """Engine can be created from a persisted graph file."""
        graph_path = tmp_path / "unified.json"
        backend = FilesystemGraphBackend(graph_path)
        backend.persist(sample_graph)

        loaded_graph = backend.load()
        engine = QueryEngine(loaded_graph)
        assert engine.graph.node_count == sample_graph.node_count

    def test_load_not_found(self, tmp_path: Path) -> None:
        """FileNotFoundError if file doesn't exist."""
        backend = FilesystemGraphBackend(tmp_path / "nonexistent.json")
        with pytest.raises(FileNotFoundError):
            backend.load()
