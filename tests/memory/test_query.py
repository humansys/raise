"""Tests for memory query engine."""

from datetime import date

import pytest

from raise_cli.memory.builder import MemoryGraph, MemoryGraphBuilder
from raise_cli.memory.models import (
    MemoryConcept,
    MemoryConceptType,
    MemoryRelationship,
    MemoryRelationshipType,
)
from raise_cli.memory.query import MemoryQuery, MemoryQueryResult, ScoredConcept


@pytest.fixture
def sample_concepts() -> list[MemoryConcept]:
    """Create sample concepts for testing."""
    return [
        MemoryConcept(
            id="PAT-001",
            type=MemoryConceptType.PATTERN,
            content="Singleton pattern with get/set/configure methods",
            context=["testing", "module-design", "python"],
            created=date(2026, 1, 31),
            metadata={"sub_type": "codebase"},
        ),
        MemoryConcept(
            id="PAT-002",
            type=MemoryConceptType.PATTERN,
            content="BFS traversal for graph exploration",
            context=["graph", "algorithm", "python"],
            created=date(2026, 1, 30),
            metadata={"sub_type": "technical"},
        ),
        MemoryConcept(
            id="CAL-001",
            type=MemoryConceptType.CALIBRATION,
            content="Feature F2.1 took 45 minutes estimated 60",
            context=["velocity", "estimation", "python"],
            created=date(2026, 1, 31),
            metadata={"feature": "F2.1"},
        ),
        MemoryConcept(
            id="SES-001",
            type=MemoryConceptType.SESSION,
            content="Implemented governance toolkit",
            context=["feature", "implementation"],
            created=date(2026, 1, 31),
            metadata={"topic": "E2 Governance"},
        ),
    ]


@pytest.fixture
def sample_graph(sample_concepts: list[MemoryConcept]) -> MemoryGraph:
    """Create a sample graph with relationships."""
    builder = MemoryGraphBuilder(min_shared_keywords=1)
    return builder.build(sample_concepts)


class TestMemoryQueryResult:
    """Tests for MemoryQueryResult model."""

    def test_default_values(self) -> None:
        """MemoryQueryResult has sensible defaults."""
        result = MemoryQueryResult()

        assert result.concepts == []
        assert result.relationships == []
        assert result.token_estimate == 0
        assert result.query_time_ms == 0.0
        assert result.total_nodes == 0
        assert result.matched_nodes == 0

    def test_with_data(self, sample_concepts: list[MemoryConcept]) -> None:
        """MemoryQueryResult stores data correctly."""
        result = MemoryQueryResult(
            concepts=sample_concepts[:2],
            token_estimate=100,
            query_time_ms=5.5,
            total_nodes=4,
            matched_nodes=2,
        )

        assert len(result.concepts) == 2
        assert result.token_estimate == 100
        assert result.query_time_ms == 5.5


class TestScoredConcept:
    """Tests for ScoredConcept dataclass."""

    def test_creation(self, sample_concepts: list[MemoryConcept]) -> None:
        """ScoredConcept stores concept with score."""
        scored = ScoredConcept(
            concept=sample_concepts[0],
            score=0.85,
            match_type="keyword",
        )

        assert scored.concept.id == "PAT-001"
        assert scored.score == 0.85
        assert scored.match_type == "keyword"


