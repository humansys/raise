"""Governance concept extractor orchestrator.

Coordinates multiple parsers to extract concepts from governance files.
Supports two paths:
- extract_all() → registry-based, returns list[GraphNode] (new)
- extract_with_result() → legacy direct imports, returns ExtractionResult (backward compat)
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any, NamedTuple

from raise_cli.adapters.models import ArtifactLocator, CoreArtifactType
from raise_cli.governance.models import Concept, ConceptType, ExtractionResult

# Legacy imports — used only by extract_with_result() and extract_from_file()
from raise_cli.governance.parsers.adr import extract_all_decisions
from raise_cli.governance.parsers.backlog import extract_epics, extract_project
from raise_cli.governance.parsers.constitution import extract_principles
from raise_cli.governance.parsers.epic import extract_epic_details, extract_stories
from raise_cli.governance.parsers.glossary import extract_all_terms
from raise_cli.governance.parsers.guardrails import extract_all_guardrails
from raise_cli.governance.parsers.prd import extract_requirements
from raise_cli.governance.parsers.roadmap import extract_releases
from raise_cli.governance.parsers.vision import extract_outcomes
from raise_core.graph.models import GraphNode

logger = logging.getLogger(__name__)

# Type aliases for extraction functions
_ExtractFn = Callable[[Path, Path], list[Concept]]
_RootExtractFn = Callable[[Path], list[Concept]]


class _SingleFileResult(NamedTuple):
    """Result from extracting concepts from a single file."""

    concepts: list[Concept]
    file_count: int
    errors: list[str]


def _extract_from_single_file(
    file_path: Path, extractor_fn: _ExtractFn, project_root: Path
) -> _SingleFileResult:
    """Extract concepts from a single governance file with error isolation.

    Args:
        file_path: Path to the governance file.
        extractor_fn: Function taking (file_path, project_root) -> list[Concept].
        project_root: Project root directory.

    Returns:
        Extraction result with concepts, file count, and any errors.
    """
    if not file_path.exists():
        return _SingleFileResult(concepts=[], file_count=0, errors=[])
    try:
        concepts = extractor_fn(file_path, project_root)
        return _SingleFileResult(concepts=concepts, file_count=1, errors=[])
    except Exception as e:  # noqa: BLE001 — error isolation: single file failure doesn't block others
        return _SingleFileResult(
            concepts=[],
            file_count=0,
            errors=[f"Error extracting from {file_path}: {e}"],
        )


def _extract_from_root_source(
    file_path: Path, extractor_fn: _RootExtractFn, project_root: Path
) -> _SingleFileResult:
    """Extract concepts using a root-based extractor with error isolation.

    For extractors that take project_root instead of file_path (e.g., guardrails, glossary).

    Args:
        file_path: Path to check for existence.
        extractor_fn: Function taking (project_root) -> list[Concept].
        project_root: Project root directory.

    Returns:
        Extraction result with concepts, file count, and any errors.
    """
    if not file_path.exists():
        return _SingleFileResult(concepts=[], file_count=0, errors=[])
    try:
        concepts = extractor_fn(project_root)
        return _SingleFileResult(concepts=concepts, file_count=1, errors=[])
    except Exception as e:  # noqa: BLE001 — error isolation: single file failure doesn't block others
        label = file_path.stem  # e.g., "guardrails", "glossary"
        return _SingleFileResult(
            concepts=[], file_count=0, errors=[f"Error extracting {label}: {e}"]
        )


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
            except Exception as exc:  # noqa: BLE001 — error isolation: skip broken parser, continue with others
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
            except Exception as exc:  # noqa: BLE001 — error isolation: malformed file skipped, other artifacts still extracted
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

        from raise_cli.adapters.registry import get_governance_parsers

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
        if concept_type == ConceptType.OUTCOME:
            return extract_outcomes(file_path, self.project_root)
        if concept_type == ConceptType.PRINCIPLE:
            return extract_principles(file_path, self.project_root)
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

        # Single-file extractions (PRD, Vision, Constitution, Roadmap)
        single_file_sources: list[tuple[Path, _ExtractFn]] = [
            (self.project_root / "governance" / "prd.md", extract_requirements),
            (self.project_root / "governance" / "vision.md", extract_outcomes),
            (
                self.project_root / "framework" / "reference" / "constitution.md",
                extract_principles,
            ),
            (self.project_root / "governance" / "roadmap.md", extract_releases),
        ]
        for file_path, extractor_fn in single_file_sources:
            result = _extract_from_single_file(
                file_path, extractor_fn, self.project_root
            )
            concepts.extend(result.concepts)
            files_processed += result.file_count
            errors.extend(result.errors)

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
        except (
            Exception
        ) as e:  # error isolation: ADR parse failure doesn't block other extractions
            errors.append(f"Error extracting ADRs: {e}")

        # Root-based extractions (Guardrails, Glossary)
        root_sources: list[tuple[Path, _RootExtractFn]] = [
            (
                self.project_root / "governance" / "guardrails.md",
                extract_all_guardrails,
            ),
            (
                self.project_root / "framework" / "reference" / "glossary.md",
                extract_all_terms,
            ),
        ]
        for file_path, root_fn in root_sources:
            result = _extract_from_root_source(file_path, root_fn, self.project_root)
            concepts.extend(result.concepts)
            files_processed += result.file_count
            errors.extend(result.errors)

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
            except Exception as e:  # error isolation: backlog parse failure doesn't block epic/story extraction
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
            except (
                Exception
            ) as e:  # error isolation: one broken scope.md doesn't block other epics
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
        if "vision" in file_name:
            return ConceptType.OUTCOME
        if "constitution" in file_name:
            return ConceptType.PRINCIPLE
        if "backlog" in file_name:
            return ConceptType.PROJECT
        if "epic" in file_name and "scope" in file_name:
            return ConceptType.EPIC
        if "guardrails" in file_name:
            return ConceptType.GUARDRAIL
        if "glossary" in file_name:
            return ConceptType.TERM
        if "roadmap" in file_name:
            return ConceptType.RELEASE
        raise ValueError(
            f"Cannot infer concept type from file path: {file_path}. "
            f"Specify concept_type explicitly."
        )
