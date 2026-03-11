"""Tests for project manifest module."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import yaml

from raise_cli.onboarding.detection import ProjectType
from raise_cli.onboarding.manifest import (
    AgentsManifest,
    BacklogConfig,
    BranchConfig,
    IdeManifest,
    ProjectInfo,
    ProjectManifest,
    TierConfig,
    load_manifest,
    save_manifest,
)


class TestProjectInfo:
    """Tests for ProjectInfo model."""

    def test_minimal_project_info(self) -> None:
        """ProjectInfo with required fields only."""
        info = ProjectInfo(name="my-project", project_type=ProjectType.GREENFIELD)
        assert info.name == "my-project"
        assert info.project_type == ProjectType.GREENFIELD
        assert info.code_file_count == 0

    def test_full_project_info(self) -> None:
        """ProjectInfo with all fields."""
        now = datetime.now(UTC)
        info = ProjectInfo(
            name="my-api",
            project_type=ProjectType.BROWNFIELD,
            code_file_count=47,
            detected_at=now,
        )
        assert info.name == "my-api"
        assert info.project_type == ProjectType.BROWNFIELD
        assert info.code_file_count == 47
        assert info.detected_at == now

    def test_toolchain_fields_default_none(self) -> None:
        """Toolchain fields default to None."""
        info = ProjectInfo(name="test", project_type=ProjectType.GREENFIELD)
        assert info.language is None
        assert info.test_command is None
        assert info.lint_command is None
        assert info.type_check_command is None

    def test_toolchain_fields_set(self) -> None:
        """Toolchain fields can be set."""
        info = ProjectInfo(
            name="my-py",
            project_type=ProjectType.BROWNFIELD,
            language="python",
            test_command="uv run pytest --tb=short",
            lint_command="uv run ruff check",
            type_check_command="uv run pyright",
        )
        assert info.language == "python"
        assert info.test_command == "uv run pytest --tb=short"
        assert info.lint_command == "uv run ruff check"
        assert info.type_check_command == "uv run pyright"

    def test_toolchain_roundtrip(self, tmp_path: Path) -> None:
        """Save and load preserves toolchain fields."""
        project = ProjectInfo(
            name="test",
            project_type=ProjectType.BROWNFIELD,
            language="typescript",
            test_command="npx vitest run",
            lint_command="npx eslint .",
            type_check_command="npx tsc --noEmit",
        )
        original = ProjectManifest(project=project)
        save_manifest(original, tmp_path)
        loaded = load_manifest(tmp_path)

        assert loaded is not None
        assert loaded.project.language == "typescript"
        assert loaded.project.test_command == "npx vitest run"
        assert loaded.project.lint_command == "npx eslint ."
        assert loaded.project.type_check_command == "npx tsc --noEmit"

    def test_loads_legacy_manifest_without_toolchain(self, tmp_path: Path) -> None:
        """Loads manifest without toolchain fields (backward compat)."""
        rai_dir = tmp_path / ".raise"
        rai_dir.mkdir()
        (rai_dir / "manifest.yaml").write_text(
            "version: '1.0'\n"
            "project:\n"
            "  name: old-project\n"
            "  project_type: brownfield\n"
            "  code_file_count: 10\n"
            "  detected_at: '2026-01-01T00:00:00Z'\n"
        )
        loaded = load_manifest(tmp_path)
        assert loaded is not None
        assert loaded.project.language is None
        assert loaded.project.test_command is None
        assert loaded.project.lint_command is None
        assert loaded.project.type_check_command is None


class TestProjectManifest:
    """Tests for ProjectManifest model."""

    def test_minimal_manifest(self) -> None:
        """ProjectManifest with required fields only."""
        project = ProjectInfo(name="test", project_type=ProjectType.GREENFIELD)
        manifest = ProjectManifest(project=project)
        assert manifest.version == "1.0"
        assert manifest.project.name == "test"

    def test_custom_version(self) -> None:
        """ProjectManifest with custom version."""
        project = ProjectInfo(name="test", project_type=ProjectType.GREENFIELD)
        manifest = ProjectManifest(version="2.0", project=project)
        assert manifest.version == "2.0"


class TestBranchConfig:
    """Tests for BranchConfig model."""

    def test_defaults_to_main(self) -> None:
        """BranchConfig defaults both branches to main."""
        config = BranchConfig()
        assert config.development == "main"
        assert config.main == "main"

    def test_custom_branches(self) -> None:
        """BranchConfig with custom branch names."""
        config = BranchConfig(development="develop", main="master")
        assert config.development == "develop"
        assert config.main == "master"


class TestManifestWithBranches:
    """Tests for ProjectManifest with branch config."""

    def test_manifest_has_default_branches(self) -> None:
        """Manifest has default branch config when not specified."""
        project = ProjectInfo(name="test", project_type=ProjectType.GREENFIELD)
        manifest = ProjectManifest(project=project)
        assert manifest.branches.development == "main"
        assert manifest.branches.main == "main"

    def test_manifest_with_custom_branches(self) -> None:
        """Manifest accepts custom branch config."""
        project = ProjectInfo(name="test", project_type=ProjectType.GREENFIELD)
        branches = BranchConfig(development="develop", main="main")
        manifest = ProjectManifest(project=project, branches=branches)
        assert manifest.branches.development == "develop"

    def test_roundtrip_with_branches(self, tmp_path: Path) -> None:
        """Save and load preserves branch config."""
        project = ProjectInfo(name="test", project_type=ProjectType.GREENFIELD)
        branches = BranchConfig(development="dev", main="master")
        original = ProjectManifest(project=project, branches=branches)

        save_manifest(original, tmp_path)
        loaded = load_manifest(tmp_path)

        assert loaded is not None
        assert loaded.branches.development == "dev"
        assert loaded.branches.main == "master"

    def test_loads_manifest_without_branches_field(self, tmp_path: Path) -> None:
        """Loads legacy manifest without branches field (backward compat)."""
        rai_dir = tmp_path / ".raise"
        rai_dir.mkdir()
        (rai_dir / "manifest.yaml").write_text(
            "version: '1.0'\n"
            "project:\n"
            "  name: old-project\n"
            "  project_type: brownfield\n"
            "  code_file_count: 10\n"
            "  detected_at: '2026-01-01T00:00:00Z'\n"
        )

        loaded = load_manifest(tmp_path)
        assert loaded is not None
        assert loaded.branches.development == "main"
        assert loaded.branches.main == "main"


class TestIdeManifest:
    """Tests for IdeManifest model."""

    def test_defaults_to_claude(self) -> None:
        """IdeManifest defaults type to claude."""
        ide = IdeManifest()
        assert ide.type == "claude"

    def test_accepts_antigravity(self) -> None:
        """IdeManifest accepts antigravity type."""
        ide = IdeManifest(type="antigravity")
        assert ide.type == "antigravity"

    def test_rejects_invalid_type(self) -> None:
        """IdeManifest rejects invalid IDE type."""
        import pytest

        with pytest.raises(Exception):  # noqa: B017
            IdeManifest(type="invalid")  # type: ignore[arg-type]


class TestManifestWithIde:
    """Tests for ProjectManifest with IDE config."""

    def test_manifest_has_default_ide(self) -> None:
        """Manifest defaults to claude IDE when not specified."""
        project = ProjectInfo(name="test", project_type=ProjectType.GREENFIELD)
        manifest = ProjectManifest(project=project)
        assert manifest.ide.type == "claude"

    def test_manifest_with_antigravity_ide(self) -> None:
        """Manifest accepts antigravity IDE config."""
        project = ProjectInfo(name="test", project_type=ProjectType.GREENFIELD)
        ide = IdeManifest(type="antigravity")
        manifest = ProjectManifest(project=project, ide=ide)
        assert manifest.ide.type == "antigravity"

    def test_roundtrip_with_ide(self, tmp_path: Path) -> None:
        """Save and load preserves IDE config."""
        project = ProjectInfo(name="test", project_type=ProjectType.GREENFIELD)
        ide = IdeManifest(type="antigravity")
        original = ProjectManifest(project=project, ide=ide)

        save_manifest(original, tmp_path)
        loaded = load_manifest(tmp_path)

        assert loaded is not None
        assert loaded.ide.type == "antigravity"

    def test_loads_manifest_without_ide_field(self, tmp_path: Path) -> None:
        """Loads legacy manifest without ide field (backward compat)."""
        rai_dir = tmp_path / ".raise"
        rai_dir.mkdir()
        (rai_dir / "manifest.yaml").write_text(
            "version: '1.0'\n"
            "project:\n"
            "  name: old-project\n"
            "  project_type: brownfield\n"
            "  code_file_count: 10\n"
            "  detected_at: '2026-01-01T00:00:00Z'\n"
        )

        loaded = load_manifest(tmp_path)
        assert loaded is not None
        assert loaded.ide.type == "claude"

    def test_saved_yaml_contains_ide_section(self, tmp_path: Path) -> None:
        """Saved YAML includes ide section."""
        project = ProjectInfo(name="test", project_type=ProjectType.GREENFIELD)
        ide = IdeManifest(type="antigravity")
        manifest = ProjectManifest(project=project, ide=ide)

        save_manifest(manifest, tmp_path)

        content = (tmp_path / ".raise" / "manifest.yaml").read_text()
        data = yaml.safe_load(content)
        assert data["ide"]["type"] == "antigravity"


class TestSaveManifest:
    """Tests for save_manifest function."""

    def test_creates_rai_directory(self, tmp_path: Path) -> None:
        """Creates .raise directory if it doesn't exist."""
        project = ProjectInfo(name="test", project_type=ProjectType.GREENFIELD)
        manifest = ProjectManifest(project=project)

        save_manifest(manifest, tmp_path)

        assert (tmp_path / ".raise").is_dir()

    def test_creates_manifest_file(self, tmp_path: Path) -> None:
        """Creates manifest.yaml file."""
        project = ProjectInfo(name="test", project_type=ProjectType.GREENFIELD)
        manifest = ProjectManifest(project=project)

        save_manifest(manifest, tmp_path)

        manifest_path = tmp_path / ".raise" / "manifest.yaml"
        assert manifest_path.exists()

    def test_manifest_content_is_valid_yaml(self, tmp_path: Path) -> None:
        """Manifest file contains valid YAML."""
        project = ProjectInfo(
            name="my-project",
            project_type=ProjectType.BROWNFIELD,
            code_file_count=42,
        )
        manifest = ProjectManifest(project=project)

        save_manifest(manifest, tmp_path)

        manifest_path = tmp_path / ".raise" / "manifest.yaml"
        content = manifest_path.read_text(encoding="utf-8")
        data = yaml.safe_load(content)

        assert data["version"] == "1.0"
        assert data["project"]["name"] == "my-project"
        assert data["project"]["project_type"] == "brownfield"
        assert data["project"]["code_file_count"] == 42

    def test_overwrites_existing_manifest(self, tmp_path: Path) -> None:
        """Overwrites existing manifest file."""
        rai_dir = tmp_path / ".raise"
        rai_dir.mkdir()
        (rai_dir / "manifest.yaml").write_text("old: content")

        project = ProjectInfo(name="new", project_type=ProjectType.GREENFIELD)
        manifest = ProjectManifest(project=project)

        save_manifest(manifest, tmp_path)

        content = (rai_dir / "manifest.yaml").read_text(encoding="utf-8")
        assert "old: content" not in content
        assert "new" in content


