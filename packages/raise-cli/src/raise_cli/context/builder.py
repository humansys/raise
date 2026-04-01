"""Unified graph builder for context integration.

This module provides the GraphBuilder class that merges governance,
memory, work, and skills into a single Graph for context queries.

Architecture: ADR-019 Unified Context Graph Architecture
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from raise_cli.config.agents import AgentConfig, get_agent_config
from raise_cli.context.extractors.relationships import infer_relationships
from raise_cli.context.extractors.skills import extract_all_skills
from raise_cli.context.extractors.structure import (
    extract_bounded_contexts,
    extract_constraints,
    extract_layers,
)
from raise_cli.context.loaders.architecture import (
    load_architecture as _load_architecture,
)
from raise_cli.context.loaders.artifacts import load_artifacts as _load_artifacts
from raise_cli.context.loaders.components import load_components as _load_components
from raise_cli.context.loaders.identity import load_identity as _load_identity
from raise_cli.context.loaders.memory import load_memory as _load_memory
from raise_core.graph.engine import Graph
from raise_core.graph.models import GraphEdge, GraphNode

if TYPE_CHECKING:
    from raise_cli.governance.extractor import GovernanceExtractor


class GraphBuilder:
    """Builds unified context graph from all sources.

    Merges governance documents, memory JSONL files, work tracking,
    and skill metadata into a single queryable graph.

    Attributes:
        project_root: Root directory for the project.

    Examples:
        >>> builder = GraphBuilder(Path("."))
        >>> graph = builder.build()
        >>> graph.node_count
        50
    """

    def __init__(
        self,
        project_root: Path | None = None,
        *,
        agent_config: AgentConfig | None = None,
    ) -> None:
        """Initialize builder with project root.

        Args:
            project_root: Root directory for the project. Defaults to cwd.
            agent_config: Agent configuration. Defaults to Claude.
        """
        self.project_root = project_root or Path.cwd()
        self.ide_config = agent_config or get_agent_config()

    def build(self) -> Graph:
        """Build unified graph from all sources.

        Loads concepts from governance, memory, work, skills, and components,
        then builds a Graph with all nodes. After all nodes are loaded,
        extracts structural nodes (bounded contexts, layers) and their edges.

        Returns:
            Graph containing all concepts.
        """
        graph = Graph()

        # Load all sources
        all_nodes: list[GraphNode] = []
        all_nodes.extend(self.load_governance())
        all_nodes.extend(self.load_memory())
        all_nodes.extend(self.load_skills())
        all_nodes.extend(self.load_components())
        all_nodes.extend(self.load_artifacts())
        all_nodes.extend(self.load_architecture())
        all_nodes.extend(self.load_identity())

        # Enrich module nodes with real code analysis (S16.1)
        # Must run before add_concept() so graph gets enriched copies
        self.load_code_structure(all_nodes)

        # Fail on duplicate node IDs — silent overwrites lose data
        seen_ids: dict[str, str] = {}
        for node in all_nodes:
            if node.id in seen_ids:
                msg = (
                    f"Duplicate node ID '{node.id}' — "
                    f"'{node.source_file or 'unknown'}' would overwrite "
                    f"'{seen_ids[node.id]}'"
                )
                raise ValueError(msg)
            seen_ids[node.id] = node.source_file or "unknown"

        # Add nodes to graph
        for node in all_nodes:
            graph.add_concept(node)

        # Extract structural nodes and edges (E15 — bounded contexts, layers)
        # Runs after all nodes loaded so module nodes exist for edge safety
        node_by_id: dict[str, GraphNode] = {n.id: n for n in all_nodes}
        structural_nodes: list[GraphNode] = []
        structural_edges: list[GraphEdge] = []

        bc_nodes, bc_edges = extract_bounded_contexts(all_nodes, node_by_id)
        structural_nodes.extend(bc_nodes)
        structural_edges.extend(bc_edges)

        lyr_nodes, lyr_edges = extract_layers(all_nodes, node_by_id)
        structural_nodes.extend(lyr_nodes)
        structural_edges.extend(lyr_edges)

        for node in structural_nodes:
            graph.add_concept(node)
        all_nodes.extend(structural_nodes)

        # Update node_by_id with structural nodes for constraint edge safety
        node_by_id.update({n.id: n for n in structural_nodes})

        # Extract constraint edges (S15.3 — guardrail → BC/layer)
        constraint_edges = extract_constraints(all_nodes, node_by_id)
        structural_edges.extend(constraint_edges)

        # Infer and add relationships
        edges = infer_relationships(all_nodes)
        for edge in edges:
            graph.add_relationship(edge)

        # Add structural edges (explicit, not inferred)
        for edge in structural_edges:
            graph.add_relationship(edge)

        return graph

    def load_governance(self) -> list[GraphNode]:
        """Load concepts from governance documents.

        Uses GovernanceExtractor with registry-discovered parsers.
        extract_all() returns list[GraphNode] directly — no conversion needed.

        Returns:
            List of GraphNode for governance concepts.
        """
        try:
            extractor = self._get_governance_extractor()
            return extractor.extract_all()
        except Exception:
            # Graceful degradation if governance extraction fails
            return []

    def load_memory(self) -> list[GraphNode]:
        """Load concepts from memory JSONL files across all tiers.

        Delegates to loaders.memory.load_memory().
        """
        return _load_memory(self.project_root)

    def load_skills(self) -> list[GraphNode]:
        """Load concepts from skill YAML frontmatter.

        Parses SKILL.md files in the IDE's skill directory.

        Returns:
            List of GraphNode for skill concepts.
        """
        raw_skills_dir = self.ide_config.skills_dir or ".claude/skills"
        skills_dir = self.project_root / raw_skills_dir
        return extract_all_skills(skills_dir)

    def load_components(self) -> list[GraphNode]:
        """Load discovered components from validated JSON.

        Delegates to loaders.components.load_components().
        """
        return _load_components(self.project_root)

    def load_artifacts(self) -> list[GraphNode]:
        """Load typed skill artifacts from ``.raise/artifacts/``.

        Delegates to loaders.artifacts.load_artifacts().
        """
        return _load_artifacts(self.project_root)

    def load_architecture(self) -> list[GraphNode]:
        """Load architecture nodes from documentation.

        Delegates to loaders.architecture.load_architecture().
        """
        return _load_architecture(self.project_root)

    def load_identity(self) -> list[GraphNode]:
        """Load Rai identity values and boundaries from core.yaml.

        Delegates to loaders.identity.load_identity().
        """
        return _load_identity(self.project_root)

    def load_code_structure(self, all_nodes: list[GraphNode]) -> None:
        """Enrich module nodes with real code analysis data.

        Runs detected analyzers against the project source and merges
        results into existing mod-* node metadata under code_* keys.
        Does not create new nodes — only enriches existing ones.

        Args:
            all_nodes: All nodes loaded so far (mutated in place).
        """
        from raise_cli.context.analyzers.models import ModuleInfo
        from raise_cli.context.analyzers.python import PythonAnalyzer
        from raise_cli.context.analyzers.typescript import TypeScriptAnalyzer

        analyzers = [
            PythonAnalyzer(src_dir="src/raise_cli"),
            TypeScriptAnalyzer(src_dir="src"),
        ]

        code_modules: list[ModuleInfo] = []
        for analyzer in analyzers:
            if analyzer.detect(self.project_root):
                code_modules.extend(analyzer.analyze_modules(self.project_root))

        if not code_modules:
            return

        # Build lookup: module name → ModuleInfo
        code_by_name: dict[str, ModuleInfo] = {m.name: m for m in code_modules}

        # Enrich existing mod-* nodes
        for node in all_nodes:
            if node.type != "module":
                continue

            # Extract module name from node ID (mod-<name> → <name>)
            mod_name = node.id.removeprefix("mod-")
            info = code_by_name.get(mod_name)
            if info is None:
                continue

            node.metadata["code_imports"] = info.imports
            node.metadata["code_exports"] = info.exports
            node.metadata["code_components"] = info.component_count

    def _get_governance_extractor(self) -> GovernanceExtractor:
        """Get governance extractor instance.

        Returns:
            GovernanceExtractor for this project.
        """
        from raise_cli.governance.extractor import GovernanceExtractor

        return GovernanceExtractor(project_root=self.project_root)

    def infer_relationships(self, nodes: list[GraphNode]) -> list[GraphEdge]:
        """Infer relationships between concepts.

        Delegates to extractors.relationships module.
        """
        return infer_relationships(nodes)
