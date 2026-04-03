"""Tests for MEMORY.md generation — agent-agnostic generator."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from raise_cli.onboarding.memory_md import MemoryMdGenerator, generate_memory_md

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
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
              └── {development_branch} (development)
                    └── epic/e{N}/{name}
                          └── story/s{N}.{M}/{name}
          flow:
            - Stories merge to epic branch
            - Epics merge to development branch ({development_branch})
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

    def test_generates_lifecycle_section(self, sample_methodology_yaml: Path) -> None:
        """Should include lifecycle flows from methodology."""
        gen = MemoryMdGenerator()
        result = gen.generate(methodology_path=sample_methodology_yaml)

        assert "## RaiSE Framework Process" in result
        assert "### Work Lifecycle" in result
        assert "/epic-start" in result
        assert "/story-start" in result
        assert "/session-start" in result

    def test_generates_skills_section(self, sample_methodology_yaml: Path) -> None:
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

    def test_generates_gates_section(self, sample_methodology_yaml: Path) -> None:
        """Should render blocking gates as table."""
        gen = MemoryMdGenerator()
        result = gen.generate(methodology_path=sample_methodology_yaml)

        assert "### Gate Requirements" in result
        assert "Epic branch exists" in result
        assert "Story branch and scope commit" in result

    def test_generates_principles_section(self, sample_methodology_yaml: Path) -> None:
        """Should list principles as numbered rules."""
        gen = MemoryMdGenerator()
        result = gen.generate(methodology_path=sample_methodology_yaml)

        assert "## Critical Process Rules" in result
        assert "TDD Always" in result
        assert "Commit After Task" in result

    def test_generates_branches_section(self, sample_methodology_yaml: Path) -> None:
        """Should include branch model."""
        gen = MemoryMdGenerator()
        result = gen.generate(methodology_path=sample_methodology_yaml)

        assert "## Branch Model" in result
        assert "main (stable)" in result
        assert "Stories merge to epic branch" in result

    def test_branches_substitutes_development_branch(
        self, sample_methodology_yaml: Path
    ) -> None:
        """Should replace {development_branch} placeholder with given branch name."""
        gen = MemoryMdGenerator()
        result = gen.generate(
            methodology_path=sample_methodology_yaml,
            development_branch="develop",
        )

        assert "develop (development)" in result
        assert "development branch (develop)" in result
        assert "{development_branch}" not in result

    def test_branches_defaults_to_main(self, sample_methodology_yaml: Path) -> None:
        """Should default development_branch to 'main' when not provided."""
        gen = MemoryMdGenerator()
        result = gen.generate(methodology_path=sample_methodology_yaml)

        assert "main (development)" in result
        assert "{development_branch}" not in result

    def test_skills_count_in_header(self, sample_methodology_yaml: Path) -> None:
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
        assert "rai graph build" in result


# =============================================================================
# Fixtures for Part 2
# =============================================================================


@pytest.fixture
def sample_patterns_jsonl(tmp_path: Path) -> Path:
    """Create a sample patterns.jsonl for testing."""
    import json

    patterns = [
        {
            "id": "PAT-001",
            "type": "process",
            "content": "TDD cycle yields higher quality",
            "context": ["testing", "quality"],
            "created": "2026-01-31",
        },
        {
            "id": "PAT-002",
            "type": "codebase",
            "content": "Singleton pattern for module state",
            "context": ["architecture"],
            "created": "2026-02-01",
        },
        {
            "id": "PAT-003",
            "type": "process",
            "content": "Commit after each task enables recovery",
            "context": ["git", "workflow"],
            "created": "2026-02-02",
        },
    ]
    path = tmp_path / "patterns.jsonl"
    path.write_text("\n".join(json.dumps(p) for p in patterns) + "\n")
    return path


# =============================================================================
# Part 2 Tests — Patterns → Markdown
# =============================================================================


class TestMemoryMdGeneratorPart2:
    """Tests for Part 2: patterns.jsonl → markdown."""

    def test_renders_patterns(
        self, sample_methodology_yaml: Path, sample_patterns_jsonl: Path
    ) -> None:
        """Should render patterns with ID and content."""
        gen = MemoryMdGenerator()
        result = gen.generate(
            methodology_path=sample_methodology_yaml,
            patterns_path=sample_patterns_jsonl,
        )

        assert "## Key Patterns" in result
        assert "**PAT-001:**" in result
        assert "TDD cycle yields higher quality" in result
        assert "**PAT-003:**" in result

    def test_limits_patterns_to_max(
        self, sample_methodology_yaml: Path, tmp_path: Path
    ) -> None:
        """Should only include max_patterns most recent."""
        import json

        patterns = [
            {"id": f"PAT-{i:03d}", "content": f"Pattern {i}", "created": "2026-01-01"}
            for i in range(1, 21)
        ]
        path = tmp_path / "patterns.jsonl"
        path.write_text("\n".join(json.dumps(p) for p in patterns) + "\n")

        gen = MemoryMdGenerator()
        result = gen.generate(
            methodology_path=sample_methodology_yaml,
            patterns_path=path,
            max_patterns=5,
        )

        # Should have the last 5 (PAT-016 through PAT-020)
        assert "PAT-020" in result
        assert "PAT-016" in result
        assert "PAT-001" not in result

    def test_empty_patterns_shows_placeholder(
        self, sample_methodology_yaml: Path, tmp_path: Path
    ) -> None:
        """Should show placeholder when patterns.jsonl is empty."""
        path = tmp_path / "patterns.jsonl"
        path.write_text("")

        gen = MemoryMdGenerator()
        result = gen.generate(
            methodology_path=sample_methodology_yaml,
            patterns_path=path,
        )

        assert "No patterns yet" in result

    def test_missing_patterns_file_shows_placeholder(
        self, sample_methodology_yaml: Path, tmp_path: Path
    ) -> None:
        """Should show placeholder when patterns.jsonl doesn't exist."""
        gen = MemoryMdGenerator()
        result = gen.generate(
            methodology_path=sample_methodology_yaml,
            patterns_path=tmp_path / "nonexistent.jsonl",
        )

        assert "No patterns yet" in result

    def test_no_patterns_path_shows_placeholder(
        self, sample_methodology_yaml: Path
    ) -> None:
        """Should show placeholder when no patterns_path provided."""
        gen = MemoryMdGenerator()
        result = gen.generate(
            methodology_path=sample_methodology_yaml,
            patterns_path=None,
        )

        assert "No patterns yet" in result


