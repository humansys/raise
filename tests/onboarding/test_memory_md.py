"""Tests for MEMORY.md generation — agent-agnostic generator."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from raise_cli.onboarding.memory_md import MemoryMdGenerator


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture()
def sample_methodology_yaml(tmp_path: Path) -> Path:
    """Create a minimal methodology.yaml for testing."""
    content = dedent("""\
        version: 1

        lifecycle:
          epic:
            phases: [start, design, plan, implement, close]
            flow: "/epic-start → /epic-design → /epic-plan → [stories] → /epic-close"
          story:
            phases: [start, design, plan, implement, review, close]
            flow: "/story-start → /story-design* → /story-plan → /story-implement → /story-review → /story-close"
            note: "*design optional for S/XS stories"
          session:
            phases: [start, work, close]
            flow: "/session-start → [work] → /session-close"

        skills:
          session:
            - name: /session-start
              purpose: Load memory and propose focus
              when: Beginning of session
            - name: /session-close
              purpose: Capture learnings
              when: End of session
          epic:
            - name: /epic-start
              purpose: Create epic branch
              when: Starting new epic
          story:
            - name: /story-start
              purpose: Create story branch
              when: Starting new story
          discovery:
            - name: /discover-start
              purpose: Initialize discovery
              when: Setting up discovery
          meta:
            - name: /skill-create
              purpose: Create new skills
              when: Adding automation
          other:
            - name: /research
              purpose: Rigorous research
              when: Before ADRs

        gates:
          blocking:
            - before: Epic design
              require: Epic branch exists
              enforced_by: /epic-start
              rationale: Features nest under epic branches
            - before: Story work
              require: Story branch and scope commit
              enforced_by: /story-start
              rationale: Traceability from first commit
          quality:
            - gate: Tests pass
              when: Before any commit
              rationale: TDD is non-negotiable

        principles:
          process:
            - name: TDD Always
              rule: RED-GREEN-REFACTOR, no exceptions
              rationale: Tests are specification
            - name: Commit After Task
              rule: Commit after each completed task
              rationale: Enables recovery
          collaboration:
            - name: Direct Communication
              rule: No praise-padding
              rationale: Efficiency
          technical:
            - name: Type Everything
              rule: Type annotations on all code
              rationale: Pyright strict

        branches:
          structure: |
            main (stable)
              └── v2 (development)
                    └── epic/e{N}/{name}
                          └── story/s{N}.{M}/{name}
          flow:
            - Stories merge to epic branch
            - Epics merge to development branch (v2)
            - Development merges to main at release
    """)
    methodology_path = tmp_path / "methodology.yaml"
    methodology_path.write_text(content)
    return methodology_path


# =============================================================================
# Part 1 Tests — Methodology → Markdown
# =============================================================================


class TestMemoryMdGeneratorPart1:
    """Tests for Part 1: methodology.yaml → markdown."""

    def test_generates_header_with_project_name(
        self, sample_methodology_yaml: Path
    ) -> None:
        """Should include project name in header."""
        gen = MemoryMdGenerator()
        result = gen.generate(
            methodology_path=sample_methodology_yaml,
            project_name="my-project",
        )

        assert "# Rai Memory — my-project" in result

    def test_generates_lifecycle_section(
        self, sample_methodology_yaml: Path
    ) -> None:
        """Should include lifecycle flows from methodology."""
        gen = MemoryMdGenerator()
        result = gen.generate(methodology_path=sample_methodology_yaml)

        assert "## RaiSE Framework Process" in result
        assert "### Work Lifecycle" in result
        assert "/epic-start" in result
        assert "/story-start" in result
        assert "/session-start" in result

    def test_generates_skills_section(
        self, sample_methodology_yaml: Path
    ) -> None:
        """Should list all skills by category."""
        gen = MemoryMdGenerator()
        result = gen.generate(methodology_path=sample_methodology_yaml)

        assert "## Available Skills" in result
        assert "### Session Skills" in result
        assert "### Epic Skills" in result
        assert "### Story Skills" in result
        assert "### Discovery Skills" in result
        assert "`/session-start`" in result
        assert "Load memory and propose focus" in result

    def test_generates_gates_section(
        self, sample_methodology_yaml: Path
    ) -> None:
        """Should render blocking gates as table."""
        gen = MemoryMdGenerator()
        result = gen.generate(methodology_path=sample_methodology_yaml)

        assert "### Gate Requirements" in result
        assert "Epic branch exists" in result
        assert "Story branch and scope commit" in result

    def test_generates_principles_section(
        self, sample_methodology_yaml: Path
    ) -> None:
        """Should list principles as numbered rules."""
        gen = MemoryMdGenerator()
        result = gen.generate(methodology_path=sample_methodology_yaml)

        assert "## Critical Process Rules" in result
        assert "TDD Always" in result
        assert "Commit After Task" in result

    def test_generates_branches_section(
        self, sample_methodology_yaml: Path
    ) -> None:
        """Should include branch model."""
        gen = MemoryMdGenerator()
        result = gen.generate(methodology_path=sample_methodology_yaml)

        assert "## Branch Model" in result
        assert "main (stable)" in result
        assert "Stories merge to epic branch" in result

    def test_skills_count_in_header(
        self, sample_methodology_yaml: Path
    ) -> None:
        """Should include total skills count."""
        gen = MemoryMdGenerator()
        result = gen.generate(methodology_path=sample_methodology_yaml)

        # 2 session + 1 epic + 1 story + 1 discovery + 1 meta + 1 other = 7
        assert "7 total" in result

    def test_returns_string(self, sample_methodology_yaml: Path) -> None:
        """Generator must return str, not write to files."""
        gen = MemoryMdGenerator()
        result = gen.generate(methodology_path=sample_methodology_yaml)

        assert isinstance(result, str)
        assert len(result) > 100

    def test_includes_footer_with_timestamp(
        self, sample_methodology_yaml: Path
    ) -> None:
        """Should include last updated timestamp."""
        gen = MemoryMdGenerator()
        result = gen.generate(methodology_path=sample_methodology_yaml)

        assert "*Last updated:" in result
        assert "raise memory generate" in result
