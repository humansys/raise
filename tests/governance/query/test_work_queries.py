"""Tests for work query strategies (E8)."""

import pytest

from raise_cli.governance.graph.builder import GraphBuilder
from raise_cli.governance.graph.models import ConceptGraph, Relationship
from raise_cli.governance.models import Concept, ConceptType
from raise_cli.governance.query.strategies import (
    normalize_concept_id,
    query_work_context,
)


@pytest.fixture
def work_graph() -> ConceptGraph:
    """Create a test graph with work concepts.

    Returns:
        ConceptGraph with project, epics, and features.
    """
    project = Concept(
        id="project-test",
        type=ConceptType.PROJECT,
        file="backlog.md",
        section="Backlog: test",
        lines=(1, 10),
        content="Test project",
        metadata={"name": "test", "current_epic": "E8"},
    )

    epic_e8 = Concept(
        id="epic-e8",
        type=ConceptType.EPIC,
        file="epic-e8-scope.md",
        section="E8: Work Tracking",
        lines=(1, 20),
        content="Work tracking epic",
        metadata={"epic_id": "E8", "name": "Work Tracking", "status": "draft"},
    )

    epic_e7 = Concept(
        id="epic-e7",
        type=ConceptType.EPIC,
        file="epic-e7-scope.md",
        section="E7: Distribution",
        lines=(1, 20),
        content="Distribution epic",
        metadata={"epic_id": "E7", "name": "Distribution", "status": "pending"},
    )

    feature_f81 = Concept(
        id="feature-f8-1",
        type=ConceptType.FEATURE,
        file="epic-e8-scope.md",
        section="F8.1: Parser",
        lines=(30, 30),
        content="Backlog parser feature",
        metadata={"feature_id": "F8.1", "epic_id": "E8", "status": "complete"},
    )

    feature_f82 = Concept(
        id="feature-f8-2",
        type=ConceptType.FEATURE,
        file="epic-e8-scope.md",
        section="F8.2: Graph",
        lines=(31, 31),
        content="Graph extension feature",
        metadata={"feature_id": "F8.2", "epic_id": "E8", "status": "pending"},
    )

    nodes = {
        "project-test": project,
        "epic-e8": epic_e8,
        "epic-e7": epic_e7,
        "feature-f8-1": feature_f81,
        "feature-f8-2": feature_f82,
    }

    edges = [
        Relationship(
            source="project-test",
            target="epic-e8",
            type="contains",
            metadata={"confidence": 1.0},
        ),
        Relationship(
            source="project-test",
            target="epic-e7",
            type="contains",
            metadata={"confidence": 1.0},
        ),
        Relationship(
            source="project-test",
            target="epic-e8",
            type="current_focus",
            metadata={"confidence": 1.0},
        ),
        Relationship(
            source="epic-e8",
            target="feature-f8-1",
            type="contains",
            metadata={"confidence": 1.0},
        ),
        Relationship(
            source="epic-e8",
            target="feature-f8-2",
            type="contains",
            metadata={"confidence": 1.0},
        ),
    ]

    return ConceptGraph(nodes=nodes, edges=edges, metadata={})


class TestNormalizeConceptId:
    """Tests for normalize_concept_id with work concepts."""

    def test_epic_id(self) -> None:
        """Should normalize E8 to epic-e8."""
        assert normalize_concept_id("E8") == "epic-e8"

    def test_feature_id(self) -> None:
        """Should normalize F8.1 to feature-f8-1."""
        assert normalize_concept_id("F8.1") == "feature-f8-1"

    def test_already_normalized_epic(self) -> None:
        """Should pass through already normalized epic ID."""
        assert normalize_concept_id("epic-e8") == "epic-e8"

    def test_already_normalized_feature(self) -> None:
        """Should pass through already normalized feature ID."""
        assert normalize_concept_id("feature-f8-1") == "feature-f8-1"

    def test_project_id(self) -> None:
        """Should pass through project ID."""
        assert normalize_concept_id("project-test") == "project-test"


class TestQueryWorkContext:
    """Tests for query_work_context function."""

    def test_current_work(self, work_graph: ConceptGraph) -> None:
        """Should return project and current epic for 'current work'."""
        results = query_work_context(work_graph, "current work")

        assert len(results) >= 2
        ids = [r.id for r in results]
        assert "project-test" in ids
        assert "epic-e8" in ids

    def test_current_work_includes_features(self, work_graph: ConceptGraph) -> None:
        """Should include features of current epic."""
        results = query_work_context(work_graph, "current work")

        ids = [r.id for r in results]
        assert "feature-f8-1" in ids
        assert "feature-f8-2" in ids

    def test_epic_lookup(self, work_graph: ConceptGraph) -> None:
        """Should return epic and its features for 'E8'."""
        results = query_work_context(work_graph, "E8")

        ids = [r.id for r in results]
        assert "epic-e8" in ids
        assert "feature-f8-1" in ids
        assert "feature-f8-2" in ids

    def test_epic_features_query(self, work_graph: ConceptGraph) -> None:
        """Should return features for 'E8 features'."""
        results = query_work_context(work_graph, "E8 features")

        ids = [r.id for r in results]
        assert "epic-e8" in ids
        assert "feature-f8-1" in ids
        assert "feature-f8-2" in ids

    def test_feature_lookup(self, work_graph: ConceptGraph) -> None:
        """Should return feature and parent epic for 'F8.1'."""
        results = query_work_context(work_graph, "F8.1")

        ids = [r.id for r in results]
        assert "feature-f8-1" in ids
        assert "epic-e8" in ids  # Parent epic

    def test_no_duplicates(self, work_graph: ConceptGraph) -> None:
        """Should not return duplicate concepts."""
        results = query_work_context(work_graph, "E8 features")

        ids = [r.id for r in results]
        assert len(ids) == len(set(ids))

    def test_empty_for_nonexistent(self, work_graph: ConceptGraph) -> None:
        """Should return empty for nonexistent epic."""
        results = query_work_context(work_graph, "E99")

        assert results == []


class TestIntegrationWithRealGraph:
    """Integration tests with real governance graph."""

    def test_current_work_real(self) -> None:
        """Should return current work from real graph."""
        from raise_cli.governance.extractor import GovernanceExtractor

        extractor = GovernanceExtractor()
        concepts = extractor.extract_all()

        if not concepts:
            pytest.skip("No governance files found")

        builder = GraphBuilder()
        graph = builder.build(concepts)

        results = query_work_context(graph, "current work")

        # Should have at least project and epic
        assert len(results) >= 2
        types = {r.type for r in results}
        assert ConceptType.PROJECT in types or ConceptType.EPIC in types

    def test_e8_features_real(self) -> None:
        """Should return E8 features from real graph."""
        from raise_cli.governance.extractor import GovernanceExtractor

        extractor = GovernanceExtractor()
        concepts = extractor.extract_all()

        if not concepts:
            pytest.skip("No governance files found")

        builder = GraphBuilder()
        graph = builder.build(concepts)

        results = query_work_context(graph, "E8 features")

        # Should have epic and features
        assert len(results) >= 2
        ids = [r.id for r in results]
        assert "epic-e8" in ids
        assert any(id.startswith("feature-f8") for id in ids)
