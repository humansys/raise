"""Tests for base identity package.

Tests verify that:
1. Identity files are accessible via importlib.resources
2. Files contain required sections
3. Content is valid markdown
"""

from __future__ import annotations

from importlib.resources import files

import pytest


class TestBaseIdentityPackage:
    """Tests for base identity file accessibility."""

    def test_rai_base_package_exists(self) -> None:
        """rai_base package is importable."""
        from raise_cli import rai_base

        assert rai_base.__version__ == "1.0.0"

    def test_identity_directory_accessible(self) -> None:
        """Identity directory is accessible via importlib.resources."""
        base = files("raise_cli.rai_base")
        identity = base / "identity"
        assert identity.is_dir()

    def test_core_yaml_exists(self) -> None:
        """core.yaml file exists and is readable."""
        base = files("raise_cli.rai_base")
        core_file = base / "identity" / "core.yaml"
        content = core_file.read_text(encoding="utf-8")
        assert len(content) > 0

    def test_core_md_exists(self) -> None:
        """core.md file exists (human-readable identity doc)."""
        base = files("raise_cli.rai_base")
        core_file = base / "identity" / "core.md"
        content = core_file.read_text(encoding="utf-8")
        assert len(content) > 0

    def test_perspective_md_exists(self) -> None:
        """perspective.md file exists and is readable."""
        base = files("raise_cli.rai_base")
        perspective_file = base / "identity" / "perspective.md"
        content = perspective_file.read_text(encoding="utf-8")
        assert len(content) > 0


class TestCoreIdentityContent:
    """Tests for core.md content structure."""

    @pytest.fixture
    def core_content(self) -> str:
        """Load core.md content."""
        base = files("raise_cli.rai_base")
        return (base / "identity" / "core.md").read_text(encoding="utf-8")

    def test_has_title(self, core_content: str) -> None:
        """Core identity has proper title."""
        assert "# Rai — Core Identity" in core_content

    def test_has_essence_section(self, core_content: str) -> None:
        """Core identity explains Rai's essence."""
        assert "## Essence" in core_content
        assert "RaiSE Triad" in core_content

    def test_has_values_section(self, core_content: str) -> None:
        """Core identity defines Rai's values."""
        assert "## Values" in core_content
        assert "Honesty over Agreement" in core_content
        assert "Simplicity over Cleverness" in core_content

    def test_has_boundaries_section(self, core_content: str) -> None:
        """Core identity defines boundaries."""
        assert "## Boundaries" in core_content
        assert "### I Will" in core_content
        assert "### I Won't" in core_content

    def test_has_philosophy_section(self, core_content: str) -> None:
        """Core identity explains internalized philosophy."""
        assert "## Internalized Philosophy" in core_content
        assert "Jidoka" in core_content

    def test_no_personal_references(self, core_content: str) -> None:
        """Core identity has no project-specific personal references."""
        # Should not have specific names or dates
        assert "Emilio" not in core_content
        assert "2026-02-01" not in core_content
        assert "2026-02-02" not in core_content


class TestPerspectiveContent:
    """Tests for perspective.md content structure."""

    @pytest.fixture
    def perspective_content(self) -> str:
        """Load perspective.md content."""
        base = files("raise_cli.rai_base")
        return (base / "identity" / "perspective.md").read_text(encoding="utf-8")

    def test_has_title(self, perspective_content: str) -> None:
        """Perspective has proper title."""
        assert "# Rai — Perspective" in perspective_content

    def test_has_collaboration_section(self, perspective_content: str) -> None:
        """Perspective explains collaboration approach."""
        assert "## How I Approach Collaboration" in perspective_content
        assert "What I Bring" in perspective_content
        assert "What I Don't Do" in perspective_content

    def test_has_principles_section(self, perspective_content: str) -> None:
        """Perspective defines principles."""
        assert "## Principles I Hold" in perspective_content
        assert "Inference Economy" in perspective_content

    def test_has_voice_section(self, perspective_content: str) -> None:
        """Perspective describes voice and style."""
        assert "## Voice & Style" in perspective_content
        assert "Signature Phrases" in perspective_content

    def test_has_intelligence_section(self, perspective_content: str) -> None:
        """Perspective explains collaborative intelligence."""
        assert "Intelligence" in perspective_content
        assert "compounds" in perspective_content

    def test_no_personal_references(self, perspective_content: str) -> None:
        """Perspective has no project-specific personal references."""
        # Should not have specific names
        assert "Emilio" not in perspective_content
        # Should not have session blessing (too personal)
        assert "Session Blessing" not in perspective_content


class TestIdentityMarkdownValidity:
    """Tests for markdown structure validity."""

    @pytest.fixture
    def core_content(self) -> str:
        """Load core.md content."""
        base = files("raise_cli.rai_base")
        return (base / "identity" / "core.md").read_text(encoding="utf-8")

    @pytest.fixture
    def perspective_content(self) -> str:
        """Load perspective.md content."""
        base = files("raise_cli.rai_base")
        return (base / "identity" / "perspective.md").read_text(encoding="utf-8")

    def test_core_has_h1_header(self, core_content: str) -> None:
        """Core has exactly one H1 header at the start."""
        lines = core_content.strip().split("\n")
        assert lines[0].startswith("# ")
        # Only one H1
        h1_count = sum(1 for line in lines if line.startswith("# "))
        assert h1_count == 1

    def test_perspective_has_h1_header(self, perspective_content: str) -> None:
        """Perspective has exactly one H1 header at the start."""
        lines = perspective_content.strip().split("\n")
        assert lines[0].startswith("# ")
        # Only one H1
        h1_count = sum(1 for line in lines if line.startswith("# "))
        assert h1_count == 1

    def test_core_has_multiple_sections(self, core_content: str) -> None:
        """Core has multiple H2 sections."""
        h2_count = core_content.count("\n## ")
        assert h2_count >= 4  # Essence, Values, Philosophy, Boundaries

    def test_perspective_has_multiple_sections(self, perspective_content: str) -> None:
        """Perspective has multiple H2 sections."""
        h2_count = perspective_content.count("\n## ")
        assert h2_count >= 4  # Understanding, Collaboration, Principles, Voice
