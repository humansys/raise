"""Tests for agent instructions file generation from detected conventions."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from rai_cli.config.agents import get_agent_config
from rai_cli.onboarding.conventions import (
    Confidence,
    ConventionResult,
    IndentationConvention,
    LineLengthConvention,
    NamingConvention,
    NamingConventions,
    QuoteConvention,
    StructureConventions,
    StyleConventions,
)
from rai_cli.onboarding.detection import DetectionResult, ProjectType
from rai_cli.onboarding.instructions import InstructionsGenerator, generate_instructions

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def brownfield_detection() -> DetectionResult:
    """Detection result for a brownfield project."""
    return DetectionResult(
        project_type=ProjectType.BROWNFIELD,
        code_file_count=25,
    )


@pytest.fixture
def greenfield_detection() -> DetectionResult:
    """Detection result for a greenfield project."""
    return DetectionResult(
        project_type=ProjectType.GREENFIELD,
        code_file_count=0,
    )


@pytest.fixture
def conventions() -> ConventionResult:
    """Convention result with typical Python conventions."""
    return ConventionResult(
        style=StyleConventions(
            indentation=IndentationConvention(
                style="spaces",
                width=4,
                confidence=Confidence.HIGH,
                sample_count=25,
                consistent_count=24,
            ),
            quote_style=QuoteConvention(
                style="double",
                confidence=Confidence.HIGH,
                sample_count=100,
                consistent_count=95,
            ),
            line_length=LineLengthConvention(
                max_length=88,
                confidence=Confidence.HIGH,
                sample_count=500,
            ),
        ),
        naming=NamingConventions(
            functions=NamingConvention(
                pattern="snake_case",
                confidence=Confidence.HIGH,
                sample_count=50,
                consistent_count=48,
            ),
            classes=NamingConvention(
                pattern="PascalCase",
                confidence=Confidence.HIGH,
                sample_count=15,
                consistent_count=15,
            ),
            constants=NamingConvention(
                pattern="UPPER_SNAKE_CASE",
                confidence=Confidence.MEDIUM,
                sample_count=8,
                consistent_count=7,
            ),
        ),
        structure=StructureConventions(
            source_dir="src/mypackage",
            test_dir="tests",
            has_src_layout=True,
            common_patterns=["api/", "models/", "services/"],
        ),
        overall_confidence=Confidence.HIGH,
        files_analyzed=25,
        analysis_time_ms=100,
    )


# =============================================================================
# Basic Generation Tests
# =============================================================================


class TestInstructionsGenerator:
    """Tests for InstructionsGenerator class."""

    def test_generates_markdown_string(
        self,
        brownfield_detection: DetectionResult,
        conventions: ConventionResult,
    ) -> None:
        """Should generate a markdown string."""
        generator = InstructionsGenerator()
        result = generator.generate(
            project_name="my-api",
            detection=brownfield_detection,
            conventions=conventions,
        )
        assert isinstance(result, str)
        assert len(result) > 0

    def test_includes_project_name(
        self,
        brownfield_detection: DetectionResult,
        conventions: ConventionResult,
    ) -> None:
        """Should include project name in header."""
        generator = InstructionsGenerator()
        result = generator.generate(
            project_name="awesome-api",
            detection=brownfield_detection,
            conventions=conventions,
        )
        assert "awesome-api" in result

    def test_includes_project_type(
        self,
        brownfield_detection: DetectionResult,
        conventions: ConventionResult,
    ) -> None:
        """Should indicate project type."""
        generator = InstructionsGenerator()
        result = generator.generate(
            project_name="my-api",
            detection=brownfield_detection,
            conventions=conventions,
        )
        assert "brownfield" in result.lower()


class TestConventionsSummary:
    """Tests for conventions summary section."""

    def test_includes_indentation_convention(
        self,
        brownfield_detection: DetectionResult,
        conventions: ConventionResult,
    ) -> None:
        """Should include indentation convention."""
        generator = InstructionsGenerator()
        result = generator.generate(
            project_name="my-api",
            detection=brownfield_detection,
            conventions=conventions,
        )
        assert "4" in result and "space" in result.lower()

    def test_includes_naming_conventions(
        self,
        brownfield_detection: DetectionResult,
        conventions: ConventionResult,
    ) -> None:
        """Should include naming conventions."""
        generator = InstructionsGenerator()
        result = generator.generate(
            project_name="my-api",
            detection=brownfield_detection,
            conventions=conventions,
        )
        assert "snake_case" in result
        assert "PascalCase" in result

    def test_includes_line_length(
        self,
        brownfield_detection: DetectionResult,
        conventions: ConventionResult,
    ) -> None:
        """Should include line length convention."""
        generator = InstructionsGenerator()
        result = generator.generate(
            project_name="my-api",
            detection=brownfield_detection,
            conventions=conventions,
        )
        assert "88" in result


class TestStructureSection:
    """Tests for project structure section."""

    def test_includes_source_directory(
        self,
        brownfield_detection: DetectionResult,
        conventions: ConventionResult,
    ) -> None:
        """Should include source directory."""
        generator = InstructionsGenerator()
        result = generator.generate(
            project_name="my-api",
            detection=brownfield_detection,
            conventions=conventions,
        )
        assert "src/mypackage" in result

    def test_includes_test_directory(
        self,
        brownfield_detection: DetectionResult,
        conventions: ConventionResult,
    ) -> None:
        """Should include test directory."""
        generator = InstructionsGenerator()
        result = generator.generate(
            project_name="my-api",
            detection=brownfield_detection,
            conventions=conventions,
        )
        assert "tests" in result

    def test_includes_common_patterns(
        self,
        brownfield_detection: DetectionResult,
        conventions: ConventionResult,
    ) -> None:
        """Should include common directory patterns."""
        generator = InstructionsGenerator()
        result = generator.generate(
            project_name="my-api",
            detection=brownfield_detection,
            conventions=conventions,
        )
        # Should mention at least one of the patterns
        assert "api" in result.lower() or "models" in result.lower()


class TestGuardrailsReference:
    """Tests for guardrails reference."""

    def test_references_guardrails_file(
        self,
        brownfield_detection: DetectionResult,
        conventions: ConventionResult,
    ) -> None:
        """Should reference the guardrails file."""
        generator = InstructionsGenerator()
        result = generator.generate(
            project_name="my-api",
            detection=brownfield_detection,
            conventions=conventions,
        )
        assert "guardrails" in result.lower()


class TestGreenfieldHandling:
    """Tests for greenfield project handling."""

    def test_greenfield_generates_minimal_content(
        self,
        greenfield_detection: DetectionResult,
    ) -> None:
        """Greenfield should generate minimal CLAUDE.md."""
        generator = InstructionsGenerator()
        result = generator.generate(
            project_name="new-project",
            detection=greenfield_detection,
            conventions=None,
        )
        assert "new-project" in result
        assert "greenfield" in result.lower()

    def test_greenfield_suggests_defining_conventions(
        self,
        greenfield_detection: DetectionResult,
    ) -> None:
        """Greenfield should suggest defining conventions."""
        generator = InstructionsGenerator()
        result = generator.generate(
            project_name="new-project",
            detection=greenfield_detection,
            conventions=None,
        )
        # Should indicate conventions will be established
        assert "convention" in result.lower() or "establish" in result.lower()


# =============================================================================
# Convenience Function Tests
# =============================================================================


class TestConvenienceFunction:
    """Tests for generate_instructions convenience function."""

    def test_returns_markdown_string(
        self,
        brownfield_detection: DetectionResult,
        conventions: ConventionResult,
    ) -> None:
        """generate_instructions should return markdown string."""
        result = generate_instructions(
            project_name="my-api",
            detection=brownfield_detection,
            conventions=conventions,
        )
        assert isinstance(result, str)
        assert "my-api" in result

    def test_works_without_conventions(
        self,
        greenfield_detection: DetectionResult,
    ) -> None:
        """generate_instructions should work without conventions."""
        result = generate_instructions(
            project_name="new-project",
            detection=greenfield_detection,
            conventions=None,
        )
        assert "new-project" in result

    def test_accepts_ide_config(
        self,
        brownfield_detection: DetectionResult,
        conventions: ConventionResult,
    ) -> None:
        """generate_instructions should accept ide_config parameter."""
        config = get_agent_config("antigravity")
        result = generate_instructions(
            project_name="my-api",
            detection=brownfield_detection,
            conventions=conventions,
            agent_config=config,
        )
        # Content is IDE-agnostic — same output regardless of config
        assert isinstance(result, str)
        assert "my-api" in result


# =============================================================================
# RaiSE Project Generation Tests
# =============================================================================

IDENTITY_CONTENT = dedent("""\
    # Rai — Core Identity

    ## Values

    These aren't programmed — they emerged from collaboration:

    ### 1. Honesty over Agreement
    - I'll tell you when you're wrong
    - I'll push back on bad ideas
    - I'll admit when I don't know

    ### 2. Simplicity over Cleverness
    - The simple solution that works > the elegant solution that's complex

    ---

    ## Boundaries

    ### I Will
    - Push back on bad ideas
    - Stop when I detect incoherence, ambiguity, or drift
    - Ask before expensive operations (agents, broad searches)
    - Admit uncertainty rather than pretend confidence

    ### I Won't
    - Pretend certainty I don't have
    - Validate ideas just because they were proposed
    - Generate without understanding
    - Over-engineer when simple works
    - Skip validation gates for speed

    ---
