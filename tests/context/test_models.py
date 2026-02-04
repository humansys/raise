"""Tests for unified context graph models."""

from __future__ import annotations

import pytest

from raise_cli.context.models import ConceptEdge, ConceptNode


class TestConceptNode:
    """Tests for ConceptNode model."""

    def test_create_pattern_node(self) -> None:
        """Test creating a pattern node."""
        node = ConceptNode(
            id="PAT-001",
            type="pattern",
            content="Singleton with get/set/configure pattern",
            source_file=".rai/memory/patterns.jsonl",
            created="2026-01-31",
            metadata={"sub_type": "codebase", "context": ["testing"]},
        )
        assert node.id == "PAT-001"
        assert node.type == "pattern"
        assert "Singleton" in node.content
        assert node.source_file == ".rai/memory/patterns.jsonl"
        assert node.metadata["sub_type"] == "codebase"

    def test_create_principle_node(self) -> None:
        """Test creating a principle node."""
        node = ConceptNode(
            id="§2",
            type="principle",
            content="Governance as Code - Standards versioned in Git",
            created="2026-02-03",
        )
        assert node.id == "§2"
        assert node.type == "principle"
        assert node.source_file is None
        assert node.metadata == {}

    def test_create_skill_node(self) -> None:
        """Test creating a skill node."""
        node = ConceptNode(
            id="/feature-plan",
            type="skill",
            content="Decompose user stories into atomic executable tasks",
            source_file=".claude/skills/feature-plan/SKILL.md",
            created="2026-02-03",
            metadata={"phases": ["plan"]},
        )
        assert node.id == "/feature-plan"
        assert node.type == "skill"

    def test_create_feature_node(self) -> None:
        """Test creating a feature node."""
        node = ConceptNode(
            id="F11.1",
            type="feature",
            content="Unified Graph Schema - Pydantic models and NetworkX wrapper",
            source_file="dev/epic-e11-scope.md",
            created="2026-02-03",
            metadata={"size": "S", "epic": "E11"},
        )
        assert node.id == "F11.1"
        assert node.type == "feature"
        assert node.metadata["epic"] == "E11"

    def test_all_node_types_valid(self) -> None:
        """Test that all node types can be created."""
        node_types = [
            ("PAT-001", "pattern"),
            ("CAL-001", "calibration"),
            ("SES-001", "session"),
            ("§1", "principle"),
            ("RF-01", "requirement"),
            ("OUT-001", "outcome"),
            ("E11", "epic"),
            ("F11.1", "feature"),
            ("/test", "skill"),
        ]
        for node_id, node_type in node_types:
            node = ConceptNode(
                id=node_id,
                type=node_type,  # type: ignore[arg-type]
                content=f"Test {node_type}",
                created="2026-02-03",
            )
            assert node.type == node_type

    def test_token_estimate(self) -> None:
        """Test token estimation."""
        node = ConceptNode(
            id="PAT-001",
            type="pattern",
            content="A" * 100,  # 100 characters
            created="2026-02-03",
        )
        assert node.token_estimate == 25  # 100 // 4

    def test_invalid_node_type_rejected(self) -> None:
        """Test that invalid node types are rejected."""
        with pytest.raises(ValueError):
            ConceptNode(
                id="TEST-001",
                type="invalid_type",  # type: ignore[arg-type]
                content="Test",
                created="2026-02-03",
            )


class TestConceptEdge:
    """Tests for ConceptEdge model."""

    def test_create_learned_from_edge(self) -> None:
        """Test creating a learned_from edge."""
        edge = ConceptEdge(
            source="PAT-001",
            target="SES-015",
            type="learned_from",
            weight=1.0,
            metadata={"confidence": 0.9},
        )
        assert edge.source == "PAT-001"
        assert edge.target == "SES-015"
        assert edge.type == "learned_from"
        assert edge.weight == 1.0
        assert edge.metadata["confidence"] == 0.9

    def test_create_governed_by_edge(self) -> None:
        """Test creating a governed_by edge."""
        edge = ConceptEdge(
            source="RF-05",
            target="§2",
            type="governed_by",
        )
        assert edge.source == "RF-05"
        assert edge.target == "§2"
        assert edge.type == "governed_by"
        assert edge.weight == 1.0  # default
        assert edge.metadata == {}  # default

    def test_all_edge_types_valid(self) -> None:
        """Test that all edge types can be created."""
        edge_types = [
            "learned_from",
            "governed_by",
            "applies_to",
            "needs_context",
            "implements",
            "part_of",
            "related_to",
        ]
        for edge_type in edge_types:
            edge = ConceptEdge(
                source="A",
                target="B",
                type=edge_type,  # type: ignore[arg-type]
            )
            assert edge.type == edge_type

    def test_custom_weight(self) -> None:
        """Test custom edge weight."""
        edge = ConceptEdge(
            source="A",
            target="B",
            type="related_to",
            weight=0.5,
        )
        assert edge.weight == 0.5

    def test_invalid_edge_type_rejected(self) -> None:
        """Test that invalid edge types are rejected."""
        with pytest.raises(ValueError):
            ConceptEdge(
                source="A",
                target="B",
                type="invalid_type",  # type: ignore[arg-type]
            )
