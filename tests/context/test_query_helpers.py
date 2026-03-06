"""Tests for architectural context query helpers on QueryEngine."""

from __future__ import annotations

import pytest

from raise_core.graph.engine import Graph
from raise_core.graph.models import GraphEdge, GraphNode
from raise_core.graph.query import ArchitecturalContext, QueryEngine

# --- Fixtures ---


@pytest.fixture
def arch_graph() -> Graph:
    """Create a graph with architectural structure for testing helpers.

    Graph structure:
        mod-memory --belongs_to--> bc-ontology --constrained_by--> guardrail-must-code-001
        mod-memory --belongs_to--> bc-ontology --constrained_by--> guardrail-must-test-001
        mod-memory --in_layer--> lyr-domain
        mod-memory --depends_on--> mod-context
        mod-orphan (no edges)
    """
    graph = Graph()

    # Module nodes
    graph.add_concept(
        GraphNode(
            id="mod-memory",
            type="module",
            content="Manage Rai's persistent memory",
            source_file="governance/architecture/modules/memory.md",
            created="2026-02-08",
        )
    )
    graph.add_concept(
        GraphNode(
            id="mod-context",
            type="module",
            content="Unified context graph and query engine",
            source_file="governance/architecture/modules/context.md",
            created="2026-02-08",
        )
    )
    graph.add_concept(
        GraphNode(
            id="mod-orphan",
            type="module",
            content="Module with no edges",
            source_file="governance/architecture/modules/orphan.md",
            created="2026-02-08",
        )
    )

    # Bounded context node
    graph.add_concept(
        GraphNode(
            id="bc-ontology",
            type="bounded_context",
            content="Persist, integrate, and query accumulated knowledge",
            source_file="governance/architecture/domain-model.md",
            created="2026-02-08",
        )
    )

    # Layer node
    graph.add_concept(
        GraphNode(
            id="lyr-domain",
            type="layer",
            content="Domain layer — core business logic",
            source_file="governance/architecture/system-design.md",
            created="2026-02-08",
        )
    )

    # Guardrail nodes
    graph.add_concept(
        GraphNode(
            id="guardrail-must-code-001",
            type="guardrail",
            content="[MUST] Type hints on all code",
            source_file="governance/guardrails.md",
            created="2026-02-08",
        )
    )
    graph.add_concept(
        GraphNode(
            id="guardrail-must-test-001",
            type="guardrail",
            content="[MUST] >90% test coverage",
            source_file="governance/guardrails.md",
            created="2026-02-08",
        )
    )

    # Edges: mod-memory belongs_to bc-ontology
    graph.add_relationship(
        GraphEdge(source="mod-memory", target="bc-ontology", type="belongs_to")
    )
    # Edges: mod-memory in_layer lyr-domain
    graph.add_relationship(
        GraphEdge(source="mod-memory", target="lyr-domain", type="in_layer")
    )
    # Edges: bc-ontology constrained_by guardrails
    graph.add_relationship(
        GraphEdge(
            source="bc-ontology",
            target="guardrail-must-code-001",
            type="constrained_by",
        )
    )
    graph.add_relationship(
        GraphEdge(
            source="bc-ontology",
            target="guardrail-must-test-001",
            type="constrained_by",
        )
    )
    # Edges: mod-memory depends_on mod-context
    graph.add_relationship(
        GraphEdge(source="mod-memory", target="mod-context", type="depends_on")
    )

    return graph


@pytest.fixture
def engine(arch_graph: Graph) -> QueryEngine:
    """Create query engine with architectural graph."""
    return QueryEngine(arch_graph)


# --- ArchitecturalContext Model Tests ---


class TestArchitecturalContext:
    """Tests for ArchitecturalContext Pydantic model."""

    def test_minimal_context(self) -> None:
        """ArchitecturalContext with only module is valid."""
        module = GraphNode(
            id="mod-test", type="module", content="Test", created="2026-02-08"
        )
        ctx = ArchitecturalContext(module=module)
        assert ctx.module.id == "mod-test"
        assert ctx.domain is None
        assert ctx.layer is None
        assert ctx.constraints == []
        assert ctx.dependencies == []

    def test_full_context(self) -> None:
        """ArchitecturalContext with all fields populated."""
        module = GraphNode(
            id="mod-test", type="module", content="Test", created="2026-02-08"
        )
        domain = GraphNode(
            id="bc-test",
            type="bounded_context",
            content="Test BC",
            created="2026-02-08",
        )
        ctx = ArchitecturalContext(module=module, domain=domain)
        assert ctx.domain is not None
        assert ctx.domain.id == "bc-test"


# --- find_domain_for Tests ---


class TestFindDomainFor:
    """Tests for find_domain_for helper."""

    def test_finds_domain_via_belongs_to(self, engine: QueryEngine) -> None:
        """Finds bounded context via belongs_to edge."""
        domain = engine.find_domain_for("mod-memory")
        assert domain is not None
        assert domain.id == "bc-ontology"
        assert domain.type == "bounded_context"

    def test_returns_none_for_orphan_module(self, engine: QueryEngine) -> None:
        """Returns None when module has no belongs_to edge."""
        domain = engine.find_domain_for("mod-orphan")
        assert domain is None

    def test_returns_none_for_nonexistent_module(self, engine: QueryEngine) -> None:
        """Returns None for non-existent module ID."""
        domain = engine.find_domain_for("mod-nonexistent")
        assert domain is None


# --- find_layer_for Tests ---