class TestLoadManifest:
    """Tests for load_manifest function."""

    def test_returns_none_if_not_exists(self, tmp_path: Path) -> None:
        """Returns None if manifest doesn't exist."""
        result = load_manifest(tmp_path)
        assert result is None

    def test_returns_none_if_rai_dir_missing(self, tmp_path: Path) -> None:
        """Returns None if .raise directory doesn't exist."""
        result = load_manifest(tmp_path)
        assert result is None

    def test_loads_valid_manifest(self, tmp_path: Path) -> None:
        """Loads a valid manifest file."""
        project = ProjectInfo(
            name="test-project",
            project_type=ProjectType.BROWNFIELD,
            code_file_count=10,
        )
        manifest = ProjectManifest(project=project)
        save_manifest(manifest, tmp_path)

        loaded = load_manifest(tmp_path)

        assert loaded is not None
        assert loaded.version == "1.0"
        assert loaded.project.name == "test-project"
        assert loaded.project.project_type == ProjectType.BROWNFIELD
        assert loaded.project.code_file_count == 10

    def test_returns_none_for_invalid_yaml(self, tmp_path: Path) -> None:
        """Returns None for invalid YAML."""
        rai_dir = tmp_path / ".raise"
        rai_dir.mkdir()
        (rai_dir / "manifest.yaml").write_text("invalid: yaml: content: [")

        result = load_manifest(tmp_path)
        assert result is None

    def test_returns_none_for_invalid_schema(self, tmp_path: Path) -> None:
        """Returns None for valid YAML but invalid schema."""
        rai_dir = tmp_path / ".raise"
        rai_dir.mkdir()
        (rai_dir / "manifest.yaml").write_text("random: data\nno_project: true")

        result = load_manifest(tmp_path)
        assert result is None

    def test_roundtrip(self, tmp_path: Path) -> None:
        """Save and load produces equivalent manifest."""
        now = datetime.now(UTC)
        project = ProjectInfo(
            name="roundtrip-test",
            project_type=ProjectType.BROWNFIELD,
            code_file_count=99,
            detected_at=now,
        )
        original = ProjectManifest(project=project)

        save_manifest(original, tmp_path)
        loaded = load_manifest(tmp_path)

        assert loaded is not None
        assert loaded.version == original.version
        assert loaded.project.name == original.project.name
        assert loaded.project.project_type == original.project.project_type
        assert loaded.project.code_file_count == original.project.code_file_count


