"""Tests for governance scaffolding from bundled templates."""

from __future__ import annotations

from pathlib import Path

import pytest

from raise_cli.onboarding.governance import (
    GovernanceScaffoldResult,
    scaffold_governance,
)

# =============================================================================
# Scaffold Function Tests
# =============================================================================


class TestScaffoldGovernance:
    """Tests for scaffold_governance() function."""

    def test_creates_governance_directory(self, tmp_path: Path) -> None:
        """Should create governance/ directory."""
        scaffold_governance(tmp_path, "test-project")

        assert (tmp_path / "governance").is_dir()

    def test_creates_prd_template(self, tmp_path: Path) -> None:
        """Should create governance/prd.md from bundled template."""
        scaffold_governance(tmp_path, "test-project")

        prd = tmp_path / "governance" / "prd.md"
        assert prd.exists()
        content = prd.read_text(encoding="utf-8")
        assert "# PRD: test-project" in content
        assert "### RF-01:" in content

    def test_creates_vision_template(self, tmp_path: Path) -> None:
        """Should create governance/vision.md from bundled template."""
        scaffold_governance(tmp_path, "test-project")

        vision = tmp_path / "governance" / "vision.md"
        assert vision.exists()
        content = vision.read_text(encoding="utf-8")
        assert "# Solution Vision: test-project" in content
        assert "| **Core Value**" in content

    def test_creates_guardrails_template(self, tmp_path: Path) -> None:
        """Should create governance/guardrails.md with YAML frontmatter."""
        scaffold_governance(tmp_path, "test-project")

        guardrails = tmp_path / "governance" / "guardrails.md"
        assert guardrails.exists()
        content = guardrails.read_text(encoding="utf-8")
        assert "type: guardrails" in content
        assert "# Guardrails: test-project" in content
        # Table structure present — rows populated by rai-project-onboard per tech stack
        assert "| ID | Level | Guardrail |" in content

    def test_creates_backlog_template(self, tmp_path: Path) -> None:
        """Should create governance/backlog.md from bundled template."""
        scaffold_governance(tmp_path, "test-project")

        backlog = tmp_path / "governance" / "backlog.md"
        assert backlog.exists()
        content = backlog.read_text(encoding="utf-8")
        assert "# Backlog: test-project" in content
        assert "**Status**: Draft" in content

    def test_creates_architecture_templates(self, tmp_path: Path) -> None:
        """Should create governance/architecture/ with system docs."""
        scaffold_governance(tmp_path, "test-project")

        arch_dir = tmp_path / "governance" / "architecture"
        assert arch_dir.is_dir()
        assert (arch_dir / "system-context.md").exists()
        assert (arch_dir / "system-design.md").exists()
        assert (arch_dir / "domain-model.md").exists()

    def test_renders_project_name(self, tmp_path: Path) -> None:
        """Should substitute {project_name} in all templates."""
        scaffold_governance(tmp_path, "my-awesome-api")

        for md_file in (tmp_path / "governance").rglob("*.md"):
            content = md_file.read_text(encoding="utf-8")
            assert "{project_name}" not in content, (
                f"{md_file.name} still contains unrendered placeholder"
            )
            assert "my-awesome-api" in content

    def test_returns_result_with_file_count(self, tmp_path: Path) -> None:
        """Should return GovernanceScaffoldResult with correct counts."""
        result = scaffold_governance(tmp_path, "test-project")

        assert isinstance(result, GovernanceScaffoldResult)
        assert result.files_created == 7
        assert result.files_skipped == 0
        assert not result.already_existed
        assert result.path == tmp_path / "governance"

    def test_total_files_created(self, tmp_path: Path) -> None:
        """Should create exactly 7 template files."""
        scaffold_governance(tmp_path, "test-project")

        md_files = list((tmp_path / "governance").rglob("*.md"))
        assert len(md_files) == 7


# =============================================================================
# Idempotency Tests
# =============================================================================


class TestScaffoldIdempotency:
    """Tests for per-file idempotency (follows bootstrap.py pattern)."""

    def test_does_not_overwrite_existing_files(self, tmp_path: Path) -> None:
        """Should not overwrite existing governance files."""
        # First scaffold
        scaffold_governance(tmp_path, "test-project")

        # Modify a file
        prd = tmp_path / "governance" / "prd.md"
        prd.write_text("# My Custom PRD\n")

        # Second scaffold
        result = scaffold_governance(tmp_path, "test-project")

        assert prd.read_text(encoding="utf-8") == "# My Custom PRD\n"
        assert result.files_skipped > 0

    def test_second_run_reports_already_existed(self, tmp_path: Path) -> None:
        """Second scaffold should report already_existed=True when all files exist."""
        scaffold_governance(tmp_path, "test-project")
        result = scaffold_governance(tmp_path, "test-project")

        assert result.already_existed
        assert result.files_created == 0
        assert result.files_skipped == 7

    def test_creates_missing_files_on_partial_state(self, tmp_path: Path) -> None:
        """Should create missing files when governance/ is partial."""
        # Create governance/ with only prd.md
        gov_dir = tmp_path / "governance"
        gov_dir.mkdir()
        (gov_dir / "prd.md").write_text("# Existing PRD\n")

        result = scaffold_governance(tmp_path, "test-project")

        # prd.md should be untouched
        assert (gov_dir / "prd.md").read_text(encoding="utf-8") == "# Existing PRD\n"
        # Other files should be created
        assert (gov_dir / "vision.md").exists()
        assert (gov_dir / "guardrails.md").exists()
        assert result.files_created == 6
        assert result.files_skipped == 1


