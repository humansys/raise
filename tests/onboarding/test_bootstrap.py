"""Tests for the bootstrap module — copies bundled base Rai to project."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

from raise_cli.onboarding.bootstrap import (
    BootstrapResult,
    bootstrap_rai_base,
    ensure_gitignore,
)


class TestBootstrapRaiBase:
    """Tests for bootstrap_rai_base() function."""

    def test_copies_identity_files(self, tmp_path: Path) -> None:
        """Should copy core.yaml and perspective.md to .raise/rai/identity/."""
        result = bootstrap_rai_base(tmp_path)

        identity_dir = tmp_path / ".raise" / "rai" / "identity"
        assert (identity_dir / "core.yaml").exists()
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

        base = files("raise_cli.rai_base")
        original = (base / "identity" / "core.yaml").read_text(encoding="utf-8")
        copied = (tmp_path / ".raise" / "rai" / "identity" / "core.yaml").read_text(
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
        core_path = tmp_path / ".raise" / "rai" / "identity" / "core.yaml"
        core_path.write_text("values: []")

        # Second bootstrap
        result = bootstrap_rai_base(tmp_path)

        assert core_path.read_text(encoding="utf-8") == "values: []"
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
        (identity_dir / "core.yaml").write_text("values: []")
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
        (identity_dir / "core.yaml").write_text("values: []")
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


class TestBasePatternMerge:
    """Tests for merging base patterns on re-init."""

    def _write_patterns(self, path: Path, patterns: Sequence[dict[str, Any]]) -> None:
        """Helper: write pattern dicts as JSONL."""
        import json

        lines = [json.dumps(p) for p in patterns]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _read_patterns(self, path: Path) -> list[dict[str, object]]:
        """Helper: read JSONL patterns from file."""
        import json

        lines = path.read_text(encoding="utf-8").strip().splitlines()
        return [json.loads(line) for line in lines if line.strip()]

    def test_copy_patterns_merges_new_base_on_reinit(self, tmp_path: Path) -> None:
        """Existing patterns.jsonl with BASE-001 + PAT-E-001, package adds BASE-002+.

        After merge: BASE-001 preserved, PAT-E-001 preserved, new BASE-* appended.
        """
        patterns_file = tmp_path / ".raise" / "rai" / "memory" / "patterns.jsonl"
        self._write_patterns(
            patterns_file,
            [
                {
                    "id": "BASE-001",
                    "content": "existing base",
                    "base": True,
                    "version": 1,
                },
                {"id": "PAT-E-001", "content": "project pattern", "version": 1},
            ],
        )

        result = bootstrap_rai_base(tmp_path)

        merged = self._read_patterns(patterns_file)
        ids = [p["id"] for p in merged]

        # PAT-E-001 must survive
        assert "PAT-E-001" in ids
        # BASE-001 must survive
        assert "BASE-001" in ids
        # New base patterns from package should be added
        assert result.patterns_added > 0
        # Total should be 2 original + however many new base patterns
        assert len(merged) > 2

    def test_copy_patterns_updates_versioned_base(self, tmp_path: Path) -> None:
        """Existing BASE-007 v1 should be updated to v2 from package."""
        patterns_file = tmp_path / ".raise" / "rai" / "memory" / "patterns.jsonl"
        self._write_patterns(
            patterns_file,
            [
                {
                    "id": "BASE-007",
                    "content": "old content",
                    "base": True,
                    "version": 1,
                },
            ],
        )

        result = bootstrap_rai_base(tmp_path)

        merged = self._read_patterns(patterns_file)
        base007 = [p for p in merged if p["id"] == "BASE-007"][0]

        # Package has BASE-007 v2, so it should be updated
        assert base007["version"] == 2
        assert base007["content"] != "old content"
        assert result.patterns_updated >= 1

    def test_copy_patterns_preserves_project_patterns(self, tmp_path: Path) -> None:
        """All PAT-E-* patterns must be preserved untouched."""
        patterns_file = tmp_path / ".raise" / "rai" / "memory" / "patterns.jsonl"
        project_patterns = [
            {"id": f"PAT-E-{i:03d}", "content": f"project pattern {i}", "version": 1}
            for i in range(1, 6)
        ]
        self._write_patterns(patterns_file, project_patterns)

        bootstrap_rai_base(tmp_path)

        merged = self._read_patterns(patterns_file)
        pat_e_entries = [p for p in merged if str(p["id"]).startswith("PAT-E-")]

        assert len(pat_e_entries) == 5
        for i, p in enumerate(pat_e_entries, start=1):
            assert p["content"] == f"project pattern {i}"

    def test_copy_patterns_idempotent(self, tmp_path: Path) -> None:
        """Running merge twice produces the same result."""
        patterns_file = tmp_path / ".raise" / "rai" / "memory" / "patterns.jsonl"
        self._write_patterns(
            patterns_file,
            [{"id": "PAT-E-001", "content": "project", "version": 1}],
        )

        bootstrap_rai_base(tmp_path)
        first_content = patterns_file.read_text(encoding="utf-8")

        result2 = bootstrap_rai_base(tmp_path)
        second_content = patterns_file.read_text(encoding="utf-8")

        assert first_content == second_content
        assert result2.patterns_added == 0
        assert result2.patterns_updated == 0


class TestEnsureGitignore:
    """Tests for ensure_gitignore() — adds .raise/rai/personal/ to .gitignore."""

    def test_creates_gitignore_when_missing(self, tmp_path: Path) -> None:
        """Should create .gitignore with personal entry when file does not exist."""
        result = ensure_gitignore(tmp_path)

        gitignore = tmp_path / ".gitignore"
        assert gitignore.exists()
        assert result is True
        content = gitignore.read_text(encoding="utf-8")
        assert ".raise/rai/personal/" in content

    def test_appends_to_existing_gitignore(self, tmp_path: Path) -> None:
        """Should append entry to existing .gitignore without clobbering."""
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("node_modules/\n.env\n", encoding="utf-8")

        result = ensure_gitignore(tmp_path)

        assert result is True
        content = gitignore.read_text(encoding="utf-8")
        assert "node_modules/" in content
        assert ".env" in content
        assert ".raise/rai/personal/" in content

    def test_idempotent_no_duplicates(self, tmp_path: Path) -> None:
        """Running twice should not duplicate entries."""
        ensure_gitignore(tmp_path)
        result = ensure_gitignore(tmp_path)

        assert result is False
        content = (tmp_path / ".gitignore").read_text(encoding="utf-8")
        assert content.count(".raise/rai/personal/") == 1

    def test_skips_when_entry_already_present(self, tmp_path: Path) -> None:
        """Should not add entry if it already exists in .gitignore."""
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("# existing\n.raise/rai/personal/\n", encoding="utf-8")

        result = ensure_gitignore(tmp_path)

        assert result is False
        content = gitignore.read_text(encoding="utf-8")
        assert content.count(".raise/rai/personal/") == 1

    def test_adds_comment_before_entry(self, tmp_path: Path) -> None:
        """Should include a descriptive comment before the entry."""
        ensure_gitignore(tmp_path)

        content = (tmp_path / ".gitignore").read_text(encoding="utf-8")
        assert "# RaiSE personal directory" in content

    def test_bootstrap_calls_ensure_gitignore(self, tmp_path: Path) -> None:
        """bootstrap_rai_base should add .gitignore entries."""
        bootstrap_rai_base(tmp_path)

        gitignore = tmp_path / ".gitignore"
        assert gitignore.exists()
        content = gitignore.read_text(encoding="utf-8")
        assert ".raise/rai/personal/" in content


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
        assert result.patterns_added == 0
        assert result.patterns_updated == 0