# =============================================================================
# AgentsManifest (new multi-agent schema)
# =============================================================================


class TestAgentsManifest:
    """Tests for AgentsManifest model — new multi-agent schema."""

    def test_defaults_to_claude(self) -> None:
        """AgentsManifest defaults types to ['claude']."""
        m = AgentsManifest()
        assert m.types == ["claude"]

    def test_accepts_multiple_types(self) -> None:
        """AgentsManifest accepts list of agent types."""
        m = AgentsManifest(types=["claude", "cursor", "windsurf"])
        assert m.types == ["claude", "cursor", "windsurf"]

    def test_empty_types_allowed(self) -> None:
        """AgentsManifest accepts empty list."""
        m = AgentsManifest(types=[])
        assert m.types == []

    def test_custom_agent_types_allowed(self) -> None:
        """AgentsManifest accepts non-builtin agent types (extensibility)."""
        m = AgentsManifest(types=["azure-devops"])
        assert "azure-devops" in m.types


class TestProjectManifestAgents:
    """Tests for ProjectManifest.agents field."""

    def test_manifest_has_default_agents(self) -> None:
        """Manifest defaults agents to ['claude']."""
        project = ProjectInfo(name="test", project_type=ProjectType.GREENFIELD)
        manifest = ProjectManifest(project=project)
        assert manifest.agents.types == ["claude"]

    def test_manifest_accepts_multi_agent(self) -> None:
        """Manifest accepts explicit multi-agent config."""
        project = ProjectInfo(name="test", project_type=ProjectType.GREENFIELD)
        agents = AgentsManifest(types=["claude", "cursor"])
        manifest = ProjectManifest(project=project, agents=agents)
        assert "cursor" in manifest.agents.types

    def test_saved_yaml_contains_agents_section(self, tmp_path: Path) -> None:
        """Saved YAML includes agents.types section."""
        project = ProjectInfo(name="test", project_type=ProjectType.GREENFIELD)
        agents = AgentsManifest(types=["claude", "cursor"])
        manifest = ProjectManifest(project=project, agents=agents)

        save_manifest(manifest, tmp_path)

        data = yaml.safe_load((tmp_path / ".raise" / "manifest.yaml").read_text())
        assert data["agents"]["types"] == ["claude", "cursor"]

    def test_roundtrip_agents(self, tmp_path: Path) -> None:
        """Save + load preserves agents.types."""
        project = ProjectInfo(name="test", project_type=ProjectType.GREENFIELD)
        manifest = ProjectManifest(
            project=project, agents=AgentsManifest(types=["claude", "windsurf"])
        )
        save_manifest(manifest, tmp_path)
        loaded = load_manifest(tmp_path)

        assert loaded is not None
        assert loaded.agents.types == ["claude", "windsurf"]