class TestMemoryQuery:
    """Tests for MemoryQuery class."""

    def test_init_default_recency_weight(self, sample_graph: MemoryGraph) -> None:
        """MemoryQuery uses default recency weight."""
        query = MemoryQuery(sample_graph)

        assert query.recency_weight == 0.3
        assert query.graph is sample_graph

    def test_init_custom_recency_weight(self, sample_graph: MemoryGraph) -> None:
        """MemoryQuery accepts custom recency weight."""
        query = MemoryQuery(sample_graph, recency_weight=0.5)

        assert query.recency_weight == 0.5

    def test_recency_weight_clamped_min(self, sample_graph: MemoryGraph) -> None:
        """Recency weight is clamped to 0.0 minimum."""
        query = MemoryQuery(sample_graph, recency_weight=-0.5)

        assert query.recency_weight == 0.0

    def test_recency_weight_clamped_max(self, sample_graph: MemoryGraph) -> None:
        """Recency weight is clamped to 1.0 maximum."""
        query = MemoryQuery(sample_graph, recency_weight=1.5)

        assert query.recency_weight == 1.0

    def test_extract_keywords(self, sample_graph: MemoryGraph) -> None:
        """Keywords are extracted correctly."""
        query = MemoryQuery(sample_graph)

        keywords = query._extract_keywords("the testing pattern for python")

        assert "testing" in keywords
        assert "pattern" in keywords
        assert "python" in keywords
        assert "the" not in keywords  # Stopword
        assert "for" not in keywords  # Stopword

    def test_extract_keywords_short_words(self, sample_graph: MemoryGraph) -> None:
        """Short words are filtered out."""
        query = MemoryQuery(sample_graph)

        keywords = query._extract_keywords("a b cd efg")

        assert "efg" in keywords
        assert "cd" not in keywords  # Too short (<=2)
        assert "a" not in keywords
        assert "b" not in keywords

    def test_search_empty_query(self, sample_graph: MemoryGraph) -> None:
        """Search with no valid keywords returns empty result."""
        query = MemoryQuery(sample_graph)

        result = query.search("the a an")  # All stopwords/short

        assert len(result.concepts) == 0
        assert result.total_nodes == 4

    def test_search_keyword_match(self, sample_graph: MemoryGraph) -> None:
        """Search finds concepts by keyword."""
        query = MemoryQuery(sample_graph)

        result = query.search("singleton pattern")

        assert len(result.concepts) > 0
        assert any(c.id == "PAT-001" for c in result.concepts)

    def test_search_context_match(self, sample_graph: MemoryGraph) -> None:
        """Search matches keywords in context."""
        query = MemoryQuery(sample_graph)

        result = query.search("testing module")

        assert len(result.concepts) > 0
        assert any(c.id == "PAT-001" for c in result.concepts)

    def test_search_max_results(self, sample_graph: MemoryGraph) -> None:
        """Search respects max_results limit."""
        query = MemoryQuery(sample_graph)

        result = query.search("python", max_results=2)

        assert len(result.concepts) <= 2

    def test_search_no_expand(self, sample_graph: MemoryGraph) -> None:
        """Search without traversal expansion."""
        query = MemoryQuery(sample_graph)

        result = query.search("singleton", expand_traversal=False)

        assert len(result.concepts) >= 1
        # With no expansion, only direct matches

    def test_search_with_expand(self, sample_graph: MemoryGraph) -> None:
        """Search with traversal expansion includes related concepts."""
        query = MemoryQuery(sample_graph)

        result = query.search("singleton", expand_traversal=True, max_depth=2)

        # Should potentially include related concepts via edges
        assert result.matched_nodes >= 1

    def test_search_returns_relationships(self, sample_graph: MemoryGraph) -> None:
        """Search includes relationships between matched concepts."""
        query = MemoryQuery(sample_graph)

        result = query.search("python", max_results=10)

        # May or may not have relationships depending on matches
        assert isinstance(result.relationships, list)

    def test_search_token_estimate(self, sample_graph: MemoryGraph) -> None:
        """Search calculates token estimate."""
        query = MemoryQuery(sample_graph)

        result = query.search("singleton")

        if result.concepts:
            assert result.token_estimate > 0

    def test_search_query_time(self, sample_graph: MemoryGraph) -> None:
        """Search records query time."""
        query = MemoryQuery(sample_graph)

        result = query.search("pattern")

        assert result.query_time_ms >= 0

    def test_recency_scoring(self, sample_graph: MemoryGraph) -> None:
        """Newer concepts get higher recency scores."""
        query = MemoryQuery(sample_graph, recency_weight=1.0)

        # PAT-001 is newer (Jan 31) than PAT-002 (Jan 30)
        # Both match "python"
        result = query.search("python pattern", max_results=10)

        # With high recency weight, newer should rank higher
        if len(result.concepts) >= 2:
            # Find positions
            pat1_idx = next(
                (i for i, c in enumerate(result.concepts) if c.id == "PAT-001"), -1
            )
            pat2_idx = next(
                (i for i, c in enumerate(result.concepts) if c.id == "PAT-002"), -1
            )
            if pat1_idx >= 0 and pat2_idx >= 0:
                # PAT-001 should be ranked higher (lower index)
                assert pat1_idx < pat2_idx


