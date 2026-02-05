"""Tests for project manifest module."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

from raise_cli.onboarding.detection import ProjectType
from raise_cli.onboarding.manifest import (
    ProjectInfo,
    ProjectManifest,
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
        now = datetime.now(timezone.utc)
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
        content = manifest_path.read_text()
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

        content = (rai_dir / "manifest.yaml").read_text()
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
        now = datetime.now(timezone.utc)
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
