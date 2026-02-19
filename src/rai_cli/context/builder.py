"""Unified graph builder for context integration.

This module provides the UnifiedGraphBuilder class that merges governance,
memory, work, and skills into a single UnifiedGraph for context queries.

Architecture: ADR-019 Unified Context Graph Architecture
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

from rai_cli.compat import portable_path
from rai_cli.config.agents import AgentConfig, get_agent_config
from rai_cli.config.paths import get_global_rai_dir, get_memory_dir, get_personal_dir
from rai_cli.context.extractors.skills import extract_all_skills
from rai_cli.context.graph import UnifiedGraph
from rai_cli.context.models import ConceptEdge, ConceptNode
from rai_cli.core.text import STOPWORDS
from rai_cli.memory.models import MemoryScope

if TYPE_CHECKING:
    from rai_cli.governance.extractor import GovernanceExtractor
    from rai_cli.governance.models import Concept


class UnifiedGraphBuilder:
    """Builds unified context graph from all sources.

    Merges governance documents, memory JSONL files, work tracking,
    and skill metadata into a single queryable graph.

    Attributes:
        project_root: Root directory for the project.

    Examples:
        >>> builder = UnifiedGraphBuilder(Path("."))
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

    def build(self) -> UnifiedGraph:
        """Build unified graph from all sources.

        Loads concepts from governance, memory, work, skills, and components,
        then builds a UnifiedGraph with all nodes. After all nodes are loaded,
        extracts structural nodes (bounded contexts, layers) and their edges.

        Returns:
            UnifiedGraph containing all concepts.
        """
        graph = UnifiedGraph()

        # Load all sources
        all_nodes: list[ConceptNode] = []
        all_nodes.extend(self.load_governance())
        all_nodes.extend(self.load_memory())
        all_nodes.extend(self.load_work())
        all_nodes.extend(self.load_skills())
        all_nodes.extend(self.load_components())
        all_nodes.extend(self.load_architecture())
        all_nodes.extend(self.load_identity())

        # Enrich module nodes with real code analysis (S16.1)
        # Must run before add_concept() so graph gets enriched copies
        self.load_code_structure(all_nodes)

        # Warn on duplicate node IDs before adding (silent overwrites lose data)
        seen_ids: dict[str, str] = {}
        for node in all_nodes:
            if node.id in seen_ids:
                logging.warning(
                    "Duplicate node ID '%s' — '%s' will overwrite '%s'",
                    node.id,
                    node.source_file or "unknown",
                    seen_ids[node.id],
                )
            seen_ids[node.id] = node.source_file or "unknown"

        # Add nodes to graph
        for node in all_nodes:
            graph.add_concept(node)

        # Extract structural nodes and edges (E15 — bounded contexts, layers)
        # Runs after all nodes loaded so module nodes exist for edge safety
        node_by_id: dict[str, ConceptNode] = {n.id: n for n in all_nodes}
        structural_nodes: list[ConceptNode] = []
        structural_edges: list[ConceptEdge] = []

        bc_nodes, bc_edges = self._extract_bounded_contexts(all_nodes, node_by_id)
        structural_nodes.extend(bc_nodes)
        structural_edges.extend(bc_edges)

        lyr_nodes, lyr_edges = self._extract_layers(all_nodes, node_by_id)
        structural_nodes.extend(lyr_nodes)
        structural_edges.extend(lyr_edges)

        for node in structural_nodes:
            graph.add_concept(node)
        all_nodes.extend(structural_nodes)

        # Update node_by_id with structural nodes for constraint edge safety
        node_by_id.update({n.id: n for n in structural_nodes})

        # Extract constraint edges (S15.3 — guardrail → BC/layer)
        constraint_edges = self._extract_constraints(all_nodes, node_by_id)
        structural_edges.extend(constraint_edges)

        # Infer and add relationships
        edges = self.infer_relationships(all_nodes)
        for edge in edges:
            graph.add_relationship(edge)

        # Add structural edges (explicit, not inferred)
        for edge in structural_edges:
            graph.add_relationship(edge)

        return graph

    def load_governance(self) -> list[ConceptNode]:
        """Load concepts from governance documents.

        Uses GovernanceExtractor to parse constitution, PRD, and vision.

        Returns:
            List of ConceptNode for governance concepts.
        """
        try:
            extractor = self._get_governance_extractor()
            concepts = extractor.extract_all()
            return [self._concept_to_node(c) for c in concepts]
        except Exception:
            # Graceful degradation if governance extraction fails
            return []

    def load_memory(self) -> list[ConceptNode]:
        """Load concepts from memory JSONL files across all tiers.

        Loads from three directories with scope tracking:
        - Global (~/.rai/): Universal patterns and calibration
        - Project (.raise/rai/memory/): Shared project patterns
        - Personal (.raise/rai/personal/): Developer-specific data

        Sessions are only loaded from personal directory (developer-specific).

        Returns:
            List of ConceptNode for memory concepts with scope metadata.
        """
        nodes: list[ConceptNode] = []

        # 1. Load from global directory (~/.rai/)
        global_dir = get_global_rai_dir()
        if global_dir.exists():
            nodes.extend(
                self._load_memory_from_dir(
                    global_dir, MemoryScope.GLOBAL, sessions=False
                )
            )

        # 2. Load from project directory (.raise/rai/memory/)
        project_dir = get_memory_dir(self.project_root)
        if project_dir.exists():
            nodes.extend(
                self._load_memory_from_dir(
                    project_dir, MemoryScope.PROJECT, sessions=False
                )
            )

        # 3. Load from personal directory (.raise/rai/personal/)
        personal_dir = get_personal_dir(self.project_root)
        if personal_dir.exists():
            nodes.extend(
                self._load_memory_from_dir(
                    personal_dir, MemoryScope.PERSONAL, sessions=True
                )
            )

        # Apply precedence: personal > project > global
        return self._deduplicate_by_precedence(nodes)

    def _load_memory_from_dir(
        self,
        memory_dir: Path,
        scope: MemoryScope,
        sessions: bool = True,
    ) -> list[ConceptNode]:
        """Load memory concepts from a single directory with scope.

        Args:
            memory_dir: Directory containing JSONL files.
            scope: Scope to assign to loaded concepts.
            sessions: Whether to load sessions from this directory.

        Returns:
            List of ConceptNode with scope in metadata.
        """
        nodes: list[ConceptNode] = []

        # Load patterns
        patterns_file = memory_dir / "patterns.jsonl"
        if patterns_file.exists():
            nodes.extend(self._load_jsonl(patterns_file, "pattern", scope))

        # Load calibration
        calibration_file = memory_dir / "calibration.jsonl"
        if calibration_file.exists():
            nodes.extend(self._load_jsonl(calibration_file, "calibration", scope))

        # Load sessions (only if requested)
        if sessions:
            sessions_file = memory_dir / "sessions" / "index.jsonl"
            if sessions_file.exists():
                nodes.extend(self._load_jsonl(sessions_file, "session", scope))

        return nodes

    def _deduplicate_by_precedence(self, nodes: list[ConceptNode]) -> list[ConceptNode]:
        """Deduplicate nodes by ID using scope precedence.

        When the same ID appears in multiple tiers, keep only the
        highest-precedence version: personal > project > global.

        Args:
            nodes: List of nodes potentially with duplicate IDs.

        Returns:
            Deduplicated list with highest-precedence version of each ID.
        """
        # Precedence order: higher number = higher priority
        scope_priority = {
            MemoryScope.GLOBAL.value: 1,
            MemoryScope.PROJECT.value: 2,
            MemoryScope.PERSONAL.value: 3,
        }

        # Track best node for each ID
        best_by_id: dict[str, ConceptNode] = {}

        for node in nodes:
            node_scope = node.metadata.get("scope", MemoryScope.PROJECT.value)
            node_priority = scope_priority.get(node_scope, 0)

            if node.id not in best_by_id:
                best_by_id[node.id] = node
            else:
                existing_scope = best_by_id[node.id].metadata.get(
                    "scope", MemoryScope.PROJECT.value
                )
                existing_priority = scope_priority.get(existing_scope, 0)

                if node_priority > existing_priority:
                    best_by_id[node.id] = node

        return list(best_by_id.values())

    def load_work(self) -> list[ConceptNode]:
        """Load concepts from work tracking (backlog, epics).

        Uses E8 parsers to extract epics and stories.

        Returns:
            List of ConceptNode for work concepts.
        """
        nodes: list[ConceptNode] = []

        # Load epics from backlog
        epics = self._extract_epics()
        nodes.extend(self._concept_to_node(e) for e in epics)

        # Load stories from epic scopes
        stories = self._extract_stories()
        nodes.extend(self._concept_to_node(s) for s in stories)

        return nodes

    def load_skills(self) -> list[ConceptNode]:
        """Load concepts from skill YAML frontmatter.

        Parses SKILL.md files in the IDE's skill directory.

        Returns:
            List of ConceptNode for skill concepts.
        """
        raw_skills_dir = self.ide_config.skills_dir or ".claude/skills"
        skills_dir = self.project_root / raw_skills_dir
        return extract_all_skills(skills_dir)

    def load_components(self) -> list[ConceptNode]:
        """Load discovered components from validated JSON.

        Reads components-validated.json from work/discovery directory.

        Returns:
            List of ConceptNode for component concepts.
        """
        validated_file = (
            self.project_root / "work" / "discovery" / "components-validated.json"
        )
        if not validated_file.exists():
            return []

        try:
            data: dict[str, Any] = json.loads(
                validated_file.read_text(encoding="utf-8")
            )
            components_list: list[dict[str, Any]] = data.get("components", [])

            nodes: list[ConceptNode] = []
            for comp in components_list:
                node = ConceptNode(
                    id=comp.get("id", ""),
                    type="component",
                    content=comp.get("content", ""),
                    source_file=comp.get("source_file"),
                    created=comp.get("created", datetime.now(tz=UTC).isoformat()),
                    metadata=comp.get("metadata", {}),
                )
                nodes.append(node)

            return nodes
        except (json.JSONDecodeError, KeyError):
            return []

    def load_architecture(self) -> list[ConceptNode]:
        """Load architecture nodes from documentation.

        Scans both governance/architecture/*.md (architecture docs) and
        governance/architecture/modules/*.md (module docs). Type-dispatches
        by frontmatter ``type`` field.

        Returns:
            List of ConceptNode for architecture and module concepts.
        """
        arch_dir = self.project_root / "governance" / "architecture"
        if not arch_dir.exists():
            return []

        nodes: list[ConceptNode] = []

        # Scan parent directory for architecture docs
        for md_file in sorted(arch_dir.glob("*.md")):
            node = self._parse_architecture_doc(md_file)
            if node:
                nodes.append(node)

        # Scan modules subdirectory for module docs
        modules_dir = arch_dir / "modules"
        if modules_dir.exists():
            for md_file in sorted(modules_dir.glob("*.md")):
                node = self._parse_architecture_doc(md_file)
                if node:
                    nodes.append(node)

        return nodes

    def load_identity(self) -> list[ConceptNode]:
        """Load Rai identity values and boundaries from core.md.

        Extracts values (### N. Title) and boundaries (### I Will / ### I Won't)
        as principle nodes tagged with always_on=True.

        Returns:
            List of ConceptNode for identity concepts.
        """
        identity_file = self.project_root / ".raise" / "rai" / "identity" / "core.md"
        if not identity_file.exists():
            return []

        try:
            text = identity_file.read_text(encoding="utf-8")
        except OSError:
            return []

        try:
            source_file = portable_path(identity_file, self.project_root)
        except ValueError:
            source_file = str(identity_file)

        now = datetime.now(tz=UTC).isoformat()
        nodes: list[ConceptNode] = []

        nodes.extend(self._extract_identity_values(text, source_file, now))
        nodes.extend(self._extract_identity_boundaries(text, source_file, now))

        return nodes

    def load_code_structure(self, all_nodes: list[ConceptNode]) -> None:
        """Enrich module nodes with real code analysis data.

        Runs detected analyzers against the project source and merges
        results into existing mod-* node metadata under code_* keys.
        Does not create new nodes — only enriches existing ones.

        Args:
            all_nodes: All nodes loaded so far (mutated in place).
        """
        from rai_cli.context.analyzers.models import ModuleInfo
        from rai_cli.context.analyzers.python import PythonAnalyzer

        analyzers = [PythonAnalyzer(src_dir="src/rai_cli")]

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

    def _extract_identity_values(
        self, text: str, source_file: str, now: str
    ) -> list[ConceptNode]:
        """Extract values from identity core.md.

        Matches ### N. Title patterns under ## Values section.

        Args:
            text: Full file content.
            source_file: Relative source path.
            now: ISO timestamp.

        Returns:
            List of value ConceptNodes.
        """
        import re

        nodes: list[ConceptNode] = []

        # Find values section
        values_match = re.search(r"^## Values\b", text, re.MULTILINE)
        if not values_match:
            return nodes

        # Find end of values section (next ## heading or EOF)
        next_section = re.search(r"^## ", text[values_match.end() :], re.MULTILINE)
        values_end = (
            values_match.end() + next_section.start() if next_section else len(text)
        )
        values_text = text[values_match.end() : values_end]

        # Match ### N. Title patterns
        value_pattern = re.compile(r"^### (\d+)\.\s+(.+)$", re.MULTILINE)
        matches = list(value_pattern.finditer(values_text))

        for i, match in enumerate(matches):
            num = match.group(1)
            title = match.group(2).strip()

            # Extract first bullet point as description
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(values_text)
            section_text = values_text[start:end]

            bullet_match = re.search(r"^- (.+)$", section_text, re.MULTILINE)
            description = bullet_match.group(1).strip() if bullet_match else ""

            content = f"{title} — {description}" if description else title

            nodes.append(
                ConceptNode(
                    id=f"RAI-VAL-{num}",
                    type="principle",
                    content=content,
                    source_file=source_file,
                    created=now,
                    metadata={
                        "always_on": True,
                        "identity_type": "value",
                        "value_number": num,
                        "value_name": title,
                    },
                )
            )

        return nodes

    def _extract_identity_boundaries(
        self, text: str, source_file: str, now: str
    ) -> list[ConceptNode]:
        """Extract boundaries from identity core.md.

        Matches ### I Will and ### I Won't sections, extracts bullet items.

        Args:
            text: Full file content.
            source_file: Relative source path.
            now: ISO timestamp.

        Returns:
            List of boundary ConceptNodes.
        """
        import re

        nodes: list[ConceptNode] = []

        # Find boundaries section
        boundaries_match = re.search(r"^## Boundaries\b", text, re.MULTILINE)
        if not boundaries_match:
            return nodes

        # Find end of boundaries section (next ## heading or EOF)
        next_section = re.search(r"^## ", text[boundaries_match.end() :], re.MULTILINE)
        boundaries_end = (
            boundaries_match.end() + next_section.start() if next_section else len(text)
        )
        boundaries_text = text[boundaries_match.end() : boundaries_end]

        # Extract "I Will" bullets
        will_match = re.search(r"^### I Will\b", boundaries_text, re.MULTILINE)
        wont_match = re.search(r"^### I Won't\b", boundaries_text, re.MULTILINE)

        counter = 1

        if will_match:
            start = will_match.end()
            end = wont_match.start() if wont_match else len(boundaries_text)
            will_text = boundaries_text[start:end]

            for bullet in re.finditer(r"^- (.+)$", will_text, re.MULTILINE):
                nodes.append(
                    ConceptNode(
                        id=f"RAI-BND-{counter}",
                        type="principle",
                        content=bullet.group(1).strip(),
                        source_file=source_file,
                        created=now,
                        metadata={
                            "always_on": True,
                            "identity_type": "boundary",
                            "boundary_kind": "will",
                        },
                    )
                )
                counter += 1

        if wont_match:
            start = wont_match.end()
            # Find next ### or end
            next_heading = re.search(r"^### ", boundaries_text[start:], re.MULTILINE)
            end = start + next_heading.start() if next_heading else len(boundaries_text)
            wont_text = boundaries_text[start:end]

            for bullet in re.finditer(r"^- (.+)$", wont_text, re.MULTILINE):
                nodes.append(
                    ConceptNode(
                        id=f"RAI-BND-{counter}",
                        type="principle",
                        content=bullet.group(1).strip(),
                        source_file=source_file,
                        created=now,
                        metadata={
                            "always_on": True,
                            "identity_type": "boundary",
                            "boundary_kind": "wont",
                        },
                    )
                )
                counter += 1

        return nodes

    def _parse_architecture_doc(self, file_path: Path) -> ConceptNode | None:
        """Parse an architecture doc's YAML frontmatter into a ConceptNode.

        Dispatches by frontmatter ``type`` field to produce the appropriate
        node type (module or architecture).

        Args:
            file_path: Path to the markdown file.

        Returns:
            ConceptNode if valid frontmatter found, None otherwise.
        """
        try:
            text = file_path.read_text(encoding="utf-8")
        except OSError:
            return None

        # Extract YAML frontmatter between --- delimiters
        if not text.startswith("---"):
            return None

        end = text.find("---", 3)
        if end == -1:
            return None

        frontmatter_text = text[3:end].strip()

        try:
            import yaml

            frontmatter_raw: Any = yaml.safe_load(frontmatter_text)
        except Exception:
            return None

        if not isinstance(frontmatter_raw, dict):
            return None
        frontmatter = cast(dict[str, Any], frontmatter_raw)

        # Build relative source path
        try:
            source_file = portable_path(file_path, self.project_root)
        except ValueError:
            source_file = str(file_path)

        doc_type = frontmatter.get("type", "")

        # Type-dispatch by frontmatter type
        if doc_type == "module":
            return self._parse_module_doc(frontmatter, source_file)
        if doc_type == "architecture_context":
            return self._parse_architecture_context(frontmatter, source_file)
        if doc_type == "architecture_design":
            return self._parse_architecture_design(frontmatter, source_file)
        if doc_type == "architecture_domain_model":
            return self._parse_architecture_domain_model(frontmatter, source_file)
        # Skip architecture_index and unknown types
        return None

    def _parse_module_doc(
        self, frontmatter: dict[str, Any], source_file: str
    ) -> ConceptNode | None:
        """Parse a module-type architecture doc.

        Args:
            frontmatter: Parsed YAML frontmatter dict.
            source_file: Relative path to the source file.

        Returns:
            ConceptNode with type "module", or None if invalid.
        """
        name = frontmatter.get("name", "")
        if not name:
            return None

        metadata: dict[str, Any] = {}
        for key in (
            "depends_on",
            "depended_by",
            "entry_points",
            "public_api",
            "components",
            "constraints",
            "status",
        ):
            if key in frontmatter:
                metadata[key] = frontmatter[key]

        return ConceptNode(
            id=f"mod-{name}",
            type="module",
            content=frontmatter.get("purpose", ""),
            source_file=source_file,
            created=frontmatter.get("last_validated", datetime.now(tz=UTC).isoformat()),
            metadata=metadata,
        )

    def _parse_architecture_context(
        self, frontmatter: dict[str, Any], source_file: str
    ) -> ConceptNode:
        """Parse an architecture_context doc (system-context.md).

        Synthesizes content from tech stack and external dependencies.

        Args:
            frontmatter: Parsed YAML frontmatter dict.
            source_file: Relative path to the source file.

        Returns:
            ConceptNode with type "architecture".
        """
        # Synthesize content from tech stack
        tech_stack: dict[str, str] = frontmatter.get("tech_stack", {})
        tech_parts = [f"{k}: {v}" for k, v in tech_stack.items()]
        tech_summary = ", ".join(tech_parts) if tech_parts else "No tech stack defined"

        ext_deps: list[str] = frontmatter.get("external_dependencies", [])
        deps_summary = ", ".join(ext_deps) if ext_deps else "none"

        content = (
            f"System context: {tech_summary}. External dependencies: {deps_summary}."
        )

        # Store all structured data in metadata
        metadata: dict[str, Any] = {"arch_type": "architecture_context"}
        for key in (
            "tech_stack",
            "external_dependencies",
            "users",
            "governed_by",
            "project",
            "version",
            "status",
        ):
            if key in frontmatter:
                metadata[key] = frontmatter[key]

        return ConceptNode(
            id="arch-context",
            type="architecture",
            content=content,
            source_file=source_file,
            created=datetime.now(tz=UTC).isoformat(),
            metadata=metadata,
        )

    def _parse_architecture_design(
        self, frontmatter: dict[str, Any], source_file: str
    ) -> ConceptNode:
        """Parse an architecture_design doc (system-design.md).

        Synthesizes content from layers and their module assignments.

        Args:
            frontmatter: Parsed YAML frontmatter dict.
            source_file: Relative path to the source file.

        Returns:
            ConceptNode with type "architecture".
        """
        # Synthesize content from layers
        layers: list[dict[str, Any]] = frontmatter.get("layers", [])
        layer_parts: list[str] = []
        for layer in layers:
            name = layer.get("name", "unknown")
            modules: list[str] = layer.get("modules", [])
            layer_parts.append(f"{name}: {', '.join(modules)}")

        layers_summary = ". ".join(layer_parts) if layer_parts else "No layers defined"
        layer_names = ", ".join(layer.get("name", "") for layer in layers)
        content = (
            f"System design: {len(layers)} layers ({layer_names}). {layers_summary}."
        )

        # Store all structured data in metadata
        metadata: dict[str, Any] = {"arch_type": "architecture_design"}
        for key in (
            "layers",
            "architectural_decisions",
            "distribution",
            "guardrails_reference",
            "constitution_reference",
            "project",
            "status",
        ):
            if key in frontmatter:
                metadata[key] = frontmatter[key]

        return ConceptNode(
            id="arch-design",
            type="architecture",
            content=content,
            source_file=source_file,
            created=datetime.now(tz=UTC).isoformat(),
            metadata=metadata,
        )

    def _parse_architecture_domain_model(
        self, frontmatter: dict[str, Any], source_file: str
    ) -> ConceptNode:
        """Parse an architecture_domain_model doc (domain-model.md).

        Synthesizes content from bounded contexts and shared kernel.

        Args:
            frontmatter: Parsed YAML frontmatter dict.
            source_file: Relative path to the source file.

        Returns:
            ConceptNode with type "architecture".
        """
        # Synthesize content from bounded contexts
        bcs: list[dict[str, Any]] = frontmatter.get("bounded_contexts", [])
        bc_names = [bc.get("name", "unknown") for bc in bcs]
        bc_summary = ", ".join(bc_names) if bc_names else "none defined"

        shared: dict[str, Any] = frontmatter.get("shared_kernel", {})
        shared_modules: list[str] = shared.get("modules", [])
        shared_summary = ", ".join(shared_modules) if shared_modules else "none"

        content = (
            f"Domain model: {len(bcs)} bounded contexts — {bc_summary}. "
            f"Shared kernel: {shared_summary}."
        )

        # Store all structured data in metadata
        metadata: dict[str, Any] = {"arch_type": "architecture_domain_model"}
        for key in (
            "bounded_contexts",
            "shared_kernel",
            "application_layer",
            "distribution",
            "project",
            "status",
        ):
            if key in frontmatter:
                metadata[key] = frontmatter[key]

        return ConceptNode(
            id="arch-domain-model",
            type="architecture",
            content=content,
            source_file=source_file,
            created=datetime.now(tz=UTC).isoformat(),
            metadata=metadata,
        )

    def _extract_bounded_contexts(
        self,
        all_nodes: list[ConceptNode],
        node_by_id: dict[str, ConceptNode],
    ) -> tuple[list[ConceptNode], list[ConceptEdge]]:
        """Extract bounded context nodes and belongs_to edges from domain model.

        Reads the arch-domain-model node's metadata to create bounded_context
        nodes for each DDD context, shared kernel, application layer, and
        distribution grouping.

        Args:
            all_nodes: All nodes loaded so far.
            node_by_id: Lookup dict by node ID.

        Returns:
            Tuple of (bounded_context nodes, belongs_to edges).
        """
        nodes: list[ConceptNode] = []
        edges: list[ConceptEdge] = []

        # Find the arch-domain-model node
        dm_node = node_by_id.get("arch-domain-model")
        if dm_node is None:
            return nodes, edges

        now = datetime.now(tz=UTC).isoformat()

        # Extract bounded contexts
        bcs: list[dict[str, Any]] = dm_node.metadata.get("bounded_contexts", [])
        for bc in bcs:
            bc_name: str = bc.get("name", "")
            if not bc_name:
                continue
            bc_id = f"bc-{bc_name}"
            nodes.append(
                ConceptNode(
                    id=bc_id,
                    type="bounded_context",
                    content=bc.get("description", ""),
                    source_file=dm_node.source_file,
                    created=now,
                    metadata={
                        "bc_type": "bounded_context",
                        "modules": bc.get("modules", []),
                    },
                )
            )
            # Create belongs_to edges for modules in this BC
            modules: list[str] = bc.get("modules", [])
            for mod_name in modules:
                mod_id = f"mod-{mod_name}"
                if mod_id in node_by_id:
                    edges.append(
                        ConceptEdge(
                            source=mod_id, target=bc_id, type="belongs_to", weight=1.0
                        )
                    )

        # Extract shared kernel as a BC node
        shared: dict[str, Any] = dm_node.metadata.get("shared_kernel", {})
        if shared:
            nodes.append(
                ConceptNode(
                    id="bc-shared-kernel",
                    type="bounded_context",
                    content=shared.get("description", ""),
                    source_file=dm_node.source_file,
                    created=now,
                    metadata={
                        "bc_type": "shared_kernel",
                        "modules": shared.get("modules", []),
                    },
                )
            )
            for mod_name in shared.get("modules", []):
                mod_id = f"mod-{mod_name}"
                if mod_id in node_by_id:
                    edges.append(
                        ConceptEdge(
                            source=mod_id,
                            target="bc-shared-kernel",
                            type="belongs_to",
                            weight=1.0,
                        )
                    )

        # Extract application layer as a BC node
        app_layer: dict[str, Any] = dm_node.metadata.get("application_layer", {})
        if app_layer:
            nodes.append(
                ConceptNode(
                    id="bc-application-layer",
                    type="bounded_context",
                    content=app_layer.get("description", ""),
                    source_file=dm_node.source_file,
                    created=now,
                    metadata={
                        "bc_type": "application_layer",
                        "modules": app_layer.get("modules", []),
                    },
                )
            )
            for mod_name in app_layer.get("modules", []):
                mod_id = f"mod-{mod_name}"
                if mod_id in node_by_id:
                    edges.append(
                        ConceptEdge(
                            source=mod_id,
                            target="bc-application-layer",
                            type="belongs_to",
                            weight=1.0,
                        )
                    )

        # Extract distribution as a BC node
        dist: dict[str, Any] = dm_node.metadata.get("distribution", {})
        if dist:
            nodes.append(
                ConceptNode(
                    id="bc-distribution",
                    type="bounded_context",
                    content=dist.get("description", ""),
                    source_file=dm_node.source_file,
                    created=now,
                    metadata={
                        "bc_type": "distribution",
                        "modules": dist.get("modules", []),
                    },
                )
            )
            for mod_name in dist.get("modules", []):
                mod_id = f"mod-{mod_name}"
                if mod_id in node_by_id:
                    edges.append(
                        ConceptEdge(
                            source=mod_id,
                            target="bc-distribution",
                            type="belongs_to",
                            weight=1.0,
                        )
                    )

        return nodes, edges

    def _extract_layers(
        self,
        all_nodes: list[ConceptNode],
        node_by_id: dict[str, ConceptNode],
    ) -> tuple[list[ConceptNode], list[ConceptEdge]]:
        """Extract layer nodes and in_layer edges from system design.

        Reads the arch-design node's metadata to create layer nodes and
        in_layer edges linking modules to their architectural layer.

        Args:
            all_nodes: All nodes loaded so far.
            node_by_id: Lookup dict by node ID.

        Returns:
            Tuple of (layer nodes, in_layer edges).
        """
        nodes: list[ConceptNode] = []
        edges: list[ConceptEdge] = []

        # Find the arch-design node
        design_node = node_by_id.get("arch-design")
        if design_node is None:
            return nodes, edges

        now = datetime.now(tz=UTC).isoformat()

        layers: list[dict[str, Any]] = design_node.metadata.get("layers", [])
        for layer in layers:
            layer_name: str = layer.get("name", "")
            if not layer_name:
                continue
            layer_id = f"lyr-{layer_name}"
            nodes.append(
                ConceptNode(
                    id=layer_id,
                    type="layer",
                    content=layer.get("description", ""),
                    source_file=design_node.source_file,
                    created=now,
                    metadata={"modules": layer.get("modules", [])},
                )
            )
            # Create in_layer edges for modules in this layer
            modules: list[str] = layer.get("modules", [])
            for mod_name in modules:
                mod_id = f"mod-{mod_name}"
                if mod_id in node_by_id:
                    edges.append(
                        ConceptEdge(
                            source=mod_id, target=layer_id, type="in_layer", weight=1.0
                        )
                    )

        return nodes, edges

    def _extract_constraints(
        self,
        all_nodes: list[ConceptNode],
        node_by_id: dict[str, ConceptNode],
    ) -> list[ConceptEdge]:
        """Extract constrained_by edges from guardrail scope metadata.

        Reads ``constraint_scope`` from each guardrail node's metadata
        (set by the guardrails parser from YAML frontmatter). Creates
        ``constrained_by`` edges from target nodes (BCs or layers) to
        guardrail nodes.

        Args:
            all_nodes: All nodes loaded so far (including structural).
            node_by_id: Lookup dict by node ID.

        Returns:
            List of constrained_by edges.
        """
        edges: list[ConceptEdge] = []
        bc_ids = [n.id for n in node_by_id.values() if n.type == "bounded_context"]

        for node in all_nodes:
            if node.type != "guardrail":
                continue

            scope: Any = node.metadata.get("constraint_scope")
            if scope is None:
                continue

            if scope == "all_bounded_contexts":
                targets = bc_ids
            elif isinstance(scope, list):
                targets = [t for t in cast(list[str], scope) if t in node_by_id]
            else:
                continue

            for target_id in targets:
                edges.append(
                    ConceptEdge(
                        source=target_id,
                        target=node.id,
                        type="constrained_by",
                        weight=1.0,
                    )
                )

        return edges

    def _get_governance_extractor(self) -> GovernanceExtractor:
        """Get governance extractor instance.

        Returns:
            GovernanceExtractor for this project.
        """
        from rai_cli.governance.extractor import GovernanceExtractor

        return GovernanceExtractor(project_root=self.project_root)

    def _concept_to_node(self, concept: Concept) -> ConceptNode:
        """Convert governance Concept to ConceptNode.

        Args:
            concept: Governance concept to convert.

        Returns:
            ConceptNode with mapped fields.
        """
        return ConceptNode(
            id=concept.id,
            type=concept.type.value,  # type: ignore[arg-type]
            content=concept.content,
            source_file=concept.file,
            created=datetime.now(tz=UTC).isoformat(),
            metadata=concept.metadata,
        )

    def _load_jsonl(
        self,
        file_path: Path,
        node_type: str,
        scope: MemoryScope = MemoryScope.PROJECT,
    ) -> list[ConceptNode]:
        """Load concepts from a JSONL file.

        Args:
            file_path: Path to JSONL file.
            node_type: Type to assign to nodes (pattern, calibration, session).
            scope: Memory scope to assign to loaded concepts.

        Returns:
            List of ConceptNode parsed from file.
        """
        nodes: list[ConceptNode] = []

        # Try to make path relative, fallback to absolute
        try:
            source_file = portable_path(file_path, self.project_root)
        except ValueError:
            source_file = str(file_path)

        for line in file_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue

            try:
                record: dict[str, Any] = json.loads(line)
            except json.JSONDecodeError:
                continue

            node = self._memory_record_to_node(record, node_type, source_file, scope)
            if node:
                nodes.append(node)

        return nodes

    def _memory_record_to_node(
        self,
        record: dict[str, Any],
        node_type: str,
        source_file: str,
        scope: MemoryScope = MemoryScope.PROJECT,
    ) -> ConceptNode | None:
        """Convert memory JSONL record to ConceptNode.

        Args:
            record: Parsed JSON record.
            node_type: Type of memory concept.
            source_file: Source file path.
            scope: Memory scope for this concept.

        Returns:
            ConceptNode or None if record is invalid.
        """
        record_id = record.get("id")
        if not record_id:
            return None

        # Build content based on type
        if node_type == "pattern":
            content = record.get("content", "")
        elif node_type == "calibration":
            # Calibration uses story + name (backward compat: old "feature" key)
            story = record.get("story") or record.get("feature", "")
            name = record.get("name", "")
            content = f"{story}: {name}" if story else name
        elif node_type == "session":
            content = record.get("topic", record.get("summary", ""))
        else:
            content = record.get("content", "")

        # Get created date
        created = record.get("created") or record.get("date", "")
        if not created:
            created = datetime.now(tz=UTC).isoformat()

        # Core fields to exclude from metadata
        core_fields = {"id", "type", "content", "created", "date"}

        # Build metadata from remaining fields
        metadata: dict[str, Any] = {
            k: v for k, v in record.items() if k not in core_fields
        }

        # Add scope to metadata
        metadata["scope"] = scope.value

        return ConceptNode(
            id=str(record_id),
            type=node_type,  # type: ignore[arg-type]
            content=str(content),
            source_file=source_file,
            created=str(created),
            metadata=metadata,
        )

    def _extract_epics(self) -> list[Concept]:
        """Extract epics from backlog files.

        Returns:
            List of epic Concept objects.
        """
        from rai_cli.governance.parsers.backlog import extract_epics

        epics: list[Concept] = []

        # Find backlog files
        for backlog_path in self._find_backlogs():
            try:
                extracted = extract_epics(backlog_path, self.project_root)
                epics.extend(extracted)
            except Exception:
                continue

        return epics

    def _extract_stories(self) -> list[Concept]:
        """Extract stories from epic scope files.

        Returns:
            List of story Concept objects.
        """
        from rai_cli.governance.parsers.epic import extract_stories

        stories: list[Concept] = []

        # Find epic scope files
        for epic_path in self._find_epic_scopes():
            try:
                extracted = extract_stories(epic_path, self.project_root)
                stories.extend(extracted)
            except Exception:
                continue

        return stories

    def _find_backlogs(self) -> list[Path]:
        """Find backlog.md files in project.

        Returns:
            List of paths to backlog files.
        """
        backlogs: list[Path] = []

        # Check governance/backlog.md
        backlog_file = self.project_root / "governance" / "backlog.md"
        if backlog_file.exists():
            backlogs.append(backlog_file)

        return backlogs

    def _find_epic_scopes(self) -> list[Path]:
        """Find epic scope files in project.

        Returns:
            List of paths to epic-*.md files.
        """
        scopes: list[Path] = []

        # Check dev/epic-*.md
        dev_dir = self.project_root / "dev"
        if dev_dir.exists():
            scopes.extend(dev_dir.glob("epic-*-scope.md"))

        return scopes

    def infer_relationships(self, nodes: list[ConceptNode]) -> list[ConceptEdge]:
        """Infer relationships between concepts.

        Creates explicit edges (weight=1.0) from known fields and
        inferred edges (weight<1.0) from heuristics.

        Args:
            nodes: List of concept nodes to analyze.

        Returns:
            List of inferred ConceptEdge objects.
        """
        if not nodes:
            return []

        edges: list[ConceptEdge] = []

        # Build lookup by ID for target resolution
        node_by_id: dict[str, ConceptNode] = {n.id: n for n in nodes}

        # Infer explicit edges
        edges.extend(self._infer_learned_from(nodes, node_by_id))
        edges.extend(self._infer_part_of(nodes, node_by_id))
        edges.extend(self._infer_skill_edges(nodes, node_by_id))
        edges.extend(self._infer_depends_on(nodes, node_by_id))
        edges.extend(self._infer_release_part_of(nodes, node_by_id))

        # Infer heuristic edges
        edges.extend(self._infer_keyword_relationships(nodes))

        return edges

    def _infer_learned_from(
        self,
        nodes: list[ConceptNode],
        node_by_id: dict[str, ConceptNode],
    ) -> list[ConceptEdge]:
        """Infer learned_from edges from pattern metadata.

        Args:
            nodes: All concept nodes.
            node_by_id: Lookup dict by node ID.

        Returns:
            List of learned_from edges.
        """
        edges: list[ConceptEdge] = []

        for node in nodes:
            if node.type != "pattern":
                continue

            learned_from = node.metadata.get("learned_from")
            if not learned_from:
                continue

            # Find matching session by topic/story reference
            for candidate in nodes:
                if candidate.type != "session":
                    continue

                # Check if session topic mentions the story
                if str(learned_from) in candidate.content:
                    edges.append(
                        ConceptEdge(
                            source=node.id,
                            target=candidate.id,
                            type="learned_from",
                            weight=1.0,
                        )
                    )
                    break

        return edges

    def _infer_part_of(
        self,
        nodes: list[ConceptNode],
        node_by_id: dict[str, ConceptNode],
    ) -> list[ConceptEdge]:
        """Infer part_of edges from story to epic.

        Args:
            nodes: All concept nodes.
            node_by_id: Lookup dict by node ID.

        Returns:
            List of part_of edges.
        """
        edges: list[ConceptEdge] = []

        for node in nodes:
            if node.type != "story":
                continue

            # Extract epic ID from story ID (e.g., F11.2 -> E11)
            story_id = node.id
            if story_id.startswith("F"):
                # Parse epic number from story ID
                parts = story_id[1:].split(".")
                if parts:
                    epic_id = f"E{parts[0]}"
                    if epic_id in node_by_id:
                        edges.append(
                            ConceptEdge(
                                source=node.id,
                                target=epic_id,
                                type="part_of",
                                weight=1.0,
                            )
                        )

        return edges

    def _infer_skill_edges(
        self,
        nodes: list[ConceptNode],
        node_by_id: dict[str, ConceptNode],
    ) -> list[ConceptEdge]:
        """Infer edges from skill metadata (prerequisites, next).

        Args:
            nodes: All concept nodes.
            node_by_id: Lookup dict by node ID.

        Returns:
            List of skill relationship edges.
        """
        edges: list[ConceptEdge] = []

        for node in nodes:
            if node.type != "skill":
                continue

            # Prerequisites -> needs_context
            prereq = node.metadata.get("raise.prerequisites")
            if prereq:
                prereq_id = f"/{prereq}" if not str(prereq).startswith("/") else prereq
                if prereq_id in node_by_id:
                    edges.append(
                        ConceptEdge(
                            source=node.id,
                            target=prereq_id,
                            type="needs_context",
                            weight=1.0,
                        )
                    )

            # Next -> related_to
            next_skill = node.metadata.get("raise.next")
            if next_skill:
                next_id = (
                    f"/{next_skill}"
                    if not str(next_skill).startswith("/")
                    else next_skill
                )
                if next_id in node_by_id:
                    edges.append(
                        ConceptEdge(
                            source=node.id,
                            target=next_id,
                            type="related_to",
                            weight=1.0,
                        )
                    )

        return edges

    def _infer_depends_on(
        self,
        nodes: list[ConceptNode],
        node_by_id: dict[str, ConceptNode],
    ) -> list[ConceptEdge]:
        """Infer depends_on edges from module metadata.

        Args:
            nodes: All concept nodes.
            node_by_id: Lookup dict by node ID.

        Returns:
            List of depends_on edges between modules.
        """
        edges: list[ConceptEdge] = []

        for node in nodes:
            if node.type != "module":
                continue

            raw_deps: Any = node.metadata.get("depends_on", [])
            if not isinstance(raw_deps, list):
                continue
            deps = cast(list[str], raw_deps)

            for dep_name in deps:
                target_id = f"mod-{dep_name}"
                if target_id in node_by_id:
                    edges.append(
                        ConceptEdge(
                            source=node.id,
                            target=target_id,
                            type="depends_on",
                            weight=1.0,
                        )
                    )

        return edges

    def _infer_release_part_of(
        self,
        nodes: list[ConceptNode],
        node_by_id: dict[str, ConceptNode],
    ) -> list[ConceptEdge]:
        """Infer part_of edges from epics to releases.

        Uses the ``epics`` list in release node metadata to create
        part_of edges. Skips edges where the epic node doesn't exist.

        Args:
            nodes: All concept nodes.
            node_by_id: Lookup dict by node ID.

        Returns:
            List of part_of edges from epic to release.
        """
        edges: list[ConceptEdge] = []

        for node in nodes:
            if node.type != "release":
                continue

            epic_refs: Any = node.metadata.get("epics", [])
            if not isinstance(epic_refs, list):
                continue

            for epic_ref in cast(list[str], epic_refs):
                epic_id = f"epic-{epic_ref.lower()}"
                if epic_id in node_by_id:
                    edges.append(
                        ConceptEdge(
                            source=epic_id,
                            target=node.id,
                            type="part_of",
                            weight=1.0,
                        )
                    )

        return edges

    def _infer_keyword_relationships(
        self,
        nodes: list[ConceptNode],
    ) -> list[ConceptEdge]:
        """Infer related_to edges from shared keywords.

        Args:
            nodes: All concept nodes.

        Returns:
            List of keyword-based relationship edges.
        """
        edges: list[ConceptEdge] = []

        # Extract keywords for each node
        node_keywords: dict[str, set[str]] = {}
        for node in nodes:
            keywords = self._extract_keywords(node)
            if keywords:
                node_keywords[node.id] = keywords

        # Find pairs with shared keywords (at least 2)
        node_ids = list(node_keywords.keys())
        for i, id1 in enumerate(node_ids):
            for id2 in node_ids[i + 1 :]:
                shared = node_keywords[id1] & node_keywords[id2]
                if len(shared) >= 2:
                    edges.append(
                        ConceptEdge(
                            source=id1,
                            target=id2,
                            type="related_to",
                            weight=0.5,
                            metadata={"shared_keywords": list(shared)},
                        )
                    )

        return edges

    def _extract_keywords(self, node: ConceptNode) -> set[str]:
        """Extract keywords from a concept node.

        Args:
            node: Concept node to extract keywords from.

        Returns:
            Set of lowercase keywords.
        """
        keywords: set[str] = set()

        # From content
        if node.content:
            words = node.content.lower().split()
            for word in words:
                # Clean word (keep only alphanumeric)
                clean = "".join(c for c in word if c.isalnum())
                if len(clean) >= 4 and clean not in STOPWORDS:
                    keywords.add(clean)

        # From context metadata (for patterns)
        context_value: Any = node.metadata.get("context", [])
        if isinstance(context_value, list):
            context_list = cast(list[Any], context_value)
            for ctx in context_list:
                if isinstance(ctx, str):
                    keywords.add(ctx.lower())

        return keywords