class TestManifestBackwardCompat:
    """Tests for backward compat — old ide.type → agents.types migration."""

    def test_old_ide_yaml_populates_agents(self, tmp_path: Path) -> None:
        """Old manifest with ide.type migrates to agents.types on load."""
        rai_dir = tmp_path / ".raise"
        rai_dir.mkdir()
        (rai_dir / "manifest.yaml").write_text(
            "version: '1.0'\n"
            "project:\n"
            "  name: old-project\n"
            "  project_type: brownfield\n"
            "  code_file_count: 5\n"
            "  detected_at: '2026-01-01T00:00:00Z'\n"
            "ide:\n"
            "  type: antigravity\n"
        )
        loaded = load_manifest(tmp_path)
        assert loaded is not None
        assert "antigravity" in loaded.agents.types

    def test_manifest_without_ide_uses_claude_default(self, tmp_path: Path) -> None:
        """Manifest without ide or agents section defaults agents to ['claude']."""
        rai_dir = tmp_path / ".raise"
        rai_dir.mkdir()
        (rai_dir / "manifest.yaml").write_text(
            "version: '1.0'\n"
            "project:\n"
            "  name: old-project\n"
            "  project_type: brownfield\n"
            "  code_file_count: 5\n"
            "  detected_at: '2026-01-01T00:00:00Z'\n"
        )
        loaded = load_manifest(tmp_path)
        assert loaded is not None
        assert loaded.agents.types == ["claude"]

    def test_new_agents_yaml_takes_precedence(self, tmp_path: Path) -> None:
        """If both ide and agents present, agents.types is used."""
        rai_dir = tmp_path / ".raise"
        rai_dir.mkdir()
        (rai_dir / "manifest.yaml").write_text(
            "version: '1.0'\n"
            "project:\n"
            "  name: proj\n"
            "  project_type: brownfield\n"
            "  code_file_count: 1\n"
            "  detected_at: '2026-01-01T00:00:00Z'\n"
            "ide:\n"
            "  type: claude\n"
            "agents:\n"
            "  types:\n"
            "    - claude\n"
            "    - cursor\n"
        )
        loaded = load_manifest(tmp_path)
        assert loaded is not None
        assert loaded.agents.types == ["claude", "cursor"]