class TestFindLayerFor:
    """Tests for find_layer_for helper."""

    def test_finds_layer_via_in_layer(self, engine: QueryEngine) -> None:
        """Finds layer via in_layer edge."""
        layer = engine.find_layer_for("mod-memory")
        assert layer is not None
        assert layer.id == "lyr-domain"
        assert layer.type == "layer"

    def test_returns_none_for_orphan_module(self, engine: QueryEngine) -> None:
        """Returns None when module has no in_layer edge."""
        layer = engine.find_layer_for("mod-orphan")
        assert layer is None

    def test_returns_none_for_nonexistent_module(self, engine: QueryEngine) -> None:
        """Returns None for non-existent module ID."""
        layer = engine.find_layer_for("mod-nonexistent")
        assert layer is None


# --- find_constraints_for Tests ---


class TestFindConstraintsFor:
    """Tests for find_constraints_for helper."""

    def test_finds_constraints_via_two_hop(self, engine: QueryEngine) -> None:
        """Finds guardrails via module -> BC -> constrained_by (two-hop)."""
        constraints = engine.find_constraints_for("mod-memory")
        assert len(constraints) == 2
        constraint_ids = {c.id for c in constraints}
        assert "guardrail-must-code-001" in constraint_ids
        assert "guardrail-must-test-001" in constraint_ids

    def test_all_constraints_are_guardrails(self, engine: QueryEngine) -> None:
        """All returned constraints have guardrail type."""
        constraints = engine.find_constraints_for("mod-memory")
        for c in constraints:
            assert c.type == "guardrail"

    def test_returns_empty_for_orphan_module(self, engine: QueryEngine) -> None:
        """Returns empty list when module has no domain (no two-hop path)."""
        constraints = engine.find_constraints_for("mod-orphan")
        assert constraints == []

    def test_returns_empty_for_nonexistent_module(self, engine: QueryEngine) -> None:
        """Returns empty list for non-existent module ID."""
        constraints = engine.find_constraints_for("mod-nonexistent")
        assert constraints == []


# --- get_architectural_context Tests ---


class TestGetArchitecturalContext:
    """Tests for get_architectural_context composite helper."""

    def test_returns_full_context(self, engine: QueryEngine) -> None:
        """Returns populated ArchitecturalContext for a well-connected module."""
        ctx = engine.get_architectural_context("mod-memory")
        assert ctx is not None
        assert ctx.module.id == "mod-memory"
        assert ctx.domain is not None
        assert ctx.domain.id == "bc-ontology"
        assert ctx.layer is not None
        assert ctx.layer.id == "lyr-domain"
        assert len(ctx.constraints) == 2
        assert len(ctx.dependencies) == 1
        assert ctx.dependencies[0].id == "mod-context"

    def test_returns_partial_context_for_orphan(self, engine: QueryEngine) -> None:
        """Returns ArchitecturalContext with None/empty for unconnected module."""
        ctx = engine.get_architectural_context("mod-orphan")
        assert ctx is not None
        assert ctx.module.id == "mod-orphan"
        assert ctx.domain is None
        assert ctx.layer is None
        assert ctx.constraints == []
        assert ctx.dependencies == []

    def test_returns_none_for_nonexistent_module(self, engine: QueryEngine) -> None:
        """Returns None when module doesn't exist in graph."""
        ctx = engine.get_architectural_context("mod-nonexistent")
        assert ctx is None


# --- find_release_for Tests ---


@pytest.fixture
def release_graph() -> Graph:
    """Create a graph with epic→release part_of edges for testing.

    Graph structure:
        epic-e19 --part_of--> rel-v3.0
        epic-e20 --part_of--> rel-v3.0
        epic-e18 (no release edge)
    """
    graph = Graph()

    graph.add_concept(
        GraphNode(
            id="rel-v3.0",
            type="release",
            content="V3.0 Commercial Launch",
            source_file="governance/roadmap.md",
            created="2026-02-11",
            metadata={
                "release_id": "REL-V3.0",
                "name": "V3.0 Commercial Launch",
                "target": "2026-03-14",
            },
        )
    )
    graph.add_concept(
        GraphNode(
            id="epic-e19",
            type="epic",
            content="V3 Product Design",
            source_file="governance/backlog.md",
            created="2026-02-11",
        )
    )
    graph.add_concept(
        GraphNode(
            id="epic-e20",
            type="epic",
            content="V3 Hosted Rai",
            source_file="governance/backlog.md",
            created="2026-02-11",
        )
    )
    graph.add_concept(
        GraphNode(
            id="epic-e18",
            type="epic",
            content="V2 Open Core",
            source_file="governance/backlog.md",
            created="2026-02-11",
        )
    )

    graph.add_relationship(
        GraphEdge(source="epic-e19", target="rel-v3.0", type="part_of")
    )
    graph.add_relationship(
        GraphEdge(source="epic-e20", target="rel-v3.0", type="part_of")
    )

    return graph


@pytest.fixture
def release_engine(release_graph: Graph) -> QueryEngine:
    """Create query engine with release graph."""
    return QueryEngine(release_graph)


class TestFindReleaseFor:
    """Tests for find_release_for helper."""

    def test_finds_release_via_part_of(self, release_engine: QueryEngine) -> None:
        """Finds release node via part_of edge from epic."""
        release = release_engine.find_release_for("epic-e19")
        assert release is not None
        assert release.id == "rel-v3.0"
        assert release.type == "release"

    def test_returns_none_for_epic_without_release(
        self, release_engine: QueryEngine
    ) -> None:
        """Returns None when epic has no part_of edge to a release."""
        release = release_engine.find_release_for("epic-e18")
        assert release is None

    def test_returns_none_for_nonexistent_epic(
        self, release_engine: QueryEngine
    ) -> None:
        """Returns None for non-existent epic ID."""
        release = release_engine.find_release_for("epic-e999")
        assert release is None