# =============================================================================
# Result Model Tests
# =============================================================================


class TestGovernanceScaffoldResult:
    """Tests for GovernanceScaffoldResult Pydantic model."""

    def test_default_values(self) -> None:
        """Should have sensible defaults."""
        result = GovernanceScaffoldResult(path=Path("/tmp"))

        assert not result.already_existed
        assert result.files_created == 0
        assert result.files_skipped == 0


# =============================================================================
# Integration Test: M1 Gate (scaffold → build → verify nodes)
# =============================================================================


class TestScaffoldToBuildIntegration:
    """Integration test: scaffolded templates must produce governance nodes."""

    @pytest.fixture
    def scaffolded_project(self, tmp_path: Path) -> Path:
        """Create a project with scaffolded governance templates."""
        scaffold_governance(tmp_path, "test-project")
        return tmp_path

    def test_scaffold_then_build_produces_requirement_nodes(
        self, scaffolded_project: Path
    ) -> None:
        """Scaffolded prd.md should produce requirement nodes in graph."""
        from raise_cli.context.builder import GraphBuilder

        builder = GraphBuilder(scaffolded_project)
        graph = builder.build()

        requirements = graph.get_concepts_by_type("requirement")
        assert len(requirements) >= 1, (
            "Expected at least 1 requirement node from prd.md template"
        )
        # Verify RF-01 was extracted
        req_ids = {r.id for r in requirements}
        assert "req-rf-01" in req_ids

    def test_scaffold_then_build_produces_outcome_nodes(
        self, scaffolded_project: Path
    ) -> None:
        """Scaffolded vision.md should produce outcome nodes in graph."""
        from raise_cli.context.builder import GraphBuilder

        builder = GraphBuilder(scaffolded_project)
        graph = builder.build()

        outcomes = graph.get_concepts_by_type("outcome")
        assert len(outcomes) >= 1, (
            "Expected at least 1 outcome node from vision.md template"
        )

    def test_scaffold_then_build_produces_guardrail_nodes(
        self, scaffolded_project: Path
    ) -> None:
        """Guardrail nodes require rows added by rai-project-onboard, not just scaffold.

        The template provides table structure only — rows are tech-stack specific
        and filled by /rai-project-onboard (RAISE-219). We add a row manually here
        to test the graph builder pipeline independent of the template content.
        """
        from raise_cli.context.builder import GraphBuilder

        # Add a guardrail row — in real usage this is done by rai-project-onboard
        guardrails_path = scaffolded_project / "governance" / "guardrails.md"
        content = guardrails_path.read_text(encoding="utf-8")
        row = "| must-code-001 | MUST | Use consistent code style | linter | RF-01 |\n"
        guardrails_path.write_text(content + row, encoding="utf-8")

        builder = GraphBuilder(scaffolded_project)
        graph = builder.build()

        guardrails = graph.get_concepts_by_type("guardrail")
        assert len(guardrails) >= 1, (
            "Expected at least 1 guardrail node after adding a row"
        )

    def test_scaffold_then_build_m1_gate(self, scaffolded_project: Path) -> None:
        """M1 milestone gate: scaffold + onboard content → build → all 3 types present.

        Scaffold alone produces requirements and outcomes from templates.
        Guardrails require onboard to add tech-stack rows (RAISE-219).
        """
        from raise_cli.context.builder import GraphBuilder

        # Simulate onboard adding a guardrail row
        guardrails_path = scaffolded_project / "governance" / "guardrails.md"
        content = guardrails_path.read_text(encoding="utf-8")
        row = "| must-code-001 | MUST | Use consistent code style | linter | RF-01 |\n"
        guardrails_path.write_text(content + row, encoding="utf-8")

        builder = GraphBuilder(scaffolded_project)
        graph = builder.build()

        gov_types: set[str] = set()
        for node_type in ("requirement", "outcome", "guardrail"):
            nodes = graph.get_concepts_by_type(node_type)
            if nodes:
                gov_types.add(node_type)

        assert gov_types == {"requirement", "outcome", "guardrail"}, (
            f"M1 gate failed: expected all 3 governance types, got {gov_types}"
        )