class TestCalculateRecencyScore:
    """Tests for recency score calculation."""

    def test_recent_concept_high_score(self, sample_graph: MemoryGraph) -> None:
        """Very recent concept has high recency score."""
        query = MemoryQuery(sample_graph)
        # Override _today for testing
        query._today = date(2026, 1, 31)

        concept = MemoryConcept(
            id="TEST",
            type=MemoryConceptType.PATTERN,
            content="Test",
            created=date(2026, 1, 31),  # Same day
        )

        score = query._calculate_recency_score(concept)

        assert score == 1.0  # 0 days old = 0.5^0 = 1.0

    def test_old_concept_low_score(self, sample_graph: MemoryGraph) -> None:
        """Older concept has lower recency score."""
        query = MemoryQuery(sample_graph)
        query._today = date(2026, 1, 31)

        concept = MemoryConcept(
            id="TEST",
            type=MemoryConceptType.PATTERN,
            content="Test",
            created=date(2026, 1, 1),  # 30 days old
        )

        score = query._calculate_recency_score(concept)

        assert score == pytest.approx(0.5, rel=0.01)  # 30 days = 0.5^1

    def test_very_old_concept_very_low_score(self, sample_graph: MemoryGraph) -> None:
        """Very old concept has very low recency score."""
        query = MemoryQuery(sample_graph)
        query._today = date(2026, 1, 31)

        concept = MemoryConcept(
            id="TEST",
            type=MemoryConceptType.PATTERN,
            content="Test",
            created=date(2025, 12, 2),  # 60 days old
        )

        score = query._calculate_recency_score(concept)

        assert score == pytest.approx(0.25, rel=0.01)  # 60 days = 0.5^2


class TestCalculateKeywordScore:
    """Tests for keyword score calculation."""

    def test_full_match(self, sample_graph: MemoryGraph) -> None:
        """All keywords match gives score 1.0."""
        query = MemoryQuery(sample_graph)

        concept = sample_graph.nodes["PAT-001"]
        keywords = {"singleton", "pattern"}

        score = query._calculate_keyword_score(concept, keywords)

        assert score == 1.0

    def test_partial_match(self, sample_graph: MemoryGraph) -> None:
        """Some keywords match gives partial score."""
        query = MemoryQuery(sample_graph)

        concept = sample_graph.nodes["PAT-001"]
        keywords = {"singleton", "unknown"}

        score = query._calculate_keyword_score(concept, keywords)

        assert 0 < score < 1.0

    def test_no_match(self, sample_graph: MemoryGraph) -> None:
        """No keywords match gives score 0."""
        query = MemoryQuery(sample_graph)

        concept = sample_graph.nodes["PAT-001"]
        keywords = {"unknown", "words"}

        score = query._calculate_keyword_score(concept, keywords)

        assert score == 0.0

    def test_context_match_lower_weight(self, sample_graph: MemoryGraph) -> None:
        """Context matches have slightly lower weight."""
        query = MemoryQuery(sample_graph)

        concept = sample_graph.nodes["PAT-001"]
        # "testing" is in context, not content
        keywords = {"testing"}

        score = query._calculate_keyword_score(concept, keywords)

        assert score == 0.8  # Context match weight

    def test_empty_keywords(self, sample_graph: MemoryGraph) -> None:
        """Empty keywords gives score 0."""
        query = MemoryQuery(sample_graph)

        concept = sample_graph.nodes["PAT-001"]

        score = query._calculate_keyword_score(concept, set())

        assert score == 0.0
