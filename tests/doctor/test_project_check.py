"""Tests for ProjectCheck — .raise/ structure and project coherence.

Architecture: S352.3
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from raise_cli.doctor.checks.project import ProjectCheck
from raise_cli.doctor.models import CheckResult, CheckStatus, DoctorContext


@pytest.fixture
def check() -> ProjectCheck:
    return ProjectCheck()


@pytest.fixture
def ctx(tmp_path: Path) -> DoctorContext:
    return DoctorContext(working_dir=tmp_path)


class TestRaiseDir:
    """Tests for .raise/ directory existence."""

    def test_missing_raise_dir_is_error(
        self, check: ProjectCheck, ctx: DoctorContext
    ) -> None:
        results = check.evaluate(ctx)
        raise_result = _find(results, "project-raise-dir")
        assert raise_result.status == CheckStatus.ERROR
        assert "missing" in raise_result.message
        assert raise_result.fix_hint == "run: rai init"

    def test_present_raise_dir_is_pass(
        self, check: ProjectCheck, ctx: DoctorContext
    ) -> None:
        (ctx.working_dir / ".raise").mkdir()
        results = check.evaluate(ctx)
        raise_result = _find(results, "project-raise-dir")
        assert raise_result.status == CheckStatus.PASS


class TestManifest:
    """Tests for manifest.yaml presence and validity."""

    def test_missing_manifest_is_error(
        self, check: ProjectCheck, ctx: DoctorContext
    ) -> None:
        (ctx.working_dir / ".raise").mkdir()
        results = check.evaluate(ctx)
        manifest_result = _find(results, "project-manifest")
        assert manifest_result.status == CheckStatus.ERROR
        assert "missing" in manifest_result.message

    def test_valid_manifest_is_pass(
        self, check: ProjectCheck, ctx: DoctorContext
    ) -> None:
        raise_dir = ctx.working_dir / ".raise"
        raise_dir.mkdir()
        (raise_dir / "manifest.yaml").write_text("name: test\nversion: 1.0\n")
        results = check.evaluate(ctx)
        manifest_result = _find(results, "project-manifest")
        assert manifest_result.status == CheckStatus.PASS

    def test_invalid_yaml_is_error(
        self, check: ProjectCheck, ctx: DoctorContext
    ) -> None:
        raise_dir = ctx.working_dir / ".raise"
        raise_dir.mkdir()
        (raise_dir / "manifest.yaml").write_text(": :\n  - ]: bad yaml {{{\n")
        results = check.evaluate(ctx)
        manifest_result = _find(results, "project-manifest")
        assert manifest_result.status == CheckStatus.ERROR
        assert "invalid YAML" in manifest_result.message

    def test_non_mapping_yaml_is_error(
        self, check: ProjectCheck, ctx: DoctorContext
    ) -> None:
        raise_dir = ctx.working_dir / ".raise"
        raise_dir.mkdir()
        (raise_dir / "manifest.yaml").write_text("- just\n- a\n- list\n")
        results = check.evaluate(ctx)
        manifest_result = _find(results, "project-manifest")
        assert manifest_result.status == CheckStatus.ERROR
        assert "not a valid YAML mapping" in manifest_result.message


class TestGraphStaleness:
    """Tests for graph directory and staleness."""

    def test_missing_graph_dir_is_warn(
        self, check: ProjectCheck, ctx: DoctorContext
    ) -> None:
        results = check.evaluate(ctx)
        graph_result = _find(results, "project-graph")
        assert graph_result.status == CheckStatus.WARN
        assert "missing" in graph_result.message
        assert graph_result.fix_hint == "run: rai graph build"

    def test_fresh_graph_is_pass(self, check: ProjectCheck, ctx: DoctorContext) -> None:
        graph_dir = ctx.working_dir / ".raise" / "rai" / "memory"
        graph_dir.mkdir(parents=True, exist_ok=True)
        (graph_dir / "index.json").write_text("{}")
        results = check.evaluate(ctx)
        graph_result = _find(results, "project-graph")
        assert graph_result.status == CheckStatus.PASS

    def test_stale_graph_is_warn(self, check: ProjectCheck, ctx: DoctorContext) -> None:
        graph_dir = ctx.working_dir / ".raise" / "rai" / "memory"
        graph_dir.mkdir(parents=True, exist_ok=True)
        graph_file = graph_dir / "index.json"
        graph_file.write_text("{}")
        # Set mtime to 10 days ago
        old_time = time.time() - (10 * 86400)
        import os

        os.utime(graph_file, (old_time, old_time))
        results = check.evaluate(ctx)
        graph_result = _find(results, "project-graph")
        assert graph_result.status == CheckStatus.WARN
        assert "days old" in graph_result.message

    def test_governance_newer_than_graph_is_warn(
        self, check: ProjectCheck, ctx: DoctorContext
    ) -> None:
        graph_dir = ctx.working_dir / ".raise" / "rai" / "memory"
        graph_dir.mkdir(parents=True, exist_ok=True)
        graph_file = graph_dir / "index.json"
        graph_file.write_text("{}")
        # Set graph mtime to 1 day ago
        import os

        graph_time = time.time() - 86400
        os.utime(graph_file, (graph_time, graph_time))
        # Create governance file that's newer (now)
        gov_dir = ctx.working_dir / "governance"
        gov_dir.mkdir()
        (gov_dir / "prd.md").write_text("# PRD")
        results = check.evaluate(ctx)
        graph_result = _find(results, "project-graph")
        assert graph_result.status == CheckStatus.WARN
        assert "newer than graph" in graph_result.message


class TestAdapterConfig:
    """Tests for adapter config presence."""

    def test_missing_jira_config_is_warn(
        self, check: ProjectCheck, ctx: DoctorContext
    ) -> None:
        results = check.evaluate(ctx)
        adapter_result = _find(results, "project-adapter-config")
        assert adapter_result.status == CheckStatus.WARN
        assert "optional" in adapter_result.message

    def test_present_jira_config_is_pass(
        self, check: ProjectCheck, ctx: DoctorContext
    ) -> None:
        raise_dir = ctx.working_dir / ".raise"
        raise_dir.mkdir()
        (raise_dir / "jira.yaml").write_text("project: TEST\n")
        results = check.evaluate(ctx)
        adapter_result = _find(results, "project-adapter-config")
        assert adapter_result.status == CheckStatus.PASS


class TestSkillsDeployed:
    """Tests for skill deployment."""

    def test_missing_skills_dir_is_warn(
        self, check: ProjectCheck, ctx: DoctorContext
    ) -> None:
        results = check.evaluate(ctx)
        skills_result = _find(results, "project-skills")
        assert skills_result.status == CheckStatus.WARN

    def test_empty_skills_dir_is_warn(
        self, check: ProjectCheck, ctx: DoctorContext
    ) -> None:
        (ctx.working_dir / ".claude" / "skills").mkdir(parents=True)
        results = check.evaluate(ctx)
        skills_result = _find(results, "project-skills")
        assert skills_result.status == CheckStatus.WARN
        assert "no skills" in skills_result.message

    def test_skills_deployed_is_pass(
        self, check: ProjectCheck, ctx: DoctorContext
    ) -> None:
        skill_dir = ctx.working_dir / ".claude" / "skills" / "my-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Skill")
        results = check.evaluate(ctx)
        skills_result = _find(results, "project-skills")
        assert skills_result.status == CheckStatus.PASS
        assert "1 skills" in skills_result.message


class TestGitignore:
    """Tests for .gitignore entry."""

    def test_missing_gitignore_is_warn(
        self, check: ProjectCheck, ctx: DoctorContext
    ) -> None:
        results = check.evaluate(ctx)
        gi_result = _find(results, "project-gitignore")
        assert gi_result.status == CheckStatus.WARN
        assert ".gitignore missing" in gi_result.message

    def test_gitignore_without_personal_is_warn(
        self, check: ProjectCheck, ctx: DoctorContext
    ) -> None:
        (ctx.working_dir / ".gitignore").write_text("*.pyc\n__pycache__/\n")
        results = check.evaluate(ctx)
        gi_result = _find(results, "project-gitignore")
        assert gi_result.status == CheckStatus.WARN
        assert "not found in .gitignore" in gi_result.message

    def test_gitignore_with_personal_is_pass(
        self, check: ProjectCheck, ctx: DoctorContext
    ) -> None:
        (ctx.working_dir / ".gitignore").write_text("*.pyc\n.raise/rai/personal/\n")
        results = check.evaluate(ctx)
        gi_result = _find(results, "project-gitignore")
        assert gi_result.status == CheckStatus.PASS


class TestAllPass:
    """Test that a well-configured project passes all checks."""

    def test_everything_present_all_pass(
        self, check: ProjectCheck, tmp_path: Path
    ) -> None:
        # Set up a fully valid project
        raise_dir = tmp_path / ".raise"
        raise_dir.mkdir()
        (raise_dir / "manifest.yaml").write_text("name: test\n")
        (raise_dir / "jira.yaml").write_text("project: TEST\n")

        graph_dir = tmp_path / ".raise" / "rai" / "memory"
        graph_dir.mkdir(parents=True, exist_ok=True)
        (graph_dir / "index.json").write_text("{}")

        skill_dir = tmp_path / ".claude" / "skills" / "my-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Skill")

        (tmp_path / ".gitignore").write_text(".raise/rai/personal/\n")

        ctx = DoctorContext(working_dir=tmp_path)
        results = check.evaluate(ctx)
        assert all(r.status == CheckStatus.PASS for r in results), [
            f"{r.check_id}: {r.status.value} — {r.message}"
            for r in results
            if r.status != CheckStatus.PASS
        ]


class TestProtocolConformance:
    """Verify ProjectCheck conforms to DoctorCheck Protocol."""

    def test_has_required_class_vars(self, check: ProjectCheck) -> None:
        assert check.check_id == "project"
        assert check.category == "project"
        assert isinstance(check.description, str)
        assert check.requires_online is False

    def test_evaluate_returns_list_of_check_results(
        self, check: ProjectCheck, ctx: DoctorContext
    ) -> None:
        results = check.evaluate(ctx)
        assert isinstance(results, list)
        assert all(isinstance(r, CheckResult) for r in results)

    def test_conforms_to_doctor_check_protocol(self) -> None:
        from raise_cli.doctor.protocol import DoctorCheck

        assert isinstance(ProjectCheck(), DoctorCheck)


def _find(results: list[CheckResult], check_id: str) -> CheckResult:
    """Find a result by check_id or fail with helpful message."""
    for r in results:
        if r.check_id == check_id:
            return r
    available = [r.check_id for r in results]
    msg = f"check_id '{check_id}' not found in results: {available}"
    raise AssertionError(msg)
