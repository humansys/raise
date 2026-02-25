"""Governance concept extractor orchestrator.

Coordinates multiple parsers to extract concepts from governance files.
Supports two paths:
- extract_all() → registry-based, returns list[GraphNode] (new)
- extract_with_result() → legacy direct imports, returns ExtractionResult (backward compat)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from rai_cli.adapters.models import ArtifactLocator, CoreArtifactType
from rai_cli.context.models import GraphNode
from rai_cli.governance.models import Concept, ConceptType, ExtractionResult

# Legacy imports — used only by extract_with_result() and extract_from_file()
from rai_cli.governance.parsers.adr import extract_all_decisions
from rai_cli.governance.parsers.backlog import extract_epics, extract_project
from rai_cli.governance.parsers.constitution import extract_principles
from rai_cli.governance.parsers.epic import extract_epic_details, extract_stories
from rai_cli.governance.parsers.glossary import extract_all_terms
from rai_cli.governance.parsers.guardrails import extract_all_guardrails
from rai_cli.governance.parsers.prd import extract_requirements
from rai_cli.governance.parsers.roadmap import extract_releases
from rai_cli.governance.parsers.vision import extract_outcomes

logger = logging.getLogger(__name__)


class GovernanceExtractor:
    """Orchestrates extraction of concepts from governance markdown files.

    Two extraction paths:
    - extract_all(): Uses registry-discovered parsers, returns list[GraphNode].
    - extract_with_result(): Legacy path with direct imports, returns ExtractionResult
      with list[Concept]. Maintained for backward compat with ``rai memory extract`` CLI.

    Attributes:
        project_root: Project root directory for relative path calculation.

    Examples:
        >>> from pathlib import Path
        >>> extractor = GovernanceExtractor()
        >>> nodes = extractor.extract_all()
        >>> len(nodes) >= 20
        True
    """

    def __init__(
        self,
        project_root: Path | None = None,
        parsers: dict[str, type] | None = None,
    ) -> None:
        """Initialize the governance extractor.

        Args:
            project_root: Project root directory. If None, uses current directory.
            parsers: Optional parser classes for DI/testing. If None, discovers
                via entry points at call time.
        """
        self.project_root = project_root or Path.cwd()
        self._parser_classes = parsers

    # --- New registry path ---

    def extract_all(self) -> list[GraphNode]:
        """Extract all governance concepts via registry parsers.

        Builds ArtifactLocators for known artifact locations, discovers
        parsers via entry points, and delegates parsing to matching parsers.

        Returns:
            List of GraphNode from all governance artifacts.
        """
        locators = self._build_locators()
        parser_classes = self._get_parser_classes()

        # Instantiate parser classes
        parsers: list[Any] = []
        for name, cls in parser_classes.items():
            try:
                parsers.append(cls())
            except Exception as exc:  # noqa: BLE001
                logger.warning("Failed to instantiate parser '%s': %s", name, exc)

        nodes: list[GraphNode] = []
        for locator in locators:
            parser = self._find_parser(locator, parsers)
            if parser is None:
                logger.debug(
                    "No parser found for artifact type '%s' at '%s'",
                    locator.artifact_type,
                    locator.path,
                )
                continue
            try:
                result = parser.parse(locator)
                nodes.extend(result)
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "Error parsing '%s' with %s: %s",
                    locator.path,
                    type(parser).__name__,
                    exc,
                )

        return nodes

    def _build_locators(self) -> list[ArtifactLocator]:
        """Build ArtifactLocators for all known governance artifact locations.

        Hardcodes paths (same locations as the legacy path). For ADR and
        epic_scope, globs to produce one locator per file.

        Returns:
            List of ArtifactLocators for existing files.
        """
        root = self.project_root
        meta = {"project_root": str(root)}
        locators: list[ArtifactLocator] = []

        # Single-file artifacts
        single_files: list[tuple[str, str]] = [
            (CoreArtifactType.PRD, "governance/prd.md"),
            (CoreArtifactType.VISION, "governance/vision.md"),
            (CoreArtifactType.CONSTITUTION, "framework/reference/constitution.md"),
            (CoreArtifactType.ROADMAP, "governance/roadmap.md"),
            (CoreArtifactType.BACKLOG, "governance/backlog.md"),
            (CoreArtifactType.GUARDRAILS, "governance/guardrails.md"),
            (CoreArtifactType.GLOSSARY, "framework/reference/glossary.md"),
        ]

        for artifact_type, rel_path in single_files:
            if (root / rel_path).exists():
                locators.append(
                    ArtifactLocator(
                        path=rel_path,
                        artifact_type=artifact_type,
                        metadata=dict(meta),
                    )
                )

        # ADR files — one locator per file (two directories)
        for adr_dir in ["dev/decisions", "dev/decisions/v2"]:
            full_dir = root / adr_dir
            if full_dir.exists():
                for adr_file in sorted(full_dir.glob("adr-*.md")):
                    rel = str(adr_file.relative_to(root))
                    locators.append(
                        ArtifactLocator(
                            path=rel,
                            artifact_type=CoreArtifactType.ADR,
                            metadata=dict(meta),
                        )
                    )

        # Epic scope files — one locator per scope.md
        for scope_file in sorted(root.glob("work/epics/*/scope.md")):
            rel = str(scope_file.relative_to(root))
            locators.append(
                ArtifactLocator(
                    path=rel,
                    artifact_type=CoreArtifactType.EPIC_SCOPE,
                    metadata=dict(meta),
                )
            )

        return locators

    def _find_parser(self, locator: ArtifactLocator, parsers: list[Any]) -> Any | None:
        """Find first parser that can_parse this locator."""
        for parser in parsers:
            if parser.can_parse(locator):
                return parser
        return None

    def _get_parser_classes(self) -> dict[str, type]:
        """Get parser classes from DI or entry point discovery."""
        if self._parser_classes is not None:
            return self._parser_classes

        from rai_cli.adapters.registry import get_governance_parsers

        return get_governance_parsers()

    # --- Legacy path (backward compat) ---

    def extract_from_file(
        self, file_path: Path, concept_type: ConceptType | None = None
    ) -> list[Concept]:
        """Extract concepts from a single governance file.

        Args:
            file_path: Path to governance markdown file.
            concept_type: Type of concepts to extract. If None, infers from file path.

        Returns:
            List of extracted concepts.

        Raises:
            ValueError: If concept_type is None and cannot be inferred from file path.
        """
        if not file_path.exists():
            logger.warning(f"File not found, skipping: {file_path}")
            return []

        if concept_type is None:
            concept_type = self._infer_concept_type(file_path)

        if concept_type == ConceptType.REQUIREMENT:
            return extract_requirements(file_path, self.project_root)
        elif concept_type == ConceptType.OUTCOME:
            return extract_outcomes(file_path, self.project_root)
        elif concept_type == ConceptType.PRINCIPLE:
            return extract_principles(file_path, self.project_root)
        else:
            logger.warning(f"Unsupported concept type: {concept_type}")
            return []

    def extract_with_result(self) -> ExtractionResult:
        """Extract all concepts and return detailed result.

        Legacy path: uses direct parser imports, returns ExtractionResult
        with list[Concept]. Maintained for ``rai memory extract`` CLI which
        depends on Concept fields (file, section, lines).

        Returns:
            ExtractionResult with concepts, counts, and errors.
        """
        concepts: list[Concept] = []
        errors: list[str] = []
        files_processed = 0

        # Extract from PRD
        prd_file = self.project_root / "governance" / "prd.md"
        if prd_file.exists():
            try:
                prd_concepts = extract_requirements(prd_file, self.project_root)
                concepts.extend(prd_concepts)
                files_processed += 1
            except Exception as e:
                errors.append(f"Error extracting from {prd_file}: {e}")

        # Extract from Vision
        vision_file = self.project_root / "governance" / "vision.md"
        if vision_file.exists():
            try:
                vision_concepts = extract_outcomes(vision_file, self.project_root)
                concepts.extend(vision_concepts)
                files_processed += 1
            except Exception as e:
                errors.append(f"Error extracting from {vision_file}: {e}")

        # Extract from Constitution
        constitution_file = (
            self.project_root / "framework" / "reference" / "constitution.md"
        )
        if constitution_file.exists():
            try:
                constitution_concepts = extract_principles(
                    constitution_file, self.project_root
                )
                concepts.extend(constitution_concepts)
                files_processed += 1
            except Exception as e:
                errors.append(f"Error extracting from {constitution_file}: {e}")

        # Extract work concepts (E8)
        work_concepts = self._extract_work_concepts()
        concepts.extend(work_concepts)
        backlog_file = self.project_root / "governance" / "backlog.md"
        backlog_count = 1 if backlog_file.exists() else 0
        epic_count = len(list(self.project_root.glob("work/epics/*/scope.md")))
        files_processed += backlog_count + epic_count

        # Extract ADR decisions (E12)
        try:
            adr_concepts = extract_all_decisions(self.project_root)
            concepts.extend(adr_concepts)
            adr_root_count = len(list(self.project_root.glob("dev/decisions/adr-*.md")))
            adr_v2_count = len(
                list(self.project_root.glob("dev/decisions/v2/adr-*.md"))
            )
            files_processed += adr_root_count + adr_v2_count
        except Exception as e:
            errors.append(f"Error extracting ADRs: {e}")

        # Extract Guardrails (E12 F12.2)
        guardrails_file = self.project_root / "governance" / "guardrails.md"
        if guardrails_file.exists():
            try:
                guardrail_concepts = extract_all_guardrails(self.project_root)
                concepts.extend(guardrail_concepts)
                files_processed += 1
            except Exception as e:
                errors.append(f"Error extracting guardrails: {e}")

        # Extract Glossary terms (E12 F12.3)
        glossary_file = self.project_root / "framework" / "reference" / "glossary.md"
        if glossary_file.exists():
            try:
                term_concepts = extract_all_terms(self.project_root)
                concepts.extend(term_concepts)
                files_processed += 1
            except Exception as e:
                errors.append(f"Error extracting glossary terms: {e}")

        # Extract Releases from roadmap
        roadmap_file = self.project_root / "governance" / "roadmap.md"
        if roadmap_file.exists():
            try:
                release_concepts = extract_releases(roadmap_file, self.project_root)
                concepts.extend(release_concepts)
                files_processed += 1
            except Exception as e:
                errors.append(f"Error extracting from {roadmap_file}: {e}")

        return ExtractionResult(
            concepts=concepts,
            total=len(concepts),
            files_processed=files_processed,
            errors=errors,
        )

    def _extract_work_concepts(self) -> list[Concept]:
        """Extract work tracking concepts (Project, Epic, Story).

        Extracts from:
        - governance/backlog.md (Project + Epic index)
        - work/epics/*/scope.md (Epic details + Stories)

        Returns:
            List of work tracking concepts.
        """
        concepts: list[Concept] = []

        backlog_file = self.project_root / "governance" / "backlog.md"
        if backlog_file.exists():
            try:
                project = extract_project(backlog_file, self.project_root)
                if project:
                    concepts.append(project)
                    logger.info(f"Extracted project from {backlog_file.name}")

                epic_index = extract_epics(backlog_file, self.project_root)
                concepts.extend(epic_index)
                logger.info(
                    f"Extracted {len(epic_index)} epics from {backlog_file.name}"
                )
            except Exception as e:
                logger.error(f"Error extracting from {backlog_file}: {e}")

        for scope_file in self.project_root.glob("work/epics/*/scope.md"):
            try:
                epic_detail = extract_epic_details(scope_file, self.project_root)
                if epic_detail:
                    existing = next(
                        (c for c in concepts if c.id == epic_detail.id), None
                    )
                    if existing:
                        existing.metadata.update(epic_detail.metadata)
                        existing.content = epic_detail.content
                    else:
                        concepts.append(epic_detail)
                    logger.info(f"Extracted epic details from {scope_file.name}")

                stories = extract_stories(scope_file, self.project_root)
                concepts.extend(stories)
                logger.info(f"Extracted {len(stories)} stories from {scope_file.name}")
            except Exception as e:
                logger.error(f"Error extracting from {scope_file}: {e}")

        return concepts

    def _infer_concept_type(self, file_path: Path) -> ConceptType:
        """Infer concept type from file path.

        Args:
            file_path: Path to governance file.

        Returns:
            Inferred concept type.

        Raises:
            ValueError: If concept type cannot be inferred.
        """
        file_name = file_path.name.lower()

        if "prd" in file_name or "requirements" in file_name:
            return ConceptType.REQUIREMENT
        elif "vision" in file_name:
            return ConceptType.OUTCOME
        elif "constitution" in file_name:
            return ConceptType.PRINCIPLE
        elif "backlog" in file_name:
            return ConceptType.PROJECT
        elif "epic" in file_name and "scope" in file_name:
            return ConceptType.EPIC
        elif "guardrails" in file_name:
            return ConceptType.GUARDRAIL
        elif "glossary" in file_name:
            return ConceptType.TERM
        elif "roadmap" in file_name:
            return ConceptType.RELEASE
        else:
            raise ValueError(
                f"Cannot infer concept type from file path: {file_path}. "
                f"Specify concept_type explicitly."
            )
