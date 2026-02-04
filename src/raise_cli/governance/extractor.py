"""Governance concept extractor orchestrator.

Coordinates multiple parsers to extract concepts from governance files.
"""

from __future__ import annotations

import logging
from pathlib import Path

from raise_cli.governance.models import Concept, ConceptType, ExtractionResult
from raise_cli.governance.parsers.adr import extract_all_decisions
from raise_cli.governance.parsers.backlog import extract_epics, extract_project
from raise_cli.governance.parsers.constitution import extract_principles
from raise_cli.governance.parsers.epic import extract_epic_details, extract_features
from raise_cli.governance.parsers.prd import extract_requirements
from raise_cli.governance.parsers.vision import extract_outcomes

logger = logging.getLogger(__name__)


class GovernanceExtractor:
    """Orchestrates extraction of concepts from governance markdown files.

    Coordinates multiple parsers to extract requirements, outcomes, and
    principles from their respective governance documents.

    Attributes:
        project_root: Project root directory for relative path calculation.

    Examples:
        >>> from pathlib import Path
        >>> extractor = GovernanceExtractor()
        >>> concepts = extractor.extract_all()
        >>> len(concepts) >= 20
        True
        >>> prd_concepts = extractor.extract_from_file(
        ...     Path("governance/projects/raise-cli/prd.md"),
        ...     ConceptType.REQUIREMENT
        ... )
    """

    def __init__(self, project_root: Path | None = None) -> None:
        """Initialize the governance extractor.

        Args:
            project_root: Project root directory. If None, uses current directory.
        """
        self.project_root = project_root or Path.cwd()

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

        Examples:
            >>> extractor = GovernanceExtractor()
            >>> prd_path = Path("governance/projects/raise-cli/prd.md")
            >>> concepts = extractor.extract_from_file(prd_path, ConceptType.REQUIREMENT)
        """
        if not file_path.exists():
            logger.warning(f"File not found, skipping: {file_path}")
            return []

        # Infer concept type from file path if not provided
        if concept_type is None:
            concept_type = self._infer_concept_type(file_path)

        # Route to appropriate parser
        if concept_type == ConceptType.REQUIREMENT:
            return extract_requirements(file_path, self.project_root)
        elif concept_type == ConceptType.OUTCOME:
            return extract_outcomes(file_path, self.project_root)
        elif concept_type == ConceptType.PRINCIPLE:
            return extract_principles(file_path, self.project_root)
        else:
            logger.warning(f"Unsupported concept type: {concept_type}")
            return []

    def extract_all(self) -> list[Concept]:
        """Extract all concepts from standard governance file locations.

        Extracts from:
        - governance/projects/*/prd.md (requirements)
        - governance/solution/vision.md (outcomes)
        - framework/reference/constitution.md (principles)

        Returns:
            List of all extracted concepts.

        Examples:
            >>> extractor = GovernanceExtractor()
            >>> all_concepts = extractor.extract_all()
            >>> len(all_concepts) >= 20
            True
        """
        concepts: list[Concept] = []
        errors: list[str] = []
        files_processed = 0

        # Standard file locations
        vision_file = self.project_root / "governance" / "solution" / "vision.md"
        constitution_file = (
            self.project_root / "framework" / "reference" / "constitution.md"
        )

        # Extract from PRD files (may be multiple projects)
        for prd_file in self.project_root.glob("governance/projects/*/prd.md"):
            try:
                prd_concepts = extract_requirements(prd_file, self.project_root)
                concepts.extend(prd_concepts)
                files_processed += 1
                logger.info(
                    f"Extracted {len(prd_concepts)} requirements from {prd_file.name}"
                )
            except Exception as e:
                error_msg = f"Error extracting from {prd_file}: {e}"
                logger.error(error_msg)
                errors.append(error_msg)

        # Extract from Vision
        if vision_file.exists():
            try:
                vision_concepts = extract_outcomes(vision_file, self.project_root)
                concepts.extend(vision_concepts)
                files_processed += 1
                logger.info(
                    f"Extracted {len(vision_concepts)} outcomes from {vision_file.name}"
                )
            except Exception as e:
                error_msg = f"Error extracting from {vision_file}: {e}"
                logger.error(error_msg)
                errors.append(error_msg)
        else:
            logger.warning(f"Vision file not found: {vision_file}")

        # Extract from Constitution
        if constitution_file.exists():
            try:
                constitution_concepts = extract_principles(
                    constitution_file, self.project_root
                )
                concepts.extend(constitution_concepts)
                files_processed += 1
                logger.info(
                    f"Extracted {len(constitution_concepts)} principles from {constitution_file.name}"
                )
            except Exception as e:
                error_msg = f"Error extracting from {constitution_file}: {e}"
                logger.error(error_msg)
                errors.append(error_msg)
        else:
            logger.warning(f"Constitution file not found: {constitution_file}")

        # Extract work concepts (E8)
        concepts.extend(self._extract_work_concepts())

        # Extract ADR decisions (E12)
        try:
            adr_concepts = extract_all_decisions(self.project_root)
            concepts.extend(adr_concepts)
            logger.info(f"Extracted {len(adr_concepts)} ADR decisions")
        except Exception as e:
            logger.error(f"Error extracting ADRs: {e}")

        return concepts

    def extract_with_result(self) -> ExtractionResult:
        """Extract all concepts and return detailed result.

        Returns:
            ExtractionResult with concepts, counts, and errors.

        Examples:
            >>> extractor = GovernanceExtractor()
            >>> result = extractor.extract_with_result()
            >>> result.total >= 20
            True
            >>> result.files_processed >= 3
            True
        """
        concepts: list[Concept] = []
        errors: list[str] = []
        files_processed = 0

        # Extract from PRD files
        for prd_file in self.project_root.glob("governance/projects/*/prd.md"):
            try:
                prd_concepts = extract_requirements(prd_file, self.project_root)
                concepts.extend(prd_concepts)
                files_processed += 1
            except Exception as e:
                errors.append(f"Error extracting from {prd_file}: {e}")

        # Extract from Vision
        vision_file = self.project_root / "governance" / "solution" / "vision.md"
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
        # Count backlog and epic scope files as processed
        backlog_count = len(
            list(self.project_root.glob("governance/projects/*/backlog.md"))
        )
        epic_count = len(list(self.project_root.glob("dev/epic-*-scope.md")))
        files_processed += backlog_count + epic_count

        # Extract ADR decisions (E12)
        try:
            adr_concepts = extract_all_decisions(self.project_root)
            concepts.extend(adr_concepts)
            # Count ADR files processed
            adr_root_count = len(list(self.project_root.glob("dev/decisions/adr-*.md")))
            adr_v2_count = len(
                list(self.project_root.glob("dev/decisions/v2/adr-*.md"))
            )
            files_processed += adr_root_count + adr_v2_count
        except Exception as e:
            errors.append(f"Error extracting ADRs: {e}")

        return ExtractionResult(
            concepts=concepts,
            total=len(concepts),
            files_processed=files_processed,
            errors=errors,
        )

    def _extract_work_concepts(self) -> list[Concept]:
        """Extract work tracking concepts (Project, Epic, Feature).

        Extracts from:
        - governance/projects/*/backlog.md (Project + Epic index)
        - dev/epic-*-scope.md (Epic details + Features)

        Returns:
            List of work tracking concepts.
        """
        concepts: list[Concept] = []

        # Extract from backlog files
        for backlog_file in self.project_root.glob("governance/projects/*/backlog.md"):
            try:
                # Extract Project concept
                project = extract_project(backlog_file, self.project_root)
                if project:
                    concepts.append(project)
                    logger.info(f"Extracted project from {backlog_file.name}")

                # Extract Epic index concepts
                epic_index = extract_epics(backlog_file, self.project_root)
                concepts.extend(epic_index)
                logger.info(
                    f"Extracted {len(epic_index)} epics from {backlog_file.name}"
                )
            except Exception as e:
                logger.error(f"Error extracting from {backlog_file}: {e}")

        # Extract from epic scope documents
        for scope_file in self.project_root.glob("dev/epic-*-scope.md"):
            try:
                # Extract detailed Epic concept
                epic_detail = extract_epic_details(scope_file, self.project_root)
                if epic_detail:
                    # Merge with index if exists, otherwise add
                    # (scope doc has more detail than backlog index)
                    existing = next(
                        (c for c in concepts if c.id == epic_detail.id), None
                    )
                    if existing:
                        # Update existing with scope doc details
                        existing.metadata.update(epic_detail.metadata)
                        existing.content = epic_detail.content
                    else:
                        concepts.append(epic_detail)
                    logger.info(f"Extracted epic details from {scope_file.name}")

                # Extract Feature concepts
                features = extract_features(scope_file, self.project_root)
                concepts.extend(features)
                logger.info(
                    f"Extracted {len(features)} features from {scope_file.name}"
                )
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
        else:
            raise ValueError(
                f"Cannot infer concept type from file path: {file_path}. "
                f"Specify concept_type explicitly."
            )