# =============================================================================
# Edge Cases / Graceful Degradation
# =============================================================================


class TestMemoryMdGeneratorEdgeCases:
    """Tests for graceful degradation."""

    def test_missing_methodology_still_generates(self, tmp_path: Path) -> None:
        """Should generate MEMORY.md even without methodology.yaml."""
        gen = MemoryMdGenerator()
        result = gen.generate(
            methodology_path=tmp_path / "nonexistent.yaml",
            project_name="fallback-project",
        )

        assert "# Rai Memory — fallback-project" in result
        assert "Key Patterns" in result
        assert "Last updated" in result

    def test_no_methodology_path_still_generates(self) -> None:
        """Should generate MEMORY.md when methodology_path is None."""
        gen = MemoryMdGenerator()
        result = gen.generate(methodology_path=None, project_name="test")

        assert "# Rai Memory — test" in result
        assert isinstance(result, str)

    def test_malformed_yaml_degrades_gracefully(self, tmp_path: Path) -> None:
        """Should handle invalid YAML without crashing."""
        bad_yaml = tmp_path / "bad.yaml"
        bad_yaml.write_text(": : : invalid yaml [[[")

        gen = MemoryMdGenerator()
        result = gen.generate(methodology_path=bad_yaml)

        # Should still produce output (header + footer at minimum)
        assert "# Rai Memory" in result

    def test_malformed_jsonl_skips_bad_lines(
        self, sample_methodology_yaml: Path, tmp_path: Path
    ) -> None:
        """Should skip invalid JSON lines without crashing."""
        path = tmp_path / "patterns.jsonl"
        path.write_text(
            '{"id": "PAT-001", "content": "Good pattern"}\n'
            "this is not json\n"
            '{"id": "PAT-002", "content": "Another good one"}\n'
        )

        gen = MemoryMdGenerator()
        result = gen.generate(
            methodology_path=sample_methodology_yaml,
            patterns_path=path,
        )

        assert "PAT-001" in result
        assert "PAT-002" in result

    def test_default_project_name(self, sample_methodology_yaml: Path) -> None:
        """Should use 'project' as default project name."""
        gen = MemoryMdGenerator()
        result = gen.generate(methodology_path=sample_methodology_yaml)

        assert "# Rai Memory — project" in result


# =============================================================================
# Convenience Function
# =============================================================================


class TestGenerateMemoryMd:
    """Tests for the generate_memory_md() convenience function."""

    def test_returns_string(self, sample_methodology_yaml: Path) -> None:
        """Should return markdown string."""
        result = generate_memory_md(
            methodology_path=sample_methodology_yaml,
            project_name="convenience-test",
        )

        assert isinstance(result, str)
        assert "# Rai Memory — convenience-test" in result

    def test_passes_all_args_through(
        self, sample_methodology_yaml: Path, sample_patterns_jsonl: Path
    ) -> None:
        """Should pass all arguments to the generator."""
        result = generate_memory_md(
            methodology_path=sample_methodology_yaml,
            patterns_path=sample_patterns_jsonl,
            project_name="full-test",
            max_patterns=2,
        )

        assert "# Rai Memory — full-test" in result
        assert "PAT-003" in result  # Most recent
        assert "PAT-002" in result  # Second most recent
        assert "PAT-001" not in result  # Excluded by max_patterns=2

    def test_passes_development_branch_through(
        self, sample_methodology_yaml: Path
    ) -> None:
        """Should pass development_branch to the generator."""
        result = generate_memory_md(
            methodology_path=sample_methodology_yaml,
            project_name="branch-test",
            development_branch="v2",
        )

        assert "v2 (development)" in result
        assert "{development_branch}" not in result