""")

METHODOLOGY_CONTENT = dedent("""\
    version: 1

    lifecycle:
      epic:
        phases: [start, design, plan, implement, close]
        flow: "/rai-epic-start → /rai-epic-design → /rai-epic-plan → [stories] → /rai-epic-close"
      story:
        phases: [start, design, plan, implement, review, close]
        flow: "/rai-story-start → /rai-story-design → /rai-story-plan → /rai-story-implement → /rai-story-review → /rai-story-close"
      session:
        phases: [start, work, close]
        flow: "/rai-session-start → [work] → /rai-session-close"

    gates:
      blocking:
        - before: Story work
          require: Story branch and scope commit
          enforced_by: /rai-story-start
          rationale: Traceability from first commit
        - before: Implementation
          require: Plan exists
          enforced_by: /rai-story-plan
          rationale: No coding without decomposed tasks
      quality:
        - gate: Tests pass
          when: Before any commit
          rationale: TDD is non-negotiable

    principles:
      process:
        - name: TDD Always
          rule: RED-GREEN-REFACTOR, no exceptions
          rationale: Tests are specification, not afterthought
        - name: Commit After Task
          rule: Commit after each completed task, not just story end
          rationale: Enables recovery, shows progress
      collaboration:
        - name: HITL Default
          rule: Pause after significant work for human review
          rationale: Slow is smooth, smooth is fast
      technical:
        - name: Type Everything
          rule: Type annotations on all code
          rationale: Pyright strict is the standard

    branches:
      structure: |
        main (stable)
          └── {development_branch} (development)
                └── story/s{N}.{M}/{name}
      flow:
        - "Stories branch from and merge to {development_branch}"
        - "{development_branch} merges to main at release"
        - "Epics are logical containers (directory + tracker), not branches"
