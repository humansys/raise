"""Tests for workflow scaffolding — generates workflow shims for Antigravity."""

from __future__ import annotations

from pathlib import Path

import yaml

from raise_cli.config.agents import get_agent_config
from raise_cli.onboarding.workflows import WorkflowScaffoldResult, scaffold_workflows
from raise_cli.skills_base import DISTRIBUTABLE_SKILLS

TOTAL_SKILLS = len(DISTRIBUTABLE_SKILLS)


class TestScaffoldWorkflows:
    """Tests for scaffold_workflows() function."""

    def test_generates_all_workflows_for_antigravity(self, tmp_path: Path) -> None:
        """Should generate one workflow file per distributable skill."""
        config = get_agent_config("antigravity")
        result = scaffold_workflows(tmp_path, agent_config=config)

        workflows_dir = tmp_path / ".agent" / "workflows"
        for skill_name in DISTRIBUTABLE_SKILLS:
            assert (workflows_dir / f"{skill_name}.md").exists(), (
                f"Missing workflow: {skill_name}"
            )
        assert result.workflows_created == TOTAL_SKILLS

    def test_workflow_has_valid_yaml_frontmatter(self, tmp_path: Path) -> None:
        """Each workflow file should have parseable YAML frontmatter with name and description."""
        config = get_agent_config("antigravity")
        scaffold_workflows(tmp_path, agent_config=config)

        workflow_path = tmp_path / ".agent" / "workflows" / "rai-session-start.md"
        content = workflow_path.read_text()

        # Must start with YAML frontmatter
        assert content.startswith("---\n")

        # Parse frontmatter
        parts = content.split("---\n", 2)
        frontmatter = yaml.safe_load(parts[1])
        assert frontmatter["name"] == "rai-session-start"
        assert isinstance(frontmatter["description"], str)
        assert len(frontmatter["description"]) > 0

    def test_workflow_body_references_skill(self, tmp_path: Path) -> None:
        """Workflow body should reference the corresponding skill."""
        config = get_agent_config("antigravity")
        scaffold_workflows(tmp_path, agent_config=config)

        workflow_path = tmp_path / ".agent" / "workflows" / "rai-session-start.md"
        content = workflow_path.read_text()

        # Body after frontmatter should reference the skill
        parts = content.split("---\n", 2)
        body = parts[2].strip()
        assert "rai-session-start" in body
        assert ".agent/skills/rai-session-start/SKILL.md" in body

    def test_returns_files_created_list(self, tmp_path: Path) -> None:
        """Should return list of created file paths."""
        config = get_agent_config("antigravity")
        result = scaffold_workflows(tmp_path, agent_config=config)

        assert len(result.files_created) == TOTAL_SKILLS
        assert not result.already_existed
        assert not result.skipped_no_workflows_dir


class TestScaffoldWorkflowsNoOp:
    """Tests for scaffold_workflows() no-op when IDE has no workflows."""

    def test_noop_for_claude(self, tmp_path: Path) -> None:
        """Claude has no workflows_dir — should skip entirely."""
        config = get_agent_config("claude")
        result = scaffold_workflows(tmp_path, agent_config=config)

        assert result.workflows_created == 0
        assert result.skipped_no_workflows_dir
        assert not (tmp_path / ".agent" / "workflows").exists()

    def test_noop_default_is_claude(self, tmp_path: Path) -> None:
        """Default (no ide_config) should behave like Claude — no-op."""
        result = scaffold_workflows(tmp_path)

        assert result.workflows_created == 0
        assert result.skipped_no_workflows_dir


class TestScaffoldWorkflowsIdempotency:
    """Tests for workflow scaffolding being safe to run multiple times."""

    def test_does_not_overwrite_existing_workflows(self, tmp_path: Path) -> None:
        """Should not overwrite existing workflow files."""
        config = get_agent_config("antigravity")
        scaffold_workflows(tmp_path, agent_config=config)

        # Modify a workflow
        workflow_path = tmp_path / ".agent" / "workflows" / "rai-session-start.md"
        workflow_path.write_text("# Custom workflow")

        # Second scaffold
        result = scaffold_workflows(tmp_path, agent_config=config)

        assert workflow_path.read_text() == "# Custom workflow"
        assert "rai-session-start" in result.files_skipped

    def test_second_run_reports_already_existed(self, tmp_path: Path) -> None:
        """Second scaffold should report already_existed=True."""
        config = get_agent_config("antigravity")
        scaffold_workflows(tmp_path, agent_config=config)
        result = scaffold_workflows(tmp_path, agent_config=config)

        assert result.already_existed
        assert len(result.files_skipped) == TOTAL_SKILLS
        assert result.workflows_created == 0

    def test_creates_only_missing_workflows(self, tmp_path: Path) -> None:
        """Should create missing workflows when some already exist."""
        config = get_agent_config("antigravity")

        # Pre-create one workflow
        wf_dir = tmp_path / ".agent" / "workflows"
        wf_dir.mkdir(parents=True)
        (wf_dir / "rai-session-start.md").write_text("# Existing")

        result = scaffold_workflows(tmp_path, agent_config=config)

        assert "rai-session-start" in result.files_skipped
        assert result.workflows_created == TOTAL_SKILLS - 1


class TestWorkflowScaffoldResult:
    """Tests for WorkflowScaffoldResult model."""

    def test_default_values(self) -> None:
        """Should have sensible defaults."""
        result = WorkflowScaffoldResult()

        assert result.workflows_created == 0
        assert not result.already_existed
        assert not result.skipped_no_workflows_dir
        assert result.files_created == []
        assert result.files_skipped == []
