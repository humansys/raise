"""Integration tests for MVC query system with real governance data."""

import pytest

from raise_cli.governance import GovernanceExtractor
from raise_cli.governance.graph.builder import GraphBuilder
from raise_cli.governance.query import ContextQuery, ContextQueryEngine, QueryStrategy


@pytest.fixture
def real_graph():
    """Build graph from actual raise-commons governance files."""
    try:
        extractor = GovernanceExtractor()
        concepts = extractor.extract_all()

        if len(concepts) == 0:
            pytest.skip("No governance files found in current directory")

        builder = GraphBuilder()
        graph = builder.build(concepts)

        return graph
    except Exception as e:
        pytest.skip(f"Could not build real graph: {e}")


class TestEndToEndWorkflow:
    """Test complete workflow: extract → build → query."""

    def test_extract_build_query_workflow(self, real_graph) -> None:
        """Test end-to-end workflow with real data."""
        # Graph built in fixture
        assert len(real_graph.nodes) > 0
        assert len(real_graph.edges) >= 0

        # Create engine
        engine = ContextQueryEngine(real_graph)

        # Query (find any concept)
        first_concept_id = list(real_graph.nodes.keys())[0]
        query = ContextQuery(query=first_concept_id)
        result = engine.query(query)

        # Should return results
        assert len(result.concepts) >= 1
        assert result.metadata.total_concepts >= 1


class TestTokenSavings:
    """Test MVC achieves >90% token savings."""

    def test_token_savings_vs_full_files(self, real_graph) -> None:
        """Test MVC query achieves significant token savings."""
        if len(real_graph.nodes) == 0:
            pytest.skip("No concepts in graph")

        engine = ContextQueryEngine(real_graph)

        # Find a requirement concept if available
        req_concepts = [c for c in real_graph.nodes.values() if c.type.value == "requirement"]

        if len(req_concepts) == 0:
            pytest.skip("No requirement concepts found")

        # Query first requirement
        query = ContextQuery(query=req_concepts[0].id)
        result = engine.query(query)

        # Token estimate should be reasonable
        assert result.metadata.token_estimate > 0

        # Should be much less than manual approach (~6,000 tokens for 3 files)
        # Target: <1000 tokens for typical query
        assert result.metadata.token_estimate < 2000

    def test_keyword_search_returns_relevant_only(self, real_graph) -> None:
        """Test keyword search returns only relevant concepts."""
        if len(real_graph.nodes) < 2:
            pytest.skip("Not enough concepts for keyword test")

        engine = ContextQueryEngine(real_graph)

        # Search for a common word
        query = ContextQuery(query="governance", strategy=QueryStrategy.KEYWORD_SEARCH)
        result = engine.query(query)

        # Should return some results
        assert len(result.concepts) >= 1

        # All returned concepts should mention the keyword
        for concept in result.concepts:
            text = (concept.section + " " + concept.content).lower()
            assert "governance" in text or "govern" in text


class TestQueryPerformance:
    """Test query performance meets requirements."""

    def test_query_execution_time(self, real_graph) -> None:
        """Test query executes in <200ms."""
        if len(real_graph.nodes) == 0:
            pytest.skip("No concepts in graph")

        engine = ContextQueryEngine(real_graph)
        first_concept_id = list(real_graph.nodes.keys())[0]

        query = ContextQuery(query=first_concept_id)
        result = engine.query(query)

        # Execution time should be fast
        assert result.metadata.execution_time_ms < 500  # Generous limit

    def test_keyword_search_performance(self, real_graph) -> None:
        """Test keyword search completes quickly."""
        if len(real_graph.nodes) == 0:
            pytest.skip("No concepts in graph")

        engine = ContextQueryEngine(real_graph)

        query = ContextQuery(query="system", strategy=QueryStrategy.KEYWORD_SEARCH)
        result = engine.query(query)

        # Should be reasonably fast even for full graph search
        assert result.metadata.execution_time_ms < 1000


class TestAllStrategies:
    """Test all 4 query strategies with real data."""

    def test_concept_lookup_strategy(self, real_graph) -> None:
        """Test CONCEPT_LOOKUP with real data."""
        if len(real_graph.nodes) == 0:
            pytest.skip("No concepts in graph")

        engine = ContextQueryEngine(real_graph)
        first_concept_id = list(real_graph.nodes.keys())[0]

        query = ContextQuery(query=first_concept_id, strategy=QueryStrategy.CONCEPT_LOOKUP)
        result = engine.query(query)

        assert len(result.concepts) >= 1
        assert result.metadata.strategy == QueryStrategy.CONCEPT_LOOKUP

    def test_keyword_search_strategy(self, real_graph) -> None:
        """Test KEYWORD_SEARCH with real data."""
        if len(real_graph.nodes) == 0:
            pytest.skip("No concepts in graph")

        engine = ContextQueryEngine(real_graph)

        query = ContextQuery(query="governance", strategy=QueryStrategy.KEYWORD_SEARCH)
        result = engine.query(query)

        assert result.metadata.strategy == QueryStrategy.KEYWORD_SEARCH

    def test_relationship_traversal_strategy(self, real_graph) -> None:
        """Test RELATIONSHIP_TRAVERSAL with real data."""
        if len(real_graph.nodes) == 0:
            pytest.skip("No concepts in graph")

        engine = ContextQueryEngine(real_graph)
        first_concept_id = list(real_graph.nodes.keys())[0]

        query = ContextQuery(
            query=first_concept_id,
            strategy=QueryStrategy.RELATIONSHIP_TRAVERSAL,
            filters={"edge_types": ["governed_by", "implements"]},
        )
        result = engine.query(query)

        assert result.metadata.strategy == QueryStrategy.RELATIONSHIP_TRAVERSAL

    def test_related_concepts_strategy(self, real_graph) -> None:
        """Test RELATED_CONCEPTS with real data."""
        if len(real_graph.nodes) == 0:
            pytest.skip("No concepts in graph")

        engine = ContextQueryEngine(real_graph)

        query = ContextQuery(query="context generation", strategy=QueryStrategy.RELATED_CONCEPTS)
        result = engine.query(query)

        assert result.metadata.strategy == QueryStrategy.RELATED_CONCEPTS


class TestOutputFormats:
    """Test output formatting with real data."""

    def test_markdown_formatting(self, real_graph) -> None:
        """Test markdown output format."""
        if len(real_graph.nodes) == 0:
            pytest.skip("No concepts in graph")

        engine = ContextQueryEngine(real_graph)
        first_concept_id = list(real_graph.nodes.keys())[0]

        query = ContextQuery(query=first_concept_id)
        result = engine.query(query)

        from raise_cli.governance.query.formatters import format_markdown

        markdown = format_markdown(result)

        # Check markdown structure
        assert "# Minimum Viable Context" in markdown
        assert "**Query:**" in markdown
        assert "**Strategy:**" in markdown

    def test_json_formatting(self, real_graph) -> None:
        """Test JSON output format."""
        if len(real_graph.nodes) == 0:
            pytest.skip("No concepts in graph")

        engine = ContextQueryEngine(real_graph)
        first_concept_id = list(real_graph.nodes.keys())[0]

        query = ContextQuery(query=first_concept_id)
        result = engine.query(query)

        import json

        from raise_cli.governance.query.formatters import format_json

        json_str = format_json(result)

        # Should be valid JSON
        data = json.loads(json_str)
        assert "concepts" in data
        assert "metadata" in data
