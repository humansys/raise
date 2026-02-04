"""Unified graph builder for context integration.

This module provides the UnifiedGraphBuilder class that merges governance,
memory, work, and skills into a single UnifiedGraph for context queries.

Architecture: ADR-019 Unified Context Graph Architecture
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

from raise_cli.context.extractors.skills import extract_all_skills
from raise_cli.context.graph import UnifiedGraph
from raise_cli.context.models import ConceptEdge, ConceptNode

if TYPE_CHECKING:
    from raise_cli.governance.extractor import GovernanceExtractor
    from raise_cli.governance.models import Concept


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

    def __init__(self, project_root: Path | None = None) -> None:
        """Initialize builder with project root.

        Args:
            project_root: Root directory for the project. Defaults to cwd.
        """
        self.project_root = project_root or Path.cwd()

    def build(self) -> UnifiedGraph:
        """Build unified graph from all sources.

        Loads concepts from governance, memory, work, and skills,
        then builds a UnifiedGraph with all nodes.

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

        # Add nodes to graph
        for node in all_nodes:
            graph.add_concept(node)

        # Infer and add relationships
        edges = self.infer_relationships(all_nodes)
        for edge in edges:
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
        """Load concepts from memory JSONL files.

        Reads patterns.jsonl, calibration.jsonl, and sessions/index.jsonl.

        Returns:
            List of ConceptNode for memory concepts.
        """
        memory_dir = self.project_root / ".rai" / "memory"
        if not memory_dir.exists():
            return []

        nodes: list[ConceptNode] = []

        # Load patterns
        patterns_file = memory_dir / "patterns.jsonl"
        if patterns_file.exists():
            nodes.extend(self._load_jsonl(patterns_file, "pattern"))

        # Load calibration
        calibration_file = memory_dir / "calibration.jsonl"
        if calibration_file.exists():
            nodes.extend(self._load_jsonl(calibration_file, "calibration"))

        # Load sessions
        sessions_file = memory_dir / "sessions" / "index.jsonl"
        if sessions_file.exists():
            nodes.extend(self._load_jsonl(sessions_file, "session"))

        return nodes

    def load_work(self) -> list[ConceptNode]:
        """Load concepts from work tracking (backlog, epics).

        Uses E8 parsers to extract epics and features.

        Returns:
            List of ConceptNode for work concepts.
        """
        nodes: list[ConceptNode] = []

        # Load epics from backlog
        epics = self._extract_epics()
        nodes.extend(self._concept_to_node(e) for e in epics)

        # Load features from epic scopes
        features = self._extract_features()
        nodes.extend(self._concept_to_node(f) for f in features)

        return nodes

    def load_skills(self) -> list[ConceptNode]:
        """Load concepts from skill YAML frontmatter.

        Parses SKILL.md files in .claude/skills directory.

        Returns:
            List of ConceptNode for skill concepts.
        """
        skills_dir = self.project_root / ".claude" / "skills"
        return extract_all_skills(skills_dir)

    def _get_governance_extractor(self) -> GovernanceExtractor:
        """Get governance extractor instance.

        Returns:
            GovernanceExtractor for this project.
        """
        from raise_cli.governance.extractor import GovernanceExtractor

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

    def _load_jsonl(self, file_path: Path, node_type: str) -> list[ConceptNode]:
        """Load concepts from a JSONL file.

        Args:
            file_path: Path to JSONL file.
            node_type: Type to assign to nodes (pattern, calibration, session).

        Returns:
            List of ConceptNode parsed from file.
        """
        nodes: list[ConceptNode] = []
        source_file = str(file_path.relative_to(self.project_root))

        for line in file_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue

            try:
                record: dict[str, Any] = json.loads(line)
            except json.JSONDecodeError:
                continue

            node = self._memory_record_to_node(record, node_type, source_file)
            if node:
                nodes.append(node)

        return nodes

    def _memory_record_to_node(
        self,
        record: dict[str, Any],
        node_type: str,
        source_file: str,
    ) -> ConceptNode | None:
        """Convert memory JSONL record to ConceptNode.

        Args:
            record: Parsed JSON record.
            node_type: Type of memory concept.
            source_file: Source file path.

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
            # Calibration uses feature + name
            feature = record.get("feature", "")
            name = record.get("name", "")
            content = f"{feature}: {name}" if feature else name
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
        from raise_cli.governance.parsers.backlog import extract_epics

        epics: list[Concept] = []

        # Find backlog files
        for backlog_path in self._find_backlogs():
            try:
                extracted = extract_epics(backlog_path, self.project_root)
                epics.extend(extracted)
            except Exception:
                continue

        return epics

    def _extract_features(self) -> list[Concept]:
        """Extract features from epic scope files.

        Returns:
            List of feature Concept objects.
        """
        from raise_cli.governance.parsers.epic import extract_features

        features: list[Concept] = []

        # Find epic scope files
        for epic_path in self._find_epic_scopes():
            try:
                extracted = extract_features(epic_path, self.project_root)
                features.extend(extracted)
            except Exception:
                continue

        return features

    def _find_backlogs(self) -> list[Path]:
        """Find backlog.md files in project.

        Returns:
            List of paths to backlog files.
        """
        backlogs: list[Path] = []

        # Check governance/projects/*/backlog.md
        projects_dir = self.project_root / "governance" / "projects"
        if projects_dir.exists():
            backlogs.extend(projects_dir.glob("*/backlog.md"))

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

            # Find matching session by topic/feature reference
            for candidate in nodes:
                if candidate.type != "session":
                    continue

                # Check if session topic mentions the feature
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
        """Infer part_of edges from feature to epic.

        Args:
            nodes: All concept nodes.
            node_by_id: Lookup dict by node ID.

        Returns:
            List of part_of edges.
        """
        edges: list[ConceptEdge] = []

        for node in nodes:
            if node.type != "feature":
                continue

            # Extract epic ID from feature ID (e.g., F11.2 -> E11)
            feature_id = node.id
            if feature_id.startswith("F"):
                # Parse epic number from feature ID
                parts = feature_id[1:].split(".")
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
            # Filter short words and common stopwords
            stopwords = {
                "the",
                "a",
                "an",
                "is",
                "are",
                "was",
                "were",
                "be",
                "been",
                "being",
                "have",
                "has",
                "had",
                "do",
                "does",
                "did",
                "will",
                "would",
                "could",
                "should",
                "may",
                "might",
                "must",
                "shall",
                "can",
                "need",
                "dare",
                "ought",
                "used",
                "to",
                "of",
                "in",
                "for",
                "on",
                "with",
                "at",
                "by",
                "from",
                "as",
                "into",
                "through",
                "during",
                "before",
                "after",
                "above",
                "below",
                "between",
                "under",
                "again",
                "further",
                "then",
                "once",
                "and",
                "but",
                "or",
                "nor",
                "so",
                "yet",
                "both",
                "either",
                "neither",
                "not",
                "only",
                "own",
                "same",
                "than",
                "too",
                "very",
                "just",
                "also",
                "now",
                "here",
                "there",
                "when",
                "where",
                "why",
                "how",
                "all",
                "each",
                "every",
                "few",
                "more",
                "most",
                "other",
                "some",
                "such",
                "no",
                "any",
                "this",
                "that",
                "these",
                "those",
                "it",
                "its",
            }
            for word in words:
                # Clean word
                clean = "".join(c for c in word if c.isalnum())
                if len(clean) >= 4 and clean not in stopwords:
                    keywords.add(clean)

        # From context metadata (for patterns)
        context_value: Any = node.metadata.get("context", [])
        if isinstance(context_value, list):
            context_list = cast(list[Any], context_value)
            for ctx in context_list:
                if isinstance(ctx, str):
                    keywords.add(ctx.lower())

        return keywords
