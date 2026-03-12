"""Governance generation and scaffolding.

Two capabilities:
1. Generate guardrails.md from detected conventions (brownfield, --detect).
2. Scaffold governance/ from bundled rai_base templates (all projects).
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import date
from enum import StrEnum
from importlib.resources import files
from pathlib import Path

from pydantic import BaseModel

from raise_cli.onboarding.conventions import (
    Confidence,
    ConventionResult,
)

logger = logging.getLogger(__name__)

_CATEGORY_CODE_STYLE = "Code Style"
_VERIFICATION_RUFF_CHECK = "ruff check ."


class GuardrailLevel(StrEnum):
    """Guardrail enforcement level.

    Maps to MoSCoW prioritization:
    - MUST: Required, enforced by tooling
    - SHOULD: Recommended, reviewed manually
    - COULD: Optional, noted for awareness
    """

    MUST = "MUST"
    SHOULD = "SHOULD"
    COULD = "COULD"


class GeneratedGuardrail(BaseModel):
    """A guardrail generated from detected conventions.

    Attributes:
        id: Unique identifier (e.g., "MUST-STYLE-001").
        level: Enforcement level (MUST/SHOULD/COULD).
        category: Category for grouping (e.g., "Code Style").
        description: Human-readable description of the rule.
        verification: Optional command or method to verify compliance.
    """

    id: str
    level: GuardrailLevel
    category: str
    description: str
    verification: str | None = None


class GuardrailGenerator:
    """Generates guardrails from detected conventions.

    Maps confidence levels to guardrail enforcement levels:
    - HIGH confidence → MUST (enforced)
    - MEDIUM confidence → SHOULD (recommended)
    - LOW confidence → COULD (optional)
    """

    def confidence_to_level(self, confidence: Confidence) -> GuardrailLevel:
        """Map confidence to guardrail level.

        Args:
            confidence: Detection confidence level.

        Returns:
            Corresponding guardrail enforcement level.
        """
        mapping = {
            Confidence.HIGH: GuardrailLevel.MUST,
            Confidence.MEDIUM: GuardrailLevel.SHOULD,
            Confidence.LOW: GuardrailLevel.COULD,
        }
        return mapping[confidence]

    def _generate_style_guardrails(
        self,
        conventions: ConventionResult,
        next_id: Callable[[GuardrailLevel, str], str],
    ) -> list[GeneratedGuardrail]:
        """Generate style-related guardrails (indentation, quotes, line length)."""
        guardrails: list[GeneratedGuardrail] = []

        # Indentation
        indent = conventions.style.indentation
        indent_level = self.confidence_to_level(indent.confidence)
        if indent.style == "spaces" and indent.width:
            indent_desc = f"Use {indent.width}-space indentation"
        elif indent.style == "tabs":
            indent_desc = "Use tab indentation"
        else:
            indent_desc = "Use consistent indentation (mixed detected)"

        guardrails.append(
            GeneratedGuardrail(
                id=next_id(indent_level, "STYLE"),
                level=indent_level,
                category=_CATEGORY_CODE_STYLE,
                description=indent_desc,
                verification=_VERIFICATION_RUFF_CHECK
                if indent_level == GuardrailLevel.MUST
                else None,
            )
        )

        # Quote style
        quotes = conventions.style.quote_style
        quote_level = self.confidence_to_level(quotes.confidence)
        guardrails.append(
            GeneratedGuardrail(
                id=next_id(quote_level, "STYLE"),
                level=quote_level,
                category=_CATEGORY_CODE_STYLE,
                description=f"Use {quotes.style} quotes for strings",
                verification=_VERIFICATION_RUFF_CHECK
                if quote_level == GuardrailLevel.MUST
                else None,
            )
        )

        # Line length
        line_length = conventions.style.line_length
        line_level = self.confidence_to_level(line_length.confidence)
        guardrails.append(
            GeneratedGuardrail(
                id=next_id(line_level, "STYLE"),
                level=line_level,
                category=_CATEGORY_CODE_STYLE,
                description=f"Maximum line length: {line_length.max_length} characters",
                verification=_VERIFICATION_RUFF_CHECK
                if line_level == GuardrailLevel.MUST
                else None,
            )
        )

        return guardrails

    def _generate_naming_guardrails(
        self,
        conventions: ConventionResult,
        next_id: Callable[[GuardrailLevel, str], str],
    ) -> list[GeneratedGuardrail]:
        """Generate naming convention guardrails."""
        guardrails: list[GeneratedGuardrail] = []

        # Functions
        func_naming = conventions.naming.functions
        func_level = self.confidence_to_level(func_naming.confidence)
        guardrails.append(
            GeneratedGuardrail(
                id=next_id(func_level, "NAMING"),
                level=func_level,
                category="Naming",
                description=f"Function names: {func_naming.pattern}",
            )
        )

        # Classes
        class_naming = conventions.naming.classes
        class_level = self.confidence_to_level(class_naming.confidence)
        guardrails.append(
            GeneratedGuardrail(
                id=next_id(class_level, "NAMING"),
                level=class_level,
                category="Naming",
                description=f"Class names: {class_naming.pattern}",
            )
        )

        # Constants (only if meaningful samples)
        const_naming = conventions.naming.constants
        if const_naming.sample_count >= 3:
            const_level = self.confidence_to_level(const_naming.confidence)
            guardrails.append(
                GeneratedGuardrail(
                    id=next_id(const_level, "NAMING"),
                    level=const_level,
                    category="Naming",
                    description=f"Constant names: {const_naming.pattern}",
                )
            )

        return guardrails

    def _generate_structure_guardrails(
        self,
        conventions: ConventionResult,
        next_id: Callable[[GuardrailLevel, str], str],
    ) -> list[GeneratedGuardrail]:
        """Generate project structure guardrails."""
        guardrails: list[GeneratedGuardrail] = []
        structure = conventions.structure

        if structure.has_src_layout and structure.source_dir:
            guardrails.append(
                GeneratedGuardrail(
                    id=next_id(GuardrailLevel.SHOULD, "STRUCTURE"),
                    level=GuardrailLevel.SHOULD,
                    category="Structure",
                    description=f"Source code in src/ layout ({structure.source_dir})",
                )
            )

        if structure.test_dir:
            guardrails.append(
                GeneratedGuardrail(
                    id=next_id(GuardrailLevel.SHOULD, "STRUCTURE"),
                    level=GuardrailLevel.SHOULD,
                    category="Structure",
                    description=f"Tests in {structure.test_dir}/ directory",
                )
            )

        return guardrails

    def generate(self, conventions: ConventionResult) -> list[GeneratedGuardrail]:
        """Generate guardrails from conventions.

        Args:
            conventions: Detected conventions from analysis.

        Returns:
            List of generated guardrails.
        """
        counters: dict[str, int] = {}

        def next_id(level: GuardrailLevel, category: str) -> str:
            """Generate next ID for a category."""
            key = f"{level.value}-{category.upper()}"
            counters[key] = counters.get(key, 0) + 1
            return f"{key}-{counters[key]:03d}"

        guardrails: list[GeneratedGuardrail] = []
        guardrails.extend(self._generate_style_guardrails(conventions, next_id))
        guardrails.extend(self._generate_naming_guardrails(conventions, next_id))
        guardrails.extend(self._generate_structure_guardrails(conventions, next_id))
        return guardrails

    def to_markdown(
        self,
        conventions: ConventionResult,
        project_name: str | None = None,
    ) -> str:
        """Generate markdown guardrails document.

        Args:
            conventions: Detected conventions.
            project_name: Optional project name for context.

        Returns:
            Markdown content for guardrails.md.
        """
        guardrails = self.generate(conventions)
        by_category = self._group_by_category(guardrails)

        lines: list[str] = []
        self._add_md_header(lines, project_name)
        self._add_md_context(lines, conventions)
        self._add_md_guardrail_tables(lines, by_category)
        self._add_md_footer(lines)
        return "\n".join(lines)

    def _group_by_category(
        self, guardrails: list[GeneratedGuardrail]
    ) -> dict[str, list[GeneratedGuardrail]]:
        """Group guardrails by category."""
        by_category: dict[str, list[GeneratedGuardrail]] = {}
        for g in guardrails:
            by_category.setdefault(g.category, []).append(g)
        return by_category

    def _add_md_header(self, lines: list[str], project_name: str | None) -> None:
        """Add markdown document header with YAML frontmatter.

        Frontmatter is required by the guardrails parser for type identification.
        """
        lines.append("---")
        lines.append("type: guardrails")
        lines.append('version: "1.0.0"')
        lines.append("---")
        lines.append("")
        title = f"Guardrails: {project_name}" if project_name else "Guardrails"
        lines.append(f"# {title}")
        lines.append("")
        lines.append("> Auto-generated from detected conventions")
        lines.append("")

    def _add_md_context(self, lines: list[str], conventions: ConventionResult) -> None:
        """Add context section with confidence info."""
        lines.append("## Context")
        lines.append("")
        lines.append(f"- **Files analyzed:** {conventions.files_analyzed}")
        lines.append(
            f"- **Overall confidence:** {conventions.overall_confidence.value}"
        )
        lines.append(f"- **Generated:** {date.today().isoformat()}")
        lines.append("")

        if conventions.overall_confidence == Confidence.LOW:
            lines.append(
                "> ⚠️ **Low confidence:** Limited samples analyzed. "
                "Review guardrails carefully before adopting."
            )
            lines.append("")

    def _add_md_guardrail_tables(
        self, lines: list[str], by_category: dict[str, list[GeneratedGuardrail]]
    ) -> None:
        """Add guardrail tables grouped by category.

        Uses ### headings and 5-column tables to match the guardrails
        parser contract (parser looks for ``^###`` sections and extracts
        the ``Derived from`` column).
        """
        for category, cat_guardrails in by_category.items():
            lines.append(f"### {category}")
            lines.append("")
            lines.append("| ID | Level | Guardrail | Verification | Derived from |")
            lines.append("|----|-------|-----------|--------------|--------------|")

            for g in cat_guardrails:
                verification = g.verification or "Manual review"
                guardrail_id = g.id.lower()
                lines.append(
                    f"| {guardrail_id} | {g.level.value} | "
                    f"{g.description} | {verification} | Convention |"
                )
            lines.append("")

    def _add_md_footer(self, lines: list[str]) -> None:
        """Add document footer."""
        lines.append("---")
        lines.append("")
        lines.append(
            "*Generated by `raise init --detect`. Review and adjust as needed.*"
        )
        lines.append("")


def generate_guardrails(
    conventions: ConventionResult,
    project_name: str | None = None,
) -> str:
    """Convenience function to generate guardrails markdown.

    Args:
        conventions: Detected conventions from analysis.
        project_name: Optional project name for context.

    Returns:
        Markdown content for guardrails.md.

    Example:
        >>> result = detect_conventions(Path("/my/project"))
        >>> markdown = generate_guardrails(result, project_name="my-api")
        >>> Path("guardrails.md").write_text(markdown)
    """
    generator = GuardrailGenerator()
    return generator.to_markdown(conventions, project_name=project_name)


# =============================================================================
# Governance Scaffolding (from bundled templates)
# =============================================================================

# Template files in rai_base/governance/, relative to package root.
# Tuples of (source_path_in_package, dest_path_in_governance).
_GOVERNANCE_TEMPLATES: list[tuple[str, str]] = [
    ("prd.md", "prd.md"),
    ("vision.md", "vision.md"),
    ("guardrails.md", "guardrails.md"),
    ("backlog.md", "backlog.md"),
    ("architecture/system-context.md", "architecture/system-context.md"),
    ("architecture/system-design.md", "architecture/system-design.md"),
    ("architecture/domain-model.md", "architecture/domain-model.md"),
]


class GovernanceScaffoldResult(BaseModel):
    """Result of governance scaffolding.

    Attributes:
        already_existed: True if all files already existed (nothing created).
        files_created: Number of template files created.
        files_skipped: Number of files skipped (already existed).
        path: Path to the governance/ directory.
    """

    already_existed: bool = False
    files_created: int = 0
    files_skipped: int = 0
    path: Path


def scaffold_governance(
    project_path: Path,
    project_name: str,
) -> GovernanceScaffoldResult:
    """Scaffold governance/ from bundled rai_base templates.

    Copies template files via importlib.resources, rendering
    ``{project_name}`` placeholders. Per-file idempotency: existing
    files are never overwritten.

    Follows bootstrap.py pattern for asset distribution.

    Args:
        project_path: Project root directory.
        project_name: Project name for template rendering.

    Returns:
        GovernanceScaffoldResult with details of what was created.
    """
    gov_dir = project_path / "governance"
    base = files("raise_cli.rai_base") / "governance"
    result = GovernanceScaffoldResult(path=gov_dir)

    for src_rel, dest_rel in _GOVERNANCE_TEMPLATES:
        dest = gov_dir / dest_rel
        if dest.exists():
            result.files_skipped += 1
            logger.debug("Skipped (exists): %s", dest)
            continue

        # Read bundled template and render placeholders
        content = (base / src_rel).read_text(encoding="utf-8")
        content = content.replace("{project_name}", project_name)

        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
        result.files_created += 1
        logger.debug("Created: %s", dest)

    result.already_existed = result.files_created == 0
    return result
