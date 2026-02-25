"""Tests for the bootstrap module — copies bundled base Rai to project."""

from __future__ import annotations

from pathlib import Path

from rai_cli.onboarding.bootstrap import BootstrapResult, bootstrap_rai_base


class TestBootstrapRaiBase:
    """Tests for bootstrap_rai_base() function."""

    def test_copies_identity_files(self, tmp_path: Path) -> None:
        """Should copy core.md and perspective.md to .raise/rai/identity/."""
        result = bootstrap_rai_base(tmp_path)

        identity_dir = tmp_path / ".raise" / "rai" / "identity"
        assert (identity_dir / "core.md").exists()
        assert (identity_dir / "perspective.md").exists()
        assert result.identity_copied

    def test_copies_patterns_file(self, tmp_path: Path) -> None:
        """Should copy patterns-base.jsonl to .raise/rai/memory/patterns.jsonl."""
        result = bootstrap_rai_base(tmp_path)

        patterns_file = tmp_path / ".raise" / "rai" / "memory" / "patterns.jsonl"
        assert patterns_file.exists()
        assert result.patterns_copied
        # Should contain actual patterns (not empty)
        content = patterns_file.read_text(encoding="utf-8")
        assert "BASE-001" in content

    def test_copies_methodology_file(self, tmp_path: Path) -> None:
        """Should copy methodology.yaml to .raise/rai/framework/."""
        result = bootstrap_rai_base(tmp_path)

        methodology_file = (
            tmp_path / ".raise" / "rai" / "framework" / "methodology.yaml"
        )
        assert methodology_file.exists()
        assert result.methodology_copied
        # Should contain actual methodology content
        content = methodology_file.read_text(encoding="utf-8")
        assert "version:" in content

    def test_returns_base_version(self, tmp_path: Path) -> None:
        """Should return the base package version."""
        result = bootstrap_rai_base(tmp_path)

        assert result.base_version != ""
        # Version should be semver-like
        assert "." in result.base_version

    def test_reports_copied_files(self, tmp_path: Path) -> None:
        """Should list all copied files in result."""
        result = bootstrap_rai_base(tmp_path)

        assert len(result.files_copied) > 0
        assert len(result.files_skipped) == 0
        assert not result.already_existed

    def test_identity_content_matches_bundled(self, tmp_path: Path) -> None:
        """Copied identity files should match bundled originals."""
        from importlib.resources import files

        bootstrap_rai_base(tmp_path)

        base = files("rai_cli.rai_base")
        original = (base / "identity" / "core.md").read_text(encoding="utf-8")
        copied = (tmp_path / ".raise" / "rai" / "identity" / "core.md").read_text(
            encoding="utf-8"
        )
        assert copied == original


class TestBootstrapIdempotency:
    """Tests for bootstrap being safe to run multiple times."""

    def test_does_not_overwrite_identity(self, tmp_path: Path) -> None:
        """Should not overwrite existing identity files."""
        # First bootstrap
        bootstrap_rai_base(tmp_path)

        # Modify identity file
        core_path = tmp_path / ".raise" / "rai" / "identity" / "core.md"
        core_path.write_text("# Custom identity")

        # Second bootstrap
        result = bootstrap_rai_base(tmp_path)

        assert core_path.read_text(encoding="utf-8") == "# Custom identity"
        assert not result.identity_copied

    def test_does_not_overwrite_patterns(self, tmp_path: Path) -> None:
        """Should not overwrite existing patterns.jsonl."""
        # First bootstrap
        bootstrap_rai_base(tmp_path)

        # Modify patterns file
        patterns_path = tmp_path / ".raise" / "rai" / "memory" / "patterns.jsonl"
        patterns_path.write_text('{"id": "PAT-001", "custom": true}\n')

        # Second bootstrap
        result = bootstrap_rai_base(tmp_path)

        assert '{"id": "PAT-001", "custom": true}' in patterns_path.read_text(
            encoding="utf-8"
        )
        assert not result.patterns_copied

    def test_does_not_overwrite_methodology(self, tmp_path: Path) -> None:
        """Should not overwrite existing methodology.yaml."""
        # First bootstrap
        bootstrap_rai_base(tmp_path)

        # Modify methodology
        meth_path = tmp_path / ".raise" / "rai" / "framework" / "methodology.yaml"
        meth_path.write_text("version: 99\n")

        # Second bootstrap
        result = bootstrap_rai_base(tmp_path)

        assert meth_path.read_text(encoding="utf-8") == "version: 99\n"
        assert not result.methodology_copied

    def test_second_run_reports_already_existed(self, tmp_path: Path) -> None:
        """Second bootstrap should report already_existed=True."""
        bootstrap_rai_base(tmp_path)
        result = bootstrap_rai_base(tmp_path)

        assert result.already_existed
        assert len(result.files_skipped) > 0
        assert len(result.files_copied) == 0


class TestBootstrapPartialState:
    """Tests for bootstrap when .raise/rai/ is partially populated."""

    def test_copies_missing_patterns_when_identity_exists(self, tmp_path: Path) -> None:
        """Should copy patterns even if identity already exists."""
        # Create identity manually
        identity_dir = tmp_path / ".raise" / "rai" / "identity"
        identity_dir.mkdir(parents=True)
        (identity_dir / "core.md").write_text("# Existing")
        (identity_dir / "perspective.md").write_text("# Existing")

        result = bootstrap_rai_base(tmp_path)

        # Identity should be skipped
        assert not result.identity_copied
        # Patterns should be copied
        assert result.patterns_copied
        # Methodology should be copied
        assert result.methodology_copied

    def test_copies_missing_methodology_when_others_exist(self, tmp_path: Path) -> None:
        """Should copy methodology even if identity and patterns exist."""
        # Create identity and patterns manually
        identity_dir = tmp_path / ".raise" / "rai" / "identity"
        identity_dir.mkdir(parents=True)
        (identity_dir / "core.md").write_text("# Existing")
        (identity_dir / "perspective.md").write_text("# Existing")

        memory_dir = tmp_path / ".raise" / "rai" / "memory"
        memory_dir.mkdir(parents=True)
        (memory_dir / "patterns.jsonl").write_text('{"id": "PAT-001"}\n')

        result = bootstrap_rai_base(tmp_path)

        assert not result.identity_copied
        assert not result.patterns_copied
        assert result.methodology_copied

    def test_handles_empty_raise_dir(self, tmp_path: Path) -> None:
        """Should work when .raise/ exists but rai/ doesn't."""
        (tmp_path / ".raise").mkdir()

        result = bootstrap_rai_base(tmp_path)

        assert result.identity_copied
        assert result.patterns_copied
        assert result.methodology_copied


class TestBootstrapResult:
    """Tests for BootstrapResult model."""

    def test_default_values(self) -> None:
        """Should have sensible defaults."""
        result = BootstrapResult()

        assert not result.identity_copied
        assert not result.patterns_copied
        assert not result.methodology_copied
        assert result.base_version == ""
        assert not result.already_existed
        assert result.files_copied == []
        assert result.files_skipped == []