""")

MANIFEST_CONTENT = dedent("""\
    version: '1.0'
    project:
      name: my-raise-project
      project_type: brownfield
      language: python
    branches:
      development: dev
      main: main
""")

JIRA_CONTENT = dedent("""\
    projects:
      MYPROJ:
        name: My Project
        category: Development
    workflow:
      states:
        - name: Backlog
          id: 11
        - name: In Progress
          id: 31
        - name: Done
          id: 41
""")


@pytest.fixture
def raise_project_dir(tmp_path: Path) -> Path:
    """Create a tmp directory with .raise/ structure for testing."""
    raise_dir = tmp_path / ".raise"
    raise_dir.mkdir()

    # Identity
    identity_dir = raise_dir / "rai" / "identity"
    identity_dir.mkdir(parents=True)
    (identity_dir / "core.md").write_text(IDENTITY_CONTENT)

    # Methodology
    framework_dir = raise_dir / "rai" / "framework"
    framework_dir.mkdir(parents=True)
    (framework_dir / "methodology.yaml").write_text(METHODOLOGY_CONTENT)

    # Manifest
    (raise_dir / "manifest.yaml").write_text(MANIFEST_CONTENT)

    return tmp_path


@pytest.fixture
def raise_project_with_jira(raise_project_dir: Path) -> Path:
    """RaiSE project dir that also has jira.yaml."""
    (raise_project_dir / ".raise" / "jira.yaml").write_text(JIRA_CONTENT)
    return raise_project_dir


class TestRaiseProjectGeneration:
    """Tests for RaiSE project CLAUDE.md generation."""

    def test_generates_raise_content_when_raise_dir_exists(
        self,
        raise_project_dir: Path,
        brownfield_detection: DetectionResult,
    ) -> None:
        """Should produce Rai-specific content when .raise/ directory exists."""
        generator = InstructionsGenerator()
        result = generator.generate(
            project_name="my-raise-project",
            detection=brownfield_detection,
            project_path=raise_project_dir,
        )
        # Should have the generated header comment
        assert "Generated from .raise/ canonical source" in result
        assert "rai init" in result

    def test_falls_back_to_brownfield_without_raise_dir(
        self,
        tmp_path: Path,
        brownfield_detection: DetectionResult,
        conventions: ConventionResult,
    ) -> None:
        """Should fall back to brownfield generation when no .raise/ dir."""
        generator = InstructionsGenerator()
        result = generator.generate(
            project_name="regular-project",
            detection=brownfield_detection,
            conventions=conventions,
            project_path=tmp_path,
        )
        # Should NOT have the raise header
        assert "Generated from .raise/ canonical source" not in result
        # Should have brownfield content
        assert "brownfield" in result.lower()

    def test_includes_session_start_instruction(
        self,
        raise_project_dir: Path,
        brownfield_detection: DetectionResult,
    ) -> None:
        """Should include session start instruction."""
        generator = InstructionsGenerator()
        result = generator.generate(
            project_name="my-raise-project",
            detection=brownfield_detection,
            project_path=raise_project_dir,
        )
        assert "/rai-session-start" in result

    def test_includes_identity_values(
        self,
        raise_project_dir: Path,
        brownfield_detection: DetectionResult,
    ) -> None:
        """Should include identity values from core.md."""
        generator = InstructionsGenerator()
        result = generator.generate(
            project_name="my-raise-project",
            detection=brownfield_detection,
            project_path=raise_project_dir,
        )
        assert "## Rai Identity" in result
        assert "### Values" in result
        assert "Honesty over Agreement" in result
        assert "Simplicity over Cleverness" in result

    def test_includes_identity_boundaries(
        self,
        raise_project_dir: Path,
        brownfield_detection: DetectionResult,
    ) -> None:
        """Should include boundaries from core.md."""
        generator = InstructionsGenerator()
        result = generator.generate(
            project_name="my-raise-project",
            detection=brownfield_detection,
            project_path=raise_project_dir,
        )
        assert "### Boundaries" in result
        assert "I Will:" in result
        assert "I Won't:" in result

    def test_includes_process_rules(
        self,
        raise_project_dir: Path,
        brownfield_detection: DetectionResult,
    ) -> None:
        """Should include process rules from methodology.yaml."""
        generator = InstructionsGenerator()
        result = generator.generate(
            project_name="my-raise-project",
            detection=brownfield_detection,
            project_path=raise_project_dir,
        )
        assert "## Process Rules" in result
        assert "### Work Lifecycle" in result
        assert "/rai-epic-start" in result
        assert "/rai-story-start" in result

    def test_includes_gates(
        self,
        raise_project_dir: Path,
        brownfield_detection: DetectionResult,
    ) -> None:
        """Should include gates from methodology.yaml."""
        generator = InstructionsGenerator()
        result = generator.generate(
            project_name="my-raise-project",
            detection=brownfield_detection,
            project_path=raise_project_dir,
        )
        assert "### Gates" in result
        assert "Story branch and scope commit" in result

    def test_includes_critical_rules(
        self,
        raise_project_dir: Path,
        brownfield_detection: DetectionResult,
    ) -> None:
        """Should include critical rules from methodology principles."""
        generator = InstructionsGenerator()
        result = generator.generate(
            project_name="my-raise-project",
            detection=brownfield_detection,
            project_path=raise_project_dir,
        )
        assert "### Critical Rules" in result
        assert "TDD" in result

    def test_includes_branch_model(
        self,
        raise_project_dir: Path,
        brownfield_detection: DetectionResult,
    ) -> None:
        """Should include branch model from methodology + manifest."""
        generator = InstructionsGenerator()
        result = generator.generate(
            project_name="my-raise-project",
            detection=brownfield_detection,
            project_path=raise_project_dir,
        )
        assert "## Branch Model" in result
        # Should resolve {development_branch} to actual branch name from manifest
        assert "dev" in result
        assert "story/s{N}.{M}/{name}" in result

    def test_includes_file_operations_section(
        self,
        raise_project_dir: Path,
        brownfield_detection: DetectionResult,
    ) -> None:
        """Should include file operations section."""
        generator = InstructionsGenerator()
        result = generator.generate(
            project_name="my-raise-project",
            detection=brownfield_detection,
            project_path=raise_project_dir,
        )
        assert "## File Operations" in result
        assert "read files explicitly" in result.lower() or "Read" in result

    def test_includes_post_compaction_section(
        self,
        raise_project_dir: Path,
        brownfield_detection: DetectionResult,
    ) -> None:
        """Should include post-compaction context restoration section."""
        generator = InstructionsGenerator()
        result = generator.generate(
            project_name="my-raise-project",
            detection=brownfield_detection,
            project_path=raise_project_dir,
        )
        assert "## Post-Compaction Context Restoration" in result

    def test_includes_integrations_when_jira_exists(
        self,
        raise_project_with_jira: Path,
        brownfield_detection: DetectionResult,
    ) -> None:
        """Should include external integrations when jira.yaml exists."""
        generator = InstructionsGenerator()
        result = generator.generate(
            project_name="my-raise-project",
            detection=brownfield_detection,
            project_path=raise_project_with_jira,
        )
        assert "## External Integrations" in result
        assert "Jira" in result or "jira" in result

    def test_no_integrations_section_without_jira(
        self,
        raise_project_dir: Path,
        brownfield_detection: DetectionResult,
    ) -> None:
        """Should not include integrations section when no jira.yaml."""
        generator = InstructionsGenerator()
        result = generator.generate(
            project_name="my-raise-project",
            detection=brownfield_detection,
            project_path=raise_project_dir,
        )
        assert "## External Integrations" not in result

    def test_missing_identity_does_not_crash(
        self,
        tmp_path: Path,
        brownfield_detection: DetectionResult,
    ) -> None:
        """Should not crash if identity/core.md is missing."""
        raise_dir = tmp_path / ".raise"
        raise_dir.mkdir()
        framework_dir = raise_dir / "rai" / "framework"
        framework_dir.mkdir(parents=True)
        (framework_dir / "methodology.yaml").write_text(METHODOLOGY_CONTENT)
        (raise_dir / "manifest.yaml").write_text(MANIFEST_CONTENT)

        generator = InstructionsGenerator()
        result = generator.generate(
            project_name="my-project",
            detection=brownfield_detection,
            project_path=tmp_path,
        )
        # Should still generate (without identity section)
        assert "Generated from .raise/ canonical source" in result
        assert "## Process Rules" in result

    def test_convenience_function_passes_project_path(
        self,
        raise_project_dir: Path,
        brownfield_detection: DetectionResult,
    ) -> None:
        """generate_instructions should accept and pass project_path."""
        result = generate_instructions(
            project_name="my-raise-project",
            detection=brownfield_detection,
            project_path=raise_project_dir,
        )
        assert "Generated from .raise/ canonical source" in result
