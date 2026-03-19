"""Pydantic models for the knowledge graph.

Core data structures: nodes, edges, type systems. All knowledge in RaiSE
(patterns, governance, discovery, sessions) is represented as typed nodes
and directed edges in a queryable graph.

Architecture: ADR-019 Unified Context Graph Architecture
"""

from __future__ import annotations

from typing import Any, ClassVar

from pydantic import BaseModel, Field, model_validator

# --- Node type system (open for plugins) ---
NodeType = str


class GraphNode(BaseModel):
    """Base class for all knowledge graph nodes. Auto-registers subclasses.

    Pattern: pytest Node + Airflow BaseOperator + Kedro AbstractDataset.
    Subclasses define node_type and optionally add typed fields.

    Examples:
        >>> class JiraSprintNode(GraphNode, node_type="jira.sprint"):
        ...     sprint_id: str = ""
        >>> node = JiraSprintNode(id="S1", content="Sprint 1", created="2026-01-01")
        >>> node.type
        'jira.sprint'
    """

    _registry: ClassVar[dict[str, type[GraphNode]]] = {}

    id: str = Field(..., description="Unique identifier (e.g., 'PAT-001', '§2')")
    type: str = Field(default="", description="Node type (auto-set by subclass)")
    content: str = Field(..., description="Main text content or description")
    source_file: str | None = Field(default=None, description="Path to source file")
    created: str = Field(..., description="ISO timestamp when created")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Type-specific attributes"
    )

    def __init_subclass__(cls, node_type: str | None = None, **kwargs: Any) -> None:  # noqa: D105
        super().__init_subclass__(**kwargs)
        if node_type is not None:
            cls.__node_type__ = node_type  # type: ignore[attr-defined]
            GraphNode._registry[node_type] = cls

    @model_validator(mode="before")
    @classmethod
    def _set_default_type(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Auto-set type field from subclass registration."""
        if hasattr(cls, "__node_type__"):
            node_type: str = cls.__node_type__  # type: ignore[attr-defined]
            data.setdefault("type", node_type)
        return data

    @classmethod
    def resolve(cls, node_type: str) -> type[GraphNode]:
        """Resolve a node_type string to its registered class."""
        return cls._registry[node_type]

    @classmethod
    def registered_types(cls) -> dict[str, type[GraphNode]]:
        """All registered node type mappings."""
        return dict(cls._registry)

    @property
    def token_estimate(self) -> int:
        """Estimate tokens for this concept.

        Returns:
            Estimated token count (content length // 4).
        """
        return len(self.content) // 4


# --- Core node types (18) — documented extension points ---


class PatternNode(GraphNode, node_type="pattern"):
    """Learned patterns from memory. Extension: confidence scores, decay metadata."""


class CalibrationNode(GraphNode, node_type="calibration"):
    """Velocity/estimation data. Extension: per-team calibration fields."""


class SessionNode(GraphNode, node_type="session"):
    """Session history records. Extension: agent-specific session data."""


class PrincipleNode(GraphNode, node_type="principle"):
    """Constitution principles. Extension: org-level principle overrides."""


class RequirementNode(GraphNode, node_type="requirement"):
    """PRD requirements. Extension: priority, stakeholder fields."""


class OutcomeNode(GraphNode, node_type="outcome"):
    """Vision outcomes. Extension: OKR linkage fields."""


class ProjectNode(GraphNode, node_type="project"):
    """Project definitions. Extension: multi-repo project metadata."""


class EpicNode(GraphNode, node_type="epic"):
    """Epic scopes. Extension: Jira epic fields (key, board, sprint)."""


class StoryNode(GraphNode, node_type="story"):
    """Story work items. Extension: PM tool fields (assignee, status)."""


class SkillNode(GraphNode, node_type="skill"):
    """Skill metadata. Extension: registry, versioning, ownership."""


class DecisionNode(GraphNode, node_type="decision"):
    """Architecture decisions. Extension: review status, superseded-by."""


class GuardrailNode(GraphNode, node_type="guardrail"):
    """Code standards. Extension: enforcement level, exceptions."""


class TermNode(GraphNode, node_type="term"):
    """Glossary definitions. Extension: translations, domain scope."""


class ComponentNode(GraphNode, node_type="component"):
    """Discovered code components. Extension: language-specific metadata."""


class ModuleNode(GraphNode, node_type="module"):
    """Architecture module knowledge. Extension: dependency metrics."""


class ArchitectureNode(GraphNode, node_type="architecture"):
    """Architecture docs. Extension: diagram links, review dates."""


class BoundedContextNode(GraphNode, node_type="bounded_context"):
    """DDD bounded contexts. Extension: team ownership, API surface."""


class LayerNode(GraphNode, node_type="layer"):
    """Architectural layers. Extension: deployment mapping."""


class ReleaseNode(GraphNode, node_type="release"):
    """Release milestones. Extension: changelog, artifact URLs."""


class ArtifactNode(GraphNode, node_type="artifact"):
    """Work artifacts (scope, design, plan docs). Extension: versioning, approval status."""


# --- Edge type system (open for plugins, flat — no hierarchy needed) ---
EdgeType = str


class CoreEdgeTypes:
    """Constants for the 11 core edge types."""

    LEARNED_FROM = "learned_from"
    GOVERNED_BY = "governed_by"
    APPLIES_TO = "applies_to"
    NEEDS_CONTEXT = "needs_context"
    IMPLEMENTS = "implements"
    PART_OF = "part_of"
    RELATED_TO = "related_to"
    DEPENDS_ON = "depends_on"
    BELONGS_TO = "belongs_to"
    IN_LAYER = "in_layer"
    CONSTRAINED_BY = "constrained_by"


class GraphEdge(BaseModel):
    """An edge in the knowledge graph. Open type system.

    Represents a directed relationship between two concepts.

    Examples:
        >>> edge = GraphEdge(
        ...     source="PAT-001",
        ...     target="SES-015",
        ...     type="learned_from",
        ...     weight=1.0,
        ...     metadata={"confidence": 0.9}
        ... )
        >>> edge.source
        'PAT-001'
        >>> edge.type
        'learned_from'
    """

    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    type: EdgeType = Field(..., description="Relationship type")
    weight: float = Field(default=1.0, description="Edge weight for ranking")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional relationship attributes"
    )