# =============================================================================
# TierConfig (S211.5)
# =============================================================================


class TestTierConfig:
    """Tests for TierConfig model — optional tier section in manifest."""

    def test_defaults(self) -> None:
        cfg = TierConfig()
        assert cfg.level == "community"
        assert cfg.backend_url is None
        assert cfg.capabilities == []

    def test_pro_config(self) -> None:
        cfg = TierConfig(
            level="pro",
            backend_url="https://api.example.com",
            capabilities=["shared_memory"],
        )
        assert cfg.level == "pro"
        assert cfg.backend_url == "https://api.example.com"
        assert cfg.capabilities == ["shared_memory"]


class TestManifestWithTier:
    """Tests for ProjectManifest with optional tier config."""

    def test_manifest_without_tier(self) -> None:
        project = ProjectInfo(name="test", project_type=ProjectType.GREENFIELD)
        manifest = ProjectManifest(project=project)
        assert manifest.tier is None

    def test_manifest_with_tier(self) -> None:
        project = ProjectInfo(name="test", project_type=ProjectType.GREENFIELD)
        tier = TierConfig(level="pro", capabilities=["shared_memory"])
        manifest = ProjectManifest(project=project, tier=tier)
        assert manifest.tier is not None
        assert manifest.tier.level == "pro"

    def test_roundtrip_with_tier(self, tmp_path: Path) -> None:
        project = ProjectInfo(name="test", project_type=ProjectType.GREENFIELD)
        tier = TierConfig(
            level="pro",
            backend_url="https://api.example.com",
            capabilities=["shared_memory", "semantic_search"],
        )
        manifest = ProjectManifest(project=project, tier=tier)
        save_manifest(manifest, tmp_path)
        loaded = load_manifest(tmp_path)

        assert loaded is not None
        assert loaded.tier is not None
        assert loaded.tier.level == "pro"
        assert loaded.tier.backend_url == "https://api.example.com"
        assert loaded.tier.capabilities == ["shared_memory", "semantic_search"]

    def test_loads_manifest_without_tier_field(self, tmp_path: Path) -> None:
        rai_dir = tmp_path / ".raise"
        rai_dir.mkdir()
        (rai_dir / "manifest.yaml").write_text(
            "version: '1.0'\n"
            "project:\n"
            "  name: old-project\n"
            "  project_type: brownfield\n"
            "  code_file_count: 5\n"
            "  detected_at: '2026-01-01T00:00:00Z'\n"
        )
        loaded = load_manifest(tmp_path)
        assert loaded is not None
        assert loaded.tier is None


