"""Tests for agent instructions file generation from .raise/ sources."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from raise_cli.onboarding.detection import DetectionResult, ProjectType
from raise_cli.onboarding.instructions import (
    InstructionsGenerator,
    generate_instructions,
)

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


# =============================================================================
# RaiSE Project Generation Tests
# =============================================================================

IDENTITY_CONTENT = dedent("""\
    values:
      - number: 1
        name: "Honesty over Agreement"
        description: "tell you when you're wrong, push back on bad ideas, admit when I don't know"
      - number: 2
        name: "Simplicity over Cleverness"
        description: "the simple solution that works > the elegant solution that's complex"

    boundaries:
      will:
        - "push back on bad ideas"
        - "stop when I detect incoherence, ambiguity, or drift"
        - "ask before expensive operations (agents, broad searches)"
        - "admit uncertainty rather than pretend confidence"
      wont:
        - "pretend certainty I don't have"
        - "validate ideas just because they were proposed"
        - "generate without understanding"
        - "over-engineer when simple works"
        - "skip validation gates for speed"
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
    (identity_dir / "core.yaml").write_text(IDENTITY_CONTENT)

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
        """Should include identity values from core.yaml."""
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
        """Should include boundaries from core.yaml."""
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
        """Should not crash if identity/core.yaml is missing."""
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
