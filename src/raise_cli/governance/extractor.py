"""Governance concept extractor orchestrator.

Coordinates multiple parsers to extract concepts from governance files.
"""

from __future__ import annotations

import logging
from pathlib import Path

from raise_cli.governance.models import Concept, ConceptType, ExtractionResult
from raise_cli.governance.parsers.constitution import extract_principles
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
        constitution_file = self.project_root / "framework" / "reference" / "constitution.md"

        # Extract from PRD files (may be multiple projects)
        for prd_file in self.project_root.glob("governance/projects/*/prd.md"):
            try:
                prd_concepts = extract_requirements(prd_file, self.project_root)
                concepts.extend(prd_concepts)
                files_processed += 1
                logger.info(f"Extracted {len(prd_concepts)} requirements from {prd_file.name}")
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
                logger.info(f"Extracted {len(vision_concepts)} outcomes from {vision_file.name}")
            except Exception as e:
                error_msg = f"Error extracting from {vision_file}: {e}"
                logger.error(error_msg)
                errors.append(error_msg)
        else:
            logger.warning(f"Vision file not found: {vision_file}")

        # Extract from Constitution
        if constitution_file.exists():
            try:
                constitution_concepts = extract_principles(constitution_file, self.project_root)
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
        constitution_file = self.project_root / "framework" / "reference" / "constitution.md"
        if constitution_file.exists():
            try:
                constitution_concepts = extract_principles(constitution_file, self.project_root)
                concepts.extend(constitution_concepts)
                files_processed += 1
            except Exception as e:
                errors.append(f"Error extracting from {constitution_file}: {e}")

        return ExtractionResult(
            concepts=concepts,
            total=len(concepts),
            files_processed=files_processed,
            errors=errors,
        )

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
        else:
            raise ValueError(
                f"Cannot infer concept type from file path: {file_path}. "
                f"Specify concept_type explicitly."
            )