# =============================================================================
# BacklogConfig (S347.1)
# =============================================================================


class TestBacklogConfig:
    """Tests for BacklogConfig model — optional backlog section in manifest."""

    def test_defaults(self) -> None:
        cfg = BacklogConfig()
        assert cfg.adapter_default is None

    def test_with_adapter_default(self) -> None:
        cfg = BacklogConfig(adapter_default="jira")
        assert cfg.adapter_default == "jira"


class TestManifestWithBacklog:
    """Tests for ProjectManifest with optional backlog config."""

    def test_manifest_without_backlog(self) -> None:
        project = ProjectInfo(name="test", project_type=ProjectType.GREENFIELD)
        manifest = ProjectManifest(project=project)
        assert manifest.backlog is None

    def test_manifest_with_backlog(self) -> None:
        project = ProjectInfo(name="test", project_type=ProjectType.GREENFIELD)
        backlog = BacklogConfig(adapter_default="jira")
        manifest = ProjectManifest(project=project, backlog=backlog)
        assert manifest.backlog is not None
        assert manifest.backlog.adapter_default == "jira"

    def test_roundtrip_with_backlog(self, tmp_path: Path) -> None:
        project = ProjectInfo(name="test", project_type=ProjectType.GREENFIELD)
        backlog = BacklogConfig(adapter_default="filesystem")
        manifest = ProjectManifest(project=project, backlog=backlog)
        save_manifest(manifest, tmp_path)
        loaded = load_manifest(tmp_path)

        assert loaded is not None
        assert loaded.backlog is not None
        assert loaded.backlog.adapter_default == "filesystem"

    def test_loads_manifest_without_backlog_field(self, tmp_path: Path) -> None:
        rai_dir = tmp_path / ".raise"
        rai_dir.mkdir()
        (rai_dir / "manifest.yaml").write_text(
            "version: '1.0'\n"
            "project:\n"
            "  name: old-project\n"
            "  project_type: brownfield\n"
            "  code_file_count: 5\n"
            "  detected_at: '2026-01-01T00:00:00Z'\n"
        )
        loaded = load_manifest(tmp_path)
        assert loaded is not None
        assert loaded.backlog is None

    def test_saved_yaml_contains_backlog_section(self, tmp_path: Path) -> None:
        project = ProjectInfo(name="test", project_type=ProjectType.GREENFIELD)
        backlog = BacklogConfig(adapter_default="jira")
        manifest = ProjectManifest(project=project, backlog=backlog)

        save_manifest(manifest, tmp_path)

        data = yaml.safe_load((tmp_path / ".raise" / "manifest.yaml").read_text())
        assert data["backlog"]["adapter_default"] == "jira"
